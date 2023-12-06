from django.db import models
from django.contrib.auth.models import User, Group

# Это модель простого всеобъемлющего пользователя, который определяется при добавлении новой учётной записи.
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)                  # Расширение модели User
    name = models.CharField(max_length=100, blank=True, null=True)               # Имя пользователя
    itn = models.CharField(max_length=10, blank=True, null=True)                 # ИНН
    phone_number = models.CharField(max_length=10, blank=True, null=True)        # Номер телефона
    date_of_birth = models.DateField(blank=True, null=True)                      # Дата рождения

# Это модель, неразрывно связанная с CustomUser для определения роли пользователя
class Role(models.Model):
    user_profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.ForeignKey(Group, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"Пользователь {self.user_profile.name} имеет роль {self.role}"

# Это модель кошелька, которая так же неразрывно связана с CustomUser. В ней определены поля типа кошелька
class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ("RU", "Рубль"),
        ("USA", "Доллар")
    ]

    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="RU")
    amount = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"Пользователь {self.owner.name} имеет {self.amount} средств в единицах {self.currency}"

# Это модель кредитной карты, которая привязана к кошельку
class CreditCard(models.Model):
    name_card = models.CharField(max_length=16, null=True, blank=True)
    wallet = models.OneToOneField(Wallet, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Пользователь {self.wallet.owner.name} имеет кредитную карту с номером {self.name_card}"

# Модель для транкзакций Wallet, CreditCard..



