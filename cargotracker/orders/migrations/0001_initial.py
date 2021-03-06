# Generated by Django 2.2.7 on 2019-11-28 05:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("cargo", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(decimal_places=3, default=0.0, max_digits=12),
                ),
                (
                    "price_per_unit_weight",
                    models.DecimalField(decimal_places=3, max_digits=7),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("P", "pending"),
                            ("T", "in transit"),
                            ("D", "delivered"),
                        ],
                        default="P",
                        max_length=1,
                    ),
                ),
                ("past_main_branch", models.BooleanField(default=False)),
                (
                    "estimated_time_to_main_station",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "estimated_delivery_time",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("actual_delivery_time", models.DateTimeField(blank=True, null=True)),
                ("cargo_picked_up", models.BooleanField(default=False)),
                (
                    "cargo",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="order",
                        to="cargo.Cargo",
                    ),
                ),
            ],
        ),
    ]
