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

from django.core.mail import EmailMultiAlternatives

def send_otp_email(role, email, otp):
    role_display = {
        "seller": "Seller",
        "customer": "Customer",
        "deliveryboy": "Delivery Boy"
    }

    role_name = role_display.get(role.lower(), "User")

    subject = f"{role_name} Password Reset OTP - Clovigo"
    from_email = "clovigo0@gmail.com"
    to = [email]

    text_content = f"""
Hello {role_name},

Your OTP for password reset is: {otp}

This code will expire in 10 minutes.

Thanks,
Team Clovigo
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f6f9fc;
      margin: 0;
      padding: 0;
    }}
    .container {{
      max-width: 600px;
      margin: auto;
      background-color: #ffffff;
      padding: 20px;
      border-radius: 8px;
      border: 1px solid #ddd;
    }}
    .header {{
      background-color: #4a90e2;
      color: white;
      padding: 10px 20px;
      border-radius: 8px 8px 0 0;
      text-align: center;
    }}
    .otp-box {{
      background-color: #f1f1f1;
      padding: 20px;
      margin: 20px 0;
      text-align: center;
      border-radius: 6px;
      font-size: 24px;
      font-weight: bold;
      color: #333;
      letter-spacing: 2px;
    }}
    .footer {{
      font-size: 12px;
      color: #888;
      margin-top: 20px;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Clovigo - Password Reset</h2>
    </div>
    <p>Hi {role_name},</p>
    <p>You recently requested to reset your Clovigo password. Use the OTP below to proceed:</p>
    <div class="otp-box">{otp}</div>
    <p><strong>This OTP is valid for 10 minutes only.</strong></p>
    <p>If you didn't request this, you can safely ignore this email.</p>
    <div class="footer">
      <p>© {role_name} Services | Clovigo Pvt. Ltd.<br>
      Powered by Clovigo Team</p>
    </div>
  </div>
</body>
</html>
"""

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
