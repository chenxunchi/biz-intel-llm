# Core Business Logic Modules

This directory contains the core business intelligence processing modules for analyzing business websites and extracting insurance-relevant risk indicators.

## 📁 Module Overview

### 🕷️ `scraper.py` - Website Content Extraction
**Status:** ✅ FULLY IMPLEMENTED

**Purpose:** Ethical scraping of business websites with content discovery and robots.txt compliance.

**Key Classes:**
- `WebsiteScraper` - Main scraping functionality

**Features:**
- Text content extraction with cleaning and filtering
- Image metadata extraction (no downloads)
- Automatic page discovery via sitemap.xml and internal links
- URL normalization (handles incomplete URLs like "abc.com")
- Robots.txt compliance with domain-level caching
- Business page prioritization (about, services, products)

**Usage:**
```python
from core.scraper import WebsiteScraper

scraper = WebsiteScraper()

# Single page scraping
text = scraper.scrape_text("https://example.com")
images = scraper.scrape_images("https://example.com")

# Page discovery
pages = scraper.discover_pages("example.com", max_pages=10)
```

**Design Principles:**
- Stateless operation (no persistent storage)
- Ethical scraping with proper User-Agent
- Business-focused content filtering
- Comprehensive error handling with graceful fallbacks

---

### 🤖 `summarizer.py` - LLM Business Analysis
**Status:** 🔄 NEXT TO IMPLEMENT

**Purpose:** Generate business summaries and extract insurance risk indicators using Large Language Models.

**Planned Classes:**
- `BusinessSummarizer` - LLM-based content analysis

**Features to Implement:**
- Business summary generation from website content
- Risk indicator extraction (e-commerce, vehicle use, cyber risk)
- Integration with OpenAI API / Azure OpenAI
- Structured output parsing
- Prompt template management

**Expected Usage:**
```python
from core.summarizer import BusinessSummarizer

summarizer = BusinessSummarizer()
summary = summarizer.generate_summary(website_text)
risks = summarizer.extract_risk_indicators(website_text)
```

---

### 🏷️ `classifier.py` - NAICS Code Prediction
**Status:** 🔄 PLANNED

**Purpose:** Predict North American Industry Classification System (NAICS) codes for businesses.

**Planned Classes:**
- `NAICSClassifier` - Business industry classification

**Features to Implement:**
- NAICS code prediction from business summaries
- Model training on labeled business data
- Integration with pre-trained models (BERT, etc.)
- NAICS code description lookup

**Expected Usage:**
```python
from core.classifier import NAICSClassifier

classifier = NAICSClassifier()
naics_code = classifier.predict_naics(business_summary)
description = classifier.get_naics_description(naics_code)
```

---

### 🖼️ `image_analysis.py` - Computer Vision
**Status:** 🔄 PLANNED

**Purpose:** Analyze business images for vehicle detection and risk assessment.

**Planned Classes:**
- `ImageAnalyzer` - CV-based risk object detection

**Features to Implement:**
- Vehicle detection using YOLOv8 or Azure Computer Vision
- Risk-relevant object detection
- Image analysis integration with scraped images
- Confidence scoring and metadata extraction

**Expected Usage:**
```python
from core.image_analysis import ImageAnalyzer

analyzer = ImageAnalyzer()
vehicles = analyzer.detect_vehicles(image_url)
risk_objects = analyzer.analyze_risk_objects(image_url)
```

---

### 🛠️ `utils.py` - Shared Utilities
**Status:** 🔄 PLACEHOLDER

**Purpose:** Common utility functions used across the core modules.

**Functions to Implement:**
- URL validation and normalization helpers
- Data serialization and caching utilities
- Configuration loading helpers
- Error handling utilities

---

## 📂 Prompts Directory (`prompts/`)

### `business_summary.py` - LLM Prompt Templates
**Status:** ✅ BASIC TEMPLATES CREATED

Contains prompt templates for:
- Business summary generation
- Risk indicator extraction
- Structured output formatting

**Templates:**
- `BUSINESS_SUMMARY_PROMPT` - Main business analysis
- `RISK_EXTRACTION_PROMPT` - Insurance risk assessment

## 🔄 Data Flow Architecture

```
Input URL → scraper.py → Raw Content
                ↓
         summarizer.py → Business Summary + Risk Indicators
                ↓
         classifier.py → NAICS Code
                ↓
      image_analysis.py → Vehicle/Risk Detection
                ↓
           Final Analysis Output
```

## 🎯 Integration Patterns

### Error Handling Standard
```python
try:
    # Main processing logic
    return processed_result
except SpecificException as e:
    raise Exception(f"Module-specific error: {str(e)}")
except Exception as e:
    raise Exception(f"Unexpected error in {module_name}: {str(e)}")
```

### Configuration Access
```python
from config.settings import settings

# Access configuration values
api_key = settings.openai_api_key
timeout = settings.max_scrape_timeout
```

### Logging Pattern
```python
from monitor.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Processing started")
logger.error("Error occurred", exc_info=True)
```

## 🧪 Testing Strategy

Each module follows the testing pattern established in `tests/test_scraper.py`:
- Unit tests with mocked external dependencies
- Comprehensive error case coverage
- Integration testing for data flow
- Performance testing for large inputs

**Test Files:**
- `tests/test_scraper.py` ✅ (Complete)
- `tests/test_summarizer.py` 🔄 (To create)
- `tests/test_classifier.py` 🔄 (To create)
- `tests/test_image_analysis.py` 🔄 (To create)

## 🚀 Development Priority

**Next Implementation Order:**
1. **`summarizer.py`** - Core LLM integration (IMMEDIATE)
2. **`classifier.py`** - NAICS prediction
3. **`image_analysis.py`** - Computer vision
4. **Integration pipeline** - End-to-end workflow

## 📋 Dependencies

**Current Requirements:**
- `requests` - HTTP client for scraping
- `beautifulsoup4` - HTML parsing
- `openai` / `azure-openai` - LLM integration
- `ultralytics` - YOLOv8 for vehicle detection
- `transformers` - BERT models for classification

**Configuration:**
All modules use centralized configuration from `config/settings.py` with environment variable support.