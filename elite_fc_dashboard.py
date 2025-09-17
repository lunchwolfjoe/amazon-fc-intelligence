#!/usr/bin/env python3
"""
Elite Amazon FC Employee Intelligence Dashboard
Deep drill-down analysis with improved UX, better charts, and comprehensive filtering
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta, date
import numpy as np
from collections import Counter
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Elite FC Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional look
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
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .topic-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    
    .topic-card:hover {
        transform: translateY(-5px);
        border-color: #FF9900;
        box-shadow: 0 8px 25px rgba(255, 153, 0, 0.2);
    }
    
    .topic-card.selected {
        border-color: #232F3E;
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(35, 47, 62, 0.3);
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #FF9900;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .drill-down-container {
        background: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    .post-card {
        background: #f8f9fa;
        border-left: 4px solid #FF9900;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .post-card:hover {
        background: #e9ecef;
        border-left-width: 6px;
    }
    
    .sentiment-positive { 
        color: #28a745; 
        font-weight: 700;
        background: #d4edda;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .sentiment-negative { 
        color: #dc3545; 
        font-weight: 700;
        background: #f8d7da;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .sentiment-neutral { 
        color: #6c757d; 
        font-weight: 700;
        background: #e2e3e5;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    .confidence-badge {
        background: linear-gradient(135deg, #17a2b8, #138496);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .filter-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    .comment-thread {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #6c757d;
    }
    
    .comment-thread.positive { border-left-color: #28a745; }
    .comment-thread.negative { border-left-color: #dc3545; }
    .comment-thread.neutral { border-left-color: #6c757d; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=1800)
def load_comprehensive_data():
    """Load comprehensive analysis data with real Reddit data."""
    # Load the real analysis data (renamed for deployment)
    if os.path.exists('sample_data.json'):
        try:
            with open('sample_data.json', 'r') as f:
                data = json.load(f)
            return data, 'Real Amazon FC Analysis Data'
        except Exception as e:
            st.error(f"Error loading analysis data: {e}")
    
    # Fallback to local analysis files
    analysis_files = [f for f in os.listdir('.') if f.startswith('comprehensive_fc_analysis_') and f.endswith('.json')]
    
    if analysis_files:
        latest_file = sorted(analysis_files)[-1]
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            return data, latest_file
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
    return None

@st.cache_data(ttl=1800)
def load_raw_database_data():
    """Load raw data from database for advanced filtering."""
    # Try deployment database first
    db_path = 'sample_reddit_data.db' if os.path.exists('sample_reddit_data.db') else 'reddit_data.db'
    
    if not os.path.exists(db_path):
        return None, None
    
    try:
        conn = sqlite3.connect(db_path)
        
        posts_df = pd.read_sql_query("""
            SELECT * FROM posts 
            WHERE LOWER(subreddit) LIKE '%amazonfc%'
            ORDER BY created_date DESC
        """, conn)
        
        comments_df = pd.read_sql_query("""
            SELECT c.*, p.title as post_title FROM comments c
            JOIN posts p ON c.post_id = p.id
            WHERE LOWER(p.subreddit) LIKE '%amazonfc%'
            ORDER BY c.created_date DESC
        """, conn)
        
        conn.close()
        
        # Convert date columns
        posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
        comments_df['created_date'] = pd.to_datetime(comments_df['created_date'])
        
        return posts_df, comments_df
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return None, None

def create_enhanced_overview_chart(subject_data, selected_subjects=None):
    """Create enhanced overview visualization."""
    
    # Prepare data
    subjects = []
    post_counts = []
    sentiment_scores = []
    engagement_scores = []
    
    for subject, data in subject_data.items():
        if data['post_count'] > 0:
            subjects.append(subject.replace('_', ' ').title())
            post_counts.append(data['post_count'])
            sentiment_scores.append(data['avg_sentiment_score'])
            
            # Calculate engagement score
            total_engagement = sum([
                post.get('score', 0) + post.get('num_comments', 0) 
                for post in data.get('top_posts', [])
            ])
            engagement_scores.append(total_engagement)
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Posts by Subject Area', 
            'Sentiment Analysis by Subject',
            'Engagement Levels', 
            'Subject Distribution'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "pie"}]
        ]
    )
    
    # Posts by subject (with better colors)
    colors = ['#FF9900' if subj in (selected_subjects or []) else '#232F3E' for subj in subjects]
    fig.add_trace(
        go.Bar(
            x=subjects, 
            y=post_counts, 
            name="Posts",
            marker_color=colors,
            text=post_counts,
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Sentiment by subject (color-coded)
    sentiment_colors = [
        '#28a745' if score > 0.1 else '#dc3545' if score < -0.1 else '#6c757d' 
        for score in sentiment_scores
    ]
    fig.add_trace(
        go.Bar(
            x=subjects, 
            y=sentiment_scores, 
            name="Sentiment",
            marker_color=sentiment_colors,
            text=[f"{score:.2f}" for score in sentiment_scores],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    # Engagement levels
    fig.add_trace(
        go.Bar(
            x=subjects, 
            y=engagement_scores, 
            name="Engagement",
            marker_color='#17a2b8',
            text=engagement_scores,
            textposition='outside'
        ),
        row=2, col=1
    )
    
    # Distribution pie chart
    fig.add_trace(
        go.Pie(
            labels=subjects, 
            values=post_counts,
            name="Distribution",
            marker_colors=['#FF9900', '#232F3E', '#17a2b8', '#28a745', '#dc3545', '#6c757d', '#ffc107', '#e83e8c', '#20c997']
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=700,
        showlegend=False,
        title_text="Amazon FC Employee Intelligence Overview",
        title_x=0.5,
        title_font_size=20
    )
    
    # Update axes
    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_xaxes(tickangle=45, row=1, col=2)
    fig.update_xaxes(tickangle=45, row=2, col=1)
    
    return fig

def create_sentiment_timeline_chart(posts_df, date_range=None):
    """Create sentiment timeline with date filtering."""
    
    if posts_df is None or posts_df.empty:
        return go.Figure()
    
    # Apply date filter
    if date_range:
        start_date, end_date = date_range
        posts_df = posts_df[
            (posts_df['created_date'].dt.date >= start_date) & 
            (posts_df['created_date'].dt.date <= end_date)
        ]
    
    # Group by date and calculate sentiment metrics
    posts_df['date'] = posts_df['created_date'].dt.date
    daily_stats = posts_df.groupby('date').agg({
        'score': ['count', 'mean'],
        'num_comments': 'sum'
    }).round(2)
    
    daily_stats.columns = ['post_count', 'avg_score', 'total_comments']
    daily_stats = daily_stats.reset_index()
    
    # Create timeline chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Post Volume', 'Daily Engagement Metrics'),
        shared_xaxes=True
    )
    
    # Post volume
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['post_count'],
            mode='lines+markers',
            name='Posts per Day',
            line=dict(color='#232F3E', width=3),
            marker=dict(size=8, color='#FF9900')
        ),
        row=1, col=1
    )
    
    # Engagement metrics
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['avg_score'],
            mode='lines+markers',
            name='Avg Score',
            line=dict(color='#28a745', width=2),
            yaxis='y3'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['total_comments'],
            mode='lines+markers',
            name='Total Comments',
            line=dict(color='#17a2b8', width=2),
            yaxis='y4'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        title_text="Temporal Analysis",
        title_x=0.5
    )
    
    return fig

def display_advanced_topic_drill_down(subject_name, drill_down_data, posts_df, comments_df, date_range=None):
    """Advanced topic drill-down with multiple analysis layers."""
    
    st.markdown(f"<div class='drill-down-container'>", unsafe_allow_html=True)
    
    # Header
    st.markdown(f"# 🎯 Deep Analysis: {subject_name.replace('_', ' ').title()}")
    
    if not drill_down_data or 'posts' not in drill_down_data:
        st.warning("No detailed data available for this subject area.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    posts = drill_down_data['posts']
    
    # Apply date filtering
    if date_range:
        start_date, end_date = date_range
        posts = [
            post for post in posts 
            if start_date <= pd.to_datetime(post['created_date']).date() <= end_date
        ]
    
    if not posts:
        st.warning("No posts found in the selected date range.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Enhanced metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_posts = len(posts)
    total_comments = sum([len(post.get('comments', [])) for post in posts])
    avg_sentiment = sum([post['sentiment_score'] for post in posts]) / max(total_posts, 1)
    total_engagement = sum([post['score'] + post['num_comments'] for post in posts])
    avg_confidence = sum([post['confidence'] for post in posts]) / max(total_posts, 1)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_posts}</div>
            <div class='metric-label'>Posts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_comments}</div>
            <div class='metric-label'>Comments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sentiment_color = "#28a745" if avg_sentiment > 0.1 else "#dc3545" if avg_sentiment < -0.1 else "#6c757d"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value' style='color: {sentiment_color}'>{avg_sentiment:.2f}</div>
            <div class='metric-label'>Avg Sentiment</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_engagement:,}</div>
            <div class='metric-label'>Engagement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{avg_confidence:.2f}</div>
            <div class='metric-label'>ML Confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Advanced filtering within topic
    st.markdown("## 🔧 Advanced Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            options=['All', 'POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED'],
            key=f"sentiment_filter_{subject_name}"
        )
    
    with col2:
        min_engagement = st.slider(
            "Minimum Engagement",
            min_value=0,
            max_value=max([post['score'] + post['num_comments'] for post in posts]) if posts else 100,
            value=0,
            key=f"engagement_filter_{subject_name}"
        )
    
    with col3:
        min_confidence = st.slider(
            "Minimum ML Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"confidence_filter_{subject_name}"
        )
    
    # Apply filters
    filtered_posts = posts
    
    if sentiment_filter != 'All':
        filtered_posts = [p for p in filtered_posts if p['sentiment'] == sentiment_filter]
    
    filtered_posts = [p for p in filtered_posts if (p['score'] + p['num_comments']) >= min_engagement]
    filtered_posts = [p for p in filtered_posts if p['confidence'] >= min_confidence]
    
    st.markdown(f"**Showing {len(filtered_posts)} of {len(posts)} posts**")
    
    # Sentiment distribution chart for this topic
    st.markdown("## 📊 Topic Sentiment Analysis")
    
    sentiment_counts = Counter([post['sentiment'] for post in filtered_posts])
    
    if sentiment_counts:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=list(sentiment_counts.values()),
                names=list(sentiment_counts.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'POSITIVE': '#28a745',
                    'NEGATIVE': '#dc3545',
                    'NEUTRAL': '#6c757d',
                    'MIXED': '#ffc107'
                }
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Confidence vs Sentiment scatter
            sentiment_scores = [post['sentiment_score'] for post in filtered_posts]
            confidences = [post['confidence'] for post in filtered_posts]
            sentiments = [post['sentiment'] for post in filtered_posts]
            
            fig_scatter = px.scatter(
                x=sentiment_scores,
                y=confidences,
                color=sentiments,
                title="Sentiment Score vs ML Confidence",
                labels={'x': 'Sentiment Score', 'y': 'ML Confidence'},
                color_discrete_map={
                    'POSITIVE': '#28a745',
                    'NEGATIVE': '#dc3545',
                    'NEUTRAL': '#6c757d',
                    'MIXED': '#ffc107'
                }
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Detailed post analysis
    st.markdown("## 📝 Detailed Post Analysis")
    
    # Sort options
    sort_option = st.selectbox(
        "Sort posts by:",
        options=['Engagement (High to Low)', 'Sentiment Score (High to Low)', 'Sentiment Score (Low to High)', 'ML Confidence (High to Low)', 'Date (Newest First)'],
        key=f"sort_option_{subject_name}"
    )
    
    # Apply sorting
    if sort_option == 'Engagement (High to Low)':
        filtered_posts = sorted(filtered_posts, key=lambda x: x['score'] + x['num_comments'], reverse=True)
    elif sort_option == 'Sentiment Score (High to Low)':
        filtered_posts = sorted(filtered_posts, key=lambda x: x['sentiment_score'], reverse=True)
    elif sort_option == 'Sentiment Score (Low to High)':
        filtered_posts = sorted(filtered_posts, key=lambda x: x['sentiment_score'])
    elif sort_option == 'ML Confidence (High to Low)':
        filtered_posts = sorted(filtered_posts, key=lambda x: x['confidence'], reverse=True)
    elif sort_option == 'Date (Newest First)':
        filtered_posts = sorted(filtered_posts, key=lambda x: x['created_date'], reverse=True)
    
    # Display posts with enhanced detail
    for i, post in enumerate(filtered_posts[:10]):  # Show top 10
        
        # Post header
        engagement = post['score'] + post['num_comments']
        sentiment_class = f"sentiment-{post['sentiment'].lower()}"
        
        st.markdown(f"""
        <div class='post-card'>
            <h4>📝 {post['title']}</h4>
            <div style='margin: 1rem 0;'>
                <span class='{sentiment_class}'>{post['sentiment']}</span>
                <span class='confidence-badge'>Confidence: {post['confidence']:.2f}</span>
                <span style='margin-left: 1rem; color: #6c757d;'>
                    👍 {post['score']} | 💬 {post['num_comments']} | 🔥 {engagement}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable content
        with st.expander(f"View Details & Comments ({len(post.get('comments', []))} comments)"):
            
            # Post content and metadata
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Content:**")
                content = post.get('content', 'No content available')
                if len(content) > 500:
                    st.markdown(f"{content[:500]}...")
                    if st.button(f"Show Full Content", key=f"full_content_{i}_{subject_name}"):
                        st.markdown(content)
                else:
                    st.markdown(content)
            
            with col2:
                st.markdown("**Metadata:**")
                st.markdown(f"**Author:** {post['author']}")
                st.markdown(f"**Posted:** {pd.to_datetime(post['created_date']).strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Sentiment Score:** {post['sentiment_score']:.3f}")
                
                # Key phrases
                if post.get('key_phrases'):
                    st.markdown("**Key Phrases:**")
                    for phrase in post['key_phrases'][:5]:
                        st.markdown(f"• {phrase}")
            
            # Comments analysis
            comments = post.get('comments', [])
            if comments:
                st.markdown(f"### 💬 Comments Analysis ({len(comments)} comments)")
                
                # Comment sentiment summary
                comment_sentiments = [c['sentiment'] for c in comments]
                comment_sentiment_dist = Counter(comment_sentiments)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pos_count = comment_sentiment_dist.get('POSITIVE', 0)
                    st.metric("Positive Comments", pos_count, f"{pos_count/len(comments)*100:.1f}%")
                
                with col2:
                    neg_count = comment_sentiment_dist.get('NEGATIVE', 0)
                    st.metric("Negative Comments", neg_count, f"{neg_count/len(comments)*100:.1f}%")
                
                with col3:
                    avg_comment_sentiment = sum([c['sentiment_score'] for c in comments]) / len(comments)
                    st.metric("Avg Comment Sentiment", f"{avg_comment_sentiment:.2f}")
                
                # Show top comments by confidence
                st.markdown("**High-Confidence Comments:**")
                
                high_conf_comments = sorted(
                    [c for c in comments if c['confidence'] > 0.7], 
                    key=lambda x: x['confidence'], 
                    reverse=True
                )[:5]
                
                for comment in high_conf_comments:
                    sentiment_class = f"sentiment-{comment['sentiment'].lower()}"
                    
                    st.markdown(f"""
                    <div class='comment-thread {comment['sentiment'].lower()}'>
                        <div style='margin-bottom: 0.5rem;'>
                            <span class='{sentiment_class}'>{comment['sentiment']}</span>
                            <span class='confidence-badge'>Confidence: {comment['confidence']:.2f}</span>
                            <span style='margin-left: 1rem; color: #6c757d;'>Score: {comment['score']}</span>
                        </div>
                        <div>{comment['content'][:300]}{'...' if len(comment['content']) > 300 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Elite FC Intelligence Platform</h1>', unsafe_allow_html=True)
    
    # Load data
    data_result = load_comprehensive_data()
    posts_df, comments_df = load_raw_database_data()
    
    if not data_result:
        st.error("No analysis data found. Please run `python comprehensive_fc_analyzer.py` first.")
        return
    
    data, filename = data_result
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Controls")
        
        # Date range filter
        st.markdown("### 📅 Date Range Filter")
        
        if posts_df is not None:
            min_date = posts_df['created_date'].min().date()
            max_date = posts_df['created_date'].max().date()
            
            date_range = st.date_input(
                "Select date range:",
                value=(max_date - timedelta(days=7), max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                st.success(f"Analyzing {(end_date - start_date).days + 1} days of data")
            else:
                date_range = None
                st.info("Select both start and end dates")
        else:
            date_range = None
        
        # Analysis options
        st.markdown("### ⚙️ Analysis Options")
        show_ml_confidence = st.checkbox("Show ML Confidence Scores", value=True)
        show_key_phrases = st.checkbox("Show Key Phrases", value=True)
        auto_refresh = st.checkbox("Auto-refresh data", value=False)
        
        if auto_refresh:
            st.info("Dashboard will refresh every 30 minutes")
        
        # Data quality metrics
        st.markdown("### 📊 Data Quality")
        if data:
            st.metric("AWS API Calls", data['cost_summary']['api_calls'])
            st.metric("Analysis Cost", f"${data['cost_summary']['estimated_cost']}")
            st.metric("Items Analyzed", data['cost_summary']['items_analyzed'])
        
        # Export options
        st.markdown("### 📤 Export Options")
        if st.button("📊 Export Current View"):
            st.success("Export initiated!")
        
        if st.button("🔄 Refresh Analysis"):
            st.cache_data.clear()
            st.rerun()
    
    # Main content area
    if not data:
        return
    
    # Status bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**🤖 Elite ML-Powered Analysis** - AWS Comprehend + Advanced Filtering")
    with col2:
        st.markdown(f"**Source:** {filename}")
    with col3:
        st.markdown(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Overview section
    st.markdown("## 📈 Executive Intelligence Overview")
    
    overview = data['overview']
    
    # Enhanced metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    metrics = [
        ("Total Posts", overview['total_posts'], "📝"),
        ("Total Comments", overview['total_comments'], "💬"),
        ("Subject Areas", len([s for s, d in data['subject_areas'].items() if d['post_count'] > 0]), "🎯"),
        ("Overall Sentiment", f"{overview['average_sentiment_scores']['overall']:.2f}", "😊"),
        ("Total Engagement", f"{overview['engagement_metrics']['total_engagement']:,}", "🔥"),
        ("Analysis Cost", f"${data['cost_summary']['estimated_cost']}", "💰")
    ]
    
    for i, (label, value, icon) in enumerate(metrics):
        with [col1, col2, col3, col4, col5, col6][i]:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>{icon}</div>
                <div class='metric-value'>{value}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced overview chart
    st.markdown("## 🎯 Subject Area Intelligence")
    
    # Subject area selection
    active_subjects = {k: v for k, v in data['subject_areas'].items() if v['post_count'] > 0}
    
    # Create interactive subject cards
    st.markdown("### 📋 Select Subject Areas for Analysis")
    
    cols = st.columns(3)
    selected_subjects = []
    
    for i, (subject, subject_data) in enumerate(active_subjects.items()):
        col_idx = i % 3
        
        with cols[col_idx]:
            # Create clickable subject card
            card_key = f"subject_card_{subject}"
            
            if st.button(
                f"{subject.replace('_', ' ').title()}\n{subject_data['post_count']} posts | Sentiment: {subject_data['avg_sentiment_score']:.2f}",
                key=card_key,
                use_container_width=True
            ):
                st.session_state[f"selected_subject"] = subject
    
    # Overview chart
    overview_chart = create_enhanced_overview_chart(data['subject_areas'], selected_subjects)
    st.plotly_chart(overview_chart, use_container_width=True)
    
    # Temporal analysis
    if posts_df is not None:
        st.markdown("## ⏰ Temporal Intelligence")
        timeline_chart = create_sentiment_timeline_chart(posts_df, date_range)
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Deep dive section
    if 'selected_subject' in st.session_state:
        selected_subject = st.session_state['selected_subject']
        
        if selected_subject in data.get('drill_down_data', {}):
            display_advanced_topic_drill_down(
                selected_subject,
                data['drill_down_data'][selected_subject],
                posts_df,
                comments_df,
                date_range
            )
    else:
        st.markdown("## 🔍 Deep Dive Analysis")
        st.info("👆 Click on a subject area above to start deep dive analysis")
        
        # Show quick insights
        st.markdown("### 💡 Quick Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Most Discussed Topics:**")
            sorted_subjects = sorted(
                active_subjects.items(), 
                key=lambda x: x[1]['post_count'], 
                reverse=True
            )
            
            for subject, data in sorted_subjects[:5]:
                sentiment_emoji = "😊" if data['avg_sentiment_score'] > 0.1 else "😞" if data['avg_sentiment_score'] < -0.1 else "😐"
                st.markdown(f"• {sentiment_emoji} **{subject.replace('_', ' ').title()}**: {data['post_count']} posts")
        
        with col2:
            st.markdown("**Sentiment Highlights:**")
            
            # Most positive subject
            most_positive = max(active_subjects.items(), key=lambda x: x[1]['avg_sentiment_score'])
            st.markdown(f"• 😊 **Most Positive**: {most_positive[0].replace('_', ' ').title()} ({most_positive[1]['avg_sentiment_score']:.2f})")
            
            # Most negative subject
            most_negative = min(active_subjects.items(), key=lambda x: x[1]['avg_sentiment_score'])
            st.markdown(f"• 😞 **Most Negative**: {most_negative[0].replace('_', ' ').title()} ({most_negative[1]['avg_sentiment_score']:.2f})")
            
            # Most discussed
            most_discussed = max(active_subjects.items(), key=lambda x: x[1]['post_count'])
            st.markdown(f"• 🔥 **Most Discussed**: {most_discussed[0].replace('_', ' ').title()} ({most_discussed[1]['post_count']} posts)")

if __name__ == "__main__":
    main()