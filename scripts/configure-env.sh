#!/bin/bash
set -e

# =============================================================================
# Environment Configuration Helper
# =============================================================================
# This script helps create and configure the .env file for production deployment
# It generates secure secrets and prompts for required configuration values
#
# Usage: bash scripts/configure-env.sh
# =============================================================================

echo "=============================================="
echo "Environment Configuration Helper"
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

print_question() {
    echo -e "${BLUE}? $1${NC}"
}

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    print_error ".env.example not found. Are you in the project root directory?"
    exit 1
fi

# Check if .env already exists
if [ -f ".env" ]; then
    print_info ".env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Exiting without changes"
        exit 0
    fi
    # Backup existing .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    print_success "Backed up existing .env file"
fi

# Generate secure secrets
print_info "Generating secure secrets..."

# Generate SECRET_KEY (64 character hex)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
print_success "SECRET_KEY generated"

# Generate database password (32 character base64)
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
print_success "Database password generated"

# Prompt for configuration values
echo ""
print_question "Enter your production domain (e.g., example.com):"
read -p "> " DOMAIN

if [ -z "$DOMAIN" ]; then
    print_error "Domain is required"
    exit 1
fi

print_question "Enter your email for SSL certificate notifications:"
read -p "> " EMAIL

if [ -z "$EMAIL" ]; then
    print_error "Email is required"
    exit 1
fi

print_question "Enter database username (default: warehouse_prod_user):"
read -p "> " DB_USER
DB_USER=${DB_USER:-warehouse_prod_user}

print_question "Enter database name (default: warehouse_planner_prod):"
read -p "> " DB_NAME
DB_NAME=${DB_NAME:-warehouse_planner_prod}

print_question "Enter maximum upload size in MB (default: 10):"
read -p "> " MAX_UPLOAD_MB
MAX_UPLOAD_MB=${MAX_UPLOAD_MB:-10}
MAX_UPLOAD_SIZE=$((MAX_UPLOAD_MB * 1024 * 1024))

print_question "Enter log level (DEBUG/INFO/WARNING/ERROR, default: INFO):"
read -p "> " LOG_LEVEL
LOG_LEVEL=${LOG_LEVEL:-INFO}

# Optional: Sentry DSN
print_question "Enter Sentry DSN for error tracking (optional, press Enter to skip):"
read -p "> " SENTRY_DSN

# Create .env file
print_info "Creating .env file..."

cat > .env << EOF
# =============================================================================
# Production Environment Configuration
# Generated on: $(date)
# =============================================================================

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=${DB_NAME}

# -----------------------------------------------------------------------------
# Backend Configuration
# -----------------------------------------------------------------------------
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
CORS_ORIGINS=https://${DOMAIN}

# -----------------------------------------------------------------------------
# Frontend Configuration
# -----------------------------------------------------------------------------
VITE_API_URL=/api/v1

# -----------------------------------------------------------------------------
# Optional Configuration
# -----------------------------------------------------------------------------
MAX_UPLOAD_SIZE=${MAX_UPLOAD_SIZE}
LOG_LEVEL=${LOG_LEVEL}
EOF

# Add Sentry DSN if provided
if [ ! -z "$SENTRY_DSN" ]; then
    echo "SENTRY_DSN=${SENTRY_DSN}" >> .env
fi

# Set secure permissions
chmod 600 .env
print_success ".env file created with secure permissions (600)"

echo ""
echo "=============================================="
print_success "Environment configuration completed!"
echo "=============================================="
echo ""
echo "Configuration summary:"
echo "  Domain: ${DOMAIN}"
echo "  Email: ${EMAIL}"
echo "  Database User: ${DB_USER}"
echo "  Database Name: ${DB_NAME}"
echo "  Max Upload Size: ${MAX_UPLOAD_MB} MB"
echo "  Log Level: ${LOG_LEVEL}"
if [ ! -z "$SENTRY_DSN" ]; then
    echo "  Sentry: Enabled"
fi
echo ""
print_info "Next steps:"
echo "  1. Review the .env file if needed: cat .env"
echo "  2. Obtain SSL certificate: sudo bash scripts/setup-ssl.sh ${DOMAIN} ${EMAIL}"
echo "  3. Deploy the application: bash scripts/deploy.sh"
echo ""

# Save domain and email for SSL script
echo "DOMAIN=${DOMAIN}" > .deployment-config
echo "EMAIL=${EMAIL}" >> .deployment-config
print_success "Saved deployment configuration"
