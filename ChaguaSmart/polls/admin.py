from django.contrib import admin
from django.utils import timezone  # Add this import
from .models import Poll, Option, Vote


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    # The field might be 'text' instead of 'option_text'
    list_display = ['poll', 'text']  # Change 'option_text' to match your actual field name
    list_filter = ['poll']
    search_fields = ['text', 'poll__title']  # Update here too


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'option', 'voted_at']
    list_filter = ['voted_at']
    search_fields = ['user__username', 'option__option_text']
    readonly_fields = ('voted_at',)


# Customize admin site header and title
admin.site.site_header = "ChaguaSmart Polls Administration"
admin.site.site_title = "ChaguaSmart Admin"
admin.site.index_title = "Polling System Management"


# Admin actions for bulk operations
@admin.action(description='Close selected polls')
def close_polls(modeladmin, request, queryset):
    """Close selected polls by setting end_time to now"""
    updated = queryset.update(end_time=timezone.now())
    modeladmin.message_user(
        request,
        f'{updated} poll(s) were successfully closed.'
    )


@admin.action(description='Activate selected polls')
def activate_polls(modeladmin, request, queryset):
    """Activate selected polls by setting start_time to now"""
    now = timezone.now()
    updated = queryset.filter(start_time__gt=now).update(start_time=now)
    modeladmin.message_user(
        request,
        f'{updated} poll(s) were successfully activated.'
    )


# Add actions to PollAdmin
PollAdmin.actions = [close_polls, activate_polls]


# Register additional models if they exist
try:
    from .models import PollCategory, PollView

    @admin.register(PollCategory)
    class PollCategoryAdmin(admin.ModelAdmin):
        list_display = ('name', 'description', 'color', 'poll_count')
        search_fields = ('name', 'description')

        def poll_count(self, obj):
            return obj.polls.count()
        poll_count.short_description = 'Polls Count'

    @admin.register(PollView)
    class PollViewAdmin(admin.ModelAdmin):
        list_display = ('poll', 'user', 'ip_address', 'viewed_at')
        list_filter = ('viewed_at', 'poll')
        readonly_fields = ('poll', 'user', 'ip_address', 'viewed_at')

        def has_add_permission(self, request):
            return False

        def has_change_permission(self, request, obj=None):
            return False

except ImportError:
    # Models don't exist, skip registration
    pass

# Suggested code change: User registration data (not directly related to admin code)
user_data = {
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123",
    "campus": "Main Campus"
}
