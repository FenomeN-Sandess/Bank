from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, "index.html")

def reg_form(request):
    return render(request, "reg_form.html")
