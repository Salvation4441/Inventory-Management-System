import uuid
from django.db import models
from authentication.models import CustomUser
from django.db.models import Sum, F, FloatField

# --------------------------
# CATEGORY
# --------------------------
class Category(models.Model):
    category_name = models.CharField(max_length=100, blank=True, null=True)
    category_code = models.CharField(max_length=3, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.category_code:
            self.category_code = self.category_name[:2].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name or "(No Name)"


# --------------------------
# PRODUCT
# --------------------------
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, unique=True, editable=False)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    product_brand = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_quantity = models.PositiveIntegerField()
    product_selling_price = models.FloatField(help_text="How much the owner sells to customers")
    product_buying_price = models.FloatField(help_text="How much the owner bought the product for")
    product_discount = models.FloatField(default=0.0, help_text="Discount per item")
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    manufacture_name = models.CharField(max_length=100, blank=True, null=True)
    manufacture_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.product_sku:
            prefix = self.product_name[:2].upper()
            cat_code = self.product_category.category_code.upper() if self.product_category.category_code else "XX"

            last_product = (
                Product.objects.filter(product_sku__startswith=f"{cat_code}-{prefix}")
                .order_by('-product_sku')
                .first()
            )

            if last_product:
                try:
                    last_number = int(last_product.product_sku[-3:])
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1

            self.product_sku = f"{cat_code}-{prefix}{new_number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.product_sku})"


# --------------------------
# CUSTOMER
# --------------------------
class Customer(models.Model):
    GENDER = [('Male', 'Male'), ('Female', 'Female')]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER, default='Male')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# --------------------------
# SALES (ORDER)
# --------------------------
class Sales(models.Model):
    STATUS_CHOICES = [('Completed', 'Completed'), ('Pending', 'Pending')]
    PAYMENT_CHOICES = [('Cash', 'Cash'), ('MOMO', 'MOMO')]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Cash')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length=16, unique=True, null=True, editable=False)
    total_amount = models.FloatField(default=0.0, editable=False)

    def save(self, *args, **kwargs):
        # Auto-generate reference number
        if not self.reference:
            self.reference = f"SAL{uuid.uuid4().hex[:8].upper()}"
            prefix = "SAL"
            last_sale = Sales.objects.order_by("id").last()
            next_number = 1 if not last_sale else last_sale.id + 1
            self.reference = f"{prefix}{next_number:05d}"

        super().save(*args, **kwargs)

        # Auto-update total from SalesItems
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
        )['total'] or 0.0
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.reference} - {self.customer.first_name} ({self.status})"


# --------------------------
# SALES ITEM (MANY PRODUCTS PER SALE)
# --------------------------
class SalesItem(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.FloatField(editable=False)
    discount = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0, editable=False)

    def save(self, *args, **kwargs):
        # Auto-set unit price from Product
        if not self.unit_price:
            self.unit_price = self.product.product_selling_price

        # Validate stock
        if not self.pk:  # new item only
            if self.product.product_quantity < self.quantity:
                raise ValueError(f"Not enough stock for {self.product.product_name}. Available: {self.product.product_quantity}")
            self.product.product_quantity -= self.quantity
            self.product.save(update_fields=["product_quantity"])

        # Calculate total after discount
        subtotal = self.quantity * self.unit_price
        self.total = max(subtotal - self.discount, 0)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"


# --------------------------
# MANAGE STOCKS
# --------------------------
class ManageStocks(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history')
    previous_quantity = models.PositiveIntegerField(default=0, editable=False)
    quantity_added = models.PositiveIntegerField(help_text="Quantity to add to stock")
    new_quantity = models.PositiveIntegerField(default=0, editable=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        verbose_name = 'Stock Record'
        verbose_name_plural = 'Stock Records'

    def save(self, *args, **kwargs):
        # Capture previous quantity from product and calculate new quantity
        if not self.pk:  # Only on creation
            # Get previous quantity from product table
            self.previous_quantity = self.product.product_quantity
            # Calculate new quantity
            self.new_quantity = self.previous_quantity + self.quantity_added
            
            # Update product stock in product table
            self.product.product_quantity = self.new_quantity
            self.product.save(update_fields=["product_quantity"])
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} - Added {self.quantity_added} (from {self.previous_quantity} to {self.new_quantity})"