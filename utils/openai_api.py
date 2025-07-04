import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_marketing_report(campaign_name, target_audience, budget, duration, objectives, channels="", current_metrics=""):
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
    
    Returns:
        dict: Structured marketing report
    """
    try:
        # Construct the prompt for marketing analysis
        prompt = f"""
        As an expert marketing strategist, analyze the following campaign data and provide a comprehensive marketing report in JSON format.

        Campaign Details:
        - Campaign Name: {campaign_name}
        - Target Audience: {target_audience}
        - Budget: ${budget:,.2f}
        - Duration: {duration} days
        - Objectives: {objectives}
        - Marketing Channels: {channels if channels else 'Not specified'}
        - Current Metrics: {current_metrics if current_metrics else 'Not provided'}

        Please provide a detailed analysis in the following JSON structure:
        {{
            "executive_summary": "Brief overview of the campaign analysis and key findings",
            "budget_analysis": {{
                "daily_budget": "Recommended daily budget allocation",
                "channel_distribution": "How to distribute budget across channels",
                "roi_projection": "Expected return on investment"
            }},
            "audience_insights": {{
                "demographics": "Key demographic insights",
                "behaviors": "Target audience behaviors and preferences",
                "pain_points": "Main challenges and pain points to address"
            }},
            "strategy_recommendations": [
                "Specific actionable recommendations for campaign optimization"
            ],
            "channel_optimization": {{
                "primary_channels": "Most effective channels for this audience",
                "content_strategy": "Recommended content approach",
                "timing_recommendations": "Best times and frequency for engagement"
            }},
            "kpi_framework": {{
                "primary_metrics": "Key metrics to track",
                "success_benchmarks": "What constitutes success",
                "monitoring_frequency": "How often to review performance"
            }},
            "risk_assessment": {{
                "potential_challenges": "Possible obstacles and risks",
                "mitigation_strategies": "How to address identified risks"
            }},
            "next_steps": [
                "Immediate actions to take for campaign launch or optimization"
            ]
        }}

        Ensure all recommendations are specific, actionable, and tailored to the provided campaign details.
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
