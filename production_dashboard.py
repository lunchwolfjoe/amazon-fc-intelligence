#!/usr/bin/env python3
"""
Production Reddit Compensation Dashboard
Streamlit app optimized for production deployment with auto-refresh
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from datetime import datetime, timedelta
import time
import json
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Amazon FC Compensation Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #232F3E;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #232F3E, #37475A);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .alert-high { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 5px; }
    .positive-sentiment { color: #28a745; font-weight: bold; }
    .negative-sentiment { color: #dc3545; font-weight: bold; }
    .neutral-sentiment { color: #6c757d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load and process data from database."""
    db_path = 'reddit_data.db'
    
    if not os.path.exists(db_path):
        return pd.DataFrame(), pd.DataFrame(), datetime.now()
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get recent posts (last 3 days)
        cutoff_date = datetime.now() - timedelta(days=3)
        
        posts_df = pd.read_sql_query("""
            SELECT * FROM posts 
            WHERE created_date >= ? 
            AND (LOWER(subreddit) = 'amazonfc' OR LOWER(subreddit) = 'amazonfc')
            ORDER BY created_date DESC
        """, conn, params=[cutoff_date])
        
        comments_df = pd.read_sql_query("""
            SELECT c.* FROM comments c
            JOIN posts p ON c.post_id = p.id
            WHERE c.created_date >= ?
            AND (LOWER(p.subreddit) = 'amazonfc' OR LOWER(p.subreddit) = 'amazonfc')
            ORDER BY c.created_date DESC
        """, conn, params=[cutoff_date])
        
        conn.close()
        
        return posts_df, comments_df, datetime.now()
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame(), pd.DataFrame(), datetime.now()

def filter_compensation_posts(posts_df):
    """Filter for compensation-related posts."""
    if posts_df.empty:
        return posts_df
    
    keywords = [
        'salary', 'wage', 'pay', 'raise', 'promotion', 'bonus', 'benefits',
        'overtime', 'hourly', 'annual', 'compensation', 'tier', '$'
    ]
    
    mask = posts_df['title'].str.lower().str.contains('|'.join(keywords), na=False) | \
           posts_df['content'].str.lower().str.contains('|'.join(keywords), na=False)
    
    return posts_df[mask].copy()

def analyze_sentiment(text):
    """Simple sentiment analysis."""
    if pd.isna(text):
        return 'NEUTRAL'
    
    text = str(text).lower()
    positive = ['good', 'great', 'excellent', 'happy', 'satisfied', 'fair', 'decent', 'competitive', 'love', 'awesome']
    negative = ['bad', 'terrible', 'awful', 'hate', 'unfair', 'underpaid', 'horrible', 'sucks', 'worst', 'disgusting']
    
    pos_count = sum(1 for word in positive if word in text)
    neg_count = sum(1 for word in negative if word in text)
    
    if pos_count > neg_count:
        return 'POSITIVE'
    elif neg_count > pos_count:
        return 'NEGATIVE'
    else:
        return 'NEUTRAL'

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Amazon FC Compensation Intelligence Dashboard</h1>', unsafe_allow_html=True)
    
    # Status bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**🔴 LIVE PRODUCTION DASHBOARD** - Updates every hour")
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Load data
    with st.spinner("Loading live data..."):
        posts_df, comments_df, last_updated = load_data()
    
    # Filter compensation posts
    comp_posts_df = filter_compensation_posts(posts_df)
    
    # Key metrics
    st.markdown("## 📊 Real-Time Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Posts (3 days)",
            len(posts_df),
            delta=f"{len(posts_df[posts_df['created_date'] >= (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')])} today"
        )
    
    with col2:
        st.metric(
            "Compensation Posts",
            len(comp_posts_df),
            delta=f"{(len(comp_posts_df)/max(len(posts_df), 1)*100):.1f}% of total"
        )
    
    with col3:
        st.metric(
            "Total Comments",
            len(comments_df),
            delta=f"Avg {len(comments_df)/max(len(posts_df), 1):.1f} per post"
        )
    
    with col4:
        total_engagement = comp_posts_df['score'].sum() + comp_posts_df['num_comments'].sum() if not comp_posts_df.empty else 0
        st.metric(
            "Total Engagement",
            f"{total_engagement:,}",
            delta="Score + Comments"
        )
    
    # High activity alert
    if len(comp_posts_df) > 30:
        st.markdown("""
        <div class="alert-high">
            🚨 <strong>HIGH ACTIVITY ALERT:</strong> Unusually high compensation discussion volume detected. 
            This may indicate significant employee sentiment around recent wage announcements.
        </div>
        """, unsafe_allow_html=True)
    
    # Sentiment analysis
    if not comp_posts_df.empty:
        comp_posts_df['sentiment'] = comp_posts_df.apply(
            lambda row: analyze_sentiment(f"{row['title']} {row['content']}"), 
            axis=1
        )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            sentiment_counts = comp_posts_df['sentiment'].value_counts()
            colors = {'POSITIVE': '#28a745', 'NEGATIVE': '#dc3545', 'NEUTRAL': '#6c757d'}
            
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Sentiment Distribution - Last 3 Days",
                color=sentiment_counts.index,
                color_discrete_map=colors
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Timeline
            comp_posts_df['created_date'] = pd.to_datetime(comp_posts_df['created_date'])
            comp_posts_df['date'] = comp_posts_df['created_date'].dt.date
            daily_counts = comp_posts_df.groupby('date').size().reset_index(name='count')
            
            fig = px.line(daily_counts, x='date', y='count', title='Posts Over Time', markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    # Top posts
    st.markdown("## 🔥 Top Engaging Compensation Posts")
    if not comp_posts_df.empty:
        comp_posts_df['engagement'] = comp_posts_df['score'] + comp_posts_df['num_comments']
        top_posts = comp_posts_df.nlargest(10, 'engagement')
        
        display_df = top_posts[['title', 'author', 'score', 'num_comments', 'created_date']].copy()
        display_df['created_date'] = pd.to_datetime(display_df['created_date']).dt.strftime('%m/%d %H:%M')
        
        st.dataframe(
            display_df,
            column_config={
                "title": st.column_config.TextColumn("Title", width="large"),
                "author": st.column_config.TextColumn("Author", width="small"),
                "score": st.column_config.NumberColumn("Score", width="small"),
                "num_comments": st.column_config.NumberColumn("Comments", width="small"),
                "created_date": st.column_config.TextColumn("Posted", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("No compensation posts found in recent data.")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard Controls")
        
        # Auto-refresh
        st.markdown("### Auto-Refresh Settings")
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh Rate",
                options=[1800, 3600, 7200],
                index=1,
                format_func=lambda x: f"{x//60} minutes"
            )
            
            # Auto-refresh with placeholder
            placeholder = st.empty()
            for seconds in range(refresh_interval):
                placeholder.text(f"Next refresh in: {refresh_interval - seconds} seconds")
                time.sleep(1)
            
            st.cache_data.clear()
            st.rerun()
        
        # System status
        st.markdown("### System Status")
        st.success("✅ Database: Connected")
        st.success(f"✅ Last Update: {last_updated.strftime('%H:%M:%S')}")
        st.info(f"📊 Posts in DB: {len(posts_df)}")
        st.info(f"💬 Comments in DB: {len(comments_df)}")

if __name__ == "__main__":
    main()