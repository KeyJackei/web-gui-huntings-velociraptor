import datetime
import os.path
import pytz
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from pyvelociraptor import api_pb2, api_pb2_grpc
import grpc
import json
import yaml
from .models import Devices

#TODO:Перенести представления аутентификации в приложение users

def main_view(request):
    devices = Devices.objects.all()
    username = request.session.get('username', None)
    return render(request, 'main.html', {'devices': devices, 'username': username})

# Сохранение данных в PostgreSQL
def save_devices_data(device_data):
    for device in device_data:
        print('save')
        if isinstance(device['BootTime'], (int, float)):  # Проверяем, что это число
            boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)

        # Используем boot_time вместо device['BootTime']
        Devices.objects.update_or_create(
            hostname=device['HostName'],
            defaults={
                'uptime': device['Uptime'],
                'boot_time': boot_time,
                'procs': device['Procs'],
                'os': device['OS'],
                'platform': device['Platform'],
                'kernel_version': device['KernelVersion'],
                'arch': device['Architecture'],
            }
        )

def run(config, query, env_dict, timeout=0):
    creds = grpc.ssl_channel_credentials(
        root_certificates=config["ca_certificate"].encode("utf8"),
        private_key=config["client_private_key"].encode("utf8"),
        certificate_chain=config["client_cert"].encode("utf8"))
    options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)
    env = []
    for k, v in env_dict.items():
        env.append(dict(key=k, value=v))
    with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
        stub = api_pb2_grpc.APIStub(channel)
        request = api_pb2.VQLCollectorArgs(
            max_wait=1,
            max_row=100,
            Query=[api_pb2.VQLRequest(
                Name="Test",
                VQL=query,
            )],
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
    #TODO: Сделать так, чтобы в таблицу добавлялись соответствующие данные, которое указаны в заголовках таблицах
    query = """SELECT client_id,
               os_info.fqdn as HostName,
               os_info.system as OS,
               os_info.release as Release,
               timestamp(epoch=last_seen_at/ 1000000).String as LastSeenAt,
               last_ip AS LastIP,
               last_seen_at AS _LastSeenAt
        FROM clients(count=100000)
        ORDER BY _LastSeenAt DESC""" # Запрос
    env_dict = {"Foo": "Bar"}  # Переменные окружения
    timeout = 100  # Таймаут
    # Загрузка конфигурации
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    run(config, query, env_dict)
    print('Fetching')
    return HttpResponse(status=200)  #
