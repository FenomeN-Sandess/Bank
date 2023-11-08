from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Собственный класс для формы регистрации
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Модель, с которой связана форма
        model = User
        # Описываем поля, которые будут отображаться
        fields = ("username", "email")

