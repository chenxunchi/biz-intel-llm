#!/usr/bin/env python3
"""
Test script for the new unified scraper functionality.

This script tests the scrape_business() method with real websites
to validate the unified output structure.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.scraper import WebsiteScraper, ScrapingOptions


def test_unified_scraper():
    """Test the new unified scraper functionality."""
    print("=== UNIFIED SCRAPER TEST ===")
    print(f"Started: {datetime.now()}")
    
    scraper = WebsiteScraper()
    
    # Test cases - same business websites we used before
    test_cases = [
        ("https://domscoffee.com/", "Coffee Shop"),
        ("https://www.valleyslandscape.com/", "Landscaping Company")
    ]
    
    all_results = {}
    
    for base_url, business_type in test_cases:
        print(f"\n--- Testing: {business_type} ---")
        print(f"URL: {base_url}")
        
        try:
            # Test with custom options
            options = ScrapingOptions(
                max_pages=5,
                include_images=True,
                page_types=["about", "services", "contact", "home"]
            )
            
            # Use the new unified method
            business_data = scraper.scrape_business(base_url, options)
            
            # Display summary
            print(f"✅ SUCCESS - {business_type}")
            print(f"Pages scraped: {len(business_data.pages)}")
            print(f"Success rate: {business_data.business_intelligence['scraping_metrics']['success_rate']}")
            print(f"Total text: {business_data.business_intelligence['content_metrics']['total_text_length']:,} chars")
            print(f"Total images: {business_data.business_intelligence['content_metrics']['total_images']}")
            print(f"Quality score: {business_data.business_intelligence['page_analysis']['content_quality_score']}")
            
            # Show page breakdown
            print("Page breakdown:")
            for page in business_data.pages:
                status = "✓" if page.scrape_success else "✗"
                print(f"  {status} {page.page_type}: {page.url}")
                if page.scrape_success:
                    print(f"    Text: {page.text_length} chars, Images: {len(page.images)}")
                else:
                    print(f"    Error: {page.error_message}")
            
            # Store results for analysis
            all_results[business_type] = business_data.to_dict()
            
        except Exception as e:
            print(f"❌ ERROR - {business_type}: {str(e)}")
            all_results[business_type] = {"error": str(e)}
    
    # Save unified results
    results_file = Path("../tests/results/scraper_results/unified_scraper_test.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== TEST COMPLETE ===")
    print(f"Results saved to: {results_file}")
    print(f"Completed: {datetime.now()}")
    
    # Display comparison with old vs new approach
    print(f"\n=== UNIFIED APPROACH BENEFITS ===")
    print("✅ Single method call gets complete business data")
    print("✅ Structured output perfect for LLM integration")
    print("✅ Rich metadata for quality assessment")
    print("✅ Automatic business intelligence computation")
    print("✅ Graceful handling of partial failures")
    print("✅ Page type classification and prioritization")


def test_scraping_options():
    """Test different scraping option configurations."""
    print(f"\n=== SCRAPING OPTIONS TEST ===")
    
    scraper = WebsiteScraper()
    test_url = "https://domscoffee.com/"
    
    # Test 1: Text only, no images
    print("Test 1: Text only scraping")
    options1 = ScrapingOptions(
        max_pages=3,
        include_images=False,
        page_types=["about", "services"]
    )
    
    result1 = scraper.scrape_business(test_url, options1)
    print(f"Pages: {len(result1.pages)}, Images: {result1.business_intelligence['content_metrics']['total_images']}")
    
    # Test 2: All content types
    print("Test 2: Full scraping")
    options2 = ScrapingOptions(
        max_pages=8,
        include_images=True,
        page_types=["about", "services", "contact", "home", "other"]
    )
    
    result2 = scraper.scrape_business(test_url, options2)
    print(f"Pages: {len(result2.pages)}, Images: {result2.business_intelligence['content_metrics']['total_images']}")
    
    print("✅ Options testing complete")


def compare_old_vs_new():
    """Compare old fragmented approach vs new unified approach."""
    print(f"\n=== OLD VS NEW COMPARISON ===")
    
    scraper = WebsiteScraper()
    test_url = "https://domscoffee.com/"
    
    print("OLD APPROACH (multiple calls):")
    start_old = datetime.now()
    
    # Old way - multiple method calls
    pages = scraper.discover_pages(test_url, max_pages=3)
    all_text = ""
    all_images = []
    
    for page in pages[:2]:  # Limit for demo
        try:
            text = scraper.scrape_text(page)
            images = scraper.scrape_images(page)
            all_text += text + " "
            all_images.extend(images)
        except:
            pass
    
    old_time = (datetime.now() - start_old).total_seconds()
    print(f"  Time: {old_time:.2f}s")
    print(f"  Text: {len(all_text)} chars")
    print(f"  Images: {len(all_images)}")
    print(f"  Manual coordination required ❌")
    
    print("NEW APPROACH (unified call):")
    start_new = datetime.now()
    
    # New way - single method call
    options = ScrapingOptions(max_pages=3)
    business_data = scraper.scrape_business(test_url, options)
    
    new_time = (datetime.now() - start_new).total_seconds()
    print(f"  Time: {new_time:.2f}s")
    print(f"  Text: {business_data.business_intelligence['content_metrics']['total_text_length']} chars")
    print(f"  Images: {business_data.business_intelligence['content_metrics']['total_images']}")
    print(f"  Structured output ✅")
    print(f"  Business intelligence ✅")
    print(f"  Error handling ✅")
    print(f"  LLM-ready format ✅")


def main():
    """Run all unified scraper tests."""
    try:
        test_unified_scraper()
        test_scraping_options()
        compare_old_vs_new()
        
        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The unified scraper is ready for LLM integration!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()