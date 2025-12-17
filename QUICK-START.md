# Quick Start Deployment Guide

> Deploy Warehouse Capacity Planner to production in under 30 minutes using automated scripts

## What You Need

Before starting, make sure you have:

- [ ] **Linux server** (Ubuntu 20.04+) with root/sudo access
  - Minimum: 2 CPU cores, 4GB RAM, 20GB disk
  - Providers: DigitalOcean, Linode, AWS EC2, Vultr, etc.
- [ ] **Domain name** purchased and configured
  - DNS A record pointing to your server IP
- [ ] **Email address** for SSL certificate notifications
- [ ] **SSH access** to your server

## Deployment Methods

Choose the method that works best for you:

### Method 1: Fully Automated (Recommended)

Run this **single command** on your server to deploy everything:

```bash
curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/quick-deploy.sh | bash
```

This will:
1. Set up the server (Docker, firewall, etc.)
2. Clone the repository
3. Configure environment
4. Set up SSL certificates
5. Deploy the application
6. Run health checks

**Total time: ~20-30 minutes** (mostly waiting for Docker builds)

---

### Method 2: Step-by-Step Automated

For more control, run scripts individually:

#### Step 1: SSH into your server

```bash
ssh root@your-server-ip
```

#### Step 2: Set up server (5-10 minutes)

```bash
curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/setup-server.sh | bash
```

This installs Docker, configures firewall, installs Certbot, and sets up Fail2Ban.

**After this step completes, log out and back in to apply Docker group permissions.**

#### Step 3: Clone repository

```bash
cd ~
git clone https://github.com/bryanstanleyyy/warehouse-capacity-planner.git
cd warehouse-capacity-planner
```

#### Step 4: Configure environment (2 minutes)

```bash
bash scripts/configure-env.sh
```

You'll be prompted for:
- Domain name (e.g., `example.com`)
- Email address
- Database username (default: `warehouse_prod_user`)
- Database name (default: `warehouse_planner_prod`)
- Max upload size (default: 10MB)
- Log level (default: INFO)
- Sentry DSN (optional)

Secure secrets are **automatically generated**.

#### Step 5: Set up SSL certificates (2-3 minutes)

```bash
sudo bash scripts/setup-ssl.sh
```

This obtains Let's Encrypt certificates and configures auto-renewal.

**Note:** Domain DNS must be pointing to your server before this step.

#### Step 6: Deploy application (10-15 minutes)

```bash
bash scripts/deploy.sh
```

This builds Docker images, starts services, runs migrations, and verifies deployment.

#### Step 7: Verify deployment (1 minute)

```bash
bash scripts/health-check.sh
```

This runs comprehensive health checks and shows system status.

**Total time: ~20-30 minutes**

---

### Method 3: Manual Deployment

Follow the comprehensive step-by-step guide in the [deployment plan](C:\Users\bryan\.claude\plans\humming-knitting-horizon.md) or [DEPLOYMENT.md](DEPLOYMENT.md).

---

## After Deployment

### 1. Access Your Application

Open your browser and go to:
```
https://yourdomain.com
```

You should see the Warehouse Capacity Planner login screen with a valid SSL certificate.

### 2. Test Core Functionality

- Create a warehouse with multiple zones
- Upload inventory from Excel file
- Run an allocation analysis
- Generate reports

### 3. Set Up Automated Backups

```bash
crontab -e
```

Add this line for daily backups at 2 AM:
```
0 2 * * * cd /home/deploy/warehouse-capacity-planner && ./scripts/backup-database.sh >> logs/backup.log 2>&1
```

### 4. Set Up Monitoring (Recommended)

**UptimeRobot (Free):**
1. Sign up at https://uptimerobot.com
2. Add HTTP(S) monitor for `https://yourdomain.com/health`
3. Configure email alerts

**Sentry Error Tracking:**
1. Sign up at https://sentry.io
2. Create a new project
3. Add DSN to `.env`:
   ```bash
   nano .env
   # Add: SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```
4. Restart backend:
   ```bash
   docker compose -f docker-compose.prod.yml restart backend
   ```

---

## Common Commands

### View Logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

### Restart Services
```bash
# All services
docker compose -f docker-compose.prod.yml restart

# Specific service
docker compose -f docker-compose.prod.yml restart backend
```

### Backup Database
```bash
bash scripts/backup-database.sh
```

### Restore Database
```bash
bash scripts/restore-database.sh backups/warehouse_planner_backup_YYYYMMDD_HHMMSS.sql.gz
```

### Update Application
```bash
# Backup first
bash scripts/backup-database.sh

# Pull latest code
git pull origin main

# Redeploy
bash scripts/deploy.sh
```

### Check System Health
```bash
bash scripts/health-check.sh
```

### View Container Status
```bash
docker compose -f docker-compose.prod.yml ps
```

### View Resource Usage
```bash
docker stats
```

---

## Troubleshooting

### Issue: SSL Certificate Fails

**Problem:** `certbot certonly` fails to obtain certificate

**Solutions:**
1. Verify DNS is propagated: `dig yourdomain.com +short`
2. Ensure port 80 is open: `sudo ufw status`
3. Stop any services on port 80: `sudo lsof -i :80`
4. Try again: `sudo bash scripts/setup-ssl.sh`

### Issue: Containers Won't Start

**Problem:** Docker containers keep restarting

**Solutions:**
1. Check logs: `docker compose -f docker-compose.prod.yml logs backend`
2. Verify .env file exists: `cat .env`
3. Check database connection: `docker logs warehouse-planner-db-prod`
4. Restart services: `docker compose -f docker-compose.prod.yml restart`

### Issue: Application Not Accessible

**Problem:** Can't access `https://yourdomain.com`

**Solutions:**
1. Check firewall: `sudo ufw status` (ports 80, 443 should be open)
2. Verify containers: `docker ps`
3. Test locally: `curl https://localhost/health` (from server)
4. Check DNS: `nslookup yourdomain.com`
5. View nginx logs: `docker logs warehouse-planner-nginx`

### Issue: Database Connection Errors

**Problem:** Backend can't connect to database

**Solutions:**
1. Check database is running: `docker ps | grep db`
2. Verify DATABASE_URL in .env matches POSTGRES_* variables
3. Test connection:
   ```bash
   docker exec warehouse-planner-backend-prod flask shell
   >>> from app.extensions import db
   >>> db.engine.execute('SELECT 1').scalar()
   ```

---

## Security Checklist

After deployment, verify:

- [x] SSL/TLS certificate installed and valid
- [x] Firewall configured (only ports 22, 80, 443 open)
- [x] .env file permissions set to 600
- [x] Strong database password generated
- [x] SECRET_KEY securely generated
- [x] CORS_ORIGINS set to production domain only
- [x] Database not exposed to internet
- [ ] SSH key-based authentication enabled
- [ ] Automated backups configured
- [ ] Monitoring/alerting enabled
- [ ] System packages updated

---

## Getting Help

1. **Check documentation:**
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
   - [README.md](README.md) - Project overview and features

2. **Check logs:**
   ```bash
   docker compose -f docker-compose.prod.yml logs -f
   ```

3. **Run health check:**
   ```bash
   bash scripts/health-check.sh
   ```

4. **GitHub Issues:**
   https://github.com/bryanstanleyyy/warehouse-capacity-planner/issues

---

## Deployment Scripts Reference

All scripts are located in the `scripts/` directory:

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup-server.sh` | Prepare fresh server | `bash scripts/setup-server.sh` |
| `configure-env.sh` | Create .env file | `bash scripts/configure-env.sh` |
| `setup-ssl.sh` | Obtain SSL certificates | `sudo bash scripts/setup-ssl.sh` |
| `deploy.sh` | Deploy application | `bash scripts/deploy.sh` |
| `health-check.sh` | Verify deployment | `bash scripts/health-check.sh` |
| `backup-database.sh` | Backup PostgreSQL | `bash scripts/backup-database.sh` |
| `restore-database.sh` | Restore from backup | `bash scripts/restore-database.sh <file>` |

---

## Architecture Overview

Your deployment includes:

```
┌─────────────────────────────────────────┐
│           Internet (Port 443)           │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │  nginx Proxy   │  (SSL/TLS, Rate Limiting)
         └───────┬────────┘
                 │
    ┌────────────┴─────────────┐
    │                          │
┌───▼────────┐         ┌──────▼──────┐
│  Frontend  │         │   Backend   │
│  (React)   │         │   (Flask)   │
└────────────┘         └──────┬──────┘
                              │
                       ┌──────▼────────┐
                       │  PostgreSQL   │
                       │   Database    │
                       └───────────────┘
```

**Networks:**
- Frontend network: nginx ↔ frontend
- Backend network: backend ↔ database
- Both networks: nginx ↔ backend (API proxy)

**Persistence:**
- Database: Docker volume (`postgres_data`)
- Uploads: Docker volume (`upload_data`)
- Backups: Host directory (`./backups`)
- Logs: Host directory (`./logs`)

---

## Next Steps

1. **Test thoroughly** - Create warehouses, upload inventory, run allocations
2. **Set up monitoring** - Configure UptimeRobot and/or Sentry
3. **Document your deployment** - Note any custom configurations
4. **Test backup/restore** - Verify you can recover from backups
5. **Load testing** - Test with realistic data volumes
6. **Update documentation** - Add your specific deployment details

---

**Deployment Time Estimate:**
- Automated (Method 1): 20-30 minutes
- Step-by-step (Method 2): 20-30 minutes
- Manual (Method 3): 1.5-2.5 hours

**Enjoy your deployed Warehouse Capacity Planner!**
