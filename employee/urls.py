from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee-dashboard'),
    
    # Catch-all pattern for invalid employee URLs (should be last)
    path('<path:invalid_path>/', views.handle_invalid_employee_url, name='handle-invalid-employee-url'),
]