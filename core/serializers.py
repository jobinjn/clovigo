"""Error Serializers for Doc's."""
from rest_framework import serializers
from core.models import ImageModel, ColorModel


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = "__all__"

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorModel
        fields = ['id', 'color', 'slug', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']