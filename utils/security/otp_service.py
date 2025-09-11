from django.conf import settings
from django.core.mail import send_mail
import re
import random
import string
import requests


from django.utils import timezone
from accounts.models import Verification
from accounts.models import User
from security.models import SMS2FA
from django.template.loader import render_to_string
from decouple import config

from abc import ABC, abstractmethod

SMS_SUCCESS_MESSAGE = "Successfully Sent"

class BaseOTPService(ABC):
    """
    Abstract base class for OTP services.
    All OTP service classes should inherit from this.
    """

    @abstractmethod
    def send_otp(self, to_number: str, otp: str, action: str, channel: str = "generic"):
        """
        Send an OTP.
        Must be implemented by subclasses.
        """
        pass

    @staticmethod
    def get_otp_message(otp: str, action: str) -> str:
        pass
        
class TermiiOTPService(BaseOTPService):
    TERMII_API_KEY=config("TERMII_API_KEY")
    TERMII_SMS_URL=config("TERMII_SMS_URL")   
    TERMII_SENDER_ID=config("TERMII_SENDER_ID").split(",")

    def send_otp(self, to_number: str, otp: str, action: str, channel: str = "generic"):
        message = OTPManager.get_otp_message(otp, action)
        payload = {
            "api_key": self.TERMII_API_KEY,
            "to": to_number,
            "from": self.TERMII_SENDER_ID[0],
            "channel": channel,
            "type": "plain",
            "sms": message if channel == "generic" else otp,
        }
        try:
            response = requests.post(self.TERMII_SMS_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


class OTPManager:
    """
    A service class for sending OTPs via WhatsApp and SMS using the Termii API.

    This class provides methods to send OTPs with a fallback mechanism from WhatsApp to SMS,
    as well as methods to verify OTPs.

    Attributes:
        api_key (str): The API key for Termii.
        sender_id (str): The sender ID for messages.
    """

    @staticmethod
    def send_sms_otp(
        action: str, phone_number: str, channel: str = "generic",
        user=None,
        otp=None,
        service=None
    ) -> bool:
        """
        Attempt to send an OTP via the provided channel (e.g., WhatsApp, SMS), following a prioritized fallback mechanism for phone numbers.

        The OTP is first sent to the user's 2FA phone number (if SMS 2FA is enabled). If not available, the user's registered phone number is used.
        As a last resort, if neither are available, the OTP is sent to the provided phone number.

        Args:
            user (User): The user object.
            action (str): The action associated with the OTP (e.g., "verify", "login", "reset").
            channel (str): The channel to use for sending the OTP (e.g., SMS, WhatsApp).
            phone_number (str, optional): The fallback phone number to send the OTP to, if the user doesn't have a registered or 2FA-enabled number.

        Returns:
            bool: True if the OTP was successfully sent, False otherwise.
        """

        if otp is None:
            otp = OTPManager.generate_user_otp(user)

        # Regex to validate the phone number
        phone_number = str(phone_number)
        if not re.match(r"^\+?\d{9,15}$", phone_number):
            return False
        
        if service is None:
            service = TermiiOTPService()
        elif isinstance(service, type):
            service = service()
        
        sms_response = service.send_otp(phone_number, otp, action, channel)
        if OTPManager._is_successful(sms_response):
            return True
        return False
    
    
    @staticmethod
    def get_otp_message(otp: str, action: str = "verify"):
        """
        Generate an OTP message based on the specified action.

        Args:
            otp (str): The One-Time Password to include in the message.
            action (str, optional): The action associated with the OTP. Defaults to "verify".

        Returns:
            str: The formatted OTP message.
        """
        messages = {
            "verify": f"Your Wholesaler's account verification code is {otp}. This code will expire in 5 minutes.",
            "login": f"{otp} is your Wholesaler's login code. Valid for 5 minutes. Do not share this code with others.",
            "register": f"Welcome to Wholesaler! Your account verification code is {otp}. This code will expire in 5 minutes.",
            "reset": f"Wholesaler password reset code: {otp}. If you didn't request this, please ignore. Code expires in 5 minutes.",
            "2fa": f"Wholesaler 2FA code: {otp}. Use this to complete your login. Expires in 5 minutes. Don't share this code.",
            "phone_verification": f"Your Wholesaler's phone verification code is {otp}. It will expire in 5 minutes."
        }
        return messages.get(action, messages["verify"])

    
    @staticmethod
    def _is_successful(response):
        """
        Check if message was sent successfully.
        Returns:
            bool: True if successful, False otherwise.
        """
        return response.get("message") == SMS_SUCCESS_MESSAGE


    @staticmethod
    def send_email_otp(user, subject, template_path, context):
        """
        Sends an OTP email using the specified template and context.

        Args:
            user (User): The user object.
            subject (str): The subject of the email.
            template_path (str): The path to the HTML template.
            context (dict): The context to render in the template.

        Returns:
            None
        """

        code = OTPManager.generate_user_otp(user)

        with open(template_path, "r") as file:
            body = file.read()

        context.update(
            {
                "otp": code,
                "user": user,
                "current_year": timezone.now().year,
            }
        )

        # Render the HTML template with the context
        html_body = render_to_string(template_path, context)

        # Send the email
        send_mail(
            subject,
            message="body",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_body,
        )

    @staticmethod
    def generate_user_otp(user):
        code = OTPManager.random_code_generator()

        # Delete any existing verification codes for this user
        if verification := Verification.objects.filter(user=user).first():
            verification.delete()

        # Create a new verification record
        Verification.objects.create(user=user, code=code)

        return code

    @staticmethod
    def random_code_generator(size=6, chars=string.digits):
        return "".join(random.choice(chars) for _ in range(size))

