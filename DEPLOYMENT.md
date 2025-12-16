# Production Deployment Guide

> Comprehensive guide for deploying Warehouse Capacity Planner to production

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Security Checklist](#security-checklist)
5. [Environment Variables](#environment-variables)
6. [Docker Deployment](#docker-deployment)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Database Management](#database-management)
9. [Monitoring & Logging](#monitoring--logging)
10. [Operational Procedures](#operational-procedures)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Overview

This guide covers deploying the Warehouse Capacity Planner application to a production environment using Docker Compose. The application consists of:

- **Frontend**: React SPA served by nginx
- **Backend**: Flask API with gunicorn
- **Database**: PostgreSQL 16
- **Reverse Proxy**: nginx with SSL/TLS termination

**Target Audience**: DevOps engineers, system administrators, developers responsible for deployment.

---

## Prerequisites

### Required Software

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Domain name** pointed to your server
- **Server** with at least:
  - 2 CPU cores
  - 4GB RAM
  - 20GB disk space
  - Ubuntu 20.04+ or similar Linux distribution

### Required Access

- SSH access to production server
- Domain DNS configuration access
- SSL certificate (Let's Encrypt recommended)

---

## Quick Start

**TL;DR** for experienced users:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/warehouse-capacity-planner.git
cd warehouse-capacity-planner

# 2. Create production environment file
cp .env.example .env
# Edit .env with production values

# 3. Generate secret key
python3 -c "import secrets; print(secrets.token_hex(32))" >> .env

# 4. Build and start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Run database migrations
docker exec warehouse-planner-backend-prod flask db upgrade

# 6. Verify deployment
curl https://yourdomain.com/health
```

---

## Security Checklist

Complete this checklist **before** deploying to production:

### Critical Security Items

- [ ] **SECRET_KEY**: Generated using cryptographically secure method
- [ ] **Database Password**: Strong password (16+ characters, mixed case, numbers, symbols)
- [ ] **CORS Origins**: Set to your production domain only (no wildcards)
- [ ] **SSL/TLS**: Valid certificate installed and configured
- [ ] **Firewall**: Only ports 80, 443, and SSH exposed
- [ ] **SSH**: Key-based authentication enabled, password auth disabled
- [ ] **Database**: Not exposed to public internet (internal network only)
- [ ] **.env file**: Permissions set to 600 (readable only by owner)
- [ ] **Default Credentials**: All changed from development defaults

### Recommended Security Items

- [ ] **Rate Limiting**: Enabled in nginx configuration
- [ ] **Security Headers**: HSTS, X-Frame-Options, CSP configured
- [ ] **Backups**: Automated database backups configured
- [ ] **Monitoring**: Error tracking and uptime monitoring enabled
- [ ] **Updates**: System packages and Docker images up to date
- [ ] **Logs**: Centralized logging configured
- [ ] **File Upload Limits**: Appropriate limits configured (10MB default)

---

## Environment Variables

### Complete Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | ✅ Yes | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | ✅ Yes | - | PostgreSQL password (strong password required) |
| `POSTGRES_DB` | ✅ Yes | - | PostgreSQL database name |
| `SECRET_KEY` | ✅ Yes | - | Flask secret key (use `secrets.token_hex(32)`) |
| `FLASK_ENV` | ✅ Yes | `production` | Flask environment (`production` for prod) |
| `DATABASE_URL` | ✅ Yes | (auto-generated) | Full PostgreSQL connection string |
| `CORS_ORIGINS` | ✅ Yes | - | Comma-separated allowed origins |
| `VITE_API_URL` | No | `/api/v1` | API endpoint URL (use relative path) |
| `MAX_UPLOAD_SIZE` | No | `10485760` | Max file upload size in bytes (10MB default) |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `SENTRY_DSN` | No | - | Sentry error tracking DSN (optional) |

### Example `.env` File

```bash
# Database Configuration
POSTGRES_USER=warehouse_prod_user
POSTGRES_PASSWORD=YourStrongPasswordHere123!@#
POSTGRES_DB=warehouse_planner_prod

# Backend Configuration
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
FLASK_ENV=production
DATABASE_URL=postgresql://warehouse_prod_user:YourStrongPasswordHere123!@#@db:5432/warehouse_planner_prod
CORS_ORIGINS=https://yourdomain.com

# Frontend Configuration
VITE_API_URL=/api/v1

# Optional Configuration
MAX_UPLOAD_SIZE=10485760
LOG_LEVEL=INFO
```

### Generating Secure Values

**SECRET_KEY Generation:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Strong Password Generation:**
```bash
openssl rand -base64 32
```

---

## Docker Deployment

### Production Docker Compose

The production configuration (`docker-compose.prod.yml`) includes:

- **Separate networks** for frontend/backend isolation
- **Health checks** for all services
- **Restart policies** (unless-stopped)
- **Logging configuration** with rotation
- **Volume management** for data persistence

### Deployment Steps

#### 1. Prepare Environment

```bash
# Create directories
mkdir -p logs/backend logs/nginx backups ssl

# Set permissions
chmod 700 backups
chmod 600 .env

# Review configuration
cat docker-compose.prod.yml
```

#### 2. Build Images

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Or build specific service
docker-compose -f docker-compose.prod.yml build backend
```

#### 3. Start Services

```bash
# Start all services in detached mode
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

#### 4. Initialize Database

```bash
# Run migrations
docker exec warehouse-planner-backend-prod flask db upgrade

# Verify database connection
docker exec warehouse-planner-backend-prod flask shell
>>> from app.extensions import db
>>> db.engine.execute('SELECT 1').scalar()
```

#### 5. Verify Deployment

```bash
# Check health endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/api/v1/warehouses

# Check logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=100

# Verify all containers are running
docker ps
```

### Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (DESTRUCTIVE)
docker-compose -f docker-compose.prod.yml down -v
```

---

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

#### 1. Install Certbot

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

#### 2. Obtain Certificate

```bash
# Stop nginx if running
docker-compose -f docker-compose.prod.yml stop nginx

# Obtain certificate
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos
```

#### 3. Copy Certificates

```bash
# Copy to ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/

# Set permissions
sudo chmod 644 ./ssl/fullchain.pem
sudo chmod 600 ./ssl/privkey.pem
sudo chown $USER:$USER ./ssl/*
```

#### 4. Configure nginx

The production nginx configuration (`docker/nginx-prod.conf`) includes:

- HTTP to HTTPS redirect
- TLS 1.2 and 1.3 support
- Strong cipher suites
- HSTS header (max-age 1 year)
- Security headers

#### 5. Restart nginx

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

#### 6. Auto-Renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e

# Add this line:
0 0 1 * * certbot renew --quiet && docker-compose -f /path/to/docker-compose.prod.yml restart nginx
```

---

## Database Management

### Backup Strategy

#### Automated Daily Backups

Create backup script at `scripts/backup-database.sh`:

```bash
#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="warehouse_planner_backup_${TIMESTAMP}.sql"

echo "Starting database backup..."
docker exec warehouse-planner-db-prod pg_dump \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB} \
    > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Keep only last 30 days
find ${BACKUP_DIR} -name "warehouse_planner_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

Make executable:
```bash
chmod +x scripts/backup-database.sh
```

#### Cron Job Setup

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/warehouse-capacity-planner && ./scripts/backup-database.sh >> logs/backup.log 2>&1
```

### Database Restore

Create restore script at `scripts/restore-database.sh`:

```bash
#!/bin/bash
set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore-database.sh <backup_file.sql.gz>"
    exit 1
fi

echo "Restoring from: $BACKUP_FILE"
gunzip -c $BACKUP_FILE | docker exec -i warehouse-planner-db-prod psql \
    -U ${POSTGRES_USER} \
    -d ${POSTGRES_DB}

echo "Restore completed successfully"
```

Usage:
```bash
./scripts/restore-database.sh backups/warehouse_planner_backup_20250116_020000.sql.gz
```

### Database Migrations

```bash
# View current migration version
docker exec warehouse-planner-backend-prod flask db current

# Upgrade to latest
docker exec warehouse-planner-backend-prod flask db upgrade

# Downgrade one version
docker exec warehouse-planner-backend-prod flask db downgrade
```

---

## Monitoring & Logging

### Application Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# Follow specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Health Checks

The application includes health check endpoints:

- **Main**: `https://yourdomain.com/health`
- **API**: `https://yourdomain.com/api/v1/health` (to be added)
- **Database**: Checked via API health endpoint

### Recommended Monitoring Tools

#### Uptime Monitoring
- **UptimeRobot** (free tier available)
- **Pingdom**
- **StatusCake**

#### Error Tracking
- **Sentry** (recommended)
  ```bash
  # Add to .env
  SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
  ```

#### Log Aggregation
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**

#### Application Monitoring
- **New Relic**
- **Datadog APM**
- **Prometheus + Grafana**

### Log Rotation

Docker logging is configured in `docker-compose.prod.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## Operational Procedures

### Deployment Procedure

```bash
# 1. Pull latest code
git pull origin main

# 2. Review changes
git log --oneline -10

# 3. Backup database
./scripts/backup-database.sh

# 4. Build new images
docker-compose -f docker-compose.prod.yml build

# 5. Stop services
docker-compose -f docker-compose.prod.yml down

# 6. Start with new images
docker-compose -f docker-compose.prod.yml up -d

# 7. Run migrations
docker exec warehouse-planner-backend-prod flask db upgrade

# 8. Verify health
curl https://yourdomain.com/health
curl https://yourdomain.com/api/v1/health

# 9. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

### Rollback Procedure

```bash
# 1. Stop current containers
docker-compose -f docker-compose.prod.yml down

# 2. Restore database backup
./scripts/restore-database.sh backups/warehouse_planner_backup_YYYYMMDD_HHMMSS.sql.gz

# 3. Checkout previous version
git checkout <previous-commit-hash>

# 4. Rebuild and start
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://yourdomain.com/health
```

### Scaling Considerations

#### Horizontal Scaling (Multiple Backend Instances)

Update `docker-compose.prod.yml`:

```yaml
backend:
  # ... existing configuration
  deploy:
    replicas: 3  # Run 3 backend instances
```

nginx will automatically load balance across instances.

#### Database Scaling

- **Connection Pooling**: Configured in Flask SQLAlchemy
- **Read Replicas**: For read-heavy workloads
- **Vertical Scaling**: Increase PostgreSQL resources

#### File Storage Scaling

- **Shared Volume**: Use NFS or similar for multi-host deployments
- **S3-Compatible Storage**: For cloud deployments (e.g., AWS S3, MinIO)

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptom**: Backend can't connect to database

**Solutions**:
```bash
# Check database is running
docker ps | grep db

# Check database logs
docker logs warehouse-planner-db-prod

# Verify DATABASE_URL in .env
echo $DATABASE_URL

# Test connection from backend
docker exec warehouse-planner-backend-prod flask shell
>>> from app.extensions import db
>>> db.engine.execute('SELECT 1').scalar()
```

#### 2. File Upload Failures

**Symptom**: File uploads fail or timeout

**Solutions**:
- Check `MAX_UPLOAD_SIZE` in `.env`
- Verify nginx `client_max_body_size` in `nginx-prod.conf`
- Check upload directory permissions
- Review backend logs for specific errors

#### 3. SSL Certificate Issues

**Symptom**: HTTPS not working or certificate warnings

**Solutions**:
```bash
# Verify certificate files exist
ls -la ssl/

# Check certificate validity
openssl x509 -in ssl/fullchain.pem -text -noout

# Verify nginx configuration
docker exec warehouse-planner-nginx nginx -t

# Check nginx logs
docker logs warehouse-planner-nginx
```

#### 4. High Memory Usage

**Symptom**: Server running out of memory

**Solutions**:
```bash
# Check container resource usage
docker stats

# Reduce gunicorn workers (backend/Dockerfile)
# workers = (2 * cpu_count) + 1  # Adjust this

# Add memory limits to docker-compose.prod.yml
services:
  backend:
    mem_limit: 1g
```

#### 5. Slow Response Times

**Symptom**: API responses are slow

**Solutions**:
- Enable query logging to identify slow database queries
- Add database indexes for frequently queried fields
- Enable caching (Redis) for expensive computations
- Check if database needs vacuuming: `VACUUM ANALYZE;`

---

## FAQ

### General

**Q: Can I use a different database?**
A: PostgreSQL is recommended for production. SQLite is only for development.

**Q: How do I upgrade to a new version?**
A: Follow the deployment procedure above. Always backup first!

**Q: What are the minimum server requirements?**
A: 2 CPU cores, 4GB RAM, 20GB disk. Requirements increase with usage.

### Security

**Q: How do I change the SECRET_KEY?**
A: Generate a new key, update `.env`, restart services. Note: This invalidates existing sessions.

**Q: Should I expose the database port?**
A: No. Keep the database on an internal network only.

**Q: How often should I update Docker images?**
A: Monthly for security patches. Test updates in staging first.

### Backup & Recovery

**Q: How long should I keep backups?**
A: Minimum 30 days. Adjust based on compliance requirements.

**Q: Can I restore to a different server?**
A: Yes. Just ensure the new server has the same environment variables.

**Q: What if I lose my .env file?**
A: You'll need to recreate it. SECRET_KEY loss will invalidate sessions. Database password must match what's in PostgreSQL.

### Performance

**Q: How many concurrent users can the app handle?**
A: Depends on server resources. Default configuration: ~100 concurrent users.

**Q: Should I use a CDN?**
A: Recommended for global users. Can significantly improve frontend load times.

**Q: How do I optimize the database?**
A: Regular `VACUUM ANALYZE`, appropriate indexes, and connection pooling.

---

## Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **nginx Documentation**: https://nginx.org/en/docs/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Let's Encrypt**: https://letsencrypt.org/getting-started/

---

## Support

For issues or questions:
1. Check this documentation
2. Review application logs
3. Check [GitHub Issues](https://github.com/yourusername/warehouse-capacity-planner/issues)
4. Create a new issue with logs and error messages

---

**Last Updated**: January 2025
**Version**: 1.0
