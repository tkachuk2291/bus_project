# Generated by Django 5.0.4 on 2024-04-24 21:03

import station.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("station", "0007_bus_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bus",
            name="facilities",
            field=models.ManyToManyField(
                blank=True, related_name="buses", to="station.facility"
            ),
        ),
        migrations.AlterField(
            model_name="bus",
            name="image",
            field=models.ImageField(null=True, upload_to=station.models.bus_image_path),
        ),
    ]