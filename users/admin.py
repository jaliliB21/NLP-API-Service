from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # These fields will be displayed in the list view of the admin
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active') # Added 'username' here
    
    # Fields to search by
    search_fields = ('email', 'username', 'full_name') # Added 'username' here
    
    # Filters in the sidebar
    list_filter = ('is_staff', 'is_active')
    
    # Fieldsets define how fields are grouped and displayed on the add/change form
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}), # Added 'username' here
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Add fields that should be editable when creating a user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password', 'password2'), # Added 'username' and 'full_name' for add form
        }),
    )
    
    # Order of fields in the add user form
    # Note: UserAdmin has specific add_fieldsets, make sure to override it if needed.
    # The default add_fieldsets for UserAdmin might not include full_name,
    # so explicitly defining add_fieldsets ensures consistency.
    
    # If you want to use the default UserAdmin's add_fieldsets and just add to it,
    # it's more complex, but explicitly defining it like above is common.


admin.site.register(CustomUser, CustomUserAdmin)