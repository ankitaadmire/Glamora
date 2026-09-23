from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.dashboard,
        name='admin_dashboard'
    ),

    path(
        'users/',
        views.users,
        name='admin_users'
    ),

    path(
    'users/add/',
    views.add_user,
    name='add_user'
),

path(
    'users/<int:user_id>/view/',
    views.view_user,
    name='view_user'
),

path(
    'users/<int:user_id>/edit/',
    views.edit_user,
    name='edit_user'
),

path(
    'users/<int:user_id>/delete/',
    views.delete_user,
    name='delete_user'
),

path(
    'users/<int:user_id>/toggle-status/',
    views.toggle_user_status,
    name='toggle_user_status'
),

path(
    'users/add/',
    views.add_user,
    name='add_user'
),

path(
    'users/<int:user_id>/view/',
    views.view_user,
    name='view_user'
),

path(
    'users/<int:user_id>/edit/',
    views.edit_user,
    name='edit_user'
),

path(
    'users/<int:user_id>/delete/',
    views.delete_user,
    name='delete_user'
),

path(
    'users/<int:user_id>/toggle-status/',
    views.toggle_user_status,
    name='toggle_user_status'
),

    path(
        'providers/<int:user_id>/approve/',
        views.approve_provider,
        name='approve_provider'
    ),

    path(
        'providers/<int:user_id>/reject/',
        views.reject_provider,
        name='reject_provider'
    ),

    path(
        'categories/',
        views.categories,
        name='admin_categories'
    ),

    path(
        'categories/add/',
        views.add_category,
        name='add_category'
    ),

    path(
        'categories/<int:category_id>/edit/',
        views.edit_category,
        name='edit_category'
    ),

    path(
        'categories/<int:category_id>/delete/',
        views.delete_category,
        name='delete_category'
    ),

    path(
    'categories/',
    views.categories,
    name='admin_categories'
),

path(
    'categories/add/',
    views.add_category,
    name='add_category'
),

path(
    'categories/<int:category_id>/view/',
    views.view_category,
    name='view_category'
),

path(
    'categories/<int:category_id>/edit/',
    views.edit_category,
    name='edit_category'
),

path(
    'categories/<int:category_id>/delete/',
    views.delete_category,
    name='delete_category'
),

    path(
        'services/',
        views.services,
        name='admin_services'
    ),

    path(
        'services/add/',
        views.add_service,
        name='add_service'
    ),

    path(
        'services/<int:service_id>/edit/',
        views.edit_service,
        name='edit_service'
    ),

    path(
        'services/<int:service_id>/delete/',
        views.delete_service,
        name='delete_service'
    ),

    path(
        'provider-services/',
        views.provider_services,
        name='provider_services'
    ),

    path(
        'provider-services/add/',
        views.add_provider_service,
        name='add_provider_service'
    ),

    path(
        'provider-services/<int:assignment_id>/delete/',
        views.delete_provider_service,
        name='delete_provider_service'
        ),

    path(
        'bookings/',
        views.bookings,
        name='admin_bookings'
    ),

    path(
        'bookings/<int:booking_id>/<str:status>/',
        views.update_booking_status,
        name='update_booking_status'
    ),

    path(
        'profile/',
        views.admin_profile,
        name='admin_profile'
    ),

    path(
        'login/',
        views.admin_login,
        name='admin_login'
    ),

    path(
        'reviews/',
        views.reviews,
        name='admin_reviews'
    ),

    path(
        'reviews/<int:review_id>/status/',
        views.update_review_status,
        name='update_review_status'
    ),

    path(
        'reviews/<int:review_id>/delete/',
        views.delete_review,
        name='delete_review'
    ),

    path(
    'offers/',
    views.offers,
    name='admin_offers'
),

path(
    'offers/add/',
    views.add_offer,
    name='add_offer'
),

path(
    'offers/<int:offer_id>/edit/',
    views.edit_offer,
    name='edit_offer'
),

path(
    'offers/<int:offer_id>/delete/',
    views.delete_offer,
    name='delete_offer'
),

path(
    'offers/<int:offer_id>/toggle/',
    views.toggle_offer,
    name='toggle_offer'
),

path(
    'availability/',
    views.availability,
    name='admin_availability'
),

path(
    'availability/add/',
    views.add_availability,
    name='add_availability'
),

path(
    'availability/<int:availability_id>/toggle/',
    views.toggle_availability,
    name='toggle_availability'
),

path(
    'availability/<int:availability_id>/delete/',
    views.delete_availability,
    name='delete_availability'
),

path(
    'support/',
    views.support_queries,
    name='admin_support'
),

path(
    'support/<int:query_id>/update/',
    views.update_support_query,
    name='update_support_query'
),

path(
    'payments/',
    views.payments,
    name='admin_payments'
),

path(
    'revenue/',
    views.revenue,
    name='admin_revenue'
),

path(
    'reports/',
    views.reports,
    name='admin_reports'
),

path(
    'notifications/',
    views.notifications,
    name='admin_notifications'
),

path(
    'notifications/<int:notification_id>/read/',
    views.mark_notification_read,
    name='mark_notification_read'
),

path(
    'notifications/mark-all-read/',
    views.mark_all_notifications_read,
    name='mark_all_notifications_read'
),

path(
    'settings/',
    views.settings,
    name='admin_settings'
),

path(
    'settings/change-password/',
    views.change_password,
    name='change_password'
),

path(
    'profile/',
    views.admin_profile,
    name='admin_profile'
),

    

]