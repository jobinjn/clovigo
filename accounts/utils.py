"""
Send OTP for the request phone number with the given otp.
"""
import requests
from clovigo_main.settings import (SMS_API_KEY,
                                    OTP_MAX_TRY)
import random
from accounts.models import OTPVerifyModel
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers


# def send_otp(phone_no: int, otp: int) -> bool:
#     """Send OTP return boolean response."""
#     url = f"https://2factor.in/API/V1/{SMS_API_KEY}/SMS/{phone_no}/{otp}/OTP1"
#     payload = ""
#     headers = {"content-type" : "application/x-www-form-urlencoded"}
#
#     try:
#         response = requests.get(url, data=payload, headers=headers)
#         return bool(response.ok)
#
#     except Exception as e:
#         print(f"When sending OTP caused {e} error")
#         return False


def send_otp(phone_no: int, otp: int) -> bool:
    """Send OTP in terminal and return boolean response."""
    result = True
    print("                             ")
    print("                             ")
    if result:
        print(f"The OTP for the '{phone_no}' is {otp}")
    print("                             ")
    print("                             ")
    return result

def generate_first_otp(phone_no) -> int:
    """Generate OTP and handling OTPVerifyModel."""
    otp = random.randint(100000, 999999)
    otp_sent = send_otp(phone_no, otp)

    if not otp_sent:
        raise serializers.ValidationError({"otp": "Failed to send OTP. Please try again later."})

    return otp

def create_otp_model_first(user, otp) -> None:
    """Create OTPVerifyModel for the user."""
    OTPVerifyModel.objects.create(
        user=user,
        otp = otp,
        otp_expiry = timezone.localtime(timezone.now()) + timedelta(minutes=10),
        otp_max_try = OTP_MAX_TRY - 1
    )
