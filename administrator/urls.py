from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin-dashboard'),
    # path('purchase/',views.purchases,name='purchases'),
    path('profile/',views.profile,name='profile'),
    path('sales-report/',views.sales_report,name='sales-report'),
    path('settings/',views.settings,name='settings'),
    path('sales/',views.sales,name='sales'),
    path('products/', views.products, name='products'),
    path('users/',views.users,name='users'),
    path('customers/',views.customers,name='customers'),
    path('product-details/', views.product_details, name='products-detail'),
    path('edit-product/', views.edit_product, name='edit-product'),
    path('add-product/', views.add_product, name='add-product'),
    path('category/', views.category, name='category'),
]
