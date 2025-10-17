from django.shortcuts import render

# Create your views here.
def admin_dashboard(request):
    return render(request,'screens/administrator/dashboard.html')

# sales page
def sales(request):
    return render(request,'screens/administrator/sales.html')

# profile
def profile(request):
    return render(request,'screens/core/profile.html')


# sales report
def sales_report(request):
    return render(request,'screens/administrator/sales-report.html')

# settings page
def settings(request):
    return render(request,'screens/administrator/settings.html')

# products page
def products(request):
    return render(request,'screens/administrator/products.html')