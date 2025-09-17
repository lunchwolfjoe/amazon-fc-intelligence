# 🎯 Elite Amazon FC Employee Intelligence Platform

## Live Dashboard
**🚀 [View Live Dashboard](https://your-app-name.streamlit.app)** *(Will be updated after deployment)*

## Overview
Advanced ML-powered sentiment analysis and employee intelligence platform for Amazon FC discussions. Features comprehensive topic classification, deep drill-down analysis, and real-time insights.

## Key Features

### 🤖 ML-Powered Analysis
- **AWS Comprehend Integration**: Enterprise-grade sentiment analysis
- **Automatic Topic Classification**: 9 subject areas with ML confidence scoring
- **Key Phrase Extraction**: Identifies trending topics and themes
- **Batch Processing**: Cost-optimized API usage

### 📊 Advanced Analytics
- **Subject Area Intelligence**: Compensation, Management, Working Conditions, etc.
- **Sentiment Deep Dive**: Drill down from overview to individual comments
- **Temporal Analysis**: Date range filtering and trend analysis
- **Engagement Metrics**: Score, comments, and interaction analysis

### 🔍 Interactive Drill-Down
- **Topic Selection**: Click any subject area for detailed analysis
- **Advanced Filtering**: Sentiment, engagement, ML confidence filters
- **Comment Analysis**: Individual comment sentiment with confidence scores
- **Real-time Updates**: Live data refresh capabilities

### 📈 Executive Reporting
- **Comprehensive Reports**: HTML and JSON exports
- **Cost Tracking**: AWS usage and cost optimization
- **Data Quality Metrics**: ML confidence and analysis reliability

## Technology Stack

- **Frontend**: Streamlit with advanced Plotly visualizations
- **ML/AI**: AWS Comprehend for sentiment analysis and topic modeling
- **Data**: Reddit API with SQLite storage
- **Deployment**: Streamlit Cloud with GitHub integration

## Data Sources

- **Primary**: Reddit r/amazonfc subreddit
- **Analysis Period**: Last 14 days (configurable)
- **Content Types**: Posts and comments with full thread analysis
- **Update Frequency**: Configurable refresh intervals

## Sample Analysis Results

### Subject Area Breakdown
- **Compensation**: 64 posts, avg sentiment: -0.03
- **Management**: 36 posts, avg sentiment: -0.28  
- **General Experience**: 32 posts, avg sentiment: -0.10
- **Schedule/Time**: 16 posts, avg sentiment: -0.17
- **Career Development**: 2 posts, avg sentiment: 0.13

### ML Analysis Quality
- **Total Items Analyzed**: 951 (152 posts + 799 comments)
- **AWS API Calls**: 48 calls
- **Analysis Cost**: $0.12
- **Average ML Confidence**: 0.85

## Deployment

### Streamlit Cloud (Recommended)
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy `streamlit_app.py`
5. Configure secrets for AWS credentials

### Local Development
```bash
pip install -r requirements.txt
streamlit run elite_fc_dashboard.py
```

## Configuration

### Environment Variables
```bash
# Reddit API (Required)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# AWS Credentials (Optional - uses AWS CLI if not set)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Database
DATABASE_URL=sqlite:///reddit_data.db
```

### Streamlit Secrets
For Streamlit Cloud deployment, add these to your app secrets:
```toml
[reddit]
client_id = "your_reddit_client_id"
client_secret = "your_reddit_client_secret"
user_agent = "your_user_agent"

[aws]
access_key_id = "your_aws_access_key"
secret_access_key = "your_aws_secret_key"
region = "us-east-1"
```

## Usage

### Data Collection
```bash
# Collect comprehensive data
python comprehensive_fc_analyzer.py

# Generate executive report
python comprehend_executive_analyzer.py
```

### Dashboard Features
1. **Overview**: Executive metrics and subject area distribution
2. **Topic Selection**: Click subject areas for deep analysis
3. **Filtering**: Date range, sentiment, engagement, confidence filters
4. **Drill-Down**: Individual post and comment analysis
5. **Export**: Generate reports and export data

## Cost Optimization

- **Batch Processing**: Efficient AWS API usage
- **Caching**: Streamlit data caching for performance
- **Rate Limiting**: Respectful Reddit API usage
- **Budget Controls**: Built-in cost monitoring

## Security & Privacy

- **No PII Storage**: Only public Reddit data
- **Anonymized Analysis**: No personal information tracking
- **Secure Credentials**: Environment variable configuration
- **Rate Limited**: Respectful API usage

## Support & Documentation

- **Live Dashboard**: Interactive analysis platform
- **Executive Reports**: Comprehensive HTML/JSON exports
- **API Documentation**: Built-in help and examples
- **Cost Tracking**: Real-time usage monitoring

---

## 🚀 Quick Start

1. **View Live Dashboard**: [Click here](https://your-app-name.streamlit.app)
2. **Select Subject Area**: Click any topic for detailed analysis
3. **Apply Filters**: Use date range and sentiment filters
4. **Drill Down**: Explore individual posts and comments
5. **Export Results**: Generate executive reports

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reddit API    │───▶│  Data Collection │───▶│   SQLite DB     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ AWS Comprehend  │◀───│  ML Analysis     │───▶│  JSON Results   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Streamlit Cloud │◀───│  Elite Dashboard │───▶│  Live Analytics │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

Built with ❤️ for Amazon FC employee intelligence and sentiment analysis.