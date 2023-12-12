from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reg/", views.register, name="reg_form"),
    path("reg_profile/", views.registerProfile, name="reg_form_profile"),
    path("logout/", views.log, name="logout"),
    path("login/", views.login_view, name="login_form"),
    path("about/", views.about, name="about_form"),
    path("private_office/", views.personalArea, name ="personal"),
    path("creating_wallet/", views.registerWallet, name = "reg_form_wallet"),
    path("creating_wallet_employee/", views.registerWalletEmployee, name = "reg_form_wallet_employee"),
    path("transactions/", views.transactions, name = "transactions"),
    path("management/", views.management, name="management")
]
