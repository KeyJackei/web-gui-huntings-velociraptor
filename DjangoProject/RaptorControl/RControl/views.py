import datetime
import pytz
import grpc
import json
from .models import DeviceHost, DevicesClient
from pyvelociraptor import api_pb2, api_pb2_grpc
import os.path
from django.http import HttpResponse
from django.shortcuts import render
import yaml
import os.path
from dateutil import parser


def main_view(request):
    devices = DeviceHost.objects.all()
    username = request.session.get('username', None)
    return render(request, 'main.html', {'devices': devices, 'username': username})

#Сохранение данных в Postgresql
#TODO: доделать вывод клиентов
def save_devices_data(device_data):
    for device in device_data:
        if 'client_id' in device:
            # Парсим строку с датой
            last_seen_at = parser.isoparse(device['LastSeenAt'])  # isoparse для ISO 8601
            last_seen_at = last_seen_at.replace(tzinfo=pytz.UTC)  # UTC

            DevicesClient.objects.update_or_create(
                hostname=device['HostName'],
                defaults={
                    'client_id': device['client_id'],
                    'os': device['OS'],
                    'release': device['Release'],
                    'last_ip': device['LastIP'],
                    'last_seen_at': last_seen_at,  # Не строка
                }
            )
        else:
            boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
            DeviceHost.objects.update_or_create(
                hostname=device['Hostname'],
                defaults={
                    'uptime': device['Uptime'],
                    'boot_time': boot_time,
                    'procs': device['Procs'],
                    'os_client': device['OS'],
                    'platform': device['Platform'],
                    'kernel_version': device['KernelVersion'],
                    'arch': device['Architecture'],
                }
            )


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
                print(package)
                save_devices_data(package)


def fetch_devices(request):
    # Задайте параметры напрямую
    config_path = os.path.join(os.path.dirname(__file__),
    "api_keys/api-admin.config.yaml")  # Путь к конфигурационному файлу
    query = """SELECT * FROM info()"""
    env_dict = {"Foo": "Bar"}  # Переменные окружения
    # Загрузка конфигурации
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    run(config, query, env_dict)
    query = """SELECT client_id,
                 os_info.fqdn as HostName,
                 os_info.system as OS,
                 os_info.release as Release,
                 timestamp(epoch=last_seen_at/ 1000000).String as LastSeenAt,
                 last_ip AS LastIP,
                 last_seen_at AS _LastSeenAt
          FROM clients(count=100000)"""  # Запрос
    run(config, query, env_dict)
    print('Fetching')
    return HttpResponse(status=200)
