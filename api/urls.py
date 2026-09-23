from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ServiceViewSet,
    ProviderServiceViewSet,
    BookingViewSet
)


router = DefaultRouter()

router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)

router.register(
    'services',
    ServiceViewSet,
    basename='services'
)

router.register(
    'provider-services',
    ProviderServiceViewSet,
    basename='provider-services'
)

router.register(
    'bookings',
    BookingViewSet,
    basename='bookings'
)


urlpatterns = [
    path('', include(router.urls)),
]