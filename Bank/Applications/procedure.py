from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
import random


def is_there_group(user) -> bool:  # Функция, проверяющая принадлежит ли какой-либо группе пользователь
    return (len(user.groups.all()) > 0)


def check_group(user, name_group: str) -> bool:  # Проверяет, принадлежит ли пользователь данной группе
    return Group.objects.get(name=name_group) in user.groups.all()


def about(request):
    return render(request, "about.html")


def add_group(user, str_group):
    group = Group.objects.get(name=str_group)
    user.groups.add(group)
    user.save()


def check_profile_existence(current_user) -> bool:  # На вход принимается модель пользователя
    try:
        CustomUser.objects.get(user=current_user)
        return True
    except CustomUser.DoesNotExist:
        return False


def check_user_existence(str_user) -> bool:
    try:
        User.objects.get(username=str_user)
        return True
    except User.DoesNotExist:
        return False


def check_wallets_existence(wallet, user) -> bool:
    try:
        wallet.objects.get(owner=user.customuser)
        return True
    except wallet.DoesNotExist:
        return False
def check_wallets_existence_withNumber(wallet, number) -> bool:
    try:
        wallet.objects.get(number=number)
        return True
    except wallet.DoesNotExist:
        return False


def check_session_existence(request) -> bool:
    try:
        User.objects.get(username=request.session.get("saved_username"))
        return True
    except User.DoesNotExist:
        return False


def save_profile(current_profile, form_profile):
    current_profile.name = form_profile.cleaned_data["name"]
    current_profile.surname = form_profile.cleaned_data["surname"]
    current_profile.patronymic = form_profile.cleaned_data["patronymic"]
    current_profile.passport_series = form_profile.cleaned_data["passport_series"]
    current_profile.passport_number = form_profile.cleaned_data["passport_number"]
    current_profile.itn = form_profile.cleaned_data["itn"]
    current_profile.phone_number = form_profile.cleaned_data['phone_number']
    current_profile.date_of_birth = form_profile.cleaned_data['date_of_birth']
    current_profile.save()


def save_wallet(wallet, form_wallet):
    numbers: list = [name.number for name in Wallet.objects.only("number").all()] + [number.number for number in CreditWallet.objects.only("number").all()] + [number.number for number in SavingsWallet.objects.only("number").all()]
    wallet.number = random_nameCard(numbers)
    wallet.currency = form_wallet.cleaned_data["currency"]
    wallet.save()


def define_str_currency(user):
    currency = user.customuser.wallet.currency
    if currency == "USA":
        result = "$"
    elif currency == "RU":
        result = "₽"
    else:
        result = str()
    return result
def type_wallet(number):
    if check_wallets_existence_withNumber(Wallet, number):
        return Wallet
    elif check_wallets_existence_withNumber(CreditWallet, number):
        return CreditWallet
    elif check_wallets_existence_withNumber(SavingsWallet, number):
        return SavingsWallet
    else:
        return None


def random_nameCard(names):
    value = str(random.randint(10000000000000000000, 99999999999999999999))
    if value not in names:
        return value
    else:
        return random_nameCard(names)


def create_credit(user):
    if check_wallets_existence(CreditWallet, user):
        return HttpResponse("Кредитная карта уже оформлена")
    else:
        card = CreditWallet.objects.create(owner=user.customuser)
        names_card: list = [name for name in CreditWallet.objects.only("card_number").all()]
        card.card_number = random_nameCard(names_card)
        card.save()
