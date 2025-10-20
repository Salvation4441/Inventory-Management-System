from django.shortcuts import render
from administrator.models import Category, Customer, Product
from authentication.decorators import admin_only

# Create your views here.
@admin_only
def admin_dashboard(request):
    return render(request,'screens/administrator/dashboard.html')

# sales page
@admin_only
def sales(request):
    return render(request,'screens/administrator/sales.html')

# profile
@admin_only
def profile(request):
    return render(request,'screens/core/profile.html')

# sales report
@admin_only
def sales_report(request):
    return render(request,'screens/administrator/sales-report.html')

# settings page
@admin_only
def settings(request):
    return render(request,'screens/administrator/settings.html')

# products page
@admin_only
def products(request):
    products = Product.objects.select_related('category').all().order_by('-id')  # pylint: disable=no-member
    return render(request,'screens/administrator/products.html',{'products': products})

# users page
@admin_only
def users(request):
    return render(request,'screens/administrator/users.html')

# customers page
@admin_only
def customers(request):
    cutomers = Customer.objects.all().order_by('-id')  # pylint: disable=no-member
    return render(request,'screens/administrator/customers.html',{'cutomers':cutomers})

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
    category = Category.objects.all().order_by('-id')  # pylint: disable=no-member
    return render(request,'screens/administrator/category.html',{'category':category})

# manage stocks page
def manage_stocks(request):
    return render(request,'screens/administrator/manage-stocks.html')

# annual report page
def annual_report(request):
    return render(request,'screens/administrator/annual-report.html')

# profit and loss page
def profit_and_loss(request):
    return render(request,'screens/administrator/profit-and-loss.html')


# error - 404
def error_404(request):
    return render(request,'screens/core/error-404.html')
