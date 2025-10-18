
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import unauthenticated_user


@unauthenticated_user
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            if user.role == 'ADMIN' or user.is_superuser:
                messages.success(request,'ADMIN')
                return redirect('admin-dashboard')
            elif user.role == 'SALESPERSON':
                messages.success(request,'Sales Peron')
                return redirect('employee-dashboard')
        else:
            print('Login Request :',messages.error(request, 'Invalid username or password.'))
            messages.error(request, 'Invalid username or password.')
        
    return render(request,'screens/auth/login.html')

def lock_screen(request):
    return render(request,'screens/auth/lock-screen.html')

# logout
def logout_view(request):
    logout(request)
    return redirect('login')

# forgot-password
@unauthenticated_user
def forgot_password(request):
    return render(request,'screens/auth/forgot-password.html')