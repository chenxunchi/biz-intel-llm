# 🖥️ Streamlit Frontend Application

This directory contains the web interface for the Business Intelligence Risk Assessment system.

## 📁 Files

### `main.py`
**Primary Streamlit application** providing professional web interface for business intelligence analysis.

**Features:**
- Complete 3-pass pipeline integration
- Real-time analysis progress tracking
- Interactive risk visualization dashboards
- Professional results display with metrics
- Export functionality (JSON, TXT reports)
- Configuration controls for analysis parameters

**Key Functions:**
- `main()` - Primary Streamlit application entry point
- `run_complete_analysis()` - Executes full 3-pass pipeline
- `display_analysis_results()` - Comprehensive results visualization
- `generate_summary_report()` - Human-readable report generation

### `frontend/__init__.py`
Package initialization for future frontend components.

## 🚀 Usage

### Start the Application
```bash
# From project root
streamlit run app/main.py

# Application opens at http://localhost:8501
```

### Interface Overview
1. **URL Input**: Enter any business website
2. **Configuration**: Adjust analysis parameters via sidebar
3. **Analysis**: Click "Analyze Business" for complete assessment
4. **Results**: Interactive dashboard with risk charts and export options

## 🎯 Interface Features

### Analysis Configuration
- **Max Pages**: Control website crawl depth (1-15 pages)
- **Max Images**: Limit image analysis scope (1-10 images)

### Results Dashboard
- **Executive Summary**: Enhanced business description
- **Risk Assessment**: Interactive charts and detailed analysis
- **Business Classification**: NAICS codes with confidence scoring
- **Capabilities**: Text and visually-enhanced business capabilities
- **Export Options**: JSON for systems integration, TXT for reports

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Plotly**: Interactive risk visualization charts
- **Pandas**: Data manipulation for charts and exports

### Integration
Directly integrates with the complete 3-pass pipeline:
```python
from core.pipeline import BusinessIntelligencePipeline
pipeline = BusinessIntelligencePipeline()
result = pipeline.analyze_business_website(url)
```

### Performance
- **Load Time**: Near-instantaneous interface loading
- **Analysis Time**: 30-90 seconds depending on website complexity
- **Real-time Updates**: Progress tracking throughout analysis