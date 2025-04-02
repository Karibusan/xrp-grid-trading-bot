#!/bin/bash
# Backup script for XRP Trading Bot
# This script creates daily backups and rotates logs weekly

# Configuration
BACKUP_DIR="/path/to/backup/xrp_trading_bot"
SOURCE_DIR="/path/to/xrp_trading_bot"
LOG_DIR="${SOURCE_DIR}/data"
MAX_BACKUPS=7  # Keep 7 days of backups
MAX_LOG_BACKUPS=4  # Keep 4 weeks of logs

# Create timestamp
TIMESTAMP=$(date +%Y%m%d)
LOG_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}/daily"
mkdir -p "${BACKUP_DIR}/logs"

# Function to log messages
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "${BACKUP_DIR}/backup.log"
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Create daily backup of the entire directory
create_daily_backup() {
    log_message "Creating daily backup..."
    
    # Create tar archive of the entire directory
    tar -czf "${BACKUP_DIR}/daily/xrp_trading_bot_${TIMESTAMP}.tar.gz" -C "$(dirname ${SOURCE_DIR})" "$(basename ${SOURCE_DIR})"
    
    if [ $? -eq 0 ]; then
        log_message "Daily backup created successfully: xrp_trading_bot_${TIMESTAMP}.tar.gz"
    else
        log_message "ERROR: Failed to create daily backup"
    fi
}

# Rotate logs (weekly)
rotate_logs() {
    log_message "Rotating logs..."
    
    # Check if trading_log.txt exists
    if [ -f "${LOG_DIR}/trading_log.txt" ]; then
        # Copy current log to backup with timestamp
        cp "${LOG_DIR}/trading_log.txt" "${BACKUP_DIR}/logs/trading_log_${LOG_TIMESTAMP}.txt"
        
        if [ $? -eq 0 ]; then
            log_message "Log backup created successfully: trading_log_${LOG_TIMESTAMP}.txt"
            
            # Truncate the current log file (keep the file but empty it)
            echo "Log rotated on $(date)" > "${LOG_DIR}/trading_log.txt"
            log_message "Current log file truncated"
        else
            log_message "ERROR: Failed to backup log file"
        fi
    else
        log_message "WARNING: Log file not found at ${LOG_DIR}/trading_log.txt"
    fi
}

# Clean up old backups
cleanup_old_backups() {
    log_message "Cleaning up old backups..."
    
    # Remove old daily backups (keep only MAX_BACKUPS most recent)
    ls -t "${BACKUP_DIR}/daily" | grep "xrp_trading_bot_" | tail -n +$((MAX_BACKUPS+1)) | while read file; do
        rm "${BACKUP_DIR}/daily/$file"
        log_message "Removed old backup: $file"
    done
    
    # Remove old log backups (keep only MAX_LOG_BACKUPS most recent)
    ls -t "${BACKUP_DIR}/logs" | grep "trading_log_" | tail -n +$((MAX_LOG_BACKUPS+1)) | while read file; do
        rm "${BACKUP_DIR}/logs/$file"
        log_message "Removed old log backup: $file"
    done
}

# Verify container auto-restart configuration
verify_restart_config() {
    log_message "Verifying container auto-restart configuration..."
    
    # Check if container exists
    if docker ps -a | grep -q "xrp_trading_bot"; then
        # Check restart policy
        RESTART_POLICY=$(docker inspect --format='{{.HostConfig.RestartPolicy.Name}}' xrp_trading_bot)
        
        if [ "$RESTART_POLICY" == "always" ] || [ "$RESTART_POLICY" == "unless-stopped" ]; then
            log_message "Container restart policy is correctly set to: $RESTART_POLICY"
        else
            log_message "WARNING: Container restart policy is set to: $RESTART_POLICY (should be 'always' or 'unless-stopped')"
            log_message "Updating restart policy to 'always'..."
            
            # Update restart policy
            docker update --restart=always xrp_trading_bot
            
            if [ $? -eq 0 ]; then
                log_message "Restart policy updated successfully"
            else
                log_message "ERROR: Failed to update restart policy"
            fi
        fi
    else
        log_message "ERROR: Container 'xrp_trading_bot' not found"
    fi
}

# Main execution
log_message "Starting XRP Trading Bot backup and maintenance script"

# Create daily backup
create_daily_backup

# Check if it's Sunday (day 0) for weekly log rotation
if [ $(date +%w) -eq 0 ]; then
    log_message "It's Sunday - performing weekly log rotation"
    rotate_logs
fi

# Clean up old backups
cleanup_old_backups

# Verify restart configuration
verify_restart_config

log_message "Backup and maintenance completed"
