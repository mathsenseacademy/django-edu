#!/bin/bash

# Exit on error
set -e
set -o pipefail

# Configuration
DJANGO_APP_DIR="/var/www/django-app"
NGINX_DIR="/var/www/django-app"
BACKUP_DIR="/var/www/backups"
LOG_DIR="/var/log/django"
LOG_FILE="$LOG_DIR/django.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Default SERVER_NAME (can be overridden by .env file)
SERVER_NAME="15.207.99.95"  # Using IP address instead of full domain name

# Django configuration
DJANGO_PORT=7000
DJANGO_USER="ubuntu"
DJANGO_GROUP="ubuntu"

# Create log directory and file first
sudo mkdir -p "$LOG_DIR"
sudo touch "$LOG_FILE"
sudo chown -R $USER:$USER "$LOG_DIR"
sudo chmod -R 755 "$LOG_DIR"
sudo chmod 644 "$LOG_FILE"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | sudo tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "Error occurred in deployment at line $1"
    exit 1
}
trap 'handle_error $LINENO' ERR

# Create necessary directories
log "Creating necessary directories"
sudo mkdir -p "$DJANGO_APP_DIR" "$BACKUP_DIR" "$NGINX_DIR"
sudo chown -R $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR" "$BACKUP_DIR" "$NGINX_DIR"
sudo chmod -R 755 "$DJANGO_APP_DIR" "$BACKUP_DIR" "$NGINX_DIR"

# Load environment variables if exists
if [ -f .env ]; then
    log "Loading environment variables from .env file"
    source .env
fi

# Verify required environment variables
if [ -z "$SERVER_NAME" ]; then
    log "Warning: SERVER_NAME not set in .env, using default: $SERVER_NAME"
fi

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment"
    if [ -d "$NGINX_DIR" ]; then
        sudo tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$NGINX_DIR" .
        log "Backup created: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    fi
}

# Verify Python and Django installation
verify_python_dependencies() {
    log "Verifying Python and Django installation"
    if ! command -v python3 &> /dev/null; then
        log "Installing Python3"
        sudo apt-get install -y python3 python3-pip
    fi
    log "Installing Django and required packages"
    sudo pip3 install django gunicorn psycopg2-binary python-dotenv
}

# Verify Node.js and git installation
verify_node_dependencies() {
    log "Verifying Node.js and npm installation"
    if ! command -v git &> /dev/null; then
        log "Git not found. Installing..."
        sudo apt-get update
        sudo apt-get install -y git
    fi
    if ! command -v node &> /dev/null; then
        log "Node.js not found. Installing..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    if ! command -v npm &> /dev/null; then
        log "npm not found. Installing..."
        sudo apt-get install -y npm
    fi
    log "Git version: $(git --version)"
    log "Node.js version: $(node --version)"
    log "npm version: $(npm --version)"
}

# Configure Nginx main configuration
configure_nginx_main() {
    log "Configuring Nginx main settings"
    local NGINX_MAIN_CONF="/etc/nginx/nginx.conf"
    sudo cp "$NGINX_MAIN_CONF" "${NGINX_MAIN_CONF}.bak"
    if ! grep -q "server_names_hash_bucket_size" "$NGINX_MAIN_CONF"; then
        sudo sed -i '/http {/a \    server_names_hash_bucket_size 128;' "$NGINX_MAIN_CONF"
    else
        sudo sed -i 's/server_names_hash_bucket_size.*/server_names_hash_bucket_size 128;/' "$NGINX_MAIN_CONF"
    fi
    log "Nginx main configuration updated"
}

# Configure Nginx for static hosting
configure_nginx_static() {
    log "Configuring Nginx for static hosting"
    configure_nginx_main
    local NGINX_CONF="/etc/nginx/sites-available/react-app"
    sudo rm -f "$NGINX_CONF" /etc/nginx/sites-enabled/react-app /etc/nginx/sites-enabled/default
    sudo tee "$NGINX_CONF" > /dev/null << EOL
server {
    listen 80 default_server;
    server_name $SERVER_NAME;
    root /var/www/html;
    index index.html;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';";
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    location /static/ {
        root /var/www/html;
        try_files \$uri \$uri/ =404;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/html;
        try_files \$uri =404;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
    location / {
        root /var/www/html;
        try_files \$uri \$uri/ /index.html;
    }
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
}
EOL
    sudo ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
}

# Main deployment process
main() {
    backup_current
    verify_python_dependencies
    verify_node_dependencies
    log "Setting permissions for Django app"
    sudo chown -R $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR"
    sudo chmod -R 755 "$DJANGO_APP_DIR"
    configure_nginx_static
    sudo systemctl restart nginx
}

main
