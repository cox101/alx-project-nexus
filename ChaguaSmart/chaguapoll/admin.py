from django.contrib import admin
from django.utils import timezone
from django.db.models import Count
from .models import Poll, Option, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    fields = ('option_text',)


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'start_time', 'end_time', 'is_active', 'total_votes')
    list_filter = ('start_time', 'end_time', 'created_by')
    search_fields = ('title', 'description')
    readonly_fields = ('created_by', 'total_votes_display')
    inlines = [OptionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Meta Information', {
            'fields': ('created_by', 'total_votes_display'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new poll
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def is_active(self, obj):
        now = timezone.now()
        return obj.start_time <= now <= obj.end_time
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def total_votes(self, obj):
        return Vote.objects.filter(option__poll=obj).count()
    total_votes.short_description = 'Total Votes'
    
    def total_votes_display(self, obj):
        if obj.pk:
            return self.total_votes(obj)
        return "No votes yet"
    total_votes_display.short_description = 'Total Votes'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'poll', 'vote_count')
    list_filter = ('poll',)
    search_fields = ('option_text', 'poll__title')
    readonly_fields = ('vote_count_display',)
    
    def vote_count(self, obj):
        return obj.vote_set.count()
    vote_count.short_description = 'Votes'
    
    def vote_count_display(self, obj):
        if obj.pk:
            return self.vote_count(obj)
        return "No votes yet"
    vote_count_display.short_description = 'Vote Count'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll_title', 'option', 'voted_at')
    list_filter = ('voted_at', 'option__poll', 'user')
    search_fields = ('user__username', 'option__option_text', 'option__poll__title')
    readonly_fields = ('voted_at', 'user', 'option')
    
    def poll_title(self, obj):
        return obj.option.poll.title
    poll_title.short_description = 'Poll'
    
    def has_add_permission(self, request):
        # Prevent manual vote creation through admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent vote modification through admin
        return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'option', 'option__poll'
        )


# Customize admin site header and title
admin.site.site_header = "ChaguaSmart Polling Administration"
admin.site.site_title = "ChaguaSmart Admin"
admin.site.index_title = "Polling System Management"


# Admin actions for bulk operations
@admin.action(description='Close selected polls')
def close_polls(modeladmin, request, queryset):
    queryset.update(end_time=timezone.now())

@admin.action(description='Activate selected polls')
def activate_polls(modeladmin, request, queryset):
    now = timezone.now()
    queryset.update(start_time=now)

# Add actions to PollAdmin
PollAdmin.actions = [close_polls, activate_polls]