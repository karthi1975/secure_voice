#!/bin/bash

# Deploy VAPI Webhook to Digital Ocean Droplet
# This script should be run on your Digital Ocean droplet

set -e

echo "🚀 Starting deployment to Digital Ocean..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/secure_voice"
REPO_URL="https://github.com/karthi1975/secure_voice.git"
DOMAIN="${DOMAIN:-localhost}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo ./deploy-to-do.sh)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Running as root${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Create app directory
echo -e "${YELLOW}Setting up application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}Updating repository...${NC}"
    git pull
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone $REPO_URL .
fi
echo -e "${GREEN}✓ Repository ready${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << 'EOF'
# VAPI Configuration
VAPI_API_KEY=your_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138

# JWT Secret (generate a random secret)
JWT_SECRET=change_this_to_a_random_secret

# Home Assistant Configuration
HOMEASSISTANT_URL=https://ut-demo-urbanjungle.homeadapt.us
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator

# Domain (for SSL certificate)
DOMAIN=your-domain.com
EOF
    echo -e "${RED}⚠️  IMPORTANT: Edit .env file with your actual credentials!${NC}"
    echo -e "${YELLOW}Run: nano $APP_DIR/.env${NC}"
    read -p "Press Enter after editing .env file..."
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Update nginx config with domain
if [ "$DOMAIN" != "localhost" ]; then
    echo -e "${YELLOW}Updating nginx configuration with domain: $DOMAIN${NC}"
    sed -i "s/your-domain.com/$DOMAIN/g" nginx/conf.d/webhook.conf
    echo -e "${GREEN}✓ Nginx config updated${NC}"
fi

# Create certbot directories
mkdir -p certbot/conf certbot/www

# Setup SSL certificate
if [ "$DOMAIN" != "localhost" ]; then
    echo -e "${YELLOW}Would you like to setup SSL certificate now? (y/n)${NC}"
    read -p "Setup SSL? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Setting up SSL certificate...${NC}"

        # Temporarily use HTTP-only nginx config
        cp nginx/conf.d/webhook.conf nginx/conf.d/webhook.conf.bak
        cat > nginx/conf.d/webhook.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://webhook:8001;
    }
}
EOF

        # Start nginx for certbot challenge
        docker-compose up -d nginx
        sleep 5

        # Get certificate
        docker-compose run --rm certbot certonly --webroot \
            --webroot-path=/var/www/certbot \
            --email admin@$DOMAIN \
            --agree-tos \
            --no-eff-email \
            -d $DOMAIN

        # Restore HTTPS nginx config
        mv nginx/conf.d/webhook.conf.bak nginx/conf.d/webhook.conf

        echo -e "${GREEN}✓ SSL certificate obtained${NC}"
    fi
fi

# Build and start containers
echo -e "${YELLOW}Building and starting Docker containers...${NC}"
docker-compose down
docker-compose build
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check health
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Webhook service is healthy${NC}"
else
    echo -e "${RED}✗ Webhook service health check failed${NC}"
    echo -e "${YELLOW}Check logs: docker-compose logs webhook${NC}"
fi

# Setup firewall
if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}Configuring firewall...${NC}"
    ufw --force enable
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo -e "${GREEN}✓ Firewall configured${NC}"
fi

# Display status
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Service Status:"
docker-compose ps
echo ""
echo "Access your webhook at:"
if [ "$DOMAIN" != "localhost" ]; then
    echo -e "${GREEN}https://$DOMAIN${NC}"
else
    echo -e "${GREEN}http://$(curl -s ifconfig.me)${NC}"
fi
echo ""
echo "Useful commands:"
echo "  View logs:           docker-compose logs -f"
echo "  Restart services:    docker-compose restart"
echo "  Stop services:       docker-compose down"
echo "  Update deployment:   cd $APP_DIR && git pull && docker-compose up -d --build"
echo ""
echo -e "${YELLOW}Don't forget to update VAPI webhook URL to:${NC}"
if [ "$DOMAIN" != "localhost" ]; then
    echo -e "${GREEN}https://$DOMAIN/webhook?device_id={{device_id}}${NC}"
else
    echo -e "${GREEN}http://$(curl -s ifconfig.me)/webhook?device_id={{device_id}}${NC}"
fi
echo ""
