# 🚀 Deployment Guide

## Option 1: Railway (Recommended - Free & Easy)

### Step 1: Prepare Repository
1. Push your code to GitHub (already done ✅)
2. Make sure all files are committed

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `WholesaberB2BBackend` repository
5. Railway will automatically detect Django and deploy

### Step 3: Configure Environment Variables
In Railway dashboard, add these environment variables:

```
DJANGO_SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOST=your-app-name.railway.app
DATABASE_NAME=railway
DATABASE_USER=postgres
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=your-db-host.railway.app
DATABASE_PORT=5432
FRONTEND_URL=https://your-frontend-domain.com
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=us-east-1
```

### Step 4: Run Migrations
In Railway console:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## Option 2: Heroku

### Step 1: Install Heroku CLI
```bash
brew install heroku/brew/heroku
```

### Step 2: Login and Create App
```bash
heroku login
heroku create your-app-name
```

### Step 3: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Step 4: Set Environment Variables
```bash
heroku config:set DJANGO_SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOST=your-app-name.herokuapp.com
```

### Step 5: Deploy
```bash
git push heroku main
heroku run python manage.py migrate
```

---

## Option 3: DigitalOcean App Platform

### Step 1: Connect GitHub
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App" → "GitHub"
3. Select your repository

### Step 2: Configure
- **Source**: `Backend/WholesalersMarketServer`
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `daphne -b 0.0.0.0 -p $PORT src.asgi:application`

---

## Option 4: AWS EC2 (Advanced)

### Step 1: Launch EC2 Instance
- Ubuntu 20.04 LTS
- t2.micro (free tier)

### Step 2: Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
pip3 install gunicorn
```

### Step 3: Deploy Code
```bash
git clone https://github.com/VoltisLab/WholesaberB2BBackend.git
cd WholesaberB2BBackend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Frontend Updates

After deploying backend, update your Flutter app:

```dart
// In lib/services/graphql_service.dart
static const String _endpoint = 'https://your-backend-url.railway.app/wms/graphql/';

// In lib/services/image_upload_service.dart  
static const String _baseUrl = 'https://your-backend-url.railway.app';
```

---

## 📱 Testing

1. Deploy backend to Railway/Heroku
2. Get the live URL (e.g., `https://your-app.railway.app`)
3. Update Flutter app URLs
4. Test login and functionality
5. Deploy Flutter app to App Store/Play Store

---

## 💰 Cost Comparison

- **Railway**: Free tier (500 hours/month)
- **Heroku**: $7/month for hobby plan
- **DigitalOcean**: $5/month for basic plan
- **AWS EC2**: Free tier (1 year), then ~$10/month

**Recommendation**: Start with Railway (free) for testing, then move to Heroku or DigitalOcean for production.
