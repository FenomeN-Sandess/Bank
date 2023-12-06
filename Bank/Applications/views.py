from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.http import HttpResponse
from .models import *

def index(request):
    main_user = request.user
    custom_user = CustomUser.objects.get(user=main_user)
    role_user = Role.objects.get(user_profile=custom_user)
    Current_role = role_user.role.name
    Current_name = custom_user.name

    Authoriz: bool = main_user.is_authenticated
    privilege: bool = (role_user.role == Group.objects.get(name="Employee") or role_user.role == Group.objects.get(name="Admin"))
    contex = {
        "Authoriz": Authoriz,
        "name": Current_name,
        "role": Current_role,
        "priv": privilege

    }
    return render(request, "index.html", contex)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Перенаправление на страницу после успешной регистрации
    else:
        form = UserRegistrationForm()
    return render(request, 'reg_form.html', {'form': form})