"""
Views handling accounts and OTP verifications.
"""

"""eraser-is_otp not added, imagemodel, filemodel"""
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from .serializers import CustomerSerializer, SellerSerializer, DeliveryBoySerializer, UserManagementSerializer
from products.models import ProductModel, ReviewModel
from .serializers import ProductSerializer, ReviewSerializer
from accounts.serializers import (CustomerSignUpSerializer,
                                  OTPValidateSerializer,
                                  OTPResendSerializer,
                                  SellerSignUpSerializer,
                                  DeliveryBoySignUpSerializer,
                                  LoginSerializer,
                                  LoginResponseSerializer,
                                  UserProfileSerializer )
from accounts.models import (CustomerModel,
                             UserManagementModel,
                             OTPVerifyModel,
                             SellerModel,
                             DeliveryBoyModel)
from accounts.utils import send_otp

from core.serializers import ErrorResponseSerializer

from django.utils import timezone
from django.contrib.auth import authenticate

from clovigo_main.settings import OTP_MAX_TRY

import random
from datetime import timedelta

from drf_spectacular.utils import (extend_schema,
                                   OpenApiParameter,
                                   OpenApiExample,
                                   OpenApiResponse)
from .models import UserManagementModel, CustomerModel, SellerModel, DeliveryBoyModel
from .serializers import UserProfileSerializer, CustomerSerializer, SellerSerializer, DeliveryBoySerializer




@extend_schema(
    summary="Register a New Customer",
    description="Creates a new customer account. The account will be inactive until verified.",
    request=CustomerSignUpSerializer,  
    responses={
        201: OpenApiResponse(
            response=CustomerSignUpSerializer,
            description="Customer registered verify OTP.",
        )
    },
    tags=["Account Creation"]
)
class CustomerSignUpView(CreateAPIView):
    """
    Requires username, password, phone number to create a customer account as inactive.
    Use validated password and phonenumber.
    """
    serializer_class = CustomerSignUpSerializer
    queryset = CustomerModel.objects.all()


@extend_schema(
    summary="Register a New Seller",
    description="Creates a new Seller account. The account will be inactive until verified.",
    request=CustomerSignUpSerializer,
    responses={
        201: OpenApiResponse(
            response=SellerSignUpSerializer,
            description="Seller registered verify OTP.",
        )
    },
    tags=["Account Creation"]
)
# class SellerSignUpView(CreateAPIView):
#     """
#     Requires username, password, phone number to create a seller account as inactive.
#     Use validated password and phonenumber.
#     """
#     serializer_class = SellerSignUpSerializer
class SellerSignUpView(CreateAPIView):
    queryset = SellerModel.objects.all()
    serializer_class = SellerSignUpSerializer    


@extend_schema(
    summary="Register a new Delivery Boy",
    description="Creates a new Delivery Boy account. The account will be inactive until verified.",
    request=DeliveryBoySignUpSerializer,
    responses={
        201: OpenApiResponse(
            response=SellerSignUpSerializer,
            description="Delivery Boy registered verify OTP.",
        )
    },
    tags=["Account Creation"]
)
class DeliveryBoySignUpView(CreateAPIView):
    """
    Requires username, password, phone number to create delivery boy account as inactive.
    Use validated password and phonenumber.
    """
    serializer_class = DeliveryBoySignUpSerializer


class OTPValidateView(APIView):
    """
    View for validating OTP for Customer, Seller, and Delivery Boy.
    Requires Username and OTP.
    """

    @extend_schema(
        summary="Verify OTP",
        description="Verify OTP and activate user for all roles they belong to.",
        request=OTPValidateSerializer,
        responses={
            201: OpenApiResponse(
                response=OTPValidateSerializer,
                description="OTP verified.",
            )
        },
        tags=["OTP Management"]
    )
    def post(self, request):
        """Verify OTP and activate user for all roles they belong to."""
        serializer = OTPValidateSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data["username"]
            is_seller = serializer.validated_data["is_seller"]
            is_delivery_boy = serializer.validated_data["is_delivery_boy"]

            user = UserManagementModel.objects.get(username=username)
            user.is_active = True
            user.save()

            OTPVerifyModel.objects.filter(user=user).delete()

            if is_seller and SellerModel.objects.filter(user=user).exists():
                seller = SellerModel.objects.get(user = user)
                seller.is_otp = True

                seller.save()
                return Response(
                    {"message": "OTP matched. Seller OTP verified successfully!"},
                    status=status.HTTP_200_OK
                )

            if is_delivery_boy and DeliveryBoyModel.objects.filter(user=user).exists():
                delivery_boy = DeliveryBoyModel.objects.get(user = user)
                delivery_boy.is_otp = True
                delivery_boy.save()
                return Response(
                    {"message": "OTP matched. Delivery boy OTP verified successfully!"},
                    status=status.HTTP_200_OK
                )

            if CustomerModel.objects.filter(user=user).exists():
                customer = CustomerModel.objects.get(user = user)
                customer.is_otp = True
                customer.is_active = True
                customer.save()
                return Response(
                    {"message": "OTP matched. Customer is verified and activated successfully!"},
                    status=status.HTTP_200_OK
                )
                
            return Response(
                {"message": "OTP matched. User created but Account not activated."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OTPResendView(APIView):
    """
    View for OTP resend request for Customer, Seller, and Delivery Boy.
    Username is required.
    """

    @extend_schema(
        summary="Resend OTP",
        description="Resend OTP if applicable.",
        request=OTPResendSerializer,
        responses={
            201: OpenApiResponse(
                response=OTPResendSerializer,
                description="OTP resend successfully.",
            )
        },
        tags=["OTP Management"]
    )
    def post(self, request):
        """Resend OTP if applicable."""
        serializer = OTPResendSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            otp_entry, created = OTPVerifyModel.objects.get_or_create(
                user=user,
                defaults={
                    "otp": random.randint(100000, 999999),
                    "otp_expiry": timezone.localtime(timezone.now()) + timedelta(minutes=10)
                }
            )

            if otp_entry.otp_max_out is not None:
                if otp_entry.otp_max_out < timezone.localtime(timezone.now()) and int(otp_entry.otp_max_try) <= 0:
                        otp_entry.otp_max_try = OTP_MAX_TRY

            otp_entry.otp = random.randint(100000, 999999)
            otp_entry.otp_expiry = timezone.localtime(timezone.now()) + timedelta(minutes=10)
            otp_entry.otp_max_try = int(otp_entry.otp_max_try) - 1

            if int(otp_entry.otp_max_try) <= 0:
                otp_entry.otp_max_out = timezone.localtime(timezone.now()) + timedelta(hours=1)

            otp_entry.save()
            otp_sent = send_otp(user.phone_no, otp_entry.otp)

            if not otp_sent:
                return Response({"message": "Failed to send OTP. Please try again later."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "OTP resent successfully!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class LoginUserView(APIView):
    """
    Login any user.
    login_user -> customer, seller or deliveryboy
    username and password is required.
    """

    @extend_schema(
        summary="Login User (Customer, Seller, Delivery Boy)",
        description="Authenticate a user based on role (`customer`, `seller`, or `deliveryboy`). Returns JWT tokens if successful.",
        parameters=[
            OpenApiParameter(
                name="login_user",
                type=str,
                location=OpenApiParameter.PATH,
                description="Specify the user role: `customer`, `seller`, or `deliveryboy`",
                required=True,
                enum=["customer", "seller", "deliveryboy"],
                examples=[
                    OpenApiExample("Login Customer", value="customer"),
                    OpenApiExample("Login Seller", value="seller"),
                    OpenApiExample("Login Delivery Boy", value="deliveryboy"),
                ],
                exclude = False
            )
        ],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Successful Response",
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request - Invalid Credentials",
                examples=[
                    OpenApiExample(
                        "Invalid Credentials",
                        value={"Invalid Credentials": "Invalid Username or Password."}
                    ),
                ],
            ),         
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden - Inactive Account",
                examples=[
                    OpenApiExample(
                        "Inactive Account",
                        value={"Inactive Account": "Account is inactive."}
                    ),
                ],
            ),         
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not found - Account Not Found",
                examples=[
                    OpenApiExample(
                        "Account Not Found",
                        value={"Account Not Found": "Customer/Seller/DeliveryBoy account not found."}
                    ),
                ],
            ),         
        },
        tags=["Authentication"]
    )
    def post(self, request, login_user):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data["username"].lower()
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)

            if not user:
                return Response({"Invalid Credentials": "Invalid Username or Password."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({"Inactive Account": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)

            # Validate user role
            if login_user == "customer":
                if not CustomerModel.objects.filter(user=user).exists():
                    return Response({"Account Not Found": "Customer/Seller/DeliveryBoy account not found."}, status=status.HTTP_404_NOT_FOUND)
                
                customer = CustomerModel.objects.get(user=user)
                if not customer.is_active:
                    return Response({"Inactive Account": "Customer account not activated."}, status=status.HTTP_403_FORBIDDEN)

            elif login_user == "seller":
                if not SellerModel.objects.filter(user=user).exists():
                    return Response({"Account Not Found": "Seller account not found."}, status=status.HTTP_404_NOT_FOUND)

                seller = SellerModel.objects.get(user=user)
                if not seller.is_active:
                    return Response({"Inactive Account": "Seller account not activated."}, status=status.HTTP_403_FORBIDDEN)

            elif login_user == "deliveryboy":
                if not DeliveryBoyModel.objects.filter(user=user).exists():
                    return Response({"Account Not Found": "Delivery Boy account not found."}, status=status.HTTP_404_NOT_FOUND)

                deliveryboy = DeliveryBoyModel.objects.get(user=user)
                if not deliveryboy.is_active:
                    return Response({"Inactive Account": "Delivery Boy account not activated."}, status=status.HTTP_403_FORBIDDEN)

            else:
                return Response({"Invalid Credentials": "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate JWT Tokens
            tokens = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(tokens),
                    "access": str(tokens.access_token),
                    "user_id": user.id,
                    "username": user.username
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveDeliveryBoyView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, delivery_boy_id):
        try:
            delivery_boy = DeliveryBoyModel.objects.get(id=delivery_boy_id)
            delivery_boy.is_active = True
            delivery_boy.save()
            return Response({"message": "Delivery boy approved (activated) successfully."}, status=status.HTTP_200_OK)
        except DeliveryBoyModel.DoesNotExist:
            return Response({"error": "Delivery boy not found."}, status=status.HTTP_404_NOT_FOUND)

class ApproveSellerView(APIView):
    permission_classes = [IsAdminUser]  

    def post(self, request, seller_id):
        try:
            seller = SellerModel.objects.get(id=seller_id)
            seller.is_active = True
            seller.save()
            return Response({"message": "Seller approved (activated) successfully."}, status=status.HTTP_200_OK)
        except SellerModel.DoesNotExist:
            return Response({"error": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)   


# class UserProfileView(RetrieveUpdateAPIView):
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def get(self, request, *args, **kwargs):
#         user = request.user
#         base_data = UserProfileSerializer(user).data

#         # Check and attach role-specific profile
#         if hasattr(user, 'sellermodel'):
#             role_data = SellerSerializer(user.sellermodel).data
#             role = 'seller'
#         elif hasattr(user, 'customermodel'):
#             role_data = CustomerSerializer(user.customermodel).data
#             role = 'customer'
#         elif hasattr(user, 'deliveryboymodel'):
#             role_data = DeliveryBoySerializer(user.deliveryboymodel).data
#             role = 'delivery_boy'
#         else:
#             role_data = {}
#             role = 'general_user'

#         return Response({
#             "user": base_data,
#             "role": role,
#             "profile": role_data
#         })

#     def get_object(self):

#         return self.request.user


class UserProfileView(RetrieveUpdateAPIView):
    """
    A view to retrieve and update the user's profile.
    Returns a response with user role, user data, and profile information.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        # Returning the current authenticated user
        return self.request.user

    def get(self, request, *args, **kwargs):
        """
        Retrieves the user profile along with role and additional profile data
        (seller, customer, delivery boy, etc.) based on the user's role.
        """
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Updates the user profile. Only fields in the serializer can be updated.
        """
        return super().update(request, *args, **kwargs)
    
class SellerListAPI(APIView):
    def get(self, request):
        sellers = SellerModel.objects.select_related('user').all()
        return Response({
            "sellers": SellerSerializer(sellers, many=True).data
        })


class CustomerListAPI(APIView):
    def get(self, request):
        customers = CustomerModel.objects.select_related('user').all()
        return Response({
            "customers": CustomerSerializer(customers, many=True).data
        })


class DeliveryBoyListAPI(APIView):
    def get(self, request):
        delivery_boys = DeliveryBoyModel.objects.select_related('user').all()
        return Response({
            "delivery_boys": DeliveryBoySerializer(delivery_boys, many=True).data
        })
    
class AdminProductDashboardAPI(APIView):
    def get(self, request):
        products = ProductModel.objects.select_related('seller').all()
        reviews = ReviewModel.objects.select_related('product', 'customer').all()
        
        return Response({
            "products": ProductSerializer(products, many=True).data,
            "reviews": ReviewSerializer(reviews, many=True).data,
        })
    
class AdminLoginAPIView(APIView):
    """Class-based view for admin login without token authentication."""

    def post(self, request, *args, **kwargs):
        """Handle POST request for admin login."""
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if username and password are provided
        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate the user (without token-based auth)
        user = authenticate(username=username, password=password)

        # Check if user exists and if they are an admin (is_staff=True)
        if user is not None and user.is_superuser:
            return Response(
                {
                    "message": "Admin login successful",
                    "user": user.username
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid credentials or you are not an admin"},
                status=status.HTTP_401_UNAUTHORIZED
            )    