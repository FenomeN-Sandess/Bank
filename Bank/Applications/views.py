from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from unicodedata import decimal
from .forms import *
from .models import *
from .procedure import *
from decimal import Decimal
from django.views.generic import ListView, View, TemplateView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.db.models import Q
from django.http import JsonResponse
from .utils import *


def log(request):
    logout(request)
    return render(request, "index.html")


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


class ProfileRegistrationView(FormView):
    template_name = "reg_form_profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("choice_wallet")

    def form_valid(self, form):
        current_user = User.objects.get(username=self.request.session.get("saved_username"))
        if not(check_profile_existence(current_user)):
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
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)


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
        if not(number in numbers):
            messages.info(self.request, "Счёт не числится в базе")
            return self.render_to_response({})
        elif wallet_type:
            wallet = wallet_type.objects.get(number=number)
            if wallet_type == Wallet or wallet_type == SavingsWallet:
                if int(wallet.amount) == 0: # Удаление/Блокировка счёта
                    wallet.delete()
                else:
                    messages.error(self.request, "Невозможно заблокировать счёт с ненулевым балансом")
                    return self.render_to_response({})
            elif wallet_type == CreditWallet:
                if not(check_debtExistence(wallet)):
                    wallet.delete() # Удаление/Блокировка счёта
                else:
                    messages.error(self.request, "Невозможно заблокировать счёт с кредитной задолженностью")
                    return self.render_to_response({})
        else:
            messages.error(self.request, "Возникла ошибка")
            return self.render_to_response({})
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.info(self.request, "Вы ввели некорректные данные либо не подтвердили пользовательское соглашение")
        return self.render_to_response({})

    def dispatch(self, request, *args, **kwargs):
        is_anyGroup(request.user, "Employee")
        return super().dispatch(request, *args, **kwargs)

# def closeWallets(request):
#     is_anyGroup(request.user, "Employee")
#     contex = {
#         "request": False,
#         "request_message": str()
#     }
#
#     if request.method == "POST":
#         form = closingForm(request.POST)
#         numbers_wallet: list = [number.number for number in (Wallet.objects.only("number").all())]
#         numbers_credit: list = [number.number for number in (CreditWallet.objects.only("number").all())]
#         numbers_savings: list = [number.number for number in (SavingsWallet.objects.only("number").all())]
#         number = form.data["number"]
#         wallet_type = type_wallet(number)
#         if not (number in (numbers_wallet + numbers_credit + numbers_savings)):
#             contex.update({"request": True, "request_message": "Счёт не числится в базе"})
#         elif form.is_valid() and wallet_type:
#             wallet = wallet_type.objects.get(number=number)
#             if wallet_type == Wallet or wallet_type == SavingsWallet:
#                 if int(wallet.amount) != 0:
#                     contex.update(
#                         {"request": True, "request_message": "Невозможно заблокировать счёт с ненулевым балансом"})
#                 else:
#                     wallet.delete()
#                     contex.update({"request": True, "request_message": "Кошелек успешно удалён"})
#             elif wallet_type == CreditWallet:
#                 if not (check_debtExistence(wallet)):
#                     wallet.delete()
#                     return redirect("/management")
#                 contex.update(
#                     {"request": True, "request_message": "Невозможно заблокировать счёт с кредитной задолженностью"})
#     return render(request, "closing_wallet.html", contex)


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
    if request.method == "POST":
        comission = 0.03
        form_transfer = TransactionsForm(request.POST)
        choice_dict = dict(form_transfer.choice)
        if form_transfer.is_valid():
            type_wallet_from = choice_dict.get(form_transfer.cleaned_data["account_from"])
            wallet_from = type_wallet_from.objects.get(owner=profile)
            number = form_transfer.cleaned_data["account_to_number"]
            if number:
                type_wallet_to = type_wallet(number)
                profile_with_number = define_wallet_withNumber(number).owner
                wallet_to = type_wallet_to.objects.get(owner=profile_with_number)
            else:
                type_wallet_to = choice_dict.get(form_transfer.cleaned_data["account_to"])
                wallet_to = type_wallet_to.objects.get(owner=profile)
            if wallet_from == wallet_to:
                contex_request.update(
                    {"request": True, "request_message": "Выберите кошелек, на который планируете произвести оплату"})

            else:
                currency_to = wallet_to.currency
                currency_from = wallet_from.currency
                wallet_add = form_transfer.cleaned_data["sum"]
                if wallet_from.amount >= wallet_add:
                    if currency_to == currency_from:
                        wallet_to.amount += wallet_add
                    elif currency_from == "RU":
                        wallet_to.amount += (wallet_add / 90) * Decimal(f"{1 - comission}")
                    else:
                        wallet_to.amount += (wallet_add * 90) * Decimal(f"{1 - comission}")
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


class administrations_clients(ListView):
    model = CustomUser
    template_name = "administration_clients.html"
    context_object_name = "list_clients"

    def get_queryset(self):
        login_user = self.request.GET.get("search")
        name_user = self.request.GET.get("name")
        surname_user = self.request.GET.get("surname")
        patronymic_user = self.request.GET.get("patronymic")
        filter_objects = CustomUser.objects.filter(user__groups__name__contains="Client").exclude(
            user__groups__name__contains="Employee")
        if login_user:
            filter_objects = filter_objects.filter(user__username__contains=login_user)
        if name_user:
            filter_objects = filter_objects.filter(name__contains=name_user)
        if surname_user:
            filter_objects = filter_objects.filter(surname__contains=surname_user)
        if patronymic_user:
            filter_objects = filter_objects.filter(patronymic__contains=patronymic_user)
        return filter_objects

class administrations_employee(ListView):
    model = CustomUser
    template_name = "administration_employee.html"
    context_object_name = "list_clients"

    def get_queryset(self):
        login_user = self.request.GET.get("search")
        name_user = self.request.GET.get("name")
        surname_user = self.request.GET.get("surname")
        patronymic_user = self.request.GET.get("patronymic")
        filter_objects = CustomUser.objects.filter(user__groups__name__contains="Client").filter(
            user__groups__name__contains="Employee")
        if login_user:
            filter_objects = filter_objects.filter(user__username__contains=login_user)
        if name_user:
            filter_objects = filter_objects.filter(name__contains=name_user)
        if surname_user:
            filter_objects = filter_objects.filter(surname__contains=surname_user)
        if patronymic_user:
            filter_objects = filter_objects.filter(patronymic__contains=patronymic_user)
        return filter_objects




def delete_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        user.delete()


def levelUp_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        if not (check_group(user, "Employee")):
            add_group(user, "Employee")


def downUp_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        if check_group(user, "Employee"):
            delete_group(user, "Employee")


def choice_search(request):
    is_anyGroup(request.user, "Admin")
    return render(request, "choice_search.html")
