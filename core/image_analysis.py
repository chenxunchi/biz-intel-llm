"""
Azure Computer Vision module for business image analysis - Pass 2 of 3-pass system.

This module implements Pass 2 of the business intelligence pipeline:
- Filters business-relevant images from scraper results
- Analyzes images using Azure Computer Vision API
- Detects vehicles, equipment, and facility characteristics
- Maps computer vision results to business intelligence insights
- Generates visual risk indicators with confidence scoring

Integrates with Azure Cognitive Services Computer Vision API.
"""

import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from config.settings import settings
from core.scraper import BusinessData
from core.summarizer import TextAnalysisResult
from core.prompts.business_summary import IMAGE_ANALYSIS_CONTEXT


@dataclass
class ImageFilterResult:
    """Result of image filtering process."""
    selected_images: List[Dict]
    filtered_count: int
    filter_reasons: Dict[str, int]


@dataclass
class VisualAnalysisResult:
    """Results from Pass 2 visual analysis."""
    visual_business_insights: Dict
    image_risk_indicators: Dict
    analysis_metadata: Dict
    raw_cv_responses: List[Dict]


class ImageAnalyzer:
    """Pass 2: Azure Computer Vision-based business image analysis."""
    
    def __init__(self):
        """Initialize the image analyzer with Azure CV client."""
        self._setup_cv_client()
        
    def _setup_cv_client(self) -> None:
        """Configure Azure Computer Vision client."""
        if not settings.azure_cv_key or not settings.azure_cv_endpoint:
            raise ValueError("Azure Computer Vision credentials not found. Set AZURE_CV_KEY and AZURE_CV_ENDPOINT.")
        
        self.cv_client = ComputerVisionClient(
            settings.azure_cv_endpoint,
            CognitiveServicesCredentials(settings.azure_cv_key)
        )
    
    def analyze_business_images(self, business_data: BusinessData, 
                               text_analysis: TextAnalysisResult) -> VisualAnalysisResult:
        """Comprehensive image analysis for business intelligence.
        
        This is the main entry point for Pass 2 analysis.
        
        Args:
            business_data: Complete scraping results from WebsiteScraper
            text_analysis: Results from Pass 1 text analysis
            
        Returns:
            VisualAnalysisResult: Comprehensive visual business analysis
        """
        try:
            # Step 1: Filter and select business-relevant images
            filter_result = self._filter_business_images(business_data, text_analysis)
            
            if not filter_result.selected_images:
                # Return empty results if no images to analyze
                return self._create_empty_visual_result("No business-relevant images found")
            
            # Step 2: Analyze each image with Azure CV
            cv_results = []
            for image in filter_result.selected_images:
                try:
                    cv_result = self._analyze_single_image(image, text_analysis)
                    if cv_result:
                        cv_results.append(cv_result)
                except Exception as e:
                    # Continue with other images if one fails
                    cv_results.append({
                        "image_url": image.get("url", "unknown"),
                        "error": str(e),
                        "analysis_success": False
                    })
            
            # Step 3: Aggregate CV results into business insights
            business_insights = self._generate_business_insights(cv_results, text_analysis)
            
            # Step 4: Generate risk indicators from visual evidence
            risk_indicators = self._generate_visual_risk_indicators(cv_results, business_insights)
            
            # Step 5: Create analysis metadata
            metadata = self._generate_visual_metadata(filter_result, cv_results)
            
            return VisualAnalysisResult(
                visual_business_insights=business_insights,
                image_risk_indicators=risk_indicators,
                analysis_metadata=metadata,
                raw_cv_responses=cv_results
            )
            
        except Exception as e:
            return self._create_empty_visual_result(f"Visual analysis failed: {str(e)}")
    
    def _filter_business_images(self, business_data: BusinessData, 
                               text_analysis: TextAnalysisResult) -> ImageFilterResult:
        """Filter images to select most business-relevant ones for analysis.
        
        Args:
            business_data: Scraping results
            text_analysis: Text analysis results for context
            
        Returns:
            ImageFilterResult: Filtered images and filtering statistics
        """
        all_images = []
        filter_reasons = {"too_small": 0, "likely_decorative": 0, "no_alt_text": 0, "selected": 0}
        
        # Collect all images from successful pages
        for page in business_data.pages:
            if page.scrape_success and page.images:
                for img in page.images:
                    img["source_page"] = page.url
                    img["page_type"] = page.page_type
                    all_images.append(img)
        
        selected_images = []
        business_domain = text_analysis.business_domain.lower()
        
        # Priority scoring for business relevance
        for img in all_images:
            score = self._calculate_image_business_score(img, business_domain)
            
            # Apply filters
            if self._is_too_small(img):
                filter_reasons["too_small"] += 1
                continue
                
            if self._is_likely_decorative(img):
                filter_reasons["likely_decorative"] += 1
                continue
            
            # Select top scoring images up to limit
            if score > 0.3 and len(selected_images) < settings.max_images_for_analysis:
                img["business_score"] = score
                selected_images.append(img)
                filter_reasons["selected"] += 1
        
        # Sort by business relevance score
        selected_images.sort(key=lambda x: x.get("business_score", 0), reverse=True)
        
        return ImageFilterResult(
            selected_images=selected_images,
            filtered_count=len(all_images) - len(selected_images),
            filter_reasons=filter_reasons
        )
    
    def _calculate_image_business_score(self, img: Dict, business_domain: str) -> float:
        """Calculate business relevance score for an image.
        
        Args:
            img: Image metadata
            business_domain: Business domain from text analysis
            
        Returns:
            Business relevance score (0.0-1.0)
        """
        score = 0.0
        alt_text = img.get("alt_text", "").lower()
        title = img.get("title", "").lower()
        url = img.get("url", "").lower()
        
        # Business domain relevance
        domain_keywords = {
            "landscaping": ["lawn", "garden", "tree", "equipment", "truck", "vehicle"],
            "construction": ["building", "site", "equipment", "crane", "truck", "machinery"],
            "manufacturing": ["factory", "equipment", "machinery", "facility", "production"],
            "transportation": ["vehicle", "truck", "fleet", "warehouse", "logistics"],
            "restaurant": ["kitchen", "dining", "food", "restaurant", "facility"]
        }
        
        keywords = domain_keywords.get(business_domain, [])
        for keyword in keywords:
            if keyword in alt_text or keyword in title:
                score += 0.3
        
        # General business indicators
        business_indicators = ["team", "staff", "office", "facility", "equipment", "service"]
        for indicator in business_indicators:
            if indicator in alt_text or indicator in title:
                score += 0.2
        
        # Page type relevance
        page_type = img.get("page_type", "")
        if page_type in ["about", "services", "home"]:
            score += 0.2
        elif page_type == "contact":
            score += 0.1
        
        # Image size indicators (larger images often more important)
        width = self._parse_dimension(img.get("width", ""))
        height = self._parse_dimension(img.get("height", ""))
        if width and height and width * height > 50000:  # Large images
            score += 0.1
        
        return min(score, 1.0)
    
    def _is_too_small(self, img: Dict) -> bool:
        """Check if image is too small to be business-relevant."""
        width = self._parse_dimension(img.get("width", ""))
        height = self._parse_dimension(img.get("height", ""))
        
        if width and height:
            return width < settings.min_image_size or height < settings.min_image_size
        return False
    
    def _is_likely_decorative(self, img: Dict) -> bool:
        """Check if image is likely decorative rather than informative."""
        alt_text = img.get("alt_text", "").lower()
        url = img.get("url", "").lower()
        
        decorative_patterns = [
            "icon", "logo", "bullet", "arrow", "divider", "spacer",
            "decoration", "border", "background", "pattern"
        ]
        
        return any(pattern in alt_text or pattern in url for pattern in decorative_patterns)
    
    def _parse_dimension(self, dimension_str: str) -> Optional[int]:
        """Parse dimension string to integer."""
        if not dimension_str:
            return None
        try:
            # Extract numeric part
            numeric = re.search(r'\d+', str(dimension_str))
            return int(numeric.group()) if numeric else None
        except (ValueError, AttributeError):
            return None
    
    def _analyze_single_image(self, image: Dict, text_analysis: TextAnalysisResult) -> Dict:
        """Analyze a single image using Azure Computer Vision.
        
        Args:
            image: Image metadata with URL
            text_analysis: Business context from text analysis
            
        Returns:
            Computer vision analysis results
        """
        image_url = image.get("url")
        if not image_url:
            return {"error": "No image URL provided", "analysis_success": False}
        
        try:
            # Define visual features to extract
            visual_features = [
                VisualFeatureTypes.objects,
                VisualFeatureTypes.categories,
                VisualFeatureTypes.description,
                VisualFeatureTypes.tags
            ]
            
            # Call Azure Computer Vision API
            analysis = self.cv_client.analyze_image(image_url, visual_features)
            
            # Process and structure results
            result = {
                "image_url": image_url,
                "source_page": image.get("source_page"),
                "page_type": image.get("page_type"),
                "business_score": image.get("business_score", 0),
                "analysis_success": True,
                "objects": self._process_objects(analysis.objects),
                "categories": self._process_categories(analysis.categories),
                "description": self._process_description(analysis.description),
                "tags": self._process_tags(analysis.tags),
                "business_context": {
                    "domain": text_analysis.business_domain,
                    "services": text_analysis.primary_services,
                    "scale": text_analysis.business_scale
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "image_url": image_url,
                "error": f"Azure CV analysis failed: {str(e)}",
                "analysis_success": False
            }
    
    def _process_objects(self, objects) -> List[Dict]:
        """Process object detection results."""
        if not objects:
            return []
        
        processed = []
        for obj in objects:
            processed.append({
                "object": obj.object_property,
                "confidence": round(obj.confidence, 3),
                "rectangle": {
                    "x": obj.rectangle.x,
                    "y": obj.rectangle.y,
                    "w": obj.rectangle.w,
                    "h": obj.rectangle.h
                } if obj.rectangle else None
            })
        
        return processed
    
    def _process_categories(self, categories) -> List[Dict]:
        """Process image categorization results."""
        if not categories:
            return []
        
        processed = []
        for cat in categories:
            processed.append({
                "name": cat.name,
                "score": round(cat.score, 3)
            })
        
        return processed
    
    def _process_description(self, description) -> Dict:
        """Process image description results."""
        if not description:
            return {}
        
        return {
            "captions": [
                {"text": cap.text, "confidence": round(cap.confidence, 3)}
                for cap in (description.captions or [])
            ],
            "tags": description.tags or []
        }
    
    def _process_tags(self, tags) -> List[Dict]:
        """Process image tags results."""
        if not tags:
            return []
        
        processed = []
        for tag in tags:
            processed.append({
                "name": tag.name,
                "confidence": round(tag.confidence, 3)
            })
        
        return processed
    
    def _generate_business_insights(self, cv_results: List[Dict], 
                                   text_analysis: TextAnalysisResult) -> Dict:
        """Generate business insights from computer vision results.
        
        Args:
            cv_results: List of CV analysis results
            text_analysis: Text analysis context
            
        Returns:
            Business insights dictionary
        """
        insights = {
            "equipment_detected": [],
            "vehicle_types": [],
            "facility_characteristics": [],
            "scale_indicators": [],
            "capability_enhancements": []
        }
        
        business_domain = text_analysis.business_domain.lower()
        
        # Aggregate detections across all images
        all_objects = []
        all_categories = []
        all_tags = []
        
        for result in cv_results:
            if result.get("analysis_success"):
                all_objects.extend(result.get("objects", []))
                all_categories.extend(result.get("categories", []))
                all_tags.extend(result.get("tags", []))
        
        # Equipment detection
        equipment_keywords = ["truck", "machine", "equipment", "tool", "crane", "forklift", "vehicle"]
        for obj in all_objects:
            obj_name = obj.get("object", "").lower()
            if any(keyword in obj_name for keyword in equipment_keywords) and obj.get("confidence", 0) > 0.5:
                insights["equipment_detected"].append({
                    "type": obj.get("object"),
                    "confidence": obj.get("confidence")
                })
        
        # Vehicle type analysis
        vehicle_keywords = ["car", "truck", "van", "bus", "motorcycle"]
        for obj in all_objects:
            obj_name = obj.get("object", "").lower()
            if any(keyword in obj_name for keyword in vehicle_keywords) and obj.get("confidence", 0) > 0.5:
                insights["vehicle_types"].append({
                    "type": obj.get("object"),
                    "confidence": obj.get("confidence")
                })
        
        # Facility characteristics from categories
        facility_categories = ["building", "outdoor", "indoor", "office", "warehouse", "factory"]
        for cat in all_categories:
            cat_name = cat.get("name", "").lower()
            if any(keyword in cat_name for keyword in facility_categories) and cat.get("score", 0) > 0.3:
                insights["facility_characteristics"].append({
                    "type": cat.get("name"),
                    "confidence": cat.get("score")
                })
        
        # Scale indicators
        scale_tags = ["commercial", "industrial", "large", "fleet", "multiple"]
        for tag in all_tags:
            tag_name = tag.get("name", "").lower()
            if any(keyword in tag_name for keyword in scale_tags) and tag.get("confidence", 0) > 0.4:
                insights["scale_indicators"].append({
                    "indicator": tag.get("name"),
                    "confidence": tag.get("confidence")
                })
        
        # Business capability enhancements based on visual evidence
        insights["capability_enhancements"] = self._infer_capability_enhancements(
            insights, business_domain, text_analysis.primary_services
        )
        
        return insights
    
    def _infer_capability_enhancements(self, insights: Dict, business_domain: str, 
                                      text_services: List[str]) -> List[str]:
        """Infer additional business capabilities from visual evidence.
        
        Args:
            insights: Generated visual insights
            business_domain: Business domain
            text_services: Services mentioned in text
            
        Returns:
            List of enhanced capabilities
        """
        enhancements = []
        
        # Equipment-based capability enhancements
        equipment = [item.get("type", "").lower() for item in insights.get("equipment_detected", [])]
        
        if "crane" in equipment:
            enhancements.append("heavy lifting services")
        if "truck" in equipment or "van" in equipment:
            enhancements.append("mobile services")
        if "forklift" in equipment:
            enhancements.append("material handling")
        
        # Domain-specific enhancements
        if business_domain == "landscaping":
            if any("truck" in eq for eq in equipment):
                enhancements.append("large-scale landscaping projects")
            if "crane" in equipment:
                enhancements.append("tree removal services")
        
        elif business_domain == "construction":
            if "crane" in equipment:
                enhancements.append("high-rise construction")
            if len([eq for eq in equipment if "machine" in eq]) > 2:
                enhancements.append("heavy construction work")
        
        # Remove duplicates and filter out capabilities already in text services
        text_services_lower = [s.lower() for s in text_services]
        enhancements = list(set(enhancements))
        enhancements = [e for e in enhancements if not any(ts in e or e in ts for ts in text_services_lower)]
        
        return enhancements
    
    def _generate_visual_risk_indicators(self, cv_results: List[Dict], 
                                        business_insights: Dict) -> Dict:
        """Generate risk indicators from visual analysis.
        
        Args:
            cv_results: Computer vision results
            business_insights: Generated business insights
            
        Returns:
            Visual risk indicators dictionary
        """
        risk_indicators = {
            "vehicle_use": {"level": "Low", "evidence": [], "reasoning": ""},
            "equipment_risk": {"level": "Low", "evidence": [], "reasoning": ""},
            "facility_risk": {"level": "Low", "evidence": [], "reasoning": ""}
        }
        
        # Vehicle use risk assessment
        vehicles = business_insights.get("vehicle_types", [])
        equipment = business_insights.get("equipment_detected", [])
        
        if len(vehicles) >= 3 or any("truck" in v.get("type", "").lower() for v in vehicles):
            risk_indicators["vehicle_use"] = {
                "level": "High",
                "evidence": [f"{v.get('type')} detected" for v in vehicles[:3]],
                "reasoning": "Multiple vehicles or commercial trucks detected"
            }
        elif len(vehicles) >= 1:
            risk_indicators["vehicle_use"] = {
                "level": "Medium",
                "evidence": [f"{v.get('type')} detected" for v in vehicles[:2]],
                "reasoning": "Vehicle presence confirmed visually"
            }
        
        # Equipment risk assessment
        heavy_equipment = [eq for eq in equipment if any(keyword in eq.get("type", "").lower() 
                          for keyword in ["crane", "forklift", "machine", "heavy"])]
        
        if len(heavy_equipment) >= 2:
            risk_indicators["equipment_risk"] = {
                "level": "High", 
                "evidence": [f"{eq.get('type')} detected" for eq in heavy_equipment[:2]],
                "reasoning": "Multiple heavy equipment items detected"
            }
        elif len(heavy_equipment) >= 1:
            risk_indicators["equipment_risk"] = {
                "level": "Medium",
                "evidence": [f"{heavy_equipment[0].get('type')} detected"],
                "reasoning": "Heavy equipment operations confirmed"
            }
        
        # Facility risk assessment
        facilities = business_insights.get("facility_characteristics", [])
        industrial_facilities = [f for f in facilities if any(keyword in f.get("type", "").lower()
                               for keyword in ["warehouse", "factory", "industrial"])]
        
        if len(industrial_facilities) >= 1:
            risk_indicators["facility_risk"] = {
                "level": "Medium",
                "evidence": [f"Industrial facility: {f.get('type')}" for f in industrial_facilities[:1]],
                "reasoning": "Industrial facility operations detected"
            }
        
        return risk_indicators
    
    def _generate_visual_metadata(self, filter_result: ImageFilterResult, 
                                 cv_results: List[Dict]) -> Dict:
        """Generate metadata about the visual analysis process.
        
        Args:
            filter_result: Image filtering results
            cv_results: Computer vision analysis results
            
        Returns:
            Visual analysis metadata
        """
        successful_analyses = len([r for r in cv_results if r.get("analysis_success")])
        failed_analyses = len(cv_results) - successful_analyses
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "image_processing": {
                "total_images_found": filter_result.filtered_count + len(filter_result.selected_images),
                "images_selected_for_analysis": len(filter_result.selected_images),
                "images_filtered_out": filter_result.filtered_count,
                "filter_reasons": filter_result.filter_reasons
            },
            "azure_cv_analysis": {
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": round(successful_analyses / len(cv_results), 3) if cv_results else 0.0
            },
            "analysis_quality": {
                "avg_business_score": round(
                    sum(img.get("business_score", 0) for img in filter_result.selected_images) / 
                    len(filter_result.selected_images), 2
                ) if filter_result.selected_images else 0.0
            }
        }
    
    def _create_empty_visual_result(self, reason: str) -> VisualAnalysisResult:
        """Create empty visual analysis result for fallback scenarios.
        
        Args:
            reason: Reason for empty result
            
        Returns:
            Empty VisualAnalysisResult
        """
        return VisualAnalysisResult(
            visual_business_insights={
                "equipment_detected": [],
                "vehicle_types": [],
                "facility_characteristics": [],
                "scale_indicators": [],
                "capability_enhancements": []
            },
            image_risk_indicators={
                "vehicle_use": {"level": "Low", "evidence": [], "reasoning": "No visual analysis performed"},
                "equipment_risk": {"level": "Low", "evidence": [], "reasoning": "No visual analysis performed"},
                "facility_risk": {"level": "Low", "evidence": [], "reasoning": "No visual analysis performed"}
            },
            analysis_metadata={
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_skipped": True,
                "skip_reason": reason,
                "image_processing": {"total_images_found": 0, "images_analyzed": 0}
            },
            raw_cv_responses=[]
        )