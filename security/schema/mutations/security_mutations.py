import graphene
from graphql_jwt.decorators import login_required
import base64
from io import BytesIO

from utils.security.otp_service import OTPManager
from security.inputs.security_inputs import SmsChannelChoicesEnum, SmsActionChoicesEnum


class SendSmsOtp(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        channel = SmsChannelChoicesEnum()
        phone_number = graphene.String(
            description="If the user does not have a phone number on file, this field allows them to provide a new phone number for verification. In this case, an OTP will be sent to the provided phone number, and the user will be prompted to enter the OTP to complete verification. If the user already has a phone number, leave this field empty to send an OTP to the existing phone number. The OTP can then be used to verify and update to a new number."
        )
        action = SmsActionChoicesEnum(
            description="Specifies the purpose of the OTP. The action determines the context for the OTP message, such as verifying an account, logging in, resetting a password, or two-factor authentication (2FA). The OTP message content will change based on the selected action."
        )

    @login_required
    def mutate(self, info, **kwargs):
        channel = kwargs.get("channel", SmsChannelChoicesEnum.SMS.value)
        action = kwargs.get("action", SmsActionChoicesEnum.VERIFY.value)
        phone_number = kwargs.get("phone_number", None)
        user = info.context.user

        if hasattr(channel, "value"):  
            channel = channel.value
    
        if hasattr(action, "value"):   
            action = action.value

        response = OTPManager.send_sms_otp(
            user=user,
            action=action,
            phone_number=phone_number,
            channel=channel,
        )
        if not response:
            return SendSmsOtp(success=response, message="error sending otp")
        return SendSmsOtp(success=response, message="OTP sent successfully")



class Mutation(graphene.ObjectType):
    ...

