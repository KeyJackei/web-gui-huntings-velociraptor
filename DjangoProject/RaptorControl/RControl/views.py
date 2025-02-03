from .models import DeviceHost, QueryVQL, DevicesClient
from django.http import JsonResponse
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

#TODO: function for get info about client in modal window
def get_client_details(request):
    fields = DevicesClient._meta.get_fields()
    field_names = [field.name for field in fields]

    return JsonResponse({'fields': field_names})

def get_filtered_device(request):
    status = request.GET.get('status', 'total')
    if status == 'active':
        devices = DevicesClient.objects.filter(status='Connected')
    elif status == 'inactive':
        devices = DevicesClient.objects.filter(status='Disconnected')
    else:
        devices = DevicesClient.objects.all()

    devices_data = list(devices.values(
        'client_id', 'hostname', 'os', 'release', 'last_ip', 'last_seen_at', 'status'
    ))

    for device in devices_data:
        if device['last_seen_at']:
            device['last_seen_at'] = device['last_seen_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            device['last_seen_at'] = "N/A"

    return JsonResponse({'devices': devices_data})



#Counting connected and disconnected clients
def get_devices_counts(request):
    connected_count = DevicesClient.objects.filter(status='Online').count()
    disconnected_count = DevicesClient.objects.filter(status='Offline').count()
    total_count = DevicesClient.objects.count()

    data = JsonResponse({
        'connected_count': connected_count,
        'disconnected_count': disconnected_count,
        'total_count': total_count
    })


    return data

# Получение запроса VQL из базы
def get_query_by_name(name):
    try:
        record = QueryVQL.objects.get(name=name)
        return record.query_vql
    except QueryVQL.DoesNotExist:
        return None

def get_devices_data(request):
    try:
        #Возможно ошибки
        config_path = os.path.join(os.path.dirname('api_core/'), "api_keys/api-admin.config.yaml")
        query = get_query_by_name('get_server_info')
        env_dict = {"Foo": "Bar"}

        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        run(config, query, env_dict)

        query = get_query_by_name('get_clients_info')
        run(config, query, env_dict)

        devices = list(DeviceHost.objects.values())
        clients = list(DevicesClient.objects.values())

        return JsonResponse({'devices': devices, 'clients': clients})

    except Exception as e:
        print("Ошибка в get_devices_data:", e)
        return JsonResponse({'error': 'Server communication failed'}, status=200)


