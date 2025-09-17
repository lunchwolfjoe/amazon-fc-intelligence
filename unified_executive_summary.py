#!/usr/bin/env python3
"""
Unified Executive Summary Generator
Uses same database as dashboard for consistent data
"""

from unified_data_pipeline import UnifiedDataManager
from datetime import datetime, timedelta
import json

def generate_unified_wage_analysis():
    """Generate executive summary using unified database."""
    
    dm = UnifiedDataManager()
    
    # Get recent wage-related posts (last 24 hours)
    recent_posts = dm.get_wage_announcement_data(hours_back=24)
    
    # Get overall dashboard data for context
    dashboard_data = dm.get_dashboard_data()
    
    # Calculate sentiment breakdown for recent wage posts
    if recent_posts:
        sentiment_counts = {}
        for post in recent_posts:
            sentiment = post.get('sentiment', 'NEUTRAL')
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        total_recent = len(recent_posts)
        sentiment_percentages = {
            k: round((v / total_recent) * 100) for k, v in sentiment_counts.items()
        } if total_recent > 0 else {}
    else:
        sentiment_percentages = {}
        total_recent = 0
    
    # Get compensation subject data for broader context
    compensation_data = dashboard_data['subject_areas'].get('compensation', {})
    
    return {
        "analysis_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "time_period": "Last 24 Hours",
        "total_posts_analyzed": total_recent,
        "total_comments_analyzed": sum(len(p.get('comments', [])) for p in recent_posts),
        "recent_posts": recent_posts,
        "sentiment_breakdown": sentiment_percentages,
        "compensation_context": compensation_data,
        "overall_data": dashboard_data
    }

def create_unified_html_report():
    """Create executive summary using unified data source."""
    
    data = generate_unified_wage_analysis()
    
    # Determine overall sentiment and risk
    sentiment_breakdown = data['sentiment_breakdown']
    negative_pct = sentiment_breakdown.get('NEGATIVE', 0)
    positive_pct = sentiment_breakdown.get('POSITIVE', 0)
    
    if negative_pct > 50:
        overall_sentiment = "Predominantly Negative"
        risk_level = "HIGH"
    elif negative_pct > 30:
        overall_sentiment = "Mixed with Negative Lean"
        risk_level = "MEDIUM-HIGH"
    elif positive_pct > 50:
        overall_sentiment = "Predominantly Positive"
        risk_level = "LOW"
    else:
        overall_sentiment = "Mixed/Neutral"
        risk_level = "MEDIUM"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Executive Summary: Unified Wage Analysis</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .header {{
                text-align: center;
                border-bottom: 3px solid #FF9900;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #232F3E;
                font-size: 2.5rem;
                margin: 0;
                font-weight: 700;
            }}
            
            .data-source {{
                background: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                text-align: center;
            }}
            
            .executive-summary {{
                background: linear-gradient(135deg, #232F3E 0%, #FF9900 100%);
                color: white;
                padding: 25px;
                border-radius: 8px;
                margin: 30px 0;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            
            .metric-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #FF9900;
                text-align: center;
            }}
            
            .metric-value {{
                font-size: 2rem;
                font-weight: bold;
                color: #232F3E;
                margin: 10px 0;
            }}
            
            .risk-high {{ color: #dc3545; font-weight: bold; }}
            .risk-medium {{ color: #fd7e14; font-weight: bold; }}
            .risk-low {{ color: #28a745; font-weight: bold; }}
            
            .post-card {{
                background: #fff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            
            .no-data {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 25px;
                margin: 30px 0;
                text-align: center;
            }}
            
            .compensation-context {{
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Executive Summary</h1>
                <div style="font-size: 1.2rem; color: #666; margin-top: 10px;">
                    Unified Wage Announcement Analysis
                </div>
                <div style="margin-top: 15px; color: #666; font-size: 1rem;">
                    Analysis Period: {data['time_period']} | Generated: {data['analysis_date']}
                </div>
            </div>
            
            <div class="data-source">
                <h3 style="margin-top: 0; color: #1976d2;">📊 Single Source of Truth</h3>
                <p style="margin-bottom: 0;">This report uses the same unified database as the dashboard, ensuring consistent data across all reports and analytics.</p>
            </div>
            
            <div class="executive-summary">
                <h2>🚨 Executive Alert</h2>
                <p><strong>Overall Sentiment:</strong> {overall_sentiment}</p>
                <p><strong>Risk Level:</strong> <span class="risk-{risk_level.lower().replace('-', '')}">{risk_level}</span></p>
                <p><strong>Data Source:</strong> Unified database with real API-collected data</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">Recent Posts</div>
                    <div class="metric-value">{data['total_posts_analyzed']}</div>
                    <div style="font-size: 0.85rem; color: #495057;">Last 24 hours</div>
                </div>
                <div class="metric-card">
                    <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">Comments Analyzed</div>
                    <div class="metric-value">{data['total_comments_analyzed']}</div>
                    <div style="font-size: 0.85rem; color: #495057;">Associated discussions</div>
                </div>
    """
    
    # Add sentiment metrics if we have data
    if sentiment_breakdown:
        for sentiment, percentage in sentiment_breakdown.items():
            color = "#dc3545" if sentiment == "NEGATIVE" else "#28a745" if sentiment == "POSITIVE" else "#6c757d"
            html_content += f"""
                <div class="metric-card">
                    <div style="color: #6c757d; font-size: 0.9rem; text-transform: uppercase;">{sentiment.title()} Sentiment</div>
                    <div class="metric-value" style="color: {color};">{percentage}%</div>
                    <div style="font-size: 0.85rem; color: #495057;">Of recent posts</div>
                </div>
            """
    
    html_content += """
            </div>
    """
    
    # Show recent posts if available
    if data['recent_posts']:
        html_content += """
            <h2>📊 Recent Wage-Related Posts</h2>
            <p>The following posts were collected from our unified database and represent actual employee discussions:</p>
        """
        
        for i, post in enumerate(data['recent_posts'][:5], 1):
            sentiment = post.get('sentiment', 'NEUTRAL')
            sentiment_class = f"sentiment-{sentiment.lower()}"
            created_time = post.get('created_utc', 'Unknown time')
            
            html_content += f"""
            <div class="post-card">
                <h3>#{i}: {post.get('title', 'Untitled Post')}</h3>
                <div style="margin: 10px 0; color: #666; font-size: 0.9rem;">
                    Posted: {created_time} | Score: {post.get('score', 0)} | Comments: {post.get('num_comments', 0)}
                    | Sentiment: <strong>{sentiment}</strong>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #FF9900; margin: 15px 0; font-style: italic;">
                    "{post.get('content', 'No content available')[:300]}{'...' if len(post.get('content', '')) > 300 else ''}"
                </div>
                
                <h4>Top Comments:</h4>
            """
            
            comments = post.get('comments', [])
            if comments:
                for comment in comments[:3]:
                    comment_sentiment = comment.get('sentiment', 'NEUTRAL')
                    html_content += f"""
                    <div style="background: #f1f3f4; padding: 12px; margin: 10px 0; border-radius: 6px; border-left: 3px solid #6c757d;">
                        "{comment.get('body', 'No content')[:200]}{'...' if len(comment.get('body', '')) > 200 else ''}"
                        <div style="font-size: 0.8rem; color: #666; margin-top: 8px;">
                            Score: {comment.get('score', 0)} | Sentiment: {comment_sentiment}
                        </div>
                    </div>
                    """
            else:
                html_content += "<p>No comments available for this post.</p>"
            
            html_content += "</div>"
    
    else:
        # No recent wage posts found
        html_content += """
            <div class="no-data">
                <h3>📊 No Recent Wage Announcement Posts Found</h3>
                <p>Our unified database shows no posts specifically about wage announcements in the last 24 hours.</p>
                <p>This could indicate:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>No recent wage announcements have been made</li>
                    <li>Employee discussions are happening in other channels</li>
                    <li>The announcement is too recent for significant discussion</li>
                    <li>Data collection may need to be expanded to other timeframes</li>
                </ul>
            </div>
        """
    
    # Add compensation context from broader dataset
    compensation_data = data.get('compensation_context', {})
    if compensation_data:
        html_content += f"""
            <div class="compensation-context">
                <h3>📈 Broader Compensation Discussion Context</h3>
                <p>While recent wage announcement posts are limited, our database shows broader compensation discussions:</p>
                <ul>
                    <li><strong>Total Compensation Posts:</strong> {compensation_data.get('post_count', 0)}</li>
                    <li><strong>Total Comments:</strong> {compensation_data.get('comment_count', 0)}</li>
                    <li><strong>Average Sentiment:</strong> {compensation_data.get('avg_sentiment_score', 0):.3f}</li>
                </ul>
                
                <h4>Recent Compensation Discussions:</h4>
        """
        
        top_posts = compensation_data.get('top_posts', [])
        for post in top_posts[:3]:
            html_content += f"""
                <div style="background: white; padding: 15px; margin: 10px 0; border: 1px solid #dee2e6; border-radius: 6px;">
                    <strong>{post.get('title', 'Untitled')}</strong><br>
                    <small>Score: {post.get('score', 0)} | Comments: {post.get('num_comments', 0)} | Sentiment: {post.get('sentiment', 'NEUTRAL')}</small>
                </div>
            """
        
        html_content += "</div>"
    
    # Add recommendations
    html_content += f"""
            <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 25px; margin: 30px 0;">
                <h3 style="color: #155724; margin-top: 0;">💡 Data-Driven Recommendations</h3>
                <ul>
                    <li><strong>Expand Data Collection:</strong> Consider collecting data over longer time periods (48-72 hours) to capture delayed reactions</li>
                    <li><strong>Monitor Multiple Channels:</strong> Expand beyond Reddit to include internal forums, surveys, and other feedback channels</li>
                    <li><strong>Proactive Communication:</strong> Use the unified database to establish baseline sentiment before announcements</li>
                    <li><strong>Real-Time Monitoring:</strong> Set up automated alerts when wage-related discussions spike in volume or negative sentiment</li>
                    <li><strong>Consistent Reporting:</strong> All future reports will use this same unified database for consistent insights</li>
                </ul>
            </div>
            
            <div style="background: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 20px; margin: 30px 0;">
                <h3 style="color: #1976d2; margin-top: 0;">🔄 Unified Data Architecture</h3>
                <p style="color: #1976d2;">
                    This report is generated from the same unified database that powers the dashboard, ensuring consistency across all analytics and reports. 
                    Future wage announcements will be tracked using this same system for reliable trend analysis.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; font-size: 0.9rem;">
                <p>Generated from Unified Amazon FC Intelligence Database | {data['analysis_date']}</p>
                <p>Data Source: API-collected posts and comments with ML sentiment analysis</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

if __name__ == "__main__":
    # Generate unified report
    html_report = create_unified_html_report()
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"unified_wage_analysis_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ Unified executive summary generated: {filename}")
    print("🎯 This report uses the same data source as the dashboard for consistency!")