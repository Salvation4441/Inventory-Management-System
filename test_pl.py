#!/usr/bin/env python
"""
Quick test script to identify float conversion issues in profit_and_loss function
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
django.setup()

from administrator.views import profit_and_loss
from django.test import RequestFactory
from authentication.models import CustomUser

def test_profit_and_loss():
    """Test the profit_and_loss function to identify list conversion issues"""
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/admin/profit-and-loss/')
    
    # Create a mock admin user
    try:
        admin_user = CustomUser.objects.filter(user_type='admin').first()
        if not admin_user:
            print("No admin user found. Creating a mock admin user...")
            admin_user = CustomUser.objects.create_user(
                username='test_admin',
                email='admin@test.com',
                password='testpass',
                user_type='admin'
            )
    except Exception as e:
        print(f"Error getting admin user: {e}")
        return

    request.user = admin_user
    
    try:
        print("Testing profit_and_loss function...")
        response = profit_and_loss(request)
        print("SUCCESS: profit_and_loss function executed without errors!")
        print(f"Response status: {response.status_code if hasattr(response, 'status_code') else 'Template rendered'}")
        
    except Exception as e:
        print(f"ERROR in profit_and_loss function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_profit_and_loss()