from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat_view, name='chat'),
]