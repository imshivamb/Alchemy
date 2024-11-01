from rest_framework import serializers

class TimestampedSerializer(serializers.ModelSerializer):
    """Base serializer with common timestamp fields"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True