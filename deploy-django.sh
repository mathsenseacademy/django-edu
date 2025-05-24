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
DJANGO_USER="django"
DJANGO_GROUP="django"

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
    # Add rollback logic here if needed
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
    
    # Install Python and pip if not installed
    if ! command -v python3 &> /dev/null; then
        log "Installing Python3"
        sudo apt-get install -y python3 python3-pip
    fi

    # Install Django and other required packages
    log "Installing Django and required packages"
    sudo pip3 install django gunicorn psycopg2-binary python-dotenv
} {
    log "Verifying Node.js and npm installation"
    
    # Check and install git
    if ! command -v git &> /dev/null; then
        log "Git not found. Installing..."
        sudo apt-get update
        sudo apt-get install -y git
    fi
    
    # Check and install Node.js
    if ! command -v node &> /dev/null; then
        log "Node.js not found. Installing..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    # Check and install npm
    if ! command -v npm &> /dev/null; then
        log "npm not found. Installing..."
        sudo apt-get install -y npm
    fi
    
    # Log versions
    log "Git version: $(git --version)"
    log "Node.js version: $(node --version)"
    log "npm version: $(npm --version)"
}

# Configure Nginx main configuration
configure_nginx_main() {
    log "Configuring Nginx main settings"
    local NGINX_MAIN_CONF="/etc/nginx/nginx.conf"
    
    # Backup the original configuration
    sudo cp "$NGINX_MAIN_CONF" "${NGINX_MAIN_CONF}.bak"
    
    # Add or update server_names_hash_bucket_size
    if ! grep -q "server_names_hash_bucket_size" "$NGINX_MAIN_CONF"; then
        sudo sed -i '/http {/a \    server_names_hash_bucket_size 128;' "$NGINX_MAIN_CONF"
    else
        sudo sed -i 's/server_names_hash_bucket_size.*/server_names_hash_bucket_size 128;/' "$NGINX_MAIN_CONF"
    fi
    
    log "Nginx main configuration updated"
}

# Deploy application
deploy_app() {
    log "Starting deployment process"
    
    # Remove existing directory if it exists
    if [ -d "$REACT_APP_DIR" ]; then
        log "Removing existing directory: $REACT_APP_DIR"
        sudo rm -rf "$REACT_APP_DIR"
        # Recreate the directory
        sudo mkdir -p "$REACT_APP_DIR"
        sudo chown $USER:$USER "$REACT_APP_DIR"
        sudo chmod 755 "$REACT_APP_DIR"
    fi
    
    # Clone the repository
    log "Cloning repository"
    cd /var/www
    git clone https://github.com/mathsenseacademy/eduapp "$REACT_APP_DIR" || handle_error $LINENO
    cd "$REACT_APP_DIR"
    
    # Verify we're in the correct directory
    if [ ! -f "package.json" ]; then
        log "Error: package.json not found in $(pwd)"
        handle_error $LINENO
    fi
    
    # Install dependencies and build
    log "Installing dependencies"
    # Clear npm cache
    npm cache clean --force
    
    # Try npm ci first, fall back to npm install if it fails
    npm ci || {
        log "npm ci failed, trying npm install"
        npm install || handle_error $LINENO
    }
    
    log "Building application"
    npm run build || handle_error $LINENO
    
    # Verify build directory exists
    if [ ! -d "build" ]; then
        log "Error: Build directory not found"
        handle_error $LINENO
    fi
    
    # Verify static directory exists in build
    if [ ! -d "build/static" ]; then
        log "Error: static directory not found in build"
        handle_error $LINENO
    fi
    
    log "Build completed successfully"
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx"
    
    # Create Django Nginx configuration
    DJANGO_NGINX_CONF="/etc/nginx/sites-available/django"
    DJANGO_NGINX_LINK="/etc/nginx/sites-enabled/django"
    
    cat > "$DJANGO_NGINX_CONF" << 'EOL'
server {
    listen 80;
    server_name $SERVER_NAME;

    location / {
        proxy_pass http://127.0.0.1:$DJANGO_PORT;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias $DJANGO_APP_DIR/static/;
    }

    location /media/ {
        alias $DJANGO_APP_DIR/media/;
    }
}
EOL

    sudo ln -sf "$DJANGO_NGINX_CONF" "$DJANGO_NGINX_LINK"
    sudo nginx -t
    sudo systemctl restart nginx

    # Configure Gunicorn service
    GUNICORN_SERVICE="/etc/systemd/system/django.service"
    
    cat > "$GUNICORN_SERVICE" << 'EOL'
[Unit]
Description=Gunicorn service for Django application
After=network.target

[Service]
User=$DJANGO_USER
Group=$DJANGO_GROUP
WorkingDirectory=$DJANGO_APP_DIR
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind unix:$DJANGO_APP_DIR/django.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

    sudo systemctl daemon-reload
    sudo systemctl enable django
    sudo systemctl restart django
} {
    log "Configuring Nginx"
    
    # Configure main Nginx settings first
    configure_nginx_main
    
    local NGINX_CONF="/etc/nginx/sites-available/react-app"
    
    # Remove existing configuration if it exists
    if [ -f "$NGINX_CONF" ]; then
        sudo rm "$NGINX_CONF"
    fi
    
    # Remove existing symlink if it exists
    if [ -L "/etc/nginx/sites-enabled/react-app" ]; then
        sudo rm "/etc/nginx/sites-enabled/react-app"
    fi
    
    # Remove default nginx site if it exists
    if [ -L "/etc/nginx/sites-enabled/default" ]; then
        sudo rm "/etc/nginx/sites-enabled/default"
    fi
    
    # Create new configuration
    sudo tee "$NGINX_CONF" > /dev/null << EOL
server {
    listen 80 default_server;
    server_name $SERVER_NAME;
    
    root /var/www/html;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';";
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Serve static files
    location /static/ {
        root /var/www/html;
        try_files \$uri \$uri/ =404;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
    
    # Serve other static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/html;
        try_files \$uri =404;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
    
    # Main application - handle all routes
    location / {
        root /var/www/html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Error pages
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
}
EOL

    # Create symlink
    sudo ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/
    
    # Test Nginx configuration
    if ! sudo nginx -t; then
        log "Error: Nginx configuration test failed"
        handle_error $LINENO
    fi
    log "Nginx configuration verified"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment"
    
    # Wait for Nginx to restart
    sleep 5
    
    # Check if Nginx is running
    if ! systemctl is-active --quiet nginx; then
        log "Error: Nginx is not running"
        handle_error $LINENO
    fi
    
    # Check if the build directory exists and has content
    if [ ! -f "$NGINX_DIR/index.html" ]; then
        log "Error: index.html not found in $NGINX_DIR"
        handle_error $LINENO
    fi
    
    # Check if static directory exists and has content
    if [ ! -d "$NGINX_DIR/static" ]; then
        log "Error: static directory not found in $NGINX_DIR"
        handle_error $LINENO
    fi
    
    # List contents of the static directory for verification
    log "Contents of static directory:"
    ls -la "$NGINX_DIR/static" | sudo tee -a "$LOG_FILE"
    
    # Check if the application is accessible
    local max_retries=3
    local retry_count=0
    local success=false
    
    while [ $retry_count -lt $max_retries ] && [ "$success" = false ]; do
        if curl -s -f "http://$SERVER_NAME" > /dev/null; then
            success=true
            log "Application is accessible"
        else
            retry_count=$((retry_count + 1))
            log "Attempt $retry_count: Application not accessible, retrying..."
            sleep 5
        fi
    done
    
    if [ "$success" = false ]; then
        log "Error: Application not accessible after $max_retries attempts"
        log "Checking Nginx error logs:"
        sudo tail -n 20 /var/log/nginx/error.log
        handle_error $LINENO
    fi
    
    log "Deployment verification successful"
}

# Main deployment process
main() {
    # Execute deployment steps
    backup_current
    verify_python_dependencies
    
    # Set proper permissions for Django app
    log "Setting permissions for Django app"
    sudo chown -R $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR"
    sudo chmod -R 755 "$DJANGO_APP_DIR"
    
    configure_nginx
    sudo systemctl restart nginx
}

# Run main function
main
