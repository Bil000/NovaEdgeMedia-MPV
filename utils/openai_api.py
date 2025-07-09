import json
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai.api_key = OPENAI_API_KEY

def generate_marketing_report(campaign_name, target_audience, budget, duration, objectives, channels="", current_metrics="", real_ads_data=None):
    """
    Generate a comprehensive marketing campaign report using OpenAI GPT-4o
    
    Args:
        campaign_name (str): Name of the marketing campaign
        target_audience (str): Description of target audience
        budget (float): Campaign budget
        duration (int): Campaign duration in days
        objectives (str): Campaign objectives
        channels (str): Marketing channels (optional)
        current_metrics (str): Current performance metrics (optional)
        real_ads_data (dict): Real advertising data from connected platforms (optional)
    
    Returns:
        dict: Structured marketing report
    """
    try:
        # Build prompt with real data integration
        real_data_section = ""
        if real_ads_data and real_ads_data.get('connected_platforms'):
            platforms = ', '.join(real_ads_data['connected_platforms'])
            real_data_section = f"""
        
        REAL ADVERTISING DATA INTEGRATION:
        - Connected Platforms: {platforms}
        - Real Campaign Data Available: Yes
        
        Current Platform Performance Summary:
        """
            
            # Add performance summary from real data
            if 'performance' in real_ads_data:
                perf_summary = real_ads_data['performance'].get('summary', {})
                real_data_section += f"""
        - Total Impressions: {perf_summary.get('total_impressions', 'N/A'):,}
        - Total Clicks: {perf_summary.get('total_clicks', 'N/A'):,}
        - Total Spend: ${perf_summary.get('total_spend', 0):,.2f}
        - Average CTR: {perf_summary.get('average_ctr', 0):.2%}
        - Average CPC: ${perf_summary.get('average_cpc', 0):.2f}
        """
            
            # Add campaign insights
            if 'campaigns' in real_ads_data:
                total_campaigns = real_ads_data['campaigns'].get('summary', {}).get('total_campaigns', 0)
                real_data_section += f"""
        - Active Campaigns: {total_campaigns}
        """
        
        # Construct the prompt for marketing analysis
        prompt = f"""
        As an expert marketing strategist with access to real advertising platform data, analyze the following campaign information and provide a comprehensive marketing report in JSON format.

        CAMPAIGN PLANNING DATA:
        - Campaign Name: {campaign_name}
        - Target Audience: {target_audience}
        - Budget: ${budget:,.2f}
        - Duration: {duration} days
        - Objectives: {objectives}
        - Marketing Channels: {channels if channels else 'Not specified'}
        - Current Metrics: {current_metrics if current_metrics else 'Not provided'}
        {real_data_section}

        Please provide a detailed analysis in the following JSON structure. When real advertising data is available, integrate insights from actual platform performance into your recommendations:
        {{
            "executive_summary": "Brief overview of the campaign analysis and key findings, incorporating real data insights when available",
            "budget_analysis": {{
                "daily_budget": "Recommended daily budget allocation based on real performance data",
                "channel_distribution": "How to distribute budget across channels using actual performance insights",
                "roi_projection": "Expected return on investment with benchmarks from real data"
            }},
            "audience_insights": {{
                "demographics": "Key demographic insights enhanced with platform data",
                "behaviors": "Target audience behaviors and preferences from real campaign data",
                "pain_points": "Main challenges and pain points validated by actual performance"
            }},
            "strategy_recommendations": [
                "Specific actionable recommendations optimized using real advertising data insights"
            ],
            "channel_optimization": {{
                "primary_channels": "Most effective channels based on actual platform performance",
                "content_strategy": "Recommended content approach validated by real data",
                "timing_recommendations": "Best times and frequency using performance analytics"
            }},
            "kpi_framework": {{
                "primary_metrics": "Key metrics to track based on proven performance indicators",
                "success_benchmarks": "What constitutes success using real benchmark data",
                "monitoring_frequency": "How often to review performance based on optimization cycles"
            }},
            "risk_assessment": {{
                "potential_challenges": "Possible obstacles identified from real campaign analysis",
                "mitigation_strategies": "How to address risks using proven platform strategies"
            }},
            "platform_integration_insights": {{
                "data_driven_recommendations": "Specific insights derived from connected advertising platforms",
                "cross_platform_opportunities": "Opportunities identified from multi-platform analysis",
                "performance_benchmarks": "Real performance benchmarks from current campaigns"
            }},
            "next_steps": [
                "Immediate actions prioritized by real data insights and platform capabilities"
            ]
        }}

        IMPORTANT: When real advertising data is provided, use it to enhance every recommendation. Compare planned campaign details against actual performance data to provide data-driven insights. If no real data is available, clearly indicate this in your analysis.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior marketing strategist with expertise in campaign optimization, audience analysis, and ROI maximization. Provide detailed, actionable insights based on the campaign data provided."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )

        # Parse the JSON response
        report_data = json.loads(response.choices[0].message.content)
        
        # Add metadata
        report_data["campaign_metadata"] = {
            "campaign_name": campaign_name,
            "generated_at": "Generated using OpenAI GPT-4o",
            "budget": f"${budget:,.2f}",
            "duration": f"{duration} days",
            "daily_budget_estimate": f"${budget/duration:,.2f}" if duration > 0 else "N/A"
        }

        return report_data

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse OpenAI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
