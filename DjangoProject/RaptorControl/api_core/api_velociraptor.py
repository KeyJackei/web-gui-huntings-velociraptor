import datetime
import pytz
import grpc
import json
from RControl.models import DeviceHost, DevicesClient
from django.db import transaction
from pyvelociraptor import api_pb2, api_pb2_grpc
from dateutil import parser


#Сохранение данных в Postgresql

#TODO: Пофиксить обновление статуса, когда устройства не в сети и в сети

#Function refreshing data in PostgreSQL - delete old data and writing new one
#This functions update data, when get a new response from server

def delete_repeat_clients(device_data):

    for device in device_data:
        if 'LastIP' in device:
            current_ip, _ = device['LastIP'].split(':', 1)
            matching_clients = DevicesClient.objects.filter(last_ip__startswith=current_ip)

            if matching_clients.exists():
                matching_clients.delete()
                print(f'Клиенты с IP {current_ip} удалены')
            else:
                print(f'Клиенты с IP {current_ip} не найдены в базе')

def save_devices_data(device_data):
    delete_repeat_clients(device_data)

    active_clients = []
    active_hosts = []

    current_time = datetime.datetime.now(tz=pytz.UTC)

    for device in device_data:
        if 'client_id' in device:
            last_seen_at = parser.isoparse(device['LastSeenAt'])
            last_seen_at = last_seen_at.replace(tzinfo=pytz.UTC)

            inactivity_duration = (current_time - last_seen_at).total_seconds()
            if inactivity_duration > 10:  # Если клиент не обновлялся более 10 секунд
                status = 'Inactive'
            else:
                status = 'Active'

            client, created = DevicesClient.objects.update_or_create(
                client_id=device['client_id'],
                defaults={
                    'hostname': device['HostName'],
                    'os': device['OS'],
                    'release': device['Release'],
                    'last_ip': device['LastIP'],
                    'last_seen_at': last_seen_at,
                    'status': status,
                }
            )
            active_clients.append(client.id)
            print(f"Обновлён клиент: {client.hostname}, статус: {client.status}")

    # Обработка хостов
    for device in device_data:
        if 'HostID' in device:
            boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
            host, created = DeviceHost.objects.update_or_create(
                hostname=device['Hostname'],
                defaults={
                    'uptime': device['Uptime'],
                    'boot_time': boot_time,
                    'procs': device['Procs'],
                    'os': device['OS'],
                    'platform': device['Platform'],
                    'kernel_version': device['KernelVersion'],
                    'arch': device['Architecture'],
                    'status': 'Active'
                }
            )
            active_hosts.append(host.id)
            print(f"Обновлён хост: {host.hostname}, статус: {host.status}")

    # Обновляем статус для неактивных клиентов и хостов
    DeviceHost.objects.exclude(id__in=active_hosts).update(status='Inactive')
    DevicesClient.objects.exclude(id__in=active_clients).update(status='Inactive')





def run(config, query, env_dict):
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8"))
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
                package = json.loads(response.Response)
        save_devices_data(package)