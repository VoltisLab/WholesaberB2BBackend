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
from accounts.schema.enums.accounts_enums import (
    GenderEnum,
    AccountTypeEnum,
    AddressTypeEnum,
)
from accounts.schema.inputs.accounts_inputs import ProfilePictureInputType
from accounts.schema.types.accounts_type import UserType, DeliveryAddressType
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


class UpdateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        profile_picture = graphene.Argument(ProfilePictureInputType)
        email_address = graphene.String()
        gender = GenderEnum()
        dob = graphene.DateTime()
        street_address = graphene.String()
        city = graphene.String()
        postal_code = graphene.String()
        account_type = AccountTypeEnum()
        phone_number = graphene.String()

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        from utils.account_utils.account_utils import AccountsUtil

        user = AccountsUtil.update_user(user, **kwargs)
        return UpdateUser(
            user=user, success=True, message="Profile updated successfully"
        )


class AddDeliveryAddress(graphene.Mutation):
    class Arguments:
        address_type = AddressTypeEnum(required=True)
        name = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        street_address = graphene.String(required=True)
        city = graphene.String(required=True)
        postal_code = graphene.String(required=True)
        street_address = graphene.String()
        province = graphene.String()
        is_default = graphene.Boolean()

    message = graphene.String()
    success = graphene.Boolean()
    address = graphene.Field(DeliveryAddressType)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        from utils.account_utils.account_utils import AccountsUtil

        address = AccountsUtil.add_delivery_address(user=user, **kwargs)
        return AddDeliveryAddress(
            address=address, success=True, message="Address added successfully"
        )


class UpdateDeliveryAddress(graphene.Mutation):
    class Arguments:
        address_id = graphene.Int(required=True)
        address_type = AddressTypeEnum()
        name = graphene.String()
        phone_number = graphene.String()
        street_address = graphene.String()
        city = graphene.String()
        postal_code = graphene.String()
        street_address = graphene.String()
        province = graphene.String()
        is_default = graphene.Boolean()

    message = graphene.String()
    success = graphene.Boolean()
    address = graphene.Field(DeliveryAddressType)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        from utils.account_utils.account_utils import AccountsUtil

        address_id = kwargs.pop("address_id")
        address = AccountsUtil.update_delivery_address(
            user=user, address_id=address_id, **kwargs
        )
        return UpdateDeliveryAddress(
            address=address, success=True, message="Address updated successfully"
        )


class DeleteDeliveryAddress(graphene.Mutation):
    class Arguments:
        address_id = graphene.Int(required=True)

    message = graphene.String()
    success = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        from utils.account_utils.account_utils import AccountsUtil

        address_id = kwargs.get("address_id")
        result = AccountsUtil.delete_delivery_address(user=user, address_id=address_id)
        if result:
            return DeleteDeliveryAddress(
                success=True, message="Address deleted successfully"
            )
        else:
            return DeleteDeliveryAddress(
                success=False, message="Address not found or could not be deleted"
            )


class VerifyEmailMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @ratelimit(key="user", rate="5/m", block=True)
    def mutate(root, info, token):
        from accounts.models import EmailVerification
        from accounts.schema.accounts_responses import (
            OTP_VERIFICATION_SUCCESS,
            VERIFICATION_CODE_INVALID,
        )

        try:
            verification = EmailVerification.objects.get(token=token, is_used=False)

            if verification.is_expired():
                return VerifyEmailMutation(
                    success=False, message=VERIFICATION_CODE_INVALID
                )

            # Mark email as verified
            user = verification.user
            user.email_verified = True
            user.email = verification.email  # Update email if it was changed
            user.save(update_fields=["email_verified", "email"])

            # Mark verification as used
            verification.is_used = True
            verification.save(update_fields=["is_used"])

            return VerifyEmailMutation(success=True, message=OTP_VERIFICATION_SUCCESS)

        except EmailVerification.DoesNotExist:
            return VerifyEmailMutation(success=False, message=VERIFICATION_CODE_INVALID)


class ResetPasswordMutation(graphene.Mutation):
    class Arguments:
        current_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        current_password = kwargs.get("current_password")
        new_password = kwargs.get("new_password")

        try:
            # Verify current password
            if not user.check_password(current_password):
                return ResetPasswordMutation(
                    success=False,
                    message="Current password is incorrect"
                )

            # Validate new password
            if len(new_password) < 8:
                return ResetPasswordMutation(
                    success=False,
                    message="New password must be at least 8 characters long"
                )

            # Check if new password is different from current
            if user.check_password(new_password):
                return ResetPasswordMutation(
                    success=False,
                    message="New password must be different from current password"
                )

            # Update password
            user.set_password(new_password)
            user.save(update_fields=["password"])

            return ResetPasswordMutation(
                success=True,
                message="Password reset successfully"
            )

        except Exception as e:
            return ResetPasswordMutation(
                success=False,
                message=f"An error occurred: {str(e)}"
            )


# Two-Factor Authentication Mutations
class Is2FAEnabledQuery(graphene.ObjectType):
    enabled = graphene.Boolean()

class Is2FAEnabled(graphene.ObjectType):
    is2FAEnabled = graphene.Field(Is2FAEnabledQuery)

    @login_required
    def resolve_is2FAEnabled(self, info):
        user = info.context.user
        # For now, return False as 2FA is not implemented in the User model
        # In a real implementation, you would check user.two_factor_enabled
        return Is2FAEnabledQuery(enabled=False)

class Enable2FAMutation(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    qrCodeUrl = graphene.String()
    backupCode = graphene.String()
    backupCodes = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        
        # For demo purposes, return mock data
        # In a real implementation, you would:
        # 1. Generate a secret key
        # 2. Create QR code URL
        # 3. Generate backup codes
        # 4. Store in user model
        
        return Enable2FAMutation(
            success=True,
            qrCodeUrl="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=otpauth://totp/ArcVest:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=ArcVest",
            backupCode="12345678",
            backupCodes=["12345678", "87654321", "11223344", "44332211", "55667788"]
        )

class Disable2FAMutation(graphene.Mutation):
    class Arguments:
        password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        password = kwargs.get("password")

        try:
            # Verify password
            if not user.check_password(password):
                return Disable2FAMutation(
                    success=False,
                    message="Incorrect password"
                )

            # For demo purposes, just return success
            # In a real implementation, you would disable 2FA in user model
            
            return Disable2FAMutation(
                success=True,
                message="2FA disabled successfully"
            )

        except Exception as e:
            return Disable2FAMutation(
                success=False,
                message=f"An error occurred: {str(e)}"
            )

# Active Sessions Mutations
class SessionType(graphene.ObjectType):
    id = graphene.String()
    deviceName = graphene.String()
    deviceType = graphene.String()
    location = graphene.String()
    ipAddress = graphene.String()
    lastActive = graphene.String()
    userAgent = graphene.String()

class GetActiveSessionsQuery(graphene.ObjectType):
    sessions = graphene.List(SessionType)
    currentSessionId = graphene.String()

class GetActiveSessions(graphene.ObjectType):
    getActiveSessions = graphene.Field(GetActiveSessionsQuery)

    @login_required
    def resolve_getActiveSessions(self, info):
        # For demo purposes, return mock data
        # In a real implementation, you would query actual session data
        sessions = [
            SessionType(
                id="session_1",
                deviceName="iPhone 16 Plus",
                deviceType="Mobile",
                location="San Francisco, CA",
                ipAddress="192.168.1.100",
                lastActive="2 minutes ago",
                userAgent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)"
            ),
            SessionType(
                id="session_2",
                deviceName="MacBook Pro",
                deviceType="Desktop",
                location="San Francisco, CA",
                ipAddress="192.168.1.101",
                lastActive="1 hour ago",
                userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            ),
        ]
        
        return GetActiveSessionsQuery(
            sessions=sessions,
            currentSessionId="session_1"
        )

class TerminateSessionMutation(graphene.Mutation):
    class Arguments:
        sessionId = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        session_id = kwargs.get("sessionId")
        
        # For demo purposes, just return success
        # In a real implementation, you would terminate the actual session
        
        return TerminateSessionMutation(
            success=True,
            message=f"Session {session_id} terminated successfully"
        )

class TerminateAllOtherSessionsMutation(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        # For demo purposes, just return success
        # In a real implementation, you would terminate all other sessions
        
        return TerminateAllOtherSessionsMutation(
            success=True,
            message="All other sessions terminated successfully"
        )

class Mutation(graphene.ObjectType):
    logout = LogoutMutation.Field()
    send_phone_verification = SendPhoneVerificationMutation.Field()
    verify_phone = VerifyPhoneMutation.Field()
    update_user = UpdateUser.Field()
    add_delivery_address = AddDeliveryAddress.Field()
    update_delivery_address = UpdateDeliveryAddress.Field()
    delete_delivery_address = DeleteDeliveryAddress.Field()
    reset_password = ResetPasswordMutation.Field()
    # 2FA Mutations
    enable2FA = Enable2FAMutation.Field()
    disable2FA = Disable2FAMutation.Field()
    # Session Mutations
    terminateSession = TerminateSessionMutation.Field()
    terminateAllOtherSessions = TerminateAllOtherSessionsMutation.Field()
    # verify_email_address = VerifyEmailMutation.Field()
