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
        user = super(UserRegistrationForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    itn = forms.CharField(max_length=10, required=False)
    phone_number = forms.CharField(max_length=10, required=False)
    date_of_birth = forms.DateField(required=False)

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

