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
                            AdminProductDashboardAPI
                            )
from accounts.views import AdminLoginAPIView


app_name = "accounts"

urlpatterns = [
    path('signup/customer/', CustomerSignUpView.as_view(), name="customer_signup"),     
    path('signup/seller/', SellerSignUpView.as_view(), name="seller_signup"),
    path('signup/deliveryboy/', DeliveryBoySignUpView.as_view(), name="deliveryboy_signup"),
    path('user/otp/validate/', OTPValidateView.as_view(), name="otp_validate"),  # http://127.0.0.1:8000/api/accounts/user/otp/validate/
    path('user/otp/resend/', OTPResendView.as_view(), name="otp_resend"),       #  http://127.0.0.1:8000/api/accounts/user/otp/resend/
    path('login/<str:login_user>/', LoginUserView.as_view(), name="login"),
    path('admin/approve-seller/<int:seller_id>/', ApproveSellerView.as_view(), name='approve-seller'),
    path('admin/approve-delivery-boy/<int:delivery_boy_id>/', ApproveDeliveryBoyView.as_view(), name='approve-delivery-boy'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('admin/sellers/', SellerListAPI.as_view(), name='admin-sellers'),
    path('admin/customers/', CustomerListAPI.as_view(), name='admin-customers'),
    path('admin/delivery-boys/', DeliveryBoyListAPI.as_view(), name='admin-delivery-boys'),  
    path('admin-product-dashboard/', AdminProductDashboardAPI.as_view(), name='admin_product_dashboard_api'),
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin_login'),


]
