#!/bin/bash
set -e

# =============================================================================
# Production Deployment Script
# =============================================================================
# This script deploys the Warehouse Capacity Planner application to production
# It builds Docker images, starts services, runs migrations, and verifies deployment
#
# Usage: bash scripts/deploy.sh
# =============================================================================

echo "=============================================="
echo "Warehouse Capacity Planner - Deployment"
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
    echo -e "${BLUE}▶ $1${NC}"
}

# Error handler
trap 'print_error "Deployment failed at line $LINENO. Check logs above."; exit 1' ERR

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found"
    print_info "Run: bash scripts/configure-env.sh"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f "./ssl/fullchain.pem" ] || [ ! -f "./ssl/privkey.pem" ]; then
    print_error "SSL certificates not found in ./ssl/"
    print_info "Run: sudo bash scripts/setup-ssl.sh <domain> <email>"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    print_info "Run: bash scripts/setup-server.sh"
    exit 1
fi

# Backup database if containers are running
if docker ps | grep -q "warehouse-planner-db-prod"; then
    print_step "Creating database backup before deployment..."
    if [ -f "./scripts/backup-database.sh" ]; then
        bash ./scripts/backup-database.sh || print_info "Backup failed or skipped"
    fi
fi

# Stop existing containers
print_step "Stopping existing containers..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
print_success "Containers stopped"

# Create required directories
print_step "Creating required directories..."
mkdir -p logs/backend logs/nginx backups
chmod 700 backups
print_success "Directories created"

# Build Docker images
print_step "Building Docker images..."
print_info "This may take 5-10 minutes depending on server speed..."
docker compose -f docker-compose.prod.yml build --no-cache
print_success "Docker images built"

# Start services
print_step "Starting services..."
docker compose -f docker-compose.prod.yml up -d
print_success "Services started"

# Wait for services to be healthy
print_step "Waiting for services to be healthy..."
sleep 10

# Check if containers are running
CONTAINERS=$(docker compose -f docker-compose.prod.yml ps -q | wc -l)
if [ "$CONTAINERS" -lt 4 ]; then
    print_error "Not all containers are running"
    docker compose -f docker-compose.prod.yml ps
    exit 1
fi
print_success "All containers are running"

# Wait for database to be ready
print_step "Waiting for database to be ready..."
for i in {1..30}; do
    if docker exec warehouse-planner-db-prod pg_isready -U ${POSTGRES_USER:-warehouse_prod_user} >/dev/null 2>&1; then
        print_success "Database is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Database failed to start"
        docker logs warehouse-planner-db-prod --tail=50
        exit 1
    fi
    sleep 1
done

# Run database migrations
print_step "Running database migrations..."
docker exec warehouse-planner-backend-prod flask db upgrade
print_success "Database migrations completed"

# Optional: Seed example data
read -p "Do you want to seed example warehouse data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Seeding example warehouses..."
    docker exec warehouse-planner-backend-prod python seed_warehouses.py
    print_success "Example data seeded"
fi

# Make backup scripts executable
print_step "Configuring backup scripts..."
chmod +x scripts/backup-database.sh
chmod +x scripts/restore-database.sh
print_success "Backup scripts configured"

# Check container health
print_step "Checking container health..."
sleep 5
docker ps --format "table {{.Names}}\t{{.Status}}" | grep warehouse-planner

# Get domain from .env or deployment config
if [ -f ".deployment-config" ]; then
    source .deployment-config
fi

echo ""
echo "=============================================="
print_success "Deployment completed successfully!"
echo "=============================================="
echo ""
echo "Container status:"
docker compose -f docker-compose.prod.yml ps
echo ""

if [ ! -z "$DOMAIN" ]; then
    echo "Your application should be accessible at:"
    echo "  → https://${DOMAIN}"
    echo ""
fi

print_info "Next steps:"
echo "  1. Run health check: bash scripts/health-check.sh"
echo "  2. View logs: docker compose -f docker-compose.prod.yml logs -f"
echo "  3. Configure automated backups (crontab -e)"
echo ""
echo "Useful commands:"
echo "  • View logs: docker compose -f docker-compose.prod.yml logs -f [service]"
echo "  • Restart service: docker compose -f docker-compose.prod.yml restart [service]"
echo "  • Stop all: docker compose -f docker-compose.prod.yml down"
echo "  • Backup database: bash scripts/backup-database.sh"
echo ""
