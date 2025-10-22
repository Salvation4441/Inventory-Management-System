from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .decorators import admin_only, unauthenticated_user
from .forms import CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser

@unauthenticated_user
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Get remember me checkbox value

        if not password:
            messages.error(request, 'Password cannot be empty.')
            return render(request, 'screens/auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Handle Remember Me functionality
            if remember_me:
                # Keep user logged in for 30 days (30 * 24 * 60 * 60 seconds)
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                messages.info(request, 'You will stay logged in for 30 days.')
            else:
                # Session expires when browser is closed (default behavior)
                request.session.set_expiry(0)
            
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


@login_required(login_url='login')
def lock_screen(request):
    if request.method == 'POST':
        # Handle AJAX lock session request
        if request.POST.get('lock_session'):
            request.session['is_locked'] = True
            request.session['lock_time'] = str(timezone.now())
            return JsonResponse({'status': 'locked'})
        
        # Handle unlock request
        password = request.POST.get('password')
        
        if not password:
            messages.error(request, 'Password is required.')
            return render(request, 'screens/auth/lock-screen.html')
        
        # Verify password against current user
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None and user == request.user:
            # Password is correct, unlock the session
            request.session['is_locked'] = False
            request.session.pop('lock_time', None)
            messages.success(request, 'Screen unlocked successfully!')
            
            # Redirect based on user role
            role = getattr(user, 'role', '').upper()
            if role == 'ADMIN' or user.is_superuser:
                return redirect('admin-dashboard')
            elif role == 'SALESPERSON':
                return redirect('employee-dashboard')
            else:
                return redirect('admin-dashboard')  # Default fallback
        else:
            messages.error(request, 'Invalid password. Please try again.')
    
    # Mark session as locked when accessing lock screen
    request.session['is_locked'] = True
    if not request.session.get('lock_time'):
        request.session['lock_time'] = str(timezone.now())
    
    context = {
        'user': request.user,
        'lock_time': request.session.get('lock_time'),
    }
    return render(request, 'screens/auth/lock-screen.html', context)

# logout
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
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