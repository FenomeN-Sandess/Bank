from django.shortcuts import render, redirect
from User.procedure import *
from User.models import *
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView


class administrations_clients(ListView):
    model = CustomUser
    template_name = "administration_clients.html"
    context_object_name = "list_clients"

    def get_queryset(self):
        login_user = self.request.GET.get("search")
        name_user = self.request.GET.get("name")
        surname_user = self.request.GET.get("surname")
        patronymic_user = self.request.GET.get("patronymic")
        filter_objects = CustomUser.objects.filter(user__groups__name__contains="Client").exclude(
            user__groups__name__contains="Employee")
        if login_user:
            filter_objects = filter_objects.filter(user__username__contains=login_user)
        if name_user:
            filter_objects = filter_objects.filter(name__contains=name_user)
        if surname_user:
            filter_objects = filter_objects.filter(surname__contains=surname_user)
        if patronymic_user:
            filter_objects = filter_objects.filter(patronymic__contains=patronymic_user)
        return filter_objects

    def dispatch(self, request, *args, **kwargs):
        if is_anyGroup(request.user, "Admin"):
            return redirect(reverse("index"))
        return super().dispatch(request, *args, **kwargs)

class administrations_employee(ListView):
    model = CustomUser
    template_name = "administration_employee.html"
    context_object_name = "list_clients"

    def get_queryset(self):
        login_user = self.request.GET.get("search")
        name_user = self.request.GET.get("name")
        surname_user = self.request.GET.get("surname")
        patronymic_user = self.request.GET.get("patronymic")
        filter_objects = CustomUser.objects.filter(user__groups__name__contains="Client").filter(
            user__groups__name__contains="Employee")
        if login_user:
            filter_objects = filter_objects.filter(user__username__contains=login_user)
        if name_user:
            filter_objects = filter_objects.filter(name__contains=name_user)
        if surname_user:
            filter_objects = filter_objects.filter(surname__contains=surname_user)
        if patronymic_user:
            filter_objects = filter_objects.filter(patronymic__contains=patronymic_user)
        return filter_objects

    def dispatch(self, request, *args, **kwargs):
        if is_anyGroup(request.user, "Admin"):
            return redirect(reverse("index"))
        return super().dispatch(request, *args, **kwargs)

def delete_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        user.delete()


def levelUp_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        if not (check_group(user, "Employee")):
            add_group(user, "Employee")


def downUp_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.get(username=username)
        if check_group(user, "Employee"):
            delete_group(user, "Employee")


def choice_search(request):
    if is_anyGroup(request.user, "Admin"):
        return redirect(reverse("index"))
    return render(request, "choice_search.html")