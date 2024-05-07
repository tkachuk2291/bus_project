from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from station.models import Bus, Facility
from station.serializers import BusSerializer, BusListSerializer, FacilitySerializer

BUS_URL = reverse("station:buses-list")


def detail_url(bus_id):
    return reverse("station:buses-detail", args=(bus_id,))


def sample_buses(**params):
    defaults = {
        "info": "Test bus info",
        "num_seats": 50,
    }
    defaults.update(params)
    return Bus.objects.create(**defaults)


class UnauthenticatedBusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated(self):
        response = self.client.get(BUS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_authenticated(self):
        response = self.client.get(BUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bus_list(self):
        sample_buses()
        bus_facilities = sample_buses()
        facilities_1 = Facility.objects.create(name="Facility 1")
        facilities_2 = Facility.objects.create(name="Facility 2")

        bus_facilities.facilities.add(facilities_1, facilities_2)

        response = self.client.get(BUS_URL)
        buses = Bus.objects.all()
        serializer = BusListSerializer(buses, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_buses_by_facility(self):
        buses_without_facilities = sample_buses()
        bus_facilities_1 = sample_buses(info="Test bus info")
        bus_facilities_2 = sample_buses(info="Test bus info")
        facilities_1 = Facility.objects.create(name="Wifi")
        facilities_2 = Facility.objects.create(name="WC")
        bus_facilities_1.facilities.add(facilities_1)
        bus_facilities_2.facilities.add(facilities_2)
        response = self.client.get(BUS_URL, {"facilities": f"{facilities_1.id},{facilities_2.id}"})
        serializer_without_facilities = BusListSerializer(buses_without_facilities)
        serializer_bus_facilities_1 = BusListSerializer(bus_facilities_1)
        serializer_bus_facilities_2 = BusListSerializer(bus_facilities_2)
        self.assertIn(serializer_bus_facilities_1.data, response.data)
        self.assertIn(serializer_bus_facilities_2.data, response.data)
        self.assertNotIn(serializer_without_facilities, response.data)

    def test_retrieve_facilities_bus_detail(self):
        bus = sample_buses()
        bus.facilities.add(Facility.objects.create(name="Wifi"))
        url = detail_url(bus.id)
        response = self.client.get(url)
        serializer = BusSerializer(bus)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_bus_forbidden(self):
        payload = {
            "info": "Avtobus 500",
            "num_seats": 50
        }
        response = self.client.post(BUS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBusTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuseradmin",
            password="testpasswordadmin",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_admin_bus(self):
        payload = {
            "info": "Avtobus 500",
            "num_seats": 50
        }
        response = self.client.post(BUS_URL, payload)
        bus = Bus.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(bus, key))

    def test_create_admin_bus_with_facilities(self):
        facilities_1 = Facility.objects.create(name="Facility 1")
        facilities_2 = Facility.objects.create(name="Facility 2")
        payload = {
            "info": "Avtobus",
            "num_seats": 50,
            "facilities": [facilities_1.id, facilities_2.id],
        }

        response = self.client.post(BUS_URL, payload)
        bus = Bus.objects.get(id=response.data["id"])
        facilities = bus.facilities.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(facilities_1, facilities)
        self.assertIn(facilities_2, facilities)
        self.assertEqual(facilities.count(), 2)
