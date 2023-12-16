from django.urls import path
from . import views
from .views import administrations_clients, administrations_employee, AboutView, IndexView, LoginView, \
    UserRegistrationView, ProfileRegistrationView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("reg/", UserRegistrationView.as_view(), name="reg_form"),
    path("reg_profile/", ProfileRegistrationView.as_view(), name="reg_form_profile"),
    path("logout/", views.log, name="logout"),
    path("login/", LoginView.as_view(), name="login_form"),
    path("about/", AboutView.as_view(), name="about_form"),
    path("private_office/", views.personalArea, name="personal"),
    path("creating_wallet/", views.registerWallet, name="reg_form_wallet"),
    path("creating_savings_wallet/", views.registerSavingsWallet, name="reg_form_savings"),
    path("creating_credit_wallet/", views.registerCreditWallet, name="reg_form_credit"),
    path("transactions/", views.transactions, name="transactions"),
    path("management/", views.management, name="management"),
    path("choice_wallet/", views.choice, name="choice_wallet"),
    path("closing_wallet/", views.closeWallets, name="closing_wallet"),
    path("administration/clients", administrations_clients.as_view(), name="administration_clients"),
    path("administration/employee", administrations_employee.as_view(), name="administration_employee"),
    path("administration/", views.choice_search, name="choice_search"),
    path("delete_user/", views.delete_user_view, name="delete_user"),
    path("levelUp_user/", views.levelUp_user_view, name="levelUp_user"),
    path("downUp_user/", views.downUp_user_view, name="downUp_user")
]
