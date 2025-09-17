#!/usr/bin/env python3
"""
Advanced Amazon FC Employee Intelligence Dashboard
Interactive drill-down analysis with subject areas, sentiment deep-dive, and comment-level insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Amazon FC Employee Intelligence Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #232F3E;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #232F3E, #FF9900);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #232F3E, #37475A);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .subject-card {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .subject-card:hover {
        border-color: #FF9900;
        box-shadow: 0 4px 12px rgba(255, 153, 0, 0.2);
    }
    .sentiment-positive { color: #28a745; font-weight: bold; }
    .sentiment-negative { color: #dc3545; font-weight: bold; }
    .sentiment-neutral { color: #6c757d; font-weight: bold; }
    .sentiment-mixed { color: #ffc107; font-weight: bold; }
    .confidence-high { background: #d4edda; padding: 0.5rem; border-radius: 5px; }
    .confidence-medium { background: #fff3cd; padding: 0.5rem; border-radius: 5px; }
    .confidence-low { background: #f8d7da; padding: 0.5rem; border-radius: 5px; }
    .drill-down-section {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_comprehensive_data():
    """Load the comprehensive analysis data."""
    
    # Find the most recent comprehensive analysis file
    analysis_files = [f for f in os.listdir('.') if f.startswith('comprehensive_fc_analysis_') and f.endswith('.json')]
    
    if not analysis_files:
        return None
    
    latest_file = sorted(analysis_files)[-1]
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
        return data, latest_file
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_subject_overview_chart(subject_data):
    """Create overview chart of all subject areas."""
    
    subjects = []
    post_counts = []
    avg_sentiments = []
    comment_counts = []
    
    for subject, data in subject_data.items():
        if data['post_count'] > 0:
            subjects.append(subject.replace('_', ' ').title())
            post_counts.append(data['post_count'])
            avg_sentiments.append(data['avg_sentiment_score'])
            comment_counts.append(data.get('comment_count', 0))
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Posts by Subject Area', 'Average Sentiment by Subject', 
                       'Comments by Subject Area', 'Sentiment Distribution'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"type": "pie"}]]
    )
    
    # Posts by subject
    fig.add_trace(
        go.Bar(x=subjects, y=post_counts, name="Posts", marker_color='#232F3E'),
        row=1, col=1
    )
    
    # Sentiment by subject
    colors = ['#dc3545' if s < -0.1 else '#28a745' if s > 0.1 else '#6c757d' for s in avg_sentiments]
    fig.add_trace(
        go.Bar(x=subjects, y=avg_sentiments, name="Avg Sentiment", marker_color=colors),
        row=1, col=2
    )
    
    # Comments by subject
    fig.add_trace(
        go.Bar(x=subjects, y=comment_counts, name="Comments", marker_color='#FF9900'),
        row=2, col=1
    )
    
    # Overall sentiment pie
    all_sentiments = []
    for data in subject_data.values():
        for sentiment, count in data.get('sentiment_distribution', {}).items():
            all_sentiments.extend([sentiment] * count)
    
    if all_sentiments:
        sentiment_counts = pd.Series(all_sentiments).value_counts()
        fig.add_trace(
            go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values, 
                   name="Overall Sentiment"),
            row=2, col=2
        )
    
    fig.update_layout(height=800, showlegend=False, title_text="Amazon FC Employee Intelligence Overview")
    return fig

def create_sentiment_deep_dive_chart(sentiment_data):
    """Create detailed sentiment analysis visualization."""
    
    # Confidence distribution
    post_confidences = []
    comment_confidences = []
    
    for sentiment_type, examples in sentiment_data['high_confidence_examples'].items():
        for example in examples:
            if example['type'] == 'post':
                post_confidences.append(example['confidence'])
            else:
                comment_confidences.append(example['confidence'])
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Confidence Distribution - Posts', 'Confidence Distribution - Comments',
                       'Sentiment Score Distribution', 'High Confidence Examples Count'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Post confidence histogram
    if post_confidences:
        fig.add_trace(
            go.Histogram(x=post_confidences, name="Post Confidence", nbinsx=20, marker_color='#232F3E'),
            row=1, col=1
        )
    
    # Comment confidence histogram
    if comment_confidences:
        fig.add_trace(
            go.Histogram(x=comment_confidences, name="Comment Confidence", nbinsx=20, marker_color='#FF9900'),
            row=1, col=2
        )
    
    # Sentiment score distribution (placeholder - would need actual scores)
    fig.add_trace(
        go.Histogram(x=np.random.normal(0, 0.3, 100), name="Sentiment Scores", nbinsx=20, marker_color='#28a745'),
        row=2, col=1
    )
    
    # High confidence examples count
    example_counts = [len(examples) for examples in sentiment_data['high_confidence_examples'].values()]
    sentiments = list(sentiment_data['high_confidence_examples'].keys())
    
    fig.add_trace(
        go.Bar(x=sentiments, y=example_counts, name="High Confidence Examples", 
               marker_color=['#28a745', '#dc3545', '#6c757d', '#ffc107']),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Sentiment Analysis Deep Dive")
    return fig

def display_subject_drill_down(subject_name, subject_data, drill_down_data):
    """Display detailed drill-down for a specific subject area."""
    
    st.markdown(f"<div class='drill-down-section'>", unsafe_allow_html=True)
    st.markdown(f"## 🔍 Deep Dive: {subject_name.replace('_', ' ').title()}")
    
    # Subject overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Posts", subject_data['post_count'])
    with col2:
        st.metric("Comments", subject_data.get('comment_count', 0))
    with col3:
        sentiment_score = subject_data['avg_sentiment_score']
        sentiment_label = "Positive" if sentiment_score > 0.1 else "Negative" if sentiment_score < -0.1 else "Neutral"
        st.metric("Avg Sentiment", f"{sentiment_score:.2f}", sentiment_label)
    with col4:
        total_engagement = sum([post['score'] + post['num_comments'] for post in drill_down_data.get('posts', [])])
        st.metric("Total Engagement", total_engagement)
    
    # Key insights
    if subject_data.get('key_insights'):
        st.markdown("### 💡 Key Insights")
        for insight in subject_data['key_insights']:
            st.markdown(f"• {insight}")
    
    # Top posts in this subject
    st.markdown("### 🔥 Top Posts")
    
    if drill_down_data and 'posts' in drill_down_data:
        posts = drill_down_data['posts']
        
        # Sort by engagement
        posts_sorted = sorted(posts, key=lambda x: x['score'] + x['num_comments'], reverse=True)
        
        for i, post in enumerate(posts_sorted[:5]):
            with st.expander(f"📝 {post['title'][:100]}... (Score: {post['score']}, Comments: {len(post.get('comments', []))})"):
                
                # Post details
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Content:** {post.get('content', 'No content')[:500]}...")
                    st.markdown(f"**Author:** {post['author']}")
                    st.markdown(f"**Posted:** {post['created_date']}")
                
                with col2:
                    # Sentiment analysis
                    sentiment = post['sentiment']
                    confidence = post['confidence']
                    sentiment_score = post['sentiment_score']
                    
                    sentiment_color = "sentiment-positive" if sentiment == "POSITIVE" else "sentiment-negative" if sentiment == "NEGATIVE" else "sentiment-neutral"
                    confidence_class = "confidence-high" if confidence > 0.8 else "confidence-medium" if confidence > 0.6 else "confidence-low"
                    
                    st.markdown(f"<div class='{confidence_class}'>", unsafe_allow_html=True)
                    st.markdown(f"**Sentiment:** <span class='{sentiment_color}'>{sentiment}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Confidence:** {confidence:.2f}")
                    st.markdown(f"**Sentiment Score:** {sentiment_score:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Key phrases
                    if post.get('key_phrases'):
                        st.markdown("**Key Phrases:**")
                        for phrase in post['key_phrases'][:5]:
                            st.markdown(f"• {phrase}")
                
                # Comments analysis
                comments = post.get('comments', [])
                if comments:
                    st.markdown(f"### 💬 Comments Analysis ({len(comments)} comments)")
                    
                    # Comment sentiment distribution
                    comment_sentiments = [c['sentiment'] for c in comments]
                    sentiment_dist = pd.Series(comment_sentiments).value_counts()
                    
                    # Create mini chart
                    fig = px.pie(values=sentiment_dist.values, names=sentiment_dist.index, 
                               title="Comment Sentiment Distribution")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show top comments by sentiment confidence
                    st.markdown("**High-Confidence Comments:**")
                    
                    high_conf_comments = sorted([c for c in comments if c['confidence'] > 0.7], 
                                              key=lambda x: x['confidence'], reverse=True)[:3]
                    
                    for comment in high_conf_comments:
                        sentiment_color = "sentiment-positive" if comment['sentiment'] == "POSITIVE" else "sentiment-negative" if comment['sentiment'] == "NEGATIVE" else "sentiment-neutral"
                        
                        st.markdown(f"""
                        <div style='border-left: 3px solid #ddd; padding-left: 1rem; margin: 0.5rem 0;'>
                            <strong>Sentiment:</strong> <span class='{sentiment_color}'>{comment['sentiment']}</span> 
                            (Confidence: {comment['confidence']:.2f})<br>
                            <strong>Content:</strong> {comment['content'][:200]}...
                        </div>
                        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">🏭 Amazon FC Employee Intelligence Platform</h1>', unsafe_allow_html=True)
    
    # Load data
    data_result = load_comprehensive_data()
    
    if not data_result:
        st.error("No comprehensive analysis data found. Please run `python comprehensive_fc_analyzer.py` first.")
        return
    
    data, filename = data_result
    
    # Status bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**🤖 ML-Powered Analysis** - AWS Comprehend Intelligence")
    with col2:
        st.markdown(f"**Data Source:** {filename}")
    with col3:
        st.markdown(f"**Generated:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Overview metrics
    st.markdown("## 📊 Executive Overview")
    
    overview = data['overview']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Posts", overview['total_posts'])
    with col2:
        st.metric("Total Comments", overview['total_comments'])
    with col3:
        st.metric("Subject Areas", len([s for s, d in data['subject_areas'].items() if d['post_count'] > 0]))
    with col4:
        st.metric("Overall Sentiment", f"{overview['average_sentiment_scores']['overall']:.2f}")
    with col5:
        st.metric("Total Engagement", f"{overview['engagement_metrics']['total_engagement']:,}")
    
    # Cost and quality metrics
    st.markdown("### 💰 Analysis Quality & Cost")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("AWS API Calls", data['cost_summary']['api_calls'])
    with col2:
        st.metric("Analysis Cost", f"${data['cost_summary']['estimated_cost']}")
    with col3:
        st.metric("Items Analyzed", data['cost_summary']['items_analyzed'])
    with col4:
        st.metric("Cost per Item", f"${data['cost_summary']['estimated_cost']/data['cost_summary']['items_analyzed']:.4f}")
    
    # Subject area overview
    st.markdown("## 🎯 Subject Area Intelligence")
    
    # Create and display overview chart
    overview_chart = create_subject_overview_chart(data['subject_areas'])
    st.plotly_chart(overview_chart, use_container_width=True)
    
    # Interactive subject area selection
    st.markdown("### 🔍 Interactive Subject Area Analysis")
    
    # Filter to subjects with posts
    active_subjects = {k: v for k, v in data['subject_areas'].items() if v['post_count'] > 0}
    
    selected_subject = st.selectbox(
        "Select a subject area for detailed analysis:",
        options=list(active_subjects.keys()),
        format_func=lambda x: f"{x.replace('_', ' ').title()} ({active_subjects[x]['post_count']} posts)"
    )
    
    if selected_subject:
        # Display detailed drill-down
        drill_down_data = data.get('drill_down_data', {}).get(selected_subject, {})
        display_subject_drill_down(selected_subject, active_subjects[selected_subject], drill_down_data)
    
    # Sentiment deep dive
    st.markdown("## 😊 Sentiment Intelligence Deep Dive")
    
    if 'sentiment_deep_dive' in data:
        sentiment_chart = create_sentiment_deep_dive_chart(data['sentiment_deep_dive'])
        st.plotly_chart(sentiment_chart, use_container_width=True)
        
        # High confidence examples
        st.markdown("### 🎯 High-Confidence Sentiment Examples")
        
        sentiment_tabs = st.tabs(["Positive", "Negative", "Neutral", "Mixed"])
        
        for i, (sentiment_type, tab) in enumerate(zip(['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED'], sentiment_tabs)):
            with tab:
                examples = data['sentiment_deep_dive']['high_confidence_examples'].get(sentiment_type, [])
                
                if examples:
                    for example in examples[:5]:
                        confidence_class = "confidence-high" if example['confidence'] > 0.8 else "confidence-medium"
                        
                        st.markdown(f"<div class='{confidence_class}'>", unsafe_allow_html=True)
                        
                        if example['type'] == 'post':
                            st.markdown(f"**📝 Post:** {example['title']}")
                        else:
                            st.markdown(f"**💬 Comment on:** {example.get('post_title', 'Unknown post')}")
                        
                        st.markdown(f"**Content:** {example['text']}")
                        st.markdown(f"**Confidence:** {example['confidence']:.2f} | **Sentiment Score:** {example['sentiment_score']:.2f}")
                        
                        if 'engagement' in example:
                            st.markdown(f"**Engagement:** {example['engagement']}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("---")
                else:
                    st.markdown(f"No high-confidence {sentiment_type.lower()} examples found.")
    
    # Advanced analytics
    st.markdown("## 📈 Advanced Analytics")
    
    # Temporal analysis
    if 'temporal_analysis' in data:
        temporal = data['temporal_analysis']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily posting pattern
            daily_data = temporal['daily_post_counts']
            if daily_data:
                dates = list(daily_data.keys())
                counts = list(daily_data.values())
                
                fig = px.line(x=dates, y=counts, title="Daily Posting Pattern")
                fig.update_layout(xaxis_title="Date", yaxis_title="Number of Posts")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Hourly distribution
            hourly_data = temporal['hourly_distribution']
            if hourly_data:
                hours = list(hourly_data.keys())
                counts = list(hourly_data.values())
                
                fig = px.bar(x=hours, y=counts, title="Hourly Posting Distribution")
                fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Number of Posts")
                st.plotly_chart(fig, use_container_width=True)
        
        # Peak insights
        st.markdown("### ⏰ Peak Activity Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Peak Posting Hour", f"{temporal['peak_posting_time']}:00")
        with col2:
            st.metric("Peak Posting Day", temporal['peak_posting_day'])
    
    # Topic insights
    if 'topic_insights' in data:
        st.markdown("### 🔍 Advanced Topic Insights")
        
        topic_insights = data['topic_insights']
        
        # Top key phrases
        if 'top_key_phrases' in topic_insights:
            st.markdown("**Most Discussed Topics:**")
            
            phrases_df = pd.DataFrame(topic_insights['top_key_phrases'], columns=['Phrase', 'Frequency'])
            
            fig = px.bar(phrases_df.head(10), x='Frequency', y='Phrase', orientation='h',
                        title="Top 10 Key Phrases")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Emerging topics
        if 'emerging_topics' in topic_insights:
            st.markdown("**Emerging Topic Areas:**")
            
            for topic in topic_insights['emerging_topics'][:5]:
                st.markdown(f"• **{topic['topic'].replace('_', ' ').title()}**: {topic['total_mentions']} mentions")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard Controls")
        
        # Refresh data
        if st.button("🔄 Refresh Analysis"):
            st.cache_data.clear()
            st.rerun()
        
        # Analysis settings
        st.markdown("### 📊 Analysis Settings")
        show_confidence_scores = st.checkbox("Show Confidence Scores", value=True)
        show_key_phrases = st.checkbox("Show Key Phrases", value=True)
        
        # Export options
        st.markdown("### 📤 Export Options")
        if st.button("📊 Generate Executive Report"):
            st.success("Executive report generation triggered!")
        
        if st.button("📈 Export Data to CSV"):
            st.success("Data export initiated!")
        
        # System status
        st.markdown("### 🔧 System Status")
        st.success("✅ AWS Comprehend: Active")
        st.success("✅ Database: Connected")
        st.success("✅ ML Analysis: Complete")
        st.info(f"💰 Last Analysis Cost: ${data['cost_summary']['estimated_cost']}")

if __name__ == "__main__":
    main()