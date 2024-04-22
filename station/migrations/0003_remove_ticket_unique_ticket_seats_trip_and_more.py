# Generated by Django 5.0.4 on 2024-04-17 09:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0002_bus_facilities'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ticket',
            name='unique_ticket_seats_trip',
        ),
        migrations.AlterField(
            model_name='ticket',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='station.order'),
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('seats', 'trip')},
        ),
    ]
