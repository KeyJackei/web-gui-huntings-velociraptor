from multiprocessing.managers import Array

from django.contrib.postgres.fields import ArrayField
from django.db import models


class DeviceHost(models.Model):
    hostname = models.CharField(max_length=255)
    boot_time = models.DateTimeField()
    os = models.CharField(max_length=50)
    platform = models.CharField(max_length=50)
    kernel_version = models.CharField(max_length=50)
    arch = models.CharField(max_length=50)
    uptime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.hostname

class DevicesClient(models.Model):
    client_id = models.CharField(max_length=128, unique=True)
    hostname = models.CharField(max_length=255)
    os = models.CharField(max_length=50)
    release = models.CharField(max_length=50)
    last_ip = models.CharField(max_length=50)
    last_seen_at = models.DateTimeField()
    status = models.CharField(max_length=20, default='Offline')
    machine = models.CharField(max_length=255, default="t")
    fqdn = models.CharField(max_length=255, default="t")
    mac_addresses = ArrayField(models.CharField(max_length=17), default=list)
    first_seen_at = models.DateTimeField(default='2025-02-03 11:56:37+05')
    last_interrogate_flow_id = models.CharField(max_length=255, default="t")
    last_interrogate_artifact_name = models.CharField(max_length=255, default="t")
    last_hunt_timestamp = models.BigIntegerField(default=0)

    def __str__(self):
        return self.hostname


class QueryVQL(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    query_vql = models.TextField()

