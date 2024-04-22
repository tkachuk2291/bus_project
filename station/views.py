from django.contrib.admin import actions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework import status, mixins, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from station.models import Bus, Trip, Facility, Order
from station.permissions import IsAdminAllORISAuthenticatedReadOnly
from station.serializers import BusSerializer, TripSerializer, BusListSerializer, FacilitySerializer, \
    OrderSerializer, RetrieveTripSerializer, BusImageSerializer


# @api_view(["GET", "POST"])
# def bus_list(request):
#     if request.method == 'GET':
#         buses = Bus.objects.all()
#         serializer = BusSerializer(buses, many=True)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         serializer = BusSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# @api_view(["GET", "PUT", "DELETE"])
# def bus_detail(request, pk):
#     bus = get_object_or_404(Bus, pk=pk)
#     if request.method == 'GET':
#         serializer = BusSerializer(bus)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'PUT':
#         serializer = BusSerializer(bus, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         bus.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllORISAuthenticatedReadOnly,)


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(',')]

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "upload_image":
            return BusImageSerializer
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset
        facilities = self.request.query_params.get('facilities')
        if facilities:
            facilities = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities)

        if self.action == "list":
            return queryset.prefetch_related("facilities")
        return queryset.distinct()


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().select_related()

    def get_serializer_class(self):
        if self.action == "list":
            return TripSerializer
        return RetrieveTripSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related()
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@action(methods=['POST'],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path='upload-image')
def upload_image(self, request, pk=None):
    bus = self.get_object()
    serializer = self.get_serializer(bus, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)