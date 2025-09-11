from django.core.management.base import BaseCommand
from products.choices import SizeSubTypeChoices, SizeTypeChoices
from products.models import Size


class Command(BaseCommand):
    help = "Add size values to the database"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Adding sizes to the database..."))
        sizes = {
            "men clothing": [
                "XXS",
                "XS",
                "S",
                "M",
                "L",
                "XL",
                "2XL",
                "3XL",
                "4XL",
                "5XL",
                "6XL",
                "7XL",
                "ONE SIZE",
            ],
            "men shoes": [
                "UK 5",
                "UK 5.5",
                "UK 6",
                "UK 6.5",
                "UK 7",
                "UK 7.5",
                "UK 8",
                "UK 8.5",
                "UK 9",
                "UK 9.5",
                "UK 10",
                "UK 10.5",
                "UK 11",
                "UK 11.5",
                "UK 12",
                "UK 12.5",
                "UK 13",
                "UK 13.5",
                "UK 14",
                "ONE SIZE",
            ],
            "women clothing": [
                "UK 4",
                "UK 6",
                "UK 8",
                "UK 10",
                "UK 12",
                "UK 14",
                "UK 16",
                "UK 18",
                "UK 20",
                "ONE SIZE",
            ],
            "women shoes": [
                "UK 2",
                "UK 2.5",
                "UK 3",
                "UK 3.5",
                "UK 4",
                "UK 4.5",
                "UK 5",
                "UK 5.5",
                "UK 6",
                "UK 6.5",
                "UK 7",
                "UK 7.5",
                "UK 8",
                "UK 8.5",
                "UK 9",
                "ONE SIZE",
            ],
            "kids clothing": [
                "Preemie, up to 44cm",
                "Newborns / 44cm",
                "Up to 1 month / 50cm",
                "1-3 months / 56cm",
                "3-6 months / 62cm",
                "6-9 months / 68cm",
                "9-12 months / 74cm",
                "12-18 months / 80cm",
                "18-24 months / 86cm",
                "24-36 months / 92cm",
                "3 years / 98cm",
                "4 years / 104cm",
                "5 years / 110cm",
                "6 years / 116cm",
                "7 years / 122cm",
                "8 years / 128cm",
                "9 years / 134cm",
                "10 years / 140cm",
                "11 years / 146cm",
                "12 years / 152cm",
                "13 years / 158cm",
                "14 years / 164cm",
                "15 years / 170cm",
                "16 years / 176cm",
                "ONE SIZE",
                "XS",
                "S",
                "M",
                "L",
                "XL",
                "2XL",
            ],
            "kids shoes": [
                "15",
                "16",
                "17",
                "18",
                "19",
                "20",
                "21",
                "22",
                "23",
                "24",
                "25",
                "26",
                "27",
                "28",
                "29",
                "30",
                "31",
                "32",
                "33",
                "34",
                "35",
                "36",
                "37",
                "38",
                "39",
                "40",
            ],
            "unisex accessories": [
                "S",
                "M",
                "L",
                "XL",
                "ONE SIZE",
            ],
        }

        size_type_mapping = {
            "men clothing": (SizeTypeChoices.MEN, SizeSubTypeChoices.CLOTHING),
            "women clothing": (SizeTypeChoices.WOMEN, SizeSubTypeChoices.CLOTHING),
            "men shoes": (SizeTypeChoices.MEN, SizeSubTypeChoices.SHOES),
            "women shoes": (SizeTypeChoices.WOMEN, SizeSubTypeChoices.SHOES),
            "kids clothing": (SizeTypeChoices.KIDS, SizeSubTypeChoices.CLOTHING),
            "kids shoes": (SizeTypeChoices.KIDS, SizeSubTypeChoices.SHOES),
            "unisex accessories": (
                SizeTypeChoices.UNISEX,
                SizeSubTypeChoices.ACCESSORIES,
            ),
        }

        for size_type_key, size_list in sizes.items():
            size_type, size_subtype = size_type_mapping.get(size_type_key)

            for size in size_list:
                size_obj, created = Size.objects.get_or_create(
                    name=size,
                    size_type=size_type,
                    size_subtype=size_subtype,
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Size "{size}" added under size type "{size_type_key}".'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Size "{size}" already exists under size type "{size_type_key}".'
                        )
                    )

        self.stdout.write(self.style.SUCCESS("All sizes have been added successfully."))
