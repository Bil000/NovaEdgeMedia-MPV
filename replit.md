# NovaEdge Media - AI Marketing Assistant

## Overview

This is a Flask-based web application that serves as an AI-powered marketing assistant. The application allows users to input campaign details and generates comprehensive marketing reports using OpenAI's GPT-4o model. It features a modern, responsive web interface with real-time form validation and interactive report generation.

## System Architecture

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap 5 for styling
- **Design Pattern**: Class-based JavaScript architecture with event-driven interactions
- **UI Framework**: Bootstrap 5 with custom CSS variables for consistent theming
- **Responsiveness**: Mobile-first responsive design using Bootstrap's grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM and Flask-Migrate
- **API Design**: RESTful endpoints with JSON request/response format
- **Data Persistence**: Campaign and report storage with relational database
- **Error Handling**: Comprehensive validation with structured error responses
- **Logging**: Built-in Python logging for debugging and monitoring

### Styling and Assets
- **CSS Architecture**: Custom CSS with CSS variables for theme consistency
- **Color Scheme**: Dark theme with blue gradient primary colors
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **Layout**: Two-column layout with form on left and results on right

## Key Components

### Core Application (app.py)
- **Main Flask Application**: Handles routing and request processing
- **CORS Integration**: Enables cross-origin requests for API flexibility
- **Input Validation**: Multi-layer validation for campaign data
- **Session Management**: Basic session handling with configurable secret key

### OpenAI Integration (utils/openai_api.py)
- **AI Model**: Uses GPT-4o (latest OpenAI model as of May 2024)
- **Prompt Engineering**: Structured prompts for marketing analysis
- **Response Format**: JSON-structured reports with multiple analysis sections
- **Error Handling**: Graceful handling of API failures and rate limits

### Frontend Controller (static/js/app.js)
- **Form Management**: Real-time validation and submission handling
- **State Management**: Multiple UI states (welcome, loading, error, results)
- **User Experience**: Loading indicators and error feedback
- **Input Validation**: Client-side validation before API submission

### User Interface
- **Responsive Design**: Mobile-optimized layout
- **Interactive Elements**: Form validation feedback and loading states
- **Accessibility**: Semantic HTML with proper labels and ARIA attributes
- **Visual Hierarchy**: Clear section separation and visual cues

## Data Flow

1. **User Input**: User fills out campaign form with required fields
2. **Client Validation**: JavaScript validates inputs before submission
3. **API Request**: Form data sent to Flask backend via POST request
4. **Server Validation**: Backend validates and sanitizes input data
5. **AI Processing**: OpenAI API generates structured marketing report
6. **Response Delivery**: JSON report returned to frontend
7. **UI Update**: Results displayed in structured, readable format

## External Dependencies

### Python Dependencies
- **Flask**: Web framework for backend API
- **Flask-CORS**: Cross-origin resource sharing support
- **Flask-SQLAlchemy**: SQLAlchemy integration for Flask
- **Flask-Migrate**: Database migration support
- **OpenAI**: Official OpenAI Python client library
- **psycopg2-binary**: PostgreSQL database adapter

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework via CDN
- **Font Awesome 6.4.0**: Icon library via CDN
- **Vanilla JavaScript**: No additional JavaScript frameworks

### Environment Variables
- **OPENAI_API_KEY**: Required for OpenAI API access
- **SESSION_SECRET**: Optional Flask session security (defaults to dev key)

## Deployment Strategy

### Development Environment
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5000
- **Debug Mode**: Enabled for development
- **Hot Reload**: Automatic reloading on code changes

### Production Considerations
- **Environment Variables**: Secure API key and session secret management
- **Static Assets**: CDN-hosted external dependencies
- **Error Handling**: Comprehensive error responses without exposing internals
- **CORS Configuration**: Configured for cross-origin requests

### File Structure
```
/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── utils/
│   └── openai_api.py     # OpenAI integration
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Custom styling
    └── js/
        └── app.js        # Frontend JavaScript
```

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### Customer Credential Management Implementation
- **User-Friendly Credential Interface**: Added tabbed interface for customers to add their own Google Ads and Meta Ads credentials
- **Secure Credential Storage**: Backend endpoints to securely handle and validate customer API keys
- **Real-time Connection Status**: Live status indicators showing platform connection health
- **Data-Driven AI Reports**: Enhanced OpenAI integration to use real advertising data when available
- **Cross-Platform Analytics**: Unified dashboard comparing performance across Google and Meta platforms

### Technical Architecture Updates
- **Platform Integrations**: Complete Google Ads and Meta Ads API integration with unified ads manager
- **Credential Management**: Secure backend storage and validation of customer API credentials
- **Enhanced AI Analysis**: Real advertising data integration for improved report accuracy
- **User Interface**: Professional tabbed interface for campaign analysis and platform connections

## Changelog

```
Changelog:
- July 05, 2025. Added customer credential management for Google Ads and Meta Ads
- July 04, 2025. Initial setup
```