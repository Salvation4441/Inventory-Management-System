
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import unauthenticated_user


# @unauthenticated_user
# def signin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         if not password:
#             messages.error(request, 'Password cannot be empty.')
#             return render(request,'screens/auth/login.html')
#         user = authenticate(request,username=username,password=password)
        
#         if user:
#             login(request,user)
#             if user.role == 'ADMIN' or user.is_superuser:
#                 messages.success(request,'ADMIN')
#                 return redirect('admin-dashboard')
#             elif user.role == 'SALESPERSON':
#                 print('Sales person')
#                 messages.success(request,'Sales Peron')
#                 return redirect('employee-dashboard')
#         else:
#             print('Login Request :',messages.error(request, 'Invalid username or password.'))
#             messages.error(request, 'Invalid username or password.')
#     return render(request,'screens/auth/login.html')



@unauthenticated_user
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not password:
            messages.error(request, 'Password cannot be empty.')
            return render(request, 'screens/auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            role = getattr(user, 'role', '').upper()

            if role == 'ADMIN' or user.is_superuser:
                messages.success(request, f"Welcome {user.username}, Admin login successful.")
                return redirect('admin-dashboard')
            elif role == 'SALESPERSON':
                messages.success(request, f"Welcome {user.username}, Salesperson login successful.")
                return redirect('employee-dashboard')
            else:
                messages.error(request, "Unknown user role.")
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'screens/auth/login.html')


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