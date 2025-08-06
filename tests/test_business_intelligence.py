"""
Comprehensive test suite for the 3-pass business intelligence system.

Tests all major components:
- Pass 1: BusinessSummarizer (text analysis)
- Pass 2: ImageAnalyzer (visual analysis) 
- Pass 3: BusinessIntelligencePipeline (integration)
- Error handling and fallback scenarios
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from core.scraper import BusinessData, PageData, ScrapingOptions
from core.summarizer import BusinessSummarizer, TextAnalysisResult
from core.image_analysis import ImageAnalyzer, VisualAnalysisResult
from core.pipeline import BusinessIntelligencePipeline, FinalBusinessAnalysis


class TestBusinessSummarizer(unittest.TestCase):
    """Test Pass 1: Text Analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.summarizer = BusinessSummarizer()
        self.sample_business_data = self._create_sample_business_data()
    
    def _create_sample_business_data(self) -> BusinessData:
        """Create sample business data for testing."""
        pages = [
            PageData(
                url="https://example-landscaping.com",
                page_type="home",
                text_content="Green Thumb Landscaping provides professional lawn care and garden maintenance services for residential and commercial properties.",
                text_length=120,
                images=[],
                scraped_at=datetime.now(),
                scrape_success=True
            ),
            PageData(
                url="https://example-landscaping.com/services",
                page_type="services",
                text_content="Our services include lawn mowing, tree trimming, garden design, and landscape installation. We have a fleet of trucks and professional equipment.",
                text_length=150,
                images=[],
                scraped_at=datetime.now(),
                scrape_success=True
            )
        ]
        
        return BusinessData(
            business_url="https://example-landscaping.com",
            scraped_at=datetime.now(),
            scraping_metadata={},
            pages=pages,
            business_intelligence={
                "page_analysis": {
                    "content_quality_score": 0.8
                }
            }
        )
    
    @patch('openai.ChatCompletion.create')
    def test_analyze_business_success(self, mock_openai):
        """Test successful business analysis."""
        # Mock LLM response
        mock_response = {
            "business_summary": "Professional landscaping company serving residential and commercial clients",
            "business_domain": "landscaping", 
            "naics_code": "561730",
            "naics_reasoning": "Landscaping services classification",
            "primary_services": ["lawn care", "garden maintenance", "tree trimming"],
            "business_scale": "medium_regional",
            "text_risk_indicators": {
                "ecommerce": {"level": "Low", "evidence": [], "reasoning": "No online sales mentioned"},
                "vehicle_use": {"level": "High", "evidence": ["fleet of trucks"], "reasoning": "Fleet operations mentioned"},
                "cyber_risk": {"level": "Low", "evidence": [], "reasoning": "Basic service business"}
            },
            "text_capabilities": ["lawn care", "garden maintenance", "tree trimming", "landscape installation"]
        }
        
        mock_openai.return_value.choices = [
            Mock(message=Mock(content=json.dumps(mock_response)))
        ]
        
        # Execute test
        result = self.summarizer.analyze_business(self.sample_business_data)
        
        # Assertions
        self.assertIsInstance(result, TextAnalysisResult)
        self.assertEqual(result.business_domain, "landscaping")
        self.assertEqual(result.naics_code, "561730")
        self.assertGreater(result.naics_confidence, 0.0)
        self.assertEqual(result.text_risk_indicators["vehicle_use"]["level"], "High")
        self.assertIn("lawn care", result.text_capabilities)
    
    def test_combine_page_content(self):
        """Test page content combination logic."""
        combined = self.summarizer._combine_page_content(self.sample_business_data)
        
        self.assertIn("HOME PAGE", combined)
        self.assertIn("SERVICES PAGE", combined)
        self.assertIn("Green Thumb Landscaping", combined)
        self.assertIn("fleet of trucks", combined)
    
    def test_naics_confidence_calculation(self):
        """Test NAICS confidence scoring."""
        mock_parsed_results = {
            "primary_services": ["lawn care", "tree trimming", "garden design"],
            "business_scale": "medium_regional"
        }
        
        confidence = self.summarizer._calculate_naics_confidence(
            "561730", 
            "landscaping lawn care garden maintenance professional services",
            0.8,  # High quality score
            mock_parsed_results
        )
        
        self.assertGreater(confidence, 0.5)  # Should be reasonably confident
        self.assertLessEqual(confidence, 1.0)  # Should not exceed 1.0
    
    @patch('openai.ChatCompletion.create')
    def test_analyze_business_with_empty_content(self, mock_openai):
        """Test handling of empty content."""
        empty_business_data = BusinessData(
            business_url="https://example.com",
            scraped_at=datetime.now(),
            scraping_metadata={},
            pages=[],
            business_intelligence={}
        )
        
        with self.assertRaises(Exception) as context:
            self.summarizer.analyze_business(empty_business_data)
        
        self.assertIn("No usable text content", str(context.exception))


class TestImageAnalyzer(unittest.TestCase):
    """Test Pass 2: Image Analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock Azure CV client to avoid requiring actual credentials
        with patch('core.image_analysis.ComputerVisionClient'):
            self.analyzer = ImageAnalyzer()
        
        self.sample_text_analysis = self._create_sample_text_analysis()
        self.sample_business_data = self._create_sample_business_data_with_images()
    
    def _create_sample_text_analysis(self) -> TextAnalysisResult:
        """Create sample text analysis result."""
        return TextAnalysisResult(
            business_summary="Professional landscaping company",
            business_domain="landscaping",
            naics_code="561730",
            naics_confidence=0.8,
            naics_reasoning="Landscaping services",
            primary_services=["lawn care", "tree trimming"],
            business_scale="medium_regional",
            text_risk_indicators={},
            text_capabilities=["lawn care", "tree trimming"],
            raw_llm_response="",
            analysis_metadata={}
        )
    
    def _create_sample_business_data_with_images(self) -> BusinessData:
        """Create sample business data with images."""
        pages = [
            PageData(
                url="https://example-landscaping.com",
                page_type="home",
                text_content="Landscaping services",
                text_length=50,
                images=[
                    {
                        "url": "https://example.com/truck.jpg",
                        "alt_text": "Commercial landscaping truck",
                        "title": "Our service vehicle",
                        "width": "400",
                        "height": "300"
                    },
                    {
                        "url": "https://example.com/equipment.jpg", 
                        "alt_text": "Landscaping equipment and tools",
                        "title": "Professional equipment",
                        "width": "500",
                        "height": "400"
                    }
                ],
                scraped_at=datetime.now(),
                scrape_success=True
            )
        ]
        
        return BusinessData(
            business_url="https://example-landscaping.com",
            scraped_at=datetime.now(),
            scraping_metadata={},
            pages=pages,
            business_intelligence={}
        )
    
    def test_filter_business_images(self):
        """Test image filtering logic."""
        filter_result = self.analyzer._filter_business_images(
            self.sample_business_data, 
            self.sample_text_analysis
        )
        
        self.assertGreater(len(filter_result.selected_images), 0)
        self.assertEqual(filter_result.filter_reasons["selected"], len(filter_result.selected_images))
        
        # Check that business-relevant images are prioritized
        selected_image = filter_result.selected_images[0]
        self.assertIn("truck", selected_image["alt_text"].lower())
    
    def test_calculate_image_business_score(self):
        """Test business relevance scoring for images."""
        landscaping_image = {
            "alt_text": "commercial landscaping truck",
            "title": "service vehicle",
            "page_type": "services",
            "width": "400",
            "height": "300"
        }
        
        score = self.analyzer._calculate_image_business_score(landscaping_image, "landscaping")
        self.assertGreater(score, 0.5)  # Should be highly relevant
        
        # Test decorative image gets low score
        decorative_image = {
            "alt_text": "decorative border icon",
            "title": "decoration",
            "page_type": "home",
            "width": "20",
            "height": "20"
        }
        
        score = self.analyzer._calculate_image_business_score(decorative_image, "landscaping")
        self.assertLess(score, 0.3)  # Should be low relevance
    
    def test_is_too_small_filter(self):
        """Test small image filtering."""
        small_image = {"width": "50", "height": "30"}
        large_image = {"width": "400", "height": "300"}
        
        self.assertTrue(self.analyzer._is_too_small(small_image))
        self.assertFalse(self.analyzer._is_too_small(large_image))
    
    def test_is_decorative_filter(self):
        """Test decorative image filtering."""
        decorative_image = {"alt_text": "icon arrow", "url": "https://example.com/icon.png"}
        content_image = {"alt_text": "team photo", "url": "https://example.com/team.jpg"}
        
        self.assertTrue(self.analyzer._is_likely_decorative(decorative_image))
        self.assertFalse(self.analyzer._is_likely_decorative(content_image))
    
    @patch('core.image_analysis.settings')
    def test_analyze_business_images_no_cv_config(self, mock_settings):
        """Test graceful handling when Azure CV is not configured."""
        mock_settings.azure_cv_key = None
        mock_settings.azure_cv_endpoint = None
        
        result = self.analyzer.analyze_business_images(
            self.sample_business_data,
            self.sample_text_analysis
        )
        
        self.assertIsInstance(result, VisualAnalysisResult)
        self.assertTrue(result.analysis_metadata.get("analysis_skipped", False))
        self.assertIn("not configured", result.analysis_metadata.get("skip_reason", ""))


class TestBusinessIntelligencePipeline(unittest.TestCase):
    """Test Pass 3: Complete Pipeline Integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock external dependencies
        with patch('core.pipeline.WebsiteScraper'), \
             patch('core.pipeline.BusinessSummarizer'), \
             patch('core.pipeline.ImageAnalyzer'):
            self.pipeline = BusinessIntelligencePipeline()
    
    def test_aggregate_risk_indicators_vehicle_use(self):
        """Test vehicle use risk aggregation (MAX rule)."""
        text_risks = {
            "vehicle_use": {
                "level": "Medium",
                "evidence": ["delivery services mentioned"],
                "reasoning": "Text indicates vehicle use"
            }
        }
        
        visual_risks = {
            "vehicle_use": {
                "level": "High", 
                "evidence": ["commercial trucks detected"],
                "reasoning": "Visual confirmation of fleet"
            }
        }
        
        result = self.pipeline._aggregate_risk_indicators(text_risks, visual_risks)
        
        # Should take MAX (High from visual)
        self.assertEqual(result["vehicle_use"]["level"], "High")
        self.assertEqual(result["vehicle_use"]["primary_source"], "visual")
        self.assertGreater(result["vehicle_use"]["confidence"], 0.7)  # Should have high confidence due to alignment
    
    def test_aggregate_risk_indicators_ecommerce(self):
        """Test e-commerce risk aggregation (text-primary rule)."""
        text_risks = {
            "ecommerce": {
                "level": "High",
                "evidence": ["online store", "payment processing"],
                "reasoning": "Clear e-commerce functionality"
            }
        }
        
        visual_risks = {
            "ecommerce": {
                "level": "Low",
                "evidence": [],
                "reasoning": "No visual e-commerce evidence"
            }
        }
        
        result = self.pipeline._aggregate_risk_indicators(text_risks, visual_risks)
        
        # Should use text level (High)
        self.assertEqual(result["ecommerce"]["level"], "High")
        self.assertEqual(result["ecommerce"]["primary_source"], "text")
    
    def test_combine_capabilities(self):
        """Test capability combination and deduplication."""
        text_capabilities = ["lawn care", "garden design", "tree trimming"]
        visual_enhancements = ["heavy equipment operations", "lawn care", "mobile services"]
        
        result = self.pipeline._combine_capabilities(text_capabilities, visual_enhancements)
        
        # Should combine and deduplicate
        self.assertIn("lawn care", result)  # From both sources
        self.assertIn("heavy equipment operations", result)  # From visual
        self.assertIn("garden design", result)  # From text
        
        # Should not have duplicates
        self.assertEqual(len([c for c in result if c.lower() == "lawn care"]), 1)
    
    def test_calculate_risk_confidence(self):
        """Test risk confidence calculation."""
        text_risk = {
            "evidence": ["online store", "payment processing"],
            "reasoning": "Clear e-commerce evidence"
        }
        visual_risk = {"evidence": [], "reasoning": ""}
        
        confidence = self.pipeline._calculate_risk_confidence(text_risk, visual_risk, "ecommerce")
        
        self.assertGreater(confidence, 0.5)  # Should be confident with good text evidence
        self.assertLessEqual(confidence, 1.0)
    
    @patch('core.pipeline.openai.ChatCompletion.create')
    def test_generate_enhanced_summary(self, mock_openai):
        """Test enhanced summary generation."""
        # Mock LLM response
        mock_openai.return_value.choices = [
            Mock(message=Mock(content='{"enhanced_business_summary": "Professional landscaping company with heavy equipment capabilities and commercial fleet operations"}'))
        ]
        
        text_analysis = TextAnalysisResult(
            business_summary="Professional landscaping company",
            business_domain="landscaping",
            naics_code="561730",
            naics_confidence=0.8,
            naics_reasoning="",
            primary_services=["lawn care"],
            business_scale="medium",
            text_risk_indicators={},
            text_capabilities=[],
            raw_llm_response="",
            analysis_metadata={}
        )
        
        visual_analysis = VisualAnalysisResult(
            visual_business_insights={
                "equipment_detected": [{"type": "truck", "confidence": 0.9}],
                "capability_enhancements": ["heavy equipment operations"]
            },
            image_risk_indicators={},
            analysis_metadata={},
            raw_cv_responses=[]
        )
        
        enhanced_summary = self.pipeline._generate_enhanced_summary(text_analysis, visual_analysis)
        
        self.assertIn("heavy equipment", enhanced_summary)
        self.assertIn("fleet", enhanced_summary)
    
    def test_create_fallback_analysis(self):
        """Test fallback analysis creation."""
        start_time = datetime.now()
        
        fallback = self.pipeline._create_fallback_analysis(
            "https://example.com",
            "Connection timeout",
            start_time
        )
        
        self.assertIsInstance(fallback, FinalBusinessAnalysis)
        self.assertIn("Analysis failed", fallback.enhanced_business_summary)
        self.assertEqual(fallback.naics_confidence, 0.0)
        self.assertEqual(fallback.pipeline_metadata["pipeline_execution"]["status"], "failed")


class TestEndToEndIntegration(unittest.TestCase):
    """Test complete end-to-end scenarios."""
    
    @patch('core.scraper.WebsiteScraper.scrape_business')
    @patch('core.summarizer.openai.ChatCompletion.create')
    @patch('core.image_analysis.ComputerVisionClient')
    @patch('core.pipeline.openai.ChatCompletion.create')
    def test_complete_pipeline_success(self, mock_pipeline_openai, mock_cv_client, 
                                     mock_summarizer_openai, mock_scraper):
        """Test complete successful pipeline execution."""
        # Mock scraper response
        mock_scraper.return_value = BusinessData(
            business_url="https://example-landscaping.com",
            scraped_at=datetime.now(),
            scraping_metadata={},
            pages=[
                PageData(
                    url="https://example-landscaping.com",
                    page_type="home",
                    text_content="Professional landscaping services with fleet operations",
                    text_length=60,
                    images=[
                        {
                            "url": "https://example.com/truck.jpg",
                            "alt_text": "commercial truck",
                            "width": "400",
                            "height": "300"
                        }
                    ],
                    scraped_at=datetime.now(),
                    scrape_success=True
                )
            ],
            business_intelligence={
                "page_analysis": {"content_quality_score": 0.8}
            }
        )
        
        # Mock text analysis LLM response
        mock_summarizer_openai.return_value.choices = [
            Mock(message=Mock(content=json.dumps({
                "business_summary": "Professional landscaping company",
                "business_domain": "landscaping",
                "naics_code": "561730",
                "naics_reasoning": "Landscaping services",
                "primary_services": ["landscaping"],
                "business_scale": "medium",
                "text_risk_indicators": {
                    "vehicle_use": {"level": "Medium", "evidence": ["fleet operations"], "reasoning": "Fleet mentioned"}
                },
                "text_capabilities": ["landscaping"]
            })))
        ]
        
        # Mock Azure CV response
        mock_cv_analysis = Mock()
        mock_cv_analysis.objects = [Mock(object_property="truck", confidence=0.9, rectangle=None)]
        mock_cv_analysis.categories = []
        mock_cv_analysis.description = Mock(captions=[], tags=[])
        mock_cv_analysis.tags = []
        
        mock_cv_instance = Mock()
        mock_cv_instance.analyze_image.return_value = mock_cv_analysis
        mock_cv_client.return_value = mock_cv_instance
        
        # Mock integration LLM response
        mock_pipeline_openai.return_value.choices = [
            Mock(message=Mock(content='{"enhanced_business_summary": "Professional landscaping company with commercial fleet operations"}'))
        ]
        
        # Execute pipeline
        pipeline = BusinessIntelligencePipeline()
        result = pipeline.analyze_business_website("https://example-landscaping.com")
        
        # Assertions
        self.assertIsInstance(result, FinalBusinessAnalysis)
        self.assertEqual(result.naics_code, "561730")
        self.assertGreater(result.naics_confidence, 0.0)
        self.assertIn("landscaping", result.enhanced_business_summary.lower())
        self.assertEqual(result.final_risk_indicators["vehicle_use"]["level"], "High")  # Should be upgraded by visual


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2)