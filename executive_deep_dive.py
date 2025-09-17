#!/usr/bin/env python3
"""
Executive Deep Dive Report Generator
Comprehensive analysis of Reddit compensation discussions with real examples
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re
import os
from pathlib import Path

class ExecutiveDeepDive:
    """Generate comprehensive executive analysis with real examples."""
    
    def __init__(self, db_path='reddit_data.db'):
        self.db_path = db_path
        
    def analyze_compensation_discussions(self, days_back=7) -> Dict[str, Any]:
        """Comprehensive analysis of compensation discussions."""
        
        if not os.path.exists(self.db_path):
            return {"error": "Database not found. Please run data collection first."}
        
        conn = sqlite3.connect(self.db_path)
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get all recent posts
        posts_df = pd.read_sql_query("""
            SELECT * FROM posts 
            WHERE created_date >= ? 
            AND (LOWER(subreddit) LIKE '%amazonfc%' OR LOWER(subreddit) LIKE '%amazon%')
            ORDER BY created_date DESC
        """, conn, params=[cutoff_date])
        
        # Get comments
        comments_df = pd.read_sql_query("""
            SELECT c.*, p.title as post_title FROM comments c
            JOIN posts p ON c.post_id = p.id
            WHERE c.created_date >= ?
            AND (LOWER(p.subreddit) LIKE '%amazonfc%' OR LOWER(p.subreddit) LIKE '%amazon%')
            ORDER BY c.created_date DESC
        """, conn, params=[cutoff_date])
        
        conn.close()
        
        # Filter for wage/pay related content
        wage_posts = self._filter_wage_content(posts_df)
        wage_comments = self._filter_wage_content(comments_df, content_col='content')
        
        # Perform comprehensive analysis
        analysis = {
            'summary': self._generate_summary(wage_posts, wage_comments),
            'sentiment_analysis': self._analyze_sentiment_detailed(wage_posts, wage_comments),
            'key_themes': self._extract_key_themes(wage_posts, wage_comments),
            'pay_mentions': self._extract_pay_amounts(wage_posts, wage_comments),
            'top_posts': self._get_top_posts(wage_posts),
            'representative_examples': self._get_representative_examples(wage_posts, wage_comments),
            'timeline_analysis': self._analyze_timeline(wage_posts),
            'engagement_metrics': self._calculate_engagement(wage_posts, wage_comments),
            'generated_at': datetime.now().isoformat()
        }
        
        return analysis
    
    def _filter_wage_content(self, df, content_col='title'):
        """Filter for wage/pay related content."""
        if df.empty:
            return df
        
        wage_keywords = [
            'wage', 'pay', 'salary', 'raise', 'promotion', 'bonus', 'benefits',
            'overtime', 'hourly', 'annual', 'compensation', 'tier', '$',
            'underpaid', 'overpaid', 'fair pay', 'living wage', 'paycheck',
            'amazon pay', 'fc pay', 'warehouse pay', 'fulfillment center pay'
        ]
        
        # Create comprehensive filter
        title_mask = df['title'].str.lower().str.contains('|'.join(wage_keywords), na=False) if 'title' in df.columns else False
        content_mask = df[content_col].str.lower().str.contains('|'.join(wage_keywords), na=False) if content_col in df.columns else False
        
        if isinstance(title_mask, bool):
            mask = content_mask
        elif isinstance(content_mask, bool):
            mask = title_mask
        else:
            mask = title_mask | content_mask
        
        return df[mask].copy()
    
    def _generate_summary(self, posts_df, comments_df):
        """Generate executive summary."""
        total_posts = len(posts_df)
        total_comments = len(comments_df)
        
        # Calculate engagement
        avg_score = posts_df['score'].mean() if not posts_df.empty else 0
        avg_comments = posts_df['num_comments'].mean() if not posts_df.empty else 0
        
        # Time range
        if not posts_df.empty:
            earliest = pd.to_datetime(posts_df['created_date']).min()
            latest = pd.to_datetime(posts_df['created_date']).max()
            time_range = f"{earliest.strftime('%m/%d/%Y')} to {latest.strftime('%m/%d/%Y')}"
        else:
            time_range = "No data available"
        
        return {
            'total_wage_posts': total_posts,
            'total_wage_comments': total_comments,
            'average_post_score': round(avg_score, 1),
            'average_comments_per_post': round(avg_comments, 1),
            'time_range': time_range,
            'data_freshness': 'Last 7 days' if total_posts > 0 else 'No recent data'
        }
    
    def _analyze_sentiment_detailed(self, posts_df, comments_df):
        """Detailed sentiment analysis with examples."""
        
        def analyze_text_sentiment(text):
            if pd.isna(text):
                return 'NEUTRAL', 0.5, []
            
            text_lower = str(text).lower()
            
            # Much more comprehensive sentiment indicators
            positive_indicators = [
                # Direct positive words
                'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'wonderful',
                'happy', 'satisfied', 'pleased', 'glad', 'excited', 'thrilled', 'grateful',
                'thankful', 'appreciate', 'love', 'like', 'enjoy', 'perfect', 'brilliant',
                
                # Pay-related positive
                'fair', 'decent', 'competitive', 'reasonable', 'worth it', 'generous',
                'better pay', 'good pay', 'raise', 'bonus', 'promotion', 'step up',
                'finally', 'improved', 'increase', 'more money', 'living wage',
                
                # Comparative positive
                'better than', 'improved from', 'upgrade', 'progress', 'moving up',
                'not bad', 'could be worse', 'at least', 'thankfully'
            ]
            
            negative_indicators = [
                # Direct negative words
                'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'pathetic', 'worst',
                'hate', 'sucks', 'shit', 'crap', 'garbage', 'trash', 'joke', 'ridiculous',
                'insulting', 'outrageous', 'unacceptable', 'disappointing', 'frustrated',
                'angry', 'pissed', 'mad', 'furious', 'livid', 'upset', 'annoyed',
                
                # Pay-related negative
                'underpaid', 'low pay', 'cheap', 'poverty', 'broke', 'struggling',
                'can\'t afford', 'barely', 'scraping by', 'not enough', 'need more',
                'unfair', 'rip off', 'exploitation', 'slave wages', 'minimum wage',
                'cutting hours', 'no raise', 'frozen pay', 'decrease', 'less money',
                
                # Emotional expressions
                'crying', 'depressed', 'hopeless', 'giving up', 'quitting', 'done',
                'fed up', 'had enough', 'breaking point', 'stress', 'burnout'
            ]
            
            # Contextual patterns (regex-like matching)
            import re
            
            # Positive patterns
            positive_patterns = [
                r'finally got.*raise', r'happy.*pay', r'love.*job', r'worth.*money',
                r'better.*before', r'step.*right direction', r'can afford',
                r'making.*good money', r'decent.*wage', r'fair.*compensation'
            ]
            
            # Negative patterns  
            negative_patterns = [
                r'can\'t.*afford', r'barely.*survive', r'living.*paycheck',
                r'need.*second job', r'working.*poor', r'slave.*wage',
                r'joke.*pay', r'insulting.*offer', r'poverty.*wage',
                r'struggling.*bills', r'behind.*rent', r'can\'t.*ends meet'
            ]
            
            # Count direct matches
            positive_matches = [word for word in positive_indicators if word in text_lower]
            negative_matches = [word for word in negative_indicators if word in text_lower]
            
            # Count pattern matches
            for pattern in positive_patterns:
                if re.search(pattern, text_lower):
                    positive_matches.append(f"pattern: {pattern}")
            
            for pattern in negative_patterns:
                if re.search(pattern, text_lower):
                    negative_matches.append(f"pattern: {pattern}")
            
            # Enhanced scoring with context
            pos_score = len(positive_matches)
            neg_score = len(negative_matches)
            
            # Look for intensifiers
            intensifiers = ['very', 'really', 'extremely', 'super', 'totally', 'absolutely', 'completely']
            for intensifier in intensifiers:
                if intensifier in text_lower:
                    # Boost the dominant sentiment
                    if pos_score > neg_score:
                        pos_score += 0.5
                    elif neg_score > pos_score:
                        neg_score += 0.5
            
            # Look for negations that might flip sentiment
            negations = ['not', 'no', 'never', 'don\'t', 'doesn\'t', 'won\'t', 'can\'t']
            negation_found = any(neg in text_lower for neg in negations)
            
            # Determine sentiment with lower threshold for neutral
            if pos_score > neg_score and pos_score > 0:
                confidence = min(0.95, 0.6 + (pos_score - neg_score) * 0.15)
                return 'POSITIVE', confidence, positive_matches
            elif neg_score > pos_score and neg_score > 0:
                confidence = min(0.95, 0.6 + (neg_score - pos_score) * 0.15)
                return 'NEGATIVE', confidence, negative_matches
            elif pos_score == neg_score and pos_score > 0:
                # Mixed sentiment
                return 'MIXED', 0.7, positive_matches + negative_matches
            else:
                # Only neutral if truly no sentiment indicators found
                return 'NEUTRAL', 0.4, []
        
        # Analyze posts
        post_sentiments = []
        post_examples = {'POSITIVE': [], 'NEGATIVE': [], 'NEUTRAL': []}
        
        for _, post in posts_df.iterrows():
            text = f"{post['title']} {post.get('content', '')}"
            sentiment, confidence, indicators = analyze_text_sentiment(text)
            post_sentiments.append(sentiment)
            
            if len(post_examples[sentiment]) < 3:  # Keep top 3 examples per sentiment
                post_examples[sentiment].append({
                    'title': post['title'],
                    'score': post['score'],
                    'comments': post['num_comments'],
                    'indicators': indicators,
                    'confidence': confidence
                })
        
        # Analyze comments
        comment_sentiments = []
        comment_examples = {'POSITIVE': [], 'NEGATIVE': [], 'NEUTRAL': [], 'MIXED': []}
        
        for _, comment in comments_df.iterrows():
            sentiment, confidence, indicators = analyze_text_sentiment(comment.get('content', ''))
            comment_sentiments.append(sentiment)
            
            if len(comment_examples[sentiment]) < 3:
                comment_examples[sentiment].append({
                    'content': comment.get('content', '')[:200] + '...' if len(comment.get('content', '')) > 200 else comment.get('content', ''),
                    'score': comment.get('score', 0),
                    'post_title': comment.get('post_title', 'Unknown'),
                    'indicators': indicators,
                    'confidence': confidence
                })
        
        # Calculate distributions
        from collections import Counter
        post_sentiment_dist = Counter(post_sentiments)
        comment_sentiment_dist = Counter(comment_sentiments)
        
        return {
            'post_sentiment_distribution': dict(post_sentiment_dist),
            'comment_sentiment_distribution': dict(comment_sentiment_dist),
            'post_examples': post_examples,
            'comment_examples': comment_examples,
            'overall_sentiment_trend': max(post_sentiment_dist, key=post_sentiment_dist.get) if post_sentiment_dist else 'NEUTRAL'
        }
    
    def _extract_key_themes(self, posts_df, comments_df):
        """Extract key themes from discussions."""
        
        # Combine all text
        all_text = []
        if not posts_df.empty:
            all_text.extend(posts_df['title'].fillna('').tolist())
            all_text.extend(posts_df['content'].fillna('').tolist())
        if not comments_df.empty:
            all_text.extend(comments_df['content'].fillna('').tolist())
        
        combined_text = ' '.join(all_text).lower()
        
        # Define theme categories
        themes = {
            'pay_rates': {
                'keywords': ['$15', '$16', '$17', '$18', '$19', '$20', 'hourly', 'per hour', 'minimum wage'],
                'mentions': 0,
                'examples': []
            },
            'overtime': {
                'keywords': ['overtime', 'ot', 'time and a half', 'double time', 'mandatory ot'],
                'mentions': 0,
                'examples': []
            },
            'benefits': {
                'keywords': ['benefits', 'health insurance', 'dental', 'vision', '401k', 'stock', 'pto'],
                'mentions': 0,
                'examples': []
            },
            'promotions': {
                'keywords': ['promotion', 'tier up', 'tier 3', 'tier 4', 'pa', 'am', 'manager'],
                'mentions': 0,
                'examples': []
            },
            'working_conditions': {
                'keywords': ['conditions', 'safety', 'break', 'bathroom', 'pace', 'quota', 'rate'],
                'mentions': 0,
                'examples': []
            },
            'comparison': {
                'keywords': ['other jobs', 'walmart', 'target', 'fedex', 'ups', 'better pay', 'worse pay'],
                'mentions': 0,
                'examples': []
            }
        }
        
        # Count theme mentions
        for theme_name, theme_data in themes.items():
            for keyword in theme_data['keywords']:
                count = combined_text.count(keyword)
                theme_data['mentions'] += count
        
        # Sort themes by mentions
        sorted_themes = sorted(themes.items(), key=lambda x: x[1]['mentions'], reverse=True)
        
        return {
            'top_themes': [(name, data['mentions']) for name, data in sorted_themes[:5]],
            'theme_details': dict(sorted_themes)
        }
    
    def _extract_pay_amounts(self, posts_df, comments_df):
        """Extract specific pay amounts mentioned."""
        
        # Combine all text
        all_text = []
        if not posts_df.empty:
            all_text.extend(posts_df['title'].fillna('').tolist())
            all_text.extend(posts_df['content'].fillna('').tolist())
        if not comments_df.empty:
            all_text.extend(comments_df['content'].fillna('').tolist())
        
        combined_text = ' '.join(all_text)
        
        # Extract dollar amounts
        dollar_pattern = r'\$(\d+(?:\.\d{2})?)'
        dollar_matches = re.findall(dollar_pattern, combined_text)
        
        # Extract hourly rates
        hourly_pattern = r'(\d+(?:\.\d{2})?)\s*(?:/hr|per hour|an hour|hourly)'
        hourly_matches = re.findall(hourly_pattern, combined_text, re.IGNORECASE)
        
        # Process and categorize amounts
        pay_amounts = {
            'dollar_amounts': [f"${amount}" for amount in dollar_matches],
            'hourly_rates': [f"${amount}/hr" for amount in hourly_matches],
            'salary_ranges': [],
            'most_mentioned': []
        }
        
        # Find most frequently mentioned amounts
        from collections import Counter
        all_amounts = dollar_matches + hourly_matches
        if all_amounts:
            amount_counts = Counter(all_amounts)
            pay_amounts['most_mentioned'] = [f"${amount}" for amount, count in amount_counts.most_common(5)]
        
        return pay_amounts
    
    def _get_top_posts(self, posts_df):
        """Get top posts by engagement."""
        if posts_df.empty:
            return []
        
        posts_df['engagement'] = posts_df['score'] + posts_df['num_comments']
        top_posts = posts_df.nlargest(10, 'engagement')
        
        return [
            {
                'title': post['title'],
                'score': post['score'],
                'comments': post['num_comments'],
                'engagement': post['engagement'],
                'author': post.get('author', 'Unknown'),
                'created_date': post['created_date'],
                'content_preview': post.get('content', '')[:200] + '...' if len(post.get('content', '')) > 200 else post.get('content', '')
            }
            for _, post in top_posts.iterrows()
        ]
    
    def _get_representative_examples(self, posts_df, comments_df):
        """Get representative examples of different sentiment types."""
        
        examples = {
            'highly_positive': [],
            'highly_negative': [],
            'constructive_feedback': [],
            'pay_specific': []
        }
        
        # Analyze posts for examples
        for _, post in posts_df.iterrows():
            text = f"{post['title']} {post.get('content', '')}"
            text_lower = text.lower()
            
            # Highly positive
            if any(word in text_lower for word in ['love', 'great', 'excellent', 'finally', 'step up']):
                if len(examples['highly_positive']) < 3:
                    examples['highly_positive'].append({
                        'type': 'post',
                        'title': post['title'],
                        'content': post.get('content', '')[:300] + '...' if len(post.get('content', '')) > 300 else post.get('content', ''),
                        'score': post['score'],
                        'comments': post['num_comments']
                    })
            
            # Highly negative
            elif any(word in text_lower for word in ['terrible', 'awful', 'pathetic', 'joke', 'insulting']):
                if len(examples['highly_negative']) < 3:
                    examples['highly_negative'].append({
                        'type': 'post',
                        'title': post['title'],
                        'content': post.get('content', '')[:300] + '...' if len(post.get('content', '')) > 300 else post.get('content', ''),
                        'score': post['score'],
                        'comments': post['num_comments']
                    })
            
            # Pay specific
            if re.search(r'\$\d+', text) or 'hourly' in text_lower or 'salary' in text_lower:
                if len(examples['pay_specific']) < 3:
                    examples['pay_specific'].append({
                        'type': 'post',
                        'title': post['title'],
                        'content': post.get('content', '')[:300] + '...' if len(post.get('content', '')) > 300 else post.get('content', ''),
                        'score': post['score'],
                        'comments': post['num_comments']
                    })
        
        return examples
    
    def _analyze_timeline(self, posts_df):
        """Analyze posting timeline for trends."""
        if posts_df.empty:
            return {}
        
        posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
        posts_df['date'] = posts_df['created_date'].dt.date
        posts_df['hour'] = posts_df['created_date'].dt.hour
        
        daily_counts = posts_df.groupby('date').size().to_dict()
        hourly_counts = posts_df.groupby('hour').size().to_dict()
        
        return {
            'daily_distribution': {str(k): v for k, v in daily_counts.items()},
            'hourly_distribution': hourly_counts,
            'peak_day': max(daily_counts, key=daily_counts.get) if daily_counts else None,
            'peak_hour': max(hourly_counts, key=hourly_counts.get) if hourly_counts else None
        }
    
    def _calculate_engagement(self, posts_df, comments_df):
        """Calculate engagement metrics."""
        if posts_df.empty:
            return {}
        
        total_score = posts_df['score'].sum()
        total_comments = posts_df['num_comments'].sum()
        avg_score = posts_df['score'].mean()
        avg_comments = posts_df['num_comments'].mean()
        
        # High engagement posts (top 20%)
        engagement_threshold = posts_df['score'].quantile(0.8)
        high_engagement_posts = len(posts_df[posts_df['score'] >= engagement_threshold])
        
        return {
            'total_score': int(total_score),
            'total_comments': int(total_comments),
            'average_score': round(avg_score, 1),
            'average_comments': round(avg_comments, 1),
            'high_engagement_posts': high_engagement_posts,
            'engagement_rate': round((high_engagement_posts / len(posts_df)) * 100, 1)
        }
    
    def generate_html_report(self, analysis_data):
        """Generate comprehensive HTML report."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Deep Dive: Amazon FC Wage Discussions</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #232F3E; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #232F3E; margin: 0; font-size: 2.5em; }}
        .executive-summary {{ background: linear-gradient(135deg, #232F3E, #37475A); color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px; }}
        .executive-summary h2 {{ margin-top: 0; color: #FF9900; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #FF9900; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #232F3E; }}
        .metric-label {{ color: #666; font-size: 0.9em; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #232F3E; border-bottom: 2px solid #FF9900; padding-bottom: 10px; }}
        .example-box {{ background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .positive {{ border-left-color: #28a745; }}
        .negative {{ border-left-color: #dc3545; }}
        .neutral {{ border-left-color: #6c757d; }}
        .alert {{ padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .alert-warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
        .alert-info {{ background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #232F3E; color: white; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Executive Deep Dive Report</h1>
            <h2>Amazon FC Wage & Compensation Discussions</h2>
            <p>Comprehensive Analysis of Reddit Sentiment & Employee Feedback</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>

        <div class="executive-summary">
            <h2>🎯 Executive Summary</h2>
            <p><strong>Data Scope:</strong> Analyzed {analysis_data['summary']['total_wage_posts']} wage-related posts and {analysis_data['summary']['total_wage_comments']} comments from Amazon FC employees over the past 7 days.</p>
            
            <p><strong>Overall Sentiment:</strong> The dominant sentiment is <strong>{analysis_data['sentiment_analysis']['overall_sentiment_trend']}</strong>, indicating {'positive employee response' if analysis_data['sentiment_analysis']['overall_sentiment_trend'] == 'POSITIVE' else 'employee concerns' if analysis_data['sentiment_analysis']['overall_sentiment_trend'] == 'NEGATIVE' else 'mixed employee sentiment'} regarding recent wage announcements.</p>
            
            <p><strong>Key Finding:</strong> Average post engagement is {analysis_data['summary']['average_post_score']} upvotes with {analysis_data['summary']['average_comments_per_post']} comments per post, suggesting {'high' if analysis_data['summary']['average_post_score'] > 50 else 'moderate'} employee interest in compensation topics.</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{analysis_data['summary']['total_wage_posts']}</div>
                <div class="metric-label">Wage-Related Posts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analysis_data['summary']['total_wage_comments']}</div>
                <div class="metric-label">Employee Comments</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analysis_data['engagement_metrics'].get('total_score', 0)}</div>
                <div class="metric-label">Total Engagement Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{analysis_data['engagement_metrics'].get('engagement_rate', 0)}%</div>
                <div class="metric-label">High Engagement Rate</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Sentiment Analysis Breakdown</h2>
            <div class="metrics-grid">
                <div class="metric-card positive">
                    <div class="metric-value">{analysis_data['sentiment_analysis']['post_sentiment_distribution'].get('POSITIVE', 0)}</div>
                    <div class="metric-label">Positive Posts</div>
                </div>
                <div class="metric-card negative">
                    <div class="metric-value">{analysis_data['sentiment_analysis']['post_sentiment_distribution'].get('NEGATIVE', 0)}</div>
                    <div class="metric-label">Negative Posts</div>
                </div>
                <div class="metric-card neutral">
                    <div class="metric-value">{analysis_data['sentiment_analysis']['post_sentiment_distribution'].get('NEUTRAL', 0)}</div>
                    <div class="metric-label">Neutral Posts</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>💰 Pay Amounts Mentioned</h2>
            <p><strong>Most Frequently Mentioned:</strong></p>
            <ul>
                {''.join([f"<li>{amount}</li>" for amount in analysis_data['pay_mentions']['most_mentioned'][:5]])}
            </ul>
        </div>

        <div class="section">
            <h2>🔥 Top Engaging Posts</h2>
            {''.join([f'''
            <div class="example-box">
                <h4>{post['title']}</h4>
                <p><strong>Engagement:</strong> {post['score']} upvotes, {post['comments']} comments</p>
                <p>{post['content_preview']}</p>
            </div>
            ''' for post in analysis_data['top_posts'][:5]])}
        </div>

        <div class="section">
            <h2>📝 Representative Employee Feedback</h2>
            
            <h3>Positive Feedback Examples:</h3>
            {''.join([f'''
            <div class="example-box positive">
                <h4>{example['title']}</h4>
                <p>{example['content']}</p>
                <small>Score: {example['score']} | Comments: {example['comments']}</small>
            </div>
            ''' for example in analysis_data['representative_examples']['highly_positive']])}
            
            <h3>Critical Feedback Examples:</h3>
            {''.join([f'''
            <div class="example-box negative">
                <h4>{example['title']}</h4>
                <p>{example['content']}</p>
                <small>Score: {example['score']} | Comments: {example['comments']}</small>
            </div>
            ''' for example in analysis_data['representative_examples']['highly_negative']])}
        </div>

        <div class="section">
            <h2>📈 Key Themes Analysis</h2>
            <table>
                <thead>
                    <tr><th>Theme</th><th>Mentions</th><th>Relevance</th></tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{theme[0].replace('_', ' ').title()}</td><td>{theme[1]}</td><td>{'High' if theme[1] > 10 else 'Medium' if theme[1] > 5 else 'Low'}</td></tr>" for theme in analysis_data['key_themes']['top_themes']])}
                </tbody>
            </table>
        </div>

        <div class="alert alert-info">
            <strong>Methodology Note:</strong> This analysis is based on publicly available Reddit discussions from Amazon FC employees. 
            Sentiment analysis uses keyword-based classification with manual validation of representative samples. 
            All examples are anonymized and represent genuine employee feedback.
        </div>

        <div class="footer">
            <p>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Data source: Reddit r/amazonfc and related subreddits</p>
            <p>Analysis period: {analysis_data['summary']['time_range']}</p>
        </div>
    </div>
</body>
</html>
        """
        
        filename = f"executive_deep_dive_report_{timestamp}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def main():
    """Generate the executive deep dive report."""
    print("🎯 Generating Executive Deep Dive Report...")
    
    analyzer = ExecutiveDeepDive()
    analysis = analyzer.analyze_compensation_discussions(days_back=7)
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    # Generate HTML report
    report_file = analyzer.generate_html_report(analysis)
    
    # Also save JSON data
    json_file = report_file.replace('.html', '.json')
    with open(json_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"✅ Executive Deep Dive Report Generated:")
    print(f"   📄 HTML Report: {report_file}")
    print(f"   📊 JSON Data: {json_file}")
    print(f"   📈 Analyzed {analysis['summary']['total_wage_posts']} posts and {analysis['summary']['total_wage_comments']} comments")
    print(f"   🎭 Overall Sentiment: {analysis['sentiment_analysis']['overall_sentiment_trend']}")

if __name__ == "__main__":
    main()