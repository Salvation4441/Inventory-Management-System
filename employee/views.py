from django.shortcuts import render

# Create your views here.
def employee_dashboard(request):
    return render(request,'screens/employee/employee.html')