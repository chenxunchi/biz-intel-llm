"""
Business Intelligence Risk Assessment - Streamlit Frontend

Complete web interface for the 3-pass business intelligence analysis system.
Provides professional insurance underwriting intelligence from business websites.
"""

import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px
import pandas as pd

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.pipeline import BusinessIntelligencePipeline, FinalBusinessAnalysis
from core.scraper import ScrapingOptions


def main():
    """Main Streamlit application."""
    configure_page()
    render_header()
    
    # Sidebar configuration
    config = render_sidebar()
    
    # Main analysis interface
    url = render_url_input()
    
    if url:
        if st.button("🧠 Analyze Business", type="primary", use_container_width=True):
            run_complete_analysis(url, config)


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Business Intelligence Risk Assessment",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_header():
    """Render application header and description."""
    st.title("🧠 Business Intelligence Risk Assessment")
    st.markdown("""
    **Complete 3-Pass AI Analysis for Insurance Underwriting**
    
    This system analyzes business websites to extract comprehensive intelligence including:
    - Business classification (NAICS codes)
    - Risk indicators (vehicle use, e-commerce, cyber risk)  
    - Business capabilities and scale assessment
    - Visual confirmation through image analysis
    """)


def render_sidebar():
    """Render sidebar configuration options."""
    st.sidebar.header("⚙️ Analysis Configuration")
    
    config = {
        'max_pages': st.sidebar.slider("Max pages to analyze", 1, 15, 8),
        'max_images': st.sidebar.slider("Max images per analysis", 1, 10, 5),
    }
    
    st.sidebar.header("🎯 System Info")
    st.sidebar.info("""
    **3-Pass Pipeline:**
    1. 🔍 Text Analysis & NAICS
    2. 👁️ Image Analysis & Visual Risks  
    3. 🧠 Intelligent Integration
    """)
    
    return config


def render_url_input():
    """Render URL input interface."""
    st.header("🌐 Business Website Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Enter business website URL:",
            placeholder="landscaping-company.com",
            help="Enter any business website. The system will normalize URLs automatically."
        )
    
    with col2:
        st.write("**Example URLs:**")
        if st.button("🏗️ Construction Co.", type="secondary"):
            st.rerun()
        if st.button("🍕 Restaurant", type="secondary"):
            st.rerun()
    
    return url


def run_complete_analysis(url: str, config: dict):
    """Execute complete 3-pass business intelligence analysis."""
    
    # Initialize progress tracking
    progress_container = st.container()
    results_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize pipeline
            status_text.text("🔧 Initializing AI pipeline...")
            pipeline = BusinessIntelligencePipeline()
            progress_bar.progress(0.1)
            
            # Configure scraping
            scraping_options = ScrapingOptions(
                max_pages=config['max_pages'],
                max_images_per_site=config['max_images']
            )
            
            # Pass 1: Text Analysis
            status_text.text("📝 Pass 1: Analyzing website content and business data...")
            progress_bar.progress(0.3)
            
            # Pass 2: Image Analysis  
            status_text.text("🖼️ Pass 2: Analyzing business images with Azure Computer Vision...")
            progress_bar.progress(0.6)
            
            # Pass 3: Integration
            status_text.text("🧠 Pass 3: Integrating insights and generating final assessment...")
            progress_bar.progress(0.9)
            
            # Execute pipeline
            start_time = datetime.now()
            analysis_result = pipeline.analyze_business_website(url, scraping_options)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            progress_bar.progress(1.0)
            status_text.text("✅ Business intelligence analysis complete!")
            
        except Exception as e:
            progress_bar.progress(1.0)
            status_text.text("❌ Analysis failed")
            st.error(f"Analysis failed: {str(e)}")
            
            with st.expander("🔧 Troubleshooting"):
                st.markdown("""
                **Common Solutions:**
                - Verify API keys: `OPENAI_API_KEY`, `AZURE_CV_KEY`, `AZURE_CV_ENDPOINT`
                - Check website accessibility
                - Try a different business website
                """)
            return
    
    # Display results
    with results_container:
        display_analysis_results(analysis_result, execution_time, url)


def display_analysis_results(analysis: FinalBusinessAnalysis, execution_time: float, original_url: str):
    """Display comprehensive business analysis results."""
    
    st.divider()
    st.header("📈 Business Intelligence Report")
    
    # Executive Summary Card
    with st.container():
        st.subheader("📋 Executive Summary")
        summary_col1, summary_col2 = st.columns([2, 1])
        
        with summary_col1:
            st.markdown(f"**Business Description:**")
            st.write(analysis.enhanced_business_summary)
        
        with summary_col2:
            st.metric("Analysis Time", f"{execution_time:.1f}s")
            st.metric("Pipeline Version", "3-Pass v1.0")
    
    # Key Classification
    st.subheader("🎯 Business Classification")
    class_col1, class_col2, class_col3 = st.columns(3)
    
    with class_col1:
        confidence_color = "🟢" if analysis.naics_confidence > 0.8 else "🟡" if analysis.naics_confidence > 0.6 else "🔴"
        st.metric(
            "NAICS Industry Code",
            analysis.naics_code,
            help=f"Confidence: {analysis.naics_confidence:.0%}"
        )
        st.write(f"{confidence_color} Confidence: {analysis.naics_confidence:.0%}")
    
    with class_col2:
        high_risk_count = sum(1 for risk in analysis.final_risk_indicators.values() if risk["level"] == "High")
        medium_risk_count = sum(1 for risk in analysis.final_risk_indicators.values() if risk["level"] == "Medium")
        
        st.metric("High Risk Areas", high_risk_count)
        st.metric("Medium Risk Areas", medium_risk_count)
    
    with class_col3:
        st.metric("Total Capabilities", len(analysis.business_capabilities))
        if analysis.visual_enhancements:
            st.metric("Visual Enhancements", len(analysis.visual_enhancements))
    
    # Risk Dashboard
    st.subheader("⚠️ Risk Assessment Dashboard")
    
    # Create risk visualization
    risk_data = []
    risk_colors_map = {"High": "#ff4444", "Medium": "#ffaa00", "Low": "#44ff44"}
    
    for risk_type, risk_info in analysis.final_risk_indicators.items():
        risk_data.append({
            "Risk Type": risk_type.replace("_", " ").title(),
            "Level": risk_info["level"],
            "Confidence": risk_info["confidence"],
            "Primary Source": risk_info["primary_source"]
        })
    
    if risk_data:
        df_risks = pd.DataFrame(risk_data)
        
        # Risk level chart
        fig = px.bar(
            df_risks, 
            x="Risk Type", 
            y="Confidence",
            color="Level",
            color_discrete_map=risk_colors_map,
            title="Risk Confidence by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Risk Analysis
    st.subheader("🔍 Detailed Risk Analysis")
    
    for risk_type, risk_data in analysis.final_risk_indicators.items():
        risk_name = risk_type.replace("_", " ").title()
        level = risk_data["level"]
        confidence = risk_data["confidence"]
        
        # Risk level styling
        if level == "High":
            risk_color = "🔴"
            alert_type = "error"
        elif level == "Medium":
            risk_color = "🟡"
            alert_type = "warning" 
        else:
            risk_color = "🟢"
            alert_type = "success"
        
        with st.expander(f"{risk_color} **{risk_name}**: {level} Risk (Confidence: {confidence:.0%})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Assessment:** {risk_data['reasoning']}")
                
                if risk_data['evidence']:
                    st.write("**Supporting Evidence:**")
                    for evidence in risk_data['evidence']:
                        st.write(f"• {evidence}")
            
            with col2:
                st.write(f"**Primary Source:** {risk_data['primary_source']}")
                
                # Confidence indicator
                conf_pct = confidence
                if conf_pct >= 0.8:
                    st.success(f"High confidence ({conf_pct:.0%})")
                elif conf_pct >= 0.6:
                    st.warning(f"Medium confidence ({conf_pct:.0%})")
                else:
                    st.error(f"Low confidence ({conf_pct:.0%})")
    
    # Business Capabilities
    st.subheader("🛠️ Business Capabilities & Services")
    
    if analysis.business_capabilities:
        # Regular capabilities
        regular_caps = [cap for cap in analysis.business_capabilities if cap not in analysis.visual_enhancements]
        visual_caps = analysis.visual_enhancements
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Text-Based Capabilities:**")
            for cap in regular_caps:
                st.write(f"• {cap}")
        
        with col2:
            if visual_caps:
                st.write("**🔍 Visually Enhanced Capabilities:**")
                for cap in visual_caps:
                    st.write(f"🔍 **{cap}**")
                st.info("These capabilities were enhanced or confirmed through image analysis")
    else:
        st.warning("No specific business capabilities identified")
    
    # Export Section
    st.subheader("💾 Export & Integration")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        st.write("**📥 Download Options:**")
        
        # JSON export
        results_json = json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        st.download_button(
            label="📊 Complete Analysis (JSON)",
            data=results_json,
            file_name=f"business_intel_{timestamp}.json",
            mime="application/json",
            help="Full structured data for system integration"
        )
        
        # Summary export
        summary_report = generate_summary_report(analysis, original_url, execution_time)
        st.download_button(
            label="📄 Executive Summary (TXT)",
            data=summary_report,
            file_name=f"business_summary_{timestamp}.txt",
            mime="text/plain",
            help="Human-readable summary report"
        )
    
    with export_col2:
        st.write("**🔗 Integration Ready:**")
        st.code(f"""
# Use this analysis in your system:
pipeline = BusinessIntelligencePipeline()
result = pipeline.analyze_business_website("{original_url}")

# Access key data:
naics_code = result.naics_code
risk_indicators = result.final_risk_indicators
business_summary = result.enhanced_business_summary
        """, language="python")
    
    # Technical Details
    with st.expander("🔧 Technical Analysis Details"):
        metadata = analysis.pipeline_metadata
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Pipeline Execution:**")
            exec_info = metadata.get("pipeline_execution", {})
            st.write(f"• Started: {exec_info.get('started_at', 'unknown')}")
            st.write(f"• Duration: {exec_info.get('total_duration_seconds', execution_time):.1f}s")
            st.write(f"• Version: {exec_info.get('version', 'unknown')}")
        
        with col2:
            st.write("**Analysis Quality:**")
            quality = metadata.get("integration_quality", {})
            
            text_success = quality.get('text_analysis_success', False)
            visual_success = quality.get('visual_analysis_success', False)
            integration_success = quality.get('integration_used_visual_data', False)
            
            st.write(f"• Text Analysis: {'✅' if text_success else '❌'}")
            st.write(f"• Visual Analysis: {'✅' if visual_success else '❌'}")
            st.write(f"• Visual Integration: {'✅' if integration_success else '❌'}")
            
            confidence_boost = quality.get('final_confidence_boost', 0)
            if confidence_boost > 0:
                st.write(f"• Integration Boost: +{confidence_boost:.1%}")


def generate_summary_report(analysis: FinalBusinessAnalysis, url: str, execution_time: float) -> str:
    """Generate human-readable summary report."""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Risk summary
    risk_summary = []
    for risk_type, risk_info in analysis.final_risk_indicators.items():
        risk_name = risk_type.replace("_", " ").title()
        risk_summary.append(f"• {risk_name}: {risk_info['level']} ({risk_info['confidence']:.0%} confidence)")
    
    report = f"""BUSINESS INTELLIGENCE REPORT
Generated: {timestamp}
Analysis Time: {execution_time:.1f} seconds
Website: {url}

BUSINESS SUMMARY
{analysis.enhanced_business_summary}

INDUSTRY CLASSIFICATION
NAICS Code: {analysis.naics_code}
Classification Confidence: {analysis.naics_confidence:.0%}

RISK ASSESSMENT
{chr(10).join(risk_summary)}

BUSINESS CAPABILITIES
{chr(10).join([f"• {cap}" for cap in analysis.business_capabilities])}

VISUAL ENHANCEMENTS
{chr(10).join([f"• {enhancement}" for enhancement in analysis.visual_enhancements]) if analysis.visual_enhancements else "None detected"}

---
Generated by Business Intelligence Risk Assessment System
3-Pass Pipeline v1.0
"""
    return report


def render_example_section():
    """Render example business types for testing."""
    with st.expander("💡 Try These Example Business Types"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🏗️ Construction & Trade:**")
            st.write("• Landscaping companies")
            st.write("• HVAC contractors") 
            st.write("• Plumbing services")
        
        with col2:
            st.write("**🚛 Transportation & Logistics:**")
            st.write("• Delivery services")
            st.write("• Moving companies")
            st.write("• Fleet operations")
        
        with col3:
            st.write("**🏪 Retail & Services:**")
            st.write("• Restaurants")
            st.write("• Professional services")
            st.write("• E-commerce stores")


if __name__ == "__main__":
    main()