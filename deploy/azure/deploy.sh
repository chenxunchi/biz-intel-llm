#!/bin/bash
# Quick Azure deployment script for testing the scraper

set -e

# Simple configuration
RESOURCE_GROUP="biz-intel-test-rg"
APP_NAME="biz-intel-scraper-test"
LOCATION="East US"
RUNTIME="PYTHON:3.11"

echo "🚀 Quick Deploy: Business Intelligence Scraper Test"
echo "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Install from: https://aka.ms/installazurecliwindows"
    exit 1
fi

# Login check
if ! az account show &> /dev/null; then
    echo "🔐 Logging into Azure..."
    az login
fi

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  App Name: $APP_NAME"
echo "  Location: $LOCATION"
echo ""

# Deploy in one command (creates everything)
echo "🚀 Deploying..."
az webapp up \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --runtime $RUNTIME \
    --sku F1 \
    --location "$LOCATION"

# Get the URL
APP_URL="https://$APP_NAME.azurewebsites.net"
echo ""
echo "✅ Deployment complete!"
echo "🌐 Test URL: $APP_URL"
echo ""
echo "🧪 Ready to test:"
echo "  1. Open: $APP_URL"
echo "  2. Enter a website URL (e.g., 'example.com')"
echo "  3. Click 'Full Analysis' to test scraper"
echo ""
echo "📊 Monitor logs:"
echo "  az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"