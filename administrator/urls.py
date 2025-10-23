from django.urls import path
from . import views

urlpatterns = [
    
    # --------------------------
    # MAIN DASHBOARD
    # --------------------------
    path('', views.admin_dashboard, name='admin-dashboard'),
    path('error/',views.error_404,name='error-404'),
    path('profile/',views.profile,name='profile'),
    path('settings/',views.settings,name='settings'),
    
    
    # --------------------------
    # SALES REPORT
    # --------------------------
    path('sales/',views.sales,name='sales'),
    path('sales-report/',views.salesReport,name='sales-report'),
    path('annual-report/', views.annualReport, name='annual-report'),
    path('profit-and-loss/', views.profit_and_loss, name='profit-and-loss'),
    
    # --------------------------
    # USER
    # --------------------------
    path('users/',views.users,name='users'),
    path('add-user/', views.addUser, name='addUser'),
    path('edit-user/<int:user_id>/', views.editUser, name='editUser'),
    path('delete-user/<int:user_id>/', views.deleteUser, name='deleteUser'),
    path('profile/',views.profile,name='profile'),
    path('settings/',views.settings,name='settings'),
    
    

    # CATEGORY
    # --------------------------
    path('category/', views.allCategory, name='category'),
    path('add-category/', views.addCategory, name='addCategory'),
    path('edit-category/<str:category_id>/', views.editCategory, name='editCategory'),
    path('delete-category/<str:category_id>/', views.deleteCategory, name='deleteCategory'),
    
    
     # PRODUCTS
    # --------------------------
    path('products/', views.products, name='products'),
    path('add-product/', views.addProduct, name='addProduct'),
    path('delete-product/<int:product_id>/', views.deleteProduct, name='deleteProduct'),
    path('product/<int:product_id>/', views.productDetails, name='productDetails'),
    path('edit-product/<int:product_id>/', views.editProduct, name='editProduct'),
    path('search-products/', views.searchProducts, name='search-products'),
    # path('delete-product/<int:product_id>/', views.deleteProduct, name='deleteProduct'),


    # CUSTOMERS
    # --------------------------
    path('customers/',views.customers,name='customers'),
    path('customers/create/', views.customerCreate, name='customer_create'),
    path('customers/<str:id>/edit/', views.customerEdit, name='customer_edit'),
    path('customers/<str:id>/delete/', views.customerDelete, name='customer_delete'),

    # SALES
    # --------------------------
    path('sales/',views.sales,name='sales'),
    path('add-sales/',views.addSales,name='add-sales'),
    
    
    # MANAGE STOCKS
    path('manage-stocks/', views.manageStocks, name='manage-stocks'),
]