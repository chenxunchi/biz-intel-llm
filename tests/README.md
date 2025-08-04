# Testing Directory

This directory contains all automated and integration tests for the Business Intelligence Risk Assessment system.

## 📁 Structure

### `unit/` - Fast Unit Tests
- **Purpose:** Isolated, mocked tests for individual components
- **Speed:** Fast (< 1 second each)
- **Dependencies:** No external APIs or network calls
- **CI/CD:** Run on every commit

**Files:**
- `test_scraper.py` - Unit tests for scraper module with mocked HTTP requests
- `test_summarizer.py` - Unit tests for LLM summarizer (future)
- `test_classifier.py` - Unit tests for NAICS classifier (future)

### `integration/` - Real API/Network Tests
- **Purpose:** Test actual functionality with real websites/APIs
- **Speed:** Slower (10-60 seconds each)
- **Dependencies:** Live internet, real APIs
- **CI/CD:** Run on releases or manually

**Files:**
- `test_scraper_live.py` - Live website scraping tests
- `test_llm_integration.py` - Real LLM API integration tests (future)
- `test_end_to_end.py` - Complete pipeline tests (future)

### `results/` - Test Output Storage
- **Purpose:** Store test results, reports, and artifacts
- **Organization:** Organized by module and test type
- **Usage:** Reference data, debugging, benchmarking

**Structure:**
```
results/
├── scraper_results/     # Scraper test outputs
├── llm_results/         # LLM test outputs (future)
└── reports/             # Generated test reports
```

## 🚀 Running Tests

### Unit Tests (Fast)
```bash
# Run all unit tests
python -m pytest tests/unit/

# Run specific module
python -m pytest tests/unit/test_scraper.py

# With coverage
python -m pytest tests/unit/ --cov=core
```

### Integration Tests (Slow)
```bash
# Run live scraper test
python tests/integration/test_scraper_live.py

# Run all integration tests
python -m pytest tests/integration/ -v
```

### All Tests
```bash
# Run everything
python -m pytest tests/ -v
```

## 📝 Test Conventions

### Naming
- Unit tests: `test_[module].py`
- Integration tests: `test_[module]_live.py` or `test_[module]_integration.py`
- Test functions: `test_[functionality]_[scenario]()`

### Structure
```python
class TestModuleName:
    def setUp(self):
        # Test setup
        
    def test_functionality_success(self):
        # Happy path test
        
    def test_functionality_error_handling(self):
        # Error case test
```

### Mocking
- Use `unittest.mock` for external dependencies
- Mock HTTP requests, API calls, file system operations
- Keep unit tests isolated and fast

## 🎯 Future Tests to Add

### When LLM Summarizer is implemented:
- `tests/unit/test_summarizer.py` - Mocked LLM tests
- `tests/integration/test_llm_integration.py` - Real API tests

### When NAICS Classifier is implemented:
- `tests/unit/test_classifier.py` - Model prediction tests
- `tests/integration/test_classifier_accuracy.py` - Accuracy benchmarks

### When Computer Vision is implemented:
- `tests/unit/test_image_analysis.py` - Mocked CV tests
- `tests/integration/test_vehicle_detection.py` - Real image tests

### End-to-End Pipeline:
- `tests/integration/test_end_to_end.py` - Complete workflow test
- `tests/integration/test_performance.py` - Performance benchmarks