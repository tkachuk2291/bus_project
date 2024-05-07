import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Facility(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'facilities'

    def __str__(self):
        return self.name


def bus_image_path(instance, filename):
    filename = f'{slugify(instance.info)}-{uuid.uuid4()}' + pathlib.Path(filename).suffix
    return pathlib.Path("upload/buses/") / pathlib.Path(filename)


class Bus(models.Model):
    info = models.CharField(max_length=255, null=True)
    num_seats = models.IntegerField()
    facilities = models.ManyToManyField(Facility, related_name="buses", blank=True)
    image = models.ImageField(null=True, upload_to=bus_image_path)

    class Meta:
        verbose_name_plural = "buses"

    @property
    def is_small(self):
        return self.num_seats <= 25

    def __str__(self):
        return f"Bus: {self.info} (id = {self.id})"


class Trip(models.Model):
    source = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure = models.DateTimeField()
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="bus")

    class Meta:
        indexes = [
            models.Index(fields=["source", "destination"]),
            models.Index(fields=["departure"])
        ]

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.departure})"


class Ticket(models.Model):
    seats = models.IntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        # constraints = [
        #     UniqueConstraint(fields=["seats", "trip"], name="unique_ticket_seats_trip")
        # ]
        unique_together = ("seats", "trip")
        ordering = ("seats",)

    def __str__(self):
        return f"{self.trip} - (seats - {self.seats})"

    @staticmethod
    def validate_seats(seat: int, num_seats: int, error_to_raise):
        if not (1 <= seat <= num_seats):
            raise error_to_raise(
                {"seats": f"Seats must be between 1 and {num_seats}"}
            )

    def clean(self):
        Ticket.validate_seats(self.seat, self.trip.bus.num_seats, ValueError)

    def save(self, force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update, using, update_fields)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)
