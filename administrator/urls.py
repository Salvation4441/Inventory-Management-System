from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin-dashboard'),
    # path('purchase/',views.purchases,name='purchases'),
    path('profile/',views.profile,name='profile'),
    path('sales-report/',views.sales_report,name='sales-report'),
    path('settings/',views.settings,name='settings'),
    path('sales/',views.sales,name='sales')
]
