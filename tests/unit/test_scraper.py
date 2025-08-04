"""
Unit tests for the website scraper module.

This module contains tests for the WebsiteScraper class and related
functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from core.scraper import WebsiteScraper


class TestWebsiteScraper(unittest.TestCase):
    """Test cases for WebsiteScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WebsiteScraper()
        self.mock_html = """
        <html>
            <head><title>Test Business</title></head>
            <body>
                <header><nav>Navigation</nav></header>
                <main>
                    <h1>Test Business Company</h1>
                    <p>We provide excellent services for business customers.</p>
                    <section>
                        <h2>Our Services</h2>
                        <p>We offer web development, consulting, and digital marketing services.</p>
                    </section>
                    <img src="/logo.png" alt="company logo" width="200" height="100">
                    <img src="/team.jpg" alt="our team" width="400" height="300">
                    <img src="/pixel.gif" alt="tracking" width="1" height="1">
                </main>
                <footer>Copyright 2024</footer>
            </body>
        </html>
        """
    
    def test_url_validation_valid_urls(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://test.org",
            "https://subdomain.example.com/path"
        ]
        for url in valid_urls:
            self.assertTrue(self.scraper._validate_url(url))
    
    def test_url_validation_invalid_urls(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",
            "javascript:alert('test')",
            "",
            "file:///etc/passwd"
        ]
        for url in invalid_urls:
            self.assertFalse(self.scraper._validate_url(url))
    
    def test_clean_text_functionality(self):
        """Test text cleaning functionality."""
        dirty_text = "  Multiple   spaces\n\nand\n\nnewlines  "
        cleaned = self.scraper._clean_text(dirty_text)
        self.assertEqual(cleaned, "Multiple spaces and newlines")
        
        # Test length limiting
        long_text = "a" * 15000
        cleaned_long = self.scraper._clean_text(long_text)
        self.assertTrue(len(cleaned_long) <= 10003)  # 10000 + "..."
    
    def test_image_validation(self):
        """Test image validation logic."""
        from bs4 import BeautifulSoup
        
        # Valid content image
        soup = BeautifulSoup('<img src="/content.jpg" alt="product photo" width="300" height="200">', 'html.parser')
        img = soup.find('img')
        self.assertTrue(self.scraper._is_valid_image(img, "product photo"))
        
        # Invalid small image
        soup = BeautifulSoup('<img src="/small.jpg" alt="bullet" width="10" height="10">', 'html.parser')
        img = soup.find('img')
        self.assertFalse(self.scraper._is_valid_image(img, "bullet"))
        
        # Invalid logo image
        soup = BeautifulSoup('<img src="/logo.png" alt="company logo">', 'html.parser')
        img = soup.find('img')
        self.assertFalse(self.scraper._is_valid_image(img, "company logo"))
    
    @patch('core.scraper.requests.Session.get')
    def test_scrape_text_success(self, mock_get):
        """Test successful text scraping."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = self.mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.scrape_text("https://example.com")
        
        self.assertIn("Test Business Company", result)
        self.assertIn("excellent services", result)
        self.assertNotIn("Navigation", result)  # Should exclude nav
        self.assertNotIn("Copyright", result)  # Should exclude footer
    
    @patch('core.scraper.requests.Session.get')
    def test_scrape_text_request_error(self, mock_get):
        """Test text scraping with request error."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(Exception) as context:
            self.scraper.scrape_text("https://example.com")
        
        self.assertIn("Error scraping text", str(context.exception))
    
    @patch('core.scraper.requests.Session.get')
    def test_scrape_images_success(self, mock_get):
        """Test successful image scraping."""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = self.mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.scraper.scrape_images("https://example.com")
        
        # Should find the team image but filter out logo and pixel
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['alt_text'], 'our team')
        self.assertEqual(result[0]['url'], 'https://example.com/team.jpg')
    
    @patch('core.scraper.requests.Session.get')
    def test_scrape_images_request_error(self, mock_get):
        """Test image scraping with request error."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(Exception) as context:
            self.scraper.scrape_images("https://example.com")
        
        self.assertIn("Error scraping images", str(context.exception))
    
    def test_scrape_text_invalid_url(self):
        """Test text scraping with invalid URL."""
        with self.assertRaises(ValueError) as context:
            self.scraper.scrape_text("invalid_url")
        
        self.assertIn("Invalid URL", str(context.exception))
    
    def test_scrape_images_invalid_url(self):
        """Test image scraping with invalid URL."""
        with self.assertRaises(ValueError) as context:
            self.scraper.scrape_images("invalid_url")
        
        self.assertIn("Invalid URL", str(context.exception))
    
    @patch('core.scraper.requests.Session.get')
    def test_scrape_with_timeout(self, mock_get):
        """Test that scraping respects timeout settings."""
        mock_response = Mock()
        mock_response.content = self.mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        self.scraper.scrape_text("https://example.com")
        
        # Verify timeout was passed to requests
        mock_get.assert_called_with("https://example.com", timeout=self.scraper.timeout)
    
    @patch('core.scraper.requests.Session.get')
    def test_robots_txt_allowed(self, mock_get):
        """Test scraping when robots.txt allows access."""
        # Mock robots.txt response (allows all)
        robots_response = Mock()
        robots_response.status_code = 200
        robots_response.content = b"User-agent: *\nAllow: /"
        
        # Mock main page response
        main_response = Mock()
        main_response.content = self.mock_html.encode('utf-8')
        main_response.raise_for_status.return_value = None
        
        # Configure mock to return different responses for different URLs
        def mock_get_side_effect(url, timeout=None):
            if url.endswith('/robots.txt'):
                return robots_response
            else:
                return main_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # This should work fine
        result = self.scraper.scrape_text("https://example.com/page")
        self.assertIn("Test Business Company", result)
    
    @patch('core.scraper.requests.Session.get')
    def test_robots_txt_disallowed(self, mock_get):
        """Test scraping when robots.txt disallows access."""
        # Mock robots.txt response (disallows all)
        robots_response = Mock()
        robots_response.status_code = 200
        robots_response.content = b"User-agent: *\nDisallow: /"
        
        def mock_get_side_effect(url, timeout=None):
            if url.endswith('/robots.txt'):
                return robots_response
            else:
                # This shouldn't be called due to robots.txt
                raise Exception("Should not reach here")
        
        mock_get.side_effect = mock_get_side_effect
        
        with self.assertRaises(ValueError) as context:
            self.scraper.scrape_text("https://example.com/page")
        
        self.assertIn("Robots.txt disallows scraping", str(context.exception))
    
    @patch('core.scraper.requests.Session.get')
    def test_robots_txt_not_found(self, mock_get):
        """Test scraping when robots.txt is not found (should allow)."""
        # Mock robots.txt 404 response
        robots_response = Mock()
        robots_response.status_code = 404
        
        # Mock main page response
        main_response = Mock()
        main_response.content = self.mock_html.encode('utf-8')
        main_response.raise_for_status.return_value = None
        
        def mock_get_side_effect(url, timeout=None):
            if url.endswith('/robots.txt'):
                return robots_response
            else:
                return main_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Should work fine when robots.txt is not found
        result = self.scraper.scrape_text("https://example.com/page")
        self.assertIn("Test Business Company", result)


if __name__ == '__main__':
    unittest.main()