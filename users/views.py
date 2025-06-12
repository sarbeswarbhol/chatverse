from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def signup_view(request):
    return render(request, 'auth/signup.html')


def login_view(request):
    return render(request, 'auth/login.html')


def logout_view(request):
    pass