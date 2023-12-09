from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login

def is_there_group(user) -> bool: # Функция, проверяющая принадлежит ли какой-либо группе пользователь
    return (len(user.groups.all()) > 0)
def check_group(user, name_group: str) -> bool: # Проверяет, принадлежит ли пользователь данной группе
    return Group.objects.get(name = name_group) in user.groups.all()
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
        profile = check_model_existence(user) # Делаем проверочку зарегистрован ли профиль в системе
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
def log(request):
    logout(request)
    return render(request, "index.html")
def about(request):
    return render(request, "about.html")
def login_view(request):
    if request.method=="POST":
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
def register(request):
    if not(request.user.is_authenticated and check_group(request.user, "Employee")):
        return redirect("/")
    if request.user.is_authenticated:
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
                if check_model_existence(User.objects.get(username=str_current_user)):
                     return HttpResponse("Пользователь уже прошёл все этапы регистрации")
                return redirect("/reg_profile")
        return render(request, 'reg_form.html', {"message": message})
def check_model_existence(current_user) -> bool: # На вход принимается модель пользователя
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
def save_profile(current_profile, form_profile):
    current_profile.name = form_profile.cleaned_data["name"]
    current_profile.itn = form_profile.cleaned_data["itn"]
    current_profile.phone_number = form_profile.cleaned_data['phone_number']
    current_profile.date_of_birth = form_profile.cleaned_data['date_of_birth']
    current_profile.save()
def registerProfile(request):
    if not(request.user.is_authenticated and check_group(request.user, "Employee")):
        return redirect("/")
    text = str()
    current_user = User.objects.get(username=request.session.get("saved_username"))
    if request.method == "POST":
        current_profile = CustomUser.objects.create(user=current_user)                               # Создаём запись в БД о пользователе
        form_profile = ProfileForm(request.POST)
        if form_profile.is_valid():
            save_profile(current_profile, form_profile)
            return redirect("/")

    if (request.session.get("saved_username") and not(check_model_existence(current_user))):
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

    # В форме с кошельком организовать выполнение Транзакций

    contex = {
        "name": name,
        "itn": itn,
        "phone": phone_number,
        "birth": date_of_birth
    }
    return render(request, "personal.html", contex)
