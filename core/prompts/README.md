# 🧠 LLM Prompt Templates

This directory contains carefully engineered prompts for the Business Intelligence system's AI analysis components.

## 📁 Files

### `business_summary.py`
**Complete prompt template collection** for all 3 passes of the business intelligence pipeline.

**Prompt Templates:**

#### `BUSINESS_ANALYSIS_PROMPT`
**Pass 1 text analysis prompt** for comprehensive business understanding.
- Business summary generation
- NAICS industry classification  
- Risk indicator extraction (vehicle use, e-commerce, cyber risk)
- Business capability identification
- Structured JSON output format

#### `IMAGE_ANALYSIS_PROMPT`
**Pass 2 visual analysis prompt** for Azure Computer Vision integration.
- Equipment and vehicle detection context
- Business relevance filtering guidance
- Visual risk indicator generation
- Capability enhancement identification

#### `BUSINESS_INTEGRATION_PROMPT` 
**Pass 3 integration prompt** for multi-modal evidence combination.
- Text and visual insight integration
- Enhanced summary generation
- Cross-modal validation and enhancement

### `__init__.py`
Package initialization file.

## 🎯 Prompt Engineering Principles

### Structured Output
All prompts enforce **strict JSON formatting** for reliable parsing:
```json
{
  "business_summary": "...",
  "naics_code": "...",
  "risk_indicators": {...},
  "capabilities": [...]
}
```

### Evidence-Based Analysis
Prompts emphasize:
- **Specific evidence extraction** from content
- **Confidence assessment** for all classifications  
- **Reasoning documentation** for transparency
- **Fallback handling** for incomplete data

### Domain Expertise
Prompts incorporate:
- **Insurance industry knowledge** for risk assessment
- **NAICS classification standards** for industry coding
- **Business analysis best practices** for capability identification

## 🔧 Customization

### Modifying Prompts
```python
# Access current prompts
from core.prompts.business_summary import (
    BUSINESS_ANALYSIS_PROMPT,
    IMAGE_ANALYSIS_PROMPT, 
    BUSINESS_INTEGRATION_PROMPT
)

# Customize for specific use cases
custom_prompt = BUSINESS_ANALYSIS_PROMPT + "\n\nAdditional instructions..."
```

### Best Practices
- **Test changes thoroughly** with multiple business types
- **Maintain JSON structure** for reliable parsing
- **Preserve confidence scoring** for reliability assessment
- **Document modifications** for team collaboration

## 🧪 Validation

### Prompt Testing
- All prompts validated against multiple business websites
- Consistent JSON output structure verified
- Risk assessment accuracy benchmarked against manual reviews
- Edge case handling tested (incomplete websites, unusual businesses)

### Performance Optimization
- **Token efficiency**: Prompts optimized for minimal token usage
- **Response quality**: Balanced detail vs conciseness  
- **Parsing reliability**: Structured to minimize JSON parsing errors