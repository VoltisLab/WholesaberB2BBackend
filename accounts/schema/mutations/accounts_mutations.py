from datetime import datetime, timedelta

import graphene
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django_graphql_ratelimit import ratelimit
from graphql_jwt.decorators import login_required
from graphql_jwt.refresh_token.models import RefreshToken
from graphql_jwt.utils import jwt_decode

from accounts.models import PhoneVerification, User
from accounts.schema.accounts_responses import (
    OTP_VERIFICATION_SUCCESS,
    PHONE_VERIFICATION_SENT,
    VERIFICATION_CODE_INVALID,
)
from accounts.schema.inputs.accounts_inputs import ProfilePictureInputType
from accounts.schema.types.accounts_type import UserType
from security.inputs.security_inputs import SmsActionChoicesEnum
from utils.security.otp_service import OTPManager


class LogoutMutation(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)
        fcm_token = graphene.String()

    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        refresh_token = kwargs.get("refresh_token")
        fcm_token = kwargs.get("fcm_token")
        User = info.context.user
        request = info.context

        try:
            # Extract the access token from the Authorization header
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header:
                token_type, token = auth_header.split()
                if token_type == "Bearer":
                    # Decode acces token and get it's expiration time
                    payload = jwt_decode(token)
                    exp = payload.get("exp", 0)
                    current_time = datetime.utcnow().timestamp()
                    ttl = exp - current_time

                    # Blacklist access token
                    cache.set(f"blacklisted_token:{token}", True, timeout=ttl)

            if refresh_token:
                refresh_token_obj = RefreshToken.objects.filter(
                    token=refresh_token, user=User
                ).first()
                if refresh_token_obj:
                    refresh_token_obj.delete()
                else:
                    return LogoutMutation(message="Invalid refresh token")

            return LogoutMutation(message="Logout successful")

        except Exception as e:
            return LogoutMutation(message=f"Logout failed: {str(e)}")


class SendPhoneVerificationMutation(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    @ratelimit(key="user", rate="5/m", block=True)
    def mutate(root, info, phone_number):
        import random
        from datetime import timedelta

        from accounts.models import PhoneVerification

        user = info.context.user
        if User.objects.filter(phone_number=phone_number).exists():
            return SendPhoneVerificationMutation(
                success=False, message="Phone number already in use."
            )

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)

        # Deactivate previous verifications
        PhoneVerification.objects.filter(
            user=user, phone_number=phone_number, is_used=False
        ).update(is_used=True)

        # Create new verification
        PhoneVerification.objects.create(
            user=user,
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at,
        )

        OTPManager.send_sms_otp(
            action=SmsActionChoicesEnum.PHONE_VERIFICATION.value,
            phone_number=phone_number,
            otp=otp_code,
        )

        return SendPhoneVerificationMutation(
            success=True, message=PHONE_VERIFICATION_SENT
        )


class VerifyPhoneMutation(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        otp_code = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    @ratelimit(key="user", rate="5/m", block=True)
    def mutate(root, info, phone_number, otp_code):
        user = info.context.user
        try:
            verification = PhoneVerification.objects.get(
                user=user, phone_number=phone_number, otp_code=otp_code, is_used=False
            )

            if verification.is_expired():
                return VerifyPhoneMutation(
                    success=False, message=VERIFICATION_CODE_INVALID
                )

            # # Check attempts limit
            # verification.increment_attempts()
            # if verification.attempts > 3:
            #     verification.is_used = True
            #     verification.save(update_fields=["is_used"])
            #     return VerifyPhoneMutation(
            #         success=False, message=VERIFICATION_CODE_INVALID
            #     )

            # Mark phone as verified
            user.phone_verified = True
            user.phone_number = phone_number
            user.save(update_fields=["phone_verified", "phone_number"])

            # Mark verification as used
            verification.is_used = True
            verification.save(update_fields=["is_used"])

            return VerifyPhoneMutation(success=True, message=OTP_VERIFICATION_SUCCESS)

        except PhoneVerification.DoesNotExist:
            return VerifyPhoneMutation(success=False, message=VERIFICATION_CODE_INVALID)


class Mutation(graphene.ObjectType):
    logout = LogoutMutation.Field()
    send_phone_verification = SendPhoneVerificationMutation.Field()
    verify_phone = VerifyPhoneMutation.Field()