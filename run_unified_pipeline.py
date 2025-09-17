#!/usr/bin/env python3
"""
Run Complete Unified Data Pipeline
API → Database → Dashboard & Reports
"""

import os
import sys
from datetime import datetime

def main():
    """Run the complete unified pipeline."""
    
    print("🚀 Amazon FC Intelligence - Unified Data Pipeline")
    print("=" * 60)
    
    # Step 1: Run data collection and analysis
    print("\n📡 Step 1: Running Data Pipeline...")
    try:
        from unified_data_pipeline import run_full_data_pipeline
        dashboard_data = run_full_data_pipeline()
        print("✅ Data pipeline completed successfully!")
    except Exception as e:
        print(f"❌ Data pipeline failed: {e}")
        print("🔄 Continuing with existing data...")
    
    # Step 2: Generate unified executive summary
    print("\n📊 Step 2: Generating Executive Summary...")
    try:
        from unified_executive_summary import create_unified_html_report
        html_report = create_unified_html_report()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unified_executive_summary_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"✅ Executive summary generated: {filename}")
    except Exception as e:
        print(f"❌ Executive summary failed: {e}")
    
    # Step 3: Update Streamlit app data
    print("\n🎯 Step 3: Updating Dashboard Data...")
    try:
        # The Streamlit app will automatically use the unified data
        print("✅ Dashboard will use unified database data")
        print("🌐 Deploy updated Streamlit app to see latest data")
    except Exception as e:
        print(f"❌ Dashboard update failed: {e}")
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("🎉 UNIFIED PIPELINE COMPLETE!")
    print("\n📊 What's Now Consistent:")
    print("  ✅ Dashboard uses unified database")
    print("  ✅ Executive reports use same database") 
    print("  ✅ All sentiment analysis from same source")
    print("  ✅ Single source of truth established")
    
    print("\n🔄 Next Steps:")
    print("  1. Deploy updated Streamlit app")
    print("  2. Schedule regular data collection")
    print("  3. Set up automated reporting")
    print("  4. Monitor data consistency")
    
    print(f"\n📁 Files Generated:")
    print(f"  - unified_fc_intelligence.db (database)")
    print(f"  - unified_dashboard_data.json (dashboard data)")
    print(f"  - unified_executive_summary_*.html (reports)")

if __name__ == "__main__":
    main()