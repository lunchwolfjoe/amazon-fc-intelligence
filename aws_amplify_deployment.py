#!/usr/bin/env python3
"""
AWS Amplify Deployment Setup
Real data persistence with AWS DynamoDB and S3
"""

import json
import boto3
from datetime import datetime
import os

def create_amplify_config():
    """Create AWS Amplify configuration for real data deployment."""
    
    amplify_config = {
        "version": 1,
        "applications": [
            {
                "appId": "amazon-fc-intelligence",
                "name": "Amazon FC Intelligence Platform",
                "repository": "https://github.com/lunchwolfjoe/amazon-fc-intelligence",
                "platform": "WEB",
                "environmentVariables": {
                    "AWS_REGION": "us-east-1",
                    "DYNAMODB_TABLE": "amazon-fc-posts",
                    "S3_BUCKET": "amazon-fc-intelligence-data",
                    "REDDIT_CLIENT_ID": "${REDDIT_CLIENT_ID}",
                    "REDDIT_CLIENT_SECRET": "${REDDIT_CLIENT_SECRET}",
                    "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
                    "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}"
                },
                "buildSpec": {
                    "version": 1,
                    "applications": [
                        {
                            "frontend": {
                                "phases": {
                                    "preBuild": {
                                        "commands": [
                                            "pip install -r requirements.txt",
                                            "python setup_aws_resources.py"
                                        ]
                                    },
                                    "build": {
                                        "commands": [
                                            "python collect_and_store_data.py",
                                            "streamlit run streamlit_app.py --server.port 8501"
                                        ]
                                    }
                                },
                                "artifacts": {
                                    "baseDirectory": "/",
                                    "files": ["**/*"]
                                }
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    return amplify_config

def create_aws_infrastructure():
    """Create AWS infrastructure for data persistence."""
    
    # DynamoDB table for posts and comments
    dynamodb_table = {
        "TableName": "amazon-fc-posts",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "created_utc", "KeyType": "RANGE"}
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "created_utc", "AttributeType": "N"},
            {"AttributeName": "subject_area", "AttributeType": "S"}
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "subject-area-index",
                "KeySchema": [
                    {"AttributeName": "subject_area", "KeyType": "HASH"},
                    {"AttributeName": "created_utc", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "BillingMode": "PAY_PER_REQUEST"
            }
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "Tags": [
            {"Key": "Project", "Value": "AmazonFCIntelligence"},
            {"Key": "Environment", "Value": "Production"}
        ]
    }
    
    # S3 bucket for data storage and static assets
    s3_bucket = {
        "Bucket": "amazon-fc-intelligence-data",
        "CreateBucketConfiguration": {"LocationConstraint": "us-east-1"},
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        },
        "Tags": [
            {"Key": "Project", "Value": "AmazonFCIntelligence"},
            {"Key": "Environment", "Value": "Production"}
        ]
    }
    
    return {
        "dynamodb_table": dynamodb_table,
        "s3_bucket": s3_bucket
    }

def create_data_collection_lambda():
    """Create Lambda function for automated data collection."""
    
    lambda_function = {
        "FunctionName": "amazon-fc-data-collector",
        "Runtime": "python3.9",
        "Role": "arn:aws:iam::ACCOUNT:role/lambda-execution-role",
        "Handler": "lambda_function.lambda_handler",
        "Code": {
            "ZipFile": """
import json
import boto3
import praw
from datetime import datetime

def lambda_handler(event, context):
    # Initialize AWS services
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('amazon-fc-posts')
    
    # Initialize Reddit client
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent='AmazonFCIntelligence/1.0'
    )
    
    # Collect posts from r/AmazonFC
    subreddit = reddit.subreddit('AmazonFC')
    posts_collected = 0
    
    for post in subreddit.hot(limit=100):
        # Store post in DynamoDB
        table.put_item(
            Item={
                'id': post.id,
                'title': post.title,
                'content': post.selftext,
                'author': str(post.author),
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': int(post.created_utc),
                'url': post.url,
                'subreddit': 'AmazonFC',
                'collected_at': int(datetime.now().timestamp())
            }
        )
        posts_collected += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Collected {posts_collected} posts',
            'timestamp': datetime.now().isoformat()
        })
    }
"""
        },
        "Description": "Automated Reddit data collection for Amazon FC Intelligence",
        "Timeout": 300,
        "MemorySize": 512,
        "Environment": {
            "Variables": {
                "REDDIT_CLIENT_ID": "${REDDIT_CLIENT_ID}",
                "REDDIT_CLIENT_SECRET": "${REDDIT_CLIENT_SECRET}"
            }
        },
        "Tags": {
            "Project": "AmazonFCIntelligence",
            "Environment": "Production"
        }
    }
    
    return lambda_function

def create_streamlit_app_with_dynamodb():
    """Create Streamlit app that reads from DynamoDB."""
    
    streamlit_code = '''
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
'''
    
    return streamlit_code

def create_deployment_files():
    """Create all necessary deployment files."""
    
    # Create amplify.yml
    amplify_yml = """
version: 1
applications:
  - frontend:
      phases:
        preBuild:
          commands:
            - pip install -r requirements.txt
            - python setup_aws_resources.py
        build:
          commands:
            - echo "Building Amazon FC Intelligence Platform"
            - python collect_initial_data.py
        postBuild:
          commands:
            - echo "Build completed"
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
      cache:
        paths:
          - '.cache/**/*'
"""
    
    # Create requirements.txt for Amplify
    requirements = """
streamlit>=1.28.0
boto3>=1.26.0
pandas>=2.0.0
plotly>=5.15.0
praw>=7.7.0
python-dotenv>=1.0.0
"""
    
    # Create setup script
    setup_script = """
import boto3
import os

def setup_aws_resources():
    try:
        # Create DynamoDB table if it doesn't exist
        dynamodb = boto3.resource('dynamodb')
        
        table_name = 'amazon-fc-posts'
        existing_tables = [table.name for table in dynamodb.tables.all()]
        
        if table_name not in existing_tables:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_utc', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'created_utc', 'AttributeType': 'N'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Created DynamoDB table: {table_name}")
        else:
            print(f"DynamoDB table {table_name} already exists")
            
    except Exception as e:
        print(f"Error setting up AWS resources: {e}")

if __name__ == "__main__":
    setup_aws_resources()
"""
    
    return {
        "amplify_yml": amplify_yml,
        "requirements": requirements,
        "setup_script": setup_script,
        "streamlit_app": create_streamlit_app_with_dynamodb()
    }

if __name__ == "__main__":
    print("🚀 Creating AWS Amplify Deployment Configuration...")
    
    # Create deployment files
    files = create_deployment_files()
    
    # Write amplify.yml
    with open('amplify.yml', 'w') as f:
        f.write(files['amplify_yml'])
    
    # Update requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write(files['requirements'])
    
    # Create setup script
    with open('setup_aws_resources.py', 'w') as f:
        f.write(files['setup_script'])
    
    # Update Streamlit app for DynamoDB
    with open('streamlit_app_dynamodb.py', 'w') as f:
        f.write(files['streamlit_app'])
    
    print("✅ AWS Amplify deployment files created!")
    print("\n📋 Next Steps:")
    print("1. Set up AWS Amplify app with this repository")
    print("2. Configure environment variables (AWS credentials, Reddit API)")
    print("3. Deploy to AWS Amplify for real data persistence")
    print("4. Set up Lambda function for automated data collection")
    
    print("\n🔧 AWS Resources Needed:")
    print("- DynamoDB table: amazon-fc-posts")
    print("- S3 bucket: amazon-fc-intelligence-data") 
    print("- Lambda function: amazon-fc-data-collector")
    print("- IAM roles with appropriate permissions")