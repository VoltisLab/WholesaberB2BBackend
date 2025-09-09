from django.db import models


class GenderChoice(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    ANY = "ANY", "Any"


class AccountType(models.TextChoices):
    customer = "CUSTOMER", "Customer"
    vendor = "VENDOR", "Vendor"


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
