# Deployment Guide
## Creative Pretest Analysis Platform

This guide covers deployment strategies for development, staging, and production environments.

---

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment (AWS)](#production-deployment-aws)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- FFmpeg

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In a separate terminal:
```bash
# Start Celery worker
celery -A workers.celery_app worker --loglevel=info --concurrency=2
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Start dev server
npm run dev
```

---

## Docker Deployment

### Using Docker Compose (Recommended for Development)

```bash
cd backend

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

Services started:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Celery Worker

### Building Individual Images

```bash
# Backend
cd backend
docker build -t creative-analysis-backend:latest .

# Frontend
cd frontend
docker build -t creative-analysis-frontend:latest .
```

### Running Containers

```bash
# Run backend
docker run -d \
  --name creative-backend \
  -p 8000:8000 \
  --env-file .env \
  creative-analysis-backend:latest

# Run frontend
docker run -d \
  --name creative-frontend \
  -p 3000:80 \
  creative-analysis-frontend:latest
```

---

## Production Deployment (AWS)

### Architecture Overview

```
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
    ├── ECS Service (Frontend - Nginx)
    └── ECS Service (Backend - FastAPI)
            ↓
        ECS Service (Celery Workers)
            ↓
        ├── RDS PostgreSQL
        ├── ElastiCache Redis
        └── S3 Bucket (Videos)
```

### Step 1: Set Up AWS Infrastructure

#### Create VPC and Subnets

```bash
# Using AWS CLI
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create public subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24

# Create private subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.3.0/24
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.4.0/24
```

#### Create RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier creative-analysis-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password <secure-password> \
  --allocated-storage 100 \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name creative-db-subnet \
  --multi-az \
  --backup-retention-period 7
```

#### Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id creative-redis \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name creative-redis-subnet \
  --security-group-ids sg-xxx
```

#### Create S3 Bucket

```bash
aws s3 mb s3://creative-analysis-videos
aws s3api put-bucket-versioning \
  --bucket creative-analysis-videos \
  --versioning-configuration Status=Enabled
```

### Step 2: Deploy to ECS

#### Create ECR Repositories

```bash
# Backend
aws ecr create-repository --repository-name creative-analysis-backend

# Frontend
aws ecr create-repository --repository-name creative-analysis-frontend
```

#### Build and Push Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t creative-analysis-backend:latest .
docker tag creative-analysis-backend:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/creative-analysis-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/creative-analysis-backend:latest

# Build and push frontend
cd frontend
docker build -t creative-analysis-frontend:latest .
docker tag creative-analysis-frontend:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/creative-analysis-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/creative-analysis-frontend:latest
```

#### Create ECS Task Definitions

**Backend Task Definition** (`backend-task-def.json`):

```json
{
  "family": "creative-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/creative-analysis-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:db-url"
        },
        {
          "name": "TWELVELABS_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:twelvelabs-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/creative-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
```

#### Create ECS Services

```bash
# Backend service
aws ecs create-service \
  --cluster creative-cluster \
  --service-name backend-service \
  --task-definition creative-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:xxx,containerName=backend,containerPort=8000"

# Celery worker service
aws ecs create-service \
  --cluster creative-cluster \
  --service-name celery-worker-service \
  --task-definition creative-celery-worker \
  --desired-count 3 \
  --launch-type FARGATE
```

### Step 3: Set Up Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name creative-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name creative-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --health-check-path /api/health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:xxx \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:xxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:xxx
```

### Step 4: Configure CloudFront

```bash
aws cloudfront create-distribution \
  --origin-domain-name creative-alb-xxx.us-east-1.elb.amazonaws.com \
  --default-root-object index.html
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (EKS, GKE, or self-hosted)
- kubectl configured
- Helm 3+

### Step 1: Create Namespace

```bash
kubectl create namespace creative-analysis
```

### Step 2: Create Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=url='postgresql://user:pass@host:5432/db' \
  --namespace creative-analysis

# API keys
kubectl create secret generic api-keys \
  --from-literal=twelvelabs='your-key' \
  --from-literal=elevenlabs='your-key' \
  --from-literal=openai='your-key' \
  --namespace creative-analysis

# AWS credentials
kubectl create secret generic aws-credentials \
  --from-literal=access-key-id='your-key' \
  --from-literal=secret-access-key='your-secret' \
  --namespace creative-analysis
```

### Step 3: Deploy PostgreSQL (using Helm)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install postgresql bitnami/postgresql \
  --namespace creative-analysis \
  --set auth.username=creative \
  --set auth.password=<secure-password> \
  --set auth.database=creative_analysis \
  --set primary.persistence.size=100Gi
```

### Step 4: Deploy Redis

```bash
helm install redis bitnami/redis \
  --namespace creative-analysis \
  --set auth.enabled=false \
  --set master.persistence.size=10Gi
```

### Step 5: Deploy Application

**Backend Deployment** (`k8s/backend-deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: creative-analysis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: <your-registry>/creative-analysis-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: TWELVELABS_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: twelvelabs
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: creative-analysis
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f k8s/backend-deployment.yaml
```

**Celery Worker Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
  namespace: creative-analysis
spec:
  replicas: 5
  selector:
    matchLabels:
      app: celery-worker
  template:
    metadata:
      labels:
        app: celery-worker
    spec:
      containers:
      - name: worker
        image: <your-registry>/creative-analysis-backend:latest
        command: ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### Step 6: Set Up Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: creative-ingress
  namespace: creative-analysis
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.creativeinsights.com
    secretName: creative-tls
  rules:
  - host: api.creativeinsights.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

---

## Environment Configuration

### Development
```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/creative_analysis
REDIS_URL=redis://localhost:6379/0
```

### Staging
```bash
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://user:pass@staging-db.xxx.rds.amazonaws.com:5432/creative_analysis
REDIS_URL=redis://staging-redis.xxx.cache.amazonaws.com:6379/0
```

### Production
```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db.xxx.rds.amazonaws.com:5432/creative_analysis
REDIS_URL=redis://prod-redis.xxx.cache.amazonaws.com:6379/0
```

---

## Monitoring & Logging

### Prometheus + Grafana

```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring --create-namespace

# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring
```

### Application Metrics

Backend exposes Prometheus metrics at `/metrics`:
- Request rate, latency, error rate
- Celery task duration and queue length
- Database connection pool usage

### Logging (ELK Stack)

```bash
# Install Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging --create-namespace

# Install Kibana
helm install kibana elastic/kibana \
  --namespace logging

# Install Filebeat
helm install filebeat elastic/filebeat \
  --namespace logging
```

---

## Backup & Recovery

### Database Backups

**Automated (RDS)**:
```bash
aws rds modify-db-instance \
  --db-instance-identifier creative-analysis-db \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"
```

**Manual Backup**:
```bash
pg_dump -h localhost -U postgres creative_analysis > backup_$(date +%Y%m%d).sql
```

**Restore**:
```bash
psql -h localhost -U postgres creative_analysis < backup_20250104.sql
```

### S3 Versioning

```bash
aws s3api put-bucket-versioning \
  --bucket creative-analysis-videos \
  --versioning-configuration Status=Enabled
```

---

## Scaling Strategies

### Horizontal Scaling

**ECS Auto Scaling**:
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/creative-cluster/backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/creative-cluster/backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

**Kubernetes HPA**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Troubleshooting

### Check Service Health

```bash
# ECS
aws ecs describe-services \
  --cluster creative-cluster \
  --services backend-service

# Kubernetes
kubectl get pods -n creative-analysis
kubectl logs -f <pod-name> -n creative-analysis
```

### Database Connection Issues

```bash
# Test connection
psql -h <db-host> -U <user> -d creative_analysis

# Check connection pool
kubectl exec -it <backend-pod> -- python -c "from core.database import engine; print(engine.pool.status())"
```

### Celery Worker Issues

```bash
# Check queue length
redis-cli -h <redis-host> LLEN celery

# Inspect tasks
celery -A workers.celery_app inspect active
```

---

## Security Checklist

- [ ] API keys in AWS Secrets Manager (not environment variables)
- [ ] HTTPS/TLS enabled on all endpoints
- [ ] Database encryption at rest enabled
- [ ] VPC security groups configured (least privilege)
- [ ] WAF rules configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Regular security patches applied

---

## Cost Optimization

- Use Spot Instances for Celery workers
- Enable S3 Intelligent-Tiering
- Use RDS Reserved Instances for production
- Implement CloudFront caching
- Set up auto-scaling to scale down during off-hours

---

**For production deployment support, contact: devops@creativeinsights.com**
