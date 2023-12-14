from django.contrib import admin
from .models import *
admin.site.register(CustomUser)
admin.site.register(CreditWallet)
admin.site.register(Wallet)
admin.site.register(SavingsWallet)
# admin.site.register(Wallet, AppAdmin)
