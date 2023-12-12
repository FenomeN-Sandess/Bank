from django.contrib import admin
from .models import *

# class AppAdmin(admin.ModelAdmin):
#     list_display = ("owner", "currency_unit")
#     # empty_value_display = "Не заполнено"

admin.site.register(CustomUser)
admin.site.register(CreditWallet)
admin.site.register(Wallet)
admin.site.register(SavingsWallet)



# admin.site.register(Wallet, AppAdmin)
