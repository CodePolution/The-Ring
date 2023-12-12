from django.urls import path
from .views import (
    main,
    SignInView
)
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.SignInView.as_view(), name="log")
]
