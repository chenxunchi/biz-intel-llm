#!/usr/bin/env python3
"""
Live test script for the website scraper.

This script tests the scraper functionality with real websites
to verify it works before Azure deployment.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.scraper import WebsiteScraper


def test_scraper_basic():
    """Test basic scraper functionality."""
    print("🕷️ Testing Website Scraper\n")
    
    scraper = WebsiteScraper()
    
    # Test URLs - using reliable, public sites
    test_urls = [
        "example.com",  # Test URL normalization
        "https://httpbin.org",  # Reliable test site
        "python.org",  # Another reliable site
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"📄 Test {i}: {url}")
        print("-" * 50)
        
        try:
            # Test page discovery
            print("🔍 Discovering pages...")
            pages = scraper.discover_pages(url, max_pages=3)
            print(f"Found {len(pages)} pages:")
            for page in pages:
                print(f"  - {page}")
            
            # Test text scraping on first page
            if pages:
                print(f"\n📝 Scraping text from: {pages[0]}")
                text = scraper.scrape_text(pages[0])
                print(f"Text length: {len(text)} characters")
                print(f"Preview: {text[:200]}..." if len(text) > 200 else f"Full text: {text}")
                
                # Test image scraping
                print(f"\n🖼️ Scraping images from: {pages[0]}")
                images = scraper.scrape_images(pages[0])
                print(f"Found {len(images)} images:")
                for img in images[:3]:  # Show first 3 images
                    print(f"  - {img['url']} (alt: '{img['alt_text']}')")
                if len(images) > 3:
                    print(f"  ... and {len(images) - 3} more images")
            
        except Exception as e:
            print(f"❌ Error testing {url}: {str(e)}")
        
        print("\n" + "="*70 + "\n")


def test_url_normalization():
    """Test URL normalization functionality."""
    print("🔧 Testing URL Normalization\n")
    
    scraper = WebsiteScraper()
    
    test_cases = [
        "example.com",
        "www.python.org",
        "https://github.com",
        "httpbin.org/get",
    ]
    
    for url in test_cases:
        try:
            normalized = scraper._normalize_url(url)
            is_valid = scraper._validate_url(normalized)
            print(f"'{url}' → '{normalized}' (valid: {is_valid})")
        except Exception as e:
            print(f"'{url}' → Error: {str(e)}")
    
    print("\n" + "="*70 + "\n")


def test_robots_txt():
    """Test robots.txt compliance."""
    print("🤖 Testing Robots.txt Compliance\n")
    
    scraper = WebsiteScraper()
    
    # Test sites with known robots.txt
    test_sites = [
        "https://httpbin.org",  # Usually allows
        "https://www.google.com",  # Has restrictive robots.txt
    ]
    
    for site in test_sites:
        try:
            can_fetch = scraper._can_fetch(site)
            print(f"{site}: {'✅ Allowed' if can_fetch else '❌ Disallowed'}")
        except Exception as e:
            print(f"{site}: Error checking robots.txt: {str(e)}")
    
    print("\n" + "="*70 + "\n")


def save_test_results():
    """Save test results to file for debugging."""
    print("💾 Saving Test Results\n")
    
    scraper = WebsiteScraper()
    
    try:
        # Test with a reliable site
        test_url = "https://httpbin.org"
        
        # Get discovered pages
        pages = scraper.discover_pages(test_url, max_pages=5)
        
        # Get content from first page
        if pages:
            text_content = scraper.scrape_text(pages[0])
            image_data = scraper.scrape_images(pages[0])
            
            # Save results
            results = {
                "test_url": test_url,
                "discovered_pages": pages,
                "text_content": text_content,
                "image_data": image_data,
                "timestamp": str(Path(__file__).stat().st_mtime)
            }
            
            output_file = Path("test_results.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Test results saved to: {output_file}")
            print(f"📄 Pages discovered: {len(pages)}")
            print(f"📝 Text length: {len(text_content)} characters")
            print(f"🖼️ Images found: {len(image_data)}")
        
    except Exception as e:
        print(f"❌ Error saving test results: {str(e)}")


def main():
    """Run all tests."""
    print("🚀 Live Scraper Testing Suite")
    print("="*70)
    print()
    
    try:
        # Run test suite
        test_url_normalization()
        test_robots_txt()
        test_scraper_basic()
        save_test_results()
        
        print("🎉 All tests completed!")
        print("\nNext steps:")
        print("1. Check test_results.json for detailed output")
        print("2. Run unit tests: python -m pytest tests/")
        print("3. Deploy to Azure when ready")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()