from django.contrib import admin
from django.utils import timezone
from .models import Poll, Option, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_time', 'end_time', 'is_active', 'status')
    inlines = [OptionInline]
    search_fields = ('title', 'description')
    list_filter = ('is_active', 'start_time', 'end_time')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Settings', {
            'fields': ('is_anonymous', 'allow_multiple_votes', 'campus_restricted'),
            'classes': ('collapse',)
        }),
        ('Meta Information', {
            'fields': ('created_by', 'created_at', 'updated_at', 'total_votes_display', 'status_display'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new poll
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'poll', 'vote_count')
    search_fields = ('text', 'poll__title')
    list_filter = ('poll',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('poll')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'option', 'voted_at')
    search_fields = ('user__username', 'poll__title')
    list_filter = ('poll', 'voted_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'option', 'option__poll'
        )


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
