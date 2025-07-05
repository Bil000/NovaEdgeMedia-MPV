import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.exceptions import FacebookRequestError

logger = logging.getLogger(__name__)


class MetaAdsIntegration:
    """Meta (Facebook/Instagram) Ads API integration for campaign management and reporting"""

    def __init__(self):
        """Initialize Meta Ads client"""
        self.api = None
        self.ad_account_id = None
        self.ad_account = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Meta Ads API client"""
        try:
            # Check for required environment variables
            access_token = os.getenv('META_ACCESS_TOKEN')
            app_id = os.getenv('META_APP_ID')
            app_secret = os.getenv('META_APP_SECRET')
            ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
            
            if not all([access_token, app_id, app_secret, ad_account_id]):
                missing = []
                if not access_token: missing.append('META_ACCESS_TOKEN')
                if not app_id: missing.append('META_APP_ID')
                if not app_secret: missing.append('META_APP_SECRET')
                if not ad_account_id: missing.append('META_AD_ACCOUNT_ID')
                logger.warning(f"Missing Meta Ads credentials: {missing}")
                return
            
            # Initialize API
            FacebookAdsApi.init(
                access_token=access_token,
                app_id=app_id,
                app_secret=app_secret
            )
            
            # Set up ad account
            self.ad_account_id = ad_account_id if ad_account_id.startswith('act_') else f'act_{ad_account_id}'
            self.ad_account = AdAccount(self.ad_account_id)
            self.api = FacebookAdsApi.get_default_api()
            
            # Test connection
            account_info = self.ad_account.api_get(fields=['name', 'account_status'])
            logger.info(f"Meta Ads client initialized successfully for account: {account_info.get('name')}")
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error during initialization: {e}")
            self.api = None
        except Exception as e:
            logger.error(f"Failed to initialize Meta Ads client: {str(e)}")
            self.api = None

    def is_connected(self) -> bool:
        """Check if Meta Ads connection is active"""
        return self.api is not None and self.ad_account is not None

    def get_campaigns(self) -> List[Dict]:
        """Retrieve all campaigns from Meta Ads account"""
        if not self.is_connected():
            return []

        try:
            campaigns = self.ad_account.get_campaigns(fields=[
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.status,
                Campaign.Field.objective,
                Campaign.Field.created_time,
                Campaign.Field.start_time,
                Campaign.Field.stop_time,
                Campaign.Field.daily_budget,
                Campaign.Field.lifetime_budget
            ])
            
            campaign_list = []
            for campaign in campaigns:
                campaign_data = {
                    'id': campaign.get('id'),
                    'name': campaign.get('name'),
                    'status': campaign.get('status'),
                    'objective': campaign.get('objective'),
                    'created_time': campaign.get('created_time'),
                    'start_time': campaign.get('start_time'),
                    'stop_time': campaign.get('stop_time'),
                    'daily_budget': campaign.get('daily_budget'),
                    'lifetime_budget': campaign.get('lifetime_budget'),
                    'platform': 'meta_ads'
                }
                campaign_list.append(campaign_data)
            
            logger.info(f"Retrieved {len(campaign_list)} campaigns from Meta Ads")
            return campaign_list
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error retrieving campaigns: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving Meta Ads campaigns: {str(e)}")
            return []

    def get_campaign_performance(self, campaign_id: str = None, days: int = 30) -> Dict:
        """Get campaign performance metrics"""
        if not self.is_connected():
            return {}

        try:
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get insights
            if campaign_id:
                # Get insights for specific campaign
                campaign = Campaign(campaign_id)
                insights = campaign.get_insights(
                    fields=[
                        AdsInsights.Field.campaign_id,
                        AdsInsights.Field.campaign_name,
                        AdsInsights.Field.impressions,
                        AdsInsights.Field.clicks,
                        AdsInsights.Field.spend,
                        AdsInsights.Field.ctr,
                        AdsInsights.Field.cpc,
                        AdsInsights.Field.conversions,
                        AdsInsights.Field.conversion_rate_ranking,
                        AdsInsights.Field.cost_per_conversion
                    ],
                    params={
                        'time_range': {
                            'since': str(start_date),
                            'until': str(end_date)
                        },
                        'level': 'campaign'
                    }
                )
            else:
                # Get insights for all campaigns
                insights = self.ad_account.get_insights(
                    fields=[
                        AdsInsights.Field.campaign_id,
                        AdsInsights.Field.campaign_name,
                        AdsInsights.Field.impressions,
                        AdsInsights.Field.clicks,
                        AdsInsights.Field.spend,
                        AdsInsights.Field.ctr,
                        AdsInsights.Field.cpc,
                        AdsInsights.Field.conversions,
                        AdsInsights.Field.conversion_rate_ranking,
                        AdsInsights.Field.cost_per_conversion
                    ],
                    params={
                        'time_range': {
                            'since': str(start_date),
                            'until': str(end_date)
                        },
                        'level': 'campaign'
                    }
                )
            
            performance_data = {}
            total_metrics = {
                'impressions': 0,
                'clicks': 0,
                'spend': 0,
                'conversions': 0
            }
            
            for insight in insights:
                campaign_data = {
                    'name': insight.get('campaign_name', 'Unknown'),
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'spend': float(insight.get('spend', 0)),
                    'ctr': float(insight.get('ctr', 0)),
                    'cpc': float(insight.get('cpc', 0)),
                    'conversions': int(insight.get('conversions', 0)),
                    'cost_per_conversion': float(insight.get('cost_per_conversion', 0))
                }
                
                # Calculate conversion rate
                if campaign_data['clicks'] > 0:
                    campaign_data['conversion_rate'] = (campaign_data['conversions'] / campaign_data['clicks']) * 100
                else:
                    campaign_data['conversion_rate'] = 0
                
                performance_data[insight.get('campaign_id')] = campaign_data
                
                # Add to totals
                total_metrics['impressions'] += campaign_data['impressions']
                total_metrics['clicks'] += campaign_data['clicks']
                total_metrics['spend'] += campaign_data['spend']
                total_metrics['conversions'] += campaign_data['conversions']
            
            # Calculate overall metrics
            if total_metrics['impressions'] > 0:
                total_metrics['ctr'] = (total_metrics['clicks'] / total_metrics['impressions']) * 100
            if total_metrics['clicks'] > 0:
                total_metrics['cpc'] = total_metrics['spend'] / total_metrics['clicks']
                total_metrics['conversion_rate'] = (total_metrics['conversions'] / total_metrics['clicks']) * 100
            if total_metrics['conversions'] > 0:
                total_metrics['cost_per_conversion'] = total_metrics['spend'] / total_metrics['conversions']
            
            result = {
                'campaigns': performance_data,
                'summary': total_metrics,
                'date_range': {
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                },
                'platform': 'meta_ads'
            }
            
            logger.info(f"Retrieved performance data for {len(performance_data)} Meta Ads campaigns")
            return result
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error retrieving performance: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error retrieving Meta Ads performance: {str(e)}")
            return {}

    def create_campaign(self, campaign_data: Dict) -> Optional[str]:
        """Create a new campaign in Meta Ads"""
        if not self.is_connected():
            return None

        try:
            # Create campaign
            campaign = Campaign(parent_id=self.ad_account_id)
            campaign.update({
                Campaign.Field.name: campaign_data['name'],
                Campaign.Field.objective: campaign_data.get('objective', Campaign.Objective.link_clicks),
                Campaign.Field.status: Campaign.Status.paused,  # Start paused for safety
                Campaign.Field.special_ad_categories: []
            })
            
            # Set budget if provided
            if 'daily_budget' in campaign_data:
                campaign.update({
                    Campaign.Field.daily_budget: int(campaign_data['daily_budget'] * 100)  # Convert to cents
                })
            elif 'lifetime_budget' in campaign_data:
                campaign.update({
                    Campaign.Field.lifetime_budget: int(campaign_data['lifetime_budget'] * 100)  # Convert to cents
                })
            
            campaign.remote_create()
            
            campaign_id = campaign.get_id()
            logger.info(f"Created Meta Ads campaign: {campaign_data['name']} (ID: {campaign_id})")
            return campaign_id
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error creating campaign: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating Meta Ads campaign: {str(e)}")
            return None

    def update_campaign_budget(self, campaign_id: str, new_budget: float, budget_type: str = 'daily') -> bool:
        """Update campaign budget"""
        if not self.is_connected():
            return False

        try:
            campaign = Campaign(campaign_id)
            
            if budget_type == 'daily':
                campaign.api_update({
                    Campaign.Field.daily_budget: int(new_budget * 100)  # Convert to cents
                })
            else:
                campaign.api_update({
                    Campaign.Field.lifetime_budget: int(new_budget * 100)  # Convert to cents
                })
            
            logger.info(f"Updated Meta Ads campaign {campaign_id} {budget_type} budget to ${new_budget}")
            return True
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error updating budget: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating Meta Ads campaign budget: {str(e)}")
            return False

    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign"""
        if not self.is_connected():
            return False

        try:
            campaign = Campaign(campaign_id)
            campaign.api_update({
                Campaign.Field.status: Campaign.Status.paused
            })
            
            logger.info(f"Paused Meta Ads campaign {campaign_id}")
            return True
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error pausing campaign: {e}")
            return False
        except Exception as e:
            logger.error(f"Error pausing Meta Ads campaign: {str(e)}")
            return False

    def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a campaign"""
        if not self.is_connected():
            return False

        try:
            campaign = Campaign(campaign_id)
            campaign.api_update({
                Campaign.Field.status: Campaign.Status.active
            })
            
            logger.info(f"Resumed Meta Ads campaign {campaign_id}")
            return True
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error resuming campaign: {e}")
            return False
        except Exception as e:
            logger.error(f"Error resuming Meta Ads campaign: {str(e)}")
            return False

    def get_account_info(self) -> Dict:
        """Get Meta Ads account information"""
        if not self.is_connected():
            return {}

        try:
            account_info = self.ad_account.api_get(fields=[
                'id',
                'name',
                'account_status',
                'currency',
                'timezone_name',
                'business_name',
                'spend_cap'
            ])
            
            return {
                'id': account_info.get('id'),
                'name': account_info.get('name'),
                'status': account_info.get('account_status'),
                'currency': account_info.get('currency'),
                'timezone': account_info.get('timezone_name'),
                'business_name': account_info.get('business_name'),
                'spend_cap': account_info.get('spend_cap'),
                'platform': 'meta_ads'
            }
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error retrieving account info: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error retrieving Meta Ads account info: {str(e)}")
            return {}