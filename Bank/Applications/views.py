from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from .procedure import *


def log(request):
    logout(request)
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def login_view(request):
    request_off: bool = False
    message_off: str = "Учетная запись отключена"
    request_error: bool = False
    message_error: str = "Неверный логин или пароль"
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            user = authenticate(username=form_data['username'], password=form_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("/")
                else:
                    request_off = True
            else:
                request_error = True
    content = {
        "request_off": request_off,
        "request_error": request_error,
    }
    if request_off:
        content.update({"message_off": message_off})
    if request_error:
        content.update({"message_error": message_error})

    return render(request, "login.html", content)


def index(request):
    user = request.user  # Текущий пользователь
    client = False
    employee = False
    admin = False
    profile = False
    authorization = user.is_authenticated
    if authorization:
        client: bool = check_group(user, "Client")
        employee: bool = check_group(user, "Employee")
        admin: bool = check_group(user, "Admin")
        profile = check_profile_existence(user)  # Делаем проверочку зарегистрован ли профиль в системе
    contex = {
        "client": client,
        "employee": employee,
        "admin": admin,
        "profile": profile,
        "authorization": authorization,
        "login": user.username,
        "groups": user.groups.all()
    }
    return render(request, "index.html", contex)


def register(request):
    user = request.user
    if not (user.is_authenticated and check_group(user, "Employee")):
        return redirect("/")
    if user.is_authenticated:
        message = str()
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)  # Сохраняется форма с вписанными пользователем данными
            str_current_user = form.data["username"]  # Сохраняем в сессию имя пользователя, которого регистрируем
            request.session["saved_username"] = str_current_user  # Сохраняем имя пользователя в сессии служащего
            if form.is_valid():
                form.save()  # Объявляется метод сохранения данных из формы и объявляется группа пользователя
                add_group(User.objects.get(username=form.cleaned_data["username"]),
                          "Client")  # Добавляем пользователя в группу и сохраняем
                return redirect("/reg_profile")
            elif check_user_existence(str_current_user):
                if check_profile_existence(User.objects.get(username=str_current_user)):
                    return HttpResponse("Пользователь уже прошёл все этапы регистрации")
                return redirect("/reg_profile")
        return render(request, 'reg_form.html', {"message": message})


def registerProfile(request):
    user = request.user
    if not (user.is_authenticated and check_group(user, "Employee") and check_session_existence(request)):
        return redirect("/")
    text = str()
    response: bool = False
    current_user = User.objects.get(username=request.session.get("saved_username"))
    if request.method == "POST":
        form_profile = ProfileForm(request.POST)
        if form_profile.is_valid():
            current_profile = CustomUser.objects.create(user=current_user)  # Создаём запись в БД о пользователе
            save_profile(current_profile, form_profile)
            return redirect("/choice_wallet")
        else:
            response: bool = True

    if (request.session.get("saved_username") and not (check_profile_existence(current_user))):
        if not (text):
            text = request.session.get("saved_username")
        return render(request, "reg_form_profile.html", {"text": text, "response": response})
    else:
        return redirect("/")


def registerAnyWallet(request, any_form, wallet, save, html: str):
    user = request.user
    is_anyGroup(request.user, "Employee")
    contex = {"request": False, "request_message": str()}
    if request.method == "POST":
        form_wallet = any_form(request.POST)
        name_user = form_wallet.data["username"]
        if not (check_user_existence(name_user)):
            contex.update({"request": True, "request_message": "Данный пользователь не зарегистрирован в системе"})
        else:
            current_user = User.objects.get(username=name_user)
            existence: bool = check_wallets_existence(wallet, current_user)
            if existence:
                contex.update({"request": True, "request_message": "У данного пользователя уже есть счёт"})
            else:
                if form_wallet.is_valid():
                    any_wallet = wallet.objects.create(owner=current_user.customuser)
                    save(any_wallet, form_wallet)
                    return redirect("/management")
                else:
                    contex.update({"request": True, "request_message": "Данные не валидны"})
    return render(request, html, contex)


def registerWallet(request):
    return registerAnyWallet(request, BaseForm, Wallet, save_wallet, "reg_form_wallet.html")


def registerSavingsWallet(request):
    return registerAnyWallet(request, SavingsForm, SavingsWallet, save_savings, "reg_form_savings.html")


def registerCreditWallet(request):
    return registerAnyWallet(request, CreditForm, CreditWallet, save_credit, "reg_form_credit.html")


def closeWallets(request):
    is_anyGroup(request.user, "Employee")
    contex = {
        "request": False,
        "request_message": str()
    }

    if request.method == "POST":
        form = closingForm(request.POST)
        numbers_wallet: list = [number.number for number in (Wallet.objects.only("number").all())]
        numbers_credit: list = [number.number for number in (CreditWallet.objects.only("number").all())]
        numbers_savings: list = [number.number for number in (SavingsWallet.objects.only("number").all())]
        number = form.data["number"]
        wallet_type = type_wallet(number)
        if not (number in (numbers_wallet + numbers_credit + numbers_savings)):
            contex.update({"request": True, "request_message": "Счёт не числится в базе"})
        elif form.is_valid() and wallet_type:
            wallet = wallet_type.objects.get(number=number)
            if wallet_type == Wallet or wallet_type == SavingsWallet:
                if int(wallet.amount) != 0:
                    contex.update(
                        {"request": True, "request_message": "Невозможно заблокировать счёт с ненулевым балансом"})
                else:
                    wallet.delete()
                    contex.update({"request": True, "request_message": "Кошелек успешно удалён"})
            elif wallet_type == CreditWallet:
                if not(check_debtExistence(wallet)):
                    wallet.delete()
                    return redirect("/management")
                contex.update({"request": True, "request_message": "Невозможно заблокировать счёт с кредитной задолженностью"})
    return render(request, "closing_wallet.html", contex)

def transactions(request):
    user = request.user

    if not (user.is_authenticated and check_group(user, "Client") and
            (check_wallets_existence(Wallet, user) or check_wallets_existence(CreditWallet, user) or
             check_wallets_existence(SavingsWallet, user))):
        return redirect("/")

    isThere_wallet = check_wallets_existence(Wallet, user)
    isThere_credit = check_wallets_existence(CreditWallet, user)
    isThere_savings = check_wallets_existence(SavingsWallet, user)

    contex_existence = {
        "isThere_wallet": isThere_wallet,
        "isThere_credit": isThere_credit,
        "isThere_savings": isThere_savings,
    }

    contex_request = {
        "request": False,
        "request_message": str()
    }

    contex_bool = {
        "two_wallets": two_wallets_existence(user)
    }

    contex_data = dict()

    profile = user.customuser
    if request.method=="POST":
        form_transfer = TransactionsForm(request.POST)
        choice_dict = dict(form_transfer.choice)
        if form_transfer.is_valid():
            type_wallet_from = choice_dict.get(form_transfer.cleaned_data["account_from"])
            type_wallet_to = choice_dict.get(form_transfer.cleaned_data["account_to"])
            wallet_from = type_wallet_from.objects.get(owner=profile)
            wallet_to = type_wallet_to.objects.get(owner=profile)
            if wallet_from == wallet_to:
                contex_request.update({"request": True, "request_message": "Выберите кошелек, на который планируете произвести оплату"})
            else:
                wallet_add = form_transfer.cleaned_data["sum"]
                if wallet_from.amount >= wallet_add:
                    wallet_to.amount += wallet_add
                    wallet_from.amount -= wallet_add
                    wallet_from.save()
                    wallet_to.save()
                    contex_request.update({"request": True, "request_message": "Перевод между счетами выполнен"})
                else:
                    contex_request.update({"request": True, "request_message": "Недостаточно средств на счету"})
        else:
            contex_request.update({"request": True, "request_message": "Введенные данные невалидны"})
    contex = contex_bool | contex_existence | contex_request | contex_data
    return render(request, "transactions.html", contex)

def management(request):
    is_anyGroup(request.user, "Employee")

    return render(request, "management.html")


def choice(request):
    is_anyGroup(request.user, "Employee")
    return render(request, "choice_wallet.html")


def personalArea(request):
    user = request.user
    is_anyGroup(user, "Client")
    profile = user.customuser

    contex_data = {
        "name": profile.name,
        "surname": profile.surname,
        "patronymic": profile.patronymic,
        "itn": profile.itn,
        "phone_number": profile.phone_number,
        "date_of_birth": profile.date_of_birth,
        "passport_series": profile.passport_series,
        "passport_number": profile.passport_number
        }

    isThere_wallet = check_wallets_existence(Wallet, user)
    isThere_credit = check_wallets_existence(CreditWallet, user)
    isThere_savings = check_wallets_existence(SavingsWallet, user)
    contex_existence = {
        "isThere_wallet": isThere_wallet,
        "isThere_credit": isThere_credit,
        "isThere_savings": isThere_savings,
    }

    contex_wallets = dict()
    if isThere_wallet:
        wallet = Wallet.objects.get(owner=profile)
        contex_wallets.update({
            "number_wallet": wallet.number,
            "amount_wallet": wallet.amount,
            "currency_wallet": define_str_currency(wallet.currency)
        })
    if isThere_credit:
        credit = CreditWallet.objects.get(owner=profile)
        contex_wallets.update({
            "number_credit": credit.number,
            "amount_credit": credit.amount,
            "currency_credit": define_str_currency(credit.currency),
            "limit": credit.limit,
            "percent": credit.percent
        })
    if isThere_savings:
        savings = SavingsWallet.objects.get(owner=profile)
        contex_wallets.update({
            "number_savings": savings.number,
            "amount_savings": savings.amount,
            "currency_savings": define_str_currency(savings.currency),
            "rate": savings.rate
        })

    return render(request, "personal.html", contex_data | contex_existence | contex_wallets)
