from django.urls import path
from . import views
from .views import WalletsCloseView, UserRegistrationView, ProfileRegistrationView

urlpatterns = [
    path("reg/", UserRegistrationView.as_view(), name="reg_form"),
    path("reg_profile/", ProfileRegistrationView.as_view(), name="reg_form_profile"),
    path("closing_wallet/", WalletsCloseView.as_view(), name="closing_wallet"),
    path("creating_wallet/", views.registerWallet, name="reg_form_wallet"),
    path("creating_savings_wallet/", views.registerSavingsWallet, name="reg_form_savings"),
    path("creating_credit_wallet/", views.registerCreditWallet, name="reg_form_credit"),
    path("management/", views.management, name="management"),
    path("choice_wallet/", views.choice, name="choice_wallet"),
]