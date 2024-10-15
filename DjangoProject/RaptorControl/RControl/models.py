from django.contrib.auth.hashers import make_password
from django.db import models
from django.views.decorators.http import last_modified

class Devices(models.Model):
    hostname = models.CharField(max_length=255)
    uptime = models.IntegerField()
    boot_time = models.DateTimeField()
    procs = models.IntegerField()
    os = models.CharField(max_length=50)
    platform = models.CharField(max_length=50)
    kernel_version = models.CharField(max_length=50)
    arch = models.CharField(max_length=50)

    def __str__(self):
        return self.hostname

#TODO: Перенести модель в users
class Users(models.Model):
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


