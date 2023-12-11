from django.urls import path
from .views import (
    main,
    Login
)
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', Login.as_view(), name="log")
]
