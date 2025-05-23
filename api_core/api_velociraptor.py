import datetime
import pytz
import grpc
import json
from abc import ABC, abstractmethod
from RControl.models import DeviceHost, DevicesClient
from pyvelociraptor import api_pb2, api_pb2_grpc


INACTIVITY_THRESHOLD = 15

def get_ip_without_port(last_ip):
    """Extract IP address from 'IP:port' format."""
    return last_ip.split(':')[0]

# Проверка валидности устройств
def is_valid_device(device):
    required_fields = ['client_id', 'os_info', 'last_seen_at', 'last_ip']

    # Проверяем, есть ли все необходимые ключи
    if not all(field in device and device[field] for field in required_fields):
        return False

    # Проверяем, что os_info содержит нужные данные
    if 'hostname' not in device['os_info'] or not device['os_info']['hostname']:
        return False

    # Проверка, что client_id и hostname не равны "server"
    if device['client_id'].lower() == 'server' or device['os_info']['hostname'].lower() == 'server':
        return False

    return True


class DeviceStrategy(ABC):
    @abstractmethod
    def save_device(self, device):
        """Save or update device information in the database."""
        pass


class ClientDeviceStrategy(DeviceStrategy):
    def save_device(self, device):
        if 'last_ip' not in device:
            print(f"Error: 'last_ip' not found for device {device['os_info']['hostname']}")
            return None

        last_seen_at = datetime.datetime.utcfromtimestamp(device['last_seen_at'] / 1e6).replace(tzinfo=pytz.UTC)

        first_seen_at = datetime.datetime.utcfromtimestamp(device['first_seen_at'] / 1e6).replace(
            tzinfo=pytz.UTC) if 'first_seen_at' in device else None
        fqdn = device.get('os_info', {}).get('fqdn', '')
        mac_addresses = device['os_info'].get('mac_addresses', [])
        if isinstance(mac_addresses, str):
            mac_addresses = [mac.strip() for mac in mac_addresses.split(",")]

        client, created = DevicesClient.objects.update_or_create(
            client_id=device['client_id'],
            defaults={
                'hostname': device['os_info']['hostname'],
                'os': device['os_info']['system'],
                'release': device['os_info']['release'],
                'last_ip': device['last_ip'],
                'last_seen_at': last_seen_at,
                'status': 'Online',
                'first_seen_at': first_seen_at,
                'fqdn': fqdn,
                'machine': device['os_info'].get('machine', ''),
                'mac_addresses': mac_addresses,
                'last_interrogate_flow_id': device['last_interrogate_flow_id'],
                'last_interrogate_artifact_name': device['last_interrogate_artifact_name'],
                'last_hunt_timestamp': device['last_hunt_timestamp']
            }
        )
        print(f"Client updated: {client.hostname}, Status: {client.status}")
        return client.id


class HostDeviceStrategy(DeviceStrategy):
    def save_device(self, device):
        """Save or update host device information in the database."""
        boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
        uptime_seconds = device['Uptime']
        last_seen_at = boot_time + datetime.timedelta(seconds=uptime_seconds)

        host, created = DeviceHost.objects.update_or_create(
            hostname=device['Hostname'],
            defaults={
                'uptime': last_seen_at,
                'boot_time': boot_time,
                'os': device['OS'],
                'platform': device['Platform'],
                'kernel_version': device['KernelVersion'],
                'arch': device['Architecture'],
            }
        )
        print(f"Host updated: {host.hostname}")
        return host.id

class DeleteRepeatClientsStrategy(DeviceStrategy):
    def save_device(self, device):
        """Удаляет повторяющихся клиентов с одинаковым IP-адресом."""
        if 'last_ip' not in device:
            print(f"Error: 'last_ip' not found for device {device['os_info']['hostname']}")
            return None

        # Извлекаем IP без порта
        current_ip = get_ip_without_port(device['last_ip'])
        matching_clients = DevicesClient.objects.filter(last_ip__startswith=current_ip)

        if matching_clients.exists():
            matching_clients.delete()
            print(f"Clients with IP {current_ip} deleted.")
        else:
            print(f"No clients found with IP {current_ip} in database.")


class UpdateStatusStrategy(DeviceStrategy):
    def save_device(self, device):
        """Обновляет статус устройства на 'Offline' если оно не активно."""
        if 'client_id' not in device:
            print(f"Error: 'client_id' not found for device {device['HostName']}")
            return None

        client = DevicesClient.objects.filter(client_id=device['client_id']).first()

        if client:
            current_time = datetime.datetime.now(pytz.UTC)

            time_difference = (current_time - client.last_seen_at).total_seconds()

            # Если устройство неактивно дольше заданного времени, обновляем статус на 'Offline'
            if time_difference > INACTIVITY_THRESHOLD:
                client.status = 'Offline'
                client.save()
                print(f"Client {client.hostname} marked as offline.")


class DeviceProcessorFacade:
    """
    Фасад для управления стратегиями обработки данных устройств.
    """
    def __init__(self):
        # Стратегии
        self.client_strategies = {
            'save_client': ClientDeviceStrategy(),
            'delete_repeat_clients': DeleteRepeatClientsStrategy(),
            'update_status': UpdateStatusStrategy(),
        }
        self.host_strategy = HostDeviceStrategy()

    def process_clients(self, device_data):
        """
        Обрабатывает только данные клиентов.
        """
        active_clients = []
        for device in device_data:
            #if 'client_id' in device:
            if not is_valid_device(device):
                print(f'Пропущен некорректный клиент: {device}')
                continue
            # Удаляем дубли клиентов перед сохранением
            self.client_strategies['delete_repeat_clients'].save_device(device)

            # Сохраняем данные клиента
            client_id = self.client_strategies['save_client'].save_device(device)
            print(client_id)
            active_clients.append(client_id)

            # Обновляем статус клиента
            self.client_strategies['update_status'].save_device(device)
        return active_clients

    def process_hosts(self, device_data):
        """
        Обрабатывает только данные хостов.
        """
        active_hosts = []
        for device in device_data:
            if 'HostID' in device:
                host_id = self.host_strategy.save_device(device)  # Сохранение хоста
                active_hosts.append(host_id)
        return active_hosts

    def save_all_devices(self, device_data):
        """
        Основной метод фасада для обработки данных всех устройств.
        """
        # Отдельно обрабатываем данные клиентов и хостов
        clients = [d for d in device_data if 'client_id' in d]
        hosts = [d for d in device_data if 'HostID' in d]

        print("Deleting duplicate clients and processing clients...")
        self.process_clients(clients)

        print("Processing host devices...")
        self.process_hosts(hosts)

        print("Processing completed.")


def save_devices_data_facade(device_data):
    """
    Обрабатывает данные устройств с использованием фасада.
    """
    facade = DeviceProcessorFacade()
    print("save_devices_facade")
    facade.save_all_devices(device_data)


#TODO: Вынести в класс
def run(config, query, env_dict):
    """Выполняет gRPC запрос и обрабатывает ответ через фасад."""
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8")
    )
    options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)
    env = [{"key": k, "value": v} for k, v in env_dict.items()]

    with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)
        request = api_pb2.VQLCollectorArgs(
            max_wait=1,
            max_row=100,
            Query=[api_pb2.VQLRequest(Name="Test", VQL=query)],
            env=env,
        )
        for response in stub.Query(request):
            if response.Response:
                try:
                    package = json.loads(response.Response)
                    save_devices_data_facade(package)  # Используем улучшенную функцию
                    print(package)
                    print(len(package))

                except json.JSONDecodeError:
                    print("Error: Failed to decode JSON from server response.")
                except Exception as e:
                     print(f"Error: An unexpected error occurred - {e}")


def upload_artifacts(config: dict, artifact_yaml: str):
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf-8"),
        private_key=config["client_private_key"].encode("utf-8"),
        certificate_chain=config["client_cert"].encode("utf-8")
    )

    options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)

    with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)

        # Создание запроса
        artifact = api_pb2.Artifact(name="Custom.Client.DynamicQuery", data=artifact_yaml)
        request = api_pb2.UploadArtifactRequest(Artifact=artifact)

        # Отправка запроса
        response = stub.UploadArtifact(request)
        return response
