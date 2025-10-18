from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Redirect based on user role
            if hasattr(request.user, 'role'):
                if request.user.role == 'ADMIN' or request.user.is_superuser:
                    return redirect('admin-dashboard')
                elif request.user.role == 'SALESPERSON':
                    return redirect('employee-dashboard')
            return redirect('admin-dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
             return redirect('error-404')
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        # Check for custom user role or group
        if hasattr(request.user, 'role'):
            if request.user.role == 'ADMIN' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            elif request.user.role == 'SALESPERSON':
                return redirect('employee-dashboard')
        # Fallback to group check if role not present
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'ADMIN':
            return view_func(request, *args, **kwargs)
        elif group == 'SALESPERSON':
            return redirect('employee-dashboard')
        return redirect('error-404')
    return wrapper_func
