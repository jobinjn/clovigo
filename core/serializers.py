"""Error Serializers for Doc's."""
from rest_framework import serializers
from core.models import ImageModel


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = "__all__"

