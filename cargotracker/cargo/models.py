import uuid

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from branches.models import Branch
from cargotracker.UTILS import validate_required_kwargs_are_not_empty
from cargotracker.UTILS.tasks import send_async_email


User = settings.AUTH_USER_MODEL


class CargoManager(models.Manager):
    """
    Manager class to help with managing the Cargo instance.
    """

    def create_cargo(self, **kwargs):
        """
        Create cargo before an order can be generated.
        :args:
        sender - User instance representing the sender of cargo
        title - Name of the cargo
        recepient - User instance representing the recepient of cargo
        destination - Instance representing the destination branch of cargo
        weight - Weight of cargo
        :return: cargo instance
        """

        KWARGS_LIST = ("sender", "title", "recepient", "destination", "weight")
        validate_required_kwargs_are_not_empty(KWARGS_LIST, kwargs)

        if kwargs.get("sender").id == kwargs.get("recepient").id:
            raise TypeError("Users cannot send themselves parcels.")

        cargo = self.model.objects.create(**kwargs)
        return cargo


class Cargo(models.Model):
    """
    Model that defines the Cargo.
    """

    STATUS_CHOICES = [
        ("P", "pending"),
        ("T", "in transit"),
        ("D", "delivered"),
    ]

    title = models.CharField(max_length=100)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_cargo"
    )
    recepient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_cargo"
    )
    destination = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="cargo_received"
    )
    booking_station = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="cargo_sent"
    )
    current_location = models.CharField(max_length=50, default="pending")
    uuid = models.UUIDField(primary_key=False, editable=False, default=uuid.uuid4)
    # past_main_branch = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    # price = models.DecimalField(max_digits=12, decimal_places=3)
    # booking_agent = models.OneToOneField(User, on_delete=models.CASCADE)
    # status = models.CharField(choices=STATUS_CHOICES, max_length=1)

    objects = CargoManager()

    def __str__(self):
        """
        Return a helpful string representation.
        """
        return f"{self.title} for {self.recepient} in {self.destination}."


def post_save_cargo_created_receiver(sender, instance, created, *args, **kwargs):
    """
    This signal is fired whenever a new cargo is created.
    """

    # if a new cargo instance was created, then we should send an email to the branch agent at the pickup branch so they may record the booking.

    if created:
        agent = instance.booking_station.branch_agent

        subject = "Book new order."
        message = f"Hello. A new order was made at the CargoTracker branch in {instance.booking_station.city}. As the admin of the branch, please proceed and record the order for it to be sent to its destination."
        recepient = agent.email

        send_async_email(
            subject=subject,
            message=message,
            sender=instance.sender.email,
            recepients=[recepient,],
        )


post_save.connect(post_save_cargo_created_receiver, sender=Cargo)
