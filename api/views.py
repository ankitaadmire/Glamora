from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from services.models import (
    Category,
    Service,
    ServiceProvider,
    Booking
)

from .serializers import (
    CategorySerializer,
    ServiceSerializer,
    ProviderServiceSerializer,
    BookingSerializer
)

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly
)


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.filter(
        is_active=True
    ).order_by('name')

    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        queryset = super().get_queryset()

        search = self.request.query_params.get(
            'search'
        )

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        return queryset


class ServiceViewSet(viewsets.ModelViewSet):

    queryset = Service.objects.select_related(
        'category'
    ).filter(
        is_active=True
    ).order_by('name')

    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):

        queryset = super().get_queryset()

        category = self.request.query_params.get(
            'category'
        )

        search = self.request.query_params.get(
            'search'
        )

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        return queryset


class ProviderServiceViewSet(viewsets.ModelViewSet):

    queryset = ServiceProvider.objects.select_related(
        'provider',
        'service'
    ).filter(
        is_active=True
    )

    serializer_class = ProviderServiceSerializer
    permission_classes = [AllowAny]


class BookingViewSet(viewsets.ModelViewSet):

    queryset = Booking.objects.select_related(
        'customer',
        'provider',
        'service'
    ).order_by('-created_at')

    serializer_class = BookingSerializer

    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]