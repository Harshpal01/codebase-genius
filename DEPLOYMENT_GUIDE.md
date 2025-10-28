# Deployment Guide - Codebase Genius

This guide provides instructions for deploying Codebase Genius in various environments.

---

## Table of Contents

1. [Local Development Deployment](#local-development-deployment)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Security Considerations](#security-considerations)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Local Development Deployment

### Quick Start (Development)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd codebase_genius

# 2. Setup backend
cd BE
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 4. Start backend
jac serve main.jac

# 5. Setup frontend (new terminal)
cd ../FE
pip install -r requirements.txt
streamlit run app.py
```

**Access:**
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501

---

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- Nginx (for reverse proxy)
- Supervisor (for process management)
- SSL certificate (Let's Encrypt recommended)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx supervisor git

# Install certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

### Step 2: Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash codebasegenius
sudo su - codebasegenius

# Clone repository
git clone <your-repo-url> /home/codebasegenius/app
cd /home/codebasegenius/app

# Setup backend
cd BE
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add production API key
```

### Step 3: Supervisor Configuration

Create `/etc/supervisor/conf.d/codebase-genius-backend.conf`:

```ini
[program:codebase-genius-backend]
command=/home/codebasegenius/app/BE/venv/bin/jac serve main.jac
directory=/home/codebasegenius/app/BE
user=codebasegenius
autostart=true
autorestart=true
stderr_logfile=/var/log/codebase-genius/backend.err.log
stdout_logfile=/var/log/codebase-genius/backend.out.log
environment=PATH="/home/codebasegenius/app/BE/venv/bin"
```

Create `/etc/supervisor/conf.d/codebase-genius-frontend.conf`:

```ini
[program:codebase-genius-frontend]
command=/home/codebasegenius/app/FE/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
directory=/home/codebasegenius/app/FE
user=codebasegenius
autostart=true
autorestart=true
stderr_logfile=/var/log/codebase-genius/frontend.err.log
stdout_logfile=/var/log/codebase-genius/frontend.out.log
```

```bash
# Create log directory
sudo mkdir -p /var/log/codebase-genius
sudo chown codebasegenius:codebasegenius /var/log/codebase-genius

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### Step 4: Nginx Configuration

Create `/etc/nginx/sites-available/codebase-genius`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for long-running operations
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
}

# Frontend UI
server {
    listen 80;
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/codebase-genius /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: SSL Configuration

```bash
# Obtain SSL certificates
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com

# Auto-renewal is configured by default
# Test renewal
sudo certbot renew --dry-run
```

---

## Docker Deployment

### Dockerfile for Backend

Create `BE/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create outputs directory
RUN mkdir -p outputs temp_repos

# Expose port
EXPOSE 8000

# Run application
CMD ["jac", "serve", "main.jac", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile for Frontend

Create `FE/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./BE
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./outputs:/app/outputs
      - ./temp_repos:/app/temp_repos
    restart: unless-stopped
    networks:
      - codebase-genius

  frontend:
    build:
      context: ./FE
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
    restart: unless-stopped
    networks:
      - codebase-genius

networks:
  codebase-genius:
    driver: bridge

volumes:
  outputs:
  temp_repos:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 20.04 LTS
   - Instance Type: t3.medium (minimum)
   - Storage: 30GB SSD
   - Security Group: Allow ports 80, 443, 8000, 8501

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Follow production deployment steps above
   ```

3. **Configure Elastic IP**
   - Allocate Elastic IP
   - Associate with EC2 instance
   - Update DNS records

#### Using ECS (Docker)

1. **Create ECR Repositories**
   ```bash
   aws ecr create-repository --repository-name codebase-genius-backend
   aws ecr create-repository --repository-name codebase-genius-frontend
   ```

2. **Push Images**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push
   docker build -t codebase-genius-backend ./BE
   docker tag codebase-genius-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/codebase-genius-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/codebase-genius-backend:latest
   ```

3. **Create ECS Task Definition and Service**

### Google Cloud Platform

#### Using Compute Engine

Similar to AWS EC2 deployment.

#### Using Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT-ID/codebase-genius-backend ./BE
gcloud run deploy codebase-genius-backend \
  --image gcr.io/PROJECT-ID/codebase-genius-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key

# Deploy frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/codebase-genius-frontend ./FE
gcloud run deploy codebase-genius-frontend \
  --image gcr.io/PROJECT-ID/codebase-genius-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Using App Service

```bash
# Create resource group
az group create --name CodebaseGeniusRG --location eastus

# Create App Service plan
az appservice plan create --name CodebaseGeniusPlan --resource-group CodebaseGeniusRG --sku B1 --is-linux

# Deploy backend
az webapp create --resource-group CodebaseGeniusRG --plan CodebaseGeniusPlan --name codebase-genius-backend --runtime "PYTHON|3.10"

# Deploy frontend
az webapp create --resource-group CodebaseGeniusRG --plan CodebaseGeniusPlan --name codebase-genius-frontend --runtime "PYTHON|3.10"
```

---

## Security Considerations

### 1. API Key Management

**Never hardcode API keys!**

```bash
# Use environment variables
export OPENAI_API_KEY=your-key

# Or use secret management services
# AWS Secrets Manager
# Azure Key Vault
# Google Secret Manager
```

### 2. Rate Limiting

Add rate limiting to prevent abuse:

```python
# In main.jac or middleware
# Implement rate limiting per IP
# Example: 10 requests per hour per IP
```

### 3. Input Validation

- Validate all GitHub URLs
- Sanitize user inputs
- Implement request size limits

### 4. HTTPS Only

- Always use HTTPS in production
- Redirect HTTP to HTTPS
- Use HSTS headers

### 5. Authentication (Optional)

For production, consider adding authentication:

```python
# JWT-based authentication
# API key authentication
# OAuth integration
```

### 6. Firewall Configuration

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## Monitoring and Maintenance

### 1. Logging

Configure comprehensive logging:

```python
# In main.jac
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Monitoring Tools

- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Log aggregation and analysis
- **Sentry**: Error tracking
- **UptimeRobot**: Uptime monitoring

### 3. Health Checks

Implement health check endpoints:

```jac
walker health_check {
    obj __specs__ {
        static has auth: bool = False;
    }
    
    can check with `root entry {
        report {
            "status": "healthy",
            "timestamp": get_current_datetime()
        };
    }
}
```

### 4. Backup Strategy

```bash
# Backup generated documentation
rsync -av outputs/ /backup/outputs/

# Backup configuration
cp .env /backup/.env.backup

# Automated daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

### 5. Update Strategy

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
sudo supervisorctl restart all

# Or with Docker
docker-compose pull
docker-compose up -d
```

---

## Performance Optimization

### 1. Caching

Implement caching for frequently accessed repositories:

```python
# Cache documentation for 24 hours
# Use Redis or in-memory cache
```

### 2. Queue System

For handling multiple requests:

```python
# Use Celery + Redis
# Queue documentation generation tasks
# Process asynchronously
```

### 3. Database

For production, consider adding a database:

```python
# PostgreSQL for storing:
# - Repository metadata
# - Generated documentation
# - User sessions
# - Analytics
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml with multiple backend instances
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of configuration
  
  nginx:
    image: nginx:latest
    # Load balancer configuration
```

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize code for better performance
- Use faster storage (SSD)

---

## Troubleshooting Deployment

### Issue: Service won't start

```bash
# Check logs
sudo supervisorctl tail -f codebase-genius-backend stderr
sudo journalctl -u nginx -f
```

### Issue: Permission errors

```bash
# Fix ownership
sudo chown -R codebasegenius:codebasegenius /home/codebasegenius/app
```

### Issue: Port conflicts

```bash
# Check what's using the port
sudo lsof -i :8000
# Kill the process or change port
```

---

## Deployment Checklist

Before going live:

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Error tracking configured
- [ ] Rate limiting implemented
- [ ] Documentation updated
- [ ] Health checks working
- [ ] Load testing completed

---

## Support and Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check error logs
- Monitor API usage
- Verify backups

**Weekly:**
- Review performance metrics
- Update dependencies
- Clean up temp files

**Monthly:**
- Security updates
- Performance optimization
- Feature updates

---

*Deployment Guide Complete! 🚀*
