#!/bin/bash
# VA Assistant Setup Script for Airgapped Deployment
# This script sets up the VA Assistant application for vulnerability analysis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="VA Assistant"
APP_DIR="/opt/va-assistant"
SERVICE_NAME="va-assistant"
VENV_DIR="$APP_DIR/venv"

echo -e "${BLUE}🔧 $APP_NAME Setup Script${NC}"
echo "This script will set up the Vulnerability Analysis Assistant for airgapped deployment."
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Function to print step headers
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print errors
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check system requirements
print_step "Checking system requirements..."

# Check for Python 3.8+
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python $PYTHON_VERSION found"

# Check for Node.js (for frontend build)
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Will skip frontend build."
    SKIP_FRONTEND=true
else
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
fi

# Check for required system packages
REQUIRED_PACKAGES=("curl" "git" "build-essential" "python3-dev" "python3-venv" "python3-pip")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    print_warning "Missing packages: ${MISSING_PACKAGES[*]}"
    echo "Installing missing packages..."
    sudo apt update
    sudo apt install -y "${MISSING_PACKAGES[@]}"
fi

print_success "System requirements check completed"

# Create application directory
print_step "Setting up application directory..."
sudo mkdir -p "$APP_DIR"
sudo chown $(whoami):$(whoami) "$APP_DIR"

# Copy application files
print_step "Copying application files..."
cp -r . "$APP_DIR/"
cd "$APP_DIR"

# Create Python virtual environment
print_step "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install Python dependencies
print_step "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend if Node.js is available
if [ "$SKIP_FRONTEND" != true ]; then
    print_step "Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    print_success "Frontend built successfully"
else
    print_warning "Skipping frontend build. You'll need to build it manually if needed."
fi

# Setup Django
print_step "Setting up Django application..."
python manage.py migrate
python manage.py collectstatic --noinput

# Create Django superuser (optional)
echo
read -p "Create Django admin user? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Creating Django superuser..."
    python manage.py createsuperuser
fi

# Create systemd service
print_step "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=VA Assistant - Vulnerability Analysis Assistant
After=network.target

[Service]
Type=exec
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
Environment=PYTHONPATH=$APP_DIR
Environment=DJANGO_SETTINGS_MODULE=va_assistant.settings
ExecStart=$VENV_DIR/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 va_assistant.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

print_success "Service created and started"

# Create nginx configuration (optional)
if command -v nginx &> /dev/null; then
    read -p "Configure Nginx reverse proxy? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Configuring Nginx..."
        sudo tee /etc/nginx/sites-available/va-assistant > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

        sudo ln -sf /etc/nginx/sites-available/va-assistant /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t && sudo systemctl reload nginx
        print_success "Nginx configured successfully"
    fi
fi

# Create log directory
sudo mkdir -p /var/log/va-assistant
sudo chown $(whoami):$(whoami) /var/log/va-assistant

# Set up log rotation
sudo tee /etc/logrotate.d/va-assistant > /dev/null <<EOF
/var/log/va-assistant/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        systemctl reload va-assistant
    endscript
}
EOF

# Create backup script
print_step "Creating backup script..."
tee "$APP_DIR/backup.sh" > /dev/null <<EOF
#!/bin/bash
# VA Assistant Backup Script

BACKUP_DIR="/opt/va-assistant-backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$BACKUP_DIR/va-assistant-\$DATE.tar.gz"

mkdir -p "\$BACKUP_DIR"

echo "Creating backup: \$BACKUP_FILE"
tar -czf "\$BACKUP_FILE" \\
    --exclude="$APP_DIR/venv" \\
    --exclude="$APP_DIR/__pycache__" \\
    --exclude="$APP_DIR/frontend/node_modules" \\
    "$APP_DIR"

echo "Backup completed: \$BACKUP_FILE"

# Keep only last 7 backups
find "\$BACKUP_DIR" -name "va-assistant-*.tar.gz" -type f -mtime +7 -delete
EOF

chmod +x "$APP_DIR/backup.sh"

# Final status check
print_step "Checking service status..."
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "VA Assistant is running successfully!"
else
    print_error "VA Assistant service failed to start"
    echo "Check logs with: journalctl -u $SERVICE_NAME -f"
    exit 1
fi

echo
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo
echo "VA Assistant is now running and accessible at:"
if command -v nginx &> /dev/null && [ -f /etc/nginx/sites-enabled/va-assistant ]; then
    echo "  🌐 http://$(hostname -I | awk '{print $1}')"
    echo "  🌐 http://localhost"
else
    echo "  🌐 http://$(hostname -I | awk '{print $1}'):8000"
    echo "  🌐 http://localhost:8000"
fi
echo
echo "Admin interface (if superuser was created):"
echo "  🔧 http://$(hostname -I | awk '{print $1}')/admin/"
echo
echo "Useful commands:"
echo "  📊 Service status: sudo systemctl status $SERVICE_NAME"
echo "  📋 View logs: journalctl -u $SERVICE_NAME -f"
echo "  🔄 Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  💾 Create backup: $APP_DIR/backup.sh"
echo
print_success "VA Assistant deployment completed!" 