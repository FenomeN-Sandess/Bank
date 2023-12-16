from django.urls import path
from . import views
from .views import administrations_clients

urlpatterns = [
    # ready
    path("", views.index, name="index"),

    path("reg/", views.register, name="reg_form"),
    path("reg_profile/", views.registerProfile, name="reg_form_profile"),

    # ready
    path("logout/", views.log, name="logout"),

    # ready
    path("login/", views.login_view, name="login_form"),

    # ready
    path("about/", views.about, name="about_form"),

    # ready
    path("private_office/", views.personalArea, name="personal"),

    path("creating_wallet/", views.registerWallet, name="reg_form_wallet"),
    path("creating_savings_wallet/", views.registerSavingsWallet, name="reg_form_savings"),
    path("creating_credit_wallet/", views.registerCreditWallet, name="reg_form_credit"),

    # ready
    path("transactions/", views.transactions, name="transactions"),

    # ready
    path("management/", views.management, name="management"),

    path("choice_wallet/", views.choice, name="choice_wallet"),
    path("closing_wallet/", views.closeWallets, name="closing_wallet"),
    path("administration/clients", administrations_clients.as_view(), name="administration_clients"),

    # ready
    path("administration/", views.choice_search, name="choice_search"),

    path("administration/employee", views.administration_employee, name="administration_employee"),

    # "ready" :)
    path("delete_user/", views.delete_user_view, name="delete_user"),
    path("levelUp_user/", views.levelUp_user_view, name="levelUp_user")
]
