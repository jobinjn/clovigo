from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured
from drf_spectacular.utils import (extend_schema,
                                   OpenApiResponse)
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ImageModel, ColorModel
from .serializers import ImageSerializer
from django.utils.text import slugify

from .serializers import ColorSerializer
class CatalogHomeView(APIView):
    """
    API endpoint to provide the catalog details.
    Returns catalog main url.
    """

    @extend_schema(
        summary="Redirector",
        description="Catalog main redirector",
        request=None,
        responses={
            200: OpenApiResponse(
                response=None,
            )
        },
        tags=["Catalog"]
    )
    def get(self, request):
        """
        Handles GET requests to return API documentation link dynamically.
        """
        try:
            current_site = get_current_site(request).domain
            
            swagger_url = reverse("swagger-ui")
            catalog_link = f"{request.scheme}://{current_site}{swagger_url}"

            response_data = {
                "message": "Welcome to CloviGo API",
                "catalog": catalog_link,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ImproperlyConfigured:
            return Response(
                {"error": "Site configuration is missing or incorrect."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ImageViewSet(viewsets.ModelViewSet):
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser] 


class ColorViewSet(viewsets.ModelViewSet):
    queryset = ColorModel.objects.all()
    serializer_class = ColorSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.slug = slugify(instance.color)
        instance.save()

    def get_queryset(self):
        queryset = ColorModel.objects.all()
        color = self.request.query_params.get('color')
        is_active = self.request.query_params.get('is_active')

        if color:
            queryset = queryset.filter(color__icontains=color)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset.order_by('color')

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        color = self.get_object()
        color.deactivate()
        return Response({'status': f'Color "{color.color}" deactivated.'})

