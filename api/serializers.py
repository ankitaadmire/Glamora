from rest_framework import serializers

from services.models import (
    Category,
    Service,
    ServiceProvider,
    Booking
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            'id',
            'name',
            'description',
            'image',
            'is_active',
            'created_at',
        ]


class ServiceSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    class Meta:
        model = Service

        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'duration',
            'image',
            'is_active',
            'created_at',
        ]


class ProviderServiceSerializer(serializers.ModelSerializer):

    provider_name = serializers.CharField(
        source='provider.username',
        read_only=True
    )

    service_name = serializers.CharField(
        source='service.name',
        read_only=True
    )

    class Meta:
        model = ServiceProvider

        fields = [
            'id',
            'provider',
            'provider_name',
            'service',
            'service_name',
            'provider_price',
            'is_active',
        ]


class BookingSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source='customer.username',
        read_only=True
    )

    provider_name = serializers.CharField(
        source='provider.username',
        read_only=True
    )

    service_name = serializers.CharField(
        source='service.name',
        read_only=True
    )

    class Meta:
        model = Booking

        fields = [
            'id',
            'customer',
            'customer_name',
            'provider',
            'provider_name',
            'service',
            'service_name',
            'booking_date',
            'booking_time',
            'amount',
            'status',
            'notes',
            'created_at',
        ]