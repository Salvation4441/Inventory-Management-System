from django.contrib import admin
from .models import *

# Register your models here.
# register user
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_displaylist_display = ('username', 'email', 'phone', 'created_at')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('created_at',)
