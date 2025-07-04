# NovaEdge Media - AI Marketing Assistant

A comprehensive SaaS AI marketing assistant that helps businesses generate intelligent marketing campaign reports using OpenAI's GPT-4o model.

## Features

- **AI-Powered Analysis**: Generate comprehensive marketing reports using OpenAI GPT-4o
- **Campaign Management**: Store and manage marketing campaigns in PostgreSQL database
- **Professional UI**: Modern, responsive web interface with dark blue theme
- **Real-time Validation**: Client-side form validation with error handling
- **Report Storage**: Save generated reports for future reference
- **RESTful API**: Complete API endpoints for campaigns and reports

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT-4o
- **Frontend**: Vanilla JavaScript with Bootstrap 5
- **Styling**: Custom CSS with modern design system

## API Endpoints

### Campaign Management
- `POST /generate-report` - Generate AI marketing report
- `GET /campaigns` - Get all campaigns
- `GET /campaigns/<id>` - Get specific campaign with reports
- `GET /reports` - Get all reports

### Report Generation
The main endpoint accepts campaign data and returns comprehensive analysis:

```json
{
  "campaign_name": "Launch Promo",
  "target_audience": "Young professionals aged 25-35",
  "budget": 5000,
  "duration": 30,
  "objectives": "Increase brand awareness and drive sales",
  "channels": "Social Media, Email, PPC",
  "current_metrics": "Current reach: 10K"
}
```

## Database Schema

### Campaign Table
- `id` - Primary key
- `campaign_name` - Campaign name
- `target_audience` - Target audience description
- `budget` - Campaign budget
- `duration` - Campaign duration in days
- `objectives` - Campaign objectives
- `channels` - Marketing channels (optional)
- `current_metrics` - Current metrics (optional)
- `created_at` - Creation timestamp

### Report Table
- `id` - Primary key
- `campaign_id` - Foreign key to Campaign
- `report_data` - JSON report data
- `generated_at` - Generation timestamp

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o access
- `DATABASE_URL` - PostgreSQL connection URL
- `SESSION_SECRET` - Flask session secret (optional)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export DATABASE_URL="postgresql://..."
```

3. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Open the web interface
2. Fill in campaign details:
   - Campaign name
   - Target audience description
   - Budget and duration
   - Campaign objectives
   - Marketing channels (optional)
   - Current metrics (optional)
3. Click "Generate AI Report"
4. View comprehensive analysis with:
   - Executive summary
   - Budget analysis
   - Audience insights
   - Strategy recommendations
   - Channel optimization
   - KPI framework
   - Risk assessment
   - Next steps

## Report Features

The AI generates detailed reports including:
- **Executive Summary**: Overview of campaign analysis
- **Budget Analysis**: Daily budget allocation and ROI projections
- **Audience Insights**: Demographics, behaviors, and pain points
- **Strategy Recommendations**: Actionable optimization suggestions
- **Channel Optimization**: Best channels and content strategy
- **KPI Framework**: Key metrics and success benchmarks
- **Risk Assessment**: Potential challenges and mitigation strategies
- **Next Steps**: Immediate actions for campaign success

## Development

The application uses:
- Flask for the web framework
- SQLAlchemy for database ORM
- Flask-Migrate for database migrations
- OpenAI Python client for AI integration
- Bootstrap 5 for responsive UI
- Custom CSS for professional styling

## License

This project is proprietary software for NovaEdge Media.