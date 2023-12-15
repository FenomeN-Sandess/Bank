from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


# Шаблонная тема - наследник формы для создания пользователя
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1",
                  "password2")  # Под капотом UserCreationForm реализовано сохранение полей в БД с помощью ORM команд

    def save(self, commit=True):
        # Занесение группы включено при регистрации пользователя
        user = super(UserRegistrationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    surname = forms.CharField(max_length=100, required=False)
    patronymic = forms.CharField(max_length=100, required=True)
    passport_series = forms.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    passport_number = forms.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(999999)])
    itn = forms.CharField(min_length=12, max_length=12, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class BaseForm(forms.Form):
    CURRENCY_CHOICES = [
        ("RU", "Рубль"),
        ("USA", "Доллар")
    ]

    username = forms.CharField(required=True, max_length=100)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)


class SavingsForm(BaseForm):
    rate = forms.DecimalField(max_digits=5, decimal_places=2)


class CreditForm(BaseForm):
    percent = forms.DecimalField(max_digits=5, decimal_places=2)
    limit = forms.DecimalField(max_digits=12, decimal_places=2)


class TransactionsForm(forms.Form):
    choice = [
        ("wallet_option", Wallet),
        ("credit_option", CreditWallet),
        ("savings_option", SavingsWallet)
    ]

    account_from = forms.ChoiceField(choices=choice)
    account_to = forms.ChoiceField(choices=choice)
    sum = forms.DecimalField(max_digits=12, decimal_places=2, required=True)

class closingForm(forms.Form):
    number = forms.CharField(required=False, min_length=20, max_length=20)
    checkbox = forms.BooleanField(required=True)
