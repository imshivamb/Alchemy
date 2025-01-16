from rest_framework import serializers
from ..models.workspace import Workspace, WorkspaceMembership

class WorkspaceSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'role', 'is_owner',
            'plan_type', 'settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_role(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
            
        if obj.owner == request.user:
            return 'admin'
            
        membership = obj.workspace_members.filter(user=request.user).first()
        return membership.role if membership else None

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False
        return obj.owner == request.user

class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMembership
        fields = [
            'id', 'workspace', 'user', 'role', 
            'joined_at', 'invited_by'
        ]
        read_only_fields = ['id', 'joined_at']