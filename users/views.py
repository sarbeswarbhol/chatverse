from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def signup_view(request):
    if request.method=="POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
     
        # print(f"Username: {username}, Email: {email}, Password: {password}")
        
        User.objects.create(
            username=username,
            email=email,
            password=password
        )
        messages.success(request, 'Account created successfully!')
        return redirect('login')
    
    return render(request, 'auth/signup.html')


def login_view(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
     
        # print(f"Username: {username}, Password: {password}")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
    return render(request, 'auth/login.html')


def logout_view(request):
    pass
