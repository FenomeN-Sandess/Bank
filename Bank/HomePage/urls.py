from django.urls import path

from . import views
from .views import AboutView, IndexView, LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login_form"),
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about_form"),
]
