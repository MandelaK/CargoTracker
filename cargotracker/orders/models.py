from decimal import Decimal
import random
from datetime import timedelta, datetime
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.timezone import make_aware

from cargo.models import Cargo
from cargotracker.UTILS.tasks import send_async_email

Q = models.Q


class OrderQuerySet(models.QuerySet):
    """
    QuerySet for the Orders object.
    """

    def for_user(self, user=None):
        """
        Return all orders for a specific user.
        """

        return self.filter(Q(cargo__recepient=user) | Q(cargo__sender=user))

    def for_agent(self, agent=None):
        """
        Return all orders that involve a specific agent.
        """

        return self.filter(
            Q(cargo__booking_agent=agent) | Q(cargo__clearing_agent=agent)
        )


class OrderManager(models.Manager):
    """
    Manager for the Oder class.
    """

    def get_queryset(self):
        return OrderQuerySet(self.model, using=self.db)

    def check_cargo_order(self, cargo):
        """
        Check if this cargo already has an order associated with it.
        """
        qs = self.model.objects.get_queryset().filter(cargo=cargo)
        if qs.exists():
            return qs.first()
        return None

    def get_or_create_order(
        self, cargo=None, price_per_unit_weight=0.00, past_main_branch=False, **kwargs
    ):
        """
        Method to actually create an order. If an order already exists, return it instead.
        """

        created = False

        if self.check_cargo_order(cargo):
            return self.check_cargo_order(cargo), created
        if not isinstance(cargo, Cargo):
            raise TypeError("Please provide cargo instance.")
        if Decimal(price_per_unit_weight) <= 0:
            raise TypeError("Please provide the price for this order greater than 0.")

        order = self.model.objects.create(
            cargo=cargo,
            price_per_unit_weight=price_per_unit_weight,
            past_main_branch=past_main_branch,
            **kwargs,
        )
        order.save()
        created = True
        return order, created


class Order(models.Model):
    """
    Represents an Order instance.
    """

    STATUS_CHOICES = [
        ("P", "pending"),
        ("T", "in transit"),
        ("D", "delivered"),
    ]

    cargo = models.OneToOneField(
        Cargo, on_delete=models.SET_NULL, null=True, related_name="order"
    )
    price = models.DecimalField(max_digits=12, decimal_places=3, default=0.00)
    price_per_unit_weight = models.DecimalField(max_digits=7, decimal_places=3)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
    past_main_branch = models.BooleanField(default=False)
    estimated_time_to_main_station = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    cargo_picked_up = models.BooleanField(default=False)
    tracking_id = models.UUIDField(default=uuid.uuid4, null=False, blank=True)

    objects = OrderManager()

    def __str__(self):
        """
        Return useful representation.
        """
        return f"{self.cargo}"

    def calculate_price(self):
        """
        Calculate the price of the order.
        """

        cargo_weight = self.cargo.weight
        tax_rate = Decimal(0.18)

        untaxed_total = Decimal(cargo_weight) * Decimal(self.price_per_unit_weight)

        total_price = (untaxed_total * tax_rate) + untaxed_total

        return total_price

    def approximate_delivery_time(self):
        """
        Just return a random range to act as expectation of when the cargo will be delivered.
        """
        # this is set to seconds just of demonstration
        approx_delivery_time = random.randrange(300, 600)
        approx_time_to_main_station = approx_delivery_time / 2

        return {
            "delivery_time": approx_delivery_time,
            "time_to_station": approx_time_to_main_station,
        }

    def _set_time_approximations(self):
        """
        Actually set the time approximations.
        """
        time_dict = self.approximate_delivery_time()

        self.estimated_delivery_time = make_aware(datetime.now() + timedelta(
            seconds=time_dict.get("delivery_time"))
        )
        self.estimated_time_to_main_station = make_aware(datetime.now() + timedelta(
            seconds=time_dict.get("time_to_station"))
        )

        return True

    def _set_order_price(self):
        """
        Set the final price of the order.
        """

        price = self.calculate_price()
        self.price = price
        return self.price


def post_save_order_receiver(sender, instance, created, *args, **kwargs):
    """
    Whenever an order is created, do the following.
    """
    sender_email = instance.cargo.sender.email
    recepient_email = instance.cargo.recepient.email

    booking_agent = instance.cargo.booking_station.branch_agent.email

    if created:
        instance._set_order_price()
        instance._set_time_approximations()
        price = instance.price

        subject = "Order Finalized and ready to go."
        message = f"Your cargo has been booked and is ready for delivery. You will be notified whenever the status changes. It is currently {instance.get_status_display().title()}. It cost a total of ${price:.3f}. Your booking agent is {booking_agent}"

        send_async_email(
            subject=subject,
            message=message,
            sender=booking_agent,
            recepients=[sender_email, recepient_email],
        )


post_save.connect(post_save_order_receiver, sender=Order)
