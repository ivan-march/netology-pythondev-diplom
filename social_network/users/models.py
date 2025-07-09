from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    USERNAME_FIELD = 'username'
