from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    is_admin = models.BooleanField(default=False)
    campus = models.CharField(max_length=100)

    def __str__(self):
        return self.username