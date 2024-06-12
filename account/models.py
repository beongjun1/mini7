from django.db import models
from django.urls import reverse

from django.conf import settings

class User(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=50)

