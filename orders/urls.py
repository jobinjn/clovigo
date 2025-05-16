from django.urls import path
from .views import OrderView, SellerOrdersAPIView

app="orders"



urlpatterns = [
    path('order/', OrderView.as_view(), name='order'),
    path('orders/by-seller/', SellerOrdersAPIView.as_view(), name='orders-by-logged-in-seller'),

]
