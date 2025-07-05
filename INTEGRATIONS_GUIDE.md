# Google Ads & Meta Ads Integration Guide

## Overview

NovaEdge Media now supports direct integration with Google Ads and Meta (Facebook/Instagram) Ads platforms. This allows your AI marketing assistant to:

- Pull real campaign data and performance metrics
- Generate reports using actual advertising data
- Provide data-driven recommendations based on live platform performance
- Create cross-platform insights and optimization suggestions

## Integration Features

### Google Ads Integration
- **Campaign Management**: View and manage Google Ads campaigns
- **Performance Analytics**: Real-time metrics including impressions, clicks, cost, CTR, CPC
- **Account Information**: Account status, currency, timezone details
- **Budget Management**: Update campaign budgets programmatically

### Meta Ads Integration  
- **Campaign Management**: View Facebook and Instagram ad campaigns
- **Performance Analytics**: Comprehensive insights including spend, conversions, ROI
- **Campaign Controls**: Pause/resume campaigns remotely
- **Account Management**: Business account information and spend caps

### AI Enhancement
- **Data-Driven Reports**: AI analysis incorporates real platform performance
- **Cross-Platform Insights**: Compare performance across Google and Meta
- **Benchmarking**: Use actual data to set realistic performance expectations
- **Optimization Recommendations**: Suggestions based on proven platform data

## Setup Instructions

### Google Ads Setup

1. **Create Google Ads Developer Account**
   - Go to [Google Ads Developers](https://developers.google.com/google-ads/api/docs/first-call/overview)
   - Apply for a developer token

2. **OAuth2 Setup**
   - Create credentials in Google Cloud Console
   - Generate refresh token using OAuth2 flow

3. **Required Environment Variables**
   ```bash
   GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
   GOOGLE_ADS_CLIENT_ID=your_oauth2_client_id
   GOOGLE_ADS_CLIENT_SECRET=your_oauth2_client_secret
   GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
   GOOGLE_ADS_CUSTOMER_ID=your_customer_id
   ```

### Meta Ads Setup

1. **Create Facebook App**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a new app and add Marketing API

2. **Generate Access Token**
   - Use Graph API Explorer or generate programmatically
   - Token needs `ads_management` permission

3. **Required Environment Variables**
   ```bash
   META_ACCESS_TOKEN=your_access_token
   META_APP_ID=your_app_id
   META_APP_SECRET=your_app_secret
   META_AD_ACCOUNT_ID=your_ad_account_id
   ```

## API Endpoints

### Integration Status
- **GET /ads/status** - Check connection status for all platforms
- **GET /ads/accounts** - Get account information from connected platforms

### Campaign Data
- **GET /ads/campaigns** - Retrieve campaigns from all connected platforms
- **GET /ads/performance?days=30** - Get performance data (last 30 days by default)

### Enhanced Report Generation
- **POST /generate-report-with-ads** - Generate AI reports using real advertising data

## Usage Examples

### Check Integration Status
```javascript
fetch('/ads/status')
  .then(response => response.json())
  .then(data => {
    console.log('Connected platforms:', data.status.connected_platforms);
    console.log('Google Ads connected:', data.status.google_ads.connected);
    console.log('Meta Ads connected:', data.status.meta_ads.connected);
  });
```

### Get Real Campaign Data
```javascript
fetch('/ads/campaigns')
  .then(response => response.json())
  .then(data => {
    console.log('Total campaigns:', data.summary.total_campaigns);
    console.log('Platforms:', data.platforms);
    data.campaigns.forEach(campaign => {
      console.log(`${campaign.name} (${campaign.platform})`);
    });
  });
```

### Generate Enhanced Report
```javascript
const campaignData = {
  campaign_name: "Q1 2024 Launch",
  target_audience: "Tech professionals 25-45",
  budget: 10000,
  duration: 30,
  objectives: "Increase brand awareness and drive sales",
  include_real_data: true
};

fetch('/generate-report-with-ads', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(campaignData)
})
.then(response => response.json())
.then(data => {
  console.log('Enhanced report:', data.report);
  console.log('Real data included:', data.real_data_included);
});
```

## Report Enhancements

When advertising platforms are connected, reports include:

### Platform Integration Insights
- **Data-Driven Recommendations**: Insights from actual campaign performance
- **Cross-Platform Opportunities**: Optimization across Google and Meta
- **Performance Benchmarks**: Real benchmarks from current campaigns

### Enhanced Analysis Sections
- **Budget Analysis**: Recommendations based on actual spend data
- **Channel Optimization**: Platform-specific insights from real performance
- **KPI Framework**: Metrics validated by actual campaign data
- **Risk Assessment**: Challenges identified from real campaign analysis

## Security Considerations

### API Key Management
- Store all credentials as environment variables
- Never expose API keys in frontend code
- Rotate access tokens regularly per platform requirements

### Data Privacy
- Adhere to platform privacy policies
- Only access data you have permission to view
- Implement proper data retention policies

### Rate Limiting
- Respect API rate limits for both platforms
- Implement exponential backoff for retries
- Monitor API usage to avoid quota exhaustion

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify all environment variables are set
   - Check token expiration dates
   - Ensure proper API permissions

2. **No Data Returned**
   - Verify account IDs are correct
   - Check date ranges for performance queries
   - Ensure campaigns exist in specified accounts

3. **Rate Limit Errors**
   - Implement proper retry logic
   - Reduce API call frequency
   - Consider caching frequently accessed data

### Debug Mode
Enable debug logging to troubleshoot issues:
```python
import logging
logging.getLogger('integrations').setLevel(logging.DEBUG)
```

## Best Practices

### Performance Optimization
- Cache campaign data for frequently accessed information
- Use batch operations when possible
- Implement proper error handling and retries

### Data Management
- Regularly sync platform data with local database
- Implement data validation for incoming platform data
- Set up monitoring for integration health

### User Experience
- Provide clear feedback when platforms are disconnected
- Show data freshness indicators
- Gracefully handle partial data scenarios

## Future Enhancements

Planned features for advertising integrations:

- **Automated Campaign Creation**: Create campaigns directly from AI recommendations
- **Budget Optimization**: Automatic budget adjustments based on performance
- **A/B Testing Integration**: Manage and analyze test campaigns
- **Real-Time Alerts**: Notifications for performance anomalies
- **Advanced Attribution**: Cross-platform attribution modeling
- **Competitor Analysis**: Integrate competitive intelligence data

## Support

For integration support:
1. Check the logs for specific error messages
2. Verify platform API documentation for changes
3. Test connections using platform-specific tools
4. Review rate limiting and quota usage

The integrations are designed to enhance your marketing analysis with real data while maintaining the flexibility to work without platform connections when needed.