from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView

from User.utils import *
from User.models import *
from .forms import *
from User.procedure import *


class UserRegistrationView(FormView):
    template_name = "reg_form.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("reg_form_profile")

    def form_valid(self, form):
        form.save()
        current_user = User.objects.get(username=form.cleaned_data["username"])
        add_group(current_user, "Client")
        self.request.session["saved_username"] = form.cleaned_data["username"]
        print("Это произошло")
        return super().form_valid(form)

    def form_invalid(self, form):
        username: str = form.data["username"]
        if check_user_existence(username):
            current_user = User.objects.get(username=username)
            if check_profile_existence(current_user):
                messages.info(self.request, "Пользователь уже прошёл все этапы регистрации")
                return self.render_to_response({})
            self.request.session["saved_username"] = username
            return super().form_valid(form)
        messages.error(self.request, "Введены некорректные данные")
        return self.render_to_response({})

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not (user.is_authenticated and check_group(user, "Employee")):
            return redirect(reverse("index"))
        return super().dispatch(request, *args, **kwargs)


class ProfileRegistrationView(FormView):
    template_name = "reg_form_profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("choice_wallet")

    def form_valid(self, form):
        current_user = User.objects.get(username=self.request.session.get("saved_username"))
        if not (check_profile_existence(current_user)):
            if not (form.cleaned_data["name"].isalpha() and form.cleaned_data['surname'].isalpha() and
                    form.cleaned_data["patronymic"].isalpha()):
                messages.error(self.request, "ФИО введено неправильно")
                return self.render_to_response({})
            if timezone.now().date() - form.cleaned_data["date_of_birth"] < timedelta(days=365 * 18):
                messages.error(self.request, "Регистрация в банке положена лицам не моложе 18 лет")
                return self.render_to_response({})
            else:
                current_profile = CustomUser.objects.create(user=current_user)
                save_profile(current_profile, form)
                return super().form_valid(form)
        else:
            messages.error(self.request, "У данного пользователя уже есть профиль")

    def form_invalid(self, form):
        messages.error(self.request, "Введены некорректные данные")
        return self.render_to_response({})

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not (user.is_authenticated and check_group(user, "Employee") and (check_session_existence(request))):
            return redirect(reverse("index"))
        return super().dispatch(request, *args, **kwargs)


def registerAnyWallet(request, any_form, wallet, save, html: str):
    user = request.user
    if is_anyGroup(request.user, "Employee"):
        return redirect(reverse("index"))
    contex = {"request": False, "request_message": str()}
    if check_session_existence(request):
        current_user = User.objects.get(username=request.session.get("saved_username"))
        contex.update({"login": current_user.username})
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
                    return redirect(reverse("management"))
                else:
                    contex.update({"request": True, "request_message": "Данные не валидны"})
    return render(request, html, contex)


def registerWallet(request):
    return registerAnyWallet(request, BaseForm, Wallet, save_wallet, "reg_form_wallet.html")


def registerSavingsWallet(request):
    return registerAnyWallet(request, SavingsForm, SavingsWallet, save_savings, "reg_form_savings.html")


def registerCreditWallet(request):
    return registerAnyWallet(request, CreditForm, CreditWallet, save_credit, "reg_form_credit.html")


class WalletsCloseView(FormView):
    template_name = "closing_wallet.html"
    form_class = closingForm
    success_url = reverse_lazy("management")

    def form_valid(self, form):
        numbers_wallet: list = [number.number for number in (Wallet.objects.only("number").all())]
        numbers_credit: list = [number.number for number in (CreditWallet.objects.only("number").all())]
        numbers_savings: list = [number.number for number in (SavingsWallet.objects.only("number").all())]
        numbers = numbers_wallet + numbers_credit + numbers_savings
        number = form.cleaned_data["number"]
        wallet_type = type_wallet(number)
        if not (number in numbers):
            messages.error(self.request, "Счёт не числится в базе")
            return self.render_to_response({})
        elif wallet_type:
            wallet = wallet_type.objects.get(number=number)
            if wallet_type == Wallet or wallet_type == SavingsWallet:
                if int(wallet.amount) == 0:  # Удаление/Блокировка счёта
                    wallet.delete()
                else:
                    messages.error(self.request, "Невозможно заблокировать счёт с ненулевым балансом")
                    return self.render_to_response({})
            elif wallet_type == CreditWallet:
                if not (check_debtExistence(wallet)):
                    wallet.delete()  # Удаление/Блокировка счёта
                else:
                    messages.error(self.request, "Невозможно заблокировать счёт с кредитной задолженностью")
                    return self.render_to_response({})
        else:
            messages.error(self.request, "Возникла ошибка")
            return self.render_to_response({})
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Вы ввели некорректные данные либо не подтвердили пользовательское соглашение")
        return self.render_to_response({})

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not (user.is_authenticated and check_group(user, "Employee")):
            return redirect(reverse("index"))
        return super().dispatch(request, *args, **kwargs)


def management(request):
    user = request.user
    if not (user.is_authenticated and check_group(user, "Employee")):
        return redirect(reverse("index"))
    return render(request, "management.html")


def choice(request):
    if is_anyGroup(request.user, "Employee"):
        return redirect(reverse("index"))
    return render(request, "choice_wallet.html")
