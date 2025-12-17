#!/bin/bash
set -e

# =============================================================================
# Quick Deploy Script - One Command Deployment
# =============================================================================
# This script automates the entire deployment process from start to finish
# Run this on a fresh Ubuntu server to deploy the complete application
#
# Usage: curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/quick-deploy.sh | bash
# Or: bash scripts/quick-deploy.sh
# =============================================================================

echo "=============================================="
echo "Warehouse Capacity Planner"
echo "Automated Production Deployment"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ STEP: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Prompt for configuration
print_step "Configuration"

print_info "This script will deploy the Warehouse Capacity Planner to production."
print_info "You'll need:"
echo "  • A domain name pointed to this server"
echo "  • An email address for SSL certificates"
echo "  • About 20-30 minutes"
echo ""

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Deployment cancelled"
    exit 0
fi

# Collect configuration
echo ""
read -p "Enter your domain name (e.g., example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    print_error "Domain is required"
    exit 1
fi

read -p "Enter your email address: " EMAIL
if [ -z "$EMAIL" ]; then
    print_error "Email is required"
    exit 1
fi

echo ""
print_success "Configuration collected"
echo "  Domain: $DOMAIN"
echo "  Email: $EMAIL"
echo ""

# Check DNS
print_info "Checking DNS configuration..."
SERVER_IP=$(curl -s ifconfig.me)
DNS_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$SERVER_IP" = "$DNS_IP" ]; then
    print_success "DNS is configured correctly ($DNS_IP)"
else
    print_error "DNS mismatch!"
    echo "  Server IP: $SERVER_IP"
    echo "  Domain IP: $DNS_IP"
    echo ""
    read -p "DNS is not configured correctly. Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Please configure DNS first, then run this script again"
        exit 1
    fi
fi

# =============================================================================
# STEP 1: Server Setup
# =============================================================================
print_step "1/5 - Setting Up Server"

if command -v docker &> /dev/null; then
    print_info "Docker already installed, skipping server setup"
else
    print_info "Installing Docker, configuring firewall, and setting up dependencies..."

    # Check if setup-server.sh exists locally
    if [ -f "./scripts/setup-server.sh" ]; then
        bash ./scripts/setup-server.sh
    else
        # Download and run
        curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/setup-server.sh | bash
    fi
fi

print_success "Server setup completed"

# =============================================================================
# STEP 2: Clone Repository
# =============================================================================
print_step "2/5 - Cloning Repository"

if [ -d "./warehouse-capacity-planner" ]; then
    print_info "Repository already exists, using existing directory"
    cd warehouse-capacity-planner
elif [ -d "./backend" ] && [ -d "./frontend" ]; then
    print_info "Already in repository directory"
else
    print_info "Cloning repository..."
    git clone https://github.com/bryanstanleyyy/warehouse-capacity-planner.git
    cd warehouse-capacity-planner
fi

print_success "Repository ready"

# =============================================================================
# STEP 3: Configure Environment
# =============================================================================
print_step "3/5 - Configuring Environment"

if [ -f ".env" ]; then
    print_info ".env already exists"
    read -p "Recreate .env file? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm .env
        CREATE_ENV=true
    else
        CREATE_ENV=false
    fi
else
    CREATE_ENV=true
fi

if [ "$CREATE_ENV" = true ]; then
    print_info "Generating secure configuration..."

    # Generate secrets
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

    # Create .env file
    cat > .env << EOF
# Production Environment Configuration
# Generated: $(date)

# Database Configuration
POSTGRES_USER=warehouse_prod_user
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=warehouse_planner_prod

# Backend Configuration
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
DATABASE_URL=postgresql://warehouse_prod_user:${DB_PASSWORD}@db:5432/warehouse_planner_prod
CORS_ORIGINS=https://${DOMAIN}

# Frontend Configuration
VITE_API_URL=/api/v1

# Optional Configuration
MAX_UPLOAD_SIZE=10485760
LOG_LEVEL=INFO
EOF

    chmod 600 .env
    print_success "Environment configured with secure secrets"
fi

# Save deployment config
echo "DOMAIN=${DOMAIN}" > .deployment-config
echo "EMAIL=${EMAIL}" >> .deployment-config

# =============================================================================
# STEP 4: SSL/TLS Setup
# =============================================================================
print_step "4/5 - Setting Up SSL/TLS"

if [ -f "./ssl/fullchain.pem" ] && [ -f "./ssl/privkey.pem" ]; then
    print_info "SSL certificates already exist"

    # Check if they're still valid
    DAYS_UNTIL_EXPIRY=$(( ( $(date -d "$(openssl x509 -in ./ssl/fullchain.pem -noout -enddate | cut -d= -f2)" +%s) - $(date +%s) ) / 86400 ))

    if [ $DAYS_UNTIL_EXPIRY -gt 7 ]; then
        print_success "SSL certificates are valid (${DAYS_UNTIL_EXPIRY} days remaining)"
        SETUP_SSL=false
    else
        print_info "SSL certificates expire soon, renewing..."
        SETUP_SSL=true
    fi
else
    SETUP_SSL=true
fi

if [ "$SETUP_SSL" = true ]; then
    print_info "Obtaining SSL certificates from Let's Encrypt..."

    # Stop any running services
    docker compose -f docker-compose.prod.yml down 2>/dev/null || true

    # Get certificates
    mkdir -p ssl
    sudo certbot certonly --standalone \
        -d ${DOMAIN} \
        -d www.${DOMAIN} \
        --email ${EMAIL} \
        --agree-tos \
        --non-interactive \
        --expand

    # Copy to project directory
    sudo cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ./ssl/
    sudo cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ./ssl/
    sudo chmod 644 ./ssl/fullchain.pem
    sudo chmod 600 ./ssl/privkey.pem
    sudo chown $USER:$USER ./ssl/* 2>/dev/null || true

    print_success "SSL certificates obtained and configured"

    # Set up auto-renewal
    print_info "Configuring SSL auto-renewal..."
    CRON_CMD="0 0 1 * * certbot renew --quiet --deploy-hook \"cd $(pwd) && docker compose -f docker-compose.prod.yml restart nginx\" >> /var/log/certbot-renewal.log 2>&1"
    if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (sudo crontab -l 2>/dev/null; echo "$CRON_CMD") | sudo crontab -
        print_success "Auto-renewal configured"
    fi
fi

# =============================================================================
# STEP 5: Deploy Application
# =============================================================================
print_step "5/5 - Deploying Application"

print_info "Creating required directories..."
mkdir -p logs/backend logs/nginx backups
chmod 700 backups

print_info "Building Docker images (this may take 5-10 minutes)..."
docker compose -f docker-compose.prod.yml build --no-cache

print_info "Starting services..."
docker compose -f docker-compose.prod.yml up -d

print_info "Waiting for services to be healthy..."
sleep 15

# Wait for database
for i in {1..30}; do
    if docker exec warehouse-planner-db-prod pg_isready -U warehouse_prod_user >/dev/null 2>&1; then
        print_success "Database is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Database failed to start"
        docker logs warehouse-planner-db-prod --tail=50
        exit 1
    fi
    sleep 2
done

print_info "Running database migrations..."
docker exec warehouse-planner-backend-prod flask db upgrade

print_info "Seeding example warehouses..."
docker exec warehouse-planner-backend-prod python seed_warehouses.py || print_info "Seed data already exists"

# Make backup scripts executable
chmod +x scripts/*.sh 2>/dev/null || true

print_success "Application deployed successfully!"

# =============================================================================
# Verification
# =============================================================================
print_step "Verification"

print_info "Running health checks..."
sleep 5

# Check containers
CONTAINERS=$(docker compose -f docker-compose.prod.yml ps -q | wc -l)
if [ "$CONTAINERS" -ge 4 ]; then
    print_success "All containers are running ($CONTAINERS/4)"
else
    print_error "Some containers failed to start ($CONTAINERS/4)"
fi

# Check HTTPS
if curl -s -o /dev/null -w "%{http_code}" https://${DOMAIN}/health --max-time 10 | grep -q "200"; then
    print_success "Application is accessible at https://${DOMAIN}"
else
    print_error "Cannot access https://${DOMAIN}"
    print_info "This might take a few more minutes for all services to be ready"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "=============================================="
print_success "DEPLOYMENT COMPLETED!"
echo "=============================================="
echo ""
echo "🎉 Your Warehouse Capacity Planner is now live!"
echo ""
echo "Access your application:"
echo "  🌐 https://${DOMAIN}"
echo ""
echo "Next steps:"
echo "  1. Visit https://${DOMAIN} in your browser"
echo "  2. Test creating a warehouse and uploading inventory"
echo "  3. Set up automated backups:"
echo "     crontab -e"
echo "     Add: 0 2 * * * cd $(pwd) && ./scripts/backup-database.sh >> logs/backup.log 2>&1"
echo ""
echo "  4. Set up monitoring (recommended):"
echo "     • UptimeRobot: https://uptimerobot.com"
echo "     • Sentry: https://sentry.io"
echo ""
echo "Useful commands:"
echo "  • Health check: bash scripts/health-check.sh"
echo "  • View logs: docker compose -f docker-compose.prod.yml logs -f"
echo "  • Backup database: bash scripts/backup-database.sh"
echo "  • Restart services: docker compose -f docker-compose.prod.yml restart"
echo ""
echo "Container status:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "For help, see:"
echo "  • QUICK-START.md - Quick reference guide"
echo "  • DEPLOYMENT.md - Comprehensive deployment guide"
echo "  • TROUBLESHOOTING.md - Common issues and solutions"
echo ""
print_success "Happy warehouse planning!"
echo ""
