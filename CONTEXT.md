# Business Intelligence Risk Assessment - Project Context

## 📊 Project Overview
End-to-end AI system that analyzes business websites to extract insurance underwriting risk indicators.

**Input:** Business website URL
**Output:** 
- Business summary
- NAICS code prediction
- Risk indicators (e-commerce, vehicle use, cyber risk)

## 🎯 Current Status (Session End)

### ✅ COMPLETED COMPONENTS

#### 1. Project Structure
- Complete folder architecture with all directories
- Configuration management system (`config/settings.py`)
- Proper Python package structure with `__init__.py` files
- Docker and deployment configurations ready

#### 2. Website Scraper (`core/scraper.py`) - FULLY IMPLEMENTED
**Features:**
- ✅ Text scraping with content cleaning
- ✅ Image scraping with metadata extraction  
- ✅ Robots.txt compliance with domain caching
- ✅ Sitemap.xml discovery and parsing
- ✅ Internal link discovery from homepage
- ✅ URL normalization (handles "abc.com" → "https://www.abc.com")
- ✅ Business page prioritization
- ✅ Comprehensive error handling

**Key Methods:**
```python
scraper = WebsiteScraper()
text = scraper.scrape_text(url)                    # Returns cleaned text
images = scraper.scrape_images(url)                # Returns image metadata
pages = scraper.discover_pages(base_url, max=10)   # Returns prioritized URLs
```

**Design Principles:**
- Stateless operation (no file storage)
- Ethical scraping with robots.txt compliance
- Business-focused filtering (excludes login, admin, blog pages)
- Azure-ready architecture

#### 3. Test Suite (`tests/test_scraper.py`) - COMPREHENSIVE
- ✅ Unit tests for all scraper functionality
- ✅ Mocked HTTP requests for reliable testing
- ✅ Robots.txt compliance testing
- ✅ URL normalization testing
- ✅ Error handling verification

#### 4. Git Workflow
- ✅ Main branch for stable releases
- ✅ Dev branch for ongoing development
- ✅ All work committed and pushed to GitHub

### ✅ COMPLETED IMPLEMENTATION (Latest Session)

### 🎯 3-Pass Business Intelligence System - FULLY IMPLEMENTED

#### ✅ Pass 1: Text Analysis (`core/summarizer.py`)
**Implemented Features:**
- `BusinessSummarizer` class with comprehensive text analysis
- NAICS code prediction with confidence scoring
- Risk indicator extraction (e-commerce, vehicle use, cyber risk)
- Business capability identification
- Integration with OpenAI API / Azure OpenAI

**Key Methods:**
```python
class BusinessSummarizer:
    def analyze_business(self, business_data: BusinessData) -> TextAnalysisResult
    def _calculate_naics_confidence(self, naics_code, text_content, quality_score) -> float
```

#### ✅ Pass 2: Image Analysis (`core/image_analysis.py`) 
**Implemented Features:**
- `ImageAnalyzer` class with Azure Computer Vision integration
- Business-relevant image filtering and prioritization
- Equipment, vehicle, and facility detection
- Visual risk indicator generation
- Business capability enhancement from visual evidence

**Key Methods:**
```python
class ImageAnalyzer:
    def analyze_business_images(self, business_data, text_analysis) -> VisualAnalysisResult
    def _filter_business_images(self, business_data, text_analysis) -> ImageFilterResult
```

#### ✅ Pass 3: Integration Pipeline (`core/pipeline.py`)
**Implemented Features:**
- `BusinessIntelligencePipeline` class for complete orchestration
- Intelligent risk aggregation with type-specific rules
- Enhanced summary generation using visual insights
- Comprehensive error handling and fallback scenarios
- Complete business intelligence output

**Key Methods:**
```python
class BusinessIntelligencePipeline:
    def analyze_business_website(self, website_url: str) -> FinalBusinessAnalysis
    def _aggregate_risk_indicators(self, text_risks, visual_risks) -> Dict
```

### 🏗️ Enhanced Architecture Implemented

#### **3-Pass System Flow:**
```
URL → Pass 1 (Text) → Pass 2 (Images) → Pass 3 (Integration) → Final Analysis
```

#### **Pass 1 Output:**
```python
TextAnalysisResult:
├── business_summary: str
├── business_domain: str  
├── naics_code: str
├── naics_confidence: float (text-based)
├── primary_services: List[str]
├── business_scale: str
├── text_risk_indicators: Dict
└── text_capabilities: List[str]
```

#### **Pass 2 Output:**
```python
VisualAnalysisResult:
├── visual_business_insights: Dict
│   ├── equipment_detected: List
│   ├── vehicle_types: List
│   ├── facility_characteristics: List
│   └── capability_enhancements: List
├── image_risk_indicators: Dict
└── analysis_metadata: Dict
```

#### **Pass 3 Final Output:**
```python
FinalBusinessAnalysis:
├── enhanced_business_summary: str (text + visual insights)
├── naics_code: str
├── naics_confidence: float (unchanged from Pass 1)
├── final_risk_indicators: Dict (intelligently aggregated)
│   └── Each risk: {level, confidence, primary_source, evidence, reasoning}
├── business_capabilities: List[str] (combined & deduplicated)
├── visual_enhancements: List[str] 
└── pipeline_metadata: Dict (comprehensive execution info)
```

### 🧠 Intelligent Risk Aggregation Rules

#### **Vehicle Use Risk:** MAX(text_level, visual_level)
- Visual evidence often overrides text descriptions
- High confidence boost when both sources align

#### **E-commerce Risk:** Primarily text_level  
- Visual evidence rarely provides e-commerce insights
- Text analysis is the primary source

#### **Cyber Risk:** Text_level only
- Visual analysis provides minimal cyber risk insight
- Business model analysis from text is key

### 🔧 Advanced Features Implemented

#### **Image Filtering & Business Relevance Scoring:**
- Domain-specific keyword matching
- Page type relevance weighting  
- Size and quality filtering
- Business context prioritization

#### **NAICS Confidence Scoring:**
- Website quality factor (0-0.4)
- Business description specificity (0-0.4)  
- Industry keyword matching (0-0.2)
- Comprehensive confidence interpretation

#### **Enhanced Prompt Engineering:**
- Structured JSON response templates
- Business intelligence context integration
- Risk-specific evidence extraction
- Multi-modal integration prompts

### 🧪 Comprehensive Test Suite (`tests/test_business_intelligence.py`)
**Implemented Test Coverage:**
- ✅ Pass 1: Text analysis functionality
- ✅ Pass 2: Image analysis with mocked Azure CV
- ✅ Pass 3: Pipeline integration and risk aggregation
- ✅ End-to-end integration scenarios
- ✅ Error handling and fallback cases
- ✅ NAICS confidence calculation
- ✅ Risk aggregation rules validation

### ⚙️ Configuration Enhancements
**Added to `config/settings.py`:**
```python
# Azure Computer Vision
self.azure_cv_key: Optional[str] = os.getenv("AZURE_CV_KEY")
self.azure_cv_endpoint: Optional[str] = os.getenv("AZURE_CV_ENDPOINT")

# Image Analysis Settings  
self.max_images_for_analysis: int = int(os.getenv("MAX_IMAGES_FOR_ANALYSIS", "5"))
self.min_image_size: int = int(os.getenv("MIN_IMAGE_SIZE", "100"))
```

**Updated `requirements.txt`:**
```
azure-cognitiveservices-vision-computervision>=0.9.0
azure-common>=1.1.28
```

## 🚀 READY FOR PRODUCTION

### **How to Use the Complete System:**
```python
from core.pipeline import BusinessIntelligencePipeline

# Initialize pipeline
pipeline = BusinessIntelligencePipeline()

# Analyze any business website  
result = pipeline.analyze_business_website("https://example-business.com")

# Access complete analysis
print(f"Business: {result.enhanced_business_summary}")
print(f"NAICS: {result.naics_code} (confidence: {result.naics_confidence})")
print(f"Risk Indicators: {result.final_risk_indicators}")
print(f"Capabilities: {result.business_capabilities}")
```

## 🎯 NEXT DEVELOPMENT PHASES

### Phase 4: Streamlit Frontend Integration
- Integrate pipeline with `app/main.py`
- Create interactive user interface
- Display results with visualizations

### Phase 5: Azure Deployment
- Deploy complete system to Azure App Service
- Configure environment variables for production
- Set up monitoring and logging

### Phase 6: Performance Optimization
- Implement caching for repeated analyses
- Optimize API call efficiency
- Add batch processing capabilities

## 🛠️ Technical Architecture

### Current Stack
- **Language:** Python 3.11+
- **Web Framework:** Streamlit (frontend)
- **LLM:** OpenAI API / Azure OpenAI
- **Scraping:** requests + BeautifulSoup
- **Testing:** unittest with mocking
- **Deployment:** Azure App Service / Container Apps

### Configuration System
**Environment Variables:** (`.env.example`)
```
OPENAI_API_KEY=your_key
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
MAX_SCRAPE_TIMEOUT=30
MAX_IMAGES_PER_SITE=10
```

**Settings Management:** (`config/settings.py`)
- Centralized configuration
- Environment variable loading
- Default values for all settings

### Data Flow Design
```
URL Input → Scraper → Text/Images → LLM → Summary/Risks → NAICS → Final Analysis
```

**No Persistent Storage:** All processing in memory, stateless design

## 📁 Key Files to Continue With

### Immediate Work Files
1. `core/summarizer.py` - Main LLM integration (START HERE)
2. `core/prompts/business_summary.py` - Enhance prompt templates
3. `core/classifier.py` - NAICS prediction logic
4. `app/main.py` - Streamlit frontend integration

### Reference Files
1. `core/scraper.py` - Fully implemented, reference for patterns
2. `tests/test_scraper.py` - Testing patterns to follow
3. `config/settings.py` - Configuration access
4. `requirements.txt` - Dependencies list

## 🎯 Week 3 Goals (Current Week per README plan)
- ✅ Website scraper (COMPLETED)
- 🔄 LLM summarizer integration (NEXT)
- 🔄 Risk indicator extraction (NEXT)
- 🔄 Structured output parsing (NEXT)

## 🔍 Development Patterns Established

### Error Handling Pattern
```python
try:
    # Main logic
    return result
except SpecificException as e:
    raise Exception(f"Descriptive error: {str(e)}")
except Exception as e:
    raise Exception(f"Unexpected error: {str(e)}")
```

### Testing Pattern
```python
@patch('module.requests.Session.get')
def test_functionality(self, mock_get):
    mock_response = Mock()
    mock_response.content = test_content
    mock_get.return_value = mock_response
    # Test logic
```

### Configuration Access
```python
from config.settings import settings
timeout = settings.max_scrape_timeout
api_key = settings.openai_api_key
```

## 🚀 Ready for Tomorrow
- Project structure is solid
- Scraper is production-ready
- Clear next steps defined
- All code committed and pushed
- Testing patterns established

**Start tomorrow with:** Implementing `BusinessSummarizer` class in `core/summarizer.py`