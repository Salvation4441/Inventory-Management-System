from django.shortcuts import redirect
from django.urls import reverse

# class RoleRedirectMiddleware:
    # """Redirect users based on role and prevent authenticated users from reaccessing login."""
    # def __init__(self,get_response):
    #     self.get_response = get_response
        
    # def __call__(self, request, *args, **kwds):
    #     login_path = reverse('login')
    #     admin_dashboard_path = reverse('admin-dashboard')
    #     employee_dashboard_path = reverse('employee-dashboard')

        # Prevent recursion: only redirect if not already on dashboard
        # if request.user.is_authenticated and request.path == login_path:
        #     if (request.user.role == 'ADMIN' or request.user.is_superuser) and request.path != admin_dashboard_path:
        #         return redirect('admin-dashboard')
        #     elif request.user.role == 'SALESPERSON' and request.path != employee_dashboard_path:
        #         return redirect('employee-dashboard')

        # return self.get_response(request)
        

class RoleRedirectMiddleware:
    """Prevent logged-in users from accessing login page again."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_path = reverse('login')

        if request.user.is_authenticated and request.path == login_path:
            role = getattr(request.user, 'role', '').upper()
            if role == 'ADMIN' or request.user.is_superuser:
                return redirect('admin-dashboard')
            elif role == 'SALESPERSON':
                return redirect('employee-dashboard')

        return self.get_response(request)