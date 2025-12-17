#!/bin/bash
set -e

# =============================================================================
# Server Setup Script for Warehouse Capacity Planner
# =============================================================================
# This script prepares a fresh Ubuntu server for deployment by:
# - Installing Docker and Docker Compose
# - Configuring firewall (UFW)
# - Setting up non-root user (optional)
# - Installing required dependencies
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/setup-server.sh | bash
#   Or: bash setup-server.sh
# =============================================================================

echo "=============================================="
echo "Warehouse Capacity Planner - Server Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
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
if [[ $EUID -eq 0 ]]; then
   print_info "Running as root user"
else
   print_info "Running as non-root user (will use sudo)"
fi

# Update system packages
print_info "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
print_success "System packages updated"

# Install prerequisites
print_info "Installing prerequisites..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    vim \
    htop \
    ufw \
    fail2ban
print_success "Prerequisites installed"

# Install Docker
print_info "Installing Docker..."

# Remove old versions
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

print_success "Docker installed"

# Add current user to docker group
if [[ $EUID -ne 0 ]]; then
    sudo usermod -aG docker $USER
    print_success "Added $USER to docker group"
    print_info "You may need to log out and back in for docker group to take effect"
fi

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
print_success "Docker service started and enabled"

# Verify Docker installation
DOCKER_VERSION=$(docker --version)
COMPOSE_VERSION=$(docker compose version)
print_success "Docker installed: $DOCKER_VERSION"
print_success "Docker Compose installed: $COMPOSE_VERSION"

# Configure firewall (UFW)
print_info "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
print_success "Firewall configured (ports 22, 80, 443 open)"

# Configure Fail2Ban
print_info "Configuring Fail2Ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
print_success "Fail2Ban configured and started"

# Install Certbot for Let's Encrypt
print_info "Installing Certbot for SSL certificates..."
sudo apt-get install -y certbot python3-certbot-nginx
print_success "Certbot installed"

echo ""
echo "=============================================="
print_success "Server setup completed successfully!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Log out and back in (if you're not root) to apply docker group"
echo "2. Verify Docker: docker --version"
echo "3. Clone the repository"
echo "4. Run the deployment script"
echo ""
echo "Firewall status:"
sudo ufw status
echo ""
