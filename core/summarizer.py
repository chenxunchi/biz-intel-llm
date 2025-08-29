"""
LLM-based business analysis module - Pass 1 of 3-pass system.

This module implements Pass 1 of the business intelligence pipeline:
- Comprehensive text analysis using LLM
- Business summary generation
- NAICS code classification with confidence scoring
- Risk indicator extraction from text content
- Business capability identification

Integrates with OpenAI API or Azure OpenAI for text analysis.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import openai
from config.settings import settings
from core.prompts.business_summary import (
    BUSINESS_ANALYSIS_PROMPT,
    NAICS_CONFIDENCE_FACTORS
)
from core.scraper import BusinessData


@dataclass
class TextAnalysisResult:
    """Results from Pass 1 text analysis."""
    business_summary: str
    business_domain: str
    naics_code: str
    naics_confidence: float
    naics_reasoning: str
    primary_services: List[str]
    business_scale: str
    text_risk_indicators: Dict
    text_capabilities: List[str]
    raw_llm_response: str
    analysis_metadata: Dict


class BusinessSummarizer:
    """Pass 1: LLM-based business text analysis and risk assessment."""
    
    def __init__(self):
        """Initialize the business summarizer with LLM client."""
        self._setup_llm_client()
        
    def _setup_llm_client(self) -> None:
        """Configure OpenAI client based on available settings."""
        if settings.azure_openai_key and settings.azure_openai_endpoint:
            # Use Azure OpenAI
            openai.api_type = "azure"
            openai.api_key = settings.azure_openai_key
            openai.api_base = settings.azure_openai_endpoint
            openai.api_version = "2023-12-01-preview"
            self.model_name = settings.llm_model
        elif settings.openai_api_key:
            # Use OpenAI directly
            openai.api_key = settings.openai_api_key
            self.model_name = settings.llm_model
        else:
            raise ValueError("No valid LLM API configuration found. Set OPENAI_API_KEY or Azure OpenAI credentials.")
    
    def analyze_business(self, business_data: BusinessData) -> TextAnalysisResult:
        """Comprehensive business analysis from scraped website content.
        
        This is the main entry point for Pass 1 analysis.
        
        Args:
            business_data: Complete scraping results from WebsiteScraper
            
        Returns:
            TextAnalysisResult: Comprehensive text-based business analysis
        """
        try:
            # Extract and combine text content from all successfully scraped pages
            combined_text = self._combine_page_content(business_data)
            
            if not combined_text.strip():
                raise ValueError("No usable text content found in scraped data")
            
            # Get website quality score from scraper results
            quality_score = self._extract_quality_score(business_data)
            
            # Perform LLM analysis
            llm_response = self._call_llm_analysis(combined_text, quality_score)
            
            # Parse and validate LLM response
            parsed_results = self._parse_llm_response(llm_response)
            
            # Calculate NAICS confidence
            naics_confidence = self._calculate_naics_confidence(
                parsed_results.get("naics_code", ""),
                combined_text,
                quality_score,
                parsed_results
            )
            
            # Generate metadata
            metadata = self._generate_analysis_metadata(business_data, combined_text)
            
            return TextAnalysisResult(
                business_summary=parsed_results.get("business_summary", ""),
                business_domain=parsed_results.get("business_domain", ""),
                naics_code=parsed_results.get("naics_code", ""),
                naics_confidence=naics_confidence,
                naics_reasoning=parsed_results.get("naics_reasoning", ""),
                primary_services=parsed_results.get("primary_services", []),
                business_scale=parsed_results.get("business_scale", "unknown"),
                text_risk_indicators=parsed_results.get("text_risk_indicators", {}),
                text_capabilities=parsed_results.get("text_capabilities", []),
                raw_llm_response=llm_response,
                analysis_metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Business analysis failed: {str(e)}")
    
    def _combine_page_content(self, business_data: BusinessData) -> str:
        """Combine text content from all successfully scraped pages.
        
        Args:
            business_data: Scraping results
            
        Returns:
            Combined text content with page type labels
        """
        combined_content = []
        
        # Prioritize page types for better content organization
        page_priority = ["home", "about", "services", "contact", "other"]
        
        for page_type in page_priority:
            pages_of_type = [
                page for page in business_data.pages 
                if page.page_type == page_type and page.scrape_success and page.text_content.strip()
            ]
            
            for page in pages_of_type:
                # Add page context for better LLM understanding
                combined_content.append(f"\n=== {page_type.upper()} PAGE ({page.url}) ===\n")
                combined_content.append(page.text_content)
                combined_content.append("\n")
        
        return "".join(combined_content).strip()
    
    def _extract_quality_score(self, business_data: BusinessData) -> float:
        """Extract website quality score from scraper business intelligence.
        
        Args:
            business_data: Scraping results
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            page_analysis = business_data.business_intelligence.get("page_analysis", {})
            return page_analysis.get("content_quality_score", 0.5)
        except Exception:
            return 0.5  # Default moderate quality score
    
    def _call_llm_analysis(self, text_content: str, quality_score: float) -> str:
        """Call LLM for comprehensive business analysis.
        
        Args:
            text_content: Combined website text
            quality_score: Website quality score
            
        Returns:
            Raw LLM response
        """
        prompt = BUSINESS_ANALYSIS_PROMPT.format(
            website_content=text_content[:15000],  # Limit content to fit context window
            quality_score=round(quality_score, 2)
        )
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst specializing in insurance underwriting. Provide accurate, structured JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.max_tokens,
                temperature=settings.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def _parse_llm_response(self, llm_response: str) -> Dict:
        """Parse and validate LLM JSON response.
        
        Args:
            llm_response: Raw LLM response
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Try to extract JSON from response (in case of markdown formatting)
            json_match = re.search(r'```json\s*({.*?})\s*```', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON block without markdown
                json_str = llm_response.strip()
                if not json_str.startswith('{'):
                    # Look for first { to last }
                    start = json_str.find('{')
                    end = json_str.rfind('}')
                    if start != -1 and end != -1:
                        json_str = json_str[start:end+1]
            
            parsed = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["business_summary", "business_domain", "naics_code", "text_risk_indicators"]
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"LLM response validation failed: {str(e)}")
    
    def _calculate_naics_confidence(self, naics_code: str, text_content: str, 
                                   quality_score: float, parsed_results: Dict) -> float:
        """Calculate NAICS classification confidence based on text analysis.
        
        Args:
            naics_code: Predicted NAICS code
            text_content: Original text content
            quality_score: Website quality score (0.0-1.0)
            parsed_results: Parsed LLM results
            
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0
        
        # Factor 1: Website Quality (0-0.4)
        confidence += quality_score * 0.4
        
        # Factor 2: Business Description Specificity (0-0.4)
        text_specificity = self._assess_text_specificity(text_content, parsed_results)
        confidence += text_specificity * 0.4
        
        # Factor 3: NAICS Keyword Match (0-0.2)
        keyword_match = self._assess_naics_keyword_match(naics_code, text_content)
        confidence += keyword_match * 0.2
        
        return min(confidence, 1.0)
    
    def _assess_text_specificity(self, text_content: str, parsed_results: Dict) -> float:
        """Assess how specific and detailed the business description is.
        
        Args:
            text_content: Original text content
            parsed_results: Parsed LLM analysis
            
        Returns:
            Specificity score (0.0-1.0)
        """
        score = 0.0
        
        # Check for specific industry terminology
        business_summary = parsed_results.get("business_summary", "")
        if len(business_summary) > 100 and "specific" not in business_summary.lower():
            score += 0.3
        
        # Check for detailed service descriptions
        services = parsed_results.get("primary_services", [])
        if len(services) >= 3:
            score += 0.3
            
        # Check for business scale clarity
        business_scale = parsed_results.get("business_scale", "unknown")
        if business_scale != "unknown":
            score += 0.2
            
        # Check text length and richness
        if len(text_content) > 2000:
            score += 0.2
            
        return min(score, 1.0)
    
    def _assess_naics_keyword_match(self, naics_code: str, text_content: str) -> float:
        """Assess how well the text matches expected NAICS keywords.
        
        Args:
            naics_code: Predicted NAICS code
            text_content: Original text content
            
        Returns:
            Keyword match score (0.0-1.0)
        """
        # Simplified keyword matching - in production, this would use
        # a comprehensive NAICS keyword database
        text_lower = text_content.lower()
        
        # Basic industry keyword patterns
        industry_patterns = {
            "561": ["landscaping", "lawn", "garden", "maintenance", "grounds"],
            "238": ["construction", "contractor", "building", "installation"],
            "541": ["consulting", "professional", "services", "advisory"],
            "722": ["restaurant", "food", "dining", "catering"],
            "531": ["real estate", "property", "rental", "leasing"]
        }
        
        # Check if NAICS code matches any patterns
        naics_prefix = naics_code[:3] if len(naics_code) >= 3 else ""
        keywords = industry_patterns.get(naics_prefix, [])
        
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        max_possible = len(keywords) if keywords else 1
        
        return matches / max_possible if max_possible > 0 else 0.5
    
    def _generate_analysis_metadata(self, business_data: BusinessData, text_content: str) -> Dict:
        """Generate metadata about the analysis process.
        
        Args:
            business_data: Original scraping results
            text_content: Combined text content
            
        Returns:
            Analysis metadata dictionary
        """
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "text_analysis": {
                "total_text_length": len(text_content),
                "pages_analyzed": len([p for p in business_data.pages if p.scrape_success]),
                "model_used": self.model_name,
                "content_sources": list(set(p.page_type for p in business_data.pages if p.scrape_success))
            },
            "scraping_quality": {
                "website_quality_score": self._extract_quality_score(business_data),
                "successful_pages": len([p for p in business_data.pages if p.scrape_success]),
                "total_pages_attempted": len(business_data.pages)
            }
        }