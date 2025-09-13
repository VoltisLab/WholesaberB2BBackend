from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category
from collections import defaultdict


class Command(BaseCommand):
    help = "Sets up initial category structure"

    def __init__(self):
        super().__init__()
        self.slug_count = defaultdict(int)

    def create_unique_slug(self, name, parent=None):
        """Create a unique slug for the category"""
        base_slug = slugify(name)
        if parent:
            parent_slug = parent.slug
            full_slug = f"{parent_slug}-{base_slug}"
        else:
            full_slug = base_slug

        # If this slug has been used before, append a number
        if full_slug in self.slug_count:
            self.slug_count[full_slug] += 1
            full_slug = f"{full_slug}-{self.slug_count[full_slug]}"
        else:
            self.slug_count[full_slug] = 0

        return full_slug

    def create_category(self, name, parent=None):
        """Helper method to create a category with unique slug"""
        slug = self.create_unique_slug(name, parent)

        category, created = Category.objects.get_or_create(
            slug=slug, defaults={"name": name, "parent": parent}
        )

        if created:
            self.stdout.write(f"Created category: {category.get_full_path()}")
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Category already exists: {category.get_full_path()}"
                )
            )

        return category

    def process_subcategories(self, data, parent=None):
        """Recursively process category structure"""
        if isinstance(data, dict):
            for name, subcategories in data.items():
                category = self.create_category(name, parent)
                self.stdout.write(f"Created category: {category.get_full_path()}")
                self.process_subcategories(subcategories, category)
        elif isinstance(data, list):
            for item in data:
                if item:  # Check if item is not empty
                    category = self.create_category(item, parent)
                    self.stdout.write(f"Created category: {category.get_full_path()}")

    def handle(self, *args, **kwargs):
        # Define the category structure

        """
        WARNING: DO NOT UNCOMMENT THE FOLLOWING LINE!
        Un-commenting this line will delete ALL categories in the database.
        """
        # Categories.objects.all().delete()
        # self.stdout.write("Cleared existing categories")

        categories = {
            "Men": {
                "Clothing": {
                    "Tops": {
                        "Shirts": [
                            "Plain Shirts",
                            "Striped Shirts",
                            "Denim Shirts",
                            "Print Shirts",
                            "Checked Shirts",
                            "Other Shirts",
                        ],
                        "T-Shirts": [
                            "Plain T-Shirts",
                            "Print T-Shirts",
                            "Sleeveless t-shirts",
                            "Long Sleeve T-Shirts",
                            "Polo T-Shirts",
                            "Other T-Shirts",
                        ],
                        "Polos": [],
                        "Vests": [],
                        "Tank Tops": [],
                    },
                    "Bottoms": {
                        "Jeans": [
                            "Skinny Jeans",
                            "Slim fit jeans ",
                            "Straight Jeans",
                            "Ripped Jeans",
                            "Baggy Jeans",
                            "3/4 Jeans",
                            "Slim Jeans",
                            "Other jeans",
                        ],
                        "Trousers": [
                            "Cargo Trousers",
                            "Skinny Trousers",
                            "Smart Trousers",
                            "Tailoured Trousers",
                            "Cropped Trousers",
                            "Other Trousers",
                        ],
                        "Shorts": [
                            "Cargo Trousers",
                            "Denim Shorts",
                            "Jorts",
                            "Jersey Shorts",
                            "Chino Shorts",
                            "Other Shorts",
                        ],
                        "Chinos": [],
                        "Joggers": [],
                    },
                    "Outerwear": {
                        "Jackets": [
                            "Bomber Jackets",
                            "Denim Jackets",
                            "Leather Jackets",
                            "Puffer Jackets",
                            "Biker and Racer jackets",
                            "Shackets",
                            "Denim jackets",
                            "Varsity jackets",
                            "Windbreakers",
                            "Harrington jackets",
                            "Fleece Jackets",
                            "Quilted Jackets",
                            "Ski and Snow jackets",
                            "Field and Utility jackets",
                            "Other Jackets",
                        ],
                        "Coats": [
                            "Overcoats and Smartcoats",
                            "Trench Coats",
                            "Rain Coats",
                            "Duffle Coats",
                            "Parkas",
                            "Pea Coats",
                            "Other Coats",
                        ],
                    },
                    "Activewear": [
                        "Gym Tops",
                        "Track pants",
                        "Sweaters",
                        "Hoodies",
                        "Tracksuits",
                        "Shorts",
                        "Pullovers",
                        "Other activewear",
                    ],
                    "Knitwear": [
                        "Jumpers",
                        "Cardigans",
                        "Turtleneck jumpers",
                        "Hoodies & Sweaters",
                        "Zip through hoodies and sweaters",
                        "V-neck jumpers",
                        "Crew neck jumpers",
                        "Chunky-knit jumpers",
                        "Sleeveless jumpers",
                        "Long jumpers",
                        "Other Knitwear",
                    ],
                    "Underwear & Socks": [
                        "Briefs",
                        "Boxers",
                        "Boxer Briefs",
                        "Thermal Underwear",
                        "Ankle Socks",
                        "Crew Socks",
                    ],
                    "Loungewear": [
                        "Pyjamas",
                        "Lounge Pants",
                        "Robes",
                    ],
                    "Suits": {
                        "Suit Jackets & blazers": [],
                        "Suit Trousers": [],
                        "Suit sets ": [],
                        "Waistcoats": [],
                    },
                },
                "Shoes": {
                    "Boots": [
                        "Chelsea Boots",
                        "Wellington Boots",
                        "Desert Boots",
                        "Work Boots",
                        "Hiking Boots",
                        "Cowboy Boots",
                        "Dress Boots",
                        "Winter Boots",
                        "Motorcycle Boots",
                        "Rain Boots",
                        "Ankle Boots",
                        "Mountaineering Boots",
                        "Outdoor Boots",
                    ],
                    "Sports Shoes": [
                        "Running Shoes",
                        "Training Shoes",
                        "Football Boots",
                        "Basketball Shoes",
                        "Tennis Shoes",
                        "Hiking Shoes",
                        "Golf Shoes",
                        "Skateboarding Shoes",
                        "Cycling Shoes",
                        "Cricket Shoes",
                        "Rugby Boots",
                        "Squash Shoes",
                        "Badminton Shoes",
                        "Boxing Shoes",
                        "Wrestling Shoes",
                        "Snow Sports Shoes",
                        "Water Sports Shoes",
                        "Track and Field Shoes",
                        "Motor Sports Shoes",
                    ],
                    "Formal Shoes": [],
                    "Casual Shoes": [],
                    "Sports and Activewear Shoes": [],
                    "Flips and Slippers": [],
                    "Specialty and Occasion Shoes": [],
                    "Ethnic and Traditional Shoes": [],
                    "Sustainable/Innovative Shoes": [],
                    "Orthopedic Shoes": [],
                    "Clogs": [],
                    "Water Shoes": [],
                    "Workwear Shoes": [],
                    "Custom/Designer Shoes": [],
                    "Other shoes": [],
                },
                "accessories": {
                    "Bags": [
                        "Bag packs",
                        "Duffle bags",
                        "Bum bags",
                        "Shopper bags",
                    ],
                    "Jewellery": [
                        "Rings",
                        "Necklaces",
                        "Earrings",
                        "Bracelets",
                    ],
                    "Gloves": [],
                    "Watches": [],
                    "Beanies": [],
                    "Scarves": [],
                    "Ties and tie clips": [],
                    "Socks": [],
                    "Caps and hats": [],
                    "Sunglasses": [],
                    "Belts": [],
                    "Cufflinks": [],
                    "Wallets": [],
                },
            },
            "Women": {
                "Clothing": {
                    "Tops": [
                        "Shirts",
                        "T-Shirts",
                        "Blouses",
                        "Tank Tops",
                        "Cropped Tops",
                        "Camisoles",
                        "Tunics",
                        "Halter Tops",
                        "Off-Shoulder Tops",
                        "Wrap Tops",
                        "Bodysuits",
                        "Sweatshirts",
                        "Hoodies",
                        "Vest Tops",
                        "3/4 Sleeved tops",
                        "Short sleeved tops",
                        "Cropped shirts",
                        "Turtlenecks",
                        "Peplum tops",
                        "Off-the-shoulder tops",
                        "Other tops",
                    ],
                    "Bottoms": {
                        "Jeans": [
                            "Skinny Jeans",
                            "Straight-Leg Jeans",
                            "Bootcut Jeans",
                            "Flared Jeans",
                            "Wide-Leg Jeans",
                            "Mom Jeans",
                            "Boyfriend Jeans",
                            "Jeggings",
                            "Ripped/Distressed Jeans",
                            "Cropped Jeans",
                            "High-Waisted Jeans",
                            "Colored Jeans",
                            "Printed Jeans",
                            "Raw Denim",
                            "3/4 Jeans",
                            "Other Jeans",
                        ],
                        "Leggings": [],
                        "Skirts": [
                            "Mini Skirts",
                            "Midi Skirts",
                            "Maxi Skirts",
                            "Pencil Skirts",
                            "A-Line Skirts",
                            "Wrap Skirts",
                            "Pleated Skirts",
                            "Skater Skirts",
                            "Tiered Skirts",
                            "Denim Skirts",
                            "Other Skirts",
                        ],
                        "Shorts": [
                            "Denim Shorts",
                            "Bermuda Shorts",
                            "High-Waisted Shorts",
                            "Athletic Shorts",
                            "Cargo Shorts",
                            "Biker Shorts",
                            "Paperbag Shorts",
                            "Linen Shorts",
                            "Tailored Shorts",
                            "Pleated Shorts",
                            "Other Shorts",
                        ],
                        "Trousers": [
                            "Wide-Leg Trousers",
                            "Straight-Leg Trousers",
                            "High-Waisted Trousers",
                            "Cropped Trousers",
                            "Palazzo Trousers",
                            "Flared Trousers",
                            "Tapered Trousers",
                            "Pleated Trousers",
                            "Cargo Trousers",
                            "Jogger Trousers",
                            "Linen Trousers",
                            "Other Trousers",
                        ],
                    },
                    "Dresses": [],
                    "Outerwear": {
                        "Jackets": [
                            "Puffer Jackets",
                            "Bomber Jackets",
                            "Biker and Racer Jackets",
                            "Leather Jackets",
                            "Shackets",
                            "Denim Jackets",
                            "Varsity Jackets",
                            "Windbreakers",
                            "Fleece Jackets",
                            "Quilted Jackets",
                            "Ski and Snow Jackets",
                            "Field and Utility jackets",
                            "Cropped Jackets",
                        ],
                        "Coats": [
                            "Overcoats and Smartcoats",
                            "Trench coats",
                            "Duffle Coats",
                            "Parkas",
                            "Raincoats",
                            "Peacoats",
                            "Faux Fur Coats",
                        ],
                    },
                    "Activewear": [
                        "Leggings",
                        "Sports Bras",
                        "Gym Tops",
                        "Hoodies",
                        "Tracksuits",
                        "Outerwear",
                        "Trousers",
                        "Skirts",
                        "Tops",
                        "Dresses",
                        "Accessories",
                        "Shorts ",
                        "Other Activewear",
                    ],
                    "Knitwear": {
                        "Sweaters": [
                            "Hoodies and Sweatshirts",
                            "Cropped hoodies",
                            "Other hoodies and sweatshirts",
                            "Other Sweatshirts",
                        ],
                        "Jumpers": [
                            "Crew Neck Jumpers",
                            "V-Neck Jumpers",
                            "Turtleneck Jumpers",
                            "Cable Knit Jumpers",
                            "Chunky Knit Jumpers",
                            "Oversized Jumpers",
                            "Cropped Jumpers",
                            "3/4 Sleeved jumpers",
                            "Other Jumpers",
                        ],
                        "Cardigans": [],
                        "Pullovers": [],
                        "Ponchos": [],
                    },
                    "Lingerie and underwear": [
                        "Bras",
                        "Panties",
                        "Corsets",
                        "Bustiers",
                        "Shapewear",
                        "Camisoles",
                        "Robes",
                        "Babydolls",
                        "Stockings",
                        "Garter Belts",
                        "Sets",
                        "Other Lingerie",
                    ],
                    "Loungewear": [
                        "Pyjamas",
                        "Lounge Pants",
                        "Robes",
                    ],
                    "Suits": [
                        "Suit Jackets & blazers",
                        "Suit Trousers",
                        "Suit sets ",
                        "Waistcoats",
                    ],
                    "Maternity clothing": [
                        "Maternity Dresses",
                        "Maternity Tops",
                        "Maternity T-Shirts",
                        "Maternity Pants",
                        "Maternity Jeans",
                        "Maternity Leggings",
                        "Maternity Skirts",
                        "Maternity Shorts",
                        "Maternity Sweaters",
                        "Maternity Bra",
                        "Maternity Activewear",
                        "Maternity Jumpsuits & Rompers",
                        "Maternity Coats & Outerwear",
                        "Maternity Pajamas & Sleepwear",
                        "Maternity Nursing Tops",
                    ],
                },
                "Shoes": {
                    "Boots": [
                        "Chelsea Boots",
                        "Ankle Boots",
                        "Knee-High Boots",
                        "Thigh-High Boots",
                        "Combat Boots",
                        "Hiking Boots",
                        "Cowboy Boots",
                        "Riding Boots",
                        "Rain Boots",
                        "Snow Boots",
                        "Wedge Boots",
                        "Heeled Boots",
                        "Flat Boots",
                        "Sock Boots",
                    ],
                    "Sports Shoes": [
                        "Running Shoes",
                        "Training Shoes",
                        "Tennis Shoes",
                        "Basketball Shoes",
                        "Football Boots",
                        "Hiking Shoes",
                        "Golf Shoes",
                        "Cycling Shoes",
                        "Cricket Shoes",
                        "Rugby Boots",
                        "Squash Shoes",
                        "Badminton Shoes",
                        "Boxing Shoes",
                        "Wrestling Shoes",
                        "Track and Field Shoes",
                        "Skateboarding Shoes",
                        "Water Sports Shoes",
                        "Snow Sports Shoes",
                        "Dance Sneakers",
                        "Multi-Sport Shoes",
                    ],
                    "Formal Shoes": [],
                    "Casual Shoes": [],
                    "Sports and Activewear Shoes": [],
                    "Flips and Slippers": [],
                    "Specialty and Occasion Shoes": [],
                    "Ethnic and Traditional Shoes": [],
                    "Sustainable/Innovative Shoes": [],
                    "Orthopedic Shoes": [],
                    "Clogs": [],
                    "Water Shoes": [],
                    "Workwear Shoes": [],
                    "Custom/Designer Shoes": [],
                    "Heels": [],
                    "Flats": [],
                    "Sandals": [],
                    "Ballet Shoes": [],
                    "Laced up shoes": [],
                    "Dance Shoes": [],
                },
                "Accessories": {
                    "Bags": [
                        "Tote bags",
                        "Shoulder bags",
                        "Bag packs",
                        "Handbags",
                        "Bum bags",
                    ],
                    "Jewellery": [
                        "Rings",
                        "Necklaces",
                        "Earrings",
                        "Bracelets",
                        "Body Jewellery",
                        "Anklets",
                        "Ear cuffs",
                        "Chokers",
                    ],
                    "Hair Accessories": [],
                    "Socks and tights": [],
                    "Gloves": [],
                    "Scarves": [],
                    "Hats": [],
                    "Watches": [],
                    "Belts": [],
                    "Caps and hats": [],
                    "Sunglasses": [],
                },
            },
            "Boys": {
                "Clothing": {
                    "Tops": {
                        "Shirts": [
                            "Plain Shirts",
                            "Striped Shirts",
                            "Denim Shirts",
                            "Print Shirts",
                            "Checked Shirts",
                            "Other Shirts",
                        ],
                        "T-Shirts": [
                            "Plain T-Shirts",
                            "Print T-Shirts",
                            "Sleeveless t-shirts",
                            "Long Sleeve T-Shirts",
                            "Polo T-Shirts",
                            "Other T-Shirts",
                        ],
                        "Vests": [],
                    },
                    "Bottoms": {
                        "Jeans": [
                            "Skinny Jeans",
                            "Slim fit jeans ",
                            "Straight Jeans",
                            "Ripped Jeans",
                            "Baggy Jeans",
                            "3/4 Jeans",
                            "Slim Jeans",
                            "Other jeans",
                        ],
                        "Trousers": [
                            "Cargo Trousers",
                            "Skinny Trousers",
                            "Smart Trousers",
                            "Tailoured Trousers",
                            "Cropped Trousers",
                            "Other Trousers",
                        ],
                        "Shorts": [
                            "Cargo Trousers",
                            "Denim Shorts",
                            "Jorts",
                            "Jersey Shorts",
                            "Chino Shorts",
                            "Other Shorts",
                        ],
                        "Chinos": [],
                        "Joggers": [],
                    },
                    "Outerwear": {
                        "Jackets": [
                            "Bomber Jackets",
                            "Denim Jackets",
                            "Leather Jackets",
                            "Puffer Jackets",
                            "Biker and Racer jackets",
                            "Shackets",
                            "Denim jackets",
                            "Varsity jackets",
                            "Windbreakers",
                            "Harrington jackets",
                            "Fleece Jackets",
                            "Quilted Jackets",
                            "Ski and Snow jackets",
                            "Other Jackets",
                        ],
                        "Coats": [
                            "Overcoats and Smartcoats",
                            "Trench Coats",
                            "Rain Coats",
                            "Duffle Coats",
                            "Parkas",
                            "Pea Coats",
                            "Other Coats",
                        ],
                    },
                    "Activewear": [
                        "Gym Tops",
                        "Track pants",
                        "Sweaters",
                        "Hoodies",
                        "Tracksuits",
                        "Shorts",
                        "Pullovers",
                        "Other activewear",
                    ],
                    "Knitwear": [
                        "Jumpers",
                        "Cardigans",
                        "Turtleneck jumpers",
                        "Hoodies & Sweaters",
                        "Zip through hoodies and sweaters",
                        "V-neck jumpers",
                        "Crew neck jumpers",
                        "Chunky-knit jumpers",
                        "Sleeveless jumpers",
                        "Long jumpers",
                        "Other Knitwear",
                    ],
                    "Underwear & Socks": [
                        "Briefs",
                        "Boxers",
                        "Boxer Briefs",
                        "Thermal Underwear",
                        "Ankle Socks",
                        "Crew Socks",
                    ],
                    "Loungewear": [
                        "Pyjamas",
                        "Lounge Pants",
                        "Robes",
                    ],
                    "Suits": {
                        "Suit Jackets & blazers": [],
                        "Suit Trousers": [],
                        "Suit sets ": [],
                        "Waistcoats": [],
                    },
                }
            },
            "Girls": {
                "Clothing": {
                    "Tops": {
                        "Shirts": [
                            "Plain Shirts",
                            "Striped Shirts",
                            "Denim Shirts",
                            "Print Shirts",
                            "Checked Shirts",
                            "Other Shirts",
                        ],
                        "T-Shirts": [
                            "Plain T-Shirts",
                            "Long Sleeve T-Shirts",
                            "Print T-Shirts",
                            "Polo T-Shirts",
                            "Sleeveless t-shirts",
                            "Other T-Shirts",
                        ],
                        "Vests": [],
                        "Sleeveless tops": [],
                    },
                    "Bottoms": {
                        "Jeans": [
                            "Skinny Jeans",
                            "Slim fit jeans ",
                            "Straight Jeans",
                            "Ripped Jeans",
                            "Baggy Jeans",
                            "3/4 Jeans",
                            "Other jeans",
                        ],
                        "Trousers": [
                            "Cargo Trousers",
                            "Skinny Trousers",
                            "Cropped Trousers",
                            "Smart Trousers",
                            "Tailoured Trousers",
                            "Other Trousers",
                        ],
                        "Shorts": [
                            "Cargo Trousers",
                            "Denim Shorts",
                            "Jorts",
                            "Jersey Shorts",
                            "Chino Shorts",
                            "Other Shorts",
                        ],
                        "Skirts": [
                            "Mini Skirts",
                            "Midi Skirts",
                            "Maxi Skirts",
                            "Pencil Skirts",
                            "A-Line Skirts",
                            "Wrap Skirts",
                            "Pleated Skirts",
                            "Skater Skirts",
                            "Tiered Skirts",
                            "Denim Skirts",
                            "Other Skirts",
                        ],
                        "Chinos": [],
                        "Joggers": [],
                    },
                    "Outerwear": {
                        "Jackets": [
                            "Bomber Jackets",
                            "Denim Jackets",
                            "Leather Jackets",
                            "Puffer Jackets",
                            "Biker and Racer jackets",
                            "Shackets",
                            "Denim jackets",
                            "Varsity jackets",
                            "Windbreakers",
                            "Harrington jackets",
                            "Fleece Jackets",
                            "Quilted Jackets",
                            "Ski and Snow jackets",
                            "Other Jackets",
                        ],
                        "Coats": [
                            "Overcoats and Smartcoats",
                            "Trench Coats",
                            "Rain Coats",
                            "Duffle Coats",
                            "Parkas",
                            "Pea Coats",
                            "Other Coats",
                        ],
                    },
                    "Activewear": [
                        "Gym Tops",
                        "Track pants",
                        "Sweaters",
                        "Hoodies",
                        "Tracksuits",
                        "Shorts",
                        "Pullovers",
                        "Other activewear",
                    ],
                    "Knitwear": [
                        "Jumpers",
                        "Cardigans",
                        "Turtleneck jumpers",
                        "Hoodies & Sweaters",
                        "Zip through hoodies and sweaters",
                        "V-neck jumpers",
                        "Crew neck jumpers",
                        "Chunky-knit jumpers",
                        "Sleeveless jumpers",
                        "Long jumpers",
                        "Other Knitwear",
                    ],
                    "Underwear & Socks": [
                        "Tights",
                        "Underwear",
                        "Thermal Underwear",
                        "Ankle Socks",
                        "Crew Socks",
                        "Bralet",
                    ],
                    "Sleepwear": [
                        "Pyjamas",
                        "Nighties",
                        "Onesies",
                        "Lounge Pants",
                        "Robes",
                    ],
                    "Baby": [
                        "Rompers",
                        "Bodysuits",
                        "Dungarees",
                        "Sets",
                        "Other",
                    ],
                },
                "Shoes": [
                    "Baby shoes",
                    "Boots",
                    "Clogs ",
                    "Flats",
                    "Special occasion shoes",
                    "Slippers",
                    "Flip Flops",
                    "Sports shoes",
                    "Trainers",
                    "Mules",
                    "Slides",
                    "Other",
                ],
            },
            "Toddlers": [],
            "Electronics": [],
            "General": [],
            "Fashion": [],
        }

        try:
            self.process_subcategories(categories)
            self.stdout.write(
                self.style.SUCCESS("Successfully created category structure")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating categories: {str(e)}"))
            raise
