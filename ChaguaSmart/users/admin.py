from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Poll, Option, Vote


class CustomUserAdmin(BaseUserAdmin):
    # Add custom fields to the user admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('campus', 'is_admin')}),
    )
    
    # Add custom fields to the add user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('campus', 'is_admin')}),
    )
    
    # Display these fields in the user list
    list_display = BaseUserAdmin.list_display + ('campus', 'is_admin')
    
    # Add filters for custom fields
    list_filter = BaseUserAdmin.list_filter + ('campus', 'is_admin')
    
    # Make campus searchable
    search_fields = BaseUserAdmin.search_fields + ('campus',)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_time', 'end_time')
    list_filter = ('start_time', 'end_time', 'created_by')
    search_fields = ('title', 'description')
    inlines = [OptionInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new poll
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'option', 'voted_at')
    list_filter = ('voted_at', 'option__poll')
    search_fields = ('user__username', 'option__option_text')
    readonly_fields = ('voted_at',)


# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Option)
admin.site.register(Vote, VoteAdmin)

# Customize admin site header and title
admin.site.site_header = "ChaguaSmart Administration"
admin.site.site_title = "ChaguaSmart Admin"
admin.site.index_title = "Welcome to ChaguaSmart Administration"
