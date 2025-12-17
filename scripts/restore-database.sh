#!/bin/bash
#
# Database Restore Script for Warehouse Capacity Planner
#
# This script restores a PostgreSQL database from a compressed backup.
# Usage: ./scripts/restore-database.sh <backup_file.sql.gz>
#

set -e  # Exit on error

# Check if backup file is provided
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./scripts/restore-database.sh <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lht ./backups/warehouse_planner_backup_*.sql.gz 2>/dev/null | head -n 10 || echo "  No backups found"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Verify required variables
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
    echo "Error: POSTGRES_USER and POSTGRES_DB must be set in .env file"
    exit 1
fi

echo "=========================================="
echo "Database Restore Script"
echo "=========================================="
echo "Timestamp: $(date)"
echo "Database: $POSTGRES_DB"
echo "User: $POSTGRES_USER"
echo "Backup file: $BACKUP_FILE"
echo "=========================================="
echo ""
echo "WARNING: This will replace all data in the database!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo "Starting database restore..."

# Decompress and restore
gunzip -c "$BACKUP_FILE" | docker exec -i warehouse-planner-db-prod psql \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Database restore completed successfully!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "✗ Database restore failed!"
    echo "=========================================="
    exit 1
fi

# Verify restore
echo ""
echo "Verifying database connection..."
docker exec warehouse-planner-db-prod psql \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Database verification successful"
else
    echo "✗ Database verification failed"
    exit 1
fi

echo ""
echo "Restore process complete!"
echo "Remember to restart the backend service:"
echo "  docker-compose -f docker-compose.prod.yml restart backend"
