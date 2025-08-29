# 🧪 Testing & Utility Scripts

This directory contains testing and utility scripts for development and validation.

## 📁 Files

### `test_unified_scraper.py`
**Live website validation script** for testing the complete scraping pipeline with real business websites.

**Purpose:**
- Validates scraper functionality on actual business websites
- Tests content extraction quality and completeness
- Verifies image discovery and filtering
- Generates detailed test reports with metrics

**Usage:**
```bash
# Run live website tests
python scripts/test_unified_scraper.py

# Outputs detailed analysis including:
# - Pages discovered and scraped
# - Text content extraction metrics
# - Image discovery and filtering results
# - Performance timing data
```

**Test Scenarios:**
- Coffee shop websites (service businesses)
- Landscaping companies (equipment-heavy businesses)
- Plumbing services (fleet-based businesses)

## 🛠️ Script Usage

### Development Testing
```bash
# Test scraper on new business types
python scripts/test_unified_scraper.py

# Validate changes after scraper modifications
python scripts/test_unified_scraper.py
```

### Performance Benchmarking
The script provides comprehensive metrics:
- **Page Discovery**: Number of business-relevant pages found
- **Content Quality**: Text extraction success rates and content volume
- **Image Analysis**: Relevant image detection and filtering effectiveness
- **Performance**: Timing data for optimization

## 📈 Test Results Interpretation

### Successful Scraping Indicators
- **Multiple pages discovered** (5+ pages typical for businesses)
- **High content volume** (2,000+ characters per page)
- **Business-relevant images** found and properly filtered
- **Fast execution** (under 30 seconds for discovery + scraping)

### Quality Metrics
- **Text Content**: Should extract meaningful business descriptions
- **Image Filtering**: Should find equipment, facility, or business operation images
- **Page Prioritization**: Should discover About, Services, Contact pages

## 🔧 Development Guidelines

### Adding New Test Scripts
1. Follow naming convention: `test_[component]_[purpose].py`
2. Include comprehensive output and metrics
3. Handle errors gracefully with informative messages
4. Document expected results and success criteria

### Script Maintenance
- Update test URLs if business websites change
- Validate scripts after major scraper modifications
- Ensure scripts work with current API and data structures