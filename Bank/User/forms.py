from .models import *
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class TransactionsForm(forms.Form):
    choice = [
        ("wallet_option", Wallet),
        ("credit_option", CreditWallet),
        ("savings_option", SavingsWallet)
    ]

    account_from = forms.ChoiceField(choices=choice)
    account_to = forms.ChoiceField(choices=choice, required=False)
    sum = forms.DecimalField(max_digits=12, decimal_places=2, required=True)
    account_to_number = forms.CharField(required=False, max_length=20, min_length=20)
