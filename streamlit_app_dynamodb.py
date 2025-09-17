
import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json

# AWS Configuration
@st.cache_resource
def init_aws():
    """Initialize AWS services."""
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('amazon-fc-posts')
    return table

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_posts_from_dynamodb():
    """Load posts from DynamoDB."""
    table = init_aws()
    
    try:
        # Scan table for all posts
        response = table.scan()
        posts = response['Items']
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            posts.extend(response['Items'])
        
        return posts
    except Exception as e:
        st.error(f"Error loading data from DynamoDB: {e}")
        return []

def classify_posts(posts):
    """Classify posts into subject areas."""
    
    subject_keywords = {
        'compensation': ['pay', 'wage', 'salary', 'raise', 'money', 'bonus'],
        'management': ['manager', 'supervisor', 'boss', 'hr', 'fired'],
        'working_conditions': ['safety', 'break', 'bathroom', 'heat', 'injury'],
        'schedule_time': ['schedule', 'shift', 'hours', 'overtime', 'met'],
        'general_experience': ['amazon', 'fc', 'warehouse', 'work', 'job']
    }
    
    classified_posts = {}
    
    for subject, keywords in subject_keywords.items():
        classified_posts[subject] = []
        
        for post in posts:
            title = (post.get('title', '') or '').lower()
            content = (post.get('content', '') or '').lower()
            text = f"{title} {content}"
            
            if any(keyword in text for keyword in keywords):
                classified_posts[subject].append(post)
    
    return classified_posts

def main():
    st.set_page_config(
        page_title="Amazon FC Intelligence Platform",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Amazon FC Intelligence Platform")
    st.subheader("Real-time Employee Sentiment Analysis")
    
    # Load data from DynamoDB
    with st.spinner("Loading real data from AWS DynamoDB..."):
        posts = load_posts_from_dynamodb()
    
    if not posts:
        st.error("No data available. Please check AWS configuration.")
        return
    
    # Classify posts
    classified_posts = classify_posts(posts)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Posts", len(posts))
    
    with col2:
        total_comments = sum(int(post.get('num_comments', 0)) for post in posts)
        st.metric("Total Comments", total_comments)
    
    with col3:
        avg_score = sum(int(post.get('score', 0)) for post in posts) / len(posts) if posts else 0
        st.metric("Avg Score", f"{avg_score:.1f}")
    
    with col4:
        st.metric("Subject Areas", len(classified_posts))
    
    # Subject area analysis
    st.markdown("## 📊 Subject Area Analysis")
    
    subject_names = list(classified_posts.keys())
    selected_subject = st.selectbox("Select Subject Area", subject_names)
    
    if selected_subject and classified_posts[selected_subject]:
        subject_posts = classified_posts[selected_subject]
        st.write(f"**{len(subject_posts)} posts** in {selected_subject.replace('_', ' ').title()}")
        
        # Show posts
        for i, post in enumerate(subject_posts[:10]):
            with st.expander(f"Post {i+1}: {post.get('title', 'Untitled')}"):
                st.write(f"**Score:** {post.get('score', 0)}")
                st.write(f"**Comments:** {post.get('num_comments', 0)}")
                st.write(f"**Author:** {post.get('author', 'Unknown')}")
                
                content = post.get('content', '')
                if content:
                    st.write(f"**Content:** {content[:500]}...")
    
    # Data freshness
    if posts:
        latest_post = max(posts, key=lambda x: int(x.get('created_utc', 0)))
        latest_time = datetime.fromtimestamp(int(latest_post.get('created_utc', 0)))
        st.info(f"Latest post: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
