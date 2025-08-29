"""
Prompt templates for business analysis and summarization.

This module contains enhanced prompt templates for the 3-pass business intelligence
system that analyzes text content, images, and generates comprehensive risk assessments.
"""

# Pass 1: Text Analysis - Business Understanding + NAICS + Risk Indicators
BUSINESS_ANALYSIS_PROMPT = """
You are a business intelligence analyst specializing in insurance underwriting risk assessment. 
Analyze the following website content to understand this business comprehensively.

Website Content:
{website_content}

Website Quality Score: {quality_score}/1.0
(This indicates the richness and completeness of the website content)

Please provide a structured JSON response with the following information:

{{
    "business_summary": "Clear, concise description of what this business does",
    "business_domain": "Primary industry/sector (e.g., 'landscaping', 'manufacturing', 'consulting')",
    "naics_code": "6-digit NAICS code that best matches this business",
    "naics_reasoning": "Brief explanation of why this NAICS code was selected",
    "primary_services": ["List of", "main services", "or products offered"],
    "business_scale": "small_local|medium_regional|large_commercial|enterprise",
    "text_risk_indicators": {{
        "ecommerce": {{
            "level": "Low|Medium|High",
            "evidence": ["specific text evidence", "supporting this assessment"],
            "reasoning": "Why this risk level was assigned"
        }},
        "vehicle_use": {{
            "level": "Low|Medium|High", 
            "evidence": ["specific text evidence", "supporting this assessment"],
            "reasoning": "Why this risk level was assigned"
        }},
        "cyber_risk": {{
            "level": "Low|Medium|High",
            "evidence": ["specific text evidence", "supporting this assessment"], 
            "reasoning": "Why this risk level was assigned"
        }}
    }},
    "text_capabilities": ["specific business", "capabilities mentioned", "in text content"]
}}

Focus on extracting concrete, specific information from the text. Be precise in your risk assessments and provide clear evidence for each determination.
"""

# Pass 2: Image Analysis Context Template  
IMAGE_ANALYSIS_CONTEXT = """
Business Context for Image Analysis:
- Business Domain: {business_domain}
- Primary Services: {primary_services}
- Business Scale: {business_scale}
- NAICS Code: {naics_code}

This context will help interpret images in the proper business context.
"""

# Pass 3: Integration and Enhancement
BUSINESS_INTEGRATION_PROMPT = """
You are finalizing a comprehensive business intelligence assessment by combining text analysis with visual evidence.

Text Analysis Results:
{text_analysis}

Visual Analysis Results:
{visual_analysis}

Please provide the final integrated assessment as JSON:

{{
    "enhanced_business_summary": "Enhanced description incorporating both text and visual insights",
    "final_risk_indicators": {{
        "ecommerce": {{
            "level": "Low|Medium|High",
            "confidence": 0.0-1.0,
            "primary_source": "text|visual|both",
            "reasoning": "Final assessment reasoning"
        }},
        "vehicle_use": {{
            "level": "Low|Medium|High",
            "confidence": 0.0-1.0,
            "primary_source": "text|visual|both", 
            "reasoning": "Final assessment reasoning"
        }},
        "cyber_risk": {{
            "level": "Low|Medium|High",
            "confidence": 0.0-1.0,
            "primary_source": "text|visual|both",
            "reasoning": "Final assessment reasoning"
        }}
    }},
    "business_capabilities": ["comprehensive list", "of all identified", "business capabilities"],
    "visual_enhancements": ["capabilities or", "characteristics discovered", "from visual analysis"]
}}

Integration Rules:
- For vehicle_use: Take MAX(text_level, visual_level) - visual evidence often overrides text
- For ecommerce: Primarily use text_level - visual rarely provides e-commerce evidence  
- For cyber_risk: Use text_level - visual provides minimal cyber risk insight
- Boost confidence when text and visual evidence align
- Include visual enhancements in capabilities if they add meaningful business context
"""

# NAICS Classification Support
NAICS_CONFIDENCE_FACTORS = """
NAICS Classification Confidence Assessment:

Factors to consider:
1. Website Quality (0-0.4): Higher quality sites have more reliable business descriptions
2. Business Description Specificity (0-0.4): "Commercial HVAC repair" vs "general services"  
3. Industry Keyword Match (0-0.2): How well text matches NAICS category keywords

Confidence Levels:
- 0.9-1.0: Very High - Multiple strong signals align, specific industry language
- 0.7-0.9: High - Clear business description, good website quality
- 0.5-0.7: Medium - Some uncertainty, generic descriptions
- 0.3-0.5: Low - Limited or conflicting information
- 0.0-0.3: Very Low - Poor quality site, unclear business model
"""