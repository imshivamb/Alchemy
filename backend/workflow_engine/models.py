from django.db import models
from django.contrib.auth.models import User
import uuid

class Workflow(models.Model):
    """
    Main workflow model to store Automation workflows
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    workflow_data = models.JSONField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class WorkflowTask(models.Model):
    """
    Individual workflow tasks
    """
    TASK_TYPES = [
        ('trigger', 'Trigger'),
        ('action', 'Action'),
        ('condition', 'Condition'),
        ('transformer', 'Transformer'),
        ('ai_process', 'AI Process'),
    ]
    
    workflow = models.ForeignKey(Workflow, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    config = models.JSONField()
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"
    
    class Meta:
        ordering = ['order']

class Webhook(models.Model):
    """
    Handles both incoming triggers and outgoing action webhooks
    """
    WEBHOOK_TYPE_CHOICES = [
        ('trigger', 'Trigger'),
        ('action', 'Action'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow, related_name='webhooks', on_delete=models.CASCADE)
    webhook_type = models.CharField(max_length=50, choices=WEBHOOK_TYPE_CHOICES)
    
    # For trigger webhooks (incoming)
    trigger_url = models.URLField(unique=True, blank=True, null=True)
    secret_key = models.CharField(max_length=255, unique=True)
    
    # For action webhooks (outgoing)
    target_url = models.URLField(blank=True, null=True)
    http_method = models.CharField(max_length=10, default='POST')
    headers = models.JSONField(default=dict, blank=True)
    
    #Common Fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, help_text="Additional configuration for the webhook")
    
    def __str__(self):
        return f"{self.webhook_type} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = uuid.uuid4().hex
        super().save(*args, **kwargs)
        
class WebhookLog(models.Model):
    """
    Logs all webhook activities for debugging and monitoring
    """
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    request_method = models.CharField(max_length=10)
    request_headers = models.JSONField()
    request_body = models.JSONField()
    response_status = models.IntegerField(null=True)
    response_body = models.JSONField(null=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']

