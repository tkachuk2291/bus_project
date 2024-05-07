from django.urls import path, include
from rest_framework import routers

from station.views import BusViewSet, TripViewSet, FacilityViewSet, OrderViewSet

app_name = 'station'

router = routers.DefaultRouter()
router.register('buses', BusViewSet, basename='buses')
router.register('trip', TripViewSet, basename='trip')
router.register('facilities', FacilityViewSet, basename='facility')
router.register('orders', OrderViewSet, basename='order'),

urlpatterns = [
    path("", include(router.urls))
]
# urlpatterns = router.urls


# bus_list = BusViewSet.as_view({"get": "list", "post": "create"})
# bus_detail = BusViewSet.as_view(
#         actions={"get": "retrieve",
#                  "put": "update",
#                  "patch": "partial_update",
#                  "delete": "destroy"
#                  }
#     )
#
# urlpatterns = [
#     path('buses/',bus_list, name='bus_list'),
#     path('buses/<int:pk>/', bus_detail, name='bus_detail')
# ]
