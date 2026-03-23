# Deployment Guide

## Smart Health Surveillance Platform - Production Deployment

This guide covers deploying the platform to production environments.

## Prerequisites

- Python 3.8+
- pip/conda package manager
- 2GB minimum RAM
- 500MB disk space
- Internet connection (for data updates)

## Deployment Options

### Option 1: Local Deployment (Development)

#### Setup Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd EarlyWarningSystem
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Verify Data Files**
```bash
python -c "import os; print(os.listdir('data/'))"
# Should show: ['disease_data.csv', 'weather_data.csv']
```

5. **Run Application**
```bash
streamlit run app.py
```

Access at: http://localhost:8501

---

### Option 2: Docker Deployment (Recommended)

#### Docker Setup

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Create .dockerignore**
```
__pycache__
*.pyc
.git
.gitignore
.env
venv/
.vscode/
.DS_Store
*.egg-info/
```

3. **Build Docker Image**
```bash
docker build -t health-surveillance:1.0 .
```

4. **Run Docker Container**
```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  health-surveillance:1.0
```

Access at: http://localhost:8501

---

### Option 3: Cloud Deployment (AWS/Heroku/GCP)

#### Heroku Deployment

1. **Install Heroku CLI**
```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli.heroku.com/install.sh | sh
```

2. **Create Procfile**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

3. **Create .gitignore**
```
venv/
__pycache__/
*.pyc
.env
models/trained_models/
.DS_Store
```

4. **Deploy**
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create health-surveillance-app

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

#### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - AMI: Ubuntu 20.04 LTS
   - Instance Type: t3.medium (2GB RAM)
   - Security Groups: Allow ports 8501, 22

2. **SSH into Instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install Dependencies**
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv
```

4. **Setup Application**
```bash
git clone <repository-url>
cd EarlyWarningSystem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Run with Supervisor**

Create `/etc/supervisor/conf.d/health-surveillance.conf`:
```
[program:health-surveillance]
directory=/home/ubuntu/EarlyWarningSystem
command=/home/ubuntu/EarlyWarningSystem/venv/bin/streamlit run app.py --server.port=8501
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/health-surveillance.err.log
stdout_logfile=/var/log/health-surveillance.out.log
```

Start service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start health-surveillance
```

#### Google Cloud Platform (GCP)

1. **Install Google Cloud SDK**
```bash
curl https://sdk.cloud.google.com | bash
```

2. **Initialize GCP**
```bash
gcloud init
gcloud config set project your-project-id
```

3. **Deploy to Cloud Run**
```bash
gcloud run deploy health-surveillance \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Production Configuration

### Environment Variables

Create `.env` file:
```env
# Application
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Data
DATA_PATH=/data
MODEL_PATH=/models

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/health_db

# API (optional)
API_KEY=your-api-key
API_SECRET=your-api-secret

# Security
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Email Alerts (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=alerts@example.com
SENDER_PASSWORD=your-password
```

### Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name health-surveillance.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name health-surveillance.com;

    # SSL Certificate
    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Proxy to Streamlit
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

---

## Database Setup (Optional)

### PostgreSQL Setup

1. **Install PostgreSQL**
```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib

# Mac
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

2. **Create Database**
```bash
createdb health_surveillance
```

3. **Create Tables**
```sql
CREATE TABLE disease_cases (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100),
    disease_type VARCHAR(50),
    cases_count INTEGER,
    date_reported DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE health_alerts (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100),
    alert_level VARCHAR(20),
    risk_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE community_reports (
    id SERIAL PRIMARY KEY,
    reporter_id VARCHAR(100),
    location VARCHAR(100),
    symptoms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Monitoring & Logging

### Application Logging

Create `logging_config.py`:
```python
import logging
import logging.handlers
import os

def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    # Console handler
    ch = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

### Monitoring with Prometheus (Optional)

1. **Install Prometheus**
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.30.0/prometheus-2.30.0.linux-amd64.tar.gz
tar xvfz prometheus-2.30.0.linux-amd64.tar.gz
```

2. **Configure Metrics Export**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Create metrics
alerts_generated = Counter('alerts_generated', 'Alerts generated', ['level'])
predictions_made = Counter('predictions_made', 'Predictions made')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
```

---

## Backup & Recovery

### Automated Backup

1. **Backup Script** (`backup.sh`)
```bash
#!/bin/bash

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup data
tar -czf $BACKUP_DIR/data_$TIMESTAMP.tar.gz data/

# Backup models
tar -czf $BACKUP_DIR/models_$TIMESTAMP.tar.gz models/trained_models/

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
```

2. **Schedule Backup**
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh  # Run daily at 2 AM
```

---

## Performance Tuning

### Application Optimization

1. **Enable Caching**
```python
@st.cache_resource
def load_models():
    # Load models once
    return models

@st.cache_data
def load_data():
    # Cache data
    return data
```

2. **Optimize Data Loading**
```python
# Use dtype specification
dtypes = {
    'Date': 'object',
    'Temperature_C': 'float32',
    'Humidity_%': 'int8'
}
df = pd.read_csv('data.csv', dtype=dtypes)
```

### System Tuning

```bash
# Increase file descriptors
ulimit -n 65536

# Optimize TCP
sysctl -w net.ipv4.tcp_max_syn_backlog=2048
sysctl -w net.ipv4.tcp_fin_timeout=30
```

---

## Security Considerations

### HTTPS/SSL Setup

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

### Authentication (Optional)

Add Streamlit authentication:
```python
import streamlit as st
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if username == "admin" and hash_password(password) == stored_hash:
    st.success("Logged in!")
else:
    st.error("Invalid credentials")
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
limiter.limit("100/minute")(predict_endpoint)
```

---

## Health Checks

### Endpoint Health Check

```python
@app.route('/health')
def health_check():
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': len(predictor.models),
        'data_available': os.path.exists('data/')
    }
```

### Scheduled Health Monitoring

```python
import schedule
import requests

def check_health():
    try:
        response = requests.get('http://localhost:8501/health')
        if response.status_code == 200:
            print("Application healthy")
        else:
            print("Application unhealthy")
    except:
        print("Application unreachable")

schedule.every(5).minutes.do(check_health)
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>
```

### Memory Issues
```bash
# Monitor memory
watch -n 1 'free -h'

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Data Not Loading
```bash
# Check permissions
ls -la data/

# Fix permissions
chmod 644 data/*.csv

# Verify data integrity
python -c "import pandas as pd; pd.read_csv('data/weather_data.csv').head()"
```

---

## Maintenance Tasks

### Daily Tasks
- Monitor logs for errors
- Check application health
- Verify data updates

### Weekly Tasks
- Review alert trends
- Update disease data
- Backup system

### Monthly Tasks
- Retrain models with new data
- Review performance metrics
- Update documentation

---

## Version Control

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request
# After review and merge:
git checkout main
git pull origin main
git tag v1.0.1
git push origin v1.0.1
```

---

## Support & Documentation

- **Documentation**: See README.md
- **Issues**: Report via GitHub Issues
- **Contact**: health.surveillance@example.com

---

**Deployment Status**: Ready for Production
**Last Updated**: February 2026
