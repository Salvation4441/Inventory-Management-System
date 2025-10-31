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
    path('search-customers/', views.searchCustomers, name='search-customers'),

    # SALES
    # --------------------------
    path('sales/',views.sales,name='sales'),
    path('add-sales/',views.addSales,name='add-sales'),
    path('sales/<int:sale_id>/detail/', views.saleDetail, name='sale-detail'),
    path('sales/<int:sale_id>/receipt/', views.sale_receipt, name='sale-receipt'),
    path('sales/<int:sale_id>/delete/', views.delete_sale, name='delete-sale'),

    # MANAGE STOCKS
    path('manage-stocks/', views.manageStocks, name='manage-stocks'),
    path('edit-stock/<int:stock_id>/', views.editManageStock, name='edit-stock'),
    path('delete-stock/<int:stock_id>/', views.deleteManageStock, name='delete-stock'),
    
    # ACTIVITIES/NOTIFICATIONS
    path('activities/', views.activities, name='activities'),
    path('mark-activities-read/', views.mark_activities_read, name='mark-activities-read'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity-detail'),
    path('sale-modal/<int:sale_id>/', views.sale_detail_modal, name='sale-detail-modal'),
    path('delete-activity/<int:activity_id>/', views.delete_activity, name='delete-activity'),

    # NOTIFICATIONS
    # path('notifications/', views.notifications, name='notifications'),

    # Catch-all pattern for invalid URLs (should be last)
    path('<path:invalid_path>/', views.handle_invalid_url, name='handle-invalid-url'),

]