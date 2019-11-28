from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import IntegrityError
from django.conf import settings

from cargotracker.UTILS.tasks import send_async_email


class UserManager(BaseUserManager):
    """
    Provide manager methods for creating User instances
    """

    def create_user(self, **kwargs):
        """
        Ensure that users are created with valid passwords.
        """

        if not kwargs.get("email"):
            raise TypeError("Users must have an email address.")

        if not kwargs.get("password"):
            raise TypeError("Users must have a password.")

        try:
            user = self.model.objects.create(**kwargs)
            user.is_active = True
            user.set_password(kwargs.get("password"))
            user.save()

            return user

        except IntegrityError as e:
            raise TypeError("A user with this username or email already exists.") from e

    def create_branch_agent(self, *args, **kwargs):
        """
        Branch agents are special types of Users who can only be created by the Admin.
        """

        user = self.create_user(**kwargs)

        user.is_staff = True
        user.save()

        agent_email = user.email
        sender = settings.ADMIN_EMAIL
        subject = "Account Created Succesfully."
        message = f"Hi. Your branch agent account was succesfully created. Your login credentials are: Email: {kwargs.get('email')} . Password: {kwargs.get('password')}."

        send_async_email(
            subject=subject, message=message, sender=sender, recepients=[agent_email,]
        )

        return user

    def create_superuser(self, **kwargs):
        """
        Ensure that users are created with valid passwords.
        """
        user = self.create_user(**kwargs)

        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def get_user(self, **kwargs):
        """
        Attempt to find the first user with the matching arguments.
        """

        qs = User.objects.filter(**kwargs)
        if qs.exists():
            return qs.first()
        return None


class User(AbstractUser):
    """
    Custom User that extends User
    """

    email = models.EmailField(max_length=255, unique=True, blank=False)
    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []
