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
SERVER_NAME="15.207.99.95"

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

# Install dependencies
log "Installing dependencies"
sudo apt-get update
sudo apt-get install -y python3 python3-pip git

# Clone/Update repository
log "Cloning/Updating repository"
if [ ! -d "$DJANGO_APP_DIR" ]; then
    log "Creating application directory"
    sudo mkdir -p "$DJANGO_APP_DIR"
    sudo chown $DJANGO_USER:$DJANGO_GROUP "$DJANGO_APP_DIR"
fi

cd "$DJANGO_APP_DIR"
if [ -d ".git" ]; then
    log "Updating existing repository"
    sudo -u $DJANGO_USER git fetch origin
    sudo -u $DJANGO_USER git reset --hard origin/main
else
    log "Cloning new repository"
    sudo -u $DJANGO_USER git clone https://github.com/kousikmresearch/django-edu.git .
fi

# Install Python dependencies
log "Installing Python dependencies"
sudo pip3 install -r requirements.txt

# Configure Django
log "Configuring Django"
# Update database settings to use SQLite
sed -i 's/DATABASES = {.*}/DATABASES = {\n    "default": {\n        "ENGINE": "django.db.backends.sqlite3",\n        "NAME": BASE_DIR \/ "db.sqlite3",\n    }\n}/' edu/settings.py
sed -i 's/DEBUG = True/DEBUG = False/' edu/settings.py
sed -i 's/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \[\"*\"\]/' edu/settings.py

# Collect static files
log "Collecting static files"
python manage.py collectstatic --noinput

# Apply migrations
log "Applying migrations"
python manage.py migrate

# Configure Gunicorn
log "Configuring Gunicorn"
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOL
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=$DJANGO_USER
Group=$DJANGO_GROUP
WorkingDirectory=/var/www/django-app
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind unix:/var/www/django-app/edu.sock edu.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

# Configure Nginx
log "Configuring Nginx"
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

sudo mv /tmp/nginx-config /etc/nginx/sites-available/django-app

# Enable and restart services
log "Enabling and restarting services"
sudo ln -sf /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

log "Deployment completed successfully"
