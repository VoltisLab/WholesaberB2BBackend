from django.db import models


class GenderChoice(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", "Prefer not to say"


class AccountType(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Customer"
    VENDOR = "VENDOR", "Vendor"
    SUPPLIER = "SUPPLIER", "Supplier"


class TimeZoneChoice(models.TextChoices):
    UTC = "UTC", "Coordinate Universal Time"
    EST = "EST", "Eastern Standard Time"
    PST = "PST", "Pacific Standard Time"
    CET = "CET", "Central European Time"
    IST = "IST", "Indian Standard Time"


class TimeFormatChoice(models.TextChoices):
    TIME_FORMAT_24_HOUR = "24_HOUR", "24-Hour Format"
    TIME_FORMAT_12_HOUR = "12_HOUR", "12-Hour Format"


class DateFormatChoice(models.TextChoices):
    MM_DD_YYYY = "MM/DD/YYYY", "mm/dd/yyyy"
    DD_MM_YYYY = "DD/MM/YYYY", "dd/mm/yyyy"
