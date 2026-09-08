from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .decorators import admin_only, unauthenticated_user
from .forms import CustomUserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, PasswordResetRequest

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
    reset_link_url = None
    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()
        if not identifier:
            messages.error(request, 'Please provide your email address or username.')
            return render(request, 'screens/auth/forgot-password.html')

        user = CustomUser.objects.filter(email__iexact=identifier).first()
        if not user:
            user = CustomUser.objects.filter(username__iexact=identifier).first()

        if user:
            # Clear previous reset tokens for this user
            PasswordResetRequest.objects.filter(user=user).delete()
            reset_req = PasswordResetRequest.objects.create(
                user=user,
                email=user.email or identifier,
            )
            try:
                reset_link_url = reset_req.send_reset_email(request=request)
            except Exception:
                reset_link_url = request.build_absolute_uri(f"/reset-password/{reset_req.token}/")

            messages.success(request, f'Password reset link has been created for {user.username}.')
            return render(request, 'screens/auth/forgot-password.html', {'reset_link_url': reset_link_url, 'reset_user': user})
        else:
            messages.error(request, 'No account found with that email address or username.')

    return render(request, 'screens/auth/forgot-password.html')


# reset password with token
@unauthenticated_user
def reset_password(request, token):
    reset_req = PasswordResetRequest.objects.filter(token=token).first()
    if not reset_req or not reset_req.is_valid():
        messages.error(request, 'The password reset link is invalid or has expired. Please request a new one.')
        return redirect('forgotpassword')

    user = reset_req.user
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in both password fields.')
            return render(request, 'screens/auth/reset-password.html', {'token': token, 'reset_user': user})

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'screens/auth/reset-password.html', {'token': token, 'reset_user': user})

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'screens/auth/reset-password.html', {'token': token, 'reset_user': user})

        user.set_password(new_password)
        user.save()
        reset_req.delete()
        messages.success(request, 'Your password has been reset successfully! Please log in.')
        return redirect('login')

    return render(request, 'screens/auth/reset-password.html', {'token': token, 'reset_user': user})


# edit profile
@login_required(login_url='login')
def editProfile(request, user_id=None):
    return redirect('profile')