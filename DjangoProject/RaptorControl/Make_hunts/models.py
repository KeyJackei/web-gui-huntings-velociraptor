from django.db import models

# Create your models here.

class Artifact(models.Model):
    name = models.CharField(max_length=50)
    vql_code = models.CharField(max_length=1024)

