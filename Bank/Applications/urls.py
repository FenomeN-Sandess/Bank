from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reg/", views.register, name="reg_form"),
    path("reg_profile/", views.registerProfile, name="reg_form_profile"),
    path("logout/", views.log, name="logout"),
    path("login/", views.login_view, name="login_form"),
    path("about/", views.about, name="about_form"),
    path("private_office/", views.personalArea, name="personal"),
    path("creating_wallet/", views.registerWallet, name="reg_form_wallet"),
    path("creating_savings_wallet/", views.registerSavingsWallet, name="reg_form_savings"),
    path("creating_credit_wallet/", views.registerCreditWallet, name="reg_form_credit"),
    path("transactions/", views.transactions, name="transactions"),
    path("management/", views.management, name="management"),
    path("choice_wallet/", views.choice, name="choice_wallet"),
    path("closing_wallet/", views.closeWallets, name="closing_wallet"),
    path("administration/clients", views.administration_clients, name="administration_clients"),
    path("administration/", views.choice_search, name="choice_search"),
    path("administration/employee", views.administration_employee, name="administration_employee")
]
