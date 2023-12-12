from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from .procedure import *

def log(request):
    logout(request)
    return render(request, "index.html")
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
        profile = check_profile_existence(user) # Делаем проверочку зарегистрован ли профиль в системе
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
    if not(user.is_authenticated and check_group(user, "Employee")):
        return redirect("/")
    if user.is_authenticated:
        message = str()
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)                                                      # Сохраняется форма с вписанными пользователем данными
            str_current_user = form.data["username"]                                                       # Сохраняем в сессию имя пользователя, которого регистрируем
            request.session["saved_username"] = str_current_user                                           # Сохраняем имя пользователя в сессии служащего
            if form.is_valid():
                form.save()                                                                                # Объявляется метод сохранения данных из формы и объявляется группа пользователя
                add_group(User.objects.get(username=form.cleaned_data["username"]), "Client")     # Добавляем пользователя в группу и сохраняем
                return redirect("/reg_profile")
            elif check_user_existence(str_current_user):
                if check_profile_existence(User.objects.get(username=str_current_user)):
                     return HttpResponse("Пользователь уже прошёл все этапы регистрации")
                return redirect("/reg_profile")
        return render(request, 'reg_form.html', {"message": message})
def registerProfile(request):
    user = request.user
    if not(user.is_authenticated and check_group(user, "Employee") and check_session_existence(request)):
        return redirect("/")
    text = str()
    response: bool = False
    current_user = User.objects.get(username=request.session.get("saved_username"))
    if request.method == "POST":
        form_profile = ProfileForm(request.POST)
        if form_profile.is_valid():
            current_profile = CustomUser.objects.create(user=current_user)  # Создаём запись в БД о пользователе
            save_profile(current_profile, form_profile)
            return redirect("/creating_wallet_employee")
        else:
            response: bool = True

    if (request.session.get("saved_username") and not(check_profile_existence(current_user))):
        if not(text):
            text = request.session.get("saved_username")
        return render(request, "reg_form_profile.html", {"text": text, "response": response})
    else:
        return redirect("/")

def personalArea(request):
    user = request.user
    if not(user.is_authenticated and check_group(user, "Client")):
        return redirect("/")

    # Основная инфа о пользователе
    profile = user.customuser
    name = profile.name
    itn = profile.itn
    phone_number = profile.phone_number
    date_of_birth = profile.date_of_birth

    # Кошелек, если он есть, если нет: переход на страницу с созданием
    isThere_wallet: bool = check_wallets_existence(Wallet, user)
    isThere_credit: bool = check_wallets_existence(CreditWallet, user)

    amount_wallet = str(user.customuser.wallet.amount) if isThere_wallet else "0.00"
    amount_credit = str(user.customuser.wallet.creditcard.amount) if isThere_credit else "0.00"

    # В форме с кошельком организовать выполнение Транзакций
    contex = {
        "amount_wallet": amount_wallet,
        "amount_credit": amount_credit,
        "name": name,
        "itn": itn,
        "phone": phone_number,
        "birth": date_of_birth,
        "isThere_wallet": isThere_wallet,
        "isThere_credit": isThere_credit,
        "message_credit": True,
    }

    if check_wallets_existence(Wallet, user):
        contex.update({"currency": define_str_currency(user), "number_wallet": str(user.customuser.wallet.wallet_number)})
    if check_wallets_existence(CreditWallet, user):
        contex.update({"number_credit": user.customuser.creditwallet.card_number})
    if request.method == "POST":
        create_credit(user)
        contex.update({"message_credit": False})

    return render(request, "personal.html", contex)
def registerWallet(request):
    user = request.user
    if not(user.is_authenticated and check_group(user, "Client") and not(check_wallets_existence(Wallet, user))):
        return redirect("/")

    if request.method=="POST":
        form_wallet = WalletForm(request.POST)
        if form_wallet.is_valid():
            current_wallet = Wallet.objects.create(owner=user.customuser)
            save_wallet(current_wallet, form_wallet)
            return redirect("/private_office")
        elif check_wallets_existence(Wallet, user):
            return HttpResponse("У данного пользователя уже есть кошелек")
        else:
            return HttpResponse("Данные просто не валидны")
    return render(request, "reg_form_wallet.html")
def registerWalletEmployee(request):
    user = request.user
    if not(user.is_authenticated and check_group(user, "Employee")):
        return redirect("/")
    return render(request, "reg_form_wallet_employee.html")
def transactions(request):
    user=request.user
    if not(user.is_authenticated and check_group(user, "Client") and check_wallets_existence(Wallet, user)):
        return redirect("/")
    # if request.method=="POST":

    return render(request, "transactions.html")

def management(request):
    user=request.user
    if not(user.is_authenticated and check_group(user, "Employee")):
        return redirect("/")

    return render(request, "management.html")
