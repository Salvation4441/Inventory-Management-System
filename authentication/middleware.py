from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


class RoleRedirectMiddleware:
    """Prevent logged-in users from accessing login page again."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only redirect if it's a GET request to avoid redirect loops on POST requests
        if request.method == 'GET' and request.user.is_authenticated:
            login_path = reverse('login')
            
            # Only redirect if user is trying to access the login page
            if request.path == login_path:
                role = getattr(request.user, 'role', '').upper()
                if role == 'ADMIN' or request.user.is_superuser:
                    return redirect('admin-dashboard')
                elif role == 'SALESPERSON':
                    return redirect('employee-dashboard')

        return self.get_response(request)


class SessionLockMiddleware:
    """
    Middleware to handle session locking functionality.
    Redirects users to lock screen when session is locked.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # URLs that should be accessible even when locked
        exempt_urls = [
            reverse('lock-screen'),
            reverse('logout'),
            reverse('login'),
            '/static/',
            '/media/',
        ]
        
        # Check if current URL should be exempt
        is_exempt = any(request.path.startswith(url) for url in exempt_urls if url)
        
        # Check if user is authenticated and session is locked
        if (request.user.is_authenticated and 
            request.session.get('is_locked', False) and 
            not is_exempt):
            
            # For AJAX requests, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'locked': True,
                    'redirect_url': reverse('lock-screen')
                }, status=423)  # 423 Locked status code
            
            # For regular requests, redirect to lock screen
            return redirect('lock-screen')
        
        response = self.get_response(request)
        return response