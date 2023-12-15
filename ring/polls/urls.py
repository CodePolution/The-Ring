from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='main'),
    path('login/', views.SignInView.as_view(), name="log"),
    path('logout/', views.LogoutView.as_view(), name='out'),
    path('submit/', views.SubmitView.as_view(), name='sub'),
]
