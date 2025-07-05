import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from utils.openai_api import generate_marketing_report
from integrations.ads_manager import AdsManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
CORS(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Import models after db initialization
from models import Campaign, Report

# Initialize advertising integrations
ads_manager = AdsManager()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Generate marketing campaign report using OpenAI GPT-4"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Required fields validation
        required_fields = ['campaign_name', 'target_audience', 'budget', 'duration', 'objectives']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Validate budget is numeric
        try:
            budget = float(data.get('budget', 0))
            if budget <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Budget must be a positive number'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Budget must be a valid number'
            }), 400

        # Validate duration is numeric
        try:
            duration = int(data.get('duration', 0))
            if duration <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Duration must be a positive number'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Duration must be a valid number'
            }), 400

        app.logger.info(f"Generating report for campaign: {data.get('campaign_name')}")

        # Save campaign to database
        campaign = Campaign(
            campaign_name=data.get('campaign_name'),
            target_audience=data.get('target_audience'),
            budget=budget,
            duration=duration,
            objectives=data.get('objectives'),
            channels=data.get('channels', ''),
            current_metrics=data.get('current_metrics', '')
        )
        
        db.session.add(campaign)
        db.session.commit()

        # Generate report using OpenAI
        report = generate_marketing_report(
            campaign_name=data.get('campaign_name'),
            target_audience=data.get('target_audience'),
            budget=budget,
            duration=duration,
            objectives=data.get('objectives'),
            channels=data.get('channels', ''),
            current_metrics=data.get('current_metrics', '')
        )

        # Save report to database
        report_record = Report(
            campaign_id=campaign.id,
            report_data=report
        )
        db.session.add(report_record)
        db.session.commit()

        app.logger.info("Report generated and saved successfully")

        return jsonify({
            'success': True,
            'report': report,
            'campaign_id': campaign.id,
            'report_id': report_record.id
        })

    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        # Rollback in case of error
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to generate report: {str(e)}'
        }), 500

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    try:
        campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
        return jsonify({
            'success': True,
            'campaigns': [campaign.to_dict() for campaign in campaigns]
        })
    except Exception as e:
        app.logger.error(f"Error fetching campaigns: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch campaigns: {str(e)}'
        }), 500

@app.route('/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get a specific campaign with its reports"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        campaign_data = campaign.to_dict()
        campaign_data['reports'] = [report.to_dict() for report in campaign.reports]
        
        return jsonify({
            'success': True,
            'campaign': campaign_data
        })
    except Exception as e:
        app.logger.error(f"Error fetching campaign: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch campaign: {str(e)}'
        }), 500

@app.route('/reports', methods=['GET'])
def get_reports():
    """Get all reports"""
    try:
        reports = Report.query.order_by(Report.generated_at.desc()).all()
        return jsonify({
            'success': True,
            'reports': [report.to_dict() for report in reports]
        })
    except Exception as e:
        app.logger.error(f"Error fetching reports: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch reports: {str(e)}'
        }), 500

@app.route('/ads/status', methods=['GET'])
def get_ads_status():
    """Get connection status for all advertising platforms"""
    try:
        status = ads_manager.get_connection_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        app.logger.error(f"Error getting ads status: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get ads status: {str(e)}'
        }), 500

@app.route('/ads/campaigns', methods=['GET'])
def get_ads_campaigns():
    """Get campaigns from all connected advertising platforms"""
    try:
        campaigns_data = ads_manager.get_all_campaigns()
        return jsonify({
            'success': True,
            **campaigns_data
        })
    except Exception as e:
        app.logger.error(f"Error fetching ads campaigns: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch ads campaigns: {str(e)}'
        }), 500

@app.route('/ads/performance', methods=['GET'])
def get_ads_performance():
    """Get performance data from all connected advertising platforms"""
    try:
        days = int(request.args.get('days', 30))
        performance_data = ads_manager.get_all_performance_data(days=days)
        
        # Generate cross-platform insights
        insights = ads_manager.generate_cross_platform_insights(performance_data)
        performance_data['insights'] = insights
        
        return jsonify({
            'success': True,
            **performance_data
        })
    except Exception as e:
        app.logger.error(f"Error fetching ads performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch ads performance: {str(e)}'
        }), 500

@app.route('/ads/accounts', methods=['GET'])
def get_ads_accounts():
    """Get account information from all connected platforms"""
    try:
        accounts = ads_manager.get_account_info()
        return jsonify({
            'success': True,
            'accounts': accounts
        })
    except Exception as e:
        app.logger.error(f"Error fetching ads accounts: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch ads accounts: {str(e)}'
        }), 500

@app.route('/generate-report-with-ads', methods=['POST'])
def generate_report_with_ads():
    """Generate marketing report using both form data and real advertising data"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Required fields validation
        required_fields = ['campaign_name', 'target_audience', 'budget', 'duration', 'objectives']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Validate budget and duration
        try:
            budget = float(data.get('budget', 0))
            duration = int(data.get('duration', 0))
            if budget <= 0 or duration <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Budget and duration must be positive numbers'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Budget and duration must be valid numbers'
            }), 400

        app.logger.info(f"Generating enhanced report for campaign: {data.get('campaign_name')}")

        # Get real advertising data if available
        real_ads_data = {}
        if data.get('include_real_data', True):
            try:
                # Get current campaigns and performance
                campaigns_data = ads_manager.get_all_campaigns()
                performance_data = ads_manager.get_all_performance_data(days=30)
                
                real_ads_data = {
                    'campaigns': campaigns_data,
                    'performance': performance_data,
                    'connected_platforms': ads_manager.connected_platforms
                }
                
                app.logger.info(f"Retrieved real ads data from {len(ads_manager.connected_platforms)} platforms")
            except Exception as e:
                app.logger.warning(f"Could not retrieve real ads data: {str(e)}")

        # Save campaign to database
        campaign = Campaign(
            campaign_name=data.get('campaign_name'),
            target_audience=data.get('target_audience'),
            budget=budget,
            duration=duration,
            objectives=data.get('objectives'),
            channels=data.get('channels', ''),
            current_metrics=data.get('current_metrics', '')
        )
        
        db.session.add(campaign)
        db.session.commit()

        # Generate enhanced report using OpenAI with real data
        report = generate_marketing_report(
            campaign_name=data.get('campaign_name'),
            target_audience=data.get('target_audience'),
            budget=budget,
            duration=duration,
            objectives=data.get('objectives'),
            channels=data.get('channels', ''),
            current_metrics=data.get('current_metrics', ''),
            real_ads_data=real_ads_data
        )

        # Add platform integration status to report
        report['platform_integrations'] = {
            'status': ads_manager.get_connection_status(),
            'real_data_included': bool(real_ads_data),
            'connected_platforms': ads_manager.connected_platforms
        }

        # Save report to database
        report_record = Report(
            campaign_id=campaign.id,
            report_data=report
        )
        db.session.add(report_record)
        db.session.commit()

        app.logger.info("Enhanced report generated and saved successfully")

        return jsonify({
            'success': True,
            'report': report,
            'campaign_id': campaign.id,
            'report_id': report_record.id,
            'real_data_included': bool(real_ads_data)
        })

    except Exception as e:
        app.logger.error(f"Error generating enhanced report: {str(e)}")
        # Rollback in case of error
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to generate enhanced report: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
