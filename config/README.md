# ⚙️ Configuration Management

This directory contains centralized configuration management for the Business Intelligence system.

## 📁 Files

### `settings.py`
**Centralized configuration class** managing all application settings and environment variables.

**Key Features:**
- Environment variable loading with defaults
- API credential management (OpenAI, Azure)
- Analysis parameter configuration
- Deployment-ready environment handling

**Configuration Categories:**
- **LLM Settings**: OpenAI/Azure OpenAI API configuration
- **Computer Vision**: Azure CV service credentials and endpoints
- **Scraping Limits**: Timeout, page limits, content size controls
- **Analysis Parameters**: Image processing limits and quality thresholds

**Environment Variables:**
```bash
# Core API Keys
OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_KEY=your_azure_key  
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_CV_KEY=your_cv_key
AZURE_CV_ENDPOINT=https://your-cv-resource.cognitiveservices.azure.com/

# Optional Configuration
MAX_SCRAPE_TIMEOUT=30
MAX_IMAGES_PER_SITE=10
MAX_IMAGES_FOR_ANALYSIS=5
MIN_IMAGE_SIZE=100
```

### `__init__.py`
Package initialization file.

## 🛠️ Usage

### Access Configuration
```python
from config.settings import settings

# API credentials
openai_key = settings.openai_api_key
azure_cv_key = settings.azure_cv_key

# Analysis limits
max_timeout = settings.max_scrape_timeout
max_images = settings.max_images_for_analysis
```

### Environment Setup
1. Copy `.env.example` to `.env` (create if missing)
2. Configure required API keys
3. Adjust optional parameters as needed

## 🔧 Configuration Details

### Required Settings
- **LLM API**: Either OpenAI or Azure OpenAI credentials
- **Computer Vision**: Azure Cognitive Services credentials

### Optional Settings
- **Scraping Limits**: Control analysis scope and performance
- **Quality Thresholds**: Fine-tune analysis quality vs speed
- **Cache Settings**: Configure temporary data handling

### Production Considerations
- All sensitive credentials loaded from environment variables
- Reasonable defaults for all optional parameters
- Validation for required configuration items