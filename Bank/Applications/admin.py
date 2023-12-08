from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Wallet)
admin.site.register(CreditCard)

# class AppAdmin(admin.ModelAdmin):
#     list_display = ("owner", "currency_unit")
#     # empty_value_display = "Поле не заполнено"
#
#
# admin.site.register(Wallet, AppAdmin)
