from django.shortcuts import render, redirect
from django.contrib import messages

def home_view(request):
    return render(request, 'core/home.html')