# Core Business Logic Modules

This directory contains the core business intelligence processing modules for analyzing business websites and extracting insurance-relevant risk indicators.

## 📁 Module Overview

### 🕷️ `scraper.py` - Website Content Extraction
**Status:** ✅ FULLY IMPLEMENTED (v2.0 - Unified Output)

**Purpose:** Ethical scraping of business websites with unified output structure for LLM integration.

**Key Classes:**
- `WebsiteScraper` - Main scraping functionality with unified output
- `ScrapingOptions` - Configuration dataclass for scraping behavior
- `PageData` - Individual page scraping results
- `BusinessData` - Complete business analysis results

**Features:**
- **🎯 Unified Output Architecture** - Single method provides complete business data
- Text content extraction with cleaning and filtering
- Image metadata extraction (URLs, alt text, dimensions)
- Automatic page discovery via sitemap.xml and internal links
- URL normalization (handles incomplete URLs like "abc.com")
- Robots.txt compliance with domain-level caching
- Business page prioritization and type classification
- **📊 Business Intelligence Computation** - Automatic quality scoring and metrics
- **🔧 Structured Data Format** - LLM-ready JSON output

## 📥📤 INPUT/OUTPUT SPECIFICATION

### **🚀 Primary Method: `scrape_business()`**

**Input:**
```python
from core.scraper import WebsiteScraper, ScrapingOptions

# Configuration options
options = ScrapingOptions(
    max_pages=10,           # Maximum pages to discover and scrape
    include_images=True,    # Whether to extract image metadata
    timeout_per_page=30,    # Timeout per page in seconds
    page_types=[            # Page types to include
        "about", "services", "contact", "home", "other"
    ]
)

# Single method call
scraper = WebsiteScraper()
result = scraper.scrape_business("example.com", options)
```

**Output Structure:**
```python
BusinessData {
    business_url: str              # Normalized input URL
    scraped_at: datetime          # When scraping started
    scraping_metadata: {          # Process metadata
        "scraping_session": {
            "started_at": "2024-01-01T10:00:00",
            "completed_at": "2024-01-01T10:02:30", 
            "total_duration_seconds": 150.5
        },
        "page_processing": {
            "total_pages_attempted": 8,
            "successful_pages": 7,
            "failed_pages": 1,
            "success_rate": 0.875
        },
        "errors": ["Page timeout: /large-gallery"],
        "performance": {
            "avg_time_per_page": 18.8,
            "pages_per_minute": 3.2
        }
    },
    pages: [PageData...]          # Individual page results
    business_intelligence: {      # Computed business metrics
        "scraping_metrics": {
            "total_pages_found": 8,
            "successful_pages": 7, 
            "failed_pages": 1,
            "success_rate": 0.875
        },
        "content_metrics": {
            "total_text_length": 45230,
            "total_images": 23,
            "avg_text_per_page": 6461,
            "avg_images_per_page": 3.3
        },
        "page_analysis": {
            "page_types_found": ["home", "about", "services", "contact"],
            "key_pages_present": {
                "has_about": true,
                "has_services": true, 
                "has_contact": true,
                "has_home": true
            },
            "content_quality_score": 0.87
        },
        "errors": ["Timeout on gallery page"]
    }
}
```

**Individual Page Data Structure:**
```python
PageData {
    url: str                      # Full page URL
    page_type: str                # "about" | "services" | "contact" | "home" | "other"
    text_content: str             # Cleaned text content
    text_length: int              # Character count
    images: [                     # Image metadata only (no downloads)
        {
            "url": "https://example.com/photo.jpg",
            "alt_text": "Team photo",
            "title": "Our team",
            "width": "300",
            "height": "200"
        }
    ],
    scraped_at: datetime          # When this page was processed
    scrape_success: bool          # Whether scraping succeeded
    error_message: str | None     # Error details if failed
}
```

### **📊 Business Intelligence Metrics**

The unified output automatically computes:
- **Success Rate:** Percentage of pages successfully scraped
- **Content Quality Score:** 0.0-1.0 based on text richness, images, key pages
- **Page Type Analysis:** Classification and completeness assessment
- **Performance Metrics:** Speed and efficiency measurements

### **🔄 Legacy Methods (Still Available)**

Individual scraping methods remain available for specific use cases:
```python
# Legacy individual methods
text = scraper.scrape_text("https://example.com")
images = scraper.scrape_images("https://example.com") 
pages = scraper.discover_pages("example.com", max_pages=10)
```

### **✨ Unified vs Legacy Comparison**

| Aspect | Legacy Approach | 🆕 Unified Approach |
|--------|----------------|-------------------|
| **Method Calls** | Multiple (`scrape_text`, `scrape_images`, `discover_pages`) | Single (`scrape_business`) |
| **Output Format** | Fragmented strings and lists | Structured `BusinessData` object |
| **Error Handling** | Manual coordination required | Automatic graceful handling |
| **Metadata** | None | Rich scraping and performance metrics |
| **LLM Integration** | Manual data preparation | Ready-to-use JSON structure |
| **Business Intelligence** | Manual computation | Automatic quality scoring |

**Design Principles:**
- 🎯 **LLM-First Design** - Output optimized for language model consumption
- 🔧 **Unified Interface** - Single method call for complete business analysis
- 📊 **Rich Metadata** - Built-in quality assessment and performance metrics
- 🛡️ **Graceful Degradation** - Partial failures don't break entire process
- ⚡ **Performance Aware** - Built-in timing and efficiency measurements

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