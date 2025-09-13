import graphene

from products.choices import (
    Condition,
    OfferStatus,
    OrderStatusChoices,
    ParcelSizeChoices,
    SellerResponseChoices,
    ShippingServiceProvider,
    StyleChoices,
    ProductFlagReason,
    ProductFlagTypeChoices,
    OrderCancellationReasonChoices,
)


class ConditionEnum(graphene.Enum):
    BRAND_NEW_WITH_TAGS = Condition.BRAND_NEW_WITH_TAGS.value
    BRAND_NEW_WITHOUT_TAGS = Condition.BRAND_NEW_WITHOUT_TAGS.value
    EXCELLENT_CONDITION = Condition.EXCELLENT_CONDITION.value
    GOOD_CONDITION = Condition.GOOD_CONDITION.value
    HEAVILY_USED = Condition.HEAVILY_USED.value


class ParcelSizeEnum(graphene.Enum):
    SMALL = ParcelSizeChoices.SMALL.value
    MEDIUM = ParcelSizeChoices.MEDIUM.value
    LARGE = ParcelSizeChoices.LARGE.value


class StyleEnum(graphene.Enum):
    WORKWEAR = StyleChoices.WORKWEAR.value
    WORKOUT = StyleChoices.WORKOUT.value
    CASUAL = StyleChoices.CASUAL.value
    PARTY_DRESS = StyleChoices.PARTY_DRESS.value
    PARTY_OUTFIT = StyleChoices.PARTY_OUTFIT.value
    FORMAL_WEAR = StyleChoices.FORMAL_WEAR.value
    EVENING_WEAR = StyleChoices.EVENING_WEAR.value
    WEDDING_GUEST = StyleChoices.WEDDING_GUEST.value
    LOUNGEWEAR = StyleChoices.LOUNGEWEAR.value
    VACATION_RESORT_WEAR = StyleChoices.VACATION_RESORT_WEAR.value
    FESTIVAL_WEAR = StyleChoices.FESTIVAL_WEAR.value
    ACTIVEWEAR = StyleChoices.ACTIVEWEAR.value
    NIGHTWEAR = StyleChoices.NIGHTWEAR.value
    VINTAGE = StyleChoices.VINTAGE.value
    Y2K = StyleChoices.Y2K.value
    BOHO = StyleChoices.BOHO.value
    MINIMALIST = StyleChoices.MINIMALIST.value
    GRUNGE = StyleChoices.GRUNGE.value
    CHIC = StyleChoices.CHIC.value
    STREETWEAR = StyleChoices.STREETWEAR.value
    PREPPY = StyleChoices.PREPPY.value
    RETRO = StyleChoices.RETRO.value
    COTTAGECORE = StyleChoices.COTTAGECORE.value
    GLAM = StyleChoices.GLAM.value
    SUMMER_STYLES = StyleChoices.SUMMER_STYLES.value
    WINTER_ESSENTIALS = StyleChoices.WINTER_ESSENTIALS.value
    SPRING_FLORALS = StyleChoices.SPRING_FLORALS.value
    AUTUMN_LAYERS = StyleChoices.AUTUMN_LAYERS.value
    RAINY_DAY_WEAR = StyleChoices.RAINY_DAY_WEAR.value
    DENIM_JEANS = StyleChoices.DENIM_JEANS.value
    DRESSES_GOWNS = StyleChoices.DRESSES_GOWNS.value
    JACKETS_COATS = StyleChoices.JACKETS_COATS.value
    KNITWEAR_SWEATERS = StyleChoices.KNITWEAR_SWEATERS.value
    SKIRTS_SHORTS = StyleChoices.SKIRTS_SHORTS.value
    SUITS_BLAZERS = StyleChoices.SUITS_BLAZERS.value
    TOPS_BLOUSES = StyleChoices.TOPS_BLOUSES.value
    SHOES_FOOTWEAR = StyleChoices.SHOES_FOOTWEAR.value
    TRAVEL_FRIENDLY = StyleChoices.TRAVEL_FRIENDLY.value
    MATERNITY_WEAR = StyleChoices.MATERNITY_WEAR.value
    ATHLEISURE = StyleChoices.ATHLEISURE.value
    ECO_FRIENDLY = StyleChoices.ECO_FRIENDLY.value
    FESTIVAL_READY = StyleChoices.FESTIVAL_READY.value
    DATE_NIGHT = StyleChoices.DATE_NIGHT.value
    ETHNIC_WEAR = StyleChoices.ETHNIC_WEAR.value
    OFFICE_PARTY_OUTFIT = StyleChoices.OFFICE_PARTY_OUTFIT.value
    COCKTAIL_ATTIRE = StyleChoices.COCKTAIL_ATTIRE.value
    PROM_DRESSES = StyleChoices.PROM_DRESSES.value
    MUSIC_CONCERT_WEAR = StyleChoices.MUSIC_CONCERT_WEAR.value
    OVERSIZED = StyleChoices.OVERSIZED.value
    SLIM_FIT = StyleChoices.SLIM_FIT.value
    RELAXED_FIT = StyleChoices.RELAXED_FIT.value
    CHRISTMAS = StyleChoices.CHRISTMAS.value
    SCHOOL_UNIFORMS = StyleChoices.SCHOOL_UNIFORMS.value


class ProductStatusEnum(graphene.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SOLD = "SOLD"


class DeliveryProviderEnum(graphene.Enum):
    DPD = ShippingServiceProvider.DPD.value
    EVRI = ShippingServiceProvider.EVRI.value
    UDEL = ShippingServiceProvider.UDEL.value
    ROYAL_MAIL = ShippingServiceProvider.ROYAL_MAIL.value


class DeliveryTypeEnum(graphene.Enum):
    HOME_DELIVERY = "HOME_DELIVERY"
    LOCAL_PICKUP = "LOCAL_PICKUP"


class ProductGroupingEnum(graphene.Enum):
    BRAND = "BRAND"
    CATEGORY = "CATEGORY"
    TOP_BRAND = "TOP_BRAND"


class OrderStatusEnum(graphene.Enum):
    PENDING = OrderStatusChoices.PENDING.value
    CONFIRMED = OrderStatusChoices.CONFIRMED.value
    SHIPPED = OrderStatusChoices.SHIPPED.value
    DELIVERED = OrderStatusChoices.DELIVERED.value
    COMPLETED = OrderStatusChoices.COMPLETED.value
    CANCELLED = OrderStatusChoices.CANCELLED.value
    RETURNED = OrderStatusChoices.RETURNED.value


class OrderCancellationReasonEnum(graphene.Enum):
    WRONG_ITEM = OrderCancellationReasonChoices.WRONG_ITEM.value
    NOT_AS_DESCRIBED = OrderCancellationReasonChoices.NOT_AS_DESCRIBED.value
    WRONG_SIZE = OrderCancellationReasonChoices.WRONG_SIZE.value
    COUNTERFEIT = OrderCancellationReasonChoices.COUNTERFEIT.value
    CHANGED_MY_MIND = OrderCancellationReasonChoices.CHANGED_MY_MIND.value
    MISTAKE = OrderCancellationReasonChoices.MISTAKE.value


class SellerResponseEnum(graphene.Enum):
    DECLINE_DISPUTE = SellerResponseChoices.DECLINE_DISPUTE.value
    REFUND_ORDER_WITH_RETURN = SellerResponseChoices.REFUND_ORDER_WITH_RETURN.value
    REFUND_ORDER_WITHOUT_RETURN = (
        SellerResponseChoices.REFUND_ORDER_WITHOUT_RETURN.value
    )


class ClientOrderStatusEnum(graphene.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class SortEnum(graphene.Enum):
    NEWEST = "-created_at"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"


class OfferActionEnum(graphene.Enum):
    ACCEPT = OfferStatus.ACCEPTED.value
    REJECT = OfferStatus.REJECTED.value
    COUNTER = OfferStatus.COUNTERED.value


class ParentCategoryEnum(graphene.Enum):
    MEN = "men"
    WOMEN = "women"
    BOYS = "boys"
    GIRLS = "girls"
    TODDLERS = "toddlers"


class ImageActionEnum(graphene.Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE_INDEX = "update_index"


class ProductFlagReasonEnum(graphene.Enum):
    COMMUNITY_GUIDELINES = ProductFlagReason.COMMUNITY_GUIDELINES.value
    INAPPROPRIATE_CONTENT = ProductFlagReason.INAPPROPRIATE_CONTENT.value
    COPYRIGHT_INFRINGEMENT = ProductFlagReason.COPYRIGHT_INFRINGEMENT.value
    DUPLICATE_IMAGES = ProductFlagReason.DUPLICATE_IMAGES.value
    SPAM = ProductFlagReason.SPAM.value
    OTHER = ProductFlagReason.OTHER.value


class ProductFlagTypeEnum(graphene.Enum):
    HIDDEN = ProductFlagTypeChoices.HIDDEN.value
    REMOVED = ProductFlagTypeChoices.REMOVED.value
    FLAGGED = ProductFlagTypeChoices.FLAGGED.value


class DeliveryPayerEnum(graphene.Enum):
    SELLER = "SELLER"
    BUYER = "BUYER"
