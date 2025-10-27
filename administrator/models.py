import uuid
from django.db import models
from django.core.exceptions import ValidationError
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
    product_cost_price = models.FloatField(help_text="How much the owner bought the product for")
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

    first_name = models.CharField(max_length=255,blank=True, null=True)
    last_name = models.CharField(max_length=255,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
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

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')
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

        # Auto-update total from SalesItems using selling_price
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('selling_price'), output_field=FloatField())
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
    selling_price = models.FloatField(default=0.0,editable=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.FloatField(editable=False)
    discount = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0, editable=False)

    def clean(self):
        """Validate the SalesItem before saving"""
        super().clean()
        
        if self.product and self.selling_price:
            # Check if selling price is significantly below cost price (allowing small margin for flexibility)
            cost_price = float(self.product.product_cost_price)
            selling_price = float(self.selling_price)
            
            # Allow up to 5% below cost price for promotional sales, but warn for larger losses
            min_allowed_price = cost_price * 0.95  # 5% below cost price
            
            if selling_price < min_allowed_price:
                loss_percentage = ((cost_price - selling_price) / cost_price) * 100
                raise ValidationError({
                    'selling_price': f"Selling price (GHC{selling_price:.2f}) is {loss_percentage:.1f}% below "
                    f"cost price (GHC {cost_price:.2f}) for {self.product.product_name}. "
                    f"This will result in significant loss. Minimum recommended: GHC{min_allowed_price:.2f}"
                })
        
        if self.product and self.quantity:
            # Validate stock availability (only for new items)
            if not self.pk and self.product.product_quantity < self.quantity:
                raise ValidationError({
                    'quantity': f"Insufficient stock for {self.product.product_name}. "
                    f"Requested: {self.quantity}, Available: {self.product.product_quantity}"
            })

    def save(self, *args, **kwargs):
        # Always set unit price from Product's selling price (the standard price)
        self.unit_price = self.product.product_selling_price
        
        # Auto-set selling price to unit price if not provided (allows custom pricing)
        if not self.selling_price:
            self.selling_price = self.unit_price

        # Run validation
        self.full_clean()

        # Calculate discount as difference between unit price and selling price
        # Positive discount means selling below standard price, negative means premium pricing
        price_difference = self.unit_price - self.selling_price
        if price_difference > 0:
            # Selling below standard price - this is a discount
            self.discount = price_difference * self.quantity
        else:
            # Selling at or above standard price - no discount (could be premium)
            self.discount = 0.0

        # Update stock for new items
        if not self.pk:  # new item only
            self.product.product_quantity -= self.quantity
            self.product.save(update_fields=["product_quantity"])

        # Calculate total: quantity * selling_price (discount is already factored into selling_price)
        self.total = self.quantity * self.selling_price

        super().save(*args, **kwargs)

    @property
    def profit_per_item(self):
        """Calculate profit per item (selling price - cost price)"""
        return self.selling_price - self.product.product_cost_price

    @property
    def total_profit(self):
        """Calculate total profit for this sale item"""
        return self.profit_per_item * self.quantity

    @property
    def profit_margin_percentage(self):
        """Calculate profit margin as percentage"""
        if self.selling_price == 0:
            return 0
        return (self.profit_per_item / self.selling_price) * 100

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity} @ GHC {self.selling_price:.2f}"


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


# --------------------------
# ACTIVITY/NOTIFICATION MODEL
# --------------------------
class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('sale_created', 'Sale Created'),
        ('product_added', 'Product Added'),
        ('stock_updated', 'Stock Updated'),
        ('user_created', 'User Created'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional reference to related objects
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} by {self.user.username}"