from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ], default='user')
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validators.RegexValidator(r'^[\w.@+-]+$')]
    )

    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser
