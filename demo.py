from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('signup')

        # Create user
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )

        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('login')

    return render(request, 'users/signup.html')
