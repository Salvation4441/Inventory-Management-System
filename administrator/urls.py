from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin-dashboard'),
    path('error/',views.error_404,name='error-404'),
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
    path('manage-stocks/', views.manage_stocks, name='manage-stocks'),
    path('annual-report/', views.manage_stocks, name='annual-report'),
    path('profit-and-loss/', views.profit_and_loss, name='profit-and-loss'),
    
    # --------------------------
    # USER
    # --------------------------
    path('add-user/', views.addUser, name='addUser'),
    path('edit-user/<int:user_id>/', views.editUser, name='editUser'),
    path('delete-user/<int:user_id>/', views.deleteUser, name='deleteUser'),
    # path('view-user/<int:user_id>/', views.viewUser, name='viewUser'),
    
    

    # CATEGORY
    # --------------------------
    path('category/', views.allCategory, name='category'),
    path('add-category/', views.addCategory, name='addCategory'),
    # path('edit-category/<int:category_id>/', views.editCategory, name='editCategory'),
    path('delete-category/<int:category_id>/', views.deleteCategory, name='deleteCategory'),
    # path('view-category/<int:category_id>/', views.viewCategory, name='viewCategory'),
]
