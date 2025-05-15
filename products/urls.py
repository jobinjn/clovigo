"""
URL mappings for the accounts.
"""
from django.urls import path
from products.views import (ProductGetView,
                            ProductCreate, 
                            ProductGetbyNameView,
                            ProductUpdateView,
                            PostReviewAPIView,
                            ListReviewAPIView,
                            ProductGetIdView,
                            UpdateReviewAPIView,
                            ProductListAPIView, ProductSearchView, ProductChoicesView, BuyNowAPIView, SellerProductListView,
                            ProductDeleteView)
                            


app_name = "products"

urlpatterns = [

    path('customer/products/search/', ProductSearchView.as_view(),
         name='customer-product-search'),
    path('choices/', ProductChoicesView.as_view(), name='api-choices'),
    path('buy-now/<int:product_id>/', BuyNowAPIView.as_view(), name='buy_now_api'),

    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path ('productcreate/', ProductCreate.as_view(), name="productcreate"),
    path('productview/<str:product_category>/', ProductGetView.as_view(), name="productget"),   #   http://127.0.0.1:8000/products/productview/Food/
    path('product/<str:product_name>/', ProductGetbyNameView.as_view(), name='productgetbyname'),  #  http://127.0.0.1:8000/products/product/mango/
    path('productbyid/<int:id>/', ProductGetIdView.as_view(), name='productgetbyid'),
    path('productupdate/<int:id>/', ProductUpdateView.as_view(), name='productupdate'),
    path('productdelete/<int:id>/', ProductDeleteView.as_view(), name='product-delete'),
    path('reviewpost/<int:product_id>', PostReviewAPIView.as_view(), name='reviewpost'),
    path('reviewlist/<int:product_id>/', ListReviewAPIView.as_view(), name='reviewb list'),
    path('reviewupdate/<int:pk>/',UpdateReviewAPIView.as_view(), name='reviewupdate'),
    path('seller/products/', SellerProductListView.as_view(), name='seller-product-list'),

]
