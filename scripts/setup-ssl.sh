#!/bin/bash
set -e

# =============================================================================
# SSL/TLS Certificate Setup Script
# =============================================================================
# This script obtains Let's Encrypt SSL certificates and configures them
# for use with the application
#
# Usage: sudo bash scripts/setup-ssl.sh <domain> <email>
# Example: sudo bash scripts/setup-ssl.sh example.com admin@example.com
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Parse arguments or load from config
if [ -f ".deployment-config" ]; then
    source .deployment-config
    print_info "Loaded configuration from .deployment-config"
fi

DOMAIN=${1:-$DOMAIN}
EMAIL=${2:-$EMAIL}

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    print_error "Usage: sudo bash scripts/setup-ssl.sh <domain> <email>"
    print_error "Example: sudo bash scripts/setup-ssl.sh example.com admin@example.com"
    exit 1
fi

echo "=============================================="
echo "SSL/TLS Certificate Setup"
echo "=============================================="
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_info "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
    print_success "Certbot installed"
fi

# Stop any services using port 80
print_info "Stopping services on port 80..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
print_success "Services stopped"

# Obtain certificate
print_info "Obtaining SSL certificate from Let's Encrypt..."
certbot certonly --standalone \
  -d ${DOMAIN} \
  -d www.${DOMAIN} \
  --email ${EMAIL} \
  --agree-tos \
  --non-interactive \
  --expand

if [ $? -eq 0 ]; then
    print_success "SSL certificate obtained successfully"
else
    print_error "Failed to obtain SSL certificate"
    print_info "Please check:"
    print_info "  1. Domain DNS points to this server"
    print_info "  2. Port 80 is accessible from the internet"
    print_info "  3. No firewall blocking port 80"
    exit 1
fi

# Create ssl directory if it doesn't exist
mkdir -p ssl
chmod 755 ssl

# Copy certificates to project directory
print_info "Copying certificates to project directory..."
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ./ssl/
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ./ssl/

# Set permissions
chmod 644 ./ssl/fullchain.pem
chmod 600 ./ssl/privkey.pem

# Get the current user who ran sudo
ACTUAL_USER=${SUDO_USER:-$USER}
if [ "$ACTUAL_USER" != "root" ]; then
    chown -R ${ACTUAL_USER}:${ACTUAL_USER} ./ssl/
    print_success "Set ownership to ${ACTUAL_USER}"
fi

print_success "Certificates copied and permissions set"

# Verify certificates
print_info "Verifying certificate..."
CERT_EXPIRY=$(openssl x509 -in ./ssl/fullchain.pem -noout -enddate)
print_success "Certificate valid: $CERT_EXPIRY"

# Set up auto-renewal cron job
print_info "Setting up auto-renewal..."
CRON_CMD="0 0 1 * * certbot renew --quiet --deploy-hook \"cd $(pwd) && docker compose -f docker-compose.prod.yml restart nginx\" >> /var/log/certbot-renewal.log 2>&1"

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    print_success "Auto-renewal cron job created"
else
    print_info "Auto-renewal cron job already exists"
fi

# Test renewal process
print_info "Testing certificate renewal process..."
certbot renew --dry-run
if [ $? -eq 0 ]; then
    print_success "Renewal test passed"
else
    print_error "Renewal test failed (certificate is still valid, this is just a test)"
fi

echo ""
echo "=============================================="
print_success "SSL/TLS setup completed successfully!"
echo "=============================================="
echo ""
echo "Certificate details:"
ls -lh ./ssl/
echo ""
echo "Next steps:"
echo "  1. Deploy the application: bash scripts/deploy.sh"
echo "  2. Your site will be accessible at: https://${DOMAIN}"
echo ""
