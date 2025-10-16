from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee-dashboard'),
]