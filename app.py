import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from utils.openai_api import generate_marketing_report

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
CORS(app)

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

        app.logger.info("Report generated successfully")

        return jsonify({
            'success': True,
            'report': report
        })

    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate report: {str(e)}'
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
