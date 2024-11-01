from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """Base model with common fields and functionality"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the object instead of permanently removing it"""
        self.is_active = False
        self.save()