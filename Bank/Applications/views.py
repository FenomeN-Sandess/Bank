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
    user = request.user # Текущий пользователь
    manager: bool = check_group(user, "Admin") or check_group(user, "Employee")
    contex = {
        "manager": manager,
        "authorization": user.is_authenticated,
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
    text = str()
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
    else:
        form = LoginForm()
    return render(request, "login.html", {"text": text, "form": form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST) # Сохраняется форма с вписанными пользователем данными
        if form.is_valid(): # Проверяется, являются ли данные формы валидными
            form.save() # Объявляется метод сохранения данных из формы
            request.session["saved_username"] = form.cleaned_data["username"] # Сохраняем имя пользователя в сессии служащего
            return redirect("/reg_profile")

    return render(request, 'reg_form.html')

def save_profile(current_profile, form_profile):
    current_profile.name = form_profile.cleaned_data["name"]
    current_profile.itn = form_profile.cleaned_data["itn"]
    current_profile.phone_number = form_profile.cleaned_data['phone_number']
    current_profile.date_of_birth = form_profile.cleaned_data['date_of_birth']
    current_profile.save()
def registerProfile(request):
    text = str()
    if request.method == "POST":
        current_user = User.objects.get(username=request.session.get("saved_username"))
        current_profile = CustomUser.objects.create(user=current_user)  # Создаём запись в БД о пользователе
        form_profile = ProfileForm(request.POST)
        if form_profile.is_valid():
            save_profile(current_profile, form_profile)
            return redirect("/")

    if (request.session.get("saved_username")):
        if not(text):
            text = request.session.get("saved_username") # Нужно не забыть в конце почистить сессию
        return render(request, "reg_form_profile.html", {"text": text})
    else:
        text = "Выполнено"
        return redirect("/")