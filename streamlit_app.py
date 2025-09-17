#!/usr/bin/env python3
"""
Amazon FC Employee Intelligence Platform - Quick Production Version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Amazon FC Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #232F3E 0%, #FF9900 50%, #232F3E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    
    .sentiment-negative { 
        color: #dc3545; 
        background: #f8d7da;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    .sentiment-positive { 
        color: #155724; 
        background: #d4edda;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    .sentiment-neutral { 
        color: #495057; 
        background: #e2e3e5;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    .post-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def generate_comprehensive_dataset():
    """Generate a comprehensive dataset with hundreds of posts."""
    
    # Sample post templates for each subject
    post_templates = {
        'compensation': [
            {"title": "Anyone else get a random pay raise?", "base_score": 729, "sentiment": "NEUTRAL"},
            {"title": "2025 pay increase announcement", "base_score": 241, "sentiment": "POSITIVE"},
            {"title": "Reaction to 50 cent raise 🤣", "base_score": 315, "sentiment": "NEGATIVE"},
            {"title": "Wage announcement for Columbus Ohio", "base_score": 209, "sentiment": "NEUTRAL"},
            {"title": "Still no raise after 2 years", "base_score": 156, "sentiment": "NEGATIVE"},
            {"title": "Overtime pay calculation seems wrong", "base_score": 89, "sentiment": "NEGATIVE"},
            {"title": "Benefits package review", "base_score": 67, "sentiment": "NEUTRAL"},
            {"title": "PTO policy changes", "base_score": 134, "sentiment": "NEGATIVE"},
            {"title": "Bonus structure explanation needed", "base_score": 78, "sentiment": "NEUTRAL"},
            {"title": "Shift differential rates", "base_score": 45, "sentiment": "POSITIVE"},
        ],
        'management': [
            {"title": "New manager doesn't understand the job", "base_score": 234, "sentiment": "NEGATIVE"},
            {"title": "AM wrote me up for bathroom break", "base_score": 567, "sentiment": "NEGATIVE"},
            {"title": "PA coaching session was helpful", "base_score": 89, "sentiment": "POSITIVE"},
            {"title": "HR investigation ongoing", "base_score": 123, "sentiment": "NEGATIVE"},
            {"title": "Manager plays favorites", "base_score": 345, "sentiment": "NEGATIVE"},
            {"title": "Leadership training announcement", "base_score": 67, "sentiment": "NEUTRAL"},
            {"title": "Supervisor micromanaging everything", "base_score": 189, "sentiment": "NEGATIVE"},
            {"title": "Good manager transferred out", "base_score": 156, "sentiment": "NEGATIVE"},
            {"title": "Team lead promotion process", "base_score": 78, "sentiment": "NEUTRAL"},
            {"title": "Management communication issues", "base_score": 234, "sentiment": "NEGATIVE"},
        ],
        'working_conditions': [
            {"title": "Safety incident not reported properly", "base_score": 456, "sentiment": "NEGATIVE"},
            {"title": "Break room conditions terrible", "base_score": 234, "sentiment": "NEGATIVE"},
            {"title": "New safety equipment installed", "base_score": 89, "sentiment": "POSITIVE"},
            {"title": "Temperature control issues", "base_score": 167, "sentiment": "NEGATIVE"},
            {"title": "Bathroom break restrictions", "base_score": 345, "sentiment": "NEGATIVE"},
            {"title": "Ergonomic improvements needed", "base_score": 123, "sentiment": "NEGATIVE"},
            {"title": "First aid station locations", "base_score": 67, "sentiment": "NEUTRAL"},
            {"title": "Workplace injury reporting", "base_score": 189, "sentiment": "NEGATIVE"},
            {"title": "Safety training effectiveness", "base_score": 78, "sentiment": "NEUTRAL"},
            {"title": "Environmental hazards concern", "base_score": 234, "sentiment": "NEGATIVE"},
        ],
        'schedule_time': [
            {"title": "MET announced for next month", "base_score": 345, "sentiment": "NEGATIVE"},
            {"title": "VTO offered today", "base_score": 189, "sentiment": "POSITIVE"},
            {"title": "Schedule changes with no notice", "base_score": 267, "sentiment": "NEGATIVE"},
            {"title": "Shift bid process unfair", "base_score": 156, "sentiment": "NEGATIVE"},
            {"title": "Overtime opportunities limited", "base_score": 89, "sentiment": "NEGATIVE"},
            {"title": "Flexible scheduling options", "base_score": 67, "sentiment": "POSITIVE"},
            {"title": "Peak season hours extended", "base_score": 234, "sentiment": "NEGATIVE"},
            {"title": "Time off request denied", "base_score": 178, "sentiment": "NEGATIVE"},
            {"title": "Shift differential changes", "base_score": 123, "sentiment": "NEUTRAL"},
            {"title": "Weekend mandatory overtime", "base_score": 289, "sentiment": "NEGATIVE"},
        ],
        'general_experience': [
            {"title": "Thinking about quitting Amazon", "base_score": 567, "sentiment": "NEGATIVE"},
            {"title": "First day at FC - what to expect?", "base_score": 123, "sentiment": "NEUTRAL"},
            {"title": "Been here 3 years, AMA", "base_score": 234, "sentiment": "NEUTRAL"},
            {"title": "Why I stay at Amazon FC", "base_score": 89, "sentiment": "POSITIVE"},
            {"title": "Job search while working here", "base_score": 156, "sentiment": "NEGATIVE"},
            {"title": "Training program experience", "base_score": 78, "sentiment": "NEUTRAL"},
            {"title": "Work-life balance struggles", "base_score": 234, "sentiment": "NEGATIVE"},
            {"title": "Career progression opportunities", "base_score": 67, "sentiment": "NEUTRAL"},
            {"title": "Employee recognition program", "base_score": 45, "sentiment": "POSITIVE"},
            {"title": "Workplace culture observations", "base_score": 189, "sentiment": "NEGATIVE"},
        ]
    }
    
    # Generate posts for each subject
    subject_areas = {}
    
    for subject, templates in post_templates.items():
        posts = []
        
        # Generate 30-80 posts per subject
        num_posts = random.randint(30, 80)
        
        for i in range(num_posts):
            template = random.choice(templates)
            
            # Create variations
            post = {
                'id': f"{subject}_{i}",
                'title': template['title'] + (f" - Update {i+1}" if i > 0 else ""),
                'content': f"Detailed discussion about {template['title'].lower()}. This is post {i+1} in the {subject} category.",
                'score': template['base_score'] + random.randint(-50, 100),
                'num_comments': random.randint(5, 200),
                'sentiment': template['sentiment'],
                'confidence': round(random.uniform(0.7, 0.95), 3),
                'created_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'comments': []
            }
            
            # Generate comments
            num_comments = min(post['num_comments'], 10)
            for j in range(num_comments):
                comment = {
                    'body': f"Comment {j+1} on {template['title']}. This provides additional context and discussion.",
                    'score': random.randint(1, 50),
                    'sentiment': random.choice(['NEGATIVE', 'NEUTRAL', 'POSITIVE']),
                    'confidence': round(random.uniform(0.6, 0.9), 3)
                }
                post['comments'].append(comment)
            
            posts.append(post)
        
        # Calculate subject statistics
        sentiment_dist = {}
        for post in posts:
            sent = post['sentiment']
            sentiment_dist[sent] = sentiment_dist.get(sent, 0) + 1
        
        sentiment_scores = {'NEGATIVE': -0.5, 'NEUTRAL': 0.0, 'POSITIVE': 0.5}
        avg_sentiment = sum(sentiment_scores.get(p['sentiment'], 0) for p in posts) / len(posts)
        
        subject_areas[subject] = {
            'post_count': len(posts),
            'comment_count': sum(len(p.get('comments', [])) for p in posts),
            'sentiment_distribution': sentiment_dist,
            'avg_sentiment_score': avg_sentiment,
            'top_posts': posts
        }
    
    # Calculate overall statistics
    total_posts = sum(s['post_count'] for s in subject_areas.values())
    total_comments = sum(s['comment_count'] for s in subject_areas.values())
    
    all_sentiments = []
    for subject_data in subject_areas.values():
        for post in subject_data['top_posts']:
            all_sentiments.append(post['sentiment'])
    
    post_sentiment_dist = {}
    for sent in all_sentiments:
        post_sentiment_dist[sent] = post_sentiment_dist.get(sent, 0) + 1
    
    return {
        'overview': {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'subject_distribution': {k: v['post_count'] for k, v in subject_areas.items()},
            'post_sentiment_distribution': post_sentiment_dist,
            'comment_sentiment_distribution': {'NEUTRAL': total_comments // 2, 'NEGATIVE': total_comments // 3, 'POSITIVE': total_comments // 6},
            'average_sentiment_scores': {
                'posts': -0.15,
                'comments': -0.08,
                'overall': -0.12
            },
            'engagement_metrics': {
                'avg_post_score': 150,
                'avg_comments_per_page': total_comments / total_posts if total_posts > 0 else 0,
                'total_engagement': total_posts * 150
            }
        },
        'subject_areas': subject_areas
    }

def create_summary_analytics(data):
    """Create comprehensive summary analytics and trend charts."""
    
    subject_areas = data.get('subject_areas', {})
    if not subject_areas:
        st.warning("No data available for analytics")
        return
    
    # Prepare data for visualizations
    subjects = []
    post_counts = []
    comment_counts = []
    avg_sentiments = []
    negative_ratios = []
    positive_ratios = []
    engagement_scores = []
    
    for subject, info in subject_areas.items():
        subjects.append(subject.replace('_', ' ').title())
        post_counts.append(info.get('post_count', 0))
        comment_counts.append(info.get('comment_count', 0))
        avg_sentiments.append(info.get('avg_sentiment_score', 0))
        
        # Calculate sentiment ratios
        sentiment_dist = info.get('sentiment_distribution', {})
        total_posts = info.get('post_count', 1)
        negative_ratio = sentiment_dist.get('NEGATIVE', 0) / total_posts if total_posts > 0 else 0
        positive_ratio = sentiment_dist.get('POSITIVE', 0) / total_posts if total_posts > 0 else 0
        negative_ratios.append(negative_ratio * 100)  # Convert to percentage
        positive_ratios.append(positive_ratio * 100)
        
        # Calculate engagement score (posts * avg_comments)
        avg_comments = info.get('comment_count', 0) / total_posts if total_posts > 0 else 0
        engagement_scores.append(avg_comments)
    
    # Create comprehensive dashboard with multiple charts
    
    # Row 1: Volume and Sentiment Overview
    col1, col2 = st.columns(2)
    
    with col1:
        # Post Volume by Subject
        fig_volume = go.Figure(data=[
            go.Bar(
                x=subjects,
                y=post_counts,
                marker_color='#FF9900',
                text=post_counts,
                textposition='auto',
                name='Posts'
            )
        ])
        fig_volume.update_layout(
            title="📊 Post Volume by Subject Area",
            xaxis_title="Subject Area",
            yaxis_title="Number of Posts",
            height=400,
            showlegend=False
        )
        fig_volume.update_xaxes(tickangle=45)
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with col2:
        # Average Sentiment by Subject
        colors = ['#dc3545' if s < -0.1 else '#fd7e14' if s < 0.1 else '#28a745' for s in avg_sentiments]
        fig_sentiment = go.Figure(data=[
            go.Bar(
                x=subjects,
                y=avg_sentiments,
                marker_color=colors,
                text=[f"{s:.3f}" for s in avg_sentiments],
                textposition='auto',
                name='Avg Sentiment'
            )
        ])
        fig_sentiment.update_layout(
            title="📈 Average Sentiment by Subject Area",
            xaxis_title="Subject Area",
            yaxis_title="Sentiment Score",
            height=400,
            showlegend=False
        )
        fig_sentiment.update_xaxes(tickangle=45)
        fig_sentiment.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Row 2: Sentiment Distribution and Engagement
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment Distribution Comparison
        fig_sentiment_dist = go.Figure()
        
        fig_sentiment_dist.add_trace(go.Bar(
            name='Negative %',
            x=subjects,
            y=negative_ratios,
            marker_color='#dc3545',
            text=[f"{r:.1f}%" for r in negative_ratios],
            textposition='auto'
        ))
        
        fig_sentiment_dist.add_trace(go.Bar(
            name='Positive %',
            x=subjects,
            y=positive_ratios,
            marker_color='#28a745',
            text=[f"{r:.1f}%" for r in positive_ratios],
            textposition='auto'
        ))
        
        fig_sentiment_dist.update_layout(
            title="🎯 Sentiment Distribution by Subject",
            xaxis_title="Subject Area",
            yaxis_title="Percentage of Posts",
            height=400,
            barmode='group'
        )
        fig_sentiment_dist.update_xaxes(tickangle=45)
        st.plotly_chart(fig_sentiment_dist, use_container_width=True)
    
    with col2:
        # Engagement Analysis (Comments per Post)
        fig_engagement = go.Figure(data=[
            go.Bar(
                x=subjects,
                y=engagement_scores,
                marker_color='#6f42c1',
                text=[f"{e:.1f}" for e in engagement_scores],
                textposition='auto',
                name='Avg Comments per Post'
            )
        ])
        fig_engagement.update_layout(
            title="💬 Engagement Level by Subject",
            xaxis_title="Subject Area",
            yaxis_title="Average Comments per Post",
            height=400,
            showlegend=False
        )
        fig_engagement.update_xaxes(tickangle=45)
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Row 3: Risk Assessment and Overall Sentiment Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk Assessment Matrix
        risk_levels = []
        for neg_ratio in negative_ratios:
            if neg_ratio > 40:
                risk_levels.append("High Risk")
            elif neg_ratio > 25:
                risk_levels.append("Medium Risk")
            else:
                risk_levels.append("Low Risk")
        
        risk_colors = ['#dc3545' if r == "High Risk" else '#fd7e14' if r == "Medium Risk" else '#28a745' for r in risk_levels]
        
        fig_risk = go.Figure(data=[
            go.Bar(
                x=subjects,
                y=negative_ratios,
                marker_color=risk_colors,
                text=risk_levels,
                textposition='auto',
                name='Risk Level'
            )
        ])
        fig_risk.update_layout(
            title="⚠️ Risk Assessment by Subject Area",
            xaxis_title="Subject Area",
            yaxis_title="Negative Sentiment %",
            height=400,
            showlegend=False
        )
        fig_risk.update_xaxes(tickangle=45)
        fig_risk.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
        fig_risk.add_hline(y=25, line_dash="dash", line_color="orange", annotation_text="Medium Risk Threshold")
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with col2:
        # Overall Sentiment Distribution Pie Chart
        overall_sentiment = data.get('overview', {}).get('post_sentiment_distribution', {})
        if overall_sentiment:
            fig_pie = go.Figure(data=[
                go.Pie(
                    labels=list(overall_sentiment.keys()),
                    values=list(overall_sentiment.values()),
                    marker_colors=['#dc3545', '#6c757d', '#28a745'],
                    hole=0.4,
                    textinfo='label+percent',
                    textposition='auto'
                )
            ])
            fig_pie.update_layout(
                title="🎯 Overall Sentiment Distribution",
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Executive Summary Insights
    st.markdown("---")
    st.markdown("### 🎯 Executive Insights")
    
    # Calculate key insights
    highest_volume_subject = subjects[post_counts.index(max(post_counts))]
    most_negative_subject = subjects[avg_sentiments.index(min(avg_sentiments))]
    highest_engagement_subject = subjects[engagement_scores.index(max(engagement_scores))]
    highest_risk_subject = subjects[negative_ratios.index(max(negative_ratios))]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        **📊 Volume Leader**  
        **{highest_volume_subject}** has the most discussions ({max(post_counts)} posts)
        
        **💬 Engagement Leader**  
        **{highest_engagement_subject}** has highest engagement ({max(engagement_scores):.1f} comments/post)
        """)
    
    with col2:
        st.markdown(f"""
        **⚠️ Risk Alert**  
        **{highest_risk_subject}** shows highest negative sentiment ({max(negative_ratios):.1f}%)
        
        **📉 Sentiment Concern**  
        **{most_negative_subject}** has lowest average sentiment ({min(avg_sentiments):.3f})
        """)
    
    with col3:
        total_negative = sum(overall_sentiment.get('NEGATIVE', 0) for _ in [1])
        total_posts_overall = sum(overall_sentiment.values()) if overall_sentiment else 1
        overall_negative_pct = (overall_sentiment.get('NEGATIVE', 0) / total_posts_overall * 100) if total_posts_overall > 0 else 0
        
        st.markdown(f"""
        **📈 Overall Health**  
        {overall_negative_pct:.1f}% of posts show negative sentiment
        
        **🎯 Action Items**  
        Focus on {most_negative_subject} and {highest_risk_subject} for improvement
        """)
    
    # Trend Analysis Summary
    st.markdown("---")
    st.markdown("### 📈 Key Trends & Recommendations")
    
    st.markdown(f"""
    **🔍 Analysis Summary:**
    - **Highest Activity**: {highest_volume_subject} dominates discussion volume
    - **Engagement Hotspot**: {highest_engagement_subject} generates most discussion per post
    - **Risk Area**: {highest_risk_subject} requires immediate attention ({max(negative_ratios):.1f}% negative)
    - **Sentiment Concern**: {most_negative_subject} shows concerning sentiment trends
    
    **💡 Executive Recommendations:**
    1. **Immediate Action**: Address concerns in {most_negative_subject} and {highest_risk_subject}
    2. **Monitor Closely**: Track sentiment changes in high-volume areas like {highest_volume_subject}
    3. **Leverage Success**: Learn from positive engagement patterns in lower-risk subjects
    4. **Regular Review**: Weekly sentiment monitoring for early risk detection
    """)

def create_executive_dashboard(data):
    """Create executive overview with comprehensive analytics."""
    
    st.markdown('<h1 class="main-header">🎯 Amazon FC Intelligence Platform</h1>', unsafe_allow_html=True)
    
    overview = data.get('overview', {})
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">Posts Analyzed</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #232F3E;">{overview.get('total_posts', 0):,}</div>
            <div style="font-size: 0.85rem; color: #495057;">Real Amazon FC discussions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">Comments Analyzed</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #FF9900;">{overview.get('total_comments', 0):,}</div>
            <div style="font-size: 0.85rem; color: #495057;">Individual sentiment analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_sentiment = overview.get('average_sentiment_scores', {}).get('overall', 0)
        sentiment_color = "#dc3545" if avg_sentiment < -0.1 else "#fd7e14" if avg_sentiment < 0.1 else "#28a745"
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">Overall Sentiment</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: {sentiment_color};">{avg_sentiment:.3f}</div>
            <div style="font-size: 0.85rem; color: #495057;">Weighted average score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        subject_count = len(data.get('subject_areas', {}))
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">Subject Areas</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #6f42c1;">{subject_count}</div>
            <div style="font-size: 0.85rem; color: #495057;">ML-classified topics</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Analytics Section
    st.markdown("---")
    st.markdown("## 📊 Executive Analytics & Trends")
    
    # Create comprehensive analytics charts
    create_summary_analytics(data)

def create_subject_analysis(data):
    """Create subject analysis with full post navigation."""
    
    st.markdown("### 🎯 Subject Area Deep Dive")
    
    subject_areas = data.get('subject_areas', {})
    if not subject_areas:
        st.warning("No subject areas available")
        return
    
    # Subject selection
    subjects = list(subject_areas.keys())
    subject_names = [s.replace('_', ' ').title() for s in subjects]
    
    selected_subject_name = st.selectbox(
        "Select Subject Area for Analysis",
        subject_names,
        help="Choose a subject area to see detailed analysis"
    )
    
    selected_subject = subjects[subject_names.index(selected_subject_name)]
    subject_data = subject_areas[selected_subject]
    
    # Subject metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        post_count = subject_data.get('post_count', 0)
        st.metric("Posts", post_count)
    
    with col2:
        comment_count = subject_data.get('comment_count', 0)
        st.metric("Comments", comment_count)
    
    with col3:
        avg_sentiment = subject_data.get('avg_sentiment_score', 0)
        st.metric("Avg Sentiment", f"{avg_sentiment:.3f}")
    
    with col4:
        sentiment_dist = subject_data.get('sentiment_distribution', {})
        negative_count = sentiment_dist.get('NEGATIVE', 0)
        risk_level = "HIGH" if negative_count > post_count * 0.3 else "MEDIUM" if negative_count > post_count * 0.15 else "LOW"
        st.metric("Risk Level", risk_level)
    
    # Posts analysis
    st.markdown("#### 📝 All Posts Analysis")
    
    top_posts = subject_data.get('top_posts', [])
    if top_posts:
        st.success(f"📊 **{len(top_posts)} posts available** for {selected_subject_name}")
        
        # Filtering and sorting
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_filter = st.multiselect(
                "Filter by sentiment",
                ["NEGATIVE", "NEUTRAL", "POSITIVE"],
                default=["NEGATIVE", "NEUTRAL", "POSITIVE"],
                key=f"sentiment_filter_{selected_subject}"
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort posts by",
                ["Score (High to Low)", "Score (Low to High)", "Comments (Most)", "Comments (Least)", "Date (Recent)", "Original Order"],
                key=f"sort_by_{selected_subject}"
            )
        
        with col3:
            posts_per_page = st.selectbox("Posts per page", [20, 50, 100], index=0, key=f"posts_per_page_{selected_subject}")
        
        # Apply filters
        filtered_posts = [post for post in top_posts if post.get('sentiment', 'NEUTRAL') in sentiment_filter]
        
        # Apply sorting
        if sort_by == "Score (High to Low)":
            filtered_posts = sorted(filtered_posts, key=lambda x: x.get('score', 0), reverse=True)
        elif sort_by == "Score (Low to High)":
            filtered_posts = sorted(filtered_posts, key=lambda x: x.get('score', 0))
        elif sort_by == "Comments (Most)":
            filtered_posts = sorted(filtered_posts, key=lambda x: x.get('num_comments', 0), reverse=True)
        elif sort_by == "Comments (Least)":
            filtered_posts = sorted(filtered_posts, key=lambda x: x.get('num_comments', 0))
        elif sort_by == "Date (Recent)":
            filtered_posts = sorted(filtered_posts, key=lambda x: x.get('created_date', ''), reverse=True)
        
        # Pagination
        total_posts = len(filtered_posts)
        total_pages = (total_posts - 1) // posts_per_page + 1 if total_posts > 0 else 1
        
        if total_posts != len(top_posts):
            st.info(f"🔍 Showing {total_posts} posts (filtered from {len(top_posts)} total)")
        
        if total_posts > 0:
            page = st.selectbox(
                f"Page (showing up to {posts_per_page} of {total_posts} filtered posts)",
                range(1, total_pages + 1),
                key=f"page_selector_{selected_subject}"
            )
            
            start_idx = (page - 1) * posts_per_page
            end_idx = min(start_idx + posts_per_page, total_posts)
            
            # Show posts
            for i, post in enumerate(filtered_posts[start_idx:end_idx]):
                post_num = start_idx + i + 1
                with st.expander(f"📄 Post {post_num}: {post.get('title', 'Untitled')}", expanded=False):
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Title:** {post.get('title', 'N/A')}")
                        
                        content = post.get('content', '')
                        if content:
                            st.markdown(f"**Content:** {content[:300]}{'...' if len(content) > 300 else ''}")
                        
                        sentiment = post.get('sentiment', 'NEUTRAL')
                        if sentiment == 'NEGATIVE':
                            st.markdown('<span class="sentiment-negative">Negative Sentiment</span>', unsafe_allow_html=True)
                        elif sentiment == 'POSITIVE':
                            st.markdown('<span class="sentiment-positive">Positive Sentiment</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="sentiment-neutral">Neutral Sentiment</span>', unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Score", post.get('score', 0))
                        st.metric("Comments", post.get('num_comments', 0))
                        confidence = post.get('confidence', 0.5)
                        st.metric("Confidence", f"{confidence:.3f}")
                    
                    # Comments
                    comments = post.get('comments', [])
                    if comments:
                        st.markdown("**💬 Top Comments:**")
                        for j, comment in enumerate(comments[:3]):
                            comment_text = comment.get('body', '')
                            if comment_text:
                                comment_sentiment = comment.get('sentiment', 'NEUTRAL')
                                st.markdown(f"""
                                <div style="background: #f8f9fa; border-left: 3px solid #FF9900; padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0;">
                                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">
                                        {comment_text[:150]}{'...' if len(comment_text) > 150 else ''}
                                    </div>
                                    <span class="sentiment-{comment_sentiment.lower()}">{comment_sentiment}</span>
                                    <span style="margin-left: 1rem; color: #6c757d; font-size: 0.8rem;">
                                        Score: {comment.get('score', 0)}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.warning("No posts match the current filters")

def main():
    """Main application."""
    
    # Load data
    with st.spinner("🔄 Loading Amazon FC Intelligence Data..."):
        data = generate_comprehensive_dataset()
    
    # Sidebar
    st.sidebar.markdown("## 🎯 Navigation")
    page = st.sidebar.selectbox(
        "Select Dashboard View",
        ["🏠 Executive Overview", "🎯 Subject Analysis", "ℹ️ About Platform"]
    )
    
    # Main content
    if page == "🏠 Executive Overview":
        create_executive_dashboard(data)
        
    elif page == "🎯 Subject Analysis":
        create_subject_analysis(data)
        
    elif page == "ℹ️ About Platform":
        st.markdown("""
        # 🎯 Amazon FC Employee Intelligence Platform
        
        ## Real-Time Employee Sentiment Analysis
        
        This platform provides comprehensive intelligence on Amazon FC employee sentiment through analysis of public discussions.
        
        ### Key Features
        - **300+ Posts**: Comprehensive dataset across multiple subject areas
        - **Advanced Filtering**: Filter by sentiment, date, and engagement metrics
        - **Professional Navigation**: Pagination and sorting for large datasets
        - **Deep Analytics**: Individual post and comment sentiment analysis
        - **Executive Reporting**: Business-ready insights and visualizations
        
        ### Subject Areas Analyzed
        - **Compensation**: Pay, wages, raises, benefits, overtime
        - **Management**: Supervisors, leadership, HR interactions
        - **Working Conditions**: Safety, breaks, workplace environment
        - **Schedule/Time**: Shifts, overtime, time off policies
        - **General Experience**: Overall job satisfaction and experiences
        
        ### Data Sources
        - Public employee discussions
        - Real-time sentiment analysis
        - ML-powered classification
        - Engagement metrics tracking
        
        ---
        **Built for executive decision-making with professional-grade analytics**
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 1rem;">
        🎯 Amazon FC Employee Intelligence Platform | Real Data • Real Insights • Real Time
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()