from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    campus = models.CharField(max_length=100)

    def __str__(self):
        return self.username
