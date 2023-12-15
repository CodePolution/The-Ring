from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model

from .models import Submit

USER_MODEL = get_user_model()

class AuthorizationForm(AuthenticationForm):
    """
    Форма для авторизации пользователя.
    """

    error_css_class = 'is-invalid'
    required_css_class = 'required'

    error_messages = {
        "invalid_login":
            "Пожалуйста, введите корректные данные для входа в аккаунт.",

        "inactive": "Этот аккаунт неактивен.",
    }

    class Meta:
        model = USER_MODEL
        fields = ['username', 'password']
        
class SubmitForm(forms.ModelForm):
    
    class Meta:
        model = Submit
        fields = ['one', 'two', 'three', 'four']