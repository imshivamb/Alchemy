from rest_framework import serializers
from django.conf import settings
from .models import Workflow, WorkflowTask, Webhook, WebhookLog

class WorkflowTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkflowTask model
    """
    class Meta:
        model = WorkflowTask
        fields = [
            'id',
            'name',
            'task_type',
            'config',
            'order',
            'is_active',
            'workflow',
        ]
        read_only_fields = ['id']
        
class WebhookLogSerializer(serializers.ModelSerializer):
    """
    Serializer for WebhookLog model
    """
    class Meta:
        model = WebhookLog
        fields = [
            'id',
            'webhook',
            'timestamp',
            'request_method',
            'request_headers',
            'request_body',
            'response_status',
            'response_body',
            'error_message'
        ]
        read_only_fields = ['id', 'timestamp']
        
class WebhookSerializer(serializers.ModelSerializer):
    """
    Serializer for Webhook model
    Includes logs as nested serializer
    """
    logs = WebhookLogSerializer(many=True, read_only=True)
    class Meta:
        model = Webhook
        fields = [
            'id',
            'name',
            'workflow',
            'webhook_type',
            'trigger_url',
            'secret_key',
            'target_url',
            'http_method',
            'headers',
            'created_by',
            'created_at',
            'is_active',
            'config',
            'logs'
        ]
        read_only_fields = ['id', 'secret_key', 'created_at', 'created_by', 'trigger_url']
        
class WorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for Workflow model
    Includes nested serializers for tasks and webhooks
    Handles workflow limits based on user's plan
    """
    tasks = WorkflowTaskSerializer(many=True, read_only=True)
    webhooks = WebhookSerializer(many=True, read_only=True)
    workflow_limits = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = [
            'id',
            'name',
            'description',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
            'workflow_data',
            'tasks',
            'webhooks',
            'workflow_limits'  # Added workflow limits info
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'updated_at', 'workflow_limits']

    def validate(self, attrs):
        """
        Validate workflow creation against user's plan limits
        """
        request = self.context.get('request')
        if request and request.method == 'POST':  # Only check on creation
            user = request.user
            current_workflow_count = Workflow.objects.filter(
                created_by=user,
                is_active=True
            ).count()

            # Get user's plan limit or default
            max_allowed = settings.WORKFLOW_LIMITS.get(
                user.profile.plan_type,
                settings.DEFAULT_WORKFLOW_LIMIT
            )

            if current_workflow_count >= max_allowed:
                raise serializers.ValidationError({
                    'error': f'Maximum workflow limit ({max_allowed}) reached for your '
                            f'{user.profile.plan_type} plan. Please upgrade to create more workflows.',
                    'current_count': current_workflow_count,
                    'max_allowed': max_allowed,
                    'plan': user.profile.plan_type
                })

        return attrs

    def get_workflow_limits(self, obj):
        """
        Get workflow limit information for the user
        """
        user = obj.created_by
        current_count = Workflow.objects.filter(
            created_by=user,
            is_active=True
        ).count()
        max_allowed = settings.WORKFLOW_LIMITS.get(
            user.profile.plan_type,
            settings.DEFAULT_WORKFLOW_LIMIT
        )
        
        return {
            'plan': user.profile.plan_type,
            'max_allowed': max_allowed,
            'current_count': current_count,
            'remaining': max(0, max_allowed - current_count)
        }

    def to_representation(self, instance):
        """
        Customize the output representation
        """
        data = super().to_representation(instance)
        
        # Include task count
        data['task_count'] = instance.tasks.count()
        
        # Include webhook count
        data['webhook_count'] = instance.webhooks.count()
        
        return data