#!/usr/bin/env python3
"""
Test script to download and verify scraped images.

This demonstrates how to actually download the images that the scraper found.
"""

import requests
import json
import os
from pathlib import Path
from urllib.parse import urlparse

def download_sample_images():
    """Download a few sample images to verify scraper results."""
    
    # Create download directory
    download_dir = Path("../tests/results/scraper_results/downloaded_images")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== IMAGE DOWNLOAD TEST ===")
    
    # Load scraper results
    with open('../tests/results/scraper_results/business_scraper_test.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    downloaded_count = 0
    
    # Download one image from each business
    for business_type, data in results.items():
        print(f"\n--- {business_type} ---")
        
        # Get first page with images
        for page_data in data['page_analysis']:
            if page_data.get('sample_images'):
                
                # Download first image
                img = page_data['sample_images'][0]
                img_url = img['url']
                
                print(f"Downloading: {img_url[:60]}...")
                
                try:
                    # Download image
                    response = requests.get(img_url, timeout=10)
                    response.raise_for_status()
                    
                    # Generate filename
                    parsed_url = urlparse(img_url)
                    filename = f"{business_type.replace(' ', '_')}_{downloaded_count}.jpg"
                    filepath = download_dir / filename
                    
                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Verify file
                    file_size = filepath.stat().st_size
                    print(f"SUCCESS: Saved {file_size:,} bytes to {filepath}")
                    
                    # Save metadata
                    metadata = {
                        'business_type': business_type,
                        'source_page': page_data['url'],
                        'image_url': img_url,
                        'alt_text': img['alt_text'],
                        'file_size': file_size,
                        'local_path': str(filepath)
                    }
                    
                    metadata_file = filepath.with_suffix('.json')
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    downloaded_count += 1
                    break
                    
                except Exception as e:
                    print(f"ERROR: {e}")
                    
                break  # Only download from first page per business
    
    print(f"\n=== DOWNLOAD COMPLETE ===")
    print(f"Downloaded: {downloaded_count} images")
    print(f"Location: {download_dir}")
    
    # List downloaded files
    print("\nDownloaded files:")
    for file in download_dir.glob("*"):
        if file.suffix in ['.jpg', '.png', '.webp']:
            size = file.stat().st_size
            print(f"  {file.name} ({size:,} bytes)")

if __name__ == "__main__":
    download_sample_images()