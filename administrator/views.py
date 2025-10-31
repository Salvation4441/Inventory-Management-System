import code
from os import name
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
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
from django.db.models import Sum
from django.db.models import Q
from django.db.models import Count, Sum, F, Q
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
@admin_only
def admin_dashboard(request):
    # Handle date filtering from request parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Get current date and time ranges
    today = datetime.now().date()
    
    # Parse date parameters or use defaults
    if start_date_str and end_date_str:
        try:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
        except (ValueError, TypeError):
            # Default to last 30 days if parsing fails
            start_date = today - timedelta(days=30)
            end_date = today
    else:
        # Default to last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
    
    current_month = today.month
    current_year = today.year
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    
    # Calculate financial metrics based on date range
    filtered_sales = Sales.objects.filter(
        status='Completed',
        sale_date__date__range=[start_date, end_date]
    )
    
    total_sales = filtered_sales.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Calculate this month vs last month sales for comparison
    this_month_sales = Sales.objects.filter(
        status='Completed',
        sale_date__month=current_month,
        sale_date__year=current_year
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    last_month_sales = Sales.objects.filter(
        status='Completed',
        sale_date__month=last_month,
        sale_date__year=last_month_year
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate sales growth percentage
    sales_growth = 0
    if last_month_sales > 0:
        sales_growth = ((this_month_sales - last_month_sales) / last_month_sales) * 100
    
    # Calculate total profit (selling_price - cost_price) * quantity for date range
    filtered_sales_items = SalesItem.objects.filter(
        sale__status='Completed',
        sale__sale_date__date__range=[start_date, end_date]
    )
    
    # Debug: Check for negative profit items in date range
    negative_profit_items = filtered_sales_items.select_related('product').filter(
        selling_price__lt=F('product__product_cost_price')
    )
    
    if negative_profit_items.exists():
        print(f"Warning: {negative_profit_items.count()} items have negative profit in selected period")
        for item in negative_profit_items[:3]:  # Show first 3
            print(f"  - {item.product.product_name}: Selling={item.selling_price}, Cost={item.product.product_cost_price}")
    
    total_profit = filtered_sales_items.aggregate(
        profit=Sum(F('quantity') * (F('selling_price') - F('product__product_cost_price')))
    )['profit'] or 0
    
    # Ensure profit is not None and convert to float
    total_profit = float(total_profit) if total_profit is not None else 0.0
    
    # Calculate profit margin percentage based on date range
    total_revenue = filtered_sales_items.aggregate(
        revenue=Sum(F('quantity') * F('selling_price'))
    )['revenue'] or 0
    
    profit_margin_percentage = 0
    if total_revenue > 0:
        profit_margin_percentage = (total_profit / total_revenue) * 100
    
    # Get today's orders count
    todays_orders = Sales.objects.filter(
        sale_date__date=today
    ).count()
    
    # Calculate date ranges for filtering (use consistent with main filter)
    week_ago = start_date
    month_ago = start_date
    
    # Top selling products (based on selected date range)
    top_selling_products = Product.objects.annotate(
        recent_sold=Sum(
            'salesitem__quantity', 
            filter=Q(
                salesitem__sale__status='Completed',
                salesitem__sale__sale_date__date__range=[start_date, end_date]
            )
        ),
        recent_revenue=Sum(
            F('salesitem__quantity') * F('salesitem__selling_price'),
            filter=Q(
                salesitem__sale__status='Completed',
                salesitem__sale__sale_date__date__range=[start_date, end_date]
            )
        )
    ).filter(recent_sold__isnull=False).order_by('-recent_sold')[:10]
    
    # Low stock products (below 10 units)
    low_stock_products = Product.objects.filter(
        product_quantity__lt=10
    ).order_by('product_quantity')[:10]
    
    # Recent sales (based on selected date range)
    recent_sales = Sales.objects.select_related('customer', 'user').prefetch_related(
        'items__product'
    ).filter(
        sale_date__date__range=[start_date, end_date]
    ).order_by('-sale_date')[:15]
    
    # Top customers by total purchase amount
    top_customers = Customer.objects.annotate(
        total_purchases=Sum('sales__total_amount', filter=Q(sales__status='Completed')),
        total_orders=Count('sales', filter=Q(sales__status='Completed'))
    ).filter(total_purchases__isnull=False).order_by('-total_purchases')[:5]
    
    # Category statistics
    category_stats = Category.objects.annotate(
        product_count=Count('products'),
        total_sales=Sum('products__salesitem__quantity', filter=Q(products__salesitem__sale__status='Completed'))
    ).order_by('-total_sales')[:5]
    
    # Overall counts
    total_suppliers = 0  # You can implement this if you have suppliers model
    total_customers = Customer.objects.count()
    total_orders = Sales.objects.count()
    total_categories = Category.objects.count()
    total_products = Product.objects.count()
    
    context = {
        # Financial metrics
        'total_sales': total_sales,
        'total_profit': total_profit,
        'profit_margin_percentage': profit_margin_percentage,
        'total_revenue': total_revenue,
        'sales_growth': sales_growth,
        
        # Date ranges for display
        'today': today,
        'week_ago': week_ago,
        'month_ago': month_ago,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
        
        # Counts
        'todays_orders': todays_orders,
        'total_suppliers': total_suppliers,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_categories': total_categories,
        'total_products': total_products,
        
        # Data for widgets
        'top_selling_products': top_selling_products,
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'top_customers': top_customers,
        'category_stats': category_stats,
        
        # Low stock alert (for the alert banner)
        'critical_stock_product': low_stock_products.first() if low_stock_products.exists() else None,
    }
    
    # Check if this is an AJAX request for partial data update
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        from django.template.loader import render_to_string
        
        # Return JSON response with updated HTML fragments
        return JsonResponse({
            'success': True,
            'data': {
                'total_sales': f"GHC {total_sales:,.2f}",
                'total_profit': f"GHC {total_profit:,.2f}",
                'profit_margin_percentage': f"{profit_margin_percentage:.1f}%",
                'total_revenue': f"GHC {total_revenue:,.2f}",
                'sales_growth': f"{sales_growth:+.1f}%",
                'total_orders': total_orders,
                'total_customers': total_customers,
                'date_range': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            },
            'html': {
                'top_selling_products': render_to_string('components/top_selling_products.html', {
                    'top_selling_products': top_selling_products,
                    'start_date': start_date,
                    'end_date': end_date
                }),
                'recent_sales': render_to_string('components/recent_sales.html', {
                    'recent_sales': recent_sales,
                    'today': today,
                    'start_date': start_date,
                    'end_date': end_date
                })
            }
        })
    
    return render(request, 'screens/administrator/dashboard.html', context)



#----------------------------------
# SALES REPORT
#----------------------------------
@admin_only
def salesReport(request):
    products = Product.objects.all()
    
    # Get all sales items with related data for better performance
    sales_items = SalesItem.objects.select_related(
        'sale', 'sale__customer', 'product', 'product__product_category'
    ).order_by('-sale__sale_date')
    
    # Initialize filter variables
    selected_product = None
    
    # Apply filters if form is submitted
    if request.method == 'POST':
        selected_product = request.POST.get('product')
        
        # Filter by product if selected
        if selected_product:
            sales_items = sales_items.filter(product_id=selected_product)
    
    # Calculate summary statistics
    total_sales_amount = sales_items.aggregate(
        total=Sum(F('quantity') * F('unit_price') - F('discount'), output_field=FloatField())
    )['total'] or 0.0
    
    total_quantity_sold = sales_items.aggregate(total=Sum('quantity'))['total'] or 0
    total_sales_count = sales_items.values('sale').distinct().count()
    
    # Calculate average sale value per transaction (not per item)
    avg_sale_value = 0
    if total_sales_count > 0:
        sale_totals = sales_items.values('sale').annotate(
            sale_total=Sum(F('quantity') * F('unit_price') - F('discount'), output_field=FloatField())
        ).aggregate(avg_total=Sum('sale_total'))
        avg_sale_value = (sale_totals['avg_total'] or 0) / total_sales_count
    
    context = {
        'sales_items': sales_items,
        'products': products,
        'selected_product': selected_product,
        'total_sales_amount': total_sales_amount,
        'total_quantity_sold': total_quantity_sold,
        'total_sales_count': total_sales_count,
        'avg_sale_value': avg_sale_value,
    }
    return render(request,'screens/administrator/sales-report.html', context)

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
        product_cost_price = request.POST.get('product_cost_price')
        product_discount = request.POST.get('product_discount')
        product_image = request.FILES.get('product_image')
        manufacture_name = request.POST.get('manufacture_name')
        manufacture_date = parse_date(request.POST.get('manufacture_date'))
        expiry_date = parse_date(request.POST.get('expiry_date'))
        
        # Basic validation (required fields)
        if not all([product_name, product_category, product_quantity, product_selling_price, product_cost_price]):
            messages.error(request, "All required fields must be filled.")
            return redirect('addProduct')


        try:
            product_quantity = int(product_quantity)
            product_selling_price = float(product_selling_price)
            product_cost_price = float(product_cost_price)
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
                product_cost_price=float(product_cost_price),
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
        product_cost_price = request.POST.get('product_cost_price')
        product_discount = request.POST.get('product_discount')
        product_image = request.FILES.get('product_image')
        manufacture_name = request.POST.get('manufacture_name')
        manufacture_date = parse_date(request.POST.get('manufacture_date'))
        expiry_date = parse_date(request.POST.get('expiry_date'))

        # Validation
        required_fields = [product_name, product_category_id, product_quantity, product_selling_price, product_cost_price]
        if not all(required_fields):
            messages.error(request, "All required fields must be filled.")
            return redirect('editProduct', product_id=product.id)

        try:
            category = get_object_or_404(Category, id=product_category_id)
            product_quantity = int(product_quantity)
            product_selling_price = float(product_selling_price)
            product_cost_price = float(product_cost_price)
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
        product.product_cost_price = product_cost_price
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
        {'id': p.id, 'name': p.product_name, 'price': float(p.product_selling_price),'cost': float(p.product_cost_price)}
        for p in products
    ]
    return JsonResponse(results, safe=False)

#----------------------------------
# MANAGE STOCKS
#----------------------------------
@login_required(login_url='login')
@admin_only
def manageStocks(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity_added = request.POST.get('quantity_added')
        
        # Validation
        if not all([product_id, quantity_added]):
            messages.error(request, "All required fields must be filled.")
            return redirect('manage-stocks')
        
        try:
            quantity_added = int(quantity_added)
            if quantity_added <= 0:
                messages.error(request, "Quantity must be greater than zero.")
                return redirect('manage-stocks')
        except ValueError:
            messages.error(request, "Quantity must be a valid number.")
            return redirect('manage-stocks')
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Create stock record
            stock_record = ManageStocks.objects.create(
                product=product,
                quantity_added=quantity_added
            )
            
            messages.success(request, f"Successfully added {quantity_added} units to {product.product_name}. New stock: {stock_record.new_quantity}")
            return redirect('manage-stocks')
            
        except Product.DoesNotExist:
            messages.error(request, "Selected product does not exist.")
            return redirect('manage-stocks')
        except Exception as e:
            messages.error(request, f"Error adding stock: {str(e)}")
            return redirect('manage-stocks')
    
    # GET request - display stock history
    products = Product.objects.all().order_by('product_name')
    stock_history = ManageStocks.objects.all().select_related('product', 'product__product_category')
    
    context = {
        'products': products,
        'stock_history': stock_history,
    }
    return render(request, 'screens/administrator/manage-stocks.html', context)


# edit manage stock
@login_required(login_url='login')
@admin_only
def editManageStock(request, stock_id):
    stock_record = get_object_or_404(ManageStocks, id=stock_id)
    products = Product.objects.all().order_by('product_name')
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity_added = request.POST.get('quantity_added')
        
        # Validation
        if not all([product_id, quantity_added]):
            messages.error(request, "All fields must be provided.")
            return redirect('manage-stocks')
        
        try:
            quantity_added = int(quantity_added)
            if quantity_added <= 0:
                messages.error(request, "Quantity must be greater than zero.")
                return redirect('manage-stocks')
        except ValueError:
            messages.error(request, "Quantity must be a valid number.")
            return redirect('manage-stocks')
        
        try:
            new_product = Product.objects.get(id=product_id)
            old_product = stock_record.product
            
            # Revert previous stock addition from old product
            old_product.product_quantity = stock_record.previous_quantity
            old_product.save(update_fields=['product_quantity'])
            
            # Update stock record with new product and quantity
            stock_record.product = new_product
            stock_record.previous_quantity = new_product.product_quantity
            stock_record.quantity_added = quantity_added
            stock_record.save()
            
            messages.success(request, f"Stock record updated successfully. {new_product.product_name} new stock: {stock_record.new_quantity}")
            return redirect('manage-stocks')
            
        except Product.DoesNotExist:
            messages.error(request, "Selected product does not exist.")
            return redirect('manage-stocks')
        except Exception as e:
            messages.error(request, f"Error updating stock: {str(e)}")
            return redirect('manage-stocks')
    
    context = {
        'stock_record': stock_record,
        'products': products,
    }
    return render(request, 'screens/administrator/edit-manage-stock.html', context)



# delete manage stock
@login_required(login_url='login')
@admin_only
def deleteManageStock(request, stock_id):
    stock_record = get_object_or_404(ManageStocks, id=stock_id)
    
    if request.method == 'POST':
        # Revert the product quantity back to previous state
        product = stock_record.product
        product.product_quantity = stock_record.previous_quantity
        product.save(update_fields=["product_quantity"])
        
        # Delete the stock record
        product_name = stock_record.product.product_name
        quantity_added = stock_record.quantity_added
        stock_record.delete()
        
        messages.success(request, f"Stock record deleted successfully. {product_name} quantity reverted by {quantity_added} units.")
        return redirect('manage-stocks')
    
    # If GET request, redirect back to manage stocks
    return redirect(request,'screens/administrator/manage-stocks.html')


# annual report page
def annualReport(request):
    return render(request,'screens/administrator/annual-report.html')

# Diagnostic function to check profit issues
def diagnose_profit_issues():
    """Helper function to diagnose negative profit issues"""
    from django.db.models import Sum, F, Count
    
    print("\n=== PROFIT DIAGNOSIS ===")
    
    # Check total items
    total_items = SalesItem.objects.filter(sale__status=['Completed','Pending']).count()
    print(f"Total completed sales items: {total_items}")
    
    # Check items with negative profit
    negative_profit_items = SalesItem.objects.filter(
        sale__status=['Completed','Pending'],
        selling_price__lt=F('product__product_cost_price')
    ).select_related('product')
    
    print(f"Items with negative profit: {negative_profit_items.count()}")
    
    # Show details of negative profit items
    if negative_profit_items.exists():
        print("\nNEGATIVE PROFIT ITEMS:")
        for item in negative_profit_items[:10]:  # Show first 10
            loss = (item.product.product_cost_price - item.selling_price) * item.quantity
            print(f"  - {item.product.product_name}")
            print(f"    Cost: GHC{item.product.product_cost_price:.2f}")
            print(f"    Selling: GHC{item.selling_price:.2f}")
            print(f"    Qty: {item.quantity}")
            print(f"    Loss: GHC{loss:.2f}")
    
    # Check products with zero or negative cost prices
    zero_cost_products = Product.objects.filter(product_cost_price__lte=0)
    if zero_cost_products.exists():
        print(f"\nProducts with zero/negative cost price: {zero_cost_products.count()}")
        for product in zero_cost_products[:5]:
            print(f"  - {product.product_name}: Cost = GHC{product.product_cost_price:.2f}")
    
    # Calculate overall profit
    total_profit = SalesItem.objects.filter(
        sale__status__in=['Completed','Pending']
    ).aggregate(
        profit=Sum(F('quantity') * (F('selling_price') - F('product__product_cost_price')))
    )['profit'] or 0
    
    print(f"\nTotal calculated profit: GHC{total_profit:.2f}")
    return total_profit

# profit and loss page
@admin_only
def profit_and_loss(request):
    
    
    # Get date range from request or default to last 12 months
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            # Default to last 12 months if invalid dates
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
    else:
        # Default to last 12 months
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
    
    # Generate monthly data for the selected period
    monthly_data = []
    current_date = start_date.replace(day=1)  # Start from first day of start month
    
    while current_date <= end_date:
        # Calculate next month
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        # Filter sales for this month
        month_sales = Sales.objects.filter(
            status='Completed',
            sale_date__gte=current_date,
            sale_date__lt=next_month
        )
        
        # Calculate revenue (total sales amount)
        revenue = month_sales.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate cost of goods sold
        cogs = SalesItem.objects.filter(
            sale__in=month_sales
        ).aggregate(
            total=Sum(F('quantity') * F('product__product_cost_price'))
        )['total'] or 0
        
        # Calculate gross profit
        gross_profit = revenue - cogs
        
        # Calculate profit from individual items (considering actual selling prices)
        profit_from_sales = SalesItem.objects.filter(
            sale__in=month_sales
        ).aggregate(
            total=Sum(F('quantity') * (F('selling_price') - F('product__product_cost_price')))
        )['total'] or 0
        
        # Ensure profit is not None and convert to float
        profit_from_sales = float(profit_from_sales) if profit_from_sales is not None else 0.0
        
        # Debug: Check for negative profit in this month
        month_negative_items = SalesItem.objects.filter(
            sale__in=month_sales,
            selling_price__lt=F('product__product_cost_price')
        ).count()
        
        if month_negative_items > 0:
            print(f"Month {current_date.strftime('%b %Y')}: {month_negative_items} items with negative profit")
        
        # Calculate profit margin percentage
        profit_margin = (profit_from_sales / revenue * 100) if revenue > 0 else 0
        
        monthly_data.append({
            'month': current_date.strftime('%b %Y'),
            'month_short': current_date.strftime('%b'),
            'year': current_date.year,
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'profit_from_sales': profit_from_sales,
            'profit_margin': profit_margin,
            'sales_count': month_sales.count(),
        })
        
        current_date = next_month
    
    # Calculate totals for the entire period
    total_revenue = sum(month['revenue'] for month in monthly_data)
    total_cogs = sum(month['cogs'] for month in monthly_data)
    total_gross_profit = sum(month['gross_profit'] for month in monthly_data)
    total_profit = sum(month['profit_from_sales'] for month in monthly_data)
    overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    context = {
        'monthly_data': monthly_data,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_cogs': total_cogs,
        'total_gross_profit': total_gross_profit,
        'total_profit': total_profit,
        'overall_margin': overall_margin,
        'date_range': f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}",
    }
    
    return render(request,'screens/administrator/profit-and-loss.html', context)


# error - 404
def error_404(request):
    return render(request,'screens/core/error-404.html')

# Custom 404 handler
def custom_404(request, exception):
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.http import HttpResponseNotFound
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Page not found'}, status=404)
    
    # Check if user is authenticated and redirect accordingly
    if request.user.is_authenticated:
        # Add error message
        messages.error(request, "The page you're looking for doesn't exist. You've been redirected to the dashboard.")
        
        if hasattr(request.user, 'role') and request.user.role == 'SALESPERSON':
            return redirect('employee-dashboard')
        else:
            return redirect('admin-dashboard')
    else:
        # For unauthenticated users, show the 404 page instead of redirecting to login
        return render(request, 'screens/core/error-404.html', status=404)

# Custom 500 handler
def custom_500(request):
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.http import HttpResponseServerError
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Server error'}, status=500)
    
    # Check if user is authenticated and redirect accordingly
    if request.user.is_authenticated:
        # Add error message
        messages.error(request, "Something went wrong on our end. Please try again.")
        
        if hasattr(request.user, 'role') and request.user.role == 'SALESPERSON':
            return redirect('employee-dashboard')
        else:
            return redirect('admin-dashboard')
    else:
        # For unauthenticated users, show a generic error page instead of redirecting
        return render(request, 'screens/core/error-404.html', {'error_message': 'Server Error'}, status=500)

# Handle invalid URLs
def handle_invalid_url(request, invalid_path):
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Prevent redirecting login-related paths to avoid loops
    if 'login' in invalid_path.lower() or 'auth' in invalid_path.lower():
        return render(request, 'screens/core/error-404.html', status=404)
    
    # Check if user is authenticated and redirect accordingly
    if request.user.is_authenticated:
        # Add specific error message with the invalid path
        messages.warning(request, f"The page '/{invalid_path}/' was not found. You've been redirected to the dashboard.")
        
        if hasattr(request.user, 'role') and request.user.role == 'SALESPERSON':
            return redirect('employee-dashboard')
        else:
            return redirect('admin-dashboard')
    else:
        # For unauthenticated users, show 404 page instead of redirecting to login
        return render(request, 'screens/core/error-404.html', status=404)



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


#------------------------------
# PROFILE DETAILS
#------------------------------
@login_required(login_url='login')
@admin_only
def profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    context = {'user': user}
    return render(request,'screens/core/profile.html', context)
        
        
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

# SEARCH CUSTOMERS 

def searchCustomers(request):
    q = request.GET.get('q', '').strip()
    customers = Customer.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q)
    )[:10]
    results = [
        {'id': c.id, 'name': f"{c.first_name} {c.last_name}"}
        for c in customers
    ]
    return JsonResponse(results, safe=False)


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

@login_required
@transaction.atomic
def addSales(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            status = request.POST.get('status', 'Completed')
            payment_mode = request.POST.get('payment_mode', 'Cash')

            # Get all product rows
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('quantity[]')
            # Note: unit price is not editable (comes from product), selling price is editable by user
            selling_prices = request.POST.getlist('selling_price[]') or request.POST.getlist('selling_price')

            # Validate that at least one product has been added
            if not product_ids or len(product_ids) == 0:
                messages.error(request, "Please add at least one product before submitting the sale.")
                return redirect('add-sales')
            
            # Filter out empty product IDs and validate
            valid_products = [pid for pid in product_ids if pid and pid.strip()]
            if len(valid_products) == 0:
                messages.error(request, "Please add at least one valid product before submitting the sale.")
                return redirect('add-sales')
            
            # Validate quantities and selling prices
            for i, product_id in enumerate(product_ids):
                if not product_id or not product_id.strip():
                    continue
                    
                # Check quantity
                if i >= len(quantities) or not quantities[i] or int(quantities[i]) <= 0:
                    messages.error(request, f"Invalid quantity for product. All products must have a quantity greater than 0.")
                    return redirect('add-sales')
                
                # Check selling price  
                if i >= len(selling_prices) or not selling_prices[i] or float(selling_prices[i]) <= 0:
                    messages.error(request, f"Invalid selling price for product. All products must have a selling price greater than 0.")
                    return redirect('add-sales')

            print('Products',product_ids)
            print('Quantities',quantities)
            print('Selling Prices',selling_prices)

            # Check if customer_id exists
            customer = None
            if customer_id:
                customer = Customer.objects.get(id=customer_id)

            sale = Sales.objects.create(
                customer=customer,
                status=status,
                payment_mode=payment_mode,
                user=request.user
            )

            # Create sales items - only for valid products
            created_items_count = 0
            for i in range(len(product_ids)):
                if not product_ids[i] or not product_ids[i].strip():
                    continue
                    
                try:
                    product = Product.objects.get(id=product_ids[i])
                    SalesItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=int(quantities[i]),
                        selling_price=float(selling_prices[i]) if i < len(selling_prices) and selling_prices[i] else product.product_selling_price
                    )
                    created_items_count += 1
                except Product.DoesNotExist:
                    messages.warning(request, f"Product with ID {product_ids[i]} not found. Skipping.")
                    continue
                except (ValueError, IndexError) as e:
                    messages.warning(request, f"Invalid data for product {product_ids[i]}. Skipping.")
                    continue
            
            # Double-check that at least one item was created
            if created_items_count == 0:
                # Delete the sale if no items were created
                sale.delete()
                messages.error(request, "No valid products were added to the sale. Please try again.")
                return redirect('add-sales')

            # Create activity notification
            total_items = sum(int(q) for i, q in enumerate(quantities) if q and i < len(product_ids) and product_ids[i])
            create_activity(
                user=request.user,
                activity_type='sale_created',
                title=f'New Sale Created',
                description=f"Sale #{sale.reference} created for {f'{customer.first_name} {customer.last_name}' if customer else 'Walk-in customer'} with {created_items_count} items totaling GHC{sale.total_amount:.2f}",
                sale=sale
            )
            
            messages.success(request, f"Sale added successfully! Created sale #{sale.reference} with {created_items_count} items.")
            return redirect('sales')

        except Exception as e:
            messages.error(request, f"Error adding sale: {e}")
            print("Error adding sale:", e)
            return redirect('add-sales')

    customers = Customer.objects.all()
    products = Product.objects.all()
    isSalesPerson = getattr(request.user, 'role', '').upper() == 'SALESPERSON'
    
    context = {
        'customers': customers,
        'products': products,
        'isSalesPerson': isSalesPerson,
    }

    return render(request, 'screens/administrator/add-sales.html', context)
    
@login_required
def saleDetail(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    items = SalesItem.objects.filter(sale=sale)
    
    # Handle customer data (can be None for walk-in customers)
    if sale.customer:
        customer_data = {
            "name": f"{sale.customer.first_name} {sale.customer.last_name}",
            "email": sale.customer.email if hasattr(sale.customer, "email") else "",
            "phone": sale.customer.phone if hasattr(sale.customer, "phone") else "",
            "address": sale.customer.address if hasattr(sale.customer, "address") else "",
        }
    else:
        customer_data = {
            "name": "Walk-in Customer",
            "email": "",
            "phone": "",
            "address": "",
        }
    
    sale_data = {
        "id": sale.id,
        "reference": sale.reference,
        "status": sale.status,
        "payment_mode": sale.payment_mode,
        "sale_date": sale.sale_date.strftime("%b %d, %Y"),
        "total_amount": sale.total_amount,
        "customer": customer_data,
        "user": str(sale.user),
        "items": [
            {
                "product": item.product.product_name,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "discount": item.discount,
                "total": item.total,
                "image": item.product.product_image.url if item.product.product_image else "",
            }
            for item in items
        ],
    }

    return JsonResponse(sale_data)

@login_required
@transaction.atomic
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sales, id=sale_id)
    try:
        sale.delete()
        messages.success(request, f"Sale {sale.reference} deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting sale: {e}")
    return redirect('sales')

#----------------------------------
# NOTIFICATIONS
#----------------------------------
def notifications(request):
    return render(request,'screens/administrator/activities.html')


#----------------------------------
# ACTIVITY/NOTIFICATION FUNCTIONS
#----------------------------------

def create_activity(user, activity_type, title, description, sale=None, product=None):
    """Create a new activity/notification"""
    activity = Activity.objects.create(
        user=user,
        activity_type=activity_type,
        title=title,
        description=description,
        sale=sale,
        product=product
    )
    return activity

def get_unread_activity_count():
    """Get count of unread activities"""
    from .models import Activity
    return Activity.objects.filter(is_read=False).count()

@login_required
@admin_only
def activities(request):
    """Display all activities"""

    # Base queryset
    activities_qs = Activity.objects.all().select_related('user', 'sale', 'product').order_by('-created_at')

    # Mark all unread activities as read when viewing the activities page
    Activity.objects.filter(is_read=False).update(is_read=True)

    # Paginate the activities list (10 per page)
    page = request.GET.get('page', 1)
    paginator = Paginator(activities_qs, 10)
    try:
        activities_page = paginator.page(page)
    except PageNotAnInteger:
        activities_page = paginator.page(1)
    except EmptyPage:
        activities_page = paginator.page(paginator.num_pages)

    context = {
        'activities': activities_page,
        'unread_count': 0  # Since we just marked all as read
    }
    return render(request, 'screens/administrator/activities.html', context)

@login_required
def mark_activities_read(request):
    """Mark all activities as read"""
    
    Activity.objects.filter(is_read=False).update(is_read=True)
    return redirect('activities')

@login_required
def activity_detail(request, activity_id):
    """Get activity details for modal display"""
    try:
        activity = Activity.objects.select_related('user', 'sale', 'product').get(id=activity_id)
        
        data = {
            'success': True,
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'activity_type': activity.get_activity_type_display(),
                'created_at': activity.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'user': {
                    'name': f"{activity.user.first_name} {activity.user.last_name}",
                    'username': activity.user.username,
                    'initials': f"{activity.user.first_name[0]}{activity.user.last_name[0]}" if activity.user.first_name and activity.user.last_name else activity.user.username[0].upper()
                },
                'sale': {
                    'id': activity.sale.id,
                    'reference': activity.sale.reference,
                    'total_amount': str(activity.sale.total_amount),
                    'customer_name': f"{activity.sale.customer.first_name} {activity.sale.customer.last_name}"
                } if activity.sale else None,
                'product': {
                    'id': activity.product.id,
                    'name': activity.product.product_name,
                    'sku': activity.product.sku
                } if activity.product else None
            }
        }
    except Activity.DoesNotExist:
        data = {
            'success': False,
            'error': 'Activity not found'
        }
    
    return JsonResponse(data)

@login_required
def sale_detail_modal(request, sale_id):
    """Get sale details for modal display"""
    try:
        sale = Sales.objects.select_related('customer', 'user').prefetch_related('salesitem_set__product').get(id=sale_id)
        
        # Calculate totals
        sale_items = sale.salesitem_set.all()
        subtotal = sum(item.quantity * item.unit_price for item in sale_items)
        
        data = {
            'success': True,
            'sale': {
                'id': sale.id,
                'reference': sale.reference,
                'sale_date': sale.sale_date.strftime('%B %d, %Y at %I:%M %p'),
                'status': sale.status,
                'payment_mode': sale.payment_mode,
                'total_amount': str(sale.total_amount),
                'subtotal': str(subtotal),
                'customer': {
                    'id': sale.customer.id,
                    'name': f"{sale.customer.first_name} {sale.customer.last_name}",
                    'email': getattr(sale.customer, 'email', 'N/A'),
                    'phone': getattr(sale.customer, 'phone', 'N/A')
                },
                'salesperson': {
                    'name': f"{sale.user.first_name} {sale.user.last_name}",
                    'username': sale.user.username
                },
                'items': [
                    {
                        'product_name': item.product.product_name,
                        'sku': item.product.sku,
                        'quantity': item.quantity,
                        'unit_price': str(item.unit_price),
                        'total': str(item.quantity * item.unit_price)
                    }
                    for item in sale_items
                ]
            }
        }
    except Sales.DoesNotExist:
        data = {
            'success': False,
            'error': 'Sale not found'
        }
    
    return JsonResponse(data)

@login_required
def delete_activity(request, activity_id):
    """Delete a specific activity."""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Optional: restrict deletion to admins or specific users
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete activities.")
        return redirect('activities')
    
    activity.delete()
    messages.success(request, "Activity deleted successfully.")
    
    return redirect('activities')
