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
  ResponsiveContainer 
} from 'recharts';
import './index.css';

const COLORS = {
  positive: '#4caf50',
  negative: '#f44336',
  neutral: '#ff9800'
};

// Data freshness indicator component
const DataFreshnessIndicator = ({ lastUpdated, dataTimeframe }) => {
  const getTimeSinceUpdate = () => {
    if (!lastUpdated) return 'Unknown';
    const now = new Date();
    const diff = now - lastUpdated;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} minutes ago`;
    if (hours < 24) return `${hours} hours ago`;
    return `${days} days ago`;
  };

  const getFreshnessColor = () => {
    if (!lastUpdated) return '#666';
    const now = new Date();
    const diff = now - lastUpdated;
    const hours = diff / (1000 * 60 * 60);
    
    if (hours < 1) return '#4caf50'; // Green - very fresh
    if (hours < 6) return '#ff9800'; // Orange - somewhat fresh
    return '#f44336'; // Red - stale
  };

  return (
    <div style={{ 
      background: 'white', 
      padding: '1rem', 
      borderRadius: '8px', 
      marginBottom: '1rem',
      border: `2px solid ${getFreshnessColor()}`
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: 0, color: getFreshnessColor() }}>📊 Data Freshness</h3>
          <p style={{ margin: '0.5rem 0', color: '#666' }}>
            Last updated: <strong>{getTimeSinceUpdate()}</strong>
          </p>
          <p style={{ margin: 0, fontSize: '0.9rem', color: '#666' }}>
            Data covers: <strong>{dataTimeframe}</strong>
          </p>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '12px', 
            height: '12px', 
            borderRadius: '50%', 
            backgroundColor: getFreshnessColor(),
            margin: '0 auto 0.5rem'
          }}></div>
          <div style={{ fontSize: '0.8rem', color: getFreshnessColor() }}>
            {getFreshnessColor() === '#4caf50' ? 'FRESH' : 
             getFreshnessColor() === '#ff9800' ? 'AGING' : 'STALE'}
          </div>
        </div>
      </div>
    </div>
  );
};

// Refresh controls component
const RefreshControls = ({ onRefresh, loading, autoRefresh, setAutoRefresh }) => {
  const [countdown, setCountdown] = useState(0);
  
  useEffect(() => {
    let interval;
    if (autoRefresh && countdown > 0) {
      interval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            onRefresh();
            return 300; // Reset to 5 minutes
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh, countdown, onRefresh]);

  const formatCountdown = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ 
      background: 'white', 
      padding: '1rem', 
      borderRadius: '8px', 
      marginBottom: '1rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div>
        <button 
          onClick={onRefresh} 
          className="refresh-button" 
          disabled={loading}
          style={{ marginBottom: '0.5rem' }}
        >
          {loading ? '🔄 Refreshing...' : '🔄 Refresh Data Now'}
        </button>
        <div style={{ fontSize: '0.9rem', color: '#666' }}>
          Collects latest posts from r/amazonfc and analyzes sentiment
        </div>
      </div>
      
      <div style={{ textAlign: 'right' }}>
        <label style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
          <input 
            type="checkbox" 
            checked={autoRefresh}
            onChange={(e) => {
              setAutoRefresh(e.target.checked);
              if (e.target.checked) setCountdown(300); // 5 minutes
            }}
            style={{ marginRight: '0.5rem' }}
          />
          Auto-refresh every 5 minutes
        </label>
        {autoRefresh && countdown > 0 && (
          <div style={{ fontSize: '0.9rem', color: '#666' }}>
            Next refresh in: <strong>{formatCountdown(countdown)}</strong>
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [dataTimeframe, setDataTimeframe] = useState('Last 14 days');

  // API call to get real compensation data
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to fetch from actual API first
      let response;
      try {
        response = await fetch('http://localhost:3001/api/analysis');
        if (response.ok) {
          const apiData = await response.json();
          if (apiData.success) {
            setData(apiData.data);
            setLastUpdated(new Date(apiData.lastUpdated));
            setDataTimeframe('Last 14 days (from Reddit API)');
            setLoading(false);
            return;
          }
        }
      } catch (apiError) {
        console.log('API not available, using mock data');
      }
      
      // Simulate API call delay for mock data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data based on your analysis results (fallback)
      const mockData = {
        total_posts: 56,
        analysis_date: new Date().toISOString(),
        sentiment_summary: {
          positive: 42,
          negative: 1,
          neutral: 13
        },
        detailed_insights: {
          sentiment_analysis: {
            overall_sentiment: 'positive',
            sentiment_distribution: {
              positive_percentage: 75.0,
              negative_percentage: 1.8,
              neutral_percentage: 23.2
            }
          },
          compensation_amounts: {
            most_mentioned: [
              ['50 cent', 7],
              ['$1.10', 5],
              ['50 cents', 5],
              ['$0.50', 4],
              ['$23', 3]
            ]
          },
          facility_analysis: {
            most_discussed_facilities: [
              ['BFL1', 1],
              ['CVG', 1],
              ['CMH3', 1],
              ['CMH1', 1],
              ['AKC1', 1]
            ]
          },
          topic_analysis: {
            most_common_topics: [
              ['pay_raise', 45],
              ['tenure_based', 10],
              ['new_employee', 8],
              ['general', 7],
              ['announcement', 7]
            ]
          },
          engagement_analysis: {
            high_engagement_posts: 20,
            average_score: 25.52,
            most_engaging_sentiment: 'neutral'
          }
        },
        top_posts: [
          {
            title: 'Raise',
            score: 363,
            author: 'Vitajimmi',
            sentiment: { sentiment: 'positive', score: 0.8 }
          },
          {
            title: 'Workers with the day off tomorrow refreshing Reddit...',
            score: 186,
            author: 'Interesting_Dot_2916',
            sentiment: { sentiment: 'neutral', score: 0.1 }
          },
          {
            title: 'Do you guys think it\'s time for a new bigger wage...',
            score: 132,
            author: 'YouFoundFred',
            sentiment: { sentiment: 'positive', score: 0.6 }
          },
          {
            title: 'Texas pay. (HOU8)',
            score: 125,
            author: 'mydude356',
            sentiment: { sentiment: 'neutral', score: 0.0 }
          },
          {
            title: 'Pay raise for Tier 1 and 3',
            score: 96,
            author: 'Kychiii',
            sentiment: { sentiment: 'positive', score: 0.7 }
          }
        ],
        posts_by_sentiment: {
          positive: [
            { title: 'BFL1', score: 1, sentiment_score: 1.0, author: 'user1' },
            { title: 'CVG TOM Node Raise', score: 1, sentiment_score: 1.0, author: 'user2' },
            { title: 'Pay increase update.', score: 1, sentiment_score: 1.0, author: 'user3' }
          ],
          negative: [
            { title: 'What should I do if I didn\'t get paid yet', score: 0, sentiment_score: -1.0, author: 'user4' }
          ],
          neutral: [
            { title: 'Question about raises', score: 5, sentiment_score: 0.0, author: 'user5' },
            { title: 'When do we get updates?', score: 3, sentiment_score: 0.1, author: 'user6' }
          ]
        }
      };
      
      setData(mockData);
      setLastUpdated(new Date());
      setDataTimeframe('Last 14 days (Demo Data)');
    } catch (err) {
      setError('Failed to fetch data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    fetchData();
  };

  if (loading && !data) {
    return (
      <div className="dashboard-container">
        <div className="loading">
          <h2>🔄 Loading compensation analysis...</h2>
          <p>Analyzing sentiment and generating insights...</p>
          <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
            This process collects recent posts from r/amazonfc and analyzes employee sentiment about compensation changes.
          </div>
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
  const sentimentChartData = [
    { name: 'Positive', value: data.sentiment_summary.positive, color: COLORS.positive },
    { name: 'Negative', value: data.sentiment_summary.negative, color: COLORS.negative },
    { name: 'Neutral', value: data.sentiment_summary.neutral, color: COLORS.neutral }
  ];

  const compensationData = data.detailed_insights.compensation_amounts.most_mentioned.map(([amount, count]) => ({
    amount,
    count
  }));

  const topicData = data.detailed_insights.topic_analysis.most_common_topics.map(([topic, count]) => ({
    topic: topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    count
  }));

  return (
    <div className="dashboard-container">
      <div className="header">
        <h1>💰 Compensation Sentiment Analysis Dashboard</h1>
        <p>Real-time insights from Amazon FC employee discussions on Reddit</p>
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', opacity: 0.9 }}>
          <strong>Data Source:</strong> r/amazonfc subreddit • <strong>Analysis:</strong> Sentiment + Engagement metrics
        </div>
      </div>

      {/* Data Freshness Indicator */}
      <DataFreshnessIndicator 
        lastUpdated={lastUpdated} 
        dataTimeframe={dataTimeframe}
      />

      {/* Refresh Controls */}
      <RefreshControls 
        onRefresh={handleRefresh}
        loading={loading}
        autoRefresh={autoRefresh}
        setAutoRefresh={setAutoRefresh}
      />

      {/* Key Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{data.total_posts}</div>
          <div className="stat-label">Total Posts Analyzed</div>
          <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
            From {dataTimeframe}
          </div>
        </div>
        <div className="stat-card">
          <div className={`stat-value ${data.detailed_insights.sentiment_analysis.overall_sentiment}`}>
            {data.detailed_insights.sentiment_analysis.sentiment_distribution.positive_percentage}%
          </div>
          <div className="stat-label">Positive Sentiment</div>
          <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
            Employee satisfaction level
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.detailed_insights.engagement_analysis.high_engagement_posts}</div>
          <div className="stat-label">High Engagement Posts</div>
          <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
            Posts with >10 upvotes
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.detailed_insights.engagement_analysis.average_score}</div>
          <div className="stat-label">Average Post Score</div>
          <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
            Community engagement level
          </div>
        </div>
      </div>

      {/* Sentiment Distribution Chart */}
      <div className="chart-container">
        <h2>📊 Sentiment Distribution</h2>
        <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
          How employees feel about recent compensation changes
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={sentimentChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(1)}%)`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {sentimentChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Charts Grid */}
      <div className="posts-grid">
        {/* Compensation Amounts */}
        <div className="chart-container">
          <h3>💵 Most Discussed Amounts</h3>
          <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
            Salary figures mentioned in discussions
          </div>
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
          <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
            What employees are talking about most
          </div>
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
        <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
          Posts generating the most community discussion and engagement
        </div>
        <div className="posts-grid">
          {data.top_posts.slice(0, 6).map((post, index) => (
            <div key={index} className="post-card">
              <div className="post-title">{post.title}</div>
              <div className="post-meta">
                👤 u/{post.author} | ⬆️ {post.score} upvotes
              </div>
              <span className={`sentiment-badge sentiment-${post.sentiment.sentiment}`}>
                {post.sentiment.sentiment} ({post.sentiment.score.toFixed(2)})
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Key Insights */}
      <div className="chart-container">
        <h2>🔍 Key Insights</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          <div style={{ padding: '1rem', backgroundColor: '#e8f5e8', borderRadius: '8px' }}>
            <strong>✅ Overall Sentiment:</strong> Employee sentiment about compensation changes is <strong>POSITIVE</strong> ({data.detailed_insights.sentiment_analysis.sentiment_distribution.positive_percentage}%)
          </div>
          <div style={{ padding: '1rem', backgroundColor: '#f0f8ff', borderRadius: '8px' }}>
            <strong>💰 Most Discussed:</strong> {data.detailed_insights.compensation_amounts.most_mentioned[0][0]} raises mentioned {data.detailed_insights.compensation_amounts.most_mentioned[0][1]} times
          </div>
          <div style={{ padding: '1rem', backgroundColor: '#fff3e0', borderRadius: '8px' }}>
            <strong>🔥 Engagement:</strong> {data.detailed_insights.engagement_analysis.most_engaging_sentiment.charAt(0).toUpperCase() + data.detailed_insights.engagement_analysis.most_engaging_sentiment.slice(1)} posts generate the most discussion
          </div>
          <div style={{ padding: '1rem', backgroundColor: '#f3e5f5', borderRadius: '8px' }}>
            <strong>📈 Activity:</strong> {data.detailed_insights.engagement_analysis.high_engagement_posts} posts have high engagement indicating active community discussion
          </div>
          <div style={{ padding: '1rem', backgroundColor: '#fff8e1', borderRadius: '8px' }}>
            <strong>⏰ Data Freshness:</strong> Analysis covers {dataTimeframe.toLowerCase()} and updates when new Reddit data is collected
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', padding: '2rem', color: '#666', background: 'white', borderRadius: '8px' }}>
        <h3>📊 About This Dashboard</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <strong>🔄 Update Frequency</strong>
            <p>Manual refresh or auto-refresh every 5 minutes</p>
          </div>
          <div>
            <strong>📅 Data Coverage</strong>
            <p>Last 14 days of r/amazonfc posts</p>
          </div>
          <div>
            <strong>🎯 Analysis Type</strong>
            <p>Sentiment analysis + engagement metrics</p>
          </div>
          <div>
            <strong>📈 Metrics Tracked</strong>
            <p>Sentiment, compensation amounts, facility discussions</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;