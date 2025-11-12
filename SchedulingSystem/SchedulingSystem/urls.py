from django.contrib import admin
from django.urls import path, include
from scheduler import views
from scheduler import views as system_views  # import your custom login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing_page'),
    path("scheduler/", include('scheduler.urls')),
    path("scheduler_api/", include('scheduler.api.urls')),

    # Custom login view (overrides default Django one)
    path("accounts/login/", system_views.login_view, name="login_view"),

    # Keep the rest of the auth system (logout, password reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
]
