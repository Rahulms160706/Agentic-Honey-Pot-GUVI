# Deployment Guide - Agentic Honey-Pot System

This guide covers various deployment options for the Agentic Honey-Pot system.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)

---

## Local Development

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Step 1: Setup Environment

```bash
# Create project directory
mkdir agentic-honeypot
cd agentic-honeypot

# Copy all project files to this directory

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env file and set your API key
nano .env
```

Or edit `main.py` directly:
```python
API_KEY = "YOUR_SECRET_API_KEY_12345"  # Change this!
```

### Step 3: Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### Step 4: Test the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with a scam message
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_SECRET_API_KEY_12345" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify now!",
      "timestamp": "2026-01-29T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }'
```

---

## Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Step 1: Build Docker Image

```bash
# Build the image
docker build -t agentic-honeypot:latest .

# Verify image was created
docker images | grep agentic-honeypot
```

### Step 2: Run with Docker Compose

```bash
# Start the service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Step 3: Test the Dockerized API

```bash
curl http://localhost:8000/health
```

### Docker Commands Reference

```bash
# Build without cache
docker-compose build --no-cache

# Restart service
docker-compose restart

# Remove all containers and volumes
docker-compose down -v

# Scale service (multiple instances)
docker-compose up -d --scale honeypot-api=3

# Execute command in container
docker-compose exec honeypot-api /bin/bash
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04, t3.medium)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# 4. Clone your repository
git clone <your-repo>
cd agentic-honeypot

# 5. Configure environment
cp .env.example .env
nano .env

# 6. Start service
docker-compose up -d

# 7. Configure security group
# Allow inbound traffic on port 8000
```

#### Option 2: AWS ECS (Elastic Container Service)

```bash
# 1. Push image to ECR
aws ecr create-repository --repository-name agentic-honeypot
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag agentic-honeypot:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/agentic-honeypot:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/agentic-honeypot:latest

# 2. Create ECS task definition (use AWS Console or CLI)
# 3. Create ECS service
# 4. Configure load balancer
# 5. Set up CloudWatch logs
```

#### Option 3: AWS Lambda (Serverless)

Create `lambda_handler.py`:
```python
import json
from mangum import Mangum
from main import app

handler = Mangum(app)
```

Deploy:
```bash
# Install serverless framework
npm install -g serverless

# Create serverless.yml
# Deploy
serverless deploy
```

### Google Cloud Platform (GCP)

#### GCP Cloud Run

```bash
# 1. Install gcloud CLI
# 2. Authenticate
gcloud auth login

# 3. Build and push to Container Registry
gcloud builds submit --tag gcr.io/<project-id>/agentic-honeypot

# 4. Deploy to Cloud Run
gcloud run deploy agentic-honeypot \
  --image gcr.io/<project-id>/agentic-honeypot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=your-secret-key

# 5. Get the service URL
gcloud run services describe agentic-honeypot --region us-central1
```

### Microsoft Azure

#### Azure Container Instances

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name honeypot-rg --location eastus

# 3. Create container registry
az acr create --resource-group honeypot-rg \
  --name honeypotregistry --sku Basic

# 4. Build and push image
az acr build --registry honeypotregistry \
  --image agentic-honeypot:latest .

# 5. Deploy container
az container create \
  --resource-group honeypot-rg \
  --name honeypot-api \
  --image honeypotregistry.azurecr.io/agentic-honeypot:latest \
  --dns-name-label honeypot-api \
  --ports 8000 \
  --environment-variables API_KEY=your-secret-key
```

---

## Production Considerations

### 1. Environment Variables

Never hardcode secrets. Use environment variables:

```python
import os
API_KEY = os.getenv("API_KEY", "default-key")
```

### 2. Database Integration

For production, replace in-memory sessions with a database:

```python
# Use Redis for session storage
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Or use PostgreSQL/MongoDB
```

### 3. Load Balancing

```nginx
# nginx.conf
upstream honeypot_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.honeypot.com;

    location / {
        proxy_pass http://honeypot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL/TLS Configuration

```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.honeypot.com
```

### 5. Monitoring & Logging

```python
# Add structured logging
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        })

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
```

### 6. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/message")
@limiter.limit("10/minute")
async def handle_message(request: Request, ...):
    ...
```

### 7. Health Checks

```python
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    # Check if dependencies are ready
    try:
        # Test database connection
        # Test external APIs
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="Not ready")
```

### 8. Metrics & Observability

```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 9. Security Headers

```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.honeypot.com"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 10. Backup & Recovery

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U user database > backup_$DATE.sql

# Automated backups with cron
0 2 * * * /path/to/backup.sh
```

---

## Performance Optimization

### 1. Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

@app.post("/api/message")
async def handle_message(...):
    # Run heavy tasks in background
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, heavy_computation)
```

### 2. Caching

```python
from functools import lru_cache
import redis

redis_cache = redis.Redis()

@lru_cache(maxsize=1000)
def detect_scam(message):
    # Cached scam detection
    pass
```

### 3. Connection Pooling

```python
import aiohttp

async def make_external_request():
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
```

---

## Monitoring Dashboard

### Setup Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **Docker image not building**
   ```bash
   # Clear Docker cache
   docker system prune -a
   docker-compose build --no-cache
   ```

3. **API Key not working**
   ```bash
   # Verify environment variable
   echo $API_KEY
   # Check headers in request
   curl -v -H "x-api-key: YOUR_KEY" http://localhost:8000/health
   ```

4. **Callback failing**
   ```bash
   # Check GUVI endpoint is accessible
   curl -X POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

---

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Review documentation: `README.md`
- Test endpoints: `test_scenarios.py`
