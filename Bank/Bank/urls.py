
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("Applications.urls")),
    path("auth/", include("User.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
]
