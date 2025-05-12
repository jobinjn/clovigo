"""
Views handling accounts and OTP verifications.
"""
from django.contrib.auth.hashers import make_password

"""eraser-is_otp not added, imagemodel, filemodel"""
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework import status, generics
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
                                  UserProfileSerializer , AdminOrderSerializer, SellerForgotPasswordSerializer)
from accounts.models import (CustomerModel,
                             UserManagementModel,
                             OTPVerifyModel,
                             SellerModel,
                             DeliveryBoyModel)
from django.core.mail import send_mail
from accounts.utils import send_otp
from rest_framework.authentication import SessionAuthentication
from core.serializers import ErrorResponseSerializer
from django.utils import timezone
from django.contrib.auth import authenticate
from clovigo_main.settings import OTP_MAX_TRY
import random
from orders.models import OrderModel
from orders.serializers import OrderSerializer
from accounts.utils import send_otp_email
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
    request=SellerSignUpSerializer,  # Corrected to use SellerSignUpSerializer
    responses={
        201: OpenApiResponse(
            response=SellerSignUpSerializer,
            description="Seller registered. OTP required for verification.",
        )
    },
    tags=["Account Creation"]
)
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
            username = serializer.validated_data["username"]
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
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request, delivery_boy_id):
        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)
        print("Is Staff:", request.user.is_staff)
        print("Is Superuser:", request.user.is_superuser)

        action = request.data.get("action")

        try:
            delivery_boy = DeliveryBoyModel.objects.get(id=delivery_boy_id)
        except DeliveryBoyModel.DoesNotExist:
            return Response({"error": "Delivery boy not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == "activate":
            delivery_boy.is_active = True
            message = "Delivery boy approved (activated) successfully."
        elif action == "deactivate":
            delivery_boy.is_active = False
            message = "Delivery boy deactivated successfully."
        else:
            return Response({"error": "Invalid action. Use 'activate' or 'deactivate'."}, status=status.HTTP_400_BAD_REQUEST)

        delivery_boy.save()
        return Response({"message": message}, status=status.HTTP_200_OK)


class DeliveryBoyChoicesView(APIView):
    def get(self, request):
        district_choices = [{'value': val, 'label': label} for val, label in UserManagementModel._meta.get_field('district').choices]
        state_choices = [{'value': val, 'label': label} for val, label in UserManagementModel._meta.get_field('state').choices]
        rank_choices = [{'value': val, 'label': label} for val, label in DeliveryBoyModel._meta.get_field('delivery_boy_rank').choices]
        return Response({
            'districts': district_choices,
            'states': state_choices,
            'ranks': rank_choices
        })

class ApproveSellerView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request, seller_id):
        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)
        print("Is Staff:", request.user.is_staff)
        print("Is Superuser:", request.user.is_superuser)

        action = request.data.get("action")

        try:
            seller = SellerModel.objects.get(id=seller_id)
        except SellerModel.DoesNotExist:
            return Response({"error": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)

        if action == "activate":
            seller.is_active = True
            message = "Seller approved (activated) successfully."
        elif action == "deactivate":
            seller.is_active = False
            message = "Seller deactivated successfully."
        else:
            return Response({"error": "Invalid action. Use 'activate' or 'deactivate'."}, status=status.HTTP_400_BAD_REQUEST)

        seller.save()
        return Response({"message": message}, status=status.HTTP_200_OK)

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
        try:
            # Attempt to fetch products and reviews with related data
            products = ProductModel.objects.select_related('seller').all()
            reviews = ReviewModel.objects.select_related('product', 'customer').all()

            # If data is fetched correctly, serialize and return the response
            product_data = ProductSerializer(products, many=True).data
            review_data = ReviewSerializer(reviews, many=True).data

            return Response({
                "products": product_data,
                "reviews": review_data
            }, status=status.HTTP_200_OK)

        except ProductModel.DoesNotExist:
            return Response({"error": "No products found."}, status=status.HTTP_404_NOT_FOUND)
        except ReviewModel.DoesNotExist:
            return Response({"error": "No reviews found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Catch any other exceptions and log the error message for debugging
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminLoginAPIView(APIView):
    """
    Class-based view for admin login that returns JWT refresh and access tokens.
    Automatically sets is_staff=True if the user is a superuser.
    """

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None or not user.is_superuser:
            return Response(
                {"error": "Invalid credentials or you are not an admin"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Ensure is_staff is True for superusers
        if not user.is_staff:
            user.is_staff = True
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "message": "Admin login successful",
                "user": user.username,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access),
                }
            },
            status=status.HTTP_200_OK
        )

class AdminOrderDashboardAPI(APIView):
    """admin canfetch the orders in the admin dashboard"""
    def get(self, request):
        orders = OrderModel.objects.all()  # Fetch all orders or you can filter based on some criteria
        order_data = OrderSerializer(orders, many=True).data
        return Response({
            "orders": order_data
        })

class AdminSellerProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return ProductModel.objects.filter(seller_id=seller_id)

class AdminCustomerOrderedProductsView(generics.ListAPIView):
    serializer_class = AdminOrderSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return OrderModel.objects.filter(customer_id=customer_id).order_by('-created_at')

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

class SellerForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = UserManagementModel.objects.get(email=email)
            seller = SellerModel.objects.get(user=user)
        except (UserManagementModel.DoesNotExist, SellerModel.DoesNotExist):
            return Response({"error": "Seller email not found."}, status=404)

        otp = generate_otp()
        request.session["seller_otp"] = otp
        request.session["seller_email"] = email
        send_otp_email("seller", email, otp)

        return Response({"message": "OTP sent to your seller email."})


class CustomerForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = UserManagementModel.objects.get(email=email)
            customer = CustomerModel.objects.get(user=user)
        except (UserManagementModel.DoesNotExist, CustomerModel.DoesNotExist):
            return Response({"error": "Customer email not found."}, status=404)

        otp = generate_otp()
        request.session["customer_otp"] = otp
        request.session["customer_email"] = email
        send_otp_email("customer", email, otp)

        return Response({"message": "OTP sent to your customer email."})


class DeliveryBoyForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = UserManagementModel.objects.get(email=email)
            delivery_boy = DeliveryBoyModel.objects.get(user=user)
        except (UserManagementModel.DoesNotExist, DeliveryBoyModel.DoesNotExist):
            return Response({"error": "Delivery Boy email not found."}, status=404)

        otp = generate_otp()
        request.session["deliveryboy_otp"] = otp
        request.session["deliveryboy_email"] = email
        send_otp_email("deliveryboy", email, otp)

        return Response({"message": "OTP sent to your delivery boy email."})




class SellerVerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        session_otp = request.session.get("seller_otp")

        if otp == session_otp:
            return Response({"message": "OTP verified. You can now reset your password."})
        return Response({"error": "Invalid OTP"}, status=400)


class CustomerVerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        session_otp = request.session.get("customer_otp")

        if otp == session_otp:
            return Response({"message": "OTP verified. You can now reset your password."})
        return Response({"error": "Invalid OTP"}, status=400)


class DeliveryBoyVerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        session_otp = request.session.get("delivery_otp")

        if otp == session_otp:
            return Response({"message": "OTP verified. You can now reset your password."})
        return Response({"error": "Invalid OTP"}, status=400)


class CustomerChangePasswordView(APIView):
    def post(self, request):
        # 1) Get payload
        otp_submitted    = request.data.get("otp")
        password         = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        # 2) Retrieve stored session values
        email = request.session.get("customer_email")
        otp_stored = request.session.get("customer_otp")

        # 3) Basic validations
        if not email or not otp_stored:
            return Response({"error": "No reset request found. Please request a new OTP."}, status=400)

        if otp_submitted != otp_stored:
            return Response({"error": "Invalid OTP."}, status=400)

        if not password or not confirm_password:
            return Response({"error": "Both password fields are required."}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        # 4) Lookup the customer via the related user email
        try:
            user = UserManagementModel.objects.get(email=email)
            customer = CustomerModel.objects.get(user=user)
        except (UserManagementModel.DoesNotExist, CustomerModel.DoesNotExist):
            return Response({"error": "Customer not found."}, status=404)

        # 5) Save the new password
        user.password = make_password(password)
        user.save()

        # 6) Cleanup the session keys
        request.session.pop("customer_email", None)
        request.session.pop("customer_otp", None)

        return Response({"message": "Customer password changed successfully."})


class SellerChangePasswordView(APIView):
    def post(self, request):
        otp_submitted    = request.data.get("otp")
        password         = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        email      = request.session.get("seller_email")
        otp_stored = request.session.get("seller_otp")

        if not email or not otp_stored:
            return Response({"error": "No reset request found. Please request a new OTP."}, status=400)

        if otp_submitted != otp_stored:
            return Response({"error": "Invalid OTP."}, status=400)

        if not password or not confirm_password:
            return Response({"error": "Both password fields are required."}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        try:
            user   = UserManagementModel.objects.get(email=email)
            seller = SellerModel.objects.get(user=user)
        except (UserManagementModel.DoesNotExist, SellerModel.DoesNotExist):
            return Response({"error": "Seller not found."}, status=404)

        user.password = make_password(password)
        user.save()

        request.session.pop("seller_email", None)
        request.session.pop("seller_otp", None)

        return Response({"message": "Seller password changed successfully."})


class DeliveryBoyChangePasswordView(APIView):
    def post(self, request):
        otp_submitted    = request.data.get("otp")
        password         = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        email      = request.session.get("deliveryboy_email")
        otp_stored = request.session.get("deliveryboy_otp")

        if not email or not otp_stored:
            return Response({"error": "No reset request found. Please request a new OTP."}, status=400)

        if otp_submitted != otp_stored:
            return Response({"error": "Invalid OTP."}, status=400)

        if not password or not confirm_password:
            return Response({"error": "Both password fields are required."}, status=400)

        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=400)

        try:
            user         = UserManagementModel.objects.get(email=email)
            delivery_boy = DeliveryBoyModel.objects.get(user=user)
        except (UserManagementModel.DoesNotExist, DeliveryBoyModel.DoesNotExist):
            return Response({"error": "Delivery Boy not found."}, status=404)

        user.password = make_password(password)
        user.save()

        request.session.pop("deliveryboy_email", None)
        request.session.pop("deliveryboy_otp", None)

        return Response({"message": "Delivery Boy password changed successfully."})