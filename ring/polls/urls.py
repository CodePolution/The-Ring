from django.urls import path
from .views import (
    main,
    SignInView,
    # LogOutView,
    Logoutt
)
# from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.SignInView.as_view(), name="log"),
    path('logout/', views.LogoutView.as_view(), name='out'),
]
