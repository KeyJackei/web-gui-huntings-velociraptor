import datetime
import pytz
import grpc
import json
from abc import ABC, abstractmethod
from RControl.models import DeviceHost, DevicesClient
from pyvelociraptor import api_pb2, api_pb2_grpc
from dateutil import parser


INACTIVITY_THRESHOLD = 15

def get_ip_without_port(last_ip):
    """Extract IP address from 'IP:port' format."""
    return last_ip.split(':')[0]


class DeviceStrategy(ABC):
    @abstractmethod
    def save_device(self, device):
        """Save or update device information in the database."""
        pass



class ClientDeviceStrategy(DeviceStrategy):
    def save_device(self, device):
        """Save or update client device information in the database."""
        if 'LastIP' not in device:
            print(f"Error: 'LastIP' not found for device {device['HostName']}")
            return None

        last_seen_at = parser.isoparse(device['LastSeenAt']).replace(tzinfo=pytz.UTC)

        client, created = DevicesClient.objects.update_or_create(
            client_id=device['client_id'],
            defaults={
                'hostname': device['HostName'],
                'os': device['OS'],
                'release': device['Release'],
                'last_ip': device['LastIP'],
                'last_seen_at': last_seen_at,
                'status': 'Connected',  # Default active
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
        if 'LastIP' not in device:
            print(f"Error: 'LastIP' not found for device {device['HostName']}")
            return None

        # Извлекаем IP без порта
        current_ip = get_ip_without_port(device['LastIP'])

        # Находим всех клиентов с таким IP
        matching_clients = DevicesClient.objects.filter(last_ip__startswith=current_ip)

        # Если такие клиенты есть, удаляем их
        if matching_clients.exists():
            matching_clients.delete()
            print(f"Clients with IP {current_ip} deleted.")
        else:
            print(f"No clients found with IP {current_ip} in database.")


class UpdateStatusStrategy(DeviceStrategy):
    def save_device(self, device):
        """Обновляет статус устройства на 'Disconnected' если оно не активно."""
        if 'client_id' not in device:
            print(f"Error: 'client_id' not found for device {device['HostName']}")
            return None

        client = DevicesClient.objects.filter(client_id=device['client_id']).first()

        if client:
            # Получаем текущее время
            current_time = datetime.datetime.now(pytz.UTC)

            # Рассчитываем разницу во времени с последнего обновления
            time_difference = (current_time - client.last_seen_at).total_seconds()

            # Если устройство неактивно дольше заданного времени, обновляем статус на 'Disconnected'
            if time_difference > INACTIVITY_THRESHOLD:
                client.status = 'Disconnected'
                client.save()
                print(f"Client {client.hostname} marked as disconnected.")


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
            if 'client_id' in device:
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



# Пример использования фасада в функции run
def save_devices_data_facade(device_data):
    """
    Обрабатывает данные устройств с использованием фасада.
    """
    facade = DeviceProcessorFacade()
    print("save_devices_facade")
    facade.save_all_devices(device_data)


# Пример использования фасада в функции run
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
                    print(package)
                    save_devices_data_facade(package)  # Используем улучшенную функцию
                    print(package)
                    print(len(package))

                except json.JSONDecodeError:
                    print("Error: Failed to decode JSON from server response.")
                except Exception as e:
                     print(f"Error: An unexpected error occurred - {e}")


# # Main Function to Save Devices
# # Основная функция теперь использует фасад
# def save_devices_data(device_data):
#     """Main function to save device data and update inactive statuses."""
#     facade = DeviceProcessorFacade()
#     facade.save_all_devices(device_data)  # Теперь фасад сам всё обрабатывает


# class DeviceContext:
#     def __init__(self, strategy: DeviceStrategy):
#         self.strategy = strategy
#
#     def execute(self, device):
#         return self.strategy.save_device(device)


# class DeviceProcessorFacade:
#     """
#     Фасад для управления стратегиями обработки данных устройств.
#     """
#     def __init__(self):
#         # Стратегии
#         self.strategies = {
#             'save_client': ClientDeviceStrategy(),
#             'save_host': HostDeviceStrategy(),
#             'delete_repeat_clients': DeleteRepeatClientsStrategy(),
#             'update_status': UpdateStatusStrategy(),
#         }
#
#     def process_clients(self, device_data):
#         """
#         Обрабатывает только данные клиентов.
#         """
#         self.strategies['delete_repeat_clients'].save_device(device_data)  # Удаление повторяющихся клиентов
#         active_clients = []
#         for device in device_data:
#             if 'client_id' in device:
#                 client_id = self.strategies['save_client'].save_device(device)  # Сохранение клиента
#                 print(client_id)
#                 active_clients.append(client_id)
#         return active_clients
#
#     def process_hosts(self, device_data):
#         """
#         Обрабатывает только данные хостов.
#         """
#         active_hosts = []
#         for device in device_data:
#             if 'HostID' in device:
#                 host_id = self.strategies['save_host'].save_device(device)  # Сохранение хоста
#                 active_hosts.append(host_id)
#         return active_hosts
#
#     def update_device_status(self, device_data):
#         """
#         Обновляет статус устройств.
#         """
#         self.strategies['update_status'].save_device(device_data)
#
#     def save_all_devices(self, device_data):
#         """
#         Основной метод фасада для обработки данных всех устройств.
#         """
#         print("Deleting duplicate clients...")
#         self.process_clients(device_data)
#         print("Processing host devices...")
#         self.process_hosts(device_data)
#         print("Updating device statuses...")
#         self.update_device_status(device_data)
#         print("Processing completed.")

