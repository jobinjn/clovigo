"""
URL mappings for the accounts.
"""
from django.urls import path
from accounts.views import (CustomerSignUpView,
                            OTPValidateView,
                            OTPResendView,
                            SellerSignUpView,
                            DeliveryBoySignUpView,
                            LoginUserView,
                            ApproveSellerView,
                            ApproveDeliveryBoyView,
                            UserProfileView,
                            SellerListAPI, CustomerListAPI, DeliveryBoyListAPI,
                            AdminProductDashboardAPI,AdminOrderDashboardAPI,
DeliveryBoyChoicesView
                            )
from accounts.views import AdminLoginAPIView


app_name = "accounts"

urlpatterns = [
    #signup urls
    path('signup/customer/', CustomerSignUpView.as_view(), name="customer_signup"),     
    path('signup/seller/', SellerSignUpView.as_view(), name="seller_signup"),
    path('signup/deliveryboy/', DeliveryBoySignUpView.as_view(), name="deliveryboy_signup"),

    #otp validation
    path('user/otp/validate/', OTPValidateView.as_view(), name="otp_validate"),

    #otp resend
    path('user/otp/resend/', OTPResendView.as_view(), name="otp_resend"),

    #login as user
    path('login/<str:login_user>/', LoginUserView.as_view(), name="login"),

    #admin pannels
    path('admin/seller/<int:seller_id>/status/', ApproveSellerView.as_view(), name='approve_seller'),
    path('admin/delivery-boy/<int:delivery_boy_id>/status/', ApproveDeliveryBoyView.as_view(), name='approve_delivery_boy'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('admin/sellers/', SellerListAPI.as_view(), name='admin-sellers'),
    path('admin/customers/', CustomerListAPI.as_view(), name='admin-customers'),
    path('admin/delivery-boys/', DeliveryBoyListAPI.as_view(), name='admin-delivery-boys'),  
    path('admin-product-dashboard/', AdminProductDashboardAPI.as_view(), name='admin_product_dashboard_api'),
    path('admin/orders/', AdminOrderDashboardAPI.as_view(), name='admin-orders-dashboard'),
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin_login'),

    #getting choices from global choices
    path('choices/deliveryboy/', DeliveryBoyChoicesView.as_view(), name='deliveryboy-choices'),

]
