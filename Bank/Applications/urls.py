from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reg/", views.register, name="reg_form"),
    path("reg_profile/", views.registerProfile, name="reg_form_profile"),
    path("logout/", views.log, name="logout"),
    path("login/", views.login_view, name="login_form"),
    path("about/", views.about, name="about_form"),
    path("private_office/", views.personalArea, name ="personal")
]
