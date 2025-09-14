#!/bin/bash

# User data script for EC2 instance
# This runs when the instance starts

# Update system
apt-get update
apt-get upgrade -y

# Install Python and dependencies
apt-get install -y python3 python3-pip python3-venv nginx git postgresql-client

# Install Node.js (for any frontend builds)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Create app directory
mkdir -p /opt/wholesaleb2b
cd /opt/wholesaleb2b

# Clone repository
git clone https://github.com/VoltisLab/WholesaberB2BBackend.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn psycopg2-binary

# Create systemd service
cat > /etc/systemd/system/wholesaleb2b.service << EOF
[Unit]
Description=WholesaleB2B Django App
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/wholesaleb2b
Environment=PATH=/opt/wholesaleb2b/venv/bin
ExecStart=/opt/wholesaleb2b/venv/bin/gunicorn --bind 0.0.0.0:8000 src.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
cat > /etc/nginx/sites-available/wholesaleb2b << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /opt/wholesaleb2b/staticfiles/;
    }

    location /media/ {
        alias /opt/wholesaleb2b/media/;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/wholesaleb2b /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx
systemctl enable nginx

# Set up environment variables
cat > /opt/wholesaleb2b/.env << EOF
DJANGO_SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOST=your-domain.com
DATABASE_NAME=wholesaleb2b
DATABASE_USER=postgres
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=your-rds-endpoint.region.rds.amazonaws.com
DATABASE_PORT=5432
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=us-east-1
FRONTEND_URL=https://your-frontend-domain.com
EOF

# Run migrations
cd /opt/wholesaleb2b
source venv/bin/activate
python manage.py migrate --settings=src.settings_production
python manage.py collectstatic --noinput --settings=src.settings_production

# Start the service
systemctl start wholesaleb2b
systemctl enable wholesaleb2b

echo "✅ Deployment complete!"
