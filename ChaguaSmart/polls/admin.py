from django.contrib import admin
from django.utils import timezone
from django.db.models import Count
from django.utils.html import format_html
from .models import Poll, Option, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    fields = ('option_text',)


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_time', 'end_time', 'status_display', 'total_votes_display')
    list_filter = ('start_time', 'end_time', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'total_votes_display', 'status_display')
    inlines = [OptionInline]
    date_hierarchy = 'created_at'
    
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
    
    def status_display(self, obj):
        """Display poll status with color coding"""
        status = obj.status
        colors = {
            'active': 'green',
            'upcoming': 'orange',
            'ended': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'black'),
            status.upper()
        )
    status_display.short_description = 'Status'
    
    def total_votes_display(self, obj):
        """Display total votes count"""
        if obj.pk:
            return obj.total_votes
        return "No votes yet"
    total_votes_display.short_description = 'Total Votes'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'poll', 'vote_count_display', 'vote_percentage_display')
    list_filter = ('poll', 'created_at')
    search_fields = ('option_text', 'poll__title')
    readonly_fields = ('created_at', 'vote_count_display', 'vote_percentage_display')
    
    def vote_count_display(self, obj):
        """Display vote count for this option"""
        return obj.vote_count
    vote_count_display.short_description = 'Votes'
    
    def vote_percentage_display(self, obj):
        """Display vote percentage for this option"""
        percentage = obj.vote_percentage
        return f"{percentage}%"
    vote_percentage_display.short_description = 'Percentage'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('poll')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll_title', 'option', 'voted_at', 'ip_address')
    list_filter = ('voted_at', 'option__poll', 'user')
    search_fields = ('user__username', 'option__option_text', 'option__poll__title')
    readonly_fields = ('voted_at', 'user', 'option', 'ip_address', 'user_agent')
    date_hierarchy = 'voted_at'
    
    fieldsets = (
        ('Vote Information', {
            'fields': ('user', 'option', 'voted_at')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def poll_title(self, obj):
        """Display poll title for this vote"""
        return obj.option.poll.title
    poll_title.short_description = 'Poll'
    
    def has_add_permission(self, request):
        """Prevent manual vote creation through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent vote modification through admin"""
        return False
    
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
