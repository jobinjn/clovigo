from django.db import models
from django.contrib.auth.models import AbstractUser
from core.globalchoices import (DISTRICT_CHOICES,
                                STATE_CHOICES,
                                CUSTOMER_RANK_CHOICES,
                                SELLER_RANK_CHOICES,
                                DELIVERYBOY_RANK_CHOICES)
from clovigo_main import settings
from datetime import timedelta, date
from core.filepath import (hash_profile,
                            hash_document,
                            hash_license)

def default_gst_expiry():
    return date.today() + timedelta(days=365)


class UserManagementModel(AbstractUser):
    """Custom created user."""
    profile_pic = models.ImageField(upload_to=hash_profile, null=True, blank=True)
    phone_no = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=False)  
    address_1 = models.TextField(null=True, blank=True)
    address_2 = models.TextField(null=True, blank=True)
    landmark = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True,null=True)
    district = models.CharField(max_length=50, choices=DISTRICT_CHOICES,null=True, blank=True)
    state = models.CharField(max_length=50, choices=STATE_CHOICES, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Ensure username is always saved in lowercase."""
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class CustomerModel(models.Model):
    """Customer extends from UserManagementModel."""
    user = models.ForeignKey(UserManagementModel, on_delete=models.CASCADE, related_name="customer_roles")
    clo_coin = models.PositiveIntegerField(default=0)
    customer_rank = models.CharField(max_length=10, choices=CUSTOMER_RANK_CHOICES, default=CUSTOMER_RANK_CHOICES[0][0])
    is_otp = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer - {self.user.username}"


class SellerModel(models.Model):
    """Seller extends from UserManagementModel."""
    user = models.ForeignKey(UserManagementModel, on_delete=models.CASCADE, related_name="seller_roles")
    is_active = models.BooleanField(default=False)
    is_otp = models.BooleanField(default=False)

    shop_name = models.CharField(max_length=255, blank=True)
    shop_address_1 = models.TextField(null=True, blank=True)
    shop_address_2 = models.TextField(null=True, blank=True)
    shop_landmark = models.TextField(null=True, blank=True)

    GST_no = models.CharField(max_length=50, unique=True)
    GST_expiry_date = models.DateField(default=default_gst_expiry)
    PAN_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    account_no = models.CharField(max_length=50, unique=True, null=True, blank=True)

    file_gst = models.FileField(upload_to=hash_document, null=True, blank=True)
    file_pan = models.FileField(upload_to=hash_document, null=True, blank=True)

    clo_coin = models.PositiveIntegerField(default=0)
    seller_rank = models.CharField(max_length=10, choices=SELLER_RANK_CHOICES, default=SELLER_RANK_CHOICES[0][0])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Seller - {self.user.username}"
    


class DeliveryBoyModel(models.Model):
    """DeliveryBoy extends from UserManagementModel."""
    user = models.ForeignKey(UserManagementModel, on_delete=models.CASCADE, related_name="deliveryboy_roles")
    is_active = models.BooleanField(default=False)
    is_otp = models.BooleanField(default=False)

    license_no = models.CharField(max_length=50, unique=True, blank=True)
    file_license = models.FileField(upload_to=hash_license, null=True, blank=True)

    clo_coin = models.PositiveIntegerField(default=0)
    delivery_boy_rank = models.CharField(max_length=10, choices=DELIVERYBOY_RANK_CHOICES, default=DELIVERYBOY_RANK_CHOICES[0][0])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery Boy - {self.user.username}"


class OTPVerifyModel(models.Model):
    """OTP credentials handler model."""
    otp = models.CharField(max_length=6)
    otp_expiry = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    otp_max_try = models.CharField(max_length=2, default=settings.OTP_MAX_TRY)
    otp_max_out = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(UserManagementModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"OTP model of {self.user.username}"
