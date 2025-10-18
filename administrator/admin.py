from django.contrib import admin
from .models import Category, Product, Customer, Sales, SalesItem


# --------------------------
# CATEGORY ADMIN
# --------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at', 'updated_at')
    search_fields = ('name', 'code')
    ordering = ('name',)


# --------------------------
# PRODUCT ADMIN
# --------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'quantity', 'selling_price', 'buying_price', 'discount')
    list_filter = ('category', 'manufacture_date', 'expiry_date')
    search_fields = ('name', 'sku', 'brand')
    readonly_fields = ('sku', 'created_at', 'updated_at')
    ordering = ('name',)


# --------------------------
# CUSTOMER ADMIN
# --------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'gender', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('gender',)
    ordering = ('first_name',)


# --------------------------
# INLINE: SALES ITEMS (INLINE UNDER SALES)
# --------------------------
class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 1  # allows one blank line for adding new items
    readonly_fields = ('unit_price','total',)
    fields = ('product', 'quantity', 'unit_price', 'discount', 'total')
    
    def get_readonly_fields(self, request, obj=None):
        # Allow editing only quantity and discount; others auto-filled
        if obj:
            return self.readonly_fields + ('unit_price',)
        return self.readonly_fields


# --------------------------
# SALES ADMIN
# --------------------------
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer', 'status', 'payment_mode', 'total_amount', 'sale_date', 'user')
    search_fields = ('reference', 'customer__first_name', 'customer__last_name')
    list_filter = ('status', 'payment_mode', 'sale_date')
    date_hierarchy = 'sale_date'
    readonly_fields = ('reference', 'total_amount', 'sale_date', 'updated_at')
    inlines = [SalesItemInline]

    def save_model(self, request, obj, form, change):
        # Assign current logged-in user if not already set
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer', 'user').prefetch_related('items')


# --------------------------
# SALES ITEM ADMIN (standalone, optional)
# --------------------------
@admin.register(SalesItem)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'discount', 'total')
    search_fields = ('product__name', 'sale__reference')
    list_filter = ('product',)
    readonly_fields = ('unit_price', 'total')
    ordering = ('-sale',)
