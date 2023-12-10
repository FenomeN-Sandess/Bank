from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login

def is_there_group(user) -> bool: # Функция, проверяющая принадлежит ли какой-либо группе пользователь
    return (len(user.groups.all()) > 0)
def check_group(user, name_group: str) -> bool: # Проверяет, принадлежит ли пользователь данной группе
    return Group.objects.get(name = name_group) in user.groups.all()
def log(request):
    logout(request)
    return render(request, "index.html")
def about(request):
    return render(request, "about.html")
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            user = authenticate(username= form_data['username'], password=form_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("/")
                else:
                    return HttpResponse("Учетная запись отключена")
            else:
                return HttpResponse("Неверный логин или пароль")
    return render(request, "login.html")
def add_group(user, str_group):
    group = Group.objects.get(name=str_group)
    user.groups.add(group)
    user.save()
def check_profile_existence(current_user) -> bool: # На вход принимается модель пользователя
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
def check_wallet_existence(user):
    try:
        Wallet.objects.get(owner=user.customuser)
        return True
    except Wallet.DoesNotExist:
        return False
def check_credit_existence(user):
    if check_wallet_existence(user):
        try:
            wallet = Wallet.objects.get(owner = user.customuser)
            CreditCard.objects.get(wallet = wallet)
            return True
        except CreditCard.DoesNotExist:
            return False
    return False
def check_session_existence(request) -> bool:
    try:
        User.objects.get(username=request.session.get("saved_username"))
        return True
    except User.DoesNotExist:
        return False
def save_profile(current_profile, form_profile):
    current_profile.name = form_profile.cleaned_data["name"]
    current_profile.itn = form_profile.cleaned_data["itn"]
    current_profile.phone_number = form_profile.cleaned_data['phone_number']
    current_profile.date_of_birth = form_profile.cleaned_data['date_of_birth']
    current_profile.save()
def save_wallet(wallet, form_wallet):
    wallet.wallet_number = form_wallet.cleaned_data["wallet_number"]
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
    current_user = User.objects.get(username=request.session.get("saved_username"))
    if request.method == "POST":
        current_profile = CustomUser.objects.create(user=current_user)   # Создаём запись в БД о пользователе
        form_profile = ProfileForm(request.POST)
        if form_profile.is_valid():
            save_profile(current_profile, form_profile)
            return redirect("/")

    if (request.session.get("saved_username") and not(check_profile_existence(current_user))):
        if not(text):
            text = request.session.get("saved_username") # Нужно не забыть в конце почистить сессию
        return render(request, "reg_form_profile.html", {"text": text})
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
    isThere_wallet: bool = check_wallet_existence(user)
    isThere_credit: bool = check_credit_existence(user)

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

    if check_wallet_existence(user):
        contex.update({"currency": define_str_currency(user), "number_wallet": str(user.customuser.wallet.wallet_number)})
    if check_credit_existence(user):
        contex.update({"number_credit": user.customuser.wallet.creditcard.card_number})
    if request.method == "POST":
        contex.update({"message_credit": False})

    return render(request, "personal.html", contex)
def registerWallet(request):
    user = request.user
    if not(user.is_authenticated and check_group(user, "Client") and not(check_wallet_existence(user)) ):
        return redirect("/")

    if request.method=="POST":
        form_wallet = WalletForm(request.POST)
        if form_wallet.is_valid():
            current_wallet = Wallet.objects.create(owner=user.customuser)
            save_wallet(current_wallet, form_wallet)
            return redirect("/private_office")
        elif check_wallet_existence(user):
            return HttpResponse("У данного пользователя уже есть кошелек")
        else:
            return HttpResponse("Данные просто не валидны")
    return render(request, "reg_form_wallet.html")
