from django.urls import path

from . import views
from .views import PersonalAreaView

urlpatterns = [
    path("logout/", views.log, name="logout"),
    path("private_office/", PersonalAreaView.as_view(), name="personal"),
    path("transactions/", views.transactions, name="transactions"),
]
