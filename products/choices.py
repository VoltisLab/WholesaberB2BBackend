from django.db import models


class ParcelSizeChoices(models.TextChoices):
    SMALL = "SMALL", "Small"
    MEDIUM = "MEDIUM", "Medium"
    LARGE = "LARGE", "Large"


# Condition choices
class Condition(models.TextChoices):
    BRAND_NEW_WITH_TAGS = "Brand New with Tags", "Brand New with Tags"
    BRAND_NEW_WITHOUT_TAGS = "Brand New without Tags", "Brand New without Tags"
    EXCELLENT_CONDITION = "Excellent Condition", "Excellent Condition"
    GOOD_CONDITION = "Good Condition", "Good Condition"
    HEAVILY_USED = "Heavily Used", "Heavily Used"


class OrderStatusChoices(models.TextChoices):
    PENDING = "PENDING", "PENDING"
    CONFIRMED = "CONFIRMED", "CONFIRMED"
    SHIPPED = "SHIPPED", "SHIPPED"
    IN_TRANSIT = "IN_TRANSIT", "In Transit"
    READY_FOR_PICKUP = "READY_FOR_PICKUP", "Ready for Pickup"
    DELIVERED = "DELIVERED", "DELIVERED"
    COMPLETED = "COMPLETED", "COMPLETED"
    CANCELLED = "CANCELLED", "CANCELLED"
    RETURNED = "RETURNED", "RETURNED"


class OrderCancellationReasonChoices(models.TextChoices):
    WRONG_ITEM = "WRONG ITEM", "Wrong Item"
    NOT_AS_DESCRIBED = "NOT AS DESCRIBED", "Item Was Not as Described"
    WRONG_SIZE = "WRONG SIZE", "Wrong Size"
    COUNTERFEIT = "COUNTERFEIT", "Counterfeit"
    CHANGED_MY_MIND = "CHANGED MY MIND", "Changed My Mind"
    MISTAKE = "MISTAKE", "MISTAKE"


class OrderCancellationStatusChoices(models.TextChoices):
    PENDING = "PENDING", "PENDING"
    APPROVED = "APPROVED", "APPROVED"
    PROCESSING_REFUND = "PROCESSING_REFUND", "Processing Refund"
    COMPLETED = "COMPLETED", "COMPLETED"


class SellerResponseChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    DECLINE_DISPUTE = "DECLINE_DISPUTE", "Decline Dispute"
    REFUND_ORDER_WITH_RETURN = (
        "REFUND_ORDER_WITH_RETURN ",
        "Refund the order with return",
    )
    REFUND_ORDER_WITHOUT_RETURN = (
        "REFUND_ORDER_WITHOUT_RETURN",
        "Refund order without return",
    )


class ShippingServiceProvider(models.TextChoices):
    DPD = "DPD", "DPD"
    EVRI = "EVRI", "Evri"
    UDEL = "UDEL", "Udel"
    ROYAL_MAIL = "ROYAL_MAIL", "Royal Mail"


class SizeTypeChoices(models.TextChoices):
    MEN = "MEN", "Men Sizes"
    WOMEN = "WOMEN", "Women Sizes"
    KIDS = "KIDS", "Kids Sizes"  # This include boys and girls
    TODDLERS = "TODDLERS", "Toddlers 2-5 years"
    UNISEX = "UNISEX", "Unisex Sizes"


class SizeSubTypeChoices(models.TextChoices):
    CLOTHING = "CLOTHING", "Clothing"
    SHOES = "SHOES", "Shoes"
    ACCESSORIES = "ACCESSORIES", "Accessories"


class StatusChoices(models.TextChoices):
    ACTIVE = "ACTIVE", "ACTIVE"
    INACTIVE = "INACTIVE", "INACTIVE"
    SOLD = "SOLD", "SOLD"
    FLAGGED = "FLAGGED", "FLAGGED"


class OfferStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    COUNTERED = "COUNTERED", "Counterd"
    EXPIRED = "EXPIRED", "Expired"
    CANCELLED = "CANCELLED", "Cancelled"


class StyleChoices(models.TextChoices):
    WORKWEAR = "Workwear", "Workwear"
    WORKOUT = "Workout", "Workout"
    CASUAL = "Casual", "Casual"
    PARTY_DRESS = "Party Dress", "Party Dress"
    PARTY_OUTFIT = "Party Outfit", "Party Outfit"
    FORMAL_WEAR = "Formal Wear", "Formal Wear"
    EVENING_WEAR = "Evening Wear", "Evening Wear"
    WEDDING_GUEST = "Wedding Guest", "Wedding Guest"
    LOUNGEWEAR = "Loungewear", "Loungewear"
    VACATION_RESORT_WEAR = "Vacation/Resort Wear", "Vacation/Resort Wear"
    FESTIVAL_WEAR = "Festival Wear", "Festival Wear"
    ACTIVEWEAR = "Activewear", "Activewear"
    NIGHTWEAR = "Nightwear", "Nightwear"
    VINTAGE = "Vintage", "Vintage"
    Y2K = "Y2K", "Y2K"
    BOHO = "Boho", "Boho"
    MINIMALIST = "Minimalist", "Minimalist"
    GRUNGE = "Grunge", "Grunge"
    CHIC = "Chic", "Chic"
    STREETWEAR = "Streetwear", "Streetwear"
    PREPPY = "Preppy", "Preppy"
    RETRO = "Retro", "Retro"
    COTTAGECORE = "Cottagecore", "Cottagecore"
    GLAM = "Glam", "Glam"
    SUMMER_STYLES = "Summer Styles", "Summer Styles"
    WINTER_ESSENTIALS = "Winter Essentials", "Winter Essentials"
    SPRING_FLORALS = "Spring Florals", "Spring Florals"
    AUTUMN_LAYERS = "Autumn Layers", "Autumn Layers"
    RAINY_DAY_WEAR = "Rainy Day Wear", "Rainy Day Wear"
    DENIM_JEANS = "Denim & Jeans", "Denim & Jeans"
    DRESSES_GOWNS = "Dresses & Gowns", "Dresses & Gowns"
    JACKETS_COATS = "Jackets & Coats", "Jackets & Coats"
    KNITWEAR_SWEATERS = "Knitwear & Sweaters", "Knitwear & Sweaters"
    SKIRTS_SHORTS = "Skirts & Shorts", "Skirts & Shorts"
    SUITS_BLAZERS = "Suits & Blazers", "Suits & Blazers"
    TOPS_BLOUSES = "Tops & Blouses", "Tops & Blouses"
    SHOES_FOOTWEAR = "Shoes & Footwear", "Shoes & Footwear"
    TRAVEL_FRIENDLY = "Travel-Friendly", "Travel-Friendly"
    MATERNITY_WEAR = "Maternity Wear", "Maternity Wear"
    ATHLEISURE = "Athleisure", "Athleisure"
    ECO_FRIENDLY = "Eco-Friendly/Upcycled", "Eco-Friendly/Upcycled"
    FESTIVAL_READY = "Festival-Ready", "Festival-Ready"
    DATE_NIGHT = "Date Night", "Date Night"
    ETHNIC_WEAR = "Ethnic Wear", "Ethnic Wear"
    OFFICE_PARTY_OUTFIT = "Office Party Outfit", "Office Party Outfit"
    COCKTAIL_ATTIRE = "Cocktail Attire", "Cocktail Attire"
    PROM_DRESSES = "Prom Dresses", "Prom Dresses"
    MUSIC_CONCERT_WEAR = "Music Concert Wear", "Music Concert Wear"
    OVERSIZED = "Oversized", "Oversized"
    SLIM_FIT = "Slim Fit", "Slim Fit"
    RELAXED_FIT = "Relaxed Fit", "Relaxed Fit"
    CHRISTMAS = "Christmas", "Christmas"
    SCHOOL_UNIFORMS = "School Uniforms", "School Uniforms"


class SeasonChoices(models.TextChoices):
    CHRISTMAS = "christmas", "Christmas"
    HALLOWEEN = "halloween", "Halloween"
    SUMMER = "summer", "Summer"
    WINTER = "winter", "Winter"
    SPRING = "spring", "Spring"
    AUTUMN = "autumn", "Autumn"
    BLACK_FRIDAY = "black_friday", "Black Friday"
    EASTER = "easter", "Easter"


class ProductFlagReason(models.TextChoices):
    COMMUNITY_GUIDELINES = "COMMUNITY_GUIDELINES", "Violates Community Guidelines"
    INAPPROPRIATE_CONTENT = "INAPPROPRIATE_CONTENT", "Inappropriate Content"
    COPYRIGHT_INFRINGEMENT = "COPYRIGHT_INFRINGEMENT", "Copyright Infringement"
    DUPLICATE_IMAGES = "DUPLICATE_IMAGES", "Duplicate Images"
    SPAM = "SPAM", "Spam"
    OTHER = "OTHER", "Other"


class ProductFlagStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    REVIEWED = "REVIEWED", "Reviewed"
    RESOLVED = "RESOLVED", "Resolved"


class ProductFlagTypeChoices(models.TextChoices):
    HIDDEN = "HIDDEN", "HIDDEN"
    REMOVED = "REMOVED", "REMOVED"
    FLAGGED = "FLAGGED", "FLAGGED"
