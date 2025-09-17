import React, { useState, useEffect } from 'react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import './index.css';

// AWS Sentiment Analysis Card component
const AWSSentimentCard = ({ post }) => {
  const awsData = post.aws_sentiment || post.sentiment_analysis?.aws_analysis;
  
  if (!awsData) return null;
  
  return (
    <div style={{ 
      background: '#f8f9fa', 
      padding: '0.75rem', 
      borderRadius: '6px', 
      marginTop: '0.5rem',
      border: '1px solid #e9ecef'
    }}>
      <div style={{ fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#495057' }}>
        🤖 AWS Comprehend Analysis
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.5rem' }}>
        <div>
          <div style={{ fontSize: '0.75rem', color: '#6c757d' }}>Sentiment</div>
          <div style={{ 
            fontSize: '0.8rem', 
            fontWeight: 'bold',
            color: COLORS[awsData.sentiment?.toLowerCase()] || '#666'
          }}>
            {awsData.sentiment} ({(awsData.confidence * 100).toFixed(1)}%)
          </div>
        </div>
        
        {awsData.emotions && (
          <div>
            <div style={{ fontSize: '0.75rem', color: '#6c757d' }}>Primary Emotion</div>
            <div style={{ 
              fontSize: '0.8rem', 
              fontWeight: 'bold',
              color: EMOTION_COLORS[awsData.emotions.emotion] || '#666'
            }}>
              {awsData.emotions.emotion} ({(awsData.emotions.confidence * 100).toFixed(1)}%)
            </div>
          </div>
        )}
        
        {awsData.estimated_cost && (
          <div>
            <div style={{ fontSize: '0.75rem', color: '#6c757d' }}>Analysis Cost</div>
            <div style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#28a745' }}>
              ${awsData.estimated_cost.toFixed(4)}
            </div>
          </div>
        )}
        
        {awsData.processing_time_ms && (
          <div>
            <div style={{ fontSize: '0.75rem', color: '#6c757d' }}>Processing Time</div>
            <div style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#17a2b8' }}>
              {awsData.processing_time_ms}ms
            </div>
          </div>
        )}
      </div>
      
      {awsData.key_phrases && awsData.key_phrases.compensation_phrases && awsData.key_phrases.compensation_phrases.length > 0 && (
        <div style={{ marginTop: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: '#6c757d', marginBottom: '0.25rem' }}>
            Key Compensation Terms
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
            {awsData.key_phrases.compensation_phrases.slice(0, 5).map((phrase, idx) => (
              <span key={idx} style={{
                fontSize: '0.7rem',
                background: '#e3f2fd',
                color: '#1976d2',
                padding: '0.15rem 0.4rem',
                borderRadius: '12px',
                border: '1px solid #bbdefb'
              }}>
                {phrase.text}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Emotion Breakdown Chart component with interactivity
const EmotionBreakdownChart = ({ emotionData, allPosts, onEmotionClick }) => {
  if (!emotionData || emotionData.length === 0) return null;
  
  const handleBarClick = (data) => {
    if (data && data.activePayload && data.activePayload[0]) {
      const emotion = data.activePayload[0].payload.emotion;
      const postsWithEmotion = allPosts.filter(post => 
        post.aws_sentiment?.emotions?.emotion === emotion
      );
      onEmotionClick(emotion, postsWithEmotion);
    }
  };
  
  return (
    <div className="chart-container">
      <h3>😊 Emotion Analysis (AWS Comprehend)</h3>
      <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
        Detailed emotional sentiment breakdown from AWS analysis. Click bars to see examples.
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={emotionData} onClick={handleBarClick}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="emotion" />
          <YAxis />
          <Tooltip 
            formatter={(value, name, props) => [
              `${(value * 100).toFixed(1)}% confidence`, 
              `${props.payload.count} posts (avg ${props.payload.avg_upvotes?.toFixed(1)} upvotes)`
            ]} 
          />
          <Bar dataKey="confidence" fill="#8884d8" style={{ cursor: 'pointer' }}>
            {emotionData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={EMOTION_COLORS[entry.emotion] || '#8884d8'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem', textAlign: 'center' }}>
        💡 Click on any emotion bar to see example posts with that emotion
      </div>
    </div>
  );
};

// Cost Usage Dashboard component
const CostUsageDashboard = ({ costData }) => {
  if (!costData) return null;
  
  const budgetPercentage = (costData.current_daily_spend / costData.daily_limit) * 100;
  const remainingBudget = costData.daily_limit - costData.current_daily_spend;
  
  return (
    <div className="chart-container">
      <h3>💰 AWS Cost Usage & Budget</h3>
      <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
        Daily AWS Comprehend usage and cost savings from caching
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ 
          background: budgetPercentage > 80 ? '#ffebee' : '#e8f5e8', 
          padding: '1rem', 
          borderRadius: '8px',
          border: `2px solid ${budgetPercentage > 80 ? '#f44336' : '#4caf50'}`
        }}>
          <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Daily Budget</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: budgetPercentage > 80 ? '#f44336' : '#4caf50' }}>
            ${costData.current_daily_spend.toFixed(2)} / ${costData.daily_limit.toFixed(2)}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#666' }}>
            {budgetPercentage.toFixed(1)}% used
          </div>
        </div>
        
        <div style={{ background: '#f0f8ff', padding: '1rem', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Remaining Budget</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#1976d2' }}>
            ${remainingBudget.toFixed(2)}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#666' }}>
            Available today
          </div>
        </div>
        
        {costData.cache_savings && (
          <div style={{ background: '#e8f5e8', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Cache Savings</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#4caf50' }}>
              ${costData.cache_savings.toFixed(2)}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>
              Saved today
            </div>
          </div>
        )}
        
        {costData.total_requests && (
          <div style={{ background: '#fff3e0', padding: '1rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>API Requests</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#f57c00' }}>
              {costData.total_requests}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#666' }}>
              {costData.cache_hits || 0} cached
            </div>
          </div>
        )}
      </div>
      
      {/* Budget usage bar */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Budget Usage</span>
          <span style={{ fontSize: '0.9rem', color: budgetPercentage > 80 ? '#f44336' : '#666' }}>
            {budgetPercentage.toFixed(1)}%
          </span>
        </div>
        <div style={{ 
          width: '100%', 
          height: '20px', 
          background: '#e0e0e0', 
          borderRadius: '10px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${Math.min(budgetPercentage, 100)}%`,
            height: '100%',
            background: budgetPercentage > 90 ? '#f44336' : budgetPercentage > 80 ? '#ff9800' : '#4caf50',
            transition: 'width 0.3s ease'
          }}></div>
        </div>
      </div>
      
      {budgetPercentage > 80 && (
        <div style={{ 
          background: '#ffebee', 
          border: '1px solid #f44336', 
          borderRadius: '6px', 
          padding: '0.75rem',
          fontSize: '0.85rem',
          color: '#c62828'
        }}>
          ⚠️ <strong>Budget Warning:</strong> You've used {budgetPercentage.toFixed(1)}% of your daily AWS budget. 
          Consider enabling more aggressive caching or increasing your daily limit.
        </div>
      )}
    </div>
  );
};

// Comprehensive Post Analysis Component
const ComprehensivePostAnalysis = ({ posts, sentimentType, onClose }) => {
  if (!posts || posts.length === 0) return null;

  const calculateCommentSentiment = (comments) => {
    if (!comments || comments.length === 0) return { positive: 0, negative: 0, neutral: 0 };
    
    const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
    comments.forEach(comment => {
      if (comment.aws_sentiment) {
        sentimentCounts[comment.aws_sentiment.sentiment] = (sentimentCounts[comment.aws_sentiment.sentiment] || 0) + 1;
      }
    });
    
    return sentimentCounts;
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '95vw',
        maxHeight: '90vh',
        overflow: 'auto',
        margin: '1rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0, color: COLORS[sentimentType] || '#333' }}>
            {sentimentType.charAt(0).toUpperCase() + sentimentType.slice(1)} Sentiment Posts ({posts.length} total)
          </h2>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              padding: '0.5rem'
            }}
          >
            ✕
          </button>
        </div>
        
        <div style={{ display: 'grid', gap: '1.5rem' }}>
          {posts.map((post, index) => {
            const commentSentiment = calculateCommentSentiment(post.sample_comments);
            const totalComments = Object.values(commentSentiment).reduce((a, b) => a + b, 0);
            
            return (
              <div key={index} style={{
                border: `2px solid ${COLORS[sentimentType]}`,
                borderRadius: '12px',
                padding: '1.5rem',
                backgroundColor: '#fafafa'
              }}>
                {/* Post Header */}
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '0.5rem', color: '#333' }}>
                    {post.title}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.75rem' }}>
                    👤 u/{post.author} | ⬆️ {post.score} upvotes | 💬 {post.num_comments || post.sample_comments?.length || 0} comments
                    {post.permalink && (
                      <a 
                        href={`https://reddit.com${post.permalink}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ marginLeft: '10px', color: '#1976d2', textDecoration: 'none' }}
                      >
                        🔗 View on Reddit
                      </a>
                    )}
                  </div>
                  
                  {/* Post Content */}
                  {post.content && (
                    <div style={{ 
                      fontSize: '0.95rem', 
                      fontStyle: 'italic', 
                      color: '#444',
                      marginBottom: '1rem',
                      padding: '1rem',
                      backgroundColor: 'white',
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0'
                    }}>
                      "{post.content}"
                    </div>
                  )}
                  
                  {/* Post Sentiment Analysis */}
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                    gap: '1rem',
                    marginBottom: '1rem',
                    padding: '1rem',
                    backgroundColor: '#f0f8ff',
                    borderRadius: '8px'
                  }}>
                    <div>
                      <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Post Sentiment</div>
                      <div style={{ 
                        fontSize: '0.9rem', 
                        fontWeight: 'bold',
                        color: COLORS[post.aws_sentiment?.sentiment] || '#666'
                      }}>
                        {post.aws_sentiment?.sentiment || 'Unknown'} ({((post.aws_sentiment?.confidence || 0) * 100).toFixed(1)}%)
                      </div>
                    </div>
                    
                    {post.aws_sentiment?.emotions && (
                      <div>
                        <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Primary Emotion</div>
                        <div style={{ 
                          fontSize: '0.9rem', 
                          fontWeight: 'bold',
                          color: EMOTION_COLORS[post.aws_sentiment.emotions.emotion] || '#666'
                        }}>
                          {post.aws_sentiment.emotions.emotion} ({(post.aws_sentiment.emotions.confidence * 100).toFixed(1)}%)
                        </div>
                      </div>
                    )}
                    
                    <div>
                      <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Engagement Level</div>
                      <div style={{ 
                        fontSize: '0.9rem', 
                        fontWeight: 'bold',
                        color: post.score > 100 ? '#4caf50' : post.score > 50 ? '#ff9800' : '#f44336'
                      }}>
                        {post.score > 100 ? 'Very High' : post.score > 50 ? 'High' : post.score > 20 ? 'Medium' : 'Low'}
                      </div>
                    </div>
                    
                    {post.aws_sentiment?.estimated_cost && (
                      <div>
                        <div style={{ fontSize: '0.8rem', color: '#666', marginBottom: '0.25rem' }}>Analysis Cost</div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 'bold', color: '#28a745' }}>
                          ${post.aws_sentiment.estimated_cost.toFixed(4)}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Comments Analysis */}
                {post.sample_comments && post.sample_comments.length > 0 && (
                  <div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      marginBottom: '1rem',
                      padding: '0.75rem',
                      backgroundColor: '#fff3e0',
                      borderRadius: '8px'
                    }}>
                      <strong style={{ color: '#333' }}>💬 Comments Analysis ({post.sample_comments.length} comments)</strong>
                      {totalComments > 0 && (
                        <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.8rem' }}>
                          {commentSentiment.positive > 0 && (
                            <span style={{ color: COLORS.positive }}>
                              {commentSentiment.positive} positive
                            </span>
                          )}
                          {commentSentiment.negative > 0 && (
                            <span style={{ color: COLORS.negative }}>
                              {commentSentiment.negative} negative
                            </span>
                          )}
                          {commentSentiment.neutral > 0 && (
                            <span style={{ color: COLORS.neutral }}>
                              {commentSentiment.neutral} neutral
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div style={{ display: 'grid', gap: '0.75rem' }}>
                      {post.sample_comments.map((comment, idx) => (
                        <div key={idx} style={{ 
                          padding: '0.75rem', 
                          backgroundColor: 'white', 
                          borderRadius: '6px',
                          borderLeft: `4px solid ${COLORS[comment.aws_sentiment?.sentiment || comment.sentiment] || '#ccc'}`,
                          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                        }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            marginBottom: '0.5rem'
                          }}>
                            <div style={{ fontSize: '0.85rem', color: '#666' }}>
                              👤 u/{comment.author} | ⬆️ {comment.score}
                            </div>
                            {comment.aws_sentiment && (
                              <div style={{ 
                                fontSize: '0.75rem',
                                background: COLORS[comment.aws_sentiment.sentiment] + '20',
                                color: COLORS[comment.aws_sentiment.sentiment],
                                padding: '0.2rem 0.5rem',
                                borderRadius: '12px'
                              }}>
                                {comment.aws_sentiment.sentiment} ({(comment.aws_sentiment.confidence * 100).toFixed(0)}%)
                              </div>
                            )}
                          </div>
                          <div style={{ fontSize: '0.9rem', color: '#333' }}>
                            "{comment.content}"
                          </div>
                          {comment.aws_sentiment?.emotions && (
                            <div style={{ 
                              fontSize: '0.75rem', 
                              color: '#666', 
                              marginTop: '0.5rem',
                              fontStyle: 'italic'
                            }}>
                              Emotion: {comment.aws_sentiment.emotions.emotion} ({(comment.aws_sentiment.emotions.confidence * 100).toFixed(0)}%)
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Key Phrases */}
                {post.aws_sentiment?.key_phrases?.compensation_phrases && post.aws_sentiment.key_phrases.compensation_phrases.length > 0 && (
                  <div style={{ marginTop: '1rem' }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#333' }}>
                      🔑 Key Compensation Terms Detected:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {post.aws_sentiment.key_phrases.compensation_phrases.map((phrase, idx) => (
                        <span key={idx} style={{
                          fontSize: '0.8rem',
                          background: '#e3f2fd',
                          color: '#1976d2',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '12px',
                          border: '1px solid #bbdefb'
                        }}>
                          {phrase.text} ({(phrase.confidence * 100).toFixed(0)}%)
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Interactive Modal for showing detailed examples
const DetailModal = ({ isOpen, onClose, title, posts, emotionType }) => {
  if (!isOpen) return null;
  
  return (
    <ComprehensivePostAnalysis 
      posts={posts}
      sentimentType={emotionType}
      onClose={onClose}
    />
  );
};

// PostDetailCard component for rich post display
const PostDetailCard = ({ post }) => {
  const [expanded, setExpanded] = useState(false);
  
  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="post-card" style={{ marginBottom: '1rem' }}>
      <div className="post-title" style={{ cursor: 'pointer' }} onClick={() => setExpanded(!expanded)}>
        {post.title} {expanded ? '▼' : '▶'}
      </div>
      <div className="post-meta">
        👤 u/{post.author} | ⬆️ {post.score} | 📅 {formatDate(post.created_date)}
        <br />
        <span className={`sentiment-badge sentiment-${post.sentiment?.sentiment || 'neutral'}`}>
          {post.sentiment?.sentiment || 'neutral'} ({(post.sentiment_score || 0).toFixed(2)})
        </span>
        {post.aws_sentiment && (
          <span style={{ 
            marginLeft: '0.5rem',
            fontSize: '0.75rem',
            background: '#e3f2fd',
            color: '#1976d2',
            padding: '0.2rem 0.5rem',
            borderRadius: '12px',
            border: '1px solid #bbdefb'
          }}>
            AWS: {post.aws_sentiment.sentiment} ({(post.aws_sentiment.confidence * 100).toFixed(0)}%)
          </span>
        )}
        {post.permalink && (
          <a 
            href={`https://reddit.com${post.permalink}`} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ marginLeft: '10px', color: '#667eea', textDecoration: 'none' }}
          >
            🔗 View on Reddit
          </a>
        )}
      </div>
      
      {expanded && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          {post.content && (
            <div style={{ marginBottom: '1rem' }}>
              <strong>📝 Post Content:</strong>
              <p style={{ margin: '0.5rem 0', fontStyle: 'italic', color: '#555' }}>
                "{post.content}"
              </p>
            </div>
          )}
          
          {post.sample_comments && post.sample_comments.length > 0 && (
            <div>
              <strong>💬 Sample Comments:</strong>
              {post.sample_comments.map((comment, idx) => (
                <div key={idx} style={{ 
                  margin: '0.5rem 0', 
                  padding: '0.5rem', 
                  backgroundColor: 'white', 
                  borderRadius: '4px',
                  borderLeft: `3px solid ${COLORS[comment.sentiment] || '#ccc'}`
                }}>
                  <div style={{ fontSize: '0.9rem', color: '#666' }}>
                    👤 u/{comment.author} | ⬆️ {comment.score}
                  </div>
                  <div style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
                    "{comment.content}"
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* AWS Sentiment Analysis Details */}
          <AWSSentimentCard post={post} />
        </div>
      )}
    </div>
  );
};

const COLORS = {
  positive: '#4caf50',
  negative: '#f44336',
  neutral: '#ff9800',
  mixed: '#9c27b0'
};

const EMOTION_COLORS = {
  joy: '#4caf50',
  anger: '#f44336',
  sadness: '#2196f3',
  fear: '#9c27b0',
  surprise: '#ff9800',
  disgust: '#795548',
  neutral: '#607d8b',
  confusion: '#e91e63'
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  // Modal state for detailed views
  const [modalState, setModalState] = useState({
    isOpen: false,
    title: '',
    posts: [],
    emotionType: null
  });

  // Fetch real data from your analysis
  const fetchData = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    
    try {
      // First, try to get existing analysis data
      let response = await fetch('http://localhost:3002/api/analysis');
      let result = null;
      
      if (response.ok) {
        result = await response.json();
      }
      
      // Check if we need fresh data (no data, old data, or force refresh)
      const needsFreshData = forceRefresh || 
        !result?.success || 
        !result?.data?.total_posts || 
        result.data.total_posts === 0 ||
        (result.data.analysis_date && 
         new Date() - new Date(result.data.analysis_date) > 2 * 60 * 60 * 1000); // 2 hours old
      
      if (needsFreshData) {
        console.log('Fetching fresh Reddit data...');
        setError('Collecting fresh data from Reddit... This may take a few minutes.');
        
        // Trigger fresh data collection
        const collectResponse = await fetch('http://localhost:3002/api/collect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            subreddit: 'amazonfc',
            limit: 100,
            time_filter: 'week',
            include_comments: true,
            analyze_sentiment: true
          })
        });
        
        if (!collectResponse.ok) {
          throw new Error(`Collection failed: ${collectResponse.status}`);
        }
        
        const collectResult = await collectResponse.json();
        if (!collectResult.success) {
          throw new Error(collectResult.error || 'Data collection failed');
        }
        
        // Wait a moment for processing, then fetch the updated analysis
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        response = await fetch('http://localhost:3002/api/analysis');
        if (!response.ok) {
          throw new Error(`Analysis fetch failed: ${response.status}`);
        }
        
        result = await response.json();
      }
      
      if (!result?.success) {
        throw new Error(result?.error || 'No analysis data available');
      }
      
      // Process and enhance the data for the dashboard
      const processedData = processAnalysisData(result.data);
      setData(processedData);
      setLastUpdated(new Date());
      setError(null);
      
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError(`Failed to fetch data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Process the raw analysis data for dashboard display
  const processAnalysisData = (rawData) => {
    // Group posts by sentiment for easy access
    const postsBySentiment = {
      positive: [],
      negative: [],
      neutral: [],
      mixed: []
    };
    
    const postsByEmotion = {
      joy: [],
      anger: [],
      sadness: [],
      fear: [],
      surprise: [],
      disgust: [],
      neutral: [],
      confusion: []
    };
    
    // Process posts and categorize them
    if (rawData.posts) {
      rawData.posts.forEach(post => {
        // Add to sentiment categories
        const sentiment = post.aws_sentiment?.sentiment?.toLowerCase() || 'neutral';
        if (postsBySentiment[sentiment]) {
          postsBySentiment[sentiment].push(post);
        }
        
        // Add to emotion categories
        const emotion = post.aws_sentiment?.emotions?.emotion?.toLowerCase() || 'neutral';
        if (postsByEmotion[emotion]) {
          postsByEmotion[emotion].push(post);
        }
      });
    }
    
    // Calculate emotion breakdown with engagement correlation
    const emotionBreakdown = Object.keys(postsByEmotion).map(emotion => {
      const posts = postsByEmotion[emotion];
      const avgUpvotes = posts.length > 0 
        ? posts.reduce((sum, post) => sum + (post.score || 0), 0) / posts.length 
        : 0;
      const avgConfidence = posts.length > 0
        ? posts.reduce((sum, post) => sum + (post.aws_sentiment?.emotions?.confidence || 0), 0) / posts.length
        : 0;
      
      return {
        emotion,
        confidence: avgConfidence,
        count: posts.length,
        avg_upvotes: avgUpvotes
      };
    }).filter(item => item.count > 0);
    
    // Calculate AWS sentiment summary
    const awsSentimentSummary = {
      positive: postsBySentiment.positive.length,
      negative: postsBySentiment.negative.length,
      neutral: postsBySentiment.neutral.length,
      mixed: postsBySentiment.mixed.length
    };
    
    // Calculate cost data if available
    const costData = rawData.cost_analysis ? {
      daily_limit: rawData.cost_analysis.daily_budget || 5.00,
      current_daily_spend: rawData.cost_analysis.total_cost || 0,
      cache_savings: rawData.cost_analysis.cache_savings || 0,
      total_requests: rawData.cost_analysis.total_requests || 0,
      cache_hits: rawData.cost_analysis.cache_hits || 0,
      aws_requests: rawData.cost_analysis.aws_requests || 0
    } : null;
    
    return {
      ...rawData,
      aws_sentiment_summary: awsSentimentSummary,
      posts_by_sentiment: postsBySentiment,
      posts_by_emotion: postsByEmotion,
      emotion_breakdown: emotionBreakdown,
      cost_data: costData,
      top_posts: rawData.posts?.slice(0, 10) || []
    };
  };



  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = (forceRefresh = false) => {
    fetchData(forceRefresh);
  };

  const handleEmotionClick = (emotion, posts) => {
    setModalState({
      isOpen: true,
      title: `Posts with ${emotion.charAt(0).toUpperCase() + emotion.slice(1)} Emotion`,
      posts: posts,
      emotionType: emotion
    });
  };

  const handleSentimentClick = (sentiment, posts) => {
    setModalState({
      isOpen: true,
      title: `${sentiment.charAt(0).toUpperCase() + sentiment.slice(1)} Sentiment Posts`,
      posts: posts,
      emotionType: sentiment
    });
  };

  const closeModal = () => {
    setModalState({
      isOpen: false,
      title: '',
      posts: [],
      emotionType: null
    });
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">
          <h2>🔄 Loading compensation analysis...</h2>
          <p>Analyzing sentiment and generating insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error">
          <h2>❌ Error</h2>
          <p>{error}</p>
          <button onClick={handleRefresh} className="refresh-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Prepare chart data
  const awsSentimentChartData = data?.aws_sentiment_summary ? [
    { name: 'Positive', value: data.aws_sentiment_summary.positive, color: COLORS.positive },
    { name: 'Negative', value: data.aws_sentiment_summary.negative, color: COLORS.negative },
    { name: 'Neutral', value: data.aws_sentiment_summary.neutral, color: COLORS.neutral },
    { name: 'Mixed', value: data.aws_sentiment_summary.mixed, color: COLORS.mixed }
  ] : [];

  const compensationData = data?.detailed_insights?.compensation_amounts?.most_mentioned?.map(([amount, count]) => ({
    amount,
    count
  })) || [];

  const topicData = data?.detailed_insights?.topic_analysis?.most_common_topics?.map(([topic, count]) => ({
    topic: topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    count
  })) || [];



  return (
    <div className="dashboard-container">
      <div className="header">
        <h1>💰 Compensation Sentiment Analysis Dashboard</h1>
        <p>Real-time insights from Amazon FC employee discussions</p>
        {lastUpdated && (
          <p style={{ opacity: 0.8, fontSize: '0.9rem' }}>
            Last updated: {lastUpdated.toLocaleString()}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button onClick={() => handleRefresh(false)} className="refresh-button" disabled={loading}>
          {loading ? '🔄 Loading...' : '🔄 Refresh Analysis'}
        </button>
        <button 
          onClick={() => handleRefresh(true)} 
          className="refresh-button" 
          disabled={loading}
          style={{ background: 'linear-gradient(135deg, #4caf50 0%, #45a049 100%)' }}
        >
          {loading ? '📡 Collecting...' : '📡 Collect Fresh Data'}
        </button>
      </div>

      {/* Key Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{data?.total_posts || 0}</div>
          <div className="stat-label">Total Posts Analyzed</div>
        </div>
        <div className="stat-card">
          <div className={`stat-value positive`}>
            {data?.aws_sentiment_summary ? 
              Math.round((data.aws_sentiment_summary.positive / (data.aws_sentiment_summary.positive + data.aws_sentiment_summary.negative + data.aws_sentiment_summary.neutral + data.aws_sentiment_summary.mixed)) * 100) 
              : 0}%
          </div>
          <div className="stat-label">Positive Sentiment</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data?.posts?.filter(p => p.score > 50).length || 0}</div>
          <div className="stat-label">High Engagement Posts</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data?.posts ? Math.round(data.posts.reduce((sum, p) => sum + (p.score || 0), 0) / data.posts.length) : 0}</div>
          <div className="stat-label">Average Post Score</div>
        </div>
      </div>

      {/* AWS Analysis Stats */}
      {data?.cost_data && (
        <div className="stats-grid" style={{ marginTop: '1rem' }}>
          <div className="stat-card" style={{ background: '#e3f2fd', border: '2px solid #1976d2' }}>
            <div className="stat-value" style={{ color: '#1976d2' }}>
              {data.cost_data.aws_requests ? Math.round((data.cost_data.aws_requests / data.cost_data.total_requests) * 100) : 0}%
            </div>
            <div className="stat-label">AWS Success Rate</div>
          </div>
          <div className="stat-card" style={{ background: '#e8f5e8', border: '2px solid #4caf50' }}>
            <div className="stat-value" style={{ color: '#4caf50' }}>
              ${(data.cost_data.current_daily_spend || 0).toFixed(3)}
            </div>
            <div className="stat-label">Total AWS Cost</div>
          </div>
          <div className="stat-card" style={{ background: '#fff3e0', border: '2px solid #ff9800' }}>
            <div className="stat-value" style={{ color: '#ff9800' }}>
              {data.posts?.filter(p => p.aws_sentiment?.emotions).length || 0}
            </div>
            <div className="stat-label">Emotions Detected</div>
          </div>
          <div className="stat-card" style={{ background: '#f3e5f5', border: '2px solid #9c27b0' }}>
            <div className="stat-value" style={{ color: '#9c27b0' }}>
              {data.cost_data.cache_hits && data.cost_data.total_requests ? 
                Math.round((data.cost_data.cache_hits / data.cost_data.total_requests) * 100) : 0}%
            </div>
            <div className="stat-label">Cache Hit Rate</div>
          </div>
        </div>
      )}

      {/* AWS Comprehend Sentiment Distribution */}
      <div className="chart-container">
        <h2>🤖 AWS Comprehend Sentiment Analysis</h2>
        <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
          Advanced sentiment analysis powered by AWS Comprehend. Click on any segment to explore detailed posts and comments.
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <PieChart onClick={(data) => {
            if (data && data.activePayload && data.activePayload[0]) {
              const sentiment = data.activePayload[0].name.toLowerCase();
              const sentimentPosts = data.posts_by_sentiment?.[sentiment] || [];
              handleSentimentClick(sentiment, sentimentPosts);
            }
          }}>
            <Pie
              data={awsSentimentChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(1)}%)`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              style={{ cursor: 'pointer' }}
            >
              {awsSentimentChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value, name) => [`${value} posts`, name]} />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem', textAlign: 'center' }}>
          💡 Click on any sentiment segment to see all posts with detailed comment analysis
        </div>
      </div>

      {/* AWS Cost Usage Dashboard */}
      {data.cost_data && <CostUsageDashboard costData={data.cost_data} />}

      {/* Emotion Breakdown Chart */}
      {data.emotion_breakdown && (
        <EmotionBreakdownChart 
          emotionData={data.emotion_breakdown} 
          allPosts={[...data.top_posts, ...(data.posts_by_emotion ? Object.values(data.posts_by_emotion).flat() : [])]}
          onEmotionClick={handleEmotionClick}
        />
      )}

      {/* Charts Grid */}
      <div className="posts-grid">
        {/* Compensation Amounts */}
        <div className="chart-container">
          <h3>💵 Most Discussed Amounts</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={compensationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="amount" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Topic Analysis */}
        <div className="chart-container">
          <h3>📋 Discussion Topics</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={topicData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="topic" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#764ba2" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Posts */}
      <div className="chart-container">
        <h2>🏆 Top Engaging Posts</h2>
        <div className="posts-grid">
          {data.top_posts.slice(0, 6).map((post, index) => (
            <div key={index} className="post-card">
              <div className="post-title">{post.title}</div>
              <div className="post-meta">
                👤 u/{post.author} | ⬆️ {post.score} upvotes
              </div>
              <span className={`sentiment-badge sentiment-${post.aws_sentiment?.sentiment || 'neutral'}`}>
                {post.aws_sentiment?.sentiment || 'neutral'} ({((post.aws_sentiment?.confidence || 0) * 100).toFixed(0)}%)
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Posts by Sentiment */}
      <div className="posts-grid">
        <div className="chart-container">
          <h3>😊 Positive Sentiment Posts</h3>
          {data.posts_by_sentiment.positive.slice(0, 3).map((post, index) => (
            <PostDetailCard key={post.id || index} post={post} />
          ))}
        </div>

        <div className="chart-container">
          <h3>😞 Negative Sentiment Posts</h3>
          {data.posts_by_sentiment.negative.slice(0, 2).map((post, index) => (
            <PostDetailCard key={post.id || index} post={post} />
          ))}
        </div>

        <div className="chart-container">
          <h3>😐 Neutral Sentiment Posts</h3>
          {data.posts_by_sentiment.neutral.slice(0, 2).map((post, index) => (
            <PostDetailCard key={post.id || index} post={post} />
          ))}
        </div>
      </div>

      {/* Key Insights */}
      <div className="chart-container">
        <h2>🔍 Key Insights</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {data?.aws_sentiment_summary && (
            <div style={{ padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '8px' }}>
              <strong>✅ Overall Sentiment:</strong> Employee sentiment about compensation changes is <strong>
                {data.aws_sentiment_summary.positive > data.aws_sentiment_summary.negative ? 'POSITIVE' : 
                 data.aws_sentiment_summary.negative > data.aws_sentiment_summary.positive ? 'NEGATIVE' : 'NEUTRAL'}
              </strong> ({Math.round((data.aws_sentiment_summary.positive / (data.aws_sentiment_summary.positive + data.aws_sentiment_summary.negative + data.aws_sentiment_summary.neutral + data.aws_sentiment_summary.mixed)) * 100)}% positive)
            </div>
          )}
          
          {compensationData.length > 0 && (
            <div style={{ padding: '1rem', backgroundColor: '#f0f8ff', borderRadius: '8px' }}>
              <strong>💰 Most Discussed:</strong> {compensationData[0].amount} raises mentioned {compensationData[0].count} times
            </div>
          )}
          
          {data?.posts && (
            <div style={{ padding: '1rem', backgroundColor: '#fff3e0', borderRadius: '8px' }}>
              <strong>🔥 Engagement:</strong> {data.posts.filter(p => p.score > 100).length} posts have very high engagement (&gt;100 upvotes)
            </div>
          )}
          
          {data?.emotion_breakdown && data.emotion_breakdown.length > 0 && (
            <div style={{ padding: '1rem', backgroundColor: '#f3e5f5', borderRadius: '8px' }}>
              <strong>📈 Activity:</strong> {data.posts?.length || 0} posts analyzed with {data.emotion_breakdown.reduce((sum, e) => sum + e.count, 0)} emotions detected
            </div>
          )}
          
          {/* AWS-specific insights */}
          {data?.cost_data && (
            <>
              <div style={{ padding: '1rem', backgroundColor: '#e3f2fd', borderRadius: '8px' }}>
                <strong>🤖 AWS Analysis:</strong> AWS Comprehend processed {data.cost_data.aws_requests || 0} requests with {data.cost_data.total_requests ? Math.round((data.cost_data.aws_requests / data.cost_data.total_requests) * 100) : 0}% success rate
              </div>
              <div style={{ padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '8px' }}>
                <strong>💸 Cost Efficiency:</strong> Total analysis cost ${(data.cost_data.current_daily_spend || 0).toFixed(3)} with ${(data.cost_data.cache_savings || 0).toFixed(3)} saved through caching
              </div>
              {data.emotion_breakdown && data.emotion_breakdown.length > 0 && (
                <div style={{ padding: '1rem', backgroundColor: '#fff8e1', borderRadius: '8px' }}>
                  <strong>😊 Emotion Detection:</strong> {data.emotion_breakdown.reduce((sum, e) => sum + e.count, 0)} emotions detected across posts, with {data.emotion_breakdown[0]?.emotion || 'neutral'} being the most prevalent
                </div>
              )}
              {data.emotion_breakdown?.find(e => e.emotion === 'anger') && (
                <div style={{ padding: '1rem', backgroundColor: '#f1f8e9', borderRadius: '8px' }}>
                  <strong>📈 Engagement Insight:</strong> Posts with anger emotion get {data.emotion_breakdown.find(e => e.emotion === 'anger').avg_upvotes.toFixed(0)} average upvotes, suggesting controversial topics drive engagement
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
        <p>🔄 Live data from Reddit r/amazonfc subreddit</p>
        <p>📊 Analysis powered by AWS Comprehend sentiment analysis and emotion detection</p>
        <p>💡 Click on charts and data points to explore detailed posts and comments</p>
        <p>🤖 Real-time cost tracking and caching optimization</p>
      </div>

      {/* Detail Modal */}
      <DetailModal 
        isOpen={modalState.isOpen}
        onClose={closeModal}
        title={modalState.title}
        posts={modalState.posts}
        emotionType={modalState.emotionType}
      />
    </div>
  );
}

export default App;