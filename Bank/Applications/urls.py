from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reg/", views.register, name="reg_form")
    # path("login/", views.login, name="login_form")
]
