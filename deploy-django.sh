#!/bin/bash

# Exit on error
set -e
set -o pipefail

# Configuration
DJANGO_APP_DIR="/var/www/django-app"
NGINX_DIR="/var/www/django-app"
BACKUP_DIR="/var/www/backups"
LOG_DIR="/var/log/django"

# Default SERVER_NAME
SERVER_NAME="3.108.119.201"

# Django configuration
DJANGO_PORT=7000
DJANGO_USER="ubuntu"
DJANGO_GROUP="ubuntu"

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | sudo tee -a "$LOG_DIR/deployment.log"
}

# Error handling
handle_error() {
    local lineno=$1
    log "Error occurred at line $lineno"
    exit 1
}
trap 'handle_error $LINENO' ERR

# Main execution
log "Starting deployment"

# Create directories
log "Creating necessary directories"
sudo mkdir -p "$DJANGO_APP_DIR" "$BACKUP_DIR" "$NGINX_DIR" "$LOG_DIR"
sudo chown -R $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR" "$BACKUP_DIR" "$NGINX_DIR" "$LOG_DIR"
sudo chmod -R 755 "$DJANGO_APP_DIR" "$BACKUP_DIR" "$NGINX_DIR" "$LOG_DIR"

# Install dependencies
log "Installing dependencies"
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pkg-config \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools

# Create and activate virtual environment
log "Setting up Python virtual environment"
if [ ! -d "$DJANGO_APP_DIR/venv" ]; then
    sudo -u $DJANGO_USER python3 -m venv "$DJANGO_APP_DIR/venv"
    sudo chown -R $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR/venv"
fi

# Clone/Update repository
log "Cloning/Updating repository"
if [ ! -d "$DJANGO_APP_DIR/.git" ]; then
    # If directory exists but is not a git repository, backup and remove it
    if [ -d "$DJANGO_APP_DIR" ]; then
        log "Backing up existing directory"
        backup_timestamp=$(date +%Y%m%d_%H%M%S)
        sudo mv "$DJANGO_APP_DIR" "${DJANGO_APP_DIR}_backup_${backup_timestamp}"
    fi
    
    log "Creating fresh application directory"
    sudo mkdir -p "$DJANGO_APP_DIR"
    sudo chown $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR"
    
    log "Cloning new repository"
    cd "$DJANGO_APP_DIR"
    sudo -u $DJANGO_USER git clone https://github.com/mathsenseacademy/django-edu.git .
else
    log "Updating existing repository"
    cd "$DJANGO_APP_DIR"
    sudo -u $DJANGO_USER git fetch origin
    sudo -u $DJANGO_USER git reset --hard origin/main
fi

# Install Python dependencies in virtual environment
log "Installing Python dependencies"
sudo -u $DJANGO_USER "$DJANGO_APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u $DJANGO_USER "$DJANGO_APP_DIR/venv/bin/pip" install -r requirements.txt

# Configure Django
log "Configuring Django"
# Update database settings to use SQLite
# sed -i 's/DATABASES = {.*}/DATABASES = {\n    "default": {\n        "ENGINE": "django.db.backends.sqlite3",\n        "NAME": BASE_DIR \/ "db.sqlite3",\n    }\n}/' edu/settings.py
# sed -i 's/DEBUG = True/DEBUG = False/' edu/settings.py
# sed -i 's/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \[\"*\"\]/' edu/settings.py

# Collect static files
# log "Collecting static files"
# sudo -u $DJANGO_USER "$DJANGO_APP_DIR/venv/bin/python" manage.py collectstatic --noinput

# Apply migrations
# log "Applying migrations"
# sudo -u $DJANGO_USER "$DJANGO_APP_DIR/venv/bin/python" manage.py migrate

# Configure Gunicorn
log "Configuring Gunicorn"
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOL
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=$DJANGO_USER
Group=$DJANGO_GROUP
WorkingDirectory=$DJANGO_APP_DIR
Environment="PATH=$DJANGO_APP_DIR/venv/bin"
ExecStart=$DJANGO_APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$DJANGO_APP_DIR/edu.sock edu.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

# Configure Nginx
log "Configuring Nginx"
# Ensure Nginx directories exist
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

# Create Nginx configuration
cat > /tmp/nginx-config << "EOF"
server {
    listen 80;
    server_name $SERVER_NAME;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root /var/www/django-app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/django-app/edu.sock;
    }
}
EOF

# Ensure proxy_params exists
if [ ! -f /etc/nginx/proxy_params ]; then
    sudo tee /etc/nginx/proxy_params > /dev/null << 'EOL'
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
EOL
fi

# Move and set permissions for nginx config
sudo mv /tmp/nginx-config /etc/nginx/sites-available/django-app
sudo chown root:root /etc/nginx/sites-available/django-app
sudo chmod 644 /etc/nginx/sites-available/django-app

# Enable and restart services
log "Enabling and restarting services"
sudo ln -sf /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

log "Deployment completed successfully"
