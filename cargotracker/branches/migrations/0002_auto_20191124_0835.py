# Generated by Django 2.2.7 on 2019-11-24 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("branches", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="branch",
            name="city",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]