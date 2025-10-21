from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import admin_only, unauthenticated_user
from .forms import CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser

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






# edit profile
@unauthenticated_user
@login_required(login_url='login')
def editProfile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=user)
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'screens/core/profile.html', context)