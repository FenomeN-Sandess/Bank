from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django import forms

# Шаблонная тема - наследник формы для создания пользователя
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2") #Под капотом UserCreationForm реализовано сохранение полей в БД с помощью ORM команд
    def save(self, commit=True):
        # Занесение группы включено при регистрации пользователя
        user = super(UserRegistrationForm, self).save(commit=False)
        if commit:
            user.save()
        return user
class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    itn = forms.CharField(min_length=12, max_length=12, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False)
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
class WalletForm(forms.Form):
    CURRENCY_CHOICES = [
        ("RU", "Рубль"),
        ("USA", "Доллар")
    ]

    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    wallet_number = forms.IntegerField(min_value=1000000000, max_value=9999999999, required=False)
class CreditForm(forms.Form):
    card_number = forms.IntegerField(min_value=1000000000, max_value=9999999999, required=False)
class TransactionsForm(forms.Form):
    choice = [
        ("wallet_option", "Wallet"),
        ("credit_option", "Credit_Card")
    ]

    account_from = forms.ChoiceField(choices=choice)
    account_to = forms.ChoiceField(choices=choice)
