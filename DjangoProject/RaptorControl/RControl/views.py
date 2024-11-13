from .models import DeviceHost, DevicesClient
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import yaml
import os.path
from api_core.api_velociraptor import run


def main_view(request):
    if 'user_id' not in request.session:
        return redirect('login')
    devices = DeviceHost.objects.all()
    clients = DevicesClient.objects.all()
    username = request.session.get('username', None)
    get_devices_data(request)
    return render(request, 'main.html', {'devices': devices, 'devices_client': clients, 'username': username})



def get_devices_data(request):
    try:
        config_path = os.path.join(os.path.dirname('api_core/'), "api_keys/api-admin.config.yaml")
        query = """SELECT * FROM info()"""
        env_dict = {"Foo": "Bar"}

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
              FROM clients(count=100000)"""

        run(config, query, env_dict)


        devices = list(DeviceHost.objects.values())
        clients = list(DevicesClient.objects.values())

        return JsonResponse({'devices': devices, 'clients': clients})

    except Exception as e:
        print("Ошибка в get_devices_data:", e)
        return JsonResponse({'error': str(e)}, status=500)


