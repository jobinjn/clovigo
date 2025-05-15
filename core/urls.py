from django.urls import path
from core.views import *
from django.conf import settings
from django.conf.urls.static import static
from .views import CatalogHomeView

urlpatterns = [

    path('', CatalogHomeView.as_view(), name='catalog'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
