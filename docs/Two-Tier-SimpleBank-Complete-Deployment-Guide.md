# Two-Tier SimpleBank Banking Application - Complete Deployment Guide

**Author:** THAKUR-ROHIT-21  
**Date:** July 12, 2026  
**Project Type:** Cloud DevOps Deployment  
**Cloud Provider:** AWS  
**Region:** ap-south-1 (Mumbai)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Design](#2-architecture-design)
3. [AWS Services Used](#3-aws-services-used)
4. [Prerequisites & Setup](#4-prerequisites--setup)
5. [VPC & Networking Configuration](#5-vpc--networking-configuration)
6. [Security Groups Setup](#6-security-groups-setup)
7. [RDS MySQL Database](#7-rds-mysql-database)
8. [Database Schema](#8-database-schema)
9. [SSM Parameter Store](#9-ssm-parameter-store)
10. [Flask Application Setup](#10-flask-application-setup)
11. [Docker Configuration](#11-docker-configuration)
12. [Docker Compose Setup](#12-docker-compose-setup)
13. [Amazon ECR Setup](#13-amazon-ecr-setup)
14. [S3 Configuration](#14-s3-configuration)
15. [EC2 Instances](#15-ec2-instances)
16. [IAM Roles & Permissions](#16-iam-roles--permissions)
17. [Application Load Balancer](#17-application-load-balancer)
18. [Route 53 DNS](#18-route-53-dns)
19. [HTTPS with ACM](#19-https-with-acm)
20. [SNS Notifications](#20-sns-notifications)
21. [GitHub Actions CI/CD](#21-github-actions-cicd)
22. [Deployment Process](#22-deployment-process)
23. [Testing & Verification](#23-testing--verification)
24. [Troubleshooting Guide](#24-troubleshooting-guide)
25. [Interview Explanation](#25-interview-explanation)

---

## 1. Project Overview

### What is SimpleBank?

SimpleBank is a Flask-based web banking application deployed on AWS using a two-tier architecture:

- **Tier 1 (Application Layer):** Flask application running in Docker containers on EC2 instances
- **Tier 2 (Database Layer):** Amazon RDS MySQL for secure data persistence

### Key Features

```
✓ User Registration & Login
✓ Bank Account Management
✓ Account Balance Tracking
✓ Secure Database Connection
✓ Email Notifications via SNS
✓ High Availability with Load Balancing
✓ Automated CI/CD Deployment
✓ HTTPS Security
✓ Centralized Configuration Management
```

### Project Goal

Deploy a production-ready banking application on AWS with:
- Scalability
- High Availability
- Security
- Automated Deployment

---

## 2. Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERNET USERS                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Route 53 DNS
                         │
                 ┌────────▼────────┐
                 │   ACM HTTPS     │
                 │  (SSL/TLS)      │
                 └────────┬────────┘
                         │
        ┌────────────────▼────────────────┐
        │  Application Load Balancer      │
        │         (Port 80/443)           │
        └────────┬──────────────┬─────────┘
                 │              │
        ┌────────▼────┐   ┌─────▼────────┐
        │  EC2 Instance 1 │   │  EC2 Instance 2 │
        │  (Flask App)    │   │  (Flask App)    │
        │  Port 5000      │   │  Port 5000      │
        │  Docker         │   │  Docker         │
        └────────┬────────┘   └─────┬──────────┘
                 │                  │
                 │                  │
                 └──────────┬───────┘
                            │
              ┌─────────────▼─────────────┐
              │  Amazon RDS MySQL         │
              │  (Private Subnet)         │
              │  Database: banking_db     │
              │  Port: 3306               │
              └───────────────────────────┘
```

### Request Flow

```
1. User visits https://bank.example.com
2. Route 53 resolves to ALB DNS
3. ACM validates HTTPS certificate
4. ALB receives request on port 443
5. ALB forwards to Target Group (HTTP:5000)
6. EC2 Instance 1 or 2 receives request
7. Flask application processes request
8. Flask connects to RDS MySQL (Private)
9. Database query executed
10. Response sent back through ALB to user
```

---

## 3. AWS Services Used

### Compute Services
- **EC2:** Application servers (2 instances)
- **Docker:** Container runtime
- **ECR:** Docker image registry

### Networking
- **VPC:** Custom network
- **Public Subnets:** ALB and EC2 instances
- **Private Subnets:** RDS database
- **Internet Gateway:** Internet access
- **Route Tables:** Traffic routing
- **Security Groups:** Firewall rules

### Database
- **RDS MySQL:** Managed database

### Load Balancing & DNS
- **Application Load Balancer:** Traffic distribution
- **Target Group:** EC2 instance grouping
- **Route 53:** Domain DNS

### Configuration & Secrets
- **SSM Parameter Store:** Secure configuration storage
- **Systems Manager:** Remote command execution

### Storage
- **S3:** Docker-compose file storage

### Security & Certificates
- **IAM Roles:** Access control
- **ACM:** HTTPS certificates

### Notifications
- **SNS:** Email notifications

### CI/CD
- **GitHub Actions:** Automated deployment

---

## 4. Prerequisites & Setup

### Local Machine Requirements

```
✓ Git installed
✓ Docker installed
✓ AWS CLI v2 configured
✓ AWS credentials with appropriate permissions
✓ Python 3.11+
✓ Text editor/IDE
```

### AWS CLI Configuration

```bash
aws configure
# Enter AWS Access Key ID
# Enter AWS Secret Access Key
# Enter default region: ap-south-1
# Enter default output format: json
```

---

## 5. VPC & Networking Configuration

### Create VPC

```bash
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=SimpleBank-VPC}]' \
  --region ap-south-1
```

### Create Public Subnets

```bash
aws ec2 create-subnet \
  --vpc-id vpc-xxxxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-Subnet-1}]' \
  --region ap-south-1
```

### Create Internet Gateway

```bash
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=SimpleBank-IGW}]' \
  --region ap-south-1

aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-xxxxx \
  --vpc-id vpc-xxxxx \
  --region ap-south-1
```

### Create Route Table

```bash
aws ec2 create-route-table \
  --vpc-id vpc-xxxxx \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Public-RT}]' \
  --region ap-south-1

aws ec2 create-route \
  --route-table-id rtb-xxxxx \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-xxxxx \
  --region ap-south-1
```

---

## 6. Security Groups Setup

### ALB Security Group

```bash
aws ec2 create-security-group \
  --group-name SimpleBank-ALB-SG \
  --description "ALB Security Group" \
  --vpc-id vpc-xxxxx \
  --region ap-south-1

aws ec2 authorize-security-group-ingress \
  --group-id sg-alb-xxxxx \
  --protocol tcp --port 80 \
  --cidr 0.0.0.0/0 \
  --region ap-south-1

aws ec2 authorize-security-group-ingress \
  --group-id sg-alb-xxxxx \
  --protocol tcp --port 443 \
  --cidr 0.0.0.0/0 \
  --region ap-south-1
```

### EC2 Security Group

```bash
aws ec2 create-security-group \
  --group-name SimpleBank-EC2-SG \
  --description "EC2 Security Group" \
  --vpc-id vpc-xxxxx \
  --region ap-south-1

aws ec2 authorize-security-group-ingress \
  --group-id sg-ec2-xxxxx \
  --protocol tcp --port 5000 \
  --source-group sg-alb-xxxxx \
  --region ap-south-1
```

### RDS Security Group

```bash
aws ec2 create-security-group \
  --group-name SimpleBank-RDS-SG \
  --description "RDS Security Group" \
  --vpc-id vpc-xxxxx \
  --region ap-south-1

aws ec2 authorize-security-group-ingress \
  --group-id sg-rds-xxxxx \
  --protocol tcp --port 3306 \
  --source-group sg-ec2-xxxxx \
  --region ap-south-1
```

---

## 7. RDS MySQL Database

### Create DB Subnet Group

```bash
aws rds create-db-subnet-group \
  --db-subnet-group-name simplebank-db-subnet \
  --db-subnet-group-description "DB Subnet for SimpleBank" \
  --subnet-ids subnet-private-1 subnet-private-2 \
  --region ap-south-1
```

### Create RDS Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier simplebank-mysql \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --engine-version 8.0.35 \
  --master-username admin \
  --master-user-password "YourSecurePassword123!" \
  --allocated-storage 20 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-rds-xxxxx \
  --db-subnet-group-name simplebank-db-subnet \
  --database-name banking_db \
  --publicly-accessible false \
  --backup-retention-period 7 \
  --region ap-south-1
```

### Wait for Database Ready

```bash
aws rds describe-db-instances \
  --db-instance-identifier simplebank-mysql \
  --region ap-south-1
```

---

## 8. Database Schema

### Create Users Table

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_username ON users(username);
```

### Create Accounts Table

```sql
CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    mobile VARCHAR(20),
    acc_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,
    account_type ENUM('Savings', 'Checking', 'Business') DEFAULT 'Savings',
    status ENUM('Active', 'Inactive', 'Blocked') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_user_id ON accounts(user_id);
CREATE INDEX idx_acc_number ON accounts(acc_number);
```

---

## 9. SSM Parameter Store

### Store Parameters

```bash
aws ssm put-parameter \
  --name "/application/banking/DB_HOST" \
  --value "simplebank-mysql.xxxxx.ap-south-1.rds.amazonaws.com" \
  --type "String" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/application/banking/DB_PORT" \
  --value "3306" \
  --type "String" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/application/banking/DB_NAME" \
  --value "banking_db" \
  --type "String" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/application/banking/DB_USER" \
  --value "admin" \
  --type "String" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/application/banking/DB_PASSWORD" \
  --value "YourSecurePassword123!" \
  --type "SecureString" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/application/banking/FLASK_SECRET_KEY" \
  --value "your-secret-key-from-openssl" \
  --type "SecureString" \
  --region ap-south-1

aws ssm put-parameter \
  --name "/application/banking/SNS_TOPIC_ARN" \
  --value "arn:aws:sns:ap-south-1:306158389325:simplebank-alerts" \
  --type "String" \
  --region ap-south-1
```

---

## 10. Flask Application Setup

### requirements.txt

```
Flask==3.0.0
gunicorn==21.2.0
PyMySQL==1.1.0
cryptography==41.0.0
boto3==1.34.0
python-dotenv==1.0.0
```

### app.py (Complete Flask Application)

```python
import os
import boto3
import pymysql
from flask import Flask, render_template, request, redirect, session, jsonify
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-secret-key")

sns = boto3.client("sns", region_name="ap-south-1")
ssm = boto3.client("ssm", region_name="ap-south-1")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")

def load_ssm_parameters():
    if os.getenv("FLASK_ENV") == "production":
        try:
            response = ssm.get_parameters_by_path(
                Path="/application/banking",
                WithDecryption=True
            )
            for parameter in response["Parameters"]:
                param_name = os.path.basename(parameter["Name"])
                os.environ.setdefault(param_name, parameter["Value"])
        except Exception as e:
            print(f"Error loading SSM parameters: {e}")

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        return connection
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        return None

def send_notification(subject, message):
    if SNS_TOPIC_ARN:
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=subject,
                Message=message
            )
        except Exception as e:
            print(f"SNS Error: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        connection = get_db_connection()
        if not connection:
            return render_template("register.html", error="Database error")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return render_template("register.html", error="Username exists")
                
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, password)
                )
                connection.commit()
                
                send_notification(
                    "SimpleBank Registration",
                    f"New user: {username}\nTime: {datetime.now().isoformat()}"
                )
                
                return redirect("/login?message=Registration successful")
        except Exception as e:
            print(f"Registration error: {e}")
            return render_template("register.html", error="Registration failed")
        finally:
            connection.close()
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        connection = get_db_connection()
        if not connection:
            return render_template("login.html", error="Database error")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s AND password = %s",
                    (username, password)
                )
                user = cursor.fetchone()
                
                if user:
                    session['user_id'] = user['id']
                    session['username'] = username
                    
                    send_notification(
                        "SimpleBank Login",
                        f"User {username} logged in\nTime: {datetime.now().isoformat()}"
                    )
                    
                    return redirect("/dashboard")
                else:
                    return render_template("login.html", error="Invalid credentials")
        except Exception as e:
            print(f"Login error: {e}")
            return render_template("login.html", error="Login failed")
        finally:
            connection.close()
    
    message = request.args.get("message", "")
    return render_template("login.html", message=message)

@app.route("/dashboard")
@login_required
def dashboard():
    connection = get_db_connection()
    if not connection:
        return "Database error", 500
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM accounts WHERE user_id = %s",
                (session['user_id'],)
            )
            accounts = cursor.fetchall()
        
        return render_template("dashboard.html", accounts=accounts, username=session['username'])
    except Exception as e:
        print(f"Dashboard error: {e}")
        return "Error loading dashboard", 500
    finally:
        connection.close()

@app.route("/open-account", methods=["GET", "POST"])
@login_required
def open_account():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        acc_number = request.form.get("acc_number")
        
        connection = get_db_connection()
        if not connection:
            return render_template("open_account.html", error="Database error")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO accounts (user_id, name, email, mobile, acc_number, balance) VALUES (%s, %s, %s, %s, %s, %s)",
                    (session['user_id'], name, email, mobile, acc_number, 0.00)
                )
                connection.commit()
                
                send_notification(
                    "SimpleBank Account Created",
                    f"New account: {acc_number}\nName: {name}"
                )
                
                return redirect("/dashboard?message=Account created")
        except Exception as e:
            print(f"Account error: {e}")
            return render_template("open_account.html", error="Failed to create account")
        finally:
            connection.close()
    
    return render_template("open_account.html")

@app.route("/logout")
def logout():
    username = session.get('username', 'User')
    session.clear()
    
    send_notification(
        "SimpleBank Logout",
        f"User {username} logged out\nTime: {datetime.now().isoformat()}"
    )
    
    return redirect("/?message=Logged out successfully")

if __name__ == "__main__":
    load_ssm_parameters()
    debug_mode = os.getenv("FLASK_ENV", "development") != "production"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
```

---

## 11. Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY src/ .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=20s \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

---

## 12. Docker Compose Setup

### docker-compose.yml

```yaml
version: '3.8'

services:
  simplebank_app:
    image: 306158389325.dkr.ecr.ap-south-1.amazonaws.com/flask_app_for_two_teir_application_simple_bank:${IMAGE_TAG:-latest}
    
    container_name: simplebank_app
    
    ports:
      - "5000:5000"
    
    environment:
      - FLASK_ENV=production
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT:-3306}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - SNS_TOPIC_ARN=${SNS_TOPIC_ARN}
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 20s
```

---

## 13. Amazon ECR Setup

### Create Repository

```bash
aws ecr create-repository \
  --repository-name flask_app_for_two_teir_application_simple_bank \
  --image-scan-on-push true \
  --region ap-south-1
```

### Build & Push

```bash
# Login
aws ecr get-login-password --region ap-south-1 | \
docker login --username AWS --password-stdin \
306158389325.dkr.ecr.ap-south-1.amazonaws.com

# Build
docker build -t 306158389325.dkr.ecr.ap-south-1.amazonaws.com/flask_app_for_two_teir_application_simple_bank:v1 .

# Push
docker push 306158389325.dkr.ecr.ap-south-1.amazonaws.com/flask_app_for_two_teir_application_simple_bank:v1
```

---

## 14. S3 Configuration

```bash
aws s3 mb s3://306158389325-devops-scripts --region ap-south-1
aws s3 cp docker-compose.yml s3://306158389325-devops-scripts/ --region ap-south-1
```

---

## 15. EC2 Instances

### Launch Instances

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --security-group-ids sg-ec2-xxxxx \
  --subnet-id subnet-public-1 \
  --iam-instance-profile Name=EC2-SSM-Role \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=App,Value=flask}]' \
  --region ap-south-1
```

---

## 16. IAM Roles & Permissions

```bash
aws iam create-role --role-name SimpleBank-EC2-Role \
  --assume-role-policy-document file://trust-policy.json

aws iam create-policy --policy-name SimpleBank-EC2-Policy \
  --policy-document file://ec2-policy.json

aws iam attach-role-policy --role-name SimpleBank-EC2-Role \
  --policy-arn arn:aws:iam::306158389325:policy/SimpleBank-EC2-Policy
```

---

## 17. Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name SimpleBank-ALB \
  --subnets subnet-public-1 subnet-public-2 \
  --security-groups sg-alb-xxxxx \
  --region ap-south-1

# Create Target Group
aws elbv2 create-target-group \
  --name SimpleBank-TG \
  --protocol HTTP \
  --port 5000 \
  --vpc-id vpc-xxxxx \
  --health-check-path /health \
  --region ap-south-1

# Register Targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:ap-south-1:306158389325:targetgroup/SimpleBank-TG/xxxxx \
  --targets Id=i-xxxxx Id=i-yyyyy \
  --region ap-south-1
```

---

## 18. Route 53 DNS

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id Z12345678901234 \
  --change-batch file://dns-change.json
```

---

## 19. HTTPS with ACM

```bash
aws acm request-certificate \
  --domain-name bank.example.com \
  --validation-method DNS \
  --region ap-south-1
```

---

## 20. SNS Notifications

```bash
aws sns create-topic --name simplebank-alerts --region ap-south-1

aws sns subscribe \
  --topic-arn arn:aws:sns:ap-south-1:306158389325:simplebank-alerts \
  --protocol email \
  --notification-endpoint your-email@gmail.com \
  --region ap-south-1
```

---

## 21. GitHub Actions CI/CD

### .github/workflows/deploy.yml

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

env:
  VERSION: v1
  IMAGE: 306158389325.dkr.ecr.ap-south-1.amazonaws.com/flask_app_for_two_teir_application_simple_bank
  REGION: ap-south-1

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::306158389325:role/GitHub-Action-Deploy-Role
          aws-region: ap-south-1
      
      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build Docker Image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        run: |
          docker build -t $ECR_REGISTRY/flask_app_for_two_teir_application_simple_bank:$VERSION .
          docker push $ECR_REGISTRY/flask_app_for_two_teir_application_simple_bank:$VERSION
      
      - name: Upload to S3
        run: |
          aws s3 cp docker-compose.yml s3://306158389325-devops-scripts/
      
      - name: Deploy via SSM
        run: |
          aws ssm send-command \
            --document-name "AWS-RunShellScript" \
            --targets "Key=tag:App,Values=flask" \
            --parameters 'commands=["docker pull $IMAGE:$VERSION","cd /home/ubuntu/app && IMAGE_TAG=$VERSION docker compose up -d"]' \
            --region $REGION
```

---

## 22. Deployment Process

```
Code Push → GitHub Actions → Docker Build → ECR Push
    → S3 Upload → SSM Command → EC2 Deployment
    → Health Check → SNS Notification → Complete
```

---

## 23. Testing & Verification

```bash
# Test ALB
ALB_DNS=$(aws elbv2 describe-load-balancers --names SimpleBank-ALB --query 'LoadBalancers[0].DNSName' --output text)
curl http://$ALB_DNS/health

# Check Container
aws ssm start-session --target i-xxxxx
docker ps
docker logs simplebank_app

# Verify Target Health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:ap-south-1:306158389325:targetgroup/SimpleBank-TG/xxxxx
```

---

## 24. Troubleshooting Guide

### ALB Targets Unhealthy
```bash
docker logs simplebank_app
curl http://localhost:5000/health
docker restart simplebank_app
```

### Database Connection Error
```bash
mysql -h $DB_HOST -u admin -p
aws ec2 describe-security-groups --group-ids sg-rds-xxxxx
```

### Image Not Found
```bash
aws ecr describe-images --repository-name flask_app_for_two_teir_application_simple_bank
docker push 306158389325.dkr.ecr.ap-south-1.amazonaws.com/flask_app_for_two_teir_application_simple_bank:v1
```

---

## 25. Interview Explanation

### Project Summary

> "I deployed a production-ready two-tier Flask banking application on AWS with automatic load balancing, secure database access, and CI/CD pipeline using GitHub Actions."

### Architecture

> "The application runs on two EC2 instances with Docker containers behind an Application Load Balancer. MySQL database is in private subnets with RDS. Route 53 handles DNS with HTTPS via ACM. GitHub Actions automatically builds images and deploys via SSM."

### Key Technologies

- **AWS:** VPC, EC2, RDS, ALB, Route 53, ACM, SSM, ECR, S3, SNS
- **DevOps:** Docker, Docker Compose, GitHub Actions
- **Database:** MySQL with backups
- **Security:** SSL/TLS, Security Groups, IAM roles, Parameter Store

### Results

- ✅ High availability with load balancing
- ✅ Secure private database
- ✅ Automated deployment pipeline
- ✅ Horizontal scalability
- ✅ Centralized configuration management
- ✅ Email notifications for events

---

**Project Successfully Deployed!** 🚀

For PDF conversion, use: https://pandoc.org/ or Print → Save as PDF
