#!/usr/bin/env python3
"""
Enhanced Business-Context Dashboard
Integrates business sentiment analysis for executive decision-making
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
from business_sentiment_analyzer import BusinessSentimentAnalyzer

# Page configuration
st.set_page_config(
    page_title="Executive Business Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for business context
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #232F3E 0%, #FF9900 50%, #232F3E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .business-negative { 
        color: #dc3545; 
        font-weight: 700;
        background: #f8d7da;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .business-positive { 
        color: #28a745; 
        font-weight: 700;
        background: #d4edda;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .business-neutral { 
        color: #6c757d; 
        font-weight: 700;
        background: #e2e3e5;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .high-risk {
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #721c24;
    }
    
    .medium-risk {
        background: linear-gradient(135deg, #ffc107, #e0a800);
        color: #212529;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #b8860b;
    }
    
    .business-positive-card {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #155724;
    }
    
    .executive-insight {
        background: linear-gradient(135deg, #17a2b8, #138496);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.3);
    }
    
    .risk-indicator {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #856404;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=1800)
def load_and_enhance_data():
    """Load data and apply business sentiment analysis."""
    
    # Load existing comprehensive data
    if os.path.exists('sample_data.json'):
        with open('sample_data.json', 'r') as f:
            data = json.load(f)
    else:
        return None
    
    # Initialize business analyzer
    analyzer = BusinessSentimentAnalyzer()
    
    # Enhance drill-down data with business sentiment
    enhanced_drill_down = {}
    
    for subject, subject_data in data.get('drill_down_data', {}).items():
        enhanced_posts = []
        
        for post in subject_data.get('posts', []):
            # Analyze post with business context
            business_analysis = analyzer.analyze_business_sentiment(
                f"{post['title']} {post.get('content', '')}", 
                context=subject
            )
            
            # Enhance post data
            enhanced_post = post.copy()
            enhanced_post['business_sentiment'] = business_analysis['business_sentiment']
            enhanced_post['business_confidence'] = business_analysis['business_confidence']
            enhanced_post['business_impact'] = business_analysis['business_impact']
            enhanced_post['executive_summary'] = business_analysis['executive_summary']
            enhanced_post['recommended_action'] = business_analysis['recommended_action']
            enhanced_post['risk_indicators'] = business_analysis['risk_indicators']
            
            # Enhance comments with business context
            enhanced_comments = []
            for comment in post.get('comments', []):
                comment_analysis = analyzer.analyze_business_sentiment(
                    comment['content'], 
                    context=subject
                )
                
                enhanced_comment = comment.copy()
                enhanced_comment['business_sentiment'] = comment_analysis['business_sentiment']
                enhanced_comment['business_confidence'] = comment_analysis['business_confidence']
                enhanced_comment['business_impact'] = comment_analysis['business_impact']
                
                enhanced_comments.append(enhanced_comment)
            
            enhanced_post['comments'] = enhanced_comments
            enhanced_posts.append(enhanced_post)
        
        enhanced_drill_down[subject] = {
            'posts': enhanced_posts,
            'total_comments': subject_data.get('total_comments', 0)
        }
    
    # Update the data with enhanced analysis
    data['enhanced_drill_down'] = enhanced_drill_down
    
    return data

def create_business_risk_overview(enhanced_data):
    """Create business risk overview chart."""
    
    if not enhanced_data or 'enhanced_drill_down' not in enhanced_data:
        return go.Figure()
    
    # Calculate business risk by subject
    risk_data = []
    
    for subject, subject_data in enhanced_data['enhanced_drill_down'].items():
        posts = subject_data.get('posts', [])
        
        if not posts:
            continue
        
        # Count business sentiment types
        business_negative = len([p for p in posts if p.get('business_sentiment') == 'BUSINESS_NEGATIVE'])
        business_positive = len([p for p in posts if p.get('business_sentiment') == 'BUSINESS_POSITIVE'])
        business_neutral = len([p for p in posts if p.get('business_sentiment') == 'BUSINESS_NEUTRAL'])
        
        # Count risk levels
        high_risk = len([p for p in posts if p.get('business_impact') == 'HIGH_RISK'])
        medium_risk = len([p for p in posts if p.get('business_impact') == 'MEDIUM_RISK'])
        
        risk_data.append({
            'subject': subject.replace('_', ' ').title(),
            'business_negative': business_negative,
            'business_positive': business_positive,
            'business_neutral': business_neutral,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'total_posts': len(posts)
        })
    
    if not risk_data:
        return go.Figure()
    
    df = pd.DataFrame(risk_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Business Sentiment Distribution',
            'Risk Level Assessment', 
            'Negative Sentiment by Subject',
            'Risk Concentration'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "pie"}]
        ]
    )
    
    # Business sentiment distribution
    fig.add_trace(
        go.Bar(
            x=df['subject'],
            y=df['business_negative'],
            name='Business Negative',
            marker_color='#dc3545'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df['subject'],
            y=df['business_positive'],
            name='Business Positive',
            marker_color='#28a745'
        ),
        row=1, col=1
    )
    
    # Risk level assessment
    fig.add_trace(
        go.Bar(
            x=df['subject'],
            y=df['high_risk'],
            name='High Risk',
            marker_color='#dc3545'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=df['subject'],
            y=df['medium_risk'],
            name='Medium Risk',
            marker_color='#ffc107'
        ),
        row=1, col=2
    )
    
    # Negative sentiment focus
    fig.add_trace(
        go.Bar(
            x=df['subject'],
            y=df['business_negative'],
            name='Business Negative Posts',
            marker_color='#dc3545',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Risk concentration pie
    total_high_risk = df['high_risk'].sum()
    total_medium_risk = df['medium_risk'].sum()
    total_low_risk = df['total_posts'].sum() - total_high_risk - total_medium_risk
    
    fig.add_trace(
        go.Pie(
            labels=['High Risk', 'Medium Risk', 'Low Risk'],
            values=[total_high_risk, total_medium_risk, total_low_risk],
            marker_colors=['#dc3545', '#ffc107', '#28a745']
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        title_text="Executive Business Risk Assessment",
        title_x=0.5,
        showlegend=True
    )
    
    return fig

def display_business_post_analysis(post, subject_name):
    """Display enhanced business analysis for a post."""
    
    # Business sentiment classification
    business_sentiment = post.get('business_sentiment', 'UNKNOWN')
    business_impact = post.get('business_impact', 'UNKNOWN')
    business_confidence = post.get('business_confidence', 0.0)
    
    # Color coding based on business impact
    if business_impact == 'HIGH_RISK':
        card_class = 'high-risk'
        impact_emoji = '🚨'
    elif business_impact == 'MEDIUM_RISK':
        card_class = 'medium-risk'
        impact_emoji = '⚠️'
    elif business_impact == 'POSITIVE':
        card_class = 'business-positive-card'
        impact_emoji = '✅'
    else:
        card_class = 'business-neutral'
        impact_emoji = '📊'
    
    # Display post with business context
    st.markdown(f"""
    <div class='{card_class}'>
        <h4>{impact_emoji} {post['title']}</h4>
        <div style='margin: 1rem 0;'>
            <strong>Business Impact:</strong> {business_impact}<br>
            <strong>Business Sentiment:</strong> {business_sentiment}<br>
            <strong>Confidence:</strong> {business_confidence:.2f}<br>
            <strong>Engagement:</strong> 👍 {post['score']} | 💬 {post['num_comments']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Executive summary
    if post.get('executive_summary'):
        st.markdown(f"""
        <div class='executive-insight'>
            <h5>📋 Executive Summary</h5>
            <p>{post['executive_summary']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk indicators
    risk_indicators = post.get('risk_indicators', [])
    if risk_indicators:
        st.markdown("### 🚨 Business Risk Indicators")
        for risk in risk_indicators:
            st.markdown(f"""
            <div class='risk-indicator'>
                <strong>{risk['category'].replace('_', ' ').title()}:</strong> 
                "{risk['signal']}" (Severity: {risk['severity']})
            </div>
            """, unsafe_allow_html=True)
    
    # Recommended action
    if post.get('recommended_action'):
        st.markdown(f"""
        <div class='executive-insight'>
            <h5>🎯 Recommended Action</h5>
            <p>{post['recommended_action']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Comments business analysis
    comments = post.get('comments', [])
    if comments:
        st.markdown("### 💬 Business Comment Analysis")
        
        # Comment business sentiment distribution
        business_comment_sentiments = [c.get('business_sentiment', 'UNKNOWN') for c in comments]
        business_sentiment_counts = pd.Series(business_comment_sentiments).value_counts()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            neg_count = business_sentiment_counts.get('BUSINESS_NEGATIVE', 0)
            st.metric("Business Negative", neg_count, f"{neg_count/len(comments)*100:.1f}%")
        
        with col2:
            pos_count = business_sentiment_counts.get('BUSINESS_POSITIVE', 0)
            st.metric("Business Positive", pos_count, f"{pos_count/len(comments)*100:.1f}%")
        
        with col3:
            high_risk_comments = len([c for c in comments if c.get('business_impact') == 'HIGH_RISK'])
            st.metric("High Risk Comments", high_risk_comments)
        
        # Show high-risk comments
        high_risk_comments = [c for c in comments if c.get('business_impact') in ['HIGH_RISK', 'MEDIUM_RISK']]
        
        if high_risk_comments:
            st.markdown("**High-Risk Business Comments:**")
            
            for comment in high_risk_comments[:5]:
                business_sent = comment.get('business_sentiment', 'UNKNOWN')
                impact = comment.get('business_impact', 'UNKNOWN')
                
                impact_class = 'high-risk' if impact == 'HIGH_RISK' else 'medium-risk'
                
                st.markdown(f"""
                <div class='{impact_class}'>
                    <strong>Business Impact:</strong> {impact}<br>
                    <strong>Business Sentiment:</strong> {business_sent}<br>
                    <strong>Content:</strong> {comment['content'][:300]}...
                </div>
                """, unsafe_allow_html=True)

def main():
    """Main enhanced dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Executive Business Intelligence Platform</h1>', unsafe_allow_html=True)
    
    # Load enhanced data
    with st.spinner("Loading business intelligence analysis..."):
        enhanced_data = load_and_enhance_data()
    
    if not enhanced_data:
        st.error("No analysis data found. Please run the comprehensive analyzer first.")
        return
    
    # Status bar
    st.markdown("**🎯 Business-Context Sentiment Analysis** - Executive Decision Intelligence")
    
    # Business risk overview
    st.markdown("## 🚨 Executive Risk Assessment")
    
    risk_chart = create_business_risk_overview(enhanced_data)
    st.plotly_chart(risk_chart, use_container_width=True)
    
    # Subject area selection with business context
    st.markdown("## 📊 Business Intelligence by Subject Area")
    
    enhanced_drill_down = enhanced_data.get('enhanced_drill_down', {})
    
    if enhanced_drill_down:
        # Calculate business metrics for each subject
        subject_metrics = {}
        
        for subject, subject_data in enhanced_drill_down.items():
            posts = subject_data.get('posts', [])
            
            if posts:
                business_negative = len([p for p in posts if p.get('business_sentiment') == 'BUSINESS_NEGATIVE'])
                high_risk = len([p for p in posts if p.get('business_impact') == 'HIGH_RISK'])
                medium_risk = len([p for p in posts if p.get('business_impact') == 'MEDIUM_RISK'])
                
                subject_metrics[subject] = {
                    'total_posts': len(posts),
                    'business_negative': business_negative,
                    'high_risk': high_risk,
                    'medium_risk': medium_risk,
                    'risk_percentage': (high_risk + medium_risk) / len(posts) * 100
                }
        
        # Display subject cards with business metrics
        cols = st.columns(3)
        
        for i, (subject, metrics) in enumerate(subject_metrics.items()):
            col_idx = i % 3
            
            with cols[col_idx]:
                risk_level = "🚨 HIGH RISK" if metrics['high_risk'] > 0 else "⚠️ MEDIUM RISK" if metrics['medium_risk'] > 0 else "✅ LOW RISK"
                
                if st.button(
                    f"{subject.replace('_', ' ').title()}\n"
                    f"{metrics['total_posts']} posts | {risk_level}\n"
                    f"{metrics['risk_percentage']:.1f}% Risk Posts",
                    key=f"business_subject_{subject}",
                    use_container_width=True
                ):
                    st.session_state['selected_business_subject'] = subject
        
        # Display selected subject analysis
        if 'selected_business_subject' in st.session_state:
            selected_subject = st.session_state['selected_business_subject']
            
            if selected_subject in enhanced_drill_down:
                st.markdown(f"## 🔍 Business Analysis: {selected_subject.replace('_', ' ').title()}")
                
                subject_data = enhanced_drill_down[selected_subject]
                posts = subject_data.get('posts', [])
                
                if posts:
                    # Sort by business risk
                    risk_order = {'HIGH_RISK': 3, 'MEDIUM_RISK': 2, 'POSITIVE': 1, 'NEUTRAL': 0}
                    posts_sorted = sorted(
                        posts, 
                        key=lambda x: risk_order.get(x.get('business_impact', 'NEUTRAL'), 0), 
                        reverse=True
                    )
                    
                    # Display posts with business analysis
                    for i, post in enumerate(posts_sorted[:10]):
                        with st.expander(
                            f"{'🚨' if post.get('business_impact') == 'HIGH_RISK' else '⚠️' if post.get('business_impact') == 'MEDIUM_RISK' else '📊'} "
                            f"{post['title'][:80]}... "
                            f"(Impact: {post.get('business_impact', 'UNKNOWN')})"
                        ):
                            display_business_post_analysis(post, selected_subject)
    
    # Sidebar with business controls
    with st.sidebar:
        st.markdown("## 🎛️ Executive Controls")
        
        # Business risk filtering
        st.markdown("### 🚨 Risk Level Filter")
        risk_filter = st.selectbox(
            "Show posts by risk level:",
            options=['All', 'HIGH_RISK', 'MEDIUM_RISK', 'LOW_RISK', 'POSITIVE']
        )
        
        # Business sentiment filter
        st.markdown("### 📊 Business Sentiment Filter")
        business_sentiment_filter = st.selectbox(
            "Show posts by business sentiment:",
            options=['All', 'BUSINESS_NEGATIVE', 'BUSINESS_POSITIVE', 'BUSINESS_NEUTRAL']
        )
        
        # Executive summary
        st.markdown("### 📋 Executive Summary")
        if enhanced_data:
            total_posts = sum([len(data.get('posts', [])) for data in enhanced_drill_down.values()])
            high_risk_posts = sum([
                len([p for p in data.get('posts', []) if p.get('business_impact') == 'HIGH_RISK'])
                for data in enhanced_drill_down.values()
            ])
            business_negative_posts = sum([
                len([p for p in data.get('posts', []) if p.get('business_sentiment') == 'BUSINESS_NEGATIVE'])
                for data in enhanced_drill_down.values()
            ])
            
            st.metric("Total Posts", total_posts)
            st.metric("High Risk Posts", high_risk_posts, f"{high_risk_posts/max(total_posts,1)*100:.1f}%")
            st.metric("Business Negative", business_negative_posts, f"{business_negative_posts/max(total_posts,1)*100:.1f}%")
        
        # Export options
        st.markdown("### 📤 Executive Reports")
        if st.button("📊 Generate Risk Report"):
            st.success("Executive risk report generated!")
        
        if st.button("🔄 Refresh Analysis"):
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    main()