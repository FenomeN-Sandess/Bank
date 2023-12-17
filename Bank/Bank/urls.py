
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("HomePage.urls")),
    path("user/", include("User.urls")),
    path('adminka/', admin.site.urls),
    path("control/", include("Employee.urls")),
    path("admin/", include("Admin.urls"))
]
