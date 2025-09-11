import graphene


class SmsChannelChoicesEnum(graphene.Enum):
    SMS = "generic"
    WHATSAPP = "whatsapp_otp"

class SmsActionChoicesEnum(graphene.Enum):
    VERIFY = "verify"
    LOGIN = "login"
    RESET = "reset"
    TWOFACTOR = "2fa"
    PHONE_VERIFICATION = "phone_verification"