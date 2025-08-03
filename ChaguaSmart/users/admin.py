from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Only import User from users.models


class CustomUserAdmin(UserAdmin):
    # Add custom fields to the user admin
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('campus', 'is_admin')}),
    )
    
    # Add custom fields to the add user form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('campus', 'is_admin')}),
    )
    
    # Display these fields in the user list
    list_display = UserAdmin.list_display + ('campus', 'is_admin')
    
    # Add filters for custom fields
    list_filter = UserAdmin.list_filter + ('campus', 'is_admin')
    
    # Make campus searchable
    search_fields = UserAdmin.search_fields + ('campus',)


# Register User model - ONLY REGISTER ONCE
admin.site.register(User, CustomUserAdmin)

# Customize admin site header and title
admin.site.site_header = "ChaguaSmart Administration"
admin.site.site_title = "ChaguaSmart Admin"
admin.site.index_title = "Welcome to ChaguaSmart Administration"
