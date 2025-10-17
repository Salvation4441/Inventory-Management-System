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

# users page
def users(request):
    return render(request,'screens/administrator/users.html')

# customers page
def customers(request):
    return render(request,'screens/administrator/customers.html')

# product details page
def product_details(request):
    return render(request,'screens/administrator/product-details.html')

# edit products page
def edit_product(request):
    return render(request,'screens/administrator/edit-product.html')

# add products page
def add_product(request):
    return render(request,'screens/administrator/add-product.html')

# category page
def category(request):
    return render(request,'screens/administrator/category.html')

# manage stocks page
def manage_stocks(request):
    return render(request,'screens/administrator/manage-stocks.html')