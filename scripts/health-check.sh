#!/bin/bash

# =============================================================================
# Health Check Script
# =============================================================================
# This script verifies that all services are running correctly and the
# application is accessible
#
# Usage: bash scripts/health-check.sh
# =============================================================================

echo "=============================================="
echo "Warehouse Capacity Planner - Health Check"
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

print_check() {
    echo -e "${BLUE}▶ Checking: $1${NC}"
}

PASSED=0
FAILED=0

# Get domain from deployment config
if [ -f ".deployment-config" ]; then
    source .deployment-config
fi

# Check 1: Docker containers running
print_check "Docker containers"
EXPECTED_CONTAINERS=4
RUNNING_CONTAINERS=$(docker compose -f docker-compose.prod.yml ps -q 2>/dev/null | wc -l)

if [ "$RUNNING_CONTAINERS" -eq "$EXPECTED_CONTAINERS" ]; then
    print_success "All $EXPECTED_CONTAINERS containers are running"
    ((PASSED++))
else
    print_error "Expected $EXPECTED_CONTAINERS containers, found $RUNNING_CONTAINERS"
    ((FAILED++))
    docker compose -f docker-compose.prod.yml ps
fi

# Check 2: Container health status
print_check "Container health status"
UNHEALTHY=$(docker ps --filter "name=warehouse-planner" --format "{{.Status}}" | grep -v "healthy" | grep -v "health" | wc -l)

if [ "$UNHEALTHY" -eq 0 ]; then
    print_success "All containers are healthy"
    ((PASSED++))
else
    print_error "Some containers are unhealthy"
    ((FAILED++))
    docker ps --filter "name=warehouse-planner" --format "table {{.Names}}\t{{.Status}}"
fi

# Check 3: Database connectivity
print_check "Database connectivity"
if docker exec warehouse-planner-backend-prod flask shell -c "from app.extensions import db; db.engine.execute('SELECT 1').scalar()" 2>/dev/null | grep -q "1"; then
    print_success "Database is accessible"
    ((PASSED++))
else
    print_error "Cannot connect to database"
    ((FAILED++))
fi

# Check 4: Backend API responding
print_check "Backend API"
if docker exec warehouse-planner-backend-prod curl -s http://localhost:5000/api/v1/warehouses >/dev/null 2>&1; then
    print_success "Backend API is responding"
    ((PASSED++))
else
    print_error "Backend API is not responding"
    ((FAILED++))
fi

# Check 5: nginx responding locally
print_check "nginx web server"
if docker exec warehouse-planner-nginx wget --spider -q http://localhost/health 2>/dev/null; then
    print_success "nginx is responding"
    ((PASSED++))
else
    print_error "nginx is not responding"
    ((FAILED++))
fi

# Check 6: SSL certificates
print_check "SSL certificates"
if [ -f "./ssl/fullchain.pem" ] && [ -f "./ssl/privkey.pem" ]; then
    CERT_EXPIRY=$(openssl x509 -in ./ssl/fullchain.pem -noout -enddate 2>/dev/null | cut -d= -f2)
    DAYS_UNTIL_EXPIRY=$(( ( $(date -d "$CERT_EXPIRY" +%s) - $(date +%s) ) / 86400 ))

    if [ $DAYS_UNTIL_EXPIRY -gt 0 ]; then
        print_success "SSL certificates valid (expires in $DAYS_UNTIL_EXPIRY days)"
        ((PASSED++))
    else
        print_error "SSL certificates expired"
        ((FAILED++))
    fi
else
    print_error "SSL certificate files not found"
    ((FAILED++))
fi

# Check 7: Environment file
print_check "Environment configuration"
if [ -f ".env" ]; then
    ENV_PERMS=$(stat -c "%a" .env 2>/dev/null || stat -f "%OLp" .env 2>/dev/null)
    if [ "$ENV_PERMS" = "600" ]; then
        print_success ".env file exists with secure permissions (600)"
        ((PASSED++))
    else
        print_error ".env file has insecure permissions ($ENV_PERMS), should be 600"
        ((FAILED++))
    fi
else
    print_error ".env file not found"
    ((FAILED++))
fi

# Check 8: Disk space
print_check "Disk space"
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "Disk space OK (${DISK_USAGE}% used)"
    ((PASSED++))
else
    print_error "Disk space low (${DISK_USAGE}% used)"
    ((FAILED++))
fi

# Check 9: Docker volumes
print_check "Docker volumes"
VOLUMES=$(docker volume ls | grep warehouse | wc -l)
if [ "$VOLUMES" -ge 1 ]; then
    print_success "Data volumes exist ($VOLUMES found)"
    ((PASSED++))
else
    print_error "No data volumes found"
    ((FAILED++))
fi

# Check 10: Recent backups
print_check "Database backups"
if [ -d "backups" ]; then
    RECENT_BACKUPS=$(find backups -name "*.sql.gz" -mtime -7 | wc -l)
    if [ "$RECENT_BACKUPS" -gt 0 ]; then
        print_success "Recent backups found ($RECENT_BACKUPS in last 7 days)"
        ((PASSED++))
    else
        print_error "No recent backups found (older than 7 days)"
        ((FAILED++))
    fi
else
    print_error "Backups directory not found"
    ((FAILED++))
fi

# Check 11: External accessibility (if domain is set)
if [ ! -z "$DOMAIN" ]; then
    print_check "External HTTPS accessibility"
    if curl -s -o /dev/null -w "%{http_code}" https://${DOMAIN}/health --max-time 10 | grep -q "200"; then
        print_success "Application is accessible at https://${DOMAIN}"
        ((PASSED++))
    else
        print_error "Cannot access https://${DOMAIN}"
        print_info "This might be a DNS or firewall issue"
        ((FAILED++))
    fi

    print_check "HTTP to HTTPS redirect"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${DOMAIN} --max-time 10)
    if [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        print_success "HTTP redirects to HTTPS (${HTTP_CODE})"
        ((PASSED++))
    else
        print_error "HTTP redirect not working (got ${HTTP_CODE})"
        ((FAILED++))
    fi
fi

# Check 12: Container logs for errors
print_check "Recent error logs"
ERROR_COUNT=$(docker compose -f docker-compose.prod.yml logs --tail=100 2>/dev/null | grep -i "error" | grep -v "0 error" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "No recent errors in logs"
    ((PASSED++))
else
    print_error "Found $ERROR_COUNT error messages in recent logs"
    ((FAILED++))
    print_info "Run: docker compose -f docker-compose.prod.yml logs | grep -i error"
fi

echo ""
echo "=============================================="
echo "Health Check Summary"
echo "=============================================="
echo ""

TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "Passed: $PASSED/$TOTAL ($PERCENTAGE%)"

if [ $FAILED -eq 0 ]; then
    print_success "All health checks passed! System is healthy."
    echo ""

    if [ ! -z "$DOMAIN" ]; then
        echo "Your application is running at:"
        echo "  → https://${DOMAIN}"
        echo ""
    fi

    echo "Resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep warehouse-planner

    exit 0
else
    print_error "$FAILED health check(s) failed"
    echo ""
    echo "Troubleshooting:"
    echo "  • View logs: docker compose -f docker-compose.prod.yml logs -f"
    echo "  • Restart services: docker compose -f docker-compose.prod.yml restart"
    echo "  • Check configuration: cat .env"
    echo ""
    exit 1
fi
