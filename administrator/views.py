import code
from os import name
from django.http import JsonResponse
from django.shortcuts import render
from administrator.forms import CustomerForm
from administrator.models import Category, Customer, Product
from authentication.decorators import admin_only
from authentication.models import CustomUser

from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.utils.dateparse import parse_date
from django.db import transaction
from .models import Category, Product, SalesItem



# Create your views here.
@admin_only
def admin_dashboard(request):
    return render(request,'screens/administrator/dashboard.html')


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

#----------------------------------
# PRODUCTS
#----------------------------------

# ALL PRODUCTS
@login_required(login_url='login')
@admin_only
def products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request,'screens/administrator/products.html', context)

# ADD PRODUCTS
def addProduct(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_category = request.POST.get('product_category')
        product_brand = request.POST.get('product_brand')
        product_description = request.POST.get('product_description')
        product_quantity = request.POST.get('product_quantity')
        product_selling_price = request.POST.get('product_selling_price')
        product_buying_price = request.POST.get('product_buying_price')
        product_discount = request.POST.get('product_discount')
        product_image = request.FILES.get('product_image')
        manufacture_name = request.POST.get('manufacture_name')
        manufacture_date = parse_date(request.POST.get('manufacture_date'))
        expiry_date = parse_date(request.POST.get('expiry_date'))
        
        # Basic validation (required fields)
        if not all([product_name, product_category, product_quantity, product_selling_price, product_buying_price]):
            messages.error(request, "All required fields must be filled.")
            return redirect('addProduct')


        try:
            product_quantity = int(product_quantity)
            product_selling_price = float(product_selling_price)
            product_buying_price = float(product_buying_price)
            product_discount = float(product_discount) if product_discount else 0.0
        except ValueError:
            messages.error(request, "Quantity, prices, and discount must be valid numbers.")
            return redirect('addProduct')

        try:
            category = Category.objects.get(id=product_category)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist.")
            return redirect('addProduct')

        product = Product.objects.create(
                product_name=product_name,
                product_category=category,
                product_brand=product_brand,
                product_description=product_description,
                product_quantity=int(product_quantity),
                product_selling_price=float(product_selling_price),
                product_buying_price=float(product_buying_price),
                product_discount=float(product_discount) if product_discount else 0.0,
                product_image=product_image,
                manufacture_name=manufacture_name,
                manufacture_date=manufacture_date,
                expiry_date=expiry_date,
        )
        product.save()
        messages.success(request, "Product added successfully.")
        return redirect('products')
    else:
        print('Product did not add')
    context = {'categories': categories}
    return render(request,'screens/administrator/add-product.html', context)

# product details page
def productDetails(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request,'screens/administrator/product-details.html', context)

# EDIT PRODUCT
@admin_only
@login_required(login_url='login')
def editProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_category_id = request.POST.get('product_category')
        product_brand = request.POST.get('product_brand')
        product_description = request.POST.get('product_description')
        product_quantity = request.POST.get('product_quantity')
        product_selling_price = request.POST.get('product_selling_price')
        product_buying_price = request.POST.get('product_buying_price')
        product_discount = request.POST.get('product_discount')
        product_image = request.FILES.get('product_image')
        manufacture_name = request.POST.get('manufacture_name')
        manufacture_date = parse_date(request.POST.get('manufacture_date'))
        expiry_date = parse_date(request.POST.get('expiry_date'))

        # Validation
        required_fields = [product_name, product_category_id, product_quantity, product_selling_price, product_buying_price]
        if not all(required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('editProduct', product_id=product.id)

        try:
            category = get_object_or_404(Category, id=product_category_id)
            product_quantity = int(product_quantity)
            product_selling_price = float(product_selling_price)
            product_buying_price = float(product_buying_price)
            product_discount = float(product_discount) if product_discount else 0.0
        except ValueError:
            messages.error(request, "Quantity, prices, and discount must be valid numbers.")
            return redirect('editProduct', product_id=product.id)

        # Update fields
        product.product_name = product_name
        product.product_category = category
        product.product_brand = product_brand
        product.product_description = product_description
        product.product_quantity = product_quantity
        product.product_selling_price = product_selling_price
        product.product_buying_price = product_buying_price
        product.product_discount = product_discount
        product.manufacture_name = manufacture_name
        product.manufacture_date = manufacture_date
        product.expiry_date = expiry_date

        if product_image:
            product.product_image = product_image  # Only update if a new image is uploaded

        product.save()
        messages.success(request, f"Product '{product.product_name}' updated successfully.")
        return redirect('products')

    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'screens/administrator/edit-product.html', context)

# DELETE PRODUCT
@admin_only
@login_required(login_url='login')
def deleteProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.product_name}' deleted successfully.")
        return redirect('products')
    context = {
        'product': product
    }
    return render(request, 'screens/administrator/products.html', context)

# SEARCH PRODUCT
def searchProducts(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.filter(product_name__icontains=q)[:10]
    results = [
        {'id': p.id, 'name': p.product_name, 'price': float(p.product_selling_price)}
        for p in products
    ]
    return JsonResponse(results, safe=False)

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



# --------------------------------------------
# USER MANAGEMENT (Admin Only)
# --------------------------------------------
@login_required(login_url='login')
@admin_only
def users(request):
    users = CustomUser.objects.all()
    context={
        'users':users
    }
    return render(request, 'screens/administrator/users.html', context)

# --------------------------
# CREATE NEW USER
# --------------------------
@login_required(login_url='login')
@admin_only
def addUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        photo = request.FILES.get('photo')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password')

        # ----------------------------------------
        # Basic validations
        # ----------------------------------------
        if not all([username, email, password, confirm_password]):
            messages.error(request, "All required fields must be filled.")
            return redirect('users')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('users')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('users')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('users')
        
        try:
            customUser = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                photo=photo,
                role=role,
                password=password
            )
            if role == 'ADMIN':
                customUser.is_admin = True
                customUser.is_staff = True
                customUser.is_superuser = True
            elif role == 'SALESPERSON':
                customUser.is_staff = True
            else:
                customUser.is_staff = False
                customUser.is_superuser = False
            customUser.save()

            # login(request, user)
            print('User created:', customUser)
            messages.success(request, f"User '{customUser.username}' added successfully.")
            return redirect('users')

        except IntegrityError:
            messages.error(request, "Error: could not create user. Please try again.")
            return redirect('users')

    return render(request, 'screens/administrator/users.html')


# --------------------------
# EDIT USER
# --------------------------
@login_required(login_url='login')
@admin_only
def editUser(request, user_id):
    
    user = get_object_or_404(CustomUser, id=user_id)


    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        photo = request.FILES.get('photo')
        role = request.POST.get('role')

        # Basic validations
        if not all([username, email]):
            messages.error(request, "All required fields must be filled.")
            return redirect('users')

        if CustomUser.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, "Username already exists.")
            return redirect('users')

        if CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, "Email already registered.")
            return redirect('users')

        # Update user details
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        if photo:
            user.photo = photo
        user.role = role

        if role == 'ADMIN':
            user.is_admin = True
            user.is_staff = True
            user.is_superuser = True
        elif role == 'SALESPERSON':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False

        user.save()
        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect('users')

    context = {'user': user}
    return render(request, 'screens/administrator/users.html', context)



#------------------------------
# USER DELETE
#------------------------------
@login_required(login_url='login')
@admin_only
def deleteUser(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    print('Deleting User:', user)
    if request.method == 'POST':
        if user.role == 'ADMIN':
            messages.error(request, "Admin users cannot be deleted.")
            return redirect('users')
        user.delete()
        messages.success(request, f"User '{user.username}' deleted successfully.")
        return redirect('users')
    context = {'user': user}
    return render(request, 'screens/administrator/users.html', context)


#------------------------------
# USER DETAILS
#------------------------------
@login_required(login_url='login')
@admin_only
def viewUser(request,user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    context = {'user': user}
    return render(request, 'screens/administrator/users.html', context)

        
        
        
#----------------------------------
# PRODUCT CATEGORY
#----------------------------------

# GET ALL CATEGORIES
@login_required(login_url='login')
@admin_only
def allCategory(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'screens/administrator/category.html', context)

# ADD NEW CATEGORY
@login_required(login_url='login')
@admin_only
def addCategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_code = request.POST.get('category_code')
        # If code is not provided, generate from category_name
        if not category_code and category_name:
            category_code = category_name[:2].upper()

        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect('category')

        if Category.objects.filter(category_code=category_code).exists():
            messages.error(request, "Category with this code already exists.")
            return redirect('category')

        category = Category(category_name=category_name, category_code=category_code)
        category.save()
        messages.success(request, "Category added successfully.")
        return redirect('category')

    return render(request, 'screens/administrator/category.html')

# EDIT CATEGORY
# --------------------------
@login_required(login_url='login')
@admin_only
def editCategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_code = request.POST.get('category_code')

        if not category_name or not category_code:
            messages.error(request, "All fields are required.")
            return redirect('category')

        if Category.objects.filter(category_name=category_name).exclude(id=category_id).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect('category')

        if Category.objects.filter(category_code=category_code).exclude(id=category_id).exists():
            messages.error(request, "Category with this code already exists.")
            return redirect('category')

        category.category_name = category_name
        category.category_code = category_code
        
        category.save()
        messages.success(request, "Category updated successfully.")
        return redirect('category')

    context = {'category': category}
    return render(request, 'screens/administrator/category.html', context)



# DELETE CATEGORY
@login_required(login_url='login')
@admin_only
def deleteCategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('category')
    context = {'category': category}
    return render(request, 'screens/administrator/category.html', context)


@login_required(login_url='login')
@admin_only
def customers(request):
    customers = Customer.objects.all().order_by('-id')  # pylint: disable=no-member
    return render(request,'screens/administrator/customers.html',{'customers':customers})

@login_required(login_url='login')
@admin_only
def customerCreate(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customers')
    else:
        form = CustomerForm()
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'screens/administrator/customers.html', {customers})


@login_required(login_url='login')
@admin_only
def customerEdit(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'screens/administrator/customers.html', {'customers':customers})


@login_required(login_url='login')
@admin_only
def customerDelete(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customers')
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'screens/administrator/customers.html', {'customers': customers})


#----------------------------------
# PRODUCT SALES
#----------------------------------

@admin_only
def sales(request):
    user = request.user  # current logged-in user
    
    if user.role == 'ADMIN':  
        sales = Sales.objects.all()
    else:
        sales = Sales.objects.filter(user=user)  # assuming Sales has a ForeignKey to User

    return render(request, 'screens/administrator/sales.html', {'sales': sales})
@admin_only
@login_required
@transaction.atomic
def addSales(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            status = request.POST.get('status', 'Pending')
            payment_mode = request.POST.get('payment_mode', 'Cash')

            customer = Customer.objects.get(id=customer_id)

            # Create sale
            sale = Sales.objects.create(
                customer=customer,
                status=status,
                payment_mode=payment_mode,
                user=request.user
            )

            # Get all product rows
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            unit_prices = request.POST.getlist('unit_price[]')
            print('product_ids: ',product_ids)
            print('quantities: ',quantities)
            print('unit_prices: ',unit_prices)

            for i in range(len(product_ids)):
                if not product_ids[i]:
                    continue
                product = Product.objects.get(id=product_ids[i])
                SalesItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=int(quantities[i]),
                    unit_price=float(unit_prices[i])
                )

            messages.success(request, "Sale added successfully!")

        except Exception as e:
            messages.error(request, f"Error adding sale: {e}")
            print(request, f"Error adding sale: {e}")
            return redirect('add-sales')

    customers = Customer.objects.all()
    products = Product.objects.all()

    return render(request, 'screens/administrator/add-sales.html', {
        'customers': customers,
        'products': products,
    })

# notification
def create_notification(user, message):
    raise NotImplementedError