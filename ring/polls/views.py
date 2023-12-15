import pika
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .models import ChainStatus
from .forms import AuthorizationForm, SubmitForm


class IndexView(TemplateView):
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.template_name = 'polls/index.html'
            return super().dispatch(request, *args, **kwargs)

        return redirect('log')

    def get_context_data(self, **kwargs):
        return {
            'chains': ChainStatus.objects.all()
        }


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


class SubmitView(CreateView):
    """
    Класс view для создания запроса на обработку данных.
    """

    form_class = SubmitForm
    context_object_name = 'object'
    success_url = reverse_lazy('main')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('log')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        return super().form_valid(form)
