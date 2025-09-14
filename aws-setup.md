# 🚀 AWS Deployment Guide

## Prerequisites

1. **AWS Account** ✅ (You have this)
2. **AWS CLI installed**: `brew install awscli`
3. **AWS configured**: `aws configure`

## Step 1: Set Up AWS Resources

### 1.1 Create Security Group
```bash
# Create security group
aws ec2 create-security-group \
    --group-name wholesaleb2b-sg \
    --description "Security group for WholesaleB2B app"

# Allow HTTP traffic
aws ec2 authorize-security-group-ingress \
    --group-name wholesaleb2b-sg \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS traffic
aws ec2 authorize-security-group-ingress \
    --group-name wholesaleb2b-sg \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow SSH (replace with your IP)
aws ec2 authorize-security-group-ingress \
    --group-name wholesaleb2b-sg \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_IP/32
```

### 1.2 Create Key Pair
```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name wholesaleb2b-key \
    --query 'KeyMaterial' \
    --output text > wholesaleb2b-key.pem

# Set permissions
chmod 400 wholesaleb2b-key.pem
```

### 1.3 Create RDS Database (Optional but Recommended)
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name wholesaleb2b-subnet-group \
    --db-subnet-group-description "Subnet group for WholesaleB2B" \
    --subnet-ids subnet-xxxxxxxxx subnet-yyyyyyyyy

# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier wholesaleb2b-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password YourSecurePassword123! \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name wholesaleb2b-subnet-group
```

### 1.4 Create S3 Bucket
```bash
# Create S3 bucket
aws s3 mb s3://wholesaleb2b-media-storage

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket wholesaleb2b-media-storage --policy '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::wholesaleb2b-media-storage/*"
        }
    ]
}'
```

## Step 2: Deploy to EC2

### 2.1 Update the deployment script
Edit `aws-deploy.sh` and replace:
- `your-key-pair` with `wholesaleb2b-key`
- `sg-xxxxxxxxx` with your security group ID
- `subnet-xxxxxxxxx` with your subnet ID

### 2.2 Run deployment
```bash
chmod +x aws-deploy.sh
./aws-deploy.sh
```

## Step 3: Configure Domain (Optional)

### 3.1 Get Elastic IP
```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Associate with instance
aws ec2 associate-address \
    --instance-id i-xxxxxxxxx \
    --allocation-id eipalloc-xxxxxxxxx
```

### 3.2 Set up Route 53 (if you have a domain)
```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name yourdomain.com \
    --caller-reference 2024-01-01

# Create A record
aws route53 change-resource-record-sets \
    --hosted-zone-id Z123456789 \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "api.yourdomain.com",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "YOUR_ELASTIC_IP"}]
            }
        }]
    }'
```

## Step 4: Update Frontend

Update your Flutter app URLs:

```dart
// In lib/services/graphql_service.dart
static const String _endpoint = 'https://api.yourdomain.com/wms/graphql/';

// In lib/services/image_upload_service.dart
static const String _baseUrl = 'https://api.yourdomain.com';
```

## Step 5: SSL Certificate (Recommended)

### 5.1 Install Certbot
```bash
# SSH into your EC2 instance
ssh -i wholesaleb2b-key.pem ubuntu@YOUR_EC2_IP

# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d api.yourdomain.com
```

## Step 6: Monitoring & Maintenance

### 6.1 CloudWatch Logs
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### 6.2 Auto-scaling (Optional)
```bash
# Create launch template
aws ec2 create-launch-template \
    --launch-template-name wholesaleb2b-template \
    --launch-template-data '{
        "ImageId": "ami-0c02fb55956c7d316",
        "InstanceType": "t2.micro",
        "KeyName": "wholesaleb2b-key",
        "SecurityGroupIds": ["sg-xxxxxxxxx"],
        "UserData": "base64-encoded-user-data"
    }'
```

## Cost Estimation

- **EC2 t2.micro**: ~$8.50/month (Free tier eligible for 1 year)
- **RDS db.t3.micro**: ~$15/month (Free tier eligible for 1 year)
- **S3**: ~$1-5/month (depending on usage)
- **Route 53**: ~$0.50/month per hosted zone
- **Elastic IP**: Free when attached to running instance

**Total**: ~$25-30/month (or free for first year with free tier)

## Troubleshooting

### Check instance status
```bash
aws ec2 describe-instances --instance-ids i-xxxxxxxxx
```

### View logs
```bash
# SSH into instance
ssh -i wholesaleb2b-key.pem ubuntu@YOUR_EC2_IP

# Check service status
sudo systemctl status wholesaleb2b

# View logs
sudo journalctl -u wholesaleb2b -f
```

### Restart services
```bash
sudo systemctl restart wholesaleb2b
sudo systemctl restart nginx
```

## Security Best Practices

1. **Use IAM roles** instead of hardcoded credentials
2. **Enable VPC** for better network isolation
3. **Use Application Load Balancer** for production
4. **Set up CloudTrail** for audit logging
5. **Regular security updates**: `sudo apt update && sudo apt upgrade`

Your Django backend will be production-ready on AWS! 🚀
