from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Workflow, WorkflowTask, Webhook, WebhookLog
from .serializers import WorkflowSerializer, WorkflowTaskSerializer, WebhookSerializer, WebhookLogSerializer

class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def limits(self, request):
        """Get workflow limit information for current user"""
        profile = request.user.profile
        return Response({
            'plan': profile.plan_type,
            'total_limit': profile.get_workflow_limit(),
            'current_count': request.user.workflow_set.filter(is_active=True).count(),
            'remaining': profile.workflows_remaining()
        })

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Add limit information to list response
        profile = request.user.profile
        response.data['limits'] = {
            'plan': profile.plan_type,
            'total_limit': profile.get_workflow_limit(),
            'remaining': profile.workflows_remaining()
        }
        return response
    
class WorkflowTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling WorkflowTask operations
    """
    serializer_class = WorkflowTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter tasks to show only those from workflows created by the current user
        """
        return WorkflowTask.objects.filter(workflow__created_by=self.request.user)
    
    def perform_create(self, serializer):
        """
        Validate workflow ownership before creating task
        """
        workflow = get_object_or_404(Workflow, id=self.request.data.get('workflow'))
        if workflow.created_by != self.request.user:
            raise PermissionError("You don't have permission to add tasks to this workflow")
        serializer.save()
        
class WebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Webhook operations
    """
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter webhooks to show only those from workflows created by the current user
        """
        return Webhook.objects.filter(workflow__created_by=self.request.user)
    
    def perform_create(self, serializer):
        """
        Set the created_by field and validate workflow ownership
        """
        workflow = get_object_or_404(Workflow, id=self.request.data.get('workflow'))
        if workflow.created_by != self.request.user:
            raise PermissionError("You don't have permission to add webhooks to this workflow")
        serializer.save(created_by=self.request.user)
        
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """
        Custom endpoint to handle webhook triggers
        URL: /api/webhooks/{webhook_id}/trigger/
        """
        webhook = self.get_object()
        if webhook.webhook_type != 'trigger':
            return Response(
                {"error": "This webhook is not a trigger type"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create webhook log
        log_data = {
            'webhook': webhook.id,
            'request_method': request.method,
            'request_headers': dict(request.headers),
            'request_body': request.data
        }
        log_serializer = WebhookLogSerializer(data=log_data)
        log_serializer.is_valid(raise_exception=True)
        log_serializer.save()

        # Here you would typically trigger the workflow execution
        # We'll implement this later with Celery
        
        return Response({"message": "Webhook triggered successfully"})

class WebhookLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing webhook logs (read-only)
    """
    serializer_class = WebhookLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter logs to show only those from webhooks owned by the current user
        """
        return WebhookLog.objects.filter(webhook__created_by=self.request.user)