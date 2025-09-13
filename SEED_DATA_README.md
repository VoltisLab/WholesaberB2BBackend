# Database Seeding for WholesalersMarketServer

This directory contains scripts to populate the database with fake data for testing and development.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Seed the database:**
   ```bash
   python manage.py seed_data
   ```

   Or use the custom script:
   ```bash
   python seed_database.py
   ```

## What Gets Created

The seed script creates:

- **100 Users** (80 customers, 20 vendors)
- **30 Vendor Profiles** with business information
- **500 Products** across various categories
- **200 Orders** with realistic order items
- **Shopping Carts** and **Wishlists** for users
- **Delivery Addresses** and **Payment Methods**
- **Categories, Brands, Materials, and Sizes**

## Customization

You can customize the amount of data created:

```bash
python manage.py seed_data --users 50 --vendors 15 --products 250 --orders 100
```

## Data Quality

The fake data includes:
- Realistic names, addresses, and business information
- Proper relationships between users, products, and orders
- Varied product categories and pricing
- Realistic order statuses and payment information
- Complete user profiles with preferences

## Demo Accounts

After seeding, you can use these demo accounts:
- **Customer:** `demo@wholesalers.com` / `demo123`
- **Vendor:** `vendor@wholesalers.com` / `vendor123`

## Notes

- All data is generated using the `faker` library
- The script uses database transactions for safety
- Existing data is not deleted - run migrations to reset if needed
- Images are placeholder URLs from faker

