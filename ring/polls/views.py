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

from .models import ChainStatus
from .forms import AuthorizationForm
from django.contrib.auth import *
from .views import LogoutView

# Отображение основной страницы со встроенной аутентификацией
def main(request):
    # Контекст для индикаторов
    context = {
        'chain1': ChainStatus.objects.get(title='chain1'),
        'chain2': ChainStatus.objects.get(title='chain2'),
        'chain3': ChainStatus.objects.get(title='chain3'),
        'chain4': ChainStatus.objects.get(title='chain4'),
        'chain5': ChainStatus.objects.get(title='chain5'),
    }

    # Проверка авторизации
    if request.user.is_authenticated:
        return render(request, 'polls/index.html', context)
    else:
        return redirect('log')


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

# Обновленный логаут 
class Logoutt():
    def TR(self, request):
        if request.user.is_authenticated:
            LogoutView()
            
    
 
# class LogOutView(LogoutView):
#     template_name = 'polls/authorization.html'
         