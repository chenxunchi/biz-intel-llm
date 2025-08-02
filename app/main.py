"""
Main Streamlit application entry point for Business Intelligence Risk Assessment.

This module provides the web interface for analyzing business websites
and extracting insurance-relevant risk indicators.
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.scraper import WebsiteScraper


def main():
    """Main Streamlit app function."""
    st.set_page_config(
        page_title="Business Intelligence Risk Assessment", 
        page_icon="🕷️",
        layout="wide"
    )
    
    st.title("🕷️ Business Intelligence Risk Assessment")
    st.write("Test the website scraper functionality on Azure")
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    max_pages = st.sidebar.slider("Max pages to discover", 1, 20, 5)
    cache_enabled = st.sidebar.checkbox("Enable caching", value=True)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🌐 Website Analysis")
        url = st.text_input(
            "Enter business website URL:", 
            placeholder="example.com or https://www.company.com",
            help="You can enter incomplete URLs like 'abc.com' - the scraper will normalize them"
        )
    
    with col2:
        st.header("📊 Quick Actions")
        if st.button("🔍 Test Discovery Only", type="secondary"):
            if url:
                test_discovery(url, max_pages)
        
        if st.button("📝 Full Analysis", type="primary"):
            if url:
                full_analysis(url, max_pages)
            else:
                st.error("Please enter a URL first")


def test_discovery(url: str, max_pages: int):
    """Test page discovery functionality."""
    st.header("🔍 Page Discovery Test")
    
    with st.spinner("Discovering pages..."):
        try:
            scraper = WebsiteScraper()
            pages = scraper.discover_pages(url, max_pages=max_pages)
            
            st.success(f"✅ Discovered {len(pages)} pages")
            
            # Display results
            for i, page in enumerate(pages, 1):
                st.write(f"{i}. `{page}`")
            
            # Show raw data
            with st.expander("📋 Raw Data"):
                st.json(pages)
                
        except Exception as e:
            st.error(f"❌ Discovery failed: {str(e)}")


def full_analysis(url: str, max_pages: int):
    """Run full scraper analysis."""
    st.header("📊 Full Website Analysis")
    
    scraper = WebsiteScraper()
    
    # Step 1: Discovery
    st.subheader("🔍 Step 1: Page Discovery")
    with st.spinner("Discovering pages..."):
        try:
            pages = scraper.discover_pages(url, max_pages=max_pages)
            st.success(f"Found {len(pages)} pages")
            
            # Show discovered pages
            with st.expander(f"📄 Discovered Pages ({len(pages)})"):
                for i, page in enumerate(pages, 1):
                    st.write(f"{i}. {page}")
            
        except Exception as e:
            st.error(f"❌ Page discovery failed: {str(e)}")
            return
    
    # Step 2: Content Analysis
    st.subheader("📝 Step 2: Content Extraction")
    
    # Analyze each page
    all_results = []
    
    for i, page_url in enumerate(pages):
        with st.expander(f"📄 Page {i+1}: {page_url}", expanded=(i == 0)):
            col1, col2 = st.columns(2)
            
            # Text scraping
            with col1:
                st.write("**📝 Text Content:**")
                try:
                    with st.spinner(f"Scraping text from page {i+1}..."):
                        text_content = scraper.scrape_text(page_url)
                    
                    st.success(f"✅ Extracted {len(text_content)} characters")
                    
                    # Show preview
                    preview_length = 300
                    if len(text_content) > preview_length:
                        st.text_area(
                            "Preview:", 
                            text_content[:preview_length] + "...", 
                            height=150,
                            key=f"text_preview_{i}"
                        )
                        
                        # Full text in expander
                        with st.expander("📖 Full Text"):
                            st.text(text_content)
                    else:
                        st.text_area(
                            "Full Text:", 
                            text_content, 
                            height=150,
                            key=f"text_full_{i}"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Text scraping failed: {str(e)}")
                    text_content = ""
            
            # Image scraping
            with col2:
                st.write("**🖼️ Images Found:**")
                try:
                    with st.spinner(f"Scraping images from page {i+1}..."):
                        images = scraper.scrape_images(page_url)
                    
                    st.success(f"✅ Found {len(images)} images")
                    
                    if images:
                        # Show image details
                        for j, img in enumerate(images[:5]):  # Show first 5
                            st.write(f"**Image {j+1}:**")
                            st.write(f"- URL: `{img['url']}`")
                            st.write(f"- Alt text: {img['alt_text']}")
                            if img['width'] and img['height']:
                                st.write(f"- Size: {img['width']}x{img['height']}")
                        
                        if len(images) > 5:
                            st.info(f"... and {len(images) - 5} more images")
                        
                        # Raw image data
                        with st.expander("📋 Raw Image Data"):
                            st.json(images)
                    else:
                        st.info("No relevant images found")
                    
                except Exception as e:
                    st.error(f"❌ Image scraping failed: {str(e)}")
                    images = []
            
            # Store results
            all_results.append({
                "url": page_url,
                "text_content": text_content,
                "images": images,
                "text_length": len(text_content),
                "image_count": len(images)
            })
    
    # Step 3: Summary
    st.subheader("📊 Step 3: Analysis Summary")
    
    total_text = sum(len(result["text_content"]) for result in all_results)
    total_images = sum(result["image_count"] for result in all_results)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pages Analyzed", len(pages))
    with col2:
        st.metric("Total Text (chars)", f"{total_text:,}")
    with col3:
        st.metric("Total Images", total_images)
    with col4:
        st.metric("Avg Text/Page", f"{total_text // len(pages) if pages else 0:,}")
    
    # Download results
    st.subheader("💾 Export Results")
    results_json = json.dumps(all_results, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download Results (JSON)",
        data=results_json,
        file_name=f"scraper_results_{url.replace('://', '_').replace('/', '_')}.json",
        mime="application/json"
    )
    
    st.success("🎉 Analysis complete! Scroll up to see detailed results.")


if __name__ == "__main__":
    main()