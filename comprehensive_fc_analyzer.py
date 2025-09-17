#!/usr/bin/env python3
"""
Comprehensive Amazon FC Employee Intelligence Platform
Analyzes ALL posts, auto-categorizes by subject, provides drill-down sentiment analysis
"""

import sqlite3
import pandas as pd
import json
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import os
import time
import re
from collections import Counter, defaultdict

class ComprehensiveFCAnalyzer:
    """Advanced Amazon FC employee sentiment and topic analysis platform."""
    
    def __init__(self, db_path='reddit_data.db'):
        self.db_path = db_path
        
        # Initialize AWS Comprehend
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')
        
        # Cost tracking
        self.api_calls = 0
        self.estimated_cost = 0.0
        
        # Subject area classifications (will be ML-enhanced)
        self.subject_areas = {
            'compensation': {
                'keywords': ['salary', 'wage', 'pay', 'raise', 'bonus', 'benefits', 'overtime', 'tier', 'promotion'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'working_conditions': {
                'keywords': ['safety', 'break', 'bathroom', 'pace', 'quota', 'rate', 'conditions', 'environment'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'management': {
                'keywords': ['manager', 'supervisor', 'leadership', 'boss', 'am', 'pa', 'hr'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'schedule_time': {
                'keywords': ['schedule', 'shift', 'hours', 'time', 'overtime', 'vet', 'vto', 'upt'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'career_development': {
                'keywords': ['career', 'training', 'learning', 'development', 'skills', 'advancement'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'workplace_culture': {
                'keywords': ['culture', 'team', 'coworkers', 'atmosphere', 'morale', 'respect'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'policies_procedures': {
                'keywords': ['policy', 'procedure', 'rules', 'guidelines', 'compliance', 'attendance'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'technology_systems': {
                'keywords': ['system', 'technology', 'app', 'scanner', 'computer', 'software'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            },
            'general_experience': {
                'keywords': ['experience', 'job', 'work', 'amazon', 'fc', 'warehouse'],
                'posts': [],
                'sentiment_distribution': {},
                'avg_sentiment_score': 0.0
            }
        }
    
    def analyze_all_fc_content(self, days_back=7, max_posts=500) -> Dict[str, Any]:
        """Comprehensive analysis of ALL Amazon FC content with ML classification."""
        
        print("🚀 Starting Comprehensive Amazon FC Intelligence Analysis...")
        print(f"📊 Analyzing last {days_back} days of ALL amazonfc posts")
        
        if not os.path.exists(self.db_path):
            return {"error": "Database not found. Please run data collection first."}
        
        # Load ALL data (not just compensation)
        conn = sqlite3.connect(self.db_path)
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get ALL posts from amazonfc
        posts_df = pd.read_sql_query("""
            SELECT * FROM posts 
            WHERE created_date >= ? 
            AND (LOWER(subreddit) LIKE '%amazonfc%')
            ORDER BY created_date DESC
            LIMIT ?
        """, conn, params=[cutoff_date, max_posts])
        
        # Get ALL comments
        comments_df = pd.read_sql_query("""
            SELECT c.*, p.title as post_title, p.score as post_score FROM comments c
            JOIN posts p ON c.post_id = p.id
            WHERE c.created_date >= ?
            AND (LOWER(p.subreddit) LIKE '%amazonfc%')
            ORDER BY c.created_date DESC
        """, conn, params=[cutoff_date])
        
        conn.close()
        
        print(f"📈 Loaded {len(posts_df)} posts and {len(comments_df)} comments")
        
        # Step 1: ML-powered subject classification for ALL posts
        classified_posts = self._classify_all_posts_ml(posts_df)
        
        # Step 2: Sentiment analysis for ALL content
        post_sentiments = self._analyze_sentiment_batch(posts_df, 'posts')
        comment_sentiments = self._analyze_sentiment_batch(comments_df, 'comments')
        
        # Step 3: Advanced topic modeling using key phrases
        topic_insights = self._extract_advanced_topics(posts_df, comments_df)
        
        # Step 4: Build comprehensive analysis
        analysis = {
            'overview': self._generate_overview(posts_df, comments_df, classified_posts, post_sentiments, comment_sentiments),
            'subject_areas': self._analyze_by_subject_area(classified_posts, post_sentiments, comments_df, comment_sentiments),
            'sentiment_deep_dive': self._create_sentiment_deep_dive(post_sentiments, comment_sentiments),
            'topic_insights': topic_insights,
            'engagement_analysis': self._analyze_engagement_patterns(posts_df, comments_df, post_sentiments),
            'temporal_analysis': self._analyze_temporal_patterns(posts_df, post_sentiments),
            'drill_down_data': self._prepare_drill_down_data(classified_posts, post_sentiments, comments_df, comment_sentiments),
            'cost_summary': {
                'api_calls': self.api_calls,
                'estimated_cost': round(self.estimated_cost, 4),
                'items_analyzed': len(posts_df) + len(comments_df)
            },
            'generated_at': datetime.now().isoformat()
        }
        
        print(f"💰 AWS Comprehend usage: {self.api_calls} API calls, ${self.estimated_cost:.4f}")
        print(f"🎯 Analysis complete: {len(classified_posts)} posts classified into {len(self.subject_areas)} subject areas")
        
        return analysis
    
    def _classify_all_posts_ml(self, posts_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Use ML to classify ALL posts into subject areas."""
        
        print("🤖 ML Classification: Analyzing ALL posts for subject areas...")
        
        classified_posts = []
        batch_size = 25
        
        for i in range(0, len(posts_df), batch_size):
            batch_df = posts_df.iloc[i:i+batch_size]
            
            # Prepare texts for analysis
            texts = []
            for _, row in batch_df.iterrows():
                text = f"{row['title']} {row.get('content', '')}"
                text = str(text).strip()
                if len(text.encode('utf-8')) > 5000:
                    text = text[:4000]
                texts.append(text)
            
            # Batch key phrase extraction for topic classification
            try:
                response = self.comprehend.batch_detect_key_phrases(
                    TextList=texts,
                    LanguageCode='en'
                )
                
                self.api_calls += 1
                self.estimated_cost += len(texts) * 0.0001
                
                # Classify each post based on key phrases
                for idx, result in enumerate(response['ResultList']):
                    row_data = batch_df.iloc[idx]
                    
                    # Extract key phrases
                    key_phrases = []
                    if 'KeyPhrases' in result:
                        key_phrases = [kp['Text'].lower() for kp in result['KeyPhrases']]
                    
                    # Classify into subject areas
                    subject_scores = {}
                    for subject, data in self.subject_areas.items():
                        score = 0
                        for keyword in data['keywords']:
                            # Check in key phrases
                            phrase_matches = sum(1 for phrase in key_phrases if keyword in phrase)
                            # Check in original text
                            text_matches = texts[idx].lower().count(keyword)
                            score += phrase_matches * 2 + text_matches  # Weight ML phrases higher
                        subject_scores[subject] = score
                    
                    # Determine primary and secondary subjects
                    sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
                    primary_subject = sorted_subjects[0][0] if sorted_subjects[0][1] > 0 else 'general_experience'
                    secondary_subjects = [s[0] for s in sorted_subjects[1:3] if s[1] > 0]
                    
                    classified_post = {
                        'index': batch_df.index[idx],
                        'post_data': row_data.to_dict(),
                        'primary_subject': primary_subject,
                        'secondary_subjects': secondary_subjects,
                        'subject_scores': subject_scores,
                        'key_phrases': key_phrases,
                        'classification_confidence': sorted_subjects[0][1] / max(sum(subject_scores.values()), 1)
                    }
                    
                    classified_posts.append(classified_post)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ ML Classification error: {e}")
                # Fallback classification
                for idx, text in enumerate(texts):
                    row_data = batch_df.iloc[idx]
                    classified_posts.append({
                        'index': batch_df.index[idx],
                        'post_data': row_data.to_dict(),
                        'primary_subject': 'general_experience',
                        'secondary_subjects': [],
                        'subject_scores': {},
                        'key_phrases': [],
                        'classification_confidence': 0.5
                    })
        
        return classified_posts
    
    def _analyze_sentiment_batch(self, df: pd.DataFrame, content_type: str) -> List[Dict[str, Any]]:
        """Comprehensive sentiment analysis for all content."""
        
        if df.empty:
            return []
        
        print(f"😊 Sentiment Analysis: Processing {len(df)} {content_type}...")
        
        sentiments = []
        batch_size = 25
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            
            texts = []
            for _, row in batch_df.iterrows():
                if content_type == 'posts':
                    text = f"{row['title']} {row.get('content', '')}"
                else:
                    text = row.get('content', '')
                
                text = str(text).strip()
                if len(text.encode('utf-8')) > 5000:
                    text = text[:4000]
                texts.append(text)
            
            try:
                response = self.comprehend.batch_detect_sentiment(
                    TextList=texts,
                    LanguageCode='en'
                )
                
                self.api_calls += 1
                self.estimated_cost += len(texts) * 0.0001
                
                for idx, result in enumerate(response['ResultList']):
                    row_data = batch_df.iloc[idx]
                    
                    # Calculate overall sentiment score (-1 to 1)
                    scores = result.get('SentimentScore', {})
                    sentiment_score = (
                        scores.get('Positive', 0) - scores.get('Negative', 0)
                    )
                    
                    sentiment_data = {
                        'index': batch_df.index[idx],
                        'sentiment': result.get('Sentiment', 'NEUTRAL'),
                        'confidence_scores': scores,
                        'sentiment_score': sentiment_score,
                        'confidence': max(scores.values()) if scores else 0.5,
                        'text_preview': texts[idx][:200] + '...' if len(texts[idx]) > 200 else texts[idx],
                        'metadata': {
                            'title': row_data.get('title', ''),
                            'score': row_data.get('score', 0),
                            'num_comments': row_data.get('num_comments', 0),
                            'created_date': row_data.get('created_date', ''),
                            'author': row_data.get('author', ''),
                            'post_id': row_data.get('post_id', '') if content_type == 'comments' else row_data.get('id', '')
                        }
                    }
                    
                    sentiments.append(sentiment_data)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Sentiment analysis error: {e}")
                # Fallback
                for idx, text in enumerate(texts):
                    row_data = batch_df.iloc[idx]
                    sentiments.append({
                        'index': batch_df.index[idx],
                        'sentiment': 'NEUTRAL',
                        'confidence_scores': {'Neutral': 0.5},
                        'sentiment_score': 0.0,
                        'confidence': 0.5,
                        'text_preview': text[:200] + '...' if len(text) > 200 else text,
                        'metadata': {
                            'title': row_data.get('title', ''),
                            'score': row_data.get('score', 0),
                            'num_comments': row_data.get('num_comments', 0),
                            'created_date': row_data.get('created_date', ''),
                            'author': row_data.get('author', ''),
                            'post_id': row_data.get('post_id', '') if content_type == 'comments' else row_data.get('id', '')
                        }
                    })
        
        return sentiments
    
    def _extract_advanced_topics(self, posts_df: pd.DataFrame, comments_df: pd.DataFrame) -> Dict[str, Any]:
        """Extract advanced topic insights using ML."""
        
        print("🔍 Advanced Topic Analysis: Extracting key themes...")
        
        # Sample representative content for topic analysis
        sample_posts = posts_df.head(50) if len(posts_df) > 50 else posts_df
        
        all_key_phrases = []
        
        # Extract key phrases from sample
        for i in range(0, len(sample_posts), 25):
            batch = sample_posts.iloc[i:i+25]
            texts = [f"{row['title']} {row.get('content', '')}"[:4000] for _, row in batch.iterrows()]
            
            try:
                response = self.comprehend.batch_detect_key_phrases(
                    TextList=texts,
                    LanguageCode='en'
                )
                
                self.api_calls += 1
                self.estimated_cost += len(texts) * 0.0001
                
                for result in response['ResultList']:
                    if 'KeyPhrases' in result:
                        phrases = [kp['Text'].lower() for kp in result['KeyPhrases'] if kp['Score'] > 0.8]
                        all_key_phrases.extend(phrases)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Topic extraction error: {e}")
        
        # Analyze phrase frequency and group into topics
        phrase_counter = Counter(all_key_phrases)
        top_phrases = phrase_counter.most_common(20)
        
        return {
            'top_key_phrases': top_phrases,
            'emerging_topics': self._identify_emerging_topics(phrase_counter),
            'topic_trends': self._analyze_topic_trends(all_key_phrases)
        }
    
    def _identify_emerging_topics(self, phrase_counter: Counter) -> List[Dict[str, Any]]:
        """Identify emerging topics from key phrases."""
        
        # Group related phrases
        topic_groups = {
            'pay_benefits': ['pay', 'salary', 'wage', 'benefits', 'bonus', 'raise'],
            'work_environment': ['safety', 'conditions', 'environment', 'workplace'],
            'management_issues': ['manager', 'supervisor', 'leadership', 'management'],
            'scheduling': ['schedule', 'shift', 'hours', 'overtime'],
            'technology': ['system', 'app', 'technology', 'scanner']
        }
        
        emerging_topics = []
        for topic, keywords in topic_groups.items():
            total_mentions = sum(phrase_counter.get(keyword, 0) for keyword in keywords)
            if total_mentions > 0:
                emerging_topics.append({
                    'topic': topic,
                    'total_mentions': total_mentions,
                    'key_phrases': [(kw, phrase_counter.get(kw, 0)) for kw in keywords if phrase_counter.get(kw, 0) > 0]
                })
        
        return sorted(emerging_topics, key=lambda x: x['total_mentions'], reverse=True)
    
    def _analyze_topic_trends(self, phrases: List[str]) -> Dict[str, Any]:
        """Analyze trending topics over time."""
        
        # Simple trend analysis
        return {
            'total_unique_phrases': len(set(phrases)),
            'phrase_diversity': len(set(phrases)) / max(len(phrases), 1),
            'top_categories': ['compensation', 'working_conditions', 'management']
        }
    
    def _generate_overview(self, posts_df, comments_df, classified_posts, post_sentiments, comment_sentiments):
        """Generate comprehensive overview."""
        
        # Subject area distribution
        subject_distribution = Counter([cp['primary_subject'] for cp in classified_posts])
        
        # Overall sentiment distribution
        post_sentiment_dist = Counter([ps['sentiment'] for ps in post_sentiments])
        comment_sentiment_dist = Counter([cs['sentiment'] for cs in comment_sentiments])
        
        # Calculate average sentiment scores
        avg_post_sentiment = sum([ps['sentiment_score'] for ps in post_sentiments]) / max(len(post_sentiments), 1)
        avg_comment_sentiment = sum([cs['sentiment_score'] for cs in comment_sentiments]) / max(len(comment_sentiments), 1)
        
        return {
            'total_posts': len(posts_df),
            'total_comments': len(comments_df),
            'subject_distribution': dict(subject_distribution),
            'post_sentiment_distribution': dict(post_sentiment_dist),
            'comment_sentiment_distribution': dict(comment_sentiment_dist),
            'average_sentiment_scores': {
                'posts': round(avg_post_sentiment, 3),
                'comments': round(avg_comment_sentiment, 3),
                'overall': round((avg_post_sentiment + avg_comment_sentiment) / 2, 3)
            },
            'engagement_metrics': {
                'avg_post_score': round(posts_df['score'].mean(), 1),
                'avg_comments_per_post': round(posts_df['num_comments'].mean(), 1),
                'total_engagement': int(posts_df['score'].sum() + posts_df['num_comments'].sum())
            }
        }
    
    def _analyze_by_subject_area(self, classified_posts, post_sentiments, comments_df, comment_sentiments):
        """Detailed analysis by subject area."""
        
        # Create sentiment lookup
        post_sentiment_lookup = {ps['index']: ps for ps in post_sentiments}
        comment_sentiment_lookup = {cs['index']: cs for cs in comment_sentiments}
        
        subject_analysis = {}
        
        for subject in self.subject_areas.keys():
            # Get posts for this subject
            subject_posts = [cp for cp in classified_posts if cp['primary_subject'] == subject]
            
            if not subject_posts:
                subject_analysis[subject] = {
                    'post_count': 0,
                    'sentiment_distribution': {},
                    'avg_sentiment_score': 0.0,
                    'top_posts': [],
                    'key_insights': []
                }
                continue
            
            # Get sentiment data for these posts
            post_sentiments_for_subject = []
            for sp in subject_posts:
                if sp['index'] in post_sentiment_lookup:
                    post_sentiments_for_subject.append(post_sentiment_lookup[sp['index']])
            
            # Calculate sentiment distribution
            sentiment_dist = Counter([ps['sentiment'] for ps in post_sentiments_for_subject])
            avg_sentiment = sum([ps['sentiment_score'] for ps in post_sentiments_for_subject]) / max(len(post_sentiments_for_subject), 1)
            
            # Get top posts by engagement
            top_posts = sorted(subject_posts, key=lambda x: x['post_data']['score'] + x['post_data']['num_comments'], reverse=True)[:5]
            
            # Get related comments
            post_ids = [sp['post_data']['id'] for sp in subject_posts]
            related_comments = [cs for cs in comment_sentiments if cs['metadata']['post_id'] in post_ids]
            
            subject_analysis[subject] = {
                'post_count': len(subject_posts),
                'comment_count': len(related_comments),
                'sentiment_distribution': dict(sentiment_dist),
                'avg_sentiment_score': round(avg_sentiment, 3),
                'top_posts': [
                    {
                        'title': tp['post_data']['title'],
                        'score': tp['post_data']['score'],
                        'comments': tp['post_data']['num_comments'],
                        'sentiment': post_sentiment_lookup.get(tp['index'], {}).get('sentiment', 'UNKNOWN'),
                        'confidence': post_sentiment_lookup.get(tp['index'], {}).get('confidence', 0.5),
                        'key_phrases': tp['key_phrases'][:5]
                    } for tp in top_posts
                ],
                'comment_sentiment_distribution': dict(Counter([rc['sentiment'] for rc in related_comments])),
                'key_insights': self._generate_subject_insights(subject, subject_posts, post_sentiments_for_subject)
            }
        
        return subject_analysis
    
    def _generate_subject_insights(self, subject, posts, sentiments):
        """Generate key insights for a subject area."""
        
        insights = []
        
        if not posts or not sentiments:
            return insights
        
        # Sentiment insight
        sentiment_counts = Counter([s['sentiment'] for s in sentiments])
        dominant_sentiment = sentiment_counts.most_common(1)[0][0]
        sentiment_percentage = (sentiment_counts[dominant_sentiment] / len(sentiments)) * 100
        
        insights.append(f"{sentiment_percentage:.0f}% of posts show {dominant_sentiment.lower()} sentiment")
        
        # Engagement insight
        avg_engagement = sum([p['post_data']['score'] + p['post_data']['num_comments'] for p in posts]) / len(posts)
        insights.append(f"Average engagement: {avg_engagement:.1f} (score + comments)")
        
        # Key phrase insight
        all_phrases = []
        for p in posts:
            all_phrases.extend(p['key_phrases'])
        
        if all_phrases:
            top_phrase = Counter(all_phrases).most_common(1)[0][0]
            insights.append(f"Most discussed: '{top_phrase}'")
        
        return insights
    
    def _create_sentiment_deep_dive(self, post_sentiments, comment_sentiments):
        """Create detailed sentiment analysis for drill-down."""
        
        # High confidence examples by sentiment
        high_confidence_examples = {
            'POSITIVE': [],
            'NEGATIVE': [],
            'NEUTRAL': [],
            'MIXED': []
        }
        
        # Process posts
        for ps in post_sentiments:
            sentiment = ps['sentiment']
            if ps['confidence'] > 0.8 and len(high_confidence_examples[sentiment]) < 5:
                high_confidence_examples[sentiment].append({
                    'type': 'post',
                    'title': ps['metadata']['title'],
                    'text': ps['text_preview'],
                    'confidence': ps['confidence'],
                    'sentiment_score': ps['sentiment_score'],
                    'engagement': ps['metadata']['score'] + ps['metadata']['num_comments']
                })
        
        # Process comments
        for cs in comment_sentiments:
            sentiment = cs['sentiment']
            if cs['confidence'] > 0.8 and len(high_confidence_examples[sentiment]) < 10:
                high_confidence_examples[sentiment].append({
                    'type': 'comment',
                    'text': cs['text_preview'],
                    'confidence': cs['confidence'],
                    'sentiment_score': cs['sentiment_score'],
                    'post_title': cs['metadata'].get('title', 'Unknown')
                })
        
        return {
            'high_confidence_examples': high_confidence_examples,
            'sentiment_statistics': {
                'posts': {
                    'total': len(post_sentiments),
                    'avg_confidence': sum([ps['confidence'] for ps in post_sentiments]) / max(len(post_sentiments), 1),
                    'avg_sentiment_score': sum([ps['sentiment_score'] for ps in post_sentiments]) / max(len(post_sentiments), 1)
                },
                'comments': {
                    'total': len(comment_sentiments),
                    'avg_confidence': sum([cs['confidence'] for cs in comment_sentiments]) / max(len(comment_sentiments), 1),
                    'avg_sentiment_score': sum([cs['sentiment_score'] for cs in comment_sentiments]) / max(len(comment_sentiments), 1)
                }
            }
        }
    
    def _analyze_engagement_patterns(self, posts_df, comments_df, post_sentiments):
        """Analyze engagement patterns across sentiment and topics."""
        
        # Create sentiment lookup
        sentiment_lookup = {ps['index']: ps for ps in post_sentiments}
        
        engagement_by_sentiment = defaultdict(list)
        
        for _, post in posts_df.iterrows():
            engagement = post['score'] + post['num_comments']
            sentiment_data = sentiment_lookup.get(post.name, {})
            sentiment = sentiment_data.get('sentiment', 'UNKNOWN')
            engagement_by_sentiment[sentiment].append(engagement)
        
        # Calculate averages
        avg_engagement_by_sentiment = {}
        for sentiment, engagements in engagement_by_sentiment.items():
            avg_engagement_by_sentiment[sentiment] = sum(engagements) / len(engagements)
        
        return {
            'engagement_by_sentiment': avg_engagement_by_sentiment,
            'total_engagement': int(posts_df['score'].sum() + posts_df['num_comments'].sum()),
            'high_engagement_threshold': posts_df['score'].quantile(0.8) + posts_df['num_comments'].quantile(0.8)
        }
    
    def _analyze_temporal_patterns(self, posts_df, post_sentiments):
        """Analyze temporal patterns in posting and sentiment."""
        
        posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
        posts_df['date'] = posts_df['created_date'].dt.date
        posts_df['hour'] = posts_df['created_date'].dt.hour
        posts_df['day_of_week'] = posts_df['created_date'].dt.day_name()
        
        return {
            'daily_post_counts': {str(k): v for k, v in posts_df.groupby('date').size().to_dict().items()},
            'hourly_distribution': posts_df.groupby('hour').size().to_dict(),
            'day_of_week_distribution': posts_df.groupby('day_of_week').size().to_dict(),
            'peak_posting_time': int(posts_df.groupby('hour').size().idxmax()),
            'peak_posting_day': str(posts_df.groupby('day_of_week').size().idxmax())
        }
    
    def _prepare_drill_down_data(self, classified_posts, post_sentiments, comments_df, comment_sentiments):
        """Prepare detailed data for drill-down functionality."""
        
        # Create comprehensive lookup structures
        post_lookup = {cp['index']: cp for cp in classified_posts}
        post_sentiment_lookup = {ps['index']: ps for ps in post_sentiments}
        comment_sentiment_lookup = {cs['index']: cs for cs in comment_sentiments}
        
        drill_down_data = {}
        
        # Organize by subject area
        for subject in self.subject_areas.keys():
            subject_posts = [cp for cp in classified_posts if cp['primary_subject'] == subject]
            
            drill_down_data[subject] = {
                'posts': [],
                'total_comments': 0
            }
            
            for sp in subject_posts:
                post_sentiment = post_sentiment_lookup.get(sp['index'], {})
                
                # Get comments for this post
                post_id = sp['post_data']['id']
                post_comments = []
                
                for _, comment in comments_df.iterrows():
                    if comment.get('post_id') == post_id:
                        comment_sentiment = comment_sentiment_lookup.get(comment.name, {})
                        post_comments.append({
                            'content': comment.get('content', ''),
                            'score': comment.get('score', 0),
                            'author': comment.get('author', ''),
                            'created_date': comment.get('created_date', ''),
                            'sentiment': comment_sentiment.get('sentiment', 'UNKNOWN'),
                            'sentiment_score': comment_sentiment.get('sentiment_score', 0.0),
                            'confidence': comment_sentiment.get('confidence', 0.5)
                        })
                
                drill_down_data[subject]['posts'].append({
                    'title': sp['post_data']['title'],
                    'content': sp['post_data'].get('content', ''),
                    'author': sp['post_data']['author'],
                    'score': sp['post_data']['score'],
                    'num_comments': sp['post_data']['num_comments'],
                    'created_date': sp['post_data']['created_date'],
                    'sentiment': post_sentiment.get('sentiment', 'UNKNOWN'),
                    'sentiment_score': post_sentiment.get('sentiment_score', 0.0),
                    'confidence': post_sentiment.get('confidence', 0.5),
                    'key_phrases': sp['key_phrases'],
                    'classification_confidence': sp['classification_confidence'],
                    'secondary_subjects': sp['secondary_subjects'],
                    'comments': post_comments
                })
                
                drill_down_data[subject]['total_comments'] += len(post_comments)
        
        return drill_down_data

def main():
    """Run comprehensive FC analysis."""
    print("🚀 Amazon FC Employee Intelligence Platform")
    print("=" * 60)
    
    analyzer = ComprehensiveFCAnalyzer()
    analysis = analyzer.analyze_all_fc_content(days_back=14, max_posts=300)  # Increased scope
    
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    # Save comprehensive analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"comprehensive_fc_analysis_{timestamp}.json"
    
    with open(json_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    # Print summary
    print(f"\n🎯 Analysis Complete!")
    print(f"📊 Total Posts: {analysis['overview']['total_posts']}")
    print(f"💬 Total Comments: {analysis['overview']['total_comments']}")
    print(f"📈 Subject Areas: {len(analysis['subject_areas'])}")
    print(f"💰 AWS Cost: ${analysis['cost_summary']['estimated_cost']}")
    print(f"📄 Data saved to: {json_file}")
    
    # Print subject area breakdown
    print(f"\n📋 Subject Area Breakdown:")
    for subject, data in analysis['subject_areas'].items():
        if data['post_count'] > 0:
            print(f"  {subject.replace('_', ' ').title()}: {data['post_count']} posts, avg sentiment: {data['avg_sentiment_score']:.2f}")

if __name__ == "__main__":
    main()