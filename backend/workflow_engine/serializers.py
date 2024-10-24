from rest_framework import serializers
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
    """
    tasks = WorkflowTaskSerializer(many=True, read_only=True)
    webhooks = WebhookSerializer(many=True, read_only=True)
    
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
            'webhooks'
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'updated_at']