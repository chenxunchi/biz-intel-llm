# Core Business Intelligence Modules

This directory contains the complete **3-pass business intelligence system** for analyzing business websites and extracting comprehensive intelligence for insurance underwriting.

## 🎯 3-Pass Analysis Architecture

The system implements a sophisticated 3-pass pipeline that combines text analysis, computer vision, and intelligent integration:

```
URL Input → Website Scraping → Pass 1 (Text) → Pass 2 (Images) → Pass 3 (Integration) → Final Analysis
```

---

## 📁 Module Overview

### 🕷️ `scraper.py` - Website Content Extraction
**Status:** ✅ FULLY IMPLEMENTED (Production Ready)

**Purpose:** Ethical scraping of business websites with unified output structure optimized for downstream AI analysis.

**Key Classes:**
- `WebsiteScraper` - Main scraping functionality with comprehensive business intelligence
- `ScrapingOptions` - Configuration for scraping behavior
- `PageData` - Individual page results with metadata
- `BusinessData` - Complete unified business data structure

**Advanced Features:**
- Unified business intelligence output with quality scoring
- Smart page discovery (sitemap.xml + internal links)
- Business page prioritization and classification
- URL normalization and robots.txt compliance
- Comprehensive error handling with graceful degradation

---

### 🤖 `summarizer.py` - Pass 1: Text Analysis & NAICS Prediction
**Status:** ✅ FULLY IMPLEMENTED (Production Ready)

**Purpose:** Comprehensive text analysis using LLM with business understanding, NAICS classification, and risk assessment.

**Key Classes:**
- `BusinessSummarizer` - LLM-powered business analysis
- `TextAnalysisResult` - Structured text analysis output

**Advanced Features:**
- **Business Intelligence Extraction**: Domain, scale, services, capabilities
- **NAICS Classification**: 6-digit codes with confidence scoring (0.0-1.0)
- **Text-Based Risk Assessment**: E-commerce, vehicle use, cyber risk with evidence
- **Multi-Factor Confidence Scoring**: Website quality + specificity + keyword alignment
- **OpenAI/Azure OpenAI Integration**: Flexible LLM backend support

**Usage:**
```python
from core.summarizer import BusinessSummarizer

summarizer = BusinessSummarizer()
text_analysis = summarizer.analyze_business(scraped_business_data)

# Access results
print(f"Domain: {text_analysis.business_domain}")
print(f"NAICS: {text_analysis.naics_code} (confidence: {text_analysis.naics_confidence:.1%})")
print(f"Risks: {text_analysis.text_risk_indicators}")
```

---

### 🖼️ `image_analysis.py` - Pass 2: Computer Vision Analysis  
**Status:** ✅ FULLY IMPLEMENTED (Production Ready)

**Purpose:** Azure Computer Vision-based analysis for visual business intelligence and risk assessment.

**Key Classes:**
- `ImageAnalyzer` - Azure CV-powered image analysis
- `VisualAnalysisResult` - Comprehensive visual analysis output
- `ImageFilterResult` - Business-relevant image filtering results

**Advanced Features:**
- **Business-Relevant Image Filtering**: Domain-specific scoring and prioritization
- **Equipment & Vehicle Detection**: Context-aware object recognition
- **Facility Analysis**: Scale and type assessment from visual evidence
- **Visual Risk Indicators**: Equipment risk, facility risk assessment
- **Business Capability Enhancement**: Visual evidence → additional business capabilities

**Usage:**
```python
from core.image_analysis import ImageAnalyzer

analyzer = ImageAnalyzer()
visual_analysis = analyzer.analyze_business_images(scraped_data, text_analysis)

# Access results
print(f"Equipment Detected: {visual_analysis.visual_business_insights['equipment_detected']}")
print(f"Vehicle Risk: {visual_analysis.image_risk_indicators['vehicle_use']['level']}")
```

---

### 🔄 `pipeline.py` - Pass 3: Integration & Orchestration
**Status:** ✅ FULLY IMPLEMENTED (Production Ready)

**Purpose:** Complete 3-pass pipeline orchestration with intelligent risk aggregation and enhanced analysis.

**Key Classes:**
- `BusinessIntelligencePipeline` - Complete system orchestration
- `FinalBusinessAnalysis` - Final integrated analysis output

**Advanced Features:**
- **Intelligent Risk Aggregation**: Type-specific rules (vehicle: MAX, e-commerce: text-primary)
- **Enhanced Summary Generation**: LLM-powered integration of text + visual insights
- **Confidence Boosting**: Cross-validation between text and visual evidence
- **Graceful Fallbacks**: Robust error handling with meaningful fallback results
- **Comprehensive Metadata**: Complete pipeline execution tracking

**Usage:**
```python
from core.pipeline import BusinessIntelligencePipeline

# Complete end-to-end analysis
pipeline = BusinessIntelligencePipeline()
final_analysis = pipeline.analyze_business_website("https://example-business.com")

# Access comprehensive results
print(f"Enhanced Summary: {final_analysis.enhanced_business_summary}")
print(f"Final Risks: {final_analysis.final_risk_indicators}")
print(f"All Capabilities: {final_analysis.business_capabilities}")
```

---

### 🛠️ `utils.py` - Shared Utilities
**Status:** ✅ IMPLEMENTED (Production Ready)

**Purpose:** Common utility functions for URL handling, text processing, and data management.

**Key Functions:**
- `validate_url()` - URL validation and normalization
- `clean_business_text()` - Text cleaning and preprocessing  
- `save_analysis_results()` - JSON serialization for results
- `format_confidence_score()` - User-friendly confidence formatting
- `extract_domain_from_url()` - Domain extraction utilities

---

## 📂 Prompts Directory (`prompts/`)

### `business_summary.py` - Enhanced LLM Prompt Templates
**Status:** ✅ FULLY IMPLEMENTED (Production Ready)

**Advanced Prompt Templates:**
- `BUSINESS_ANALYSIS_PROMPT` - Comprehensive text analysis with structured JSON output
- `BUSINESS_INTEGRATION_PROMPT` - Text + visual integration for enhanced summaries
- `IMAGE_ANALYSIS_CONTEXT` - Business context for image analysis
- `NAICS_CONFIDENCE_FACTORS` - Confidence scoring guidelines

**Features:**
- Structured JSON response formatting
- Multi-factor confidence assessment instructions
- Business intelligence extraction guidelines
- Risk-specific evidence requirements

---

## 🔄 Intelligent Data Flow

### **3-Pass Processing Pipeline:**
```
1. BusinessData (scraper) → 2. TextAnalysisResult (summarizer) → 3. VisualAnalysisResult (image_analysis) → 4. FinalBusinessAnalysis (pipeline)
```

### **Risk Aggregation Logic:**
- **Vehicle Use**: `MAX(text_level, visual_level)` - Visual evidence often overrides
- **E-commerce**: `text_level` (primary) - Visual rarely provides e-commerce evidence  
- **Cyber Risk**: `text_level` (only) - Visual provides minimal cyber insight

### **Confidence Enhancement:**
- Text + Visual alignment → +0.2 confidence boost
- Cross-validation between evidence sources
- Multi-factor scoring (quality + specificity + keyword match)

---

## 📊 Output Data Structures

### **Final Analysis Output (`FinalBusinessAnalysis`):**
```python
{
    "enhanced_business_summary": "Professional landscaping company with commercial fleet...",
    "naics_code": "561730",
    "naics_confidence": 0.87,
    "final_risk_indicators": {
        "vehicle_use": {
            "level": "High",
            "confidence": 0.95, 
            "primary_source": "visual",
            "evidence": ["commercial trucks detected"],
            "reasoning": "Visual confirmation overrides text assessment"
        }
    },
    "business_capabilities": ["lawn care", "heavy equipment operations"],
    "visual_enhancements": ["heavy equipment operations"],
    "pipeline_metadata": { /* comprehensive execution info */ }
}
```

---

## 🧪 Testing Strategy

### **Comprehensive Test Coverage (`tests/test_business_intelligence.py`):**
- ✅ **Pass 1 Testing**: Text analysis with mocked LLM responses
- ✅ **Pass 2 Testing**: Image analysis with mocked Azure CV
- ✅ **Pass 3 Testing**: Integration logic and risk aggregation rules
- ✅ **End-to-End Testing**: Complete pipeline scenarios
- ✅ **Error Handling**: Fallback scenarios and graceful degradation
- ✅ **Confidence Scoring**: NAICS and risk confidence validation

### **Testing Patterns:**
```python
# Example test pattern with comprehensive mocking
@patch('core.summarizer.openai.ChatCompletion.create')
@patch('core.image_analysis.ComputerVisionClient')
def test_complete_pipeline(self, mock_cv, mock_llm):
    # Setup mocks with realistic responses
    # Execute pipeline
    # Assert comprehensive results
```

---

## ⚙️ Configuration & Dependencies

### **Environment Variables:**
```bash
# Required: LLM API
OPENAI_API_KEY=your_key  # OR Azure OpenAI credentials

# Required: Computer Vision  
AZURE_CV_KEY=your_azure_cv_key
AZURE_CV_ENDPOINT=your_azure_cv_endpoint

# Optional: Analysis tuning
MAX_IMAGES_FOR_ANALYSIS=5
MIN_IMAGE_SIZE=100
LLM_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.3
```

### **Key Dependencies:**
- `openai` - LLM integration for text analysis
- `azure-cognitiveservices-vision-computervision` - Image analysis
- `requests` + `beautifulsoup4` - Web scraping
- `dataclasses` - Structured data management

---

## 🔧 Integration Patterns

### **Error Handling Standard:**
```python
try:
    # Main processing logic
    return processed_result
except SpecificException as e:
    raise Exception(f"Pass-specific error: {str(e)}")
except Exception as e:
    # Graceful fallback with meaningful error info
    return create_fallback_result(error_message=str(e))
```

### **Configuration Access:**
```python
from config.settings import settings

# Centralized configuration access
api_key = settings.openai_api_key
cv_endpoint = settings.azure_cv_endpoint
max_images = settings.max_images_for_analysis
```

---

## 🚀 Production Ready Status

All core modules are **production-ready** with:
- ✅ Comprehensive error handling and graceful fallbacks
- ✅ Extensive test coverage with mocked external dependencies
- ✅ Flexible configuration system with environment variables
- ✅ Performance optimization and resource management
- ✅ Complete documentation and usage examples

**Ready for Phase 4:** Streamlit frontend integration and deployment.