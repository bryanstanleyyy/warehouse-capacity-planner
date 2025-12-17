# Deployment Scripts

Automated scripts for deploying Warehouse Capacity Planner to production.

## Quick Deployment

For a fresh Ubuntu server, run this **single command**:

```bash
curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/quick-deploy.sh | bash
```

This automates the entire deployment process (~20-30 minutes).

## Available Scripts

### 1. `quick-deploy.sh`
**One-command deployment** - Fully automated deployment from scratch

```bash
bash scripts/quick-deploy.sh
```

**What it does:**
- Sets up server (Docker, firewall, Certbot)
- Clones repository
- Configures environment
- Obtains SSL certificates
- Deploys application
- Runs health checks

**Time: 20-30 minutes**

---

### 2. `setup-server.sh`
**Server preparation** - Installs and configures prerequisites

```bash
bash scripts/setup-server.sh
```

**What it does:**
- Installs Docker and Docker Compose
- Configures firewall (UFW)
- Installs Certbot for SSL
- Sets up Fail2Ban
- Adds user to docker group

**Time: 5-10 minutes**

---

### 3. `configure-env.sh`
**Environment configuration** - Creates .env file with secure secrets

```bash
bash scripts/configure-env.sh
```

**What it does:**
- Prompts for domain, email, database settings
- Generates secure SECRET_KEY and database password
- Creates .env file with proper permissions (600)
- Saves deployment configuration

**Time: 2 minutes**

---

### 4. `setup-ssl.sh`
**SSL/TLS setup** - Obtains Let's Encrypt certificates

```bash
sudo bash scripts/setup-ssl.sh <domain> <email>
# Or: sudo bash scripts/setup-ssl.sh (uses saved config)
```

**What it does:**
- Obtains Let's Encrypt SSL certificates
- Copies certificates to project directory
- Sets correct permissions
- Configures auto-renewal cron job
- Tests renewal process

**Time: 2-3 minutes**

---

### 5. `deploy.sh`
**Application deployment** - Builds and starts all services

```bash
bash scripts/deploy.sh
```

**What it does:**
- Creates database backup (if exists)
- Stops existing containers
- Builds Docker images
- Starts all services
- Runs database migrations
- Optionally seeds example data
- Verifies deployment

**Time: 10-15 minutes**

---

### 6. `health-check.sh`
**Health verification** - Comprehensive system health check

```bash
bash scripts/health-check.sh
```

**What it checks:**
- Docker containers running
- Container health status
- Database connectivity
- Backend API responding
- nginx web server
- SSL certificate validity
- Environment configuration
- Disk space
- Docker volumes
- Recent backups
- External HTTPS accessibility
- HTTP to HTTPS redirect
- Recent error logs

**Time: 1 minute**

---

### 7. `backup-database.sh`
**Database backup** - Creates compressed PostgreSQL backup

```bash
bash scripts/backup-database.sh
```

**What it does:**
- Creates timestamped backup (`.sql.gz`)
- Stores in `./backups/` directory
- Automatically cleans up backups older than 30 days
- Shows backup size and location

**Time: <1 minute**

**Schedule automated backups:**
```bash
crontab -e
# Add: 0 2 * * * cd /path/to/project && ./scripts/backup-database.sh >> logs/backup.log 2>&1
```

---

### 8. `restore-database.sh`
**Database restore** - Restores from backup

```bash
bash scripts/restore-database.sh backups/warehouse_planner_backup_YYYYMMDD_HHMMSS.sql.gz
```

**What it does:**
- Prompts for confirmation
- Decompresses and restores backup
- Verifies database connection
- Shows available backups if no file specified

**Time: <1 minute**

---

## Deployment Workflows

### Full Deployment from Scratch

**Option 1: Fully Automated**
```bash
curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/quick-deploy.sh | bash
```

**Option 2: Step-by-Step**
```bash
# 1. Set up server
bash scripts/setup-server.sh
# Log out and back in

# 2. Clone repo
git clone https://github.com/bryanstanleyyy/warehouse-capacity-planner.git
cd warehouse-capacity-planner

# 3. Configure environment
bash scripts/configure-env.sh

# 4. Set up SSL
sudo bash scripts/setup-ssl.sh

# 5. Deploy
bash scripts/deploy.sh

# 6. Verify
bash scripts/health-check.sh
```

### Update Existing Deployment

```bash
# 1. Backup database
bash scripts/backup-database.sh

# 2. Pull latest code
git pull origin main

# 3. Redeploy
bash scripts/deploy.sh

# 4. Verify
bash scripts/health-check.sh
```

### Disaster Recovery

```bash
# 1. List available backups
bash scripts/restore-database.sh

# 2. Restore from specific backup
bash scripts/restore-database.sh backups/warehouse_planner_backup_20250117_020000.sql.gz

# 3. Restart services
docker compose -f docker-compose.prod.yml restart

# 4. Verify
bash scripts/health-check.sh
```

---

## Script Features

### Error Handling
- All scripts use `set -e` to exit on errors
- Colored output for easy reading:
  - 🟢 Green: Success
  - 🔴 Red: Error
  - 🟡 Yellow: Info
  - 🔵 Blue: Steps

### Security
- Secure secret generation using `secrets.token_hex()` and `openssl rand`
- .env file permissions automatically set to 600
- SSL certificates with proper permissions
- Firewall configuration included
- Fail2Ban setup for SSH protection

### Idempotency
- Scripts can be run multiple times safely
- Existing resources are preserved
- Prompts before overwriting configuration

### Portability
- Works on Ubuntu 20.04+
- No hard-coded paths
- Detects existing installations

---

## Requirements

### Server Requirements
- Ubuntu 20.04+ (or compatible Linux distribution)
- 2 CPU cores minimum
- 4GB RAM minimum
- 20GB disk space minimum
- Root or sudo access

### Prerequisites
- Domain name pointed to server
- Email address for SSL certificates
- SSH access to server

### Installed by Scripts
- Docker 20.10+
- Docker Compose 2.0+
- Certbot
- UFW (firewall)
- Fail2Ban
- Git

---

## Configuration Files

### `.env`
Created by `configure-env.sh`. Contains:
- Database credentials
- Flask SECRET_KEY
- CORS origins
- Upload limits
- Log level

**Permissions: 600** (read/write by owner only)

### `.deployment-config`
Created by `configure-env.sh`. Contains:
- Domain name
- Email address

Used by other scripts to avoid re-prompting.

### SSL Certificates
Located in `./ssl/`:
- `fullchain.pem` - Certificate chain (644)
- `privkey.pem` - Private key (600)

---

## Troubleshooting

### Script fails with "Permission denied"
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### "Docker not found" after setup-server.sh
```bash
# Log out and back in to apply docker group
exit
ssh user@server
```

### SSL certificate fails
```bash
# Check DNS
dig yourdomain.com +short

# Check port 80 is open
sudo ufw status

# Try again
sudo bash scripts/setup-ssl.sh
```

### Container health checks fail
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Check specific container
docker logs warehouse-planner-backend-prod
```

---

## Support

- **Documentation**: See [DEPLOYMENT.md](../DEPLOYMENT.md) for comprehensive guide
- **Quick Reference**: See [QUICK-START.md](../QUICK-START.md) for quick deployment
- **Troubleshooting**: See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues
- **GitHub Issues**: https://github.com/bryanstanleyyy/warehouse-capacity-planner/issues

---

## Script Maintenance

### Testing Scripts Locally

Run shellcheck for syntax checking:
```bash
shellcheck scripts/*.sh
```

### Updating Scripts

After modifying scripts:
```bash
# Make executable
chmod +x scripts/*.sh

# Test locally
bash scripts/script-name.sh

# Commit changes
git add scripts/
git commit -m "Update deployment scripts"
git push
```

---

## License

MIT License - See [LICENSE](../LICENSE) for details

---

**Last Updated**: January 2025
