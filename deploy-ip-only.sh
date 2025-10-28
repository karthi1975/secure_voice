#!/bin/bash

# Deploy VAPI Webhook with IP Address Only (No Domain)
# Run this script on your Digital Ocean droplet

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VAPI Webhook - IP Only Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo ./deploy-ip-only.sh)${NC}"
    exit 1
fi

# Get droplet IP
DROPLET_IP=$(curl -s ifconfig.me)
echo -e "${BLUE}Droplet IP: ${GREEN}$DROPLET_IP${NC}"
echo ""

# Update system
echo -e "${YELLOW}Step 1/8: Updating system packages...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt-get update > /dev/null 2>&1
apt-get upgrade -y > /dev/null 2>&1
echo -e "${GREEN}✓ System updated${NC}"

# Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Step 2/8: Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    systemctl enable docker > /dev/null 2>&1
    systemctl start docker
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Step 3/8: Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Setup application directory
APP_DIR="/opt/secure_voice"
echo -e "${YELLOW}Step 4/8: Setting up application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}Updating repository...${NC}"
    git pull > /dev/null 2>&1
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone https://github.com/karthi1975/secure_voice.git . > /dev/null 2>&1
fi
echo -e "${GREEN}✓ Repository ready${NC}"

# Create .env file
echo -e "${YELLOW}Step 5/8: Creating environment file...${NC}"
if [ ! -f ".env" ]; then
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -base64 32)

    cat > .env << EOF
# VAPI Configuration
VAPI_API_KEY=your_vapi_api_key_here
VAPI_ASSISTANT_ID=31377f1e-dd62-43df-bc3c-ca8e87e08138

# JWT Secret
JWT_SECRET=$JWT_SECRET

# Home Assistant Configuration
HOMEASSISTANT_URL=https://ut-demo-urbanjungle.homeadapt.us
HOMEASSISTANT_WEBHOOK_ID=vapi_air_circulator

# Port
PORT=8001
EOF
    echo -e "${GREEN}✓ .env file created with auto-generated JWT secret${NC}"
    echo -e "${RED}⚠️  IMPORTANT: Edit .env file and update VAPI_API_KEY${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create simplified docker-compose for HTTP only
echo -e "${YELLOW}Step 6/8: Creating Docker configuration...${NC}"
cat > docker-compose-http.yml << 'EOF'
version: '3.8'

services:
  webhook:
    build:
      context: ./webhook_service
      dockerfile: Dockerfile
    container_name: vapi-webhook
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - VAPI_API_KEY=${VAPI_API_KEY}
      - VAPI_ASSISTANT_ID=${VAPI_ASSISTANT_ID}
      - JWT_SECRET=${JWT_SECRET}
      - HOMEASSISTANT_URL=${HOMEASSISTANT_URL:-https://ut-demo-urbanjungle.homeadapt.us}
      - HOMEASSISTANT_WEBHOOK_ID=${HOMEASSISTANT_WEBHOOK_ID:-vapi_air_circulator}
      - PORT=8001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF
echo -e "${GREEN}✓ Docker configuration created${NC}"

# Configure firewall
echo -e "${YELLOW}Step 7/8: Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw --force enable > /dev/null 2>&1
    ufw allow OpenSSH > /dev/null 2>&1
    ufw allow 8001/tcp > /dev/null 2>&1
    echo -e "${GREEN}✓ Firewall configured (ports 22, 8001)${NC}"
else
    echo -e "${YELLOW}⚠️  UFW not available, skipping firewall setup${NC}"
fi

# Build and start services
echo -e "${YELLOW}Step 8/8: Building and starting services...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"
docker-compose -f docker-compose-http.yml build > /dev/null 2>&1
docker-compose -f docker-compose-http.yml up -d

# Wait for service to be healthy
echo -e "${YELLOW}Waiting for service to start...${NC}"
sleep 10

# Check health
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Service is healthy${NC}"
else
    echo -e "${RED}✗ Service health check failed${NC}"
    echo -e "${YELLOW}Check logs: docker-compose -f docker-compose-http.yml logs${NC}"
fi

# Display summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Service Status:${NC}"
docker-compose -f docker-compose-http.yml ps
echo ""
echo -e "${BLUE}Your Webhook URLs:${NC}"
echo -e "  Health:  ${GREEN}http://$DROPLET_IP:8001/health${NC}"
echo -e "  Auth:    ${GREEN}http://$DROPLET_IP:8001/device/auth${NC}"
echo -e "  Webhook: ${GREEN}http://$DROPLET_IP:8001/webhook?device_id={{device_id}}${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NEXT STEPS:${NC}"
echo ""
echo -e "${BLUE}1. Edit your .env file:${NC}"
echo -e "   nano $APP_DIR/.env"
echo -e "   Update: ${YELLOW}VAPI_API_KEY=your_actual_key${NC}"
echo ""
echo -e "${BLUE}2. Restart services after editing .env:${NC}"
echo -e "   cd $APP_DIR"
echo -e "   docker-compose -f docker-compose-http.yml restart"
echo ""
echo -e "${BLUE}3. Update VAPI Assistant Server URL to:${NC}"
echo -e "   ${GREEN}http://$DROPLET_IP:8001/webhook?device_id={{device_id}}${NC}"
echo ""
echo -e "${BLUE}4. Test your webhook:${NC}"
echo -e "   curl http://$DROPLET_IP:8001/health"
echo ""
echo -e "${RED}⚠️  Security Warning:${NC}"
echo -e "   This deployment uses HTTP (not HTTPS)"
echo -e "   Traffic is NOT encrypted - OK for testing only"
echo -e "   For production, get a domain and setup SSL"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  View logs:    ${YELLOW}docker-compose -f docker-compose-http.yml logs -f${NC}"
echo -e "  Restart:      ${YELLOW}docker-compose -f docker-compose-http.yml restart${NC}"
echo -e "  Stop:         ${YELLOW}docker-compose -f docker-compose-http.yml down${NC}"
echo -e "  Status:       ${YELLOW}docker-compose -f docker-compose-http.yml ps${NC}"
echo ""
