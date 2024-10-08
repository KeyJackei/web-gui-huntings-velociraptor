import datetime
import os.path
import pytz
from django.http import HttpResponse
from django.shortcuts import render, redirect
from pyvelociraptor import api_pb2, api_pb2_grpc
import pyvelociraptor
import grpc
import json
import yaml
from .models import Devices

def login_view(request):
    return render(request, 'login.html')

def main_view(request):
    devices = Devices.objects.all()
    return render(request, 'main.html', {'devices': devices})

#Сохранение данных в PostgreSQL
# def save_devices_data(device_data):
#     for device in device_data:
#         print('save')
#         if isinstance(device['BootTime'], (int, float)):  # Проверяем, что это число
#             boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
#
#         # Используем boot_time вместо device['BootTime']
#         Devices.objects.update_or_create(
#             hostname=device['Hostname'],
#             defaults={
#                 'uptime': device['Uptime'],
#                 'boot_time': boot_time,
#                 'procs': device['Procs'],
#                 'os': device['OS'],
#                 'platform': device['Platform'],
#                 'kernel_version': device['KernelVersion'],
#                 'arch': device['Architecture'],
#             }
#         )

# # Код API
# def run(config, query, env_dict, timeout=0):
#     creds = grpc.ssl_channel_credentials(
#         root_certificates=config["ca_certificate"].encode("utf8"),
#         private_key=config["client_private_key"].encode("utf8"),
#         certificate_chain=config["client_cert"].encode("utf8"))
#
#     options = (('grpc.ssl_target_name_override', "VelociraptorServer",),)
#
#     env = []
#     for k, v in env_dict.items():
#         env.append(dict(key=k, value=v))
#
#     with grpc.secure_channel(config["api_connection_string"], creds, options) as channel:
#         stub = api_pb2_grpc.APIStub(channel)
#
#         request = api_pb2.VQLCollectorArgs(
#             max_wait=1,
#             max_row=100,
#             Query=[api_pb2.VQLRequest(
#                 Name="Test",
#                 VQL=query,
#             )],
#             env=env,
#         )
#
#         for response in stub.Query(request):
#             if response.Response:
#                 package = json.loads(response.Response)
#                 print(package)
#                 save_devices_data(package)
#
# def fetch_devices(request):
#     # Задайте параметры напрямую
#     config_path = os.path.join(os.path.dirname(__file__),
#     "api-connection-user-config/api-keyjackei.config.yaml")  # Путь к конфигурационному файлу
#     #TODO: Сделать так, чтобы в таблицу добавлялись соответствующие данные, которое указаны в заголовках таблицах
#     query = """
# SELECT config.Version.Name AS Name,
#                config.Version.BuildTime as BuildTime,
#                config.Version.Version as Version,
#                config.Version.ci_build_url AS build_url,
#                config.Version.install_time as install_time,
#                config.Labels AS Labels,
#                Hostname, OS, Architecture,
#                Platform, PlatformVersion, KernelVersion, Fqdn,
#                Interfaces.MAC AS MACAddresses
#         FROM info()
# """  # Запрос
#     env_dict = {"Foo": "Bar"}  # Переменные окружения
#     timeout = 100  # Таймаут
#
#     # Загрузка конфигурации
#     with open(config_path, 'r') as config_file:
#         config = yaml.safe_load(config_file) # Загрузка конфигурации из YAML
#
#     run(config, query, env_dict)  # Передайте загруженную конфигурацию
#     print('Fetching')
#
#     return HttpResponse(status=200)  # Возвращаем успешный ответ
