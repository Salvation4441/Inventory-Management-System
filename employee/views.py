from django.shortcuts import render
from authentication.decorators import allowed_users

# Create your views here.
@allowed_users(allowed_roles=['SALESPERSON'])
def employee_dashboard(request):
    return render(request,'screens/employee/employee-dashboard.html')

@allowed_users(allowed_roles=['SALESPERSON'])
def employee_sales(request):
    return render(request,'screens/employee/add-sales.html')