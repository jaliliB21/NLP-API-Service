from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # These fields will be displayed in the list view of the admin
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active', 'is_pro', 'free_analysis_count') # Added 'is_pro', 'free_analysis_count'
    
    # Fields to search by
    search_fields = ('email', 'username', 'full_name') 
    
    # Filters in the sidebar
    list_filter = ('is_staff', 'is_active', 'is_pro') # Added 'is_pro' to filters
    
    # Fieldsets define how fields are grouped and displayed on the add/change form
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'is_pro', 'free_analysis_count', 'is_email_verified')}), # Added 'is_pro', 'free_analysis_count' here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Add fields that should be editable when creating a user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password', 'password2', 'is_pro', 'free_analysis_count', 'is_email_verified'), # Added 'is_pro', 'free_analysis_count' for add form
        }),
    )
    
admin.site.register(CustomUser, CustomUserAdmin)