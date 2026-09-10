import random
from django.core.management.base import BaseCommand
from authentication.models import CustomUser
from administrator.models import Category, Product, Customer, Sales, SalesItem
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds the database with initial data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # 1. Create Users
        admin_user, _ = CustomUser.objects.get_or_create(
            username='admin', 
            defaults={'email': 'admin@example.com', 'first_name': 'System', 'last_name': 'Admin', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()

        sales_user, _ = CustomUser.objects.get_or_create(
            username='sales1', 
            defaults={'email': 'sales1@example.com', 'first_name': 'John', 'last_name': 'Doe', 'role': 'SALESPERSON'}
        )
        sales_user.set_password('sales123')
        sales_user.save()

        # 2. Create Categories
        categories_data = [
            ('Electronics', 'ELE'),
            ('Groceries', 'GRO'),
            ('Clothing', 'CLO'),
            ('Health', 'HEA'),
            ('Beauty', 'BEA'),
        ]
        categories = []
        for name, code in categories_data:
            cat, _ = Category.objects.get_or_create(category_name=name, defaults={'category_code': code})
            categories.append(cat)

        # 3. Create Products
        products_data = [
            ('Smartphone X', 'Electronics', 10000, 1200.0, 800.0),
            ('Laptop Pro', 'Electronics', 10000, 2500.0, 1800.0),
            ('Headphones Z', 'Electronics', 10000, 150.0, 90.0),
            ('Organic Milk', 'Groceries', 20000, 15.0, 10.0),
            ('Brown Bread', 'Groceries', 10000, 5.0, 3.0),
            ('Cotton T-Shirt', 'Clothing', 20000, 25.0, 12.0),
            ('Denim Jeans', 'Clothing', 10000, 50.0, 25.0),
            ('Vitamin C', 'Health', 10000, 20.0, 12.0),
            ('Face Cream', 'Beauty', 10000, 45.0, 20.0),
            ('Perfume Luxe', 'Beauty', 10000, 120.0, 60.0),
        ]
        products = []
        for name, cat_name, qty, sell, cost in products_data:
            cat = Category.objects.get(category_name=cat_name)
            # ALWAYS recreate product to ensure stock is reset for seeding
            Product.objects.filter(product_name=name).delete()
            prod = Product.objects.create(
                product_name=name, 
                product_category=cat, 
                product_quantity=qty, 
                product_selling_price=sell, 
                product_cost_price=cost
            )
            products.append(prod)

        # 4. Create Customers
        customers_data = [
            ('Alice', 'Smith', 'alice@example.com', '123456789', 'Accra'),
            ('Bob', 'Johnson', 'bob@example.com', '234567890', 'Kumasi'),
            ('Charlie', 'Brown', 'charlie@example.com', '345678901', 'Tamale'),
            ('Diana', 'Prince', 'diana@example.com', '456789012', 'Cape Coast'),
            ('Edward', 'Norton', 'edward@example.com', '567890123', 'Accra'),
        ]
        customers = []
        for fname, lname, email, phone, addr in customers_data:
            cust, _ = Customer.objects.get_or_create(
                email=email, 
                defaults={'first_name': fname, 'last_name': lname, 'phone': phone, 'address': addr}
            )
            customers.append(cust)

        # 5. Create Sales for the current and previous year
        # Generate sales for the last 2 years to populate annual report
        current_year = timezone.now().year
        years = [current_year, current_year - 1]
        
        for year in years:
            for month in range(1, 13):
                # Create 2-5 sales per month
                for _ in range(random.randint(2, 5)):
                    customer = random.choice(customers)
                    # We need to trick sale_date because it's auto_now_add. 
                    # For seed data, we create it then update the field.
                    sale = Sales.objects.create(
                        customer=customer,
                        user=sales_user,
                        status='Completed',
                        payment_mode=random.choice(['Cash', 'MOMO'])
                    )
                    
                    # Manually override sale_date for historical data
                    sale_date = timezone.datetime(year, month, random.randint(1, 28), random.randint(8, 18), random.randint(0, 59))
                    Sales.objects.filter(pk=sale.pk).update(sale_date=sale_date)

                    # Add 1-3 items to each sale
                    for _ in range(random.randint(1, 3)):
                        product = random.choice(products)
                        qty = random.randint(1, 5)
                        # Selling price usually matches product_selling_price, occasionally slightly different
                        selling_price = product.product_selling_price if random.random() > 0.2 else product.product_selling_price * 0.95
                        
                        SalesItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=qty,
                            selling_price=selling_price
                        )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with users, products, customers, and historical sales!'))
