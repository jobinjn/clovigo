from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

from accounts.models import (UserManagementModel,
                             CustomerModel,
                             OTPVerifyModel,
                             SellerModel,
                             DeliveryBoyModel)
from accounts.models import SellerModel, CustomerModel
from products.models import ProductModel, ReviewModel
from accounts.utils import (send_otp,
                            generate_first_otp,
                            create_otp_model_first)
from orders.models import OrderModel
from accounts.models import UserManagementModel
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class UserManagementSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, error_messages={
        "required": "Email is required.",
        "invalid": "Enter a valid email address."
    })

    phone_no = serializers.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[6-9]\d{9}$',
                message="Enter a valid 10-digit Indian phone number."
            )
        ],
        error_messages={"required": "Phone number is required."}
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            "required": "Password is required.",
            "min_length": "Password must be at least 8 characters."
        }
    )

    first_name = serializers.CharField(required=True, error_messages={"required": "First name is required."})
    last_name = serializers.CharField(required=True, error_messages={"required": "Last name is required."})
    username = serializers.CharField(required=True, error_messages={"required": "Username is required."})

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "phone_no", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_no=validated_data["phone_no"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=False
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

# class UserManagementSignUpSerializer(serializers.ModelSerializer):
#     """Create Custom User."""

#     class Meta:
#         model = User
#         fields = ["phone_no", "username", "password"]
#         extra_kwargs = {"password": {"write_only": True, 'min_length': 5}}

#     def create(self, validated_data): 
#         """
#         Create and return a new UserManagementModel instance
#         or return the existing user if already created.
#         """
        
#         user = User.objects.create(
#             phone_no=validated_data["phone_no"],
#             username=validated_data["username"]
#         )
#         user.set_password(validated_data["password"])
#         user.save()
#         return user


class CustomerSignUpSerializer(serializers.ModelSerializer):
    """Create send OTP and create new customer."""
    user = UserManagementSignUpSerializer()

    class Meta:
        model = CustomerModel
        fields = ["user"]

    def create(self, validated_data):
        """Send OTP and create CustomerModel."""
        user_data = validated_data.pop("user")
        # Need to add this to verify if the user already exists or registered with this phone_no
        customer = CustomerModel.objects.filter(user__phone_no=user_data["phone_no"]).first()

        # if customer:
        #      if not customer.user.is_active:
        #          raise serializers.ValidationError("User with this mobile number exists but is not verified. Please verify OTP.")
        #      raise serializers.ValidationError("User with this mobile number already exists. Please try logging in.")
            
        otp = generate_first_otp(user_data["phone_no"])
        user = UserManagementSignUpSerializer().create(user_data)
        create_otp_model_first(user, otp)
        customer = CustomerModel.objects.create(user=user, **validated_data)
        return  customer



class SellerSignUpSerializer(serializers.ModelSerializer):
    """Serialize data required for Seller signup"""
    user = UserManagementSignUpSerializer()

    class Meta:
        model = SellerModel
        exclude = ["is_active", "is_otp", "clo_coin", "seller_rank", "created_at", "updated_at"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        otp = generate_first_otp(user_data["phone_no"])  # send OTP
        user = UserManagementSignUpSerializer().create(user_data)
        create_otp_model_first(user, otp)  # store OTP in db
        seller = SellerModel.objects.create(user=user, **validated_data)
        return seller


class DeliveryBoySignUpSerializer(serializers.ModelSerializer):
    """Serialize data required for Delivery Boy signup"""
    user = UserManagementSignUpSerializer()

    class Meta:
        model = DeliveryBoyModel
        fields = ["license_no", "file_license", "user"]

    def create(self, validated_data):
        """Send OTP and create DeliveryBoyModel."""
        user_data = validated_data.pop("user")
        otp = generate_first_otp(user_data["phone_no"])
        user = UserManagementSignUpSerializer().create(user_data)
        create_otp_model_first(user, otp)
        deliveryboy = DeliveryBoyModel.objects.create(user=user, **validated_data)
        return deliveryboy


class OTPValidateSerializer(serializers.Serializer):
    """Validate OTP requests."""
    otp = serializers.CharField(max_length=6)
    username = serializers.CharField(max_length=150)
    is_seller = serializers.BooleanField(default=False)
    is_delivery_boy = serializers.BooleanField(default=False)

    def validate(self, data):
        """Validates OTP."""
        otp = data.get("otp")
        username = data.get("username")

        try:
            otp_entry = OTPVerifyModel.objects.get(user__username=username)
        except OTPVerifyModel.DoesNotExist:
            raise serializers.ValidationError({"otp": "Invalid username name."})

        if otp_entry.otp_expiry < timezone.localtime(timezone.now()):
            raise serializers.ValidationError({"otp": "OTP has expired. Please request a new one."})

        if otp_entry.otp != str(otp):
            raise serializers.ValidationError({"otp": "OTP does not match."})

        return data


class OTPResendSerializer(serializers.Serializer):
    """Verify OTP resend."""
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        """Validates if OTP can be resent."""
        username = data.get("username")

        try:
            user = User.objects.get(username=username)
                
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "User does not exist."})

        try:
            otp = OTPVerifyModel.objects.get(user=user)
                
        except OTPVerifyModel.DoesNotExist:
            otp = None

        if otp is not None:
            if otp.otp_max_out and otp.otp_max_out > timezone.localtime(timezone.now()):
                raise serializers.ValidationError({"otp": f"Maximum OTP request limit reached. Try again later."})

            if otp.otp_expiry > timezone.localtime(timezone.now()):
                raise serializers.ValidationError({"otp": f"Already requested OTP! Try after 10 minutes."})

        return {"user": user}


class LoginSerializer(serializers.Serializer):
    """Base Login Serializer for all user roles."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Login response visualise for Swagger UI."""
    refresh = serializers.CharField()
    access = serializers.CharField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()

# --- User Profile Serializer ---
class UserProfileSerializer(serializers.ModelSerializer):
    seller_profile = serializers.SerializerMethodField()
    customer_profile = serializers.SerializerMethodField()
    delivery_boy_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'seller_profile', 'customer_profile', 'delivery_boy_profile']

    def get_seller_profile(self, user):
        try:
            seller = SellerModel.objects.get(user=user)
            return SellerSerializer(seller).data
        except SellerModel.DoesNotExist:
            return None

    def get_customer_profile(self, user):
        try:
            customer = CustomerModel.objects.get(user=user)
            return CustomerSerializer(customer).data
        except CustomerModel.DoesNotExist:
            return None

    def get_delivery_boy_profile(self, user):
        try:
            delivery_boy = DeliveryBoyModel.objects.get(user=user)
            return DeliveryBoySerializer(delivery_boy).data
        except DeliveryBoyModel.DoesNotExist:
            return None

    
class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManagementModel
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    user = UserManagementSerializer()

    class Meta:
        model = CustomerModel
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    user = UserManagementSerializer()

    class Meta:
        model = SellerModel
        fields = '__all__'

class DeliveryBoySerializer(serializers.ModelSerializer):
    user = UserManagementSerializer()

    class Meta:
        model = DeliveryBoyModel
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    calculated_discount_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductModel
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
        
class ReviewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    customer_name = serializers.CharField(source='customer.user.username', read_only=True)

    class Meta:
        model = ReviewModel
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.user.first_name', read_only=True)
    product_details = serializers.CharField(source='product', read_only=True)

    class Meta:
        model = OrderModel
        fields = ['id', 'customer_name', 'product_details', 'quantity', 'order_status', 'total_price', 'created_at',
                  'updated_at']