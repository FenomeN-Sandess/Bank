from django.contrib import admin
from .models import wallet


class PostAdmin(admin.ModelAdmin):
    list_display = ("name", "cash", "currency_unit")
    empty_value_display = "Поле не заполнено"

admin.site.register(wallet, PostAdmin)
