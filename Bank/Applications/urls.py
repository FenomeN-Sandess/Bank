from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reg/", views.reg_form, name="reg_form")
]
