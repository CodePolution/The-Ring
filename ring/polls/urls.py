from django.urls import path
from .views import (
    main,
    SignInView,
    # LogOutView,
)
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.SignInView.as_view(), name="log"),
    path('logout/', auth_views.LogoutView.as_view(template_name='polls/authorization.html'), name='out'),
]
