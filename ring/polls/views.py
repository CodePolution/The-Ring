from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from . import broker
from .models import ChainStatus, Task
from .forms import AuthorizationForm, SubmitForm


class IndexView(TemplateView):
    template_name = 'polls/index.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('log')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        url_query = QueryDict(query_string=self.request.GET.urlencode(), mutable=True)

        task_uuid = url_query.get('task_uuid')
        task = Task.objects.filter(uuid=task_uuid)

        context_data['chains'] = ChainStatus.objects.all()

        if task:
            task = task.first()
            context_data['task'] = task

        if task and task.is_done:
            task.delete()

        return context_data


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
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        return redirect('log')

    def form_valid(self, form):
        form_data = form.data
        form_data_list = []

        for key, value in form_data.items():
            if not value.isdigit():
                continue

            value = int(value)

            form_data_list.append(
                {'name': key, 'value': value}
            )

        task = broker.create_task(form_data_list)
        self.success_url = f"{self.success_url}?task_uuid={task.uuid}"
        return redirect(self.success_url)
