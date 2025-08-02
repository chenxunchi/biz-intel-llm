"""
Prompt templates for business summarization.

This module contains prompt templates used for generating business summaries
from website content using LLMs.
"""

BUSINESS_SUMMARY_PROMPT = """
Analyze the following website content and provide a concise business summary.

Website Content:
{website_content}

Please provide:
1. Business name and industry
2. Primary products/services offered
3. Target market/customers
4. Business model (B2B, B2C, etc.)
5. Key business characteristics

Summary:
"""

RISK_EXTRACTION_PROMPT = """
Analyze the following business website content and identify insurance risk indicators.

Website Content:
{website_content}

Please identify and rate the following risk factors (Low/Medium/High):

1. E-commerce Capability:
   - Online sales functionality
   - Payment processing
   - Customer data handling

2. Vehicle Usage:
   - Fleet operations
   - Delivery services
   - Employee vehicle use

3. Cyber Risk Exposure:
   - Online presence complexity
   - Data collection practices
   - Digital infrastructure dependency

Risk Assessment:
"""