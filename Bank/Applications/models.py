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
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)

