from rest_framework import permissions
from django.utils import timezone


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to create/edit polls.
    Regular users can only view polls.
    """
    
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for admin users
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsPollCreatorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow poll creators or admin users to edit/delete polls.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions for poll creator or admin
        return (request.user and request.user.is_authenticated and 
                (obj.created_by == request.user or request.user.is_admin))


class CanVotePermission(permissions.BasePermission):
    """
    Custom permission to check if user can vote on a poll.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only authenticated users can vote
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if poll is still active
        now = timezone.now()
        if obj.end_time and obj.end_time < now:
            return False
        
        if obj.start_time and obj.start_time > now:
            return False
        
        # Check if user has already voted (handled in view logic)
        return True


class IsVoterOrAdmin(permissions.BasePermission):
    """
    Custom permission for vote objects - only the voter or admin can view their votes.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can view all votes
        if request.user.is_admin:
            return True
        
        # Users can only view their own votes
        return obj.user == request.user


class CampusBasedPermission(permissions.BasePermission):
    """
    Permission that can be used to restrict access based on campus.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # If the object has a campus field, check if user belongs to same campus
        if hasattr(obj, 'campus') and hasattr(request.user, 'campus'):
            return obj.campus == request.user.campus or request.user.is_admin
        
        return True


class PollActivePermission(permissions.BasePermission):
    """
    Permission to check if poll is currently active for voting.
    """
    
    def has_object_permission(self, request, view, obj):
        now = timezone.now()
        
        # Check if poll has started
        if obj.start_time and obj.start_time > now:
            return False
        
        # Check if poll has ended
        if obj.end_time and obj.end_time < now:
            return False
        
        return True