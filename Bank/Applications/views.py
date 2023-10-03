from django.shortcuts import render
from django.http import HttpResponse
from .models import wallet

def index(request):
    return render(request, "index.html")

def reg_form(request):
    return render(request, "reg_form.html", )

def test(request):
    wallets = wallet.objects.all()
    context = {"context": wallets}
    return render(request, "base.html", context)
