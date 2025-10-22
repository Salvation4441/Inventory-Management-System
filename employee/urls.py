from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee-dashboard'),
    path('employee-sales/', views.employee_sales, name='employee-sales'),
]