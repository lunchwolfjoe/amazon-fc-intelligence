#!/usr/bin/env python3
"""
Deploy with real data - creates a production-ready package
"""

import os
import shutil
import json
from datetime import datetime

def prepare_deployment():
    """Prepare deployment with real data."""
    
    print("🚀 Preparing deployment with real data...")
    
    # Copy the latest analysis data
    analysis_files = [f for f in os.listdir('.') if f.startswith('comprehensive_fc_analysis_') and f.endswith('.json')]
    
    if analysis_files:
        latest_file = sorted(analysis_files)[-1]
        shutil.copy(latest_file, 'sample_data.json')
        print(f"✅ Copied {latest_file} as sample_data.json")
    
    # Copy database if it exists
    if os.path.exists('reddit_data.db'):
        shutil.copy('reddit_data.db', 'sample_reddit_data.db')
        print("✅ Copied reddit_data.db as sample_reddit_data.db")
    
    # Update .gitignore to include sample data
    gitignore_content = """# Environment variables
.env
*.env
.env.local
.env.production

# Database files (exclude samples)
reddit_data.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
temp/

# Analysis outputs (keep sample data)
comprehensive_fc_analysis_*.json
!sample_data.json
comprehend_executive_report_*.html
executive_deep_dive_report_*.html

# AWS credentials (never commit)
credentials
config

# Reddit data (keep sample)
reddit_collector.log
reddit_collector_checkpoint.json
reddit_collector_metrics.json

# Node modules (for React dashboard)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
build/
dist/

# Sensitive directories
reddit-data-collector/
sentimentscreen/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Updated .gitignore for deployment")
    
    # Create deployment info
    deployment_info = {
        "deployment_date": datetime.now().isoformat(),
        "data_included": True,
        "sample_data_file": "sample_data.json",
        "sample_db_file": "sample_reddit_data.db" if os.path.exists('sample_reddit_data.db') else None,
        "dashboard_file": "elite_fc_dashboard.py",
        "streamlit_entry": "streamlit_app.py"
    }
    
    with open('deployment_info.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print("✅ Created deployment_info.json")
    print("🎯 Ready for GitHub deployment!")

if __name__ == "__main__":
    prepare_deployment()