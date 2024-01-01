from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView
from django.shortcuts import render, redirect
from django.contrib.messages.views import SuccessMessageMixin

from .forms import RegisterForm

USER_MODEL_MISMATCH = """
You are attempting to use the registration view {view}
with the form class {form},
but the model used by that form ({form_model}) is not
your Django installation's user model ({user_model}).

Most often this occurs because you are using a custom user model, but
forgot to specify a custom registration form class for it. Specifying
a custom registration form class is required when using a custom user
model. Please see django-registration's documentation on custom user
models for more details.
"""


class RegisterFormView(SuccessMessageMixin, CreateView):
    template_name = 'register/signup.html'
    success_url = reverse_lazy('home')
    form_class = RegisterForm
    success_message = "Ваш аккаунт зарегистрирован"


"""
class RegisterFormView(FormView):
    template_name = "register/signup.html"
    form_class = RegisterForm
    success_url = "/home/"

    def form_valid(self, form):
        user = form.save()

        if user:
            login(self.request, user)

        return super().form_valid(form)
        
   def register(self, form):
        if self.response.method == "POST":
            form = self.form_class(self.response.POST)
            if form.is_valid():
                form.save()

            return redirect("/home")
        else:
            form = RegisterForm()

        return render(self.response, "register/signup.html", {"form": form})
        """

