#!/bin/bash
# Backup script for XRP Trading Bot
# This script creates a backup of the bot's data and configuration

# Configuration
BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
CONFIG_DIR="/app/config"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="xrp_bot_backup_${TIMESTAMP}"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Create temporary directory for backup
TEMP_DIR="${BACKUP_DIR}/temp_${TIMESTAMP}"
mkdir -p ${TEMP_DIR}

# Copy data and configuration files
echo "Copying data files..."
cp -r ${DATA_DIR}/* ${TEMP_DIR}/ 2>/dev/null || echo "No data files to backup"

echo "Copying configuration files..."
cp -r ${CONFIG_DIR}/* ${TEMP_DIR}/ 2>/dev/null || echo "No configuration files to backup"

# Create archive
echo "Creating backup archive..."
cd ${BACKUP_DIR}
tar -czf "${BACKUP_NAME}.tar.gz" -C ${TEMP_DIR} .

# Clean up temporary directory
rm -rf ${TEMP_DIR}

# Remove old backups (keep last 7)
echo "Cleaning up old backups..."
ls -t ${BACKUP_DIR}/*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null || echo "No old backups to remove"

echo "Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
