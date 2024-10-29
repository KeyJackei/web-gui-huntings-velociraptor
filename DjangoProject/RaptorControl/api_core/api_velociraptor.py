import datetime
import pytz
import grpc
import json
from RControl.models import DeviceHost, DevicesClient
from pyvelociraptor import api_pb2, api_pb2_grpc
from dateutil import parser


#Сохранение данных в Postgresql
#TODO: сделать вывод часового пояса по Asia/Yekaterinburg (понять почему в базе не по гринвичу хранится)
def save_devices_data(device_data):

    #Status by default is inactive.
    #If we got information from API about client or host, status will be active
    DeviceHost.objects.update(status='Inactive')
    DevicesClient.objects.update(status='Inactive')

    for device in device_data:
        if 'client_id' in device:
            # Парсим строку с датой
            print(device)
            last_seen_at = parser.isoparse(device['LastSeenAt'])  # isoparse для ISO 8601
            last_seen_at = last_seen_at.replace(tzinfo=pytz.UTC)  # UTC

            DevicesClient.objects.update_or_create(
                client_id=device['client_id'],
                defaults={
                    'hostname': device['HostName'],
                    'os': device['OS'],
                    'release': device['Release'],
                    'last_ip': device['LastIP'],
                    'last_seen_at': last_seen_at,  # Not a string
                    'status': 'Active',
                }
            )
        else:
            print(device)
            boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
            DeviceHost.objects.update_or_create(
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