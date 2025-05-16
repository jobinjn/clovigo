
from django.urls import path
from cart.views import (CartView,CartRemoveView, FavoriteDeleteAPIView, FavoriteListCreateAPIView)


app_name = "cart"

urlpatterns = [
    path('cart/', CartView.as_view(), name="addtocart"),
    path('cartdelete/<int:cart_id>/',CartRemoveView.as_view(),name="cartdelete"),
    path('favorites/', FavoriteListCreateAPIView.as_view(), name='favorites-list-create'),
    path('favorites/<int:pk>/', FavoriteDeleteAPIView.as_view(), name='favorites-delete'),
]
