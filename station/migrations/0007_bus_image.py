# Generated by Django 5.0.4 on 2024-04-21 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0006_alter_ticket_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]