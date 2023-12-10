from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator

# Это модель простого всеобъемлющего пользователя, который определяется при добавлении новой учётной записи.
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)                  # Расширение модели User
    name = models.CharField(max_length=100, blank=True, null=True)               # Имя пользователя
    itn = models.CharField(max_length=10, blank=True, null=True)                 # ИНН
    phone_number = models.CharField(max_length=10, blank=True, null=True)        # Номер телефона
    date_of_birth = models.DateField(blank=True, null=True)                      # Дата рождения
    # Вот сюда можно добавить ещё поле с картинкой, но это нужно научиться загружать данные, манал я это всё, пока что без картинки в профиле )))

    def __str__(self):
        return f"Профиль пользователя {self.name} с логином {self.user.username}"
# Это модель кошелька, которая так же неразрывно связана с CustomUser. В ней определены поля типа кошелька
class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ("RU", "Рубль"),
        ("USA", "Доллар")
    ]

    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    wallet_number = models.CharField(max_length=10, blank=True, null=True, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="RU")
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Кошелек пользователя {self.owner.name}"

# Это модель кредитной карты, которая привязана к кошельку
class CreditCard(models.Model):
    card_number = models.CharField(max_length=16, null=True, blank=True)
    wallet = models.OneToOneField(Wallet, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

# Модель для транкзакций Wallet, CreditCard..



