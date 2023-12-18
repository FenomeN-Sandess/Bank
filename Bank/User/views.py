from decimal import Decimal
from django.contrib.auth import logout
from django.shortcuts import render
from django.views.generic import View
from .utils import *


def log(request):
    logout(request)
    return render(request, "index.html")


def transactions(request):
    user = request.user

    if not (user.is_authenticated and check_group(user, "Client") and
            (check_wallets_existence(Wallet, user) or check_wallets_existence(CreditWallet, user) or
             check_wallets_existence(SavingsWallet, user))):
        return redirect(reverse("index"))

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

    userinfo = UserInfo()
    contex.update(userinfo.get_user_info(request))

    return render(request, "transactions.html", contex)


class PersonalAreaView(UserInfo, View):
    template_name = "personal.html"

    def get(self, request):
        user = self.request.user
        # Проверка на то, что пользователь принадлежит группе "Client"
        if is_anyGroup(request.user, "Client"):
            return redirect(reverse("index"))
        profile = user.customuser

        context = {
            "name": profile.name,
            "surname": profile.surname,
            "patronymic": profile.patronymic,
            "itn": profile.itn,
            "phone_number": profile.phone_number,
            "date_of_birth": profile.date_of_birth,
            "passport_series": profile.passport_series,
            "passport_number": profile.passport_number
        }

        context.update(self.get_user_info(request))
        context.update(self.get_wallets_data(profile))

        return render(request, self.template_name, context)

    def get_wallets_data(self, profile):
        user = profile.user
        isThere_wallet = check_wallets_existence(Wallet, user)
        isThere_credit = check_wallets_existence(CreditWallet, user)
        isThere_savings = check_wallets_existence(SavingsWallet, user)

        wallets_existence = {
            "isThere_wallet": isThere_wallet,
            "isThere_credit": isThere_credit,
            "isThere_savings": isThere_savings,
        }

        wallets_data = {}

        if isThere_wallet:
            wallet = Wallet.objects.get(owner=profile)
            wallets_data.update({
                "number_wallet": wallet.number,
                "amount_wallet": wallet.amount,
                "currency_wallet": define_str_currency(wallet.currency)
            })

        if isThere_credit:
            credit = CreditWallet.objects.get(owner=profile)
            wallets_data.update({
                "number_credit": credit.number,
                "amount_credit": credit.amount,
                "currency_credit": define_str_currency(credit.currency),
                "limit": credit.limit,
                "percent": credit.percent
            })

        if isThere_savings:
            savings = SavingsWallet.objects.get(owner=profile)
            wallets_data.update({
                "number_savings": savings.number,
                "amount_savings": savings.amount,
                "currency_savings": define_str_currency(savings.currency),
                "rate": savings.rate
            })

        return {**wallets_existence, **wallets_data}
