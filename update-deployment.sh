#!/bin/bash

# Quick update script for Digital Ocean deployment
# Run this on your droplet to update the webhook service

set -e

APP_DIR="/opt/secure_voice"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔄 Updating secure_voice deployment...${NC}"

cd $APP_DIR

# Backup current .env
if [ -f .env ]; then
    cp .env .env.backup
    echo -e "${GREEN}✓ Backed up .env file${NC}"
fi

# Pull latest code
echo -e "${YELLOW}Pulling latest code...${NC}"
git pull

# Restore .env if it was overwritten
if [ -f .env.backup ]; then
    mv .env.backup .env
    echo -e "${GREEN}✓ Restored .env file${NC}"
fi

# Rebuild and restart containers
echo -e "${YELLOW}Rebuilding containers...${NC}"
docker-compose down
docker-compose build
docker-compose up -d

# Wait for health check
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check health
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Deployment updated successfully!${NC}"
    docker-compose ps
else
    echo -e "${RED}✗ Health check failed. Check logs:${NC}"
    echo "  docker-compose logs webhook"
    exit 1
fi
