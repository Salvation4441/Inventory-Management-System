from django.shortcuts import render

# Create your views here.
def admin_dashboard(request):
    return render(request,'screens/administrator/dashboard.html')

# purchase page
def purchases(request):
    return render(request,'screens/core/purchase.html')

# profile
def profile(request):
    return render(request,'screens/core/profile.html')


# sales report
def sales_report(request):
    return render(request,'screens/administrator/sales-report.html')

# settings page
def settings(request):
    return render(request,'screens/administrator/settings.html')