#!/usr/bin/env python3
"""
Unified Data Pipeline: Single Source of Truth
API Calls → Database → All Reports & Dashboards
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import requests
from pathlib import Path

class UnifiedDataManager:
    """Single source of truth for all Amazon FC intelligence data."""
    
    def __init__(self, db_path="unified_fc_intelligence.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize unified database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Posts table with sentiment analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                author TEXT,
                subreddit TEXT,
                score INTEGER DEFAULT 0,
                num_comments INTEGER DEFAULT 0,
                created_utc TIMESTAMP,
                url TEXT,
                permalink TEXT,
                
                -- Classification fields
                subject_area TEXT,
                keywords TEXT, -- JSON array
                
                -- Sentiment analysis
                sentiment TEXT, -- POSITIVE, NEGATIVE, NEUTRAL, MIXED
                sentiment_score REAL, -- -1.0 to 1.0
                confidence REAL, -- 0.0 to 1.0
                
                -- Metadata
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analyzed_at TIMESTAMP,
                
                -- Flags
                is_wage_related BOOLEAN DEFAULT 0,
                is_recent_announcement BOOLEAN DEFAULT 0
            )
        """)
        
        # Comments table with sentiment analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                post_id TEXT,
                parent_id TEXT,
                body TEXT,
                author TEXT,
                score INTEGER DEFAULT 0,
                created_utc TIMESTAMP,
                
                -- Sentiment analysis
                sentiment TEXT,
                sentiment_score REAL,
                confidence REAL,
                
                -- Metadata
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analyzed_at TIMESTAMP,
                
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """)
        
        # Data collection log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_type TEXT, -- 'posts', 'comments', 'sentiment_analysis'
                status TEXT, -- 'success', 'error', 'partial'
                records_processed INTEGER,
                error_message TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                metadata TEXT -- JSON
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_reddit_data(self, subreddit="AmazonFC", limit=100, time_filter="day"):
        """Collect fresh data from Reddit API."""
        
        log_id = self._start_collection_log("posts")
        
        try:
            # Use existing Reddit collector
            from reddit_data_collector.services.reddit_client import RedditClient
            from reddit_data_collector.services.post_collector import PostCollector
            from reddit_data_collector.services.comment_collector import CommentCollector
            
            # Initialize collectors
            reddit_client = RedditClient()
            post_collector = PostCollector(reddit_client)
            comment_collector = CommentCollector(reddit_client)
            
            # Collect posts
            posts = post_collector.collect_posts(
                subreddit=subreddit,
                limit=limit,
                time_filter=time_filter
            )
            
            # Store posts in database
            posts_stored = 0
            comments_stored = 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for post in posts:
                # Store post
                cursor.execute("""
                    INSERT OR REPLACE INTO posts 
                    (id, title, content, author, subreddit, score, num_comments, 
                     created_utc, url, permalink, collected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post.get('id'),
                    post.get('title'),
                    post.get('selftext') or post.get('content'),
                    post.get('author'),
                    post.get('subreddit'),
                    post.get('score', 0),
                    post.get('num_comments', 0),
                    datetime.fromtimestamp(post.get('created_utc', 0)),
                    post.get('url'),
                    post.get('permalink'),
                    datetime.now()
                ))
                posts_stored += 1
                
                # Collect and store comments for this post
                try:
                    comments = comment_collector.collect_comments(post.get('id'), limit=50)
                    
                    for comment in comments:
                        cursor.execute("""
                            INSERT OR REPLACE INTO comments
                            (id, post_id, parent_id, body, author, score, 
                             created_utc, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            comment.get('id'),
                            post.get('id'),
                            comment.get('parent_id'),
                            comment.get('body'),
                            comment.get('author'),
                            comment.get('score', 0),
                            datetime.fromtimestamp(comment.get('created_utc', 0)),
                            datetime.now()
                        ))
                        comments_stored += 1
                
                except Exception as e:
                    print(f"Error collecting comments for post {post.get('id')}: {e}")
            
            conn.commit()
            conn.close()
            
            self._complete_collection_log(log_id, "success", posts_stored + comments_stored)
            
            return {
                "status": "success",
                "posts_collected": posts_stored,
                "comments_collected": comments_stored,
                "total_records": posts_stored + comments_stored
            }
            
        except Exception as e:
            self._complete_collection_log(log_id, "error", 0, str(e))
            return {
                "status": "error",
                "error": str(e),
                "posts_collected": 0,
                "comments_collected": 0
            }
    
    def analyze_sentiment(self):
        """Analyze sentiment for all unanalyzed posts and comments."""
        
        log_id = self._start_collection_log("sentiment_analysis")
        
        try:
            from reddit_data_collector.services.aws_sentiment_analyzer import AWSSentimentAnalyzer
            
            analyzer = AWSSentimentAnalyzer()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Analyze posts without sentiment
            cursor.execute("""
                SELECT id, title, content FROM posts 
                WHERE analyzed_at IS NULL OR sentiment IS NULL
            """)
            
            posts_analyzed = 0
            
            for row in cursor.fetchall():
                post_id, title, content = row
                text = f"{title} {content or ''}"
                
                try:
                    result = analyzer.analyze_sentiment(text)
                    
                    cursor.execute("""
                        UPDATE posts SET 
                        sentiment = ?, sentiment_score = ?, confidence = ?, analyzed_at = ?
                        WHERE id = ?
                    """, (
                        result.get('sentiment'),
                        result.get('sentiment_score'),
                        result.get('confidence'),
                        datetime.now(),
                        post_id
                    ))
                    posts_analyzed += 1
                    
                except Exception as e:
                    print(f"Error analyzing post {post_id}: {e}")
            
            # Analyze comments without sentiment
            cursor.execute("""
                SELECT id, body FROM comments 
                WHERE analyzed_at IS NULL OR sentiment IS NULL
            """)
            
            comments_analyzed = 0
            
            for row in cursor.fetchall():
                comment_id, body = row
                
                if not body or len(body.strip()) < 10:
                    continue
                
                try:
                    result = analyzer.analyze_sentiment(body)
                    
                    cursor.execute("""
                        UPDATE comments SET 
                        sentiment = ?, sentiment_score = ?, confidence = ?, analyzed_at = ?
                        WHERE id = ?
                    """, (
                        result.get('sentiment'),
                        result.get('sentiment_score'),
                        result.get('confidence'),
                        datetime.now(),
                        comment_id
                    ))
                    comments_analyzed += 1
                    
                except Exception as e:
                    print(f"Error analyzing comment {comment_id}: {e}")
            
            conn.commit()
            conn.close()
            
            total_analyzed = posts_analyzed + comments_analyzed
            self._complete_collection_log(log_id, "success", total_analyzed)
            
            return {
                "status": "success",
                "posts_analyzed": posts_analyzed,
                "comments_analyzed": comments_analyzed,
                "total_analyzed": total_analyzed
            }
            
        except Exception as e:
            self._complete_collection_log(log_id, "error", 0, str(e))
            return {"status": "error", "error": str(e)}
    
    def classify_posts(self):
        """Classify posts into subject areas and identify wage-related content."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Subject classification keywords
        subject_keywords = {
            'compensation': ['pay', 'wage', 'salary', 'raise', 'money', 'dollar', 'cent', 'bonus', 'overtime', 'pto', 'benefits'],
            'management': ['manager', 'supervisor', 'boss', 'leadership', 'am', 'pa', 'hr', 'fired', 'write up', 'coaching'],
            'working_conditions': ['safety', 'break', 'bathroom', 'heat', 'cold', 'injury', 'hurt', 'dangerous', 'unsafe'],
            'schedule_time': ['schedule', 'shift', 'hours', 'overtime', 'met', 'mandatory', 'vto', 'vet', 'time off'],
            'general_experience': ['amazon', 'fc', 'warehouse', 'work', 'job', 'quit', 'leave', 'stay', 'experience'],
            'technology_systems': ['scanner', 'computer', 'system', 'app', 'technology', 'robot', 'automation'],
            'career_development': ['promotion', 'career', 'learning', 'training', 'development', 'advance']
        }
        
        # Wage announcement keywords
        wage_announcement_keywords = [
            '2025 pay increase', 'wage announcement', 'pay raise', 'salary increase',
            'new wage', 'wage structure', 'compensation change', 'pay adjustment'
        ]
        
        # Get all posts without classification
        cursor.execute("""
            SELECT id, title, content FROM posts 
            WHERE subject_area IS NULL
        """)
        
        posts_classified = 0
        
        for row in cursor.fetchall():
            post_id, title, content = row
            text = f"{title} {content or ''}".lower()
            
            # Classify subject area
            subject_area = None
            matched_keywords = []
            
            for subject, keywords in subject_keywords.items():
                matches = [kw for kw in keywords if kw in text]
                if matches:
                    if not subject_area or len(matches) > len(matched_keywords):
                        subject_area = subject
                        matched_keywords = matches
            
            # Check if wage-related
            is_wage_related = any(kw in text for kw in subject_keywords['compensation'])
            
            # Check if recent announcement related
            is_recent_announcement = any(kw in text for kw in wage_announcement_keywords)
            
            # Update post
            cursor.execute("""
                UPDATE posts SET 
                subject_area = ?, keywords = ?, is_wage_related = ?, is_recent_announcement = ?
                WHERE id = ?
            """, (
                subject_area,
                json.dumps(matched_keywords),
                is_wage_related,
                is_recent_announcement,
                post_id
            ))
            
            posts_classified += 1
        
        conn.commit()
        conn.close()
        
        return {"posts_classified": posts_classified}
    
    def get_dashboard_data(self):
        """Get unified data for dashboard display."""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute("SELECT COUNT(*) as total_posts FROM posts")
        total_posts = cursor.fetchone()['total_posts']
        
        cursor.execute("SELECT COUNT(*) as total_comments FROM comments")
        total_comments = cursor.fetchone()['total_comments']
        
        # Subject distribution
        cursor.execute("""
            SELECT subject_area, COUNT(*) as count 
            FROM posts 
            WHERE subject_area IS NOT NULL 
            GROUP BY subject_area
        """)
        subject_distribution = {row['subject_area']: row['count'] for row in cursor.fetchall()}
        
        # Sentiment distribution
        cursor.execute("""
            SELECT sentiment, COUNT(*) as count 
            FROM posts 
            WHERE sentiment IS NOT NULL 
            GROUP BY sentiment
        """)
        post_sentiment_dist = {row['sentiment']: row['count'] for row in cursor.fetchall()}
        
        # Subject areas with detailed data
        subject_areas = {}
        
        for subject in subject_distribution.keys():
            # Get posts for this subject
            cursor.execute("""
                SELECT id, title, content, score, num_comments, sentiment, 
                       sentiment_score, confidence, created_utc, is_wage_related, is_recent_announcement
                FROM posts 
                WHERE subject_area = ? 
                ORDER BY score DESC
            """, (subject,))
            
            posts = []
            for row in cursor.fetchall():
                post_data = dict(row)
                
                # Get comments for this post
                cursor.execute("""
                    SELECT body, score, sentiment, sentiment_score, confidence
                    FROM comments 
                    WHERE post_id = ?
                    ORDER BY score DESC
                    LIMIT 10
                """, (post_data['id'],))
                
                post_data['comments'] = [dict(comment_row) for comment_row in cursor.fetchall()]
                posts.append(post_data)
            
            # Calculate subject statistics
            cursor.execute("""
                SELECT sentiment, COUNT(*) as count 
                FROM posts 
                WHERE subject_area = ? AND sentiment IS NOT NULL 
                GROUP BY sentiment
            """, (subject,))
            
            sentiment_dist = {row['sentiment']: row['count'] for row in cursor.fetchall()}
            
            cursor.execute("""
                SELECT AVG(sentiment_score) as avg_score 
                FROM posts 
                WHERE subject_area = ? AND sentiment_score IS NOT NULL
            """, (subject,))
            
            avg_sentiment = cursor.fetchone()['avg_score'] or 0
            
            subject_areas[subject] = {
                'post_count': len(posts),
                'comment_count': sum(len(p['comments']) for p in posts),
                'sentiment_distribution': sentiment_dist,
                'avg_sentiment_score': avg_sentiment,
                'top_posts': posts
            }
        
        conn.close()
        
        return {
            'overview': {
                'total_posts': total_posts,
                'total_comments': total_comments,
                'subject_distribution': subject_distribution,
                'post_sentiment_distribution': post_sentiment_dist,
                'average_sentiment_scores': {
                    'overall': sum(sa['avg_sentiment_score'] * sa['post_count'] for sa in subject_areas.values()) / total_posts if total_posts > 0 else 0
                }
            },
            'subject_areas': subject_areas
        }
    
    def get_wage_announcement_data(self, hours_back=24):
        """Get data specifically about recent wage announcements."""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Get recent wage-related posts
        cursor.execute("""
            SELECT * FROM posts 
            WHERE (is_wage_related = 1 OR is_recent_announcement = 1)
            AND created_utc >= ?
            ORDER BY created_utc DESC
        """, (cutoff_time,))
        
        recent_posts = []
        for row in cursor.fetchall():
            post_data = dict(row)
            
            # Get comments
            cursor.execute("""
                SELECT * FROM comments 
                WHERE post_id = ?
                ORDER BY score DESC
                LIMIT 10
            """, (post_data['id'],))
            
            post_data['comments'] = [dict(comment_row) for comment_row in cursor.fetchall()]
            recent_posts.append(post_data)
        
        conn.close()
        
        return recent_posts
    
    def _start_collection_log(self, collection_type):
        """Start a collection log entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO collection_log (collection_type, status, started_at)
            VALUES (?, 'running', ?)
        """, (collection_type, datetime.now()))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def _complete_collection_log(self, log_id, status, records_processed, error_message=None):
        """Complete a collection log entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE collection_log SET 
            status = ?, records_processed = ?, error_message = ?, completed_at = ?
            WHERE id = ?
        """, (status, records_processed, error_message, datetime.now(), log_id))
        
        conn.commit()
        conn.close()

def run_full_data_pipeline():
    """Run the complete data pipeline: Collect → Analyze → Classify."""
    
    print("🚀 Starting Unified Data Pipeline...")
    
    # Initialize data manager
    dm = UnifiedDataManager()
    
    # Step 1: Collect fresh Reddit data
    print("📡 Collecting Reddit data...")
    collection_result = dm.collect_reddit_data(limit=200, time_filter="week")
    print(f"✅ Collected: {collection_result['posts_collected']} posts, {collection_result['comments_collected']} comments")
    
    # Step 2: Analyze sentiment
    print("🧠 Analyzing sentiment...")
    sentiment_result = dm.analyze_sentiment()
    print(f"✅ Analyzed: {sentiment_result['posts_analyzed']} posts, {sentiment_result['comments_analyzed']} comments")
    
    # Step 3: Classify posts
    print("🏷️ Classifying posts...")
    classification_result = dm.classify_posts()
    print(f"✅ Classified: {classification_result['posts_classified']} posts")
    
    # Step 4: Generate summary
    print("📊 Generating data summary...")
    dashboard_data = dm.get_dashboard_data()
    
    print(f"""
    📈 Pipeline Complete!
    
    Total Posts: {dashboard_data['overview']['total_posts']}
    Total Comments: {dashboard_data['overview']['total_comments']}
    Subject Areas: {len(dashboard_data['subject_areas'])}
    
    Subject Distribution:
    """)
    
    for subject, count in dashboard_data['overview']['subject_distribution'].items():
        print(f"  - {subject.replace('_', ' ').title()}: {count} posts")
    
    return dashboard_data

if __name__ == "__main__":
    # Run the full pipeline
    data = run_full_data_pipeline()
    
    # Save unified data for dashboard use
    with open('unified_dashboard_data.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print("\n✅ Unified data saved to: unified_dashboard_data.json")
    print("🎯 All reports and dashboards will now use this single source of truth!")