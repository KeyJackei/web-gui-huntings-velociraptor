import datetime
import pytz
import grpc
import json
from RControl.models import DeviceHost, DevicesClient
from pyvelociraptor import api_pb2, api_pb2_grpc
from dateutil import parser

# Helper Functions
def get_ip_without_port(last_ip):
    """Extract IP address from 'IP:port' format."""
    return last_ip.split(':')[0]


def delete_repeat_clients(device_data):
    """Delete existing clients with matching IPs from the database."""
    for device in device_data:
        if 'LastIP' in device:
            current_ip = get_ip_without_port(device['LastIP'])
            matching_clients = DevicesClient.objects.filter(last_ip__startswith=current_ip)
            if matching_clients.exists():
                matching_clients.delete()
                print(f"Clients with IP {current_ip} deleted.")
            else:
                print(f"No clients found with IP {current_ip} in database.")


def save_device_client(device):
    """Save or update client device information in the database."""
    last_seen_at = parser.isoparse(device['LastSeenAt']).replace(tzinfo=pytz.UTC)

    client, created = DevicesClient.objects.update_or_create(
        client_id=device['client_id'],
        defaults={
            'hostname': device['HostName'],
            'os': device['OS'],
            'release': device['Release'],
            'last_ip': device['LastIP'],
            'last_seen_at': last_seen_at,
            'status': 'Active',  # Default active
        }
    )
    print(f"Client updated: {client.hostname}, Status: {client.status}")
    return client.id


def save_device_host(device):
    """Save or update host device information in the database."""
    boot_time = datetime.datetime.fromtimestamp(device['BootTime'], tz=pytz.UTC)
    uptime_seconds = device['Uptime']
    last_seen_at = boot_time + datetime.timedelta(seconds=uptime_seconds)

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
            'status': 'Active'  # Default active
        }
    )
    print(f"Host updated: {host.hostname}, Status: {host.status}")
    return host.id


def update_device_status_based_on_data(device_data):
    """Update device status based on the presence of data in the incoming device array."""
    # Get all devices from the database and create a set of their IPs (without ports)
    existing_devices = DevicesClient.objects.all()
    existing_ips = {get_ip_without_port(device.last_ip) for device in existing_devices}

    # Create a set of IPs from incoming data (ignoring ports)
    incoming_ips = {get_ip_without_port(device['LastIP']) for device in device_data if 'LastIP' in device}

    # Check for new devices (in incoming data but not in database)
    new_devices = incoming_ips - existing_ips
    for device in device_data:
        device_ip = get_ip_without_port(device['LastIP'])
        if device_ip in new_devices:
            save_device_client(device)
            print(f"New device added: {device['HostName']} with IP: {device_ip}")

    # Mark devices as inactive (in database but not in incoming data)
    inactive_ips = existing_ips - incoming_ips
    DevicesClient.objects.filter(last_ip__in=[f"{ip}:" for ip in inactive_ips]).update(status='Inactive')
    print(f"Devices marked as inactive: {inactive_ips}")


def save_devices_data(device_data):
    """Main function to save device data and update inactive statuses based on new logic."""
    delete_repeat_clients(device_data)

    active_clients = []
    active_hosts = []

    for device in device_data:
        if 'client_id' in device:
            active_clients.append(save_device_client(device))
        if 'HostID' in device:
            active_hosts.append(save_device_host(device))

    # Update inactive status for non-active clients and hosts based on received data
    update_device_status_based_on_data(device_data)


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
                    print(package)
                    print(len(package))

                except json.JSONDecodeError:
                    print("Error: Failed to decode JSON from server response.")
                except Exception as e:
                    print(f"Error: An unexpected error occurred - {e}")
