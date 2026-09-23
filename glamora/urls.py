from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Django Admin
    path('django-admin/', admin.site.urls),

    # Accounts
    path('accounts/', include('accounts.urls')),

    # Custom Admin Panel
    path('adminpanel/', include('adminpanel.urls')),

    # API
    path('api/', include('api.urls')),
]


# Media files
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )