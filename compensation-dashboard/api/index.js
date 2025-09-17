// Simple Express API to serve compensation data
// This can be deployed as a Lambda function or standalone server

const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Path to your Python scripts
const PYTHON_SCRIPT_PATH = '../reddit-data-collector';

// Endpoint to get current analysis data
app.get('/api/analysis', async (req, res) => {
  try {
    // Read the existing analysis file
    const fs = require('fs');
    const analysisPath = path.join(PYTHON_SCRIPT_PATH, 'compensation_sentiment_analysis.json');
    
    if (fs.existsSync(analysisPath)) {
      const data = JSON.parse(fs.readFileSync(analysisPath, 'utf8'));
      res.json({
        success: true,
        data: data,
        lastUpdated: fs.statSync(analysisPath).mtime
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Analysis data not found. Run the collector first.'
      });
    }
  } catch (error) {
    console.error('Error reading analysis data:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to read analysis data'
    });
  }
});

// Endpoint to refresh data (run the collector and analyzer)
app.post('/api/refresh', async (req, res) => {
  try {
    res.json({
      success: true,
      message: 'Data refresh started',
      status: 'processing'
    });

    // Run the data collection and analysis in the background
    const collectCommand = `cd ${PYTHON_SCRIPT_PATH} && python collect_wage_discussions.py`;
    const analyzeCommand = `cd ${PYTHON_SCRIPT_PATH} && python analyze_compensation_sentiment.py`;

    exec(`echo "1" | ${collectCommand}`, (error, stdout, stderr) => {
      if (error) {
        console.error('Collection error:', error);
        return;
      }
      
      console.log('Collection completed, starting analysis...');
      
      exec(analyzeCommand, (error, stdout, stderr) => {
        if (error) {
          console.error('Analysis error:', error);
          return;
        }
        
        console.log('Analysis completed successfully');
      });
    });

  } catch (error) {
    console.error('Error starting refresh:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to start data refresh'
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'API is healthy',
    timestamp: new Date().toISOString()
  });
});

// Get collection status
app.get('/api/status', (req, res) => {
  const fs = require('fs');
  const dbPath = path.join(PYTHON_SCRIPT_PATH, 'reddit_data.db');
  const analysisPath = path.join(PYTHON_SCRIPT_PATH, 'compensation_sentiment_analysis.json');
  
  const status = {
    database_exists: fs.existsSync(dbPath),
    analysis_exists: fs.existsSync(analysisPath),
    last_analysis: null,
    database_size: null
  };

  if (status.analysis_exists) {
    status.last_analysis = fs.statSync(analysisPath).mtime;
  }

  if (status.database_exists) {
    status.database_size = fs.statSync(dbPath).size;
  }

  res.json({
    success: true,
    status: status
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Compensation API server running on port ${PORT}`);
  console.log(`📊 Analysis endpoint: http://localhost:${PORT}/api/analysis`);
  console.log(`🔄 Refresh endpoint: http://localhost:${PORT}/api/refresh`);
  console.log(`❤️  Health check: http://localhost:${PORT}/api/health`);
});

module.exports = app;