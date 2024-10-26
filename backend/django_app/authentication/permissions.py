from rest_framework import permissions

class IsTeamAdmin(permissions.BasePermission):
    """
    Custom permission to only allow team admins to perform certain actions
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Get the team membership
        try:
            membership = obj.members.through.objects.get(
                team=obj,
                user=request.user
            )
            return membership.role == 'admin'
        except obj.members.through.DoesNotExist:
            return False

class IsTeamMember(permissions.BasePermission):
    """
    Permission to only allow team members to access
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any team member
        if request.method in permissions.SAFE_METHODS:
            return obj.members.filter(id=request.user.id).exists()
        
        # Write permissions are only allowed to team members with proper roles
        try:
            membership = obj.members.through.objects.get(
                team=obj,
                user=request.user
            )
            return membership.role in ['admin', 'editor']
        except obj.members.through.DoesNotExist:
            return False

class IsAPIKeyOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an API key to access it
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user