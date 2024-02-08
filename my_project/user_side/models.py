from django.db import models

# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(max_length=200,unique=True)
    phone = models.CharField(max_length=12,blank=True)