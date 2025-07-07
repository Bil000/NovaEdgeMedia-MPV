import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from utils.openai_api import generate_marketing_report
from utils.audience_insights import analyze_deep_audience_insights, filter_audience_noise, generate_precision_targeting_recommendations
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

@app.route('/credentials/google-ads', methods=['POST'])
def save_google_ads_credentials():
    """Save Google Ads credentials securely"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No credentials provided'}), 400

        # Validate required fields
        required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token', 'customer_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Store credentials securely (in production, use encrypted storage)
        import os
        os.environ['GOOGLE_ADS_DEVELOPER_TOKEN'] = data['developer_token']
        os.environ['GOOGLE_ADS_CLIENT_ID'] = data['client_id']
        os.environ['GOOGLE_ADS_CLIENT_SECRET'] = data['client_secret']
        os.environ['GOOGLE_ADS_REFRESH_TOKEN'] = data['refresh_token']
        os.environ['GOOGLE_ADS_CUSTOMER_ID'] = data['customer_id']

        # Reinitialize Google Ads integration with new credentials
        ads_manager.google_ads._initialize_client()
        
        # Test the connection
        if ads_manager.google_ads.is_connected():
            # Update connection status
            ads_manager._check_connections()
            app.logger.info("Google Ads credentials saved and validated successfully")
            return jsonify({'success': True, 'message': 'Google Ads connected successfully'})
        else:
            return jsonify({
                'success': False, 
                'error': 'Failed to connect with provided credentials. Please verify your credentials and try again.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error saving Google Ads credentials: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to save credentials: {str(e)}'
        }), 500

@app.route('/credentials/meta-ads', methods=['POST'])
def save_meta_ads_credentials():
    """Save Meta Ads credentials securely"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No credentials provided'}), 400

        # Validate required fields
        required_fields = ['access_token', 'app_id', 'app_secret', 'ad_account_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Store credentials securely (in production, use encrypted storage)
        import os
        os.environ['META_ACCESS_TOKEN'] = data['access_token']
        os.environ['META_APP_ID'] = data['app_id']
        os.environ['META_APP_SECRET'] = data['app_secret']
        os.environ['META_AD_ACCOUNT_ID'] = data['ad_account_id']

        # Reinitialize Meta Ads integration with new credentials
        ads_manager.meta_ads._initialize_client()
        
        # Test the connection
        if ads_manager.meta_ads.is_connected():
            # Update connection status
            ads_manager._check_connections()
            app.logger.info("Meta Ads credentials saved and validated successfully")
            return jsonify({'success': True, 'message': 'Meta Ads connected successfully'})
        else:
            return jsonify({
                'success': False, 
                'error': 'Failed to connect with provided credentials. Please verify your credentials and try again.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error saving Meta Ads credentials: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to save credentials: {str(e)}'
        }), 500

@app.route('/credentials/google-ads/test', methods=['POST'])
def test_google_ads_connection():
    """Test Google Ads connection without saving credentials"""
    try:
        # Test current connection
        if ads_manager.google_ads.is_connected():
            account_info = ads_manager.google_ads.get_account_info()
            return jsonify({
                'success': True, 
                'message': 'Google Ads connection successful',
                'account_info': account_info
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Google Ads not connected. Please add your credentials first.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error testing Google Ads connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Connection test failed: {str(e)}'
        }), 500

@app.route('/credentials/meta-ads/test', methods=['POST'])
def test_meta_ads_connection():
    """Test Meta Ads connection without saving credentials"""
    try:
        # Test current connection
        if ads_manager.meta_ads.is_connected():
            account_info = ads_manager.meta_ads.get_account_info()
            return jsonify({
                'success': True, 
                'message': 'Meta Ads connection successful',
                'account_info': account_info
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Meta Ads not connected. Please add your credentials first.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error testing Meta Ads connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Connection test failed: {str(e)}'
        }), 500

@app.route('/audience-insights', methods=['POST'])
def generate_audience_insights():
    """Generate deep audience insights with smart targeting and segmentation"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Required field validation
        if not data.get('target_audience'):
            return jsonify({
                'success': False,
                'error': 'Target audience description is required'
            }), 400

        app.logger.info(f"Generating audience insights for: {data.get('target_audience')[:50]}...")

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

        # Prepare campaign context
        campaign_context = {
            'campaign_name': data.get('campaign_name', ''),
            'objectives': data.get('objectives', ''),
            'budget': data.get('budget', 0)
        }

        # Generate deep audience insights
        insights = analyze_deep_audience_insights(
            target_audience=data.get('target_audience'),
            campaign_data=campaign_context if any(campaign_context.values()) else None,
            real_ads_data=real_ads_data if real_ads_data else None
        )

        # Generate noise filtering analysis
        audience_data = {'total_users': data.get('estimated_audience_size', 10000)}
        noise_analysis = filter_audience_noise(audience_data)

        # Generate precision targeting recommendations
        precision_recommendations = generate_precision_targeting_recommendations(
            insights=insights,
            campaign_budget=data.get('budget')
        )

        # Combine all insights
        complete_analysis = {
            'audience_insights': insights,
            'noise_filtering': noise_analysis,
            'precision_targeting': precision_recommendations,
            'real_data_integration': {
                'platforms_connected': len(ads_manager.connected_platforms),
                'connected_platforms': ads_manager.connected_platforms,
                'real_data_used': bool(real_ads_data)
            }
        }

        app.logger.info("Deep audience insights generated successfully")

        return jsonify({
            'success': True,
            'insights': complete_analysis
        })

    except Exception as e:
        app.logger.error(f"Error generating audience insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate audience insights: {str(e)}'
        }), 500

@app.route('/precision-targeting', methods=['POST'])
def generate_precision_targeting():
    """Generate precision targeting recommendations with noise reduction"""
    try:
        data = request.get_json()
        if not data or not data.get('target_audience'):
            return jsonify({
                'success': False,
                'error': 'Target audience description is required'
            }), 400

        # Quick precision targeting analysis
        campaign_context = {
            'budget': data.get('budget', 0),
            'objectives': data.get('objectives', ''),
            'channels': data.get('channels', '')
        }

        # Generate basic insights for targeting
        insights = analyze_deep_audience_insights(
            target_audience=data.get('target_audience'),
            campaign_data=campaign_context
        )

        # Generate targeting recommendations
        recommendations = generate_precision_targeting_recommendations(
            insights=insights,
            campaign_budget=data.get('budget')
        )

        # Add noise filtering insights
        audience_size = data.get('estimated_audience_size', 5000)
        noise_analysis = filter_audience_noise({'total_users': audience_size})

        return jsonify({
            'success': True,
            'targeting_recommendations': recommendations,
            'audience_quality': {
                'original_size': noise_analysis['original_size'],
                'filtered_size': noise_analysis['filtered_size'],
                'quality_score': noise_analysis['quality_score'],
                'noise_reduction': {
                    'bots_filtered': True,
                    'irrelevant_users_filtered': True,
                    'quality_improvement': noise_analysis['quality_metrics']['quality_improvement']
                }
            }
        })

    except Exception as e:
        app.logger.error(f"Error generating precision targeting: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate precision targeting: {str(e)}'
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
