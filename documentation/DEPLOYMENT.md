# CampaignCraft - Deployment Guide

## 🚀 Production Deployment

This guide covers deploying CampaignCraft to production environments.

---

## 📋 Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] API keys added for AI providers
- [ ] Database configured (if using persistence)
- [ ] HTTPS/SSL certificates ready
- [ ] Domain name ready
- [ ] Backend tested thoroughly
- [ ] Frontend built for production
- [ ] Backup plan in place

---

## 🔧 Environment Setup

### Production `.env`

```env
# AI Provider - Use real provider, not mock
AI_PROVIDER=gemini

# API Keys - Use production keys only
GEMINI_API_KEY=xxx-production-key-xxx
OPENAI_API_KEY=xxx-production-key-xxx
ANTHROPIC_API_KEY=xxx-production-key-xxx

# Database - Use PostgreSQL for production
DATABASE_URL=postgresql://user:password@db.example.com:5432/campaigncraft

# Logging
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-for-jwt-tokens
ALLOWED_ORIGINS=https://yourdomain.com

# Frontend
FRONTEND_URL=https://yourdomain.com
```

---

## 🏠 Option 1: Deploy to Heroku

### Backend Setup

1. Create `Procfile` in `backend/`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Create `runtime.txt`:

```
python-3.11.5
```

3. Deploy:

```bash
cd backend
heroku login
heroku create campaigncraft-api
heroku config:set AI_PROVIDER=gemini
heroku config:set GEMINI_API_KEY=xxx
git push heroku main
```

### Frontend Setup

1. Create `netlify.toml` in `frontend/`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. Update `frontend/src/App.jsx` API URL:

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

3. Deploy to Netlify:

```bash
cd frontend
npm run build
# Drag & drop dist folder to Netlify
```

---

## ☁️ Option 2: Deploy to AWS

### Backend (EC2 + RDS)

1. Launch EC2 instance (Ubuntu 22.04, t3.medium)

2. SSH into instance:

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. Setup backend:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & dependencies
sudo apt install -y python3.11 python3-pip python3-venv

# Clone project
git clone https://github.com/yourusername/campaign-craft.git
cd campaign-craft/backend

# Setup venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env
nano .env  # Add production settings

# Start with gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -b 0.0.0.0:8000
```

4. Setup systemd service:

```bash
sudo nano /etc/systemd/system/campaigncraft.service
```

```ini
[Unit]
Description=CampaignCraft API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/campaign-craft/backend
Environment="PATH=/home/ubuntu/campaign-craft/backend/venv/bin"
ExecStart=/home/ubuntu/campaign-craft/backend/venv/bin/gunicorn app.main:app -w 4 -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable campaigncraft
sudo systemctl start campaigncraft
```

5. Setup nginx reverse proxy:

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/campaigncraft
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/campaigncraft /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Frontend (S3 + CloudFront)

1. Build frontend:

```bash
cd frontend
npm run build
```

2. Create S3 bucket:

```bash
aws s3 mb s3://campaign-craft-frontend
aws s3 sync dist/ s3://campaign-craft-frontend --delete
```

3. Setup CloudFront distribution pointing to S3

4. Update frontend API URL in build:

```bash
REACT_APP_API_URL=https://api.yourdomain.com npm run build
```

---

## 🐳 Option 3: Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AI_PROVIDER=gemini
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/campaigncraft
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=campaigncraft
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

### Deploy with Docker:

```bash
docker-compose up -d
```

---

## 🔐 SSL/HTTPS Setup

### Option 1: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 2: AWS Certificate Manager

1. Request certificate in ACM console
2. Validate domain
3. Attach to ALB/CloudFront

---

## 📊 Database Setup (PostgreSQL)

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE campaigncraft;

# Create tables (when persistence is implemented)
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    topic VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE use_cases (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    title VARCHAR(255),
    summary TEXT,
    value_prop VARCHAR(255)
);

CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    name VARCHAR(255),
    role VARCHAR(255),
    company VARCHAR(255),
    contact_link VARCHAR(500)
);

CREATE TABLE proposals (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    type VARCHAR(50),
    content TEXT
);
```

---

## 🔍 Monitoring & Logging

### Application Monitoring

```bash
# Install PM2 for process management
npm install -g pm2

# Create PM2 config
pm2 start "uvicorn app.main:app" --name "campaigncraft-api"
pm2 start "npm run preview" --name "campaigncraft-frontend"

# Setup logs
pm2 logs campaigncraft-api
```

### CloudWatch Logs (AWS)

```bash
# Install CloudWatch agent
sudo wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

---

## 🚨 Security Best Practices

1. **Environment Variables**
   - Never commit `.env` to version control
   - Use AWS Secrets Manager or similar
   - Rotate API keys regularly

2. **Database**
   - Enable SSL connections
   - Use strong passwords
   - Enable automated backups
   - Enable encryption at rest

3. **Frontend**
   - Enable CORS properly (don't use `*`)
   - Use HTTPS only
   - Set security headers

4. **Backend**
   - Enable rate limiting
   - Validate all inputs
   - Use HTTPS only
   - Enable CORS headers properly
   - Add request signing/verification

5. **Infrastructure**
   - Enable firewalls
   - Restrict SSH access
   - Enable DDoS protection
   - Setup VPN for admin access

---

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer** (AWS ALB / nginx)
   ```
   Frontend → CloudFront → ALB
   Backend → ALB → Multiple EC2 instances
   ```

2. **Database** (PostgreSQL RDS)
   - Read replicas for scaling reads
   - Connection pooling (PgBouncer)

3. **Cache** (Redis)
   - Cache frequently generated campaigns
   - Cache agent responses

### Vertical Scaling

- Upgrade instance types as traffic grows
- Monitor CPU, memory, disk usage
- Set up alerts for resource constraints

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Backend
        run: |
          # Deploy backend
          
      - name: Deploy Frontend
        run: |
          # Build and deploy frontend
          
      - name: Run Tests
        run: |
          # Run tests
```

---

## 🆘 Disaster Recovery

### Backup Strategy

1. **Database Backups**
   ```bash
   # Daily automated backups
   pg_dump -U user campaigncraft > backup-$(date +%Y%m%d).sql
   ```

2. **Application Backups**
   ```bash
   # Version control (GitHub)
   git push origin main
   ```

3. **Configuration Backups**
   - Keep `.env.prod` in AWS Secrets Manager
   - Document all infrastructure setup

### Recovery Procedure

1. Restore from database backup
2. Redeploy application from version control
3. Update DNS if needed
4. Verify functionality

---

## 📞 Support & Monitoring

- Setup monitoring dashboards (CloudWatch, Datadog)
- Setup alerts for errors and performance issues
- Keep application logs for debugging
- Regular security audits
- Performance testing under load

---

## 🎓 Resources

- [Heroku Deployment Guide](https://devcenter.heroku.com)
- [AWS Deployment Guide](https://aws.amazon.com/getting-started)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/current/admin.html)

---

**Ready to deploy CampaignCraft to production!** 🚀
