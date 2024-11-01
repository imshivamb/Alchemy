from ..models import APIKey, SecurityLog
from ..serializers.security import APIKeySerializer
import uuid
from .base import BaseViewSet

class APIKeyViewSet(BaseViewSet):
    serializer_class = APIKeySerializer

    def get_queryset(self):
        return APIKey.objects.filter(
            user=self.request.user,
            is_active=True
        )

    def perform_create(self, serializer):
        api_key = serializer.save(
            user=self.request.user,
            key=uuid.uuid4().hex
        )
        
        SecurityLog.objects.create(
            user=self.request.user,
            action='api_key_created',
            details={'key_name': api_key.name}
        )

    def perform_destroy(self, instance):
        SecurityLog.objects.create(
            user=self.request.user,
            action='api_key_deleted',
            details={'key_name': instance.name}
        )
        instance.is_active = False
        instance.save()