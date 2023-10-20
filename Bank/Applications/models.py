from django.db import models
from django.contrib.auth import get_user_model

CURRENCY_CHOICES = (
    ("RU", "Рубль"),
    ("USA", "Доллар")
)

User = get_user_model()

class wallet(models.Model):
    name = models.CharField(max_length=40, null=True)
    cash = models.PositiveIntegerField(default=0)
    currency_unit = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="RU")
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="own_wallet")

# class Credit_card(models.Model):
#     identification_code = models.CharField(max_length=40, null=False)
#     cash = models.PositiveIntegerField(default=0)
#     id_card = models.ForeignKey(wallet, related_name="own_credit_card")