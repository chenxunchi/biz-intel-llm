# Scripts Directory

This directory contains manual testing scripts, utilities, and one-off tools for development and validation.

## 📁 Purpose

**Scripts vs Tests:**
- **Scripts:** Manual execution, utilities, demonstrations, one-time tasks
- **Tests:** Automated, repeatable, part of CI/CD pipeline

## 🛠️ Current Scripts

### `test_image_download.py`
**Purpose:** Manually download and verify scraped images
**Usage:** 
```bash
cd scripts
python test_image_download.py
```
**Output:** Downloads sample images to `../tests/results/scraper_results/downloaded_images/`

## 🎯 Future Scripts to Add

### Performance & Benchmarking
- `benchmark_scraper.py` - Performance testing across multiple sites
- `benchmark_llm.py` - LLM response time and token usage analysis
- `stress_test.py` - Load testing for Azure deployment

### Validation & Quality
- `validate_scraped_data.py` - Manually validate scraper accuracy
- `validate_llm_output.py` - Review LLM summarization quality
- `validate_deployment.py` - Check Azure deployment health

### Development Utilities
- `generate_test_data.py` - Create synthetic test datasets
- `update_naics_codes.py` - Update NAICS code database
- `clean_test_results.py` - Clean up old test artifacts

### Demonstration Scripts
- `demo_full_pipeline.py` - End-to-end demonstration
- `demo_business_analysis.py` - Showcase business intelligence features
- `demo_azure_deployment.py` - Deployment demonstration

## 🚀 Usage Patterns

### Development Workflow
```bash
# 1. Test new functionality manually
python scripts/manual_test_new_feature.py

# 2. Create automated test based on manual testing
cp scripts/manual_test.py tests/unit/test_feature.py

# 3. Clean up results
python scripts/clean_test_results.py
```

### Validation Workflow  
```bash
# 1. Run integration tests
python tests/integration/test_scraper_live.py

# 2. Manually validate results
python scripts/validate_scraped_data.py

# 3. Generate quality report
python scripts/generate_quality_report.py
```

## 📝 Script Conventions

### File Naming
- Use descriptive names: `validate_scraper_accuracy.py`
- Include action verb: `generate_`, `validate_`, `benchmark_`, `demo_`
- Group related scripts with prefixes

### Code Structure
```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""

def main():
    """Main script function."""
    print("Script starting...")
    # Main logic here
    print("Script completed!")

if __name__ == "__main__":
    main()
```

### Documentation
- Include docstring explaining purpose
- Add usage examples in comments
- Document expected inputs/outputs