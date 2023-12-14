from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator

# Это модель простого всеобъемлющего пользователя, который определяется при добавлении новой учётной записи.
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)                  # Расширение модели User
    name = models.CharField(max_length=100, blank=True, null=True)               # Имя пользователя
    surname = models.CharField(max_length=100, blank=True, null=True)            # Фамилия пользователя
    patronymic = models.CharField(max_length=100, blank=True, null=True)         # Отчество пользователя
    passport_series = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1000), MaxValueValidator(9999)]) # Серия и номер паспорта
    passport_number = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(100000), MaxValueValidator(999999)])
    itn = models.CharField(max_length=14, blank=True, null=True)                 # ИНН
    phone_number = models.CharField(max_length=15, blank=True, null=True)        # Номер телефона
    date_of_birth = models.DateField(blank=True, null=True)                      # Дата рождения


    def __str__(self):
        return f"Профиль пользователя {self.name} с логином {self.user.username}"
# Это модель кошелька, которая так же неразрывно связана с CustomUser. В ней определены поля типа кошелька
class WalletBase(models.Model):
    CURRENCY_CHOICES = [
        ("RU", "Рубль"),
        ("USA", "Доллар")
    ]

    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="RU")
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    number = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        abstract = True

class Wallet(WalletBase):
    def __str__(self):
        return f"Кошелек пользователя {self.owner.name}"

# Это модель кредитной карты, которая привязана к кошельку
class CreditWallet(WalletBase):
    limit = models.DecimalField(default=5000.0, max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    percent = models.DecimalField(default=3.00, max_digits=5, decimal_places=2)
    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект еще не сохранен (новая запись)
            self.amount = self.limit
        super().save(*args, **kwargs)

class SavingsWallet(WalletBase):
    rate = models.DecimalField(default=10, max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])



