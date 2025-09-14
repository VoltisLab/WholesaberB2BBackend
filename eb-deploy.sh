#!/bin/bash

# AWS Elastic Beanstalk Deployment Script
# This is the EASIEST way to deploy to AWS

echo "🚀 Starting AWS Elastic Beanstalk Deployment..."

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Installing..."
    pip install awsebcli
fi

# Check if AWS is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

echo "✅ AWS CLI configured"

# Initialize Elastic Beanstalk
echo "📦 Initializing Elastic Beanstalk..."
eb init --platform python-3.11 --region us-east-1

# Create environment
echo "🌍 Creating Elastic Beanstalk environment..."
eb create wholesaleb2b-prod --instance-type t3.micro

# Set environment variables
echo "🔧 Setting environment variables..."
eb setenv DJANGO_SECRET_KEY=your-production-secret-key-here
eb setenv DEBUG=False
eb setenv ALLOWED_HOST=wholesaleb2b-prod.us-east-1.elasticbeanstalk.com
eb setenv DATABASE_NAME=ebdb
eb setenv DATABASE_USER=ebroot
eb setenv DATABASE_PASSWORD=your-db-password
eb setenv DATABASE_HOST=your-rds-endpoint.region.rds.amazonaws.com
eb setenv DATABASE_PORT=5432
eb setenv AWS_ACCESS_KEY_ID=your-aws-key
eb setenv AWS_SECRET_ACCESS_KEY=your-aws-secret
eb setenv AWS_STORAGE_BUCKET_NAME=your-s3-bucket
eb setenv AWS_S3_REGION_NAME=us-east-1
eb setenv FRONTEND_URL=https://your-frontend-domain.com

# Deploy
echo "🚀 Deploying application..."
eb deploy

# Get URL
echo "✅ Deployment complete!"
echo "🌐 Your app is available at:"
eb status | grep "CNAME"
