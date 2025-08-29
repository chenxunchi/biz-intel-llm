# ☁️ Azure Deployment

Azure-specific deployment configurations for the Business Intelligence system.

## 📁 Files

### `app-service.yaml`
**Azure App Service deployment configuration** for Kubernetes-style deployment.

**Configuration:**
- Container specifications
- Environment variable placeholders
- Resource allocation settings
- Health check configuration

### `deploy.sh`
**Automated Azure deployment script** for streamlined production deployment.

**Features:**
- Resource group and app service creation
- Environment variable configuration
- Application deployment automation
- Post-deployment validation

## 🚀 Quick Deployment

### Automated Deployment
```bash
# Make script executable
chmod +x deploy.sh

# Deploy with your Azure settings
./deploy.sh your-app-name your-resource-group
```

### Manual Deployment Steps
```bash
# 1. Login to Azure
az login

# 2. Create resource group (if needed)
az group create --name your-rg --location eastus

# 3. Create app service plan
az appservice plan create --name your-plan --resource-group your-rg --sku B1

# 4. Create web app
az webapp create --name your-app --resource-group your-rg --plan your-plan

# 5. Deploy from project root
cd ../../
az webapp up --name your-app --resource-group your-rg
```

## ⚙️ Environment Configuration

### Required Variables
Configure these in Azure Portal → App Services → Configuration:

```bash
OPENAI_API_KEY=your_openai_api_key
AZURE_CV_KEY=your_azure_computer_vision_key
AZURE_CV_ENDPOINT=https://your-cv-resource.cognitiveservices.azure.com/
```

### Optional Variables
```bash
MAX_IMAGES_FOR_ANALYSIS=5
MIN_IMAGE_SIZE=100
MAX_SCRAPE_TIMEOUT=30
```

## 🔧 Production Settings

### Recommended App Service Configuration
- **SKU**: B1 or higher (Basic tier minimum)
- **Python Version**: 3.11+
- **Always On**: Enabled for consistent performance
- **ARR Affinity**: Disabled for better scalability

### Performance Optimization
- Enable Application Insights for monitoring
- Configure auto-scaling based on CPU/memory usage
- Set up log streaming for troubleshooting

### Security Configuration
- Configure custom domains with SSL certificates
- Enable authentication if required
- Set up IP restrictions if needed

## 📊 Monitoring

### Application Insights
- Automatic performance monitoring
- Error tracking and diagnostics
- Usage analytics and user flows

### Log Analysis
```bash
# Stream logs in real-time
az webapp log tail --name your-app --resource-group your-rg

# Download logs
az webapp log download --name your-app --resource-group your-rg
```