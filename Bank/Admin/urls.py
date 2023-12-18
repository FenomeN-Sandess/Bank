from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path("administration/clients", administrations_clients.as_view(), name="administration_clients"),
    path("administration/employee", administrations_employee.as_view(), name="administration_employee"),
    path("administration/", views.choice_search, name="choice_search"),
    path("delete_user/", views.delete_user_view, name="delete_user"),
    path("levelUp_user/", views.levelUp_user_view, name="levelUp_user"),
    path("downUp_user/", views.downUp_user_view, name="downUp_user")
]
