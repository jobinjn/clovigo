
from django.urls import path
from cart.views import (CartView,CartRemoveView)


app_name = "cart"

urlpatterns = [
    path('cart/', CartView.as_view(), name="addtocart"),
    path('cartdelete/<int:cart_id>/',CartRemoveView.as_view(),name="cartdelete")
]
