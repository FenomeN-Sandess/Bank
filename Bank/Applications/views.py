from django.shortcuts import render
from django.http import HttpResponse
from .models import wallet

def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")

def test(request):
    enter_name = request.GET.get('enter', None)
    if enter_name:
        wallets = wallet.objects.filter(name__contains=enter_name)
    else:
        wallets = None

    context = {"wallets": wallets, "enter_name": enter_name}
    return render(request, "base.html", context)
