#!/bin/bash
#
# Automated Database Backup Script for Warehouse Capacity Planner
#
# This script creates compressed PostgreSQL backups with automatic cleanup.
# Usage: ./scripts/backup-database.sh
#

set -e  # Exit on error

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="warehouse_planner_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=30

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Verify required variables
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
    echo "Error: POSTGRES_USER and POSTGRES_DB must be set in .env file"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "Database Backup Script"
echo "=========================================="
echo "Timestamp: $(date)"
echo "Database: $POSTGRES_DB"
echo "User: $POSTGRES_USER"
echo "=========================================="

# Perform backup
echo "Starting database backup..."
docker exec warehouse-planner-db-prod pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --no-owner \
    --no-acl \
    > "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✓ Database dump completed successfully"
else
    echo "✗ Database dump failed"
    exit 1
fi

# Compress backup
echo "Compressing backup..."
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✓ Backup compressed: ${BACKUP_FILE}.gz"
else
    echo "✗ Compression failed"
    exit 1
fi

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}.gz" | cut -f1)
echo "Backup size: $BACKUP_SIZE"

# Cleanup old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "warehouse_planner_backup_*.sql.gz" -mtime +$RETENTION_DAYS -type f -delete -print | wc -l)
echo "✓ Deleted $DELETED_COUNT old backup(s)"

# List recent backups
echo ""
echo "Recent backups:"
ls -lht "$BACKUP_DIR"/warehouse_planner_backup_*.sql.gz | head -n 5

echo ""
echo "=========================================="
echo "Backup completed successfully!"
echo "File: ${BACKUP_FILE}.gz"
echo "Location: ${BACKUP_DIR}/"
echo "=========================================="
