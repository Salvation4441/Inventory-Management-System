from django.shortcuts import render
from authentication.decorators import admin_only
from authentication.models import CustomUser

from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout






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
    return render(request,'screens/administrator/products.html')


# customers page
@admin_only
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
# ADD USER
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

    print('Editing User:', user)

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

        
# notification
def create_notification(user, message):
    raise NotImplementedError