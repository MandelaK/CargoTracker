from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User that extends User
    """

    email = models.EmailField(max_length=255, unique=True, blank=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

