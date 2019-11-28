import uuid

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.shortcuts import reverse

from branches.models import Branch
from cargotracker.UTILS import validate_required_kwargs_are_not_empty
from cargotracker.UTILS.tasks import send_async_email


User = settings.AUTH_USER_MODEL

Q = models.Q


class CargoQuerySet(models.QuerySet):
    """
    Queryset for reusable queries of the Cargo object.
    """

    def all_cargo_for_user(self, user=None):
        """
        Return all the Cargo involving a user, whether they sent it or received it.
        """

        return self.filter(Q(sender=user) | Q(recepient=user))

    def cargo_sent_by_user(self, sender=None):

        return self.filter(sender=sender)

    def cargo_received_by_user(self, recepient=None):

        return self.filter(recepient=recepient)

    def cargo_booked_by_agent(self, booking_agent=None):

        return self.filter(booking_agent=booking_agent)

    def cargo_handled_by_agent(self, agent=None):
        """
        All cargo either booked or cleared by the provided agent.
        """
        return self.filter(Q(booking_agent=agent) | Q(clearing_agent=agent))

    def cargo_by_tracking_id(self, tracking_id=None):
        qs = self.filter(tracking_id=str(tracking_id))
        return qs.first() if qs.exists() else None


class CargoManager(models.Manager):
    """
    Manager class to help with managing the Cargo instance.
    """

    def get_queryset(self):
        return CargoQuerySet(self.model, using=self.db)

    def create_cargo(self, **kwargs):
        """
        Create cargo before an order can be generated.
        :args:
        sender - User instance representing the sender of cargo
        title - Name of the cargo
        recepient - User instance representing the recepient of cargo
        destination - Instance representing the destination branch of cargo
        weight - Weight of cargo
        booking_agent - agent that handled booking
        :return: cargo instance
        """

        KWARGS_LIST = (
            "sender",
            "title",
            "recepient",
            "destination",
            "weight",
            "booking_station",
            "booking_agent",
        )
        validate_required_kwargs_are_not_empty(KWARGS_LIST, kwargs)

        if kwargs.get("sender").id == kwargs.get("recepient").id:
            raise TypeError("Users cannot send themselves parcels.")

        if (
            kwargs.get("booking_agent").email
            != kwargs.get("booking_station").branch_agent.email
        ):
            raise TypeError("You can only book cargo for your station.")

        cargo = self.model.objects.create(**kwargs)
        cargo.save()
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
    booking_agent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="booked_cargo"
    )
    booking_station = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="sent_cargo"
    )
    clearing_agent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cleared_cargo"
    )
    current_location = models.CharField(max_length=50, default="pending")
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    objects = CargoManager()

    def __str__(self):
        """
        Return a helpful string representation.
        """
        return f"{self.title} for {self.recepient} in {self.destination}."

    def get_absolute_url(self):
        """
        Return url for each instance.
        """
        return reverse("cargo:cargo-detail", args=[self.id])


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
