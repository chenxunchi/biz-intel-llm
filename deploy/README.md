# 🚀 Deployment Configuration

This directory contains deployment configurations and scripts for the Business Intelligence system.

## 📁 Structure

### `/azure/` Directory
Azure-specific deployment configurations and automation scripts.

**Files:**
- `app-service.yaml` - Azure App Service deployment configuration
- `deploy.sh` - Automated Azure deployment script

## 🛠️ Deployment Options

### Azure App Service (Recommended)
```bash
# Navigate to Azure deployment directory
cd deploy/azure/

# Run automated deployment
./deploy.sh your-app-name your-resource-group
```

### Manual Azure Deployment
```bash
# Create Azure resources
az webapp create --resource-group myRG --plan myPlan --name myBusinessIntel

# Deploy application
az webapp up --name myBusinessIntel

# Configure environment variables via Azure Portal
```

### Docker Deployment
```bash
# Build container (from project root)
docker build -t business-intel .

# Run container
docker run -p 8501:8501 business-intel
```

## ⚙️ Environment Configuration

### Required Environment Variables
Set in Azure App Service → Configuration:
```bash
OPENAI_API_KEY=your_key
AZURE_CV_KEY=your_key
AZURE_CV_ENDPOINT=https://your-endpoint
```

### Optional Configuration
```bash
MAX_IMAGES_FOR_ANALYSIS=5
MIN_IMAGE_SIZE=100
MAX_SCRAPE_TIMEOUT=30
```

## 🔧 Production Considerations

### Infrastructure Requirements
- **Compute**: 2+ CPU cores, 4GB+ RAM recommended
- **Network**: Outbound HTTPS access for API calls and web scraping
- **Storage**: Minimal (stateless application)

### Security
- All API keys configured via environment variables
- No sensitive data persistence
- Outbound-only network requirements

### Monitoring
- Application logs available via Azure App Service logs
- Performance metrics through Azure Application Insights
- Health checks via `/health` endpoint (if implemented)