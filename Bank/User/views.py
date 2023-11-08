from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm

class SignUp(CreateView):
    # Обозначение формы, с которой мы работаем
    form_class = CreationForm
    # В случае успешной отправки формы происходит перенаправление на url с именем login
    success_url = reverse_lazy("index")

    # В этот html будет передана переменная form с объектом HTML-формы. Что-то вроде render()
    template_name = "signup.html"