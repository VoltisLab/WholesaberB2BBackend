from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.choices import AccountType, GenderChoice
import random
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create fake vendor accounts with existing profile images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of fake vendors to create',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Existing profile images
        profile_images = [
            '55f19ec1-9b9a-4f33-9a1e-b828f4e75c8f.jpg',
            '5d1af7d2-f764-47b5-aa52-aa9399af4fb9.jpg',
            '84c821f4-ea1c-4931-bcf1-474c48508ada.jpg',
        ]
        
        # Vendor business names and details
        vendor_data = [
            {
                'business_name': 'Elite Fashion Co.',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah@elitefashion.com',
                'bio': 'Premium fashion retailer specializing in high-end clothing and accessories.',
                'city': 'New York',
                'website': 'https://elitefashion.com'
            },
            {
                'business_name': 'Urban Streetwear',
                'first_name': 'Marcus',
                'last_name': 'Williams',
                'email': 'marcus@urbanstreetwear.com',
                'bio': 'Trendy streetwear and urban fashion for the modern generation.',
                'city': 'Los Angeles',
                'website': 'https://urbanstreetwear.com'
            },
            {
                'business_name': 'Classic Menswear',
                'first_name': 'David',
                'last_name': 'Brown',
                'email': 'david@classicmenswear.com',
                'bio': 'Traditional and contemporary mens clothing with timeless style.',
                'city': 'Chicago',
                'website': 'https://classicmenswear.com'
            },
            {
                'business_name': 'Boutique Chic',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'email': 'emma@boutiquechic.com',
                'bio': 'Elegant womens fashion and accessories for special occasions.',
                'city': 'Miami',
                'website': 'https://boutiquechic.com'
            },
            {
                'business_name': 'Sportswear Central',
                'first_name': 'Alex',
                'last_name': 'Garcia',
                'email': 'alex@sportswearcentral.com',
                'bio': 'High-performance athletic wear and sports equipment.',
                'city': 'Seattle',
                'website': 'https://sportswearcentral.com'
            },
            {
                'business_name': 'Vintage Finds',
                'first_name': 'Luna',
                'last_name': 'Martinez',
                'email': 'luna@vintagefinds.com',
                'bio': 'Curated vintage and retro clothing from different eras.',
                'city': 'Portland',
                'website': 'https://vintagefinds.com'
            },
            {
                'business_name': 'Kids Corner',
                'first_name': 'Jennifer',
                'last_name': 'Wilson',
                'email': 'jennifer@kidscorner.com',
                'bio': 'Fun and comfortable clothing for children of all ages.',
                'city': 'Austin',
                'website': 'https://kidscorner.com'
            },
            {
                'business_name': 'Luxury Accessories',
                'first_name': 'Robert',
                'last_name': 'Taylor',
                'email': 'robert@luxuryaccessories.com',
                'bio': 'Premium handbags, jewelry, and luxury accessories.',
                'city': 'Boston',
                'website': 'https://luxuryaccessories.com'
            },
            {
                'business_name': 'Eco Fashion',
                'first_name': 'Zoe',
                'last_name': 'Anderson',
                'email': 'zoe@ecofashion.com',
                'bio': 'Sustainable and eco-friendly clothing made from organic materials.',
                'city': 'San Francisco',
                'website': 'https://ecofashion.com'
            },
            {
                'business_name': 'Workwear Pro',
                'first_name': 'Michael',
                'last_name': 'Thompson',
                'email': 'michael@workwearpro.com',
                'bio': 'Professional workwear and business attire for all industries.',
                'city': 'Denver',
                'website': 'https://workwearpro.com'
            }
        ]
        
        created_count = 0
        
        for i in range(min(count, len(vendor_data))):
            vendor_info = vendor_data[i]
            
            # Check if vendor already exists
            if User.objects.filter(email=vendor_info['email']).exists():
                self.stdout.write(
                    self.style.WARNING(f'Vendor {vendor_info["email"]} already exists, skipping...')
                )
                continue
            
            try:
                # Create vendor user
                vendor = User.objects.create(
                    username=vendor_info['email'].split('@')[0] + str(i),
                    first_name=vendor_info['first_name'],
                    last_name=vendor_info['last_name'],
                    email=vendor_info['email'],
                    account_type=AccountType.SUPPLIER,
                    gender=random.choice([GenderChoice.MALE, GenderChoice.FEMALE, GenderChoice.OTHER]),
                    city=vendor_info['city'],
                    bio=vendor_info['bio'],
                    website=vendor_info['website'],
                    profile_picture_url=f'/media/profile_images/{random.choice(profile_images)}',
                    is_verified=True,
                    is_active=True,
                    terms_accepted=True,
                    date_joined=timezone.now() - timedelta(days=random.randint(1, 365)),
                    last_login=timezone.now() - timedelta(days=random.randint(1, 30)),
                    meta={
                        'business_name': vendor_info['business_name'],
                        'business_type': 'fashion_retail',
                        'years_in_business': random.randint(1, 20),
                        'customer_rating': round(random.uniform(3.5, 5.0), 1),
                        'total_products': random.randint(10, 500),
                        'social_media': {
                            'instagram': f'@{vendor_info["business_name"].lower().replace(" ", "")}',
                            'facebook': f'facebook.com/{vendor_info["business_name"].lower().replace(" ", "")}',
                            'twitter': f'@{vendor_info["business_name"].lower().replace(" ", "")}'
                        }
                    }
                )
                
                # Set a default password
                vendor.set_password('vendor123')
                vendor.save()
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created vendor: {vendor_info["business_name"]} ({vendor_info["email"]})')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating vendor {vendor_info["email"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} fake vendors!')
        )
