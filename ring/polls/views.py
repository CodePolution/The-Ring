from telnetlib import LOGOUT
from urllib import request
from django import forms
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.views import  LoginView, LogoutView
from .forms import AuthorizationForm
from django.contrib.auth import logout

def main(request):
    return render(request, 'polls/main.html')

class SignInView(LoginView):
    """
    Вьюшка для входа пользователя в аккаунт
    """

    template_name = 'polls/authorization.html'
    form_class = AuthorizationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('main')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)

        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self) -> str:
        return self.success_url
 
 
 
# class LogOutView(LogoutView):
#     template_name = 'polls/authorization.html'
         