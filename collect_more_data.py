#!/usr/bin/env python3
"""
Collect more comprehensive data from amazonfc subreddit
"""

import os
import sys
import praw
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('reddit-data-collector/.env')

def collect_comprehensive_data():
    """Collect comprehensive data from amazonfc."""
    
    print("🚀 Collecting comprehensive amazonfc data...")
    
    # Initialize Reddit client
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    # Connect to database
    db_path = 'reddit_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            author TEXT,
            created_date TIMESTAMP,
            score INTEGER,
            num_comments INTEGER,
            url TEXT,
            subreddit TEXT,
            is_self BOOLEAN,
            permalink TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            post_id TEXT,
            parent_comment_id TEXT,
            content TEXT,
            author TEXT,
            created_date TIMESTAMP,
            score INTEGER,
            depth INTEGER,
            permalink TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    
    # Get amazonfc subreddit
    subreddit = reddit.subreddit('amazonfc')
    
    posts_collected = 0
    comments_collected = 0
    
    print("📊 Collecting from multiple time periods...")
    
    # Collect from different time periods and sorting methods
    collection_methods = [
        ('hot', 200),
        ('new', 200), 
        ('top', 100, 'week'),
        ('top', 100, 'month')
    ]
    
    for method_info in collection_methods:
        method = method_info[0]
        limit = method_info[1]
        time_filter = method_info[2] if len(method_info) > 2 else None
        
        print(f"🔍 Collecting {method} posts (limit: {limit})")
        
        try:
            if method == 'hot':
                posts = subreddit.hot(limit=limit)
            elif method == 'new':
                posts = subreddit.new(limit=limit)
            elif method == 'top':
                posts = subreddit.top(limit=limit, time_filter=time_filter)
            
            for post in posts:
                try:
                    # Store post
                    cursor.execute('''
                        INSERT OR REPLACE INTO posts 
                        (id, title, content, author, created_date, score, num_comments, url, subreddit, is_self, permalink)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post.id,
                        post.title,
                        post.selftext,
                        str(post.author) if post.author else None,
                        datetime.fromtimestamp(post.created_utc),
                        post.score,
                        post.num_comments,
                        post.url,
                        'amazonfc',
                        post.is_self,
                        post.permalink
                    ))
                    
                    posts_collected += 1
                    
                    # Collect some comments for each post
                    try:
                        post.comments.replace_more(limit=0)
                        comment_count = 0
                        
                        for comment in post.comments.list()[:10]:  # Limit to 10 comments per post
                            if hasattr(comment, 'body') and comment.body != '[deleted]':
                                cursor.execute('''
                                    INSERT OR REPLACE INTO comments 
                                    (id, post_id, parent_comment_id, content, author, created_date, score, depth, permalink)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    comment.id,
                                    post.id,
                                    comment.parent_id if hasattr(comment, 'parent_id') else None,
                                    comment.body,
                                    str(comment.author) if comment.author else None,
                                    datetime.fromtimestamp(comment.created_utc),
                                    comment.score,
                                    0,
                                    comment.permalink if hasattr(comment, 'permalink') else None
                                ))
                                
                                comment_count += 1
                                comments_collected += 1
                        
                    except Exception as e:
                        print(f"⚠️ Error collecting comments for post {post.id}: {e}")
                    
                    if posts_collected % 50 == 0:
                        print(f"📈 Progress: {posts_collected} posts, {comments_collected} comments")
                        conn.commit()  # Commit periodically
                
                except Exception as e:
                    print(f"⚠️ Error processing post: {e}")
                    continue
        
        except Exception as e:
            print(f"⚠️ Error with {method} collection: {e}")
            continue
    
    # Final commit
    conn.commit()
    conn.close()
    
    print(f"✅ Data collection complete!")
    print(f"📊 Total posts collected: {posts_collected}")
    print(f"💬 Total comments collected: {comments_collected}")
    
    return posts_collected, comments_collected

if __name__ == "__main__":
    collect_comprehensive_data()