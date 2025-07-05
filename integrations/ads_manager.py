import logging
from typing import Dict, List, Optional
from .google_ads_integration import GoogleAdsIntegration
from .meta_ads_integration import MetaAdsIntegration

logger = logging.getLogger(__name__)


class AdsManager:
    """Unified manager for all advertising platform integrations"""

    def __init__(self):
        """Initialize all advertising platform integrations"""
        self.google_ads = GoogleAdsIntegration()
        self.meta_ads = MetaAdsIntegration()
        
        # Track which platforms are connected
        self.connected_platforms = []
        self._check_connections()

    def _check_connections(self):
        """Check which platforms are successfully connected"""
        self.connected_platforms = []
        
        if self.google_ads.is_connected():
            self.connected_platforms.append('google_ads')
            logger.info("Google Ads integration active")
        
        if self.meta_ads.is_connected():
            self.connected_platforms.append('meta_ads')
            logger.info("Meta Ads integration active")
        
        if not self.connected_platforms:
            logger.warning("No advertising platforms connected")

    def get_connection_status(self) -> Dict:
        """Get status of all platform connections"""
        return {
            'google_ads': {
                'connected': self.google_ads.is_connected(),
                'account_id': getattr(self.google_ads, 'customer_id', None)
            },
            'meta_ads': {
                'connected': self.meta_ads.is_connected(),
                'account_id': getattr(self.meta_ads, 'ad_account_id', None)
            },
            'connected_platforms': self.connected_platforms,
            'total_connected': len(self.connected_platforms)
        }

    def get_all_campaigns(self) -> Dict:
        """Get campaigns from all connected platforms"""
        all_campaigns = {
            'campaigns': [],
            'platforms': {},
            'summary': {
                'total_campaigns': 0,
                'platforms_connected': len(self.connected_platforms)
            }
        }
        
        # Get Google Ads campaigns
        if self.google_ads.is_connected():
            try:
                google_campaigns = self.google_ads.get_campaigns()
                all_campaigns['campaigns'].extend(google_campaigns)
                all_campaigns['platforms']['google_ads'] = {
                    'campaign_count': len(google_campaigns),
                    'status': 'connected'
                }
            except Exception as e:
                logger.error(f"Error fetching Google Ads campaigns: {str(e)}")
                all_campaigns['platforms']['google_ads'] = {
                    'campaign_count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Get Meta Ads campaigns
        if self.meta_ads.is_connected():
            try:
                meta_campaigns = self.meta_ads.get_campaigns()
                all_campaigns['campaigns'].extend(meta_campaigns)
                all_campaigns['platforms']['meta_ads'] = {
                    'campaign_count': len(meta_campaigns),
                    'status': 'connected'
                }
            except Exception as e:
                logger.error(f"Error fetching Meta Ads campaigns: {str(e)}")
                all_campaigns['platforms']['meta_ads'] = {
                    'campaign_count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        all_campaigns['summary']['total_campaigns'] = len(all_campaigns['campaigns'])
        return all_campaigns

    def get_all_performance_data(self, days: int = 30) -> Dict:
        """Get performance data from all connected platforms"""
        performance_data = {
            'platforms': {},
            'summary': {
                'total_impressions': 0,
                'total_clicks': 0,
                'total_spend': 0,
                'total_conversions': 0,
                'average_ctr': 0,
                'average_cpc': 0,
                'platforms_count': 0
            },
            'date_range_days': days
        }
        
        platform_ctrs = []
        platform_cpcs = []
        
        # Get Google Ads performance
        if self.google_ads.is_connected():
            try:
                google_data = self.google_ads.get_campaign_performance(days=days)
                if google_data:
                    performance_data['platforms']['google_ads'] = google_data
                    
                    # Add to summary
                    summary = google_data.get('summary', {})
                    performance_data['summary']['total_impressions'] += summary.get('impressions', 0)
                    performance_data['summary']['total_clicks'] += summary.get('clicks', 0)
                    performance_data['summary']['total_spend'] += summary.get('cost', 0)
                    performance_data['summary']['total_conversions'] += summary.get('conversions', 0)
                    
                    if summary.get('ctr', 0) > 0:
                        platform_ctrs.append(summary['ctr'])
                    if summary.get('average_cpc', 0) > 0:
                        platform_cpcs.append(summary['average_cpc'])
                    
                    performance_data['summary']['platforms_count'] += 1
            except Exception as e:
                logger.error(f"Error fetching Google Ads performance: {str(e)}")
        
        # Get Meta Ads performance
        if self.meta_ads.is_connected():
            try:
                meta_data = self.meta_ads.get_campaign_performance(days=days)
                if meta_data:
                    performance_data['platforms']['meta_ads'] = meta_data
                    
                    # Add to summary
                    summary = meta_data.get('summary', {})
                    performance_data['summary']['total_impressions'] += summary.get('impressions', 0)
                    performance_data['summary']['total_clicks'] += summary.get('clicks', 0)
                    performance_data['summary']['total_spend'] += summary.get('spend', 0)
                    performance_data['summary']['total_conversions'] += summary.get('conversions', 0)
                    
                    if summary.get('ctr', 0) > 0:
                        platform_ctrs.append(summary['ctr'])
                    if summary.get('cpc', 0) > 0:
                        platform_cpcs.append(summary['cpc'])
                    
                    performance_data['summary']['platforms_count'] += 1
            except Exception as e:
                logger.error(f"Error fetching Meta Ads performance: {str(e)}")
        
        # Calculate averages
        if platform_ctrs:
            performance_data['summary']['average_ctr'] = sum(platform_ctrs) / len(platform_ctrs)
        if platform_cpcs:
            performance_data['summary']['average_cpc'] = sum(platform_cpcs) / len(platform_cpcs)
        
        return performance_data

    def create_campaign_on_platform(self, platform: str, campaign_data: Dict) -> Optional[str]:
        """Create a campaign on a specific platform"""
        if platform == 'google_ads' and self.google_ads.is_connected():
            return self.google_ads.create_campaign(campaign_data)
        elif platform == 'meta_ads' and self.meta_ads.is_connected():
            return self.meta_ads.create_campaign(campaign_data)
        else:
            logger.error(f"Platform {platform} not connected or not supported")
            return None

    def update_campaign_budget(self, platform: str, campaign_id: str, new_budget: float) -> bool:
        """Update campaign budget on a specific platform"""
        if platform == 'google_ads' and self.google_ads.is_connected():
            return self.google_ads.update_campaign_budget(campaign_id, new_budget)
        elif platform == 'meta_ads' and self.meta_ads.is_connected():
            return self.meta_ads.update_campaign_budget(campaign_id, new_budget)
        else:
            logger.error(f"Platform {platform} not connected or not supported")
            return False

    def pause_campaign(self, platform: str, campaign_id: str) -> bool:
        """Pause a campaign on a specific platform"""
        if platform == 'meta_ads' and self.meta_ads.is_connected():
            return self.meta_ads.pause_campaign(campaign_id)
        else:
            logger.warning(f"Pause functionality not implemented for {platform}")
            return False

    def resume_campaign(self, platform: str, campaign_id: str) -> bool:
        """Resume a campaign on a specific platform"""
        if platform == 'meta_ads' and self.meta_ads.is_connected():
            return self.meta_ads.resume_campaign(campaign_id)
        else:
            logger.warning(f"Resume functionality not implemented for {platform}")
            return False

    def get_account_info(self) -> Dict:
        """Get account information from all connected platforms"""
        accounts = {}
        
        if self.google_ads.is_connected():
            accounts['google_ads'] = self.google_ads.get_account_info()
        
        if self.meta_ads.is_connected():
            accounts['meta_ads'] = self.meta_ads.get_account_info()
        
        return accounts

    def generate_cross_platform_insights(self, performance_data: Dict) -> Dict:
        """Generate insights comparing performance across platforms"""
        insights = {
            'platform_comparison': {},
            'recommendations': [],
            'top_performers': {},
            'optimization_opportunities': []
        }
        
        platforms = performance_data.get('platforms', {})
        
        # Compare platform performance
        for platform_name, platform_data in platforms.items():
            summary = platform_data.get('summary', {})
            
            insights['platform_comparison'][platform_name] = {
                'total_spend': summary.get('spend', summary.get('cost', 0)),
                'total_clicks': summary.get('clicks', 0),
                'total_impressions': summary.get('impressions', 0),
                'ctr': summary.get('ctr', 0),
                'cpc': summary.get('cpc', summary.get('average_cpc', 0)),
                'conversions': summary.get('conversions', 0)
            }
        
        # Generate recommendations based on cross-platform data
        if len(platforms) > 1:
            # Find best performing platform by CTR
            best_ctr_platform = max(
                platforms.keys(),
                key=lambda p: platforms[p].get('summary', {}).get('ctr', 0),
                default=None
            )
            
            if best_ctr_platform:
                insights['recommendations'].append(
                    f"Consider increasing budget allocation to {best_ctr_platform.replace('_', ' ').title()} "
                    f"which shows the highest CTR performance"
                )
            
            # Find cost efficiency opportunities
            lowest_cpc_platform = min(
                platforms.keys(),
                key=lambda p: platforms[p].get('summary', {}).get('cpc', platforms[p].get('summary', {}).get('average_cpc', float('inf'))),
                default=None
            )
            
            if lowest_cpc_platform:
                insights['recommendations'].append(
                    f"{lowest_cpc_platform.replace('_', ' ').title()} shows the most cost-efficient clicks. "
                    f"Consider optimizing other platforms to match this performance"
                )
        
        return insights