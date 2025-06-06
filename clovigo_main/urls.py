from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from core.views import ImageViewSet, ColorViewSet

from accounts.views import CategoryAdminViewSet

router = DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'admin/categories', CategoryAdminViewSet, basename='admin-categories')



urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include("core.urls")), 
    path('api/accounts/', include("accounts.urls")),
    path('carts/', include("cart.urls")),
    path('orders/', include("orders.urls")),
    path('products/', include("products.urls")),
    path('', include(router.urls)),

    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/catalog/main/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/catalog/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
