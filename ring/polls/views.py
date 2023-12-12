from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.views import  LoginView
from .forms import AuthorizationForm

def main(request):
    return render(request, 'polls/authorization.html')


class SignInView(LoginView):
    """
    Вьюшка для входа пользователя в аккаунт
    """

    template_name = 'account/auth/login.html'
    form_class = AuthorizationForm
    redirect_authenticated_user = True
    success_url = settings.PROFILE_URL

    def dispatch(self, request, args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)

        return super().dispatch(request,args, **kwargs)