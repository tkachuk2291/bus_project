from rest_framework import serializers
from django.db import transaction
from rest_framework.validators import UniqueTogetherValidator

from station.models import Bus, Trip, Facility, Ticket, Order


# class BusSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     info = serializers.CharField(required=False, max_length=255)
#     num_seats = serializers.IntegerField(required=True)
#
#     def create(self, validated_data):
#         return Bus.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         instance.info = validated_data.get('info', instance.info)
#         instance.num_seats = validated_data.get('num_seats', instance)
#         instance.save()
#         return instance

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ("id", "name")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "seats", "trip")

        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Ticket.objects.all(),
        #         fields=['seats', 'trip']
        #     )
        # ]

    def validate(self, attrs):
        Ticket.validate_seats(
            attrs["seats"],
            attrs["trip"].bus.num_seats,
            serializers.ValidationError
        )
        # if not (1 <= attrs["seats"] <= attrs["trip"].bus.num_seats):
        #     raise serializers.ValidationError(
        #         {"seats": f"Seats must be between 1 and {attrs['trip'].bus.num_seats}"}
        #     )


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ("id", "info", "num_seats", "is_small", "facilities")
        # read_only_fields = ("id")


class BusListSerializer(BusSerializer):
    facilities = FacilitySerializer(many=True)


class BusImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ("id", "image")


class TripSerializer(serializers.ModelSerializer):
    ticket_taken = serializers.IntegerField(read_only=True, source="tickets.count")

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus", "ticket_taken")


class RetrieveTripSerializer(TripSerializer):
    bus = BusListSerializer()
    taken_seats = serializers.SlugRelatedField(many=True, read_only=True, slug_field="seats", source="tickets")

    class Meta:
        model = Trip
        fields = ("id", "source", "destination", "departure", "bus", "taken_seats")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop('tickets')
            print(tickets_data)
            order = Order.objects.create(**validated_data)
            print("order", order)
            for tickets in tickets_data:
                Ticket.objects.create(order=order, **tickets)
            return order
