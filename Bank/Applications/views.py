from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import HttpResponse


def user_update(authoriz: bool, main_user):
    if authoriz:
        custom_user = CustomUser.objects.get(user=main_user)
        role_user = Role.objects.get(user_profile=custom_user)
        current_role = role_user.role.name
        current_name = custom_user.name
        privilege: bool = role_user.role.name in ["Employee", "Admin"]

        user_tuple = {
            "name": current_name,
            "role": current_role,
            "priv": privilege
        }
        return user_tuple
    else:
        return tuple()

def index(request):
    main_user = request.user
    authoriz: bool = main_user.is_authenticated
    contex = {"authoriz": authoriz, "priv": False}
    contex.update(user_update(authoriz, main_user))
    return render(request, "index.html", contex)


def register(request):
    text = str()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST) #Сохраняется форма с вписанными пользователем данными
        # form2 = CustomUserRegistrationForm(request.POST, prefix = "form2")
        text = "Не успешно, но что-то"
        if (form.is_valid()): # Проверяется, являются ли данные формы валидными
            form.save() # Объявляется метод сохранения данных из формы
            # form2.save() # Объявляется метод сохранения данных из формы
            text = "Успешно"
            # return redirect("index_url")  # Перенаправление на страницу после успешной регистрации
    else:
        form = UserRegistrationForm(prefix="form1")
        # form2 = CustomUserRegistrationForm(prefix="form2")
    contex = {
        "form": form,
        # "form2": form2,
        "text": text
    }

    return render(request, 'reg_form.html', contex)