import datetime
import math

import pytz
import grpc
import json
from RControl.models import DeviceHost, DevicesClient
from pyvelociraptor import api_pb2, api_pb2_grpc
from dateutil import parser

# Constants
INACTIVITY_THRESHOLD = 10  # seconds


# Helper Functions
def delete_repeat_clients(device_data):
    """Delete existing clients with matching IPs from the database."""
    for device in device_data:
        if 'LastIP' in device:
            current_ip, _ = device['LastIP'].split(':', 1)
            matching_clients = DevicesClient.objects.filter(last_ip__startswith=current_ip)
            if matching_clients.exists():
                matching_clients.delete()
                print(f"Clients with IP {current_ip} deleted.")
            else:
                print(f"No clients found with IP {current_ip} in database.")


def determine_status(last_seen_at, current_time):
    """Determine the active/inactive status based on inactivity duration."""
    inactivity_duration = math.floor((current_time - last_seen_at).total_seconds())
    return 'Inactive' if inactivity_duration > INACTIVITY_THRESHOLD else 'Active'


def save_device_client(device, current_time):
    """Save or update client device information in the database."""
    last_seen_at = parser.isoparse(device['LastSeenAt']).replace(tzinfo=pytz.UTC)
    status = determine_status(last_seen_at, current_time)

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
    print(f"Client updated: {client.hostname}, Status: {client.status}")
    return client.id


def save_device_host(device):
    """Save or update host device information in the database."""
    boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
    uptime_seconds = device['Uptime']
    current_time = datetime.datetime.now(tz=pytz.UTC)
    last_seen_at = boot_time + datetime.timedelta(seconds=uptime_seconds)
    status = determine_status(last_seen_at, current_time)
    print(last_seen_at)

    host, created = DeviceHost.objects.update_or_create(
        hostname=device['Hostname'],
        defaults={
            'uptime': last_seen_at,
            'boot_time': boot_time,
            'procs': device['Procs'],
            'os': device['OS'],
            'platform': device['Platform'],
            'kernel_version': device['KernelVersion'],
            'arch': device['Architecture'],
            'status': status
        }
    )
    print(f"Host updated: {host.hostname}, Status: {host.status}")
    return host.id


def save_devices_data(device_data):
    """Main function to save device data and update inactive statuses."""
    delete_repeat_clients(device_data)

    current_time = datetime.datetime.now(tz=pytz.UTC)
    active_clients = []
    active_hosts = []

    for device in device_data:
        if 'client_id' in device:
            active_clients.append(save_device_client(device, current_time))
        if 'HostID' in device:
            active_hosts.append(save_device_host(device))

    # Update inactive status for non-active clients and hosts
    DeviceHost.objects.exclude(id__in=active_hosts).update(status='Inactive')
    DevicesClient.objects.exclude(id__in=active_clients).update(status='Inactive')


def run(config, query, env_dict):
    """Execute the gRPC query and process the response to save device data."""
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
                    save_devices_data(package)
                except json.JSONDecodeError:
                    print("Error: Failed to decode JSON from server response.")
                except Exception as e:
                    print(f"Error: An unexpected error occurred - {e}")
