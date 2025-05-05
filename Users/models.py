from django.db import models
from django.contrib.auth.hashers import make_password


class Users(models.Model):
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

