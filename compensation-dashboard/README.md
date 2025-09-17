# Compensation Sentiment Analysis Dashboard

A modern React dashboard for visualizing sentiment analysis of Amazon FC compensation discussions from Reddit.

## Features

- 📊 **Real-time Sentiment Analysis** - View positive, negative, and neutral sentiment distribution
- 💰 **Compensation Insights** - Track most discussed salary amounts and raises
- 🏢 **Facility Analysis** - See facility-specific compensation discussions
- 🔥 **Engagement Metrics** - Monitor high-engagement posts and trending topics
- 🔄 **Live Data Refresh** - Update data with latest Reddit discussions
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Open browser:**
   Navigate to `http://localhost:3000`

### Deploy to AWS Amplify

1. **Initialize Amplify (if not already done):**
   ```bash
   npm install -g @aws-amplify/cli
   amplify init
   ```

2. **Add hosting:**
   ```bash
   amplify add hosting
   ```
   - Choose "Amazon CloudFront and S3"
   - Choose "DEV (S3 only with HTTP)"

3. **Deploy:**
   ```bash
   amplify publish
   ```

### One-Click Amplify Deployment

[![Deploy to Amplify Console](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy?repo=https://github.com/your-repo/compensation-dashboard)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React App     │    │   API Gateway    │    │  Lambda Function│
│   (Frontend)    │───▶│   (REST API)     │───▶│  (Data Processor)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   Reddit API    │
                                               │   + Database    │
                                               └─────────────────┘
```

## Data Sources

- **Reddit API**: Live compensation discussions from r/amazonfc
- **Sentiment Analysis**: Custom NLP processing for employee sentiment
- **Engagement Metrics**: Upvotes, comments, and discussion activity

## Key Metrics Displayed

### Sentiment Analysis
- Overall sentiment distribution (Positive/Negative/Neutral)
- Sentiment trends over time
- Most engaging sentiment type

### Compensation Data
- Most discussed salary amounts
- Facility-specific compensation discussions
- Raise amounts and frequency

### Engagement Insights
- High-engagement posts (>10 upvotes)
- Average post scores
- Top posts by engagement

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_ENDPOINT=https://your-api-gateway-url.amazonaws.com/prod
REACT_APP_REFRESH_INTERVAL=300000
```

### API Integration

To connect to your actual Reddit data collector:

1. **Create API endpoint** in `src/services/api.js`
2. **Update data fetching** in `src/App.js`
3. **Configure CORS** for your API Gateway

## Customization

### Adding New Charts

1. Import chart component from `recharts`
2. Add data processing logic
3. Create new chart container in JSX

### Styling

- Modify `src/index.css` for global styles
- Component-specific styles in respective files
- Uses CSS Grid and Flexbox for responsive layout

## Performance

- **Lazy Loading**: Components load on demand
- **Data Caching**: API responses cached for 5 minutes
- **Optimized Rendering**: React.memo for expensive components
- **CDN Delivery**: Static assets served via CloudFront

## Security

- **HTTPS Only**: All traffic encrypted
- **CORS Configured**: API access restricted to dashboard domain
- **No Sensitive Data**: No personal information displayed

## Monitoring

- **CloudWatch**: Automatic logging and monitoring
- **Real User Monitoring**: Performance metrics collection
- **Error Tracking**: Automatic error reporting

## Support

For issues or questions:
1. Check the troubleshooting section below
2. Review CloudWatch logs
3. Contact the development team

## Troubleshooting

### Common Issues

**Data not loading:**
- Check API endpoint configuration
- Verify CORS settings
- Check network connectivity

**Charts not displaying:**
- Ensure data format matches expected structure
- Check browser console for errors
- Verify chart dimensions

**Slow performance:**
- Check data payload size
- Monitor API response times
- Review component re-rendering

## License

This project is licensed under the MIT License.