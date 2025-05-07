from django.urls import path
from .views import OrderView

app="orders"

urlpatterns = [
    path('order/', OrderView.as_view(), name='order'),
]
