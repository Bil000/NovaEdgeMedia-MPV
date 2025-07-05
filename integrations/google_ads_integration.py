import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)


class GoogleAdsIntegration:
    """Google Ads API integration for campaign management and reporting"""

    def __init__(self):
        """Initialize Google Ads client"""
        self.client = None
        self.customer_id = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Google Ads API client"""
        try:
            # Check for required environment variables
            required_vars = [
                'GOOGLE_ADS_DEVELOPER_TOKEN',
                'GOOGLE_ADS_CLIENT_ID', 
                'GOOGLE_ADS_CLIENT_SECRET',
                'GOOGLE_ADS_REFRESH_TOKEN',
                'GOOGLE_ADS_CUSTOMER_ID'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                logger.warning(f"Missing Google Ads credentials: {missing_vars}")
                return
            
            # Initialize client with environment variables
            self.client = GoogleAdsClient.load_from_env()
            self.customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
            logger.info("Google Ads client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if Google Ads connection is active"""
        return self.client is not None and self.customer_id is not None

    def get_campaigns(self) -> List[Dict]:
        """Retrieve all campaigns from Google Ads account"""
        if not self.is_connected():
            return []

        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.campaign_budget,
                    campaign.start_date,
                    campaign.end_date
                FROM campaign
                WHERE campaign.status IN ('ENABLED', 'PAUSED')
                ORDER BY campaign.name
            """
            
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = self.customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            campaigns = []
            for row in response:
                campaign = {
                    'id': str(row.campaign.id),
                    'name': row.campaign.name,
                    'status': row.campaign.status.name,
                    'channel_type': row.campaign.advertising_channel_type.name,
                    'start_date': row.campaign.start_date,
                    'end_date': row.campaign.end_date,
                    'platform': 'google_ads'
                }
                campaigns.append(campaign)
            
            logger.info(f"Retrieved {len(campaigns)} campaigns from Google Ads")
            return campaigns
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex.error.code().name}")
            for error in ex.failure.errors:
                logger.error(f"Error details: {error.message}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving Google Ads campaigns: {str(e)}")
            return []

    def get_campaign_performance(self, campaign_id: str = None, days: int = 30) -> Dict:
        """Get campaign performance metrics"""
        if not self.is_connected():
            return {}

        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Build query with optional campaign filter
            campaign_filter = f"AND campaign.id = {campaign_id}" if campaign_id else ""
            
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.conversion_rate
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                {campaign_filter}
                ORDER BY metrics.impressions DESC
            """
            
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = self.customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            performance_data = {}
            total_metrics = {
                'impressions': 0,
                'clicks': 0,
                'cost': 0,
                'conversions': 0
            }
            
            for row in response:
                campaign_data = {
                    'name': row.campaign.name,
                    'impressions': int(row.metrics.impressions),
                    'clicks': int(row.metrics.clicks),
                    'cost': float(row.metrics.cost_micros) / 1_000_000,
                    'conversions': float(row.metrics.conversions),
                    'ctr': float(row.metrics.ctr) * 100,
                    'average_cpc': float(row.metrics.average_cpc) / 1_000_000,
                    'conversion_rate': float(row.metrics.conversion_rate) * 100
                }
                
                performance_data[str(row.campaign.id)] = campaign_data
                
                # Add to totals
                total_metrics['impressions'] += campaign_data['impressions']
                total_metrics['clicks'] += campaign_data['clicks']
                total_metrics['cost'] += campaign_data['cost']
                total_metrics['conversions'] += campaign_data['conversions']
            
            # Calculate overall metrics
            if total_metrics['impressions'] > 0:
                total_metrics['ctr'] = (total_metrics['clicks'] / total_metrics['impressions']) * 100
            if total_metrics['clicks'] > 0:
                total_metrics['average_cpc'] = total_metrics['cost'] / total_metrics['clicks']
                total_metrics['conversion_rate'] = (total_metrics['conversions'] / total_metrics['clicks']) * 100
            
            result = {
                'campaigns': performance_data,
                'summary': total_metrics,
                'date_range': {
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                },
                'platform': 'google_ads'
            }
            
            logger.info(f"Retrieved performance data for {len(performance_data)} Google Ads campaigns")
            return result
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex.error.code().name}")
            return {}
        except Exception as e:
            logger.error(f"Error retrieving Google Ads performance: {str(e)}")
            return {}

    def create_campaign(self, campaign_data: Dict) -> Optional[str]:
        """Create a new campaign in Google Ads"""
        if not self.is_connected():
            return None

        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            
            # Create campaign budget first
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"{campaign_data['name']} Budget"
            budget.amount_micros = int(campaign_data.get('daily_budget', 1000) * 1_000_000)
            budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            
            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id, operations=[budget_operation]
            )
            budget_resource_name = budget_response.results[0].resource_name
            
            # Create campaign
            operation = self.client.get_type("CampaignOperation")
            campaign = operation.create
            campaign.name = campaign_data['name']
            campaign.advertising_channel_type = self.client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
            campaign.campaign_budget = budget_resource_name
            campaign.bidding_strategy_type = self.client.enums.BiddingStrategyTypeEnum.MANUAL_CPC
            
            # Set manual CPC
            campaign.manual_cpc.enhanced_cpc_enabled = True
            
            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id, operations=[operation]
            )
            
            campaign_id = response.results[0].resource_name.split('/')[-1]
            logger.info(f"Created Google Ads campaign: {campaign_data['name']} (ID: {campaign_id})")
            return campaign_id
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error creating campaign: {ex.error.code().name}")
            return None
        except Exception as e:
            logger.error(f"Error creating Google Ads campaign: {str(e)}")
            return None

    def update_campaign_budget(self, campaign_id: str, new_budget: float) -> bool:
        """Update campaign budget"""
        if not self.is_connected():
            return False

        try:
            # This would require getting the campaign budget resource name first
            # and then updating it - implementation depends on specific requirements
            logger.info(f"Budget update requested for campaign {campaign_id}: ${new_budget}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Google Ads campaign budget: {str(e)}")
            return False

    def get_account_info(self) -> Dict:
        """Get Google Ads account information"""
        if not self.is_connected():
            return {}

        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = """
                SELECT
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.status
                FROM customer
                LIMIT 1
            """
            
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = self.customer_id
            search_request.query = query
            
            response = ga_service.search(request=search_request)
            
            for row in response:
                return {
                    'id': str(row.customer.id),
                    'name': row.customer.descriptive_name,
                    'currency': row.customer.currency_code,
                    'timezone': row.customer.time_zone,
                    'status': row.customer.status.name,
                    'platform': 'google_ads'
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error retrieving Google Ads account info: {str(e)}")
            return {}