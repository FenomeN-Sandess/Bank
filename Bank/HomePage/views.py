from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View, FormView

from User.utils import *


class AboutView(UserInfo, View):
    template_name = "about.html"

    def get(self, request):
        context = self.get_user_info(request)
        return render(request, self.template_name, context)


class IndexView(UserInfo, View):
    template_name = "index.html"

    def get(self, request):
        context = self.get_user_info(request)
        return render(request, self.template_name, context)


class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Эти сообщения отправляются
        messages.error(self.request, "Неверный логин или пароль")
        return super().form_invalid(form)