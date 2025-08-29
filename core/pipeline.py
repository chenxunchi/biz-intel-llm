"""
Business Intelligence Pipeline - Pass 3 integration and orchestration.

This module implements Pass 3 of the business intelligence system:
- Orchestrates the complete 3-pass analysis pipeline
- Integrates text analysis (Pass 1) with visual analysis (Pass 2)
- Applies intelligent risk aggregation rules
- Generates final enhanced business summaries
- Provides complete business intelligence output with confidence scoring

This is the main entry point for the complete business intelligence system.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

import openai
from config.settings import settings
from core.scraper import WebsiteScraper, BusinessData, ScrapingOptions
from core.summarizer import BusinessSummarizer, TextAnalysisResult
from core.image_analysis import ImageAnalyzer, VisualAnalysisResult
from core.prompts.business_summary import BUSINESS_INTEGRATION_PROMPT


@dataclass
class FinalBusinessAnalysis:
    """Complete business intelligence analysis result."""
    enhanced_business_summary: str
    naics_code: str
    naics_confidence: float
    final_risk_indicators: Dict
    business_capabilities: List[str]
    visual_enhancements: List[str]
    pipeline_metadata: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "enhanced_business_summary": self.enhanced_business_summary,
            "naics_code": self.naics_code,
            "naics_confidence": self.naics_confidence,
            "final_risk_indicators": self.final_risk_indicators,
            "business_capabilities": self.business_capabilities,
            "visual_enhancements": self.visual_enhancements,
            "pipeline_metadata": self.pipeline_metadata
        }


class BusinessIntelligencePipeline:
    """Complete 3-pass business intelligence analysis pipeline."""
    
    def __init__(self):
        """Initialize the complete business intelligence pipeline."""
        self.scraper = WebsiteScraper()
        self.text_analyzer = BusinessSummarizer()
        self.image_analyzer = ImageAnalyzer()
        self._setup_integration_llm()
    
    def _setup_integration_llm(self) -> None:
        """Setup LLM client for Pass 3 integration."""
        # Use same configuration as BusinessSummarizer
        if settings.azure_openai_key and settings.azure_openai_endpoint:
            # Azure OpenAI configuration already set by BusinessSummarizer
            pass
        elif settings.openai_api_key:
            # OpenAI configuration already set by BusinessSummarizer
            pass
        else:
            raise ValueError("No valid LLM API configuration found for integration.")
    
    def analyze_business_website(self, website_url: str, 
                                scraping_options: Optional[ScrapingOptions] = None) -> FinalBusinessAnalysis:
        """Complete business intelligence analysis of a website.
        
        This is the main entry point for the complete 3-pass analysis.
        
        Args:
            website_url: Business website URL to analyze
            scraping_options: Optional scraping configuration
            
        Returns:
            FinalBusinessAnalysis: Complete business intelligence assessment
        """
        pipeline_start = datetime.now()
        
        try:
            # Pass 1: Website Scraping and Text Analysis
            scraping_data = self._execute_pass_1(website_url, scraping_options)
            text_analysis = scraping_data["text_analysis"]
            business_data = scraping_data["business_data"]
            
            # Pass 2: Image Analysis (with graceful fallback)
            visual_analysis = self._execute_pass_2(business_data, text_analysis)
            
            # Pass 3: Integration and Final Analysis
            final_analysis = self._execute_pass_3(text_analysis, visual_analysis, pipeline_start)
            
            return final_analysis
            
        except Exception as e:
            # Create fallback analysis with error information
            return self._create_fallback_analysis(website_url, str(e), pipeline_start)
    
    def _execute_pass_1(self, website_url: str, 
                       scraping_options: Optional[ScrapingOptions] = None) -> Dict:
        """Execute Pass 1: Website scraping and text analysis.
        
        Args:
            website_url: Website URL to scrape
            scraping_options: Scraping configuration
            
        Returns:
            Dictionary with business_data and text_analysis
        """
        try:
            # Step 1: Scrape website
            options = scraping_options or ScrapingOptions()
            business_data = self.scraper.scrape_business(website_url, options)
            
            if not business_data.pages or not any(p.scrape_success for p in business_data.pages):
                raise Exception("No content could be scraped from the website")
            
            # Step 2: Analyze text content
            text_analysis = self.text_analyzer.analyze_business(business_data)
            
            return {
                "business_data": business_data,
                "text_analysis": text_analysis
            }
            
        except Exception as e:
            raise Exception(f"Pass 1 (Text Analysis) failed: {str(e)}")
    
    def _execute_pass_2(self, business_data: BusinessData, 
                       text_analysis: TextAnalysisResult) -> VisualAnalysisResult:
        """Execute Pass 2: Image analysis with graceful fallback.
        
        Args:
            business_data: Scraping results
            text_analysis: Text analysis results
            
        Returns:
            VisualAnalysisResult: Visual analysis results (may be empty if failed)
        """
        try:
            # Check if Azure CV is properly configured
            if not settings.azure_cv_key or not settings.azure_cv_endpoint:
                return self.image_analyzer._create_empty_visual_result("Azure Computer Vision not configured")
            
            # Check if there are any images to analyze
            total_images = sum(len(page.images) for page in business_data.pages if page.scrape_success)
            if total_images == 0:
                return self.image_analyzer._create_empty_visual_result("No images found in scraped content")
            
            # Execute image analysis
            visual_analysis = self.image_analyzer.analyze_business_images(business_data, text_analysis)
            return visual_analysis
            
        except Exception as e:
            # Return empty results but continue pipeline
            return self.image_analyzer._create_empty_visual_result(f"Pass 2 failed: {str(e)}")
    
    def _execute_pass_3(self, text_analysis: TextAnalysisResult, 
                       visual_analysis: VisualAnalysisResult,
                       pipeline_start: datetime) -> FinalBusinessAnalysis:
        """Execute Pass 3: Integration and final analysis.
        
        Args:
            text_analysis: Results from Pass 1
            visual_analysis: Results from Pass 2
            pipeline_start: Pipeline start time
            
        Returns:
            FinalBusinessAnalysis: Final integrated analysis
        """
        try:
            # Step 1: Aggregate risk indicators with intelligent rules
            final_risk_indicators = self._aggregate_risk_indicators(
                text_analysis.text_risk_indicators,
                visual_analysis.image_risk_indicators
            )
            
            # Step 2: Combine capabilities from text and visual analysis
            business_capabilities = self._combine_capabilities(
                text_analysis.text_capabilities,
                visual_analysis.visual_business_insights.get("capability_enhancements", [])
            )
            
            # Step 3: Generate enhanced summary using LLM integration
            enhanced_summary = self._generate_enhanced_summary(text_analysis, visual_analysis)
            
            # Step 4: Extract visual enhancements
            visual_enhancements = visual_analysis.visual_business_insights.get("capability_enhancements", [])
            
            # Step 5: Generate pipeline metadata
            pipeline_metadata = self._generate_pipeline_metadata(text_analysis, visual_analysis, pipeline_start)
            
            return FinalBusinessAnalysis(
                enhanced_business_summary=enhanced_summary,
                naics_code=text_analysis.naics_code,
                naics_confidence=text_analysis.naics_confidence,
                final_risk_indicators=final_risk_indicators,
                business_capabilities=business_capabilities,
                visual_enhancements=visual_enhancements,
                pipeline_metadata=pipeline_metadata
            )
            
        except Exception as e:
            raise Exception(f"Pass 3 (Integration) failed: {str(e)}")
    
    def _aggregate_risk_indicators(self, text_risks: Dict, visual_risks: Dict) -> Dict:
        """Aggregate risk indicators using intelligent rules per risk type.
        
        Args:
            text_risks: Risk indicators from text analysis
            visual_risks: Risk indicators from visual analysis
            
        Returns:
            Final aggregated risk indicators with confidence scores
        """
        final_risks = {}
        risk_levels = {"Low": 1, "Medium": 2, "High": 3}
        
        # Process each risk type with specific aggregation rules
        for risk_type in ["ecommerce", "vehicle_use", "cyber_risk"]:
            text_risk = text_risks.get(risk_type, {})
            visual_risk = visual_risks.get(risk_type, {})
            
            # Extract levels and evidence
            text_level = text_risk.get("level", "Low")
            visual_level = visual_risk.get("level", "Low")
            text_evidence = text_risk.get("evidence", [])
            visual_evidence = visual_risk.get("evidence", [])
            
            # Apply risk-specific aggregation rules
            if risk_type == "vehicle_use":
                # For vehicle use: MAX(text, visual) - visual evidence often overrides
                final_level_num = max(risk_levels[text_level], risk_levels[visual_level])
                primary_source = "visual" if risk_levels[visual_level] > risk_levels[text_level] else "text"
                confidence_boost = 0.2 if text_evidence and visual_evidence else 0.0
                
            elif risk_type == "ecommerce":
                # For ecommerce: Primarily text-based, visual adds minimal value
                final_level_num = risk_levels[text_level]
                primary_source = "text"
                confidence_boost = 0.1 if visual_evidence else 0.0
                
            elif risk_type == "cyber_risk":
                # For cyber risk: Text-only, visual provides minimal insight
                final_level_num = risk_levels[text_level]
                primary_source = "text"
                confidence_boost = 0.0
            
            # Convert back to level name
            final_level = [k for k, v in risk_levels.items() if v == final_level_num][0]
            
            # Calculate confidence based on evidence alignment and quality
            base_confidence = self._calculate_risk_confidence(
                text_risk, visual_risk, risk_type
            )
            final_confidence = min(base_confidence + confidence_boost, 1.0)
            
            # Combine evidence
            combined_evidence = []
            if text_evidence:
                combined_evidence.extend(text_evidence[:2])
            if visual_evidence:
                combined_evidence.extend(visual_evidence[:2])
            
            # Generate reasoning
            reasoning = self._generate_risk_reasoning(
                risk_type, final_level, text_risk, visual_risk, primary_source
            )
            
            final_risks[risk_type] = {
                "level": final_level,
                "confidence": round(final_confidence, 2),
                "primary_source": primary_source,
                "evidence": combined_evidence[:3],  # Limit to top 3 pieces of evidence
                "reasoning": reasoning
            }
        
        return final_risks
    
    def _calculate_risk_confidence(self, text_risk: Dict, visual_risk: Dict, risk_type: str) -> float:
        """Calculate base confidence for a risk indicator.
        
        Args:
            text_risk: Text-based risk assessment
            visual_risk: Visual-based risk assessment
            risk_type: Type of risk being assessed
            
        Returns:
            Base confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Evidence quality factors
        text_evidence = text_risk.get("evidence", [])
        visual_evidence = visual_risk.get("evidence", [])
        
        # Text evidence quality
        if len(text_evidence) >= 2:
            confidence += 0.2
        elif len(text_evidence) >= 1:
            confidence += 0.1
        
        # Visual evidence quality (varies by risk type)
        if risk_type == "vehicle_use" and visual_evidence:
            confidence += 0.2  # Visual evidence is strong for vehicle use
        elif risk_type in ["ecommerce", "cyber_risk"] and visual_evidence:
            confidence += 0.05  # Visual evidence is weak for these risks
        
        return min(confidence, 1.0)
    
    def _generate_risk_reasoning(self, risk_type: str, final_level: str, 
                                text_risk: Dict, visual_risk: Dict, primary_source: str) -> str:
        """Generate reasoning for final risk assessment.
        
        Args:
            risk_type: Type of risk
            final_level: Final risk level
            text_risk: Text risk data
            visual_risk: Visual risk data
            primary_source: Primary source of evidence
            
        Returns:
            Reasoning string
        """
        text_reasoning = text_risk.get("reasoning", "")
        visual_reasoning = visual_risk.get("reasoning", "")
        
        if primary_source == "text" and text_reasoning:
            base_reasoning = text_reasoning
            if visual_risk.get("evidence"):
                base_reasoning += f" Visual analysis provides supporting evidence."
        elif primary_source == "visual" and visual_reasoning:
            base_reasoning = visual_reasoning
            if text_risk.get("evidence"):
                base_reasoning += f" Text analysis provides additional context."
        else:
            # Fallback reasoning
            base_reasoning = f"{final_level} {risk_type} risk based on available evidence."
        
        return base_reasoning
    
    def _combine_capabilities(self, text_capabilities: List[str], 
                             visual_enhancements: List[str]) -> List[str]:
        """Combine and deduplicate business capabilities from text and visual analysis.
        
        Args:
            text_capabilities: Capabilities from text analysis
            visual_enhancements: Additional capabilities from visual analysis
            
        Returns:
            Combined list of unique business capabilities
        """
        # Combine all capabilities
        all_capabilities = text_capabilities + visual_enhancements
        
        # Normalize and deduplicate
        normalized = []
        seen = set()
        
        for capability in all_capabilities:
            capability_lower = capability.lower().strip()
            if capability_lower not in seen and len(capability.strip()) > 0:
                normalized.append(capability.strip())
                seen.add(capability_lower)
        
        return normalized
    
    def _generate_enhanced_summary(self, text_analysis: TextAnalysisResult, 
                                  visual_analysis: VisualAnalysisResult) -> str:
        """Generate enhanced business summary using LLM integration.
        
        Args:
            text_analysis: Text analysis results
            visual_analysis: Visual analysis results
            
        Returns:
            Enhanced business summary incorporating visual insights
        """
        try:
            # Check if we have meaningful visual insights to integrate
            visual_insights = visual_analysis.visual_business_insights
            has_visual_insights = (
                visual_insights.get("equipment_detected") or
                visual_insights.get("vehicle_types") or 
                visual_insights.get("capability_enhancements")
            )
            
            if not has_visual_insights:
                # Return original text summary if no visual insights
                return text_analysis.business_summary
            
            # Prepare integration prompt
            text_analysis_summary = {
                "business_summary": text_analysis.business_summary,
                "business_domain": text_analysis.business_domain,
                "primary_services": text_analysis.primary_services,
                "business_scale": text_analysis.business_scale
            }
            
            visual_analysis_summary = {
                "equipment_detected": visual_insights.get("equipment_detected", []),
                "vehicle_types": visual_insights.get("vehicle_types", []),
                "facility_characteristics": visual_insights.get("facility_characteristics", []),
                "capability_enhancements": visual_insights.get("capability_enhancements", [])
            }
            
            prompt = BUSINESS_INTEGRATION_PROMPT.format(
                text_analysis=json.dumps(text_analysis_summary, indent=2),
                visual_analysis=json.dumps(visual_analysis_summary, indent=2)
            )
            
            # Call LLM for integration
            response = openai.ChatCompletion.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst creating enhanced business summaries by integrating text and visual evidence."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,  # Shorter for summary generation
                temperature=0.2  # Lower temperature for consistency
            )
            
            # Extract enhanced summary from response
            integration_result = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                parsed_result = json.loads(integration_result)
                return parsed_result.get("enhanced_business_summary", text_analysis.business_summary)
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw response or fallback
                if "enhanced_business_summary" in integration_result:
                    # Try to extract summary from text
                    lines = integration_result.split('\n')
                    for line in lines:
                        if "enhanced_business_summary" in line.lower():
                            summary_part = line.split(":", 1)
                            if len(summary_part) > 1:
                                return summary_part[1].strip().strip('"')
                
                # Final fallback
                return text_analysis.business_summary
            
        except Exception as e:
            # Fallback to original summary if integration fails
            return text_analysis.business_summary
    
    def _generate_pipeline_metadata(self, text_analysis: TextAnalysisResult,
                                   visual_analysis: VisualAnalysisResult,
                                   pipeline_start: datetime) -> Dict:
        """Generate metadata about the complete pipeline execution.
        
        Args:
            text_analysis: Text analysis results
            visual_analysis: Visual analysis results
            pipeline_start: Pipeline start time
            
        Returns:
            Pipeline metadata dictionary
        """
        pipeline_end = datetime.now()
        total_time = (pipeline_end - pipeline_start).total_seconds()
        
        return {
            "pipeline_execution": {
                "started_at": pipeline_start.isoformat(),
                "completed_at": pipeline_end.isoformat(),
                "total_duration_seconds": round(total_time, 2),
                "version": "3-pass-system-v1.0"
            },
            "pass_1_metadata": text_analysis.analysis_metadata,
            "pass_2_metadata": visual_analysis.analysis_metadata,
            "integration_quality": {
                "text_analysis_success": bool(text_analysis.business_summary),
                "visual_analysis_success": not visual_analysis.analysis_metadata.get("analysis_skipped", False),
                "integration_used_visual_data": bool(visual_analysis.visual_business_insights.get("capability_enhancements")),
                "final_confidence_boost": self._calculate_integration_confidence_boost(text_analysis, visual_analysis)
            }
        }
    
    def _calculate_integration_confidence_boost(self, text_analysis: TextAnalysisResult,
                                              visual_analysis: VisualAnalysisResult) -> float:
        """Calculate confidence boost from visual-text integration.
        
        Args:
            text_analysis: Text analysis results
            visual_analysis: Visual analysis results
            
        Returns:
            Confidence boost score (0.0-0.3)
        """
        boost = 0.0
        
        # Check for visual confirmation of text-based risk indicators
        text_risks = text_analysis.text_risk_indicators
        visual_risks = visual_analysis.image_risk_indicators
        
        # Vehicle use confirmation
        if (text_risks.get("vehicle_use", {}).get("level") != "Low" and 
            visual_risks.get("vehicle_use", {}).get("level") != "Low"):
            boost += 0.1
        
        # Business capability enhancements
        visual_enhancements = visual_analysis.visual_business_insights.get("capability_enhancements", [])
        if len(visual_enhancements) > 0:
            boost += 0.1
        
        # Equipment detection alignment
        equipment_detected = visual_analysis.visual_business_insights.get("equipment_detected", [])
        if len(equipment_detected) > 0:
            boost += 0.05
        
        return round(min(boost, 0.3), 2)
    
    def _create_fallback_analysis(self, website_url: str, error_message: str, 
                                 pipeline_start: datetime) -> FinalBusinessAnalysis:
        """Create fallback analysis result when pipeline fails completely.
        
        Args:
            website_url: Original website URL
            error_message: Error that caused failure
            pipeline_start: Pipeline start time
            
        Returns:
            Fallback FinalBusinessAnalysis with error information
        """
        return FinalBusinessAnalysis(
            enhanced_business_summary=f"Analysis failed for {website_url}. Please check website accessibility and try again.",
            naics_code="000000",
            naics_confidence=0.0,
            final_risk_indicators={
                "ecommerce": {"level": "Low", "confidence": 0.0, "primary_source": "none", "evidence": [], "reasoning": "Analysis failed"},
                "vehicle_use": {"level": "Low", "confidence": 0.0, "primary_source": "none", "evidence": [], "reasoning": "Analysis failed"},
                "cyber_risk": {"level": "Low", "confidence": 0.0, "primary_source": "none", "evidence": [], "reasoning": "Analysis failed"}
            },
            business_capabilities=[],
            visual_enhancements=[],
            pipeline_metadata={
                "pipeline_execution": {
                    "started_at": pipeline_start.isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "total_duration_seconds": (datetime.now() - pipeline_start).total_seconds(),
                    "status": "failed",
                    "error": error_message
                }
            }
        )