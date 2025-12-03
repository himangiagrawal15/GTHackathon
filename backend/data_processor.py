import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    def __init__(self, df):
        self.df = df.copy()
        self.clean_data()
    
    def clean_data(self):
        """Clean and prepare data"""
        # Convert time to datetime
        if 'time' in self.df.columns:
            self.df['time'] = pd.to_datetime(self.df['time'], errors='coerce')
            self.df['date'] = self.df['time'].dt.date
            self.df['day_of_week'] = self.df['time'].dt.day_name()
        
        # Fill NaN values appropriately
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            self.df[col].fillna(0, inplace=True)
        
        # Calculate derived metrics
        self.df['ctr'] = np.where(
            self.df['impressions'] > 0,
            (self.df['clicks'] / self.df['impressions']) * 100,
            0
        )
        
        self.df['cpm'] = np.where(
            self.df['impressions'] > 0,
            (self.df['media_cost_usd'] / self.df['impressions']) * 1000,
            0
        )
        
        self.df['cpc'] = np.where(
            self.df['clicks'] > 0,
            self.df['media_cost_usd'] / self.df['clicks'],
            0
        )
        
        # Calculate aspect ratio (only if columns exist)
        if 'creative_width' in self.df.columns and 'creative_height' in self.df.columns:
            self.df['aspect_ratio'] = np.where(
                self.df['creative_height'] > 0,
                self.df['creative_width'] / self.df['creative_height'],
                0
            )
        else:
            self.df['aspect_ratio'] = 0
        
        # Weekend vs Weekday (only if not already present)
        if 'weekday_cat' not in self.df.columns:
            if 'day_of_week' in self.df.columns:
                self.df['weekday_cat'] = self.df['day_of_week'].apply(
                    lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday'
                )
            elif 'time' in self.df.columns:
                # If we have time but not day_of_week, create it
                self.df['weekday_cat'] = self.df['time'].dt.day_name().apply(
                    lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday'
                )
            else:
                self.df['weekday_cat'] = 'Unknown'
    
    def get_data_summary(self):
        """Get high-level data summary"""
        summary = {
            'total_rows': len(self.df),
            'date_range': {
                'start': str(self.df['time'].min()) if 'time' in self.df.columns else 'N/A',
                'end': str(self.df['time'].max()) if 'time' in self.df.columns else 'N/A'
            },
            'campaigns': {
                'total': int(self.df['campaign_item_id'].nunique()),
                'list': self.df['campaign_item_id'].unique().tolist()
            },
            'platforms': {
                'total': int(self.df['ext_service_name'].nunique()),
                'list': self.df['ext_service_name'].unique().tolist()
            },
            'channels': {
                'total': int(self.df['channel_name'].nunique()),
                'list': self.df['channel_name'].unique().tolist()
            },
            'total_spend': float(self.df['media_cost_usd'].sum()),
            'total_impressions': int(self.df['impressions'].sum()),
            'total_clicks': int(self.df['clicks'].sum()),
            'overall_ctr': float((self.df['clicks'].sum() / self.df['impressions'].sum() * 100) if self.df['impressions'].sum() > 0 else 0)
        }
        return summary
    
    def get_campaign_list(self):
        """Get list of campaigns with basic metrics"""
        campaigns = []
        for campaign_id in self.df['campaign_item_id'].unique():
            campaign_data = self.df[self.df['campaign_item_id'] == campaign_id]
            
            campaigns.append({
                'id': int(campaign_id),
                'impressions': int(campaign_data['impressions'].sum()),
                'clicks': int(campaign_data['clicks'].sum()),
                'spend': float(campaign_data['media_cost_usd'].sum()),
                'ctr': float(campaign_data['ctr'].mean()),
                'days': int(campaign_data['date'].nunique()) if 'date' in campaign_data.columns else 0,
                'platforms': campaign_data['ext_service_name'].unique().tolist()
            })
        
        return sorted(campaigns, key=lambda x: x['spend'], reverse=True)
    
    def get_campaign_analysis(self, campaign_id):
        """Get detailed analysis for a single campaign"""
        campaign_data = self.df[self.df['campaign_item_id'] == campaign_id]
        
        if len(campaign_data) == 0:
            return None
        
        analysis = {
            'campaign_id': int(campaign_id),
            'summary': self._get_campaign_summary(campaign_data),
            'trends': self._get_campaign_trends(campaign_data),
            'channels': self._get_channel_analysis(campaign_data),
            'creatives': self._get_creative_analysis(campaign_data),
            'keywords': self._get_keyword_analysis(campaign_data),
            'landing_pages': self._get_landing_page_analysis(campaign_data),
            'platforms': self._get_platform_breakdown(campaign_data)
        }
        
        return analysis
    
    def _get_campaign_summary(self, data):
        """Get campaign summary metrics"""
        summary = {
            'total_impressions': int(data['impressions'].sum()),
            'total_clicks': int(data['clicks'].sum()),
            'total_spend': float(data['media_cost_usd'].sum()),
            'avg_ctr': float(data['ctr'].mean()),
            'avg_cpm': float(data['cpm'].mean()),
            'avg_cpc': float(data['cpc'].mean()),
            'total_reach': int(data['total_reach'].sum()) if 'total_reach' in data.columns else 0,
            'unique_reach': int(data['unique_reach'].sum()) if 'unique_reach' in data.columns else 0,
            'days_running': int(data['date'].nunique()) if 'date' in data.columns else 0,
            'platforms': data['ext_service_name'].unique().tolist(),
            'channels': data['channel_name'].unique().tolist(),
            'budget': float(data['campaign_budget_usd'].max()) if 'campaign_budget_usd' in data.columns else 0
        }
        return summary
    
    def _get_campaign_trends(self, data):
        """Get daily trends for campaign"""
        if 'date' not in data.columns:
            return {}
        
        daily = data.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'media_cost_usd': 'sum',
            'ctr': 'mean',
            'cpm': 'mean',
            'cpc': 'mean'
        }).reset_index()
        
        daily['date'] = daily['date'].astype(str)
        
        # Weekend vs Weekday
        weekday_data = data.groupby('weekday_cat').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'ctr': 'mean',
            'media_cost_usd': 'sum'
        }).reset_index()
        
        return {
            'daily': daily.to_dict('records'),
            'weekday_performance': weekday_data.to_dict('records')
        }
    
    def _get_channel_analysis(self, data):
        """Get channel-level analysis"""
        channels = data.groupby('channel_name').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'media_cost_usd': 'sum',
            'ctr': 'mean',
            'cpm': 'mean',
            'cpc': 'mean'
        }).reset_index()
        
        channels = channels.sort_values('media_cost_usd', ascending=False)
        
        return {
            'by_channel': channels.to_dict('records'),
            'best_performing': channels.nlargest(1, 'ctr').to_dict('records')[0] if len(channels) > 0 else {},
            'most_expensive': channels.nlargest(1, 'media_cost_usd').to_dict('records')[0] if len(channels) > 0 else {}
        }
    
    def _get_creative_analysis(self, data):
        """Get creative performance analysis"""
        # Check if creative columns exist
        if 'creative_width' not in data.columns or 'creative_height' not in data.columns:
            return {
                'by_size': [],
                'best_performing_size': {},
                'templates': []
            }
        
        creatives = data.groupby(['creative_width', 'creative_height', 'aspect_ratio']).agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'ctr': 'mean',
            'media_cost_usd': 'sum'
        }).reset_index()
        
        creatives = creatives.sort_values('ctr', ascending=False)
        
        # Template analysis
        if 'template_id' in data.columns:
            templates = data.groupby('template_id').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'ctr': 'mean'
            }).reset_index()
            templates = templates.sort_values('ctr', ascending=False)
            template_data = templates.to_dict('records')
        else:
            template_data = []
        
        return {
            'by_size': creatives.to_dict('records'),
            'best_performing_size': creatives.nlargest(1, 'ctr').to_dict('records')[0] if len(creatives) > 0 else {},
            'templates': template_data
        }
    
    def _get_keyword_analysis(self, data):
        """Get keyword performance analysis"""
        if 'keywords' not in data.columns or data['keywords'].isna().all():
            return {'keywords': [], 'search_tags': []}
        
        # Keywords analysis
        keyword_data = data[data['keywords'].notna()].copy()
        if len(keyword_data) > 0:
            keywords = keyword_data.groupby('keywords').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'ctr': 'mean',
                'media_cost_usd': 'sum'
            }).reset_index()
            keywords = keywords.sort_values('ctr', ascending=False)
            keyword_list = keywords.head(10).to_dict('records')
        else:
            keyword_list = []
        
        # Search tags analysis
        if 'search_tags' in data.columns:
            tag_data = data[data['search_tags'].notna()].copy()
            if len(tag_data) > 0:
                tags = tag_data.groupby('search_tags').agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'ctr': 'mean'
                }).reset_index()
                tags = tags.sort_values('ctr', ascending=False)
                tag_list = tags.head(10).to_dict('records')
            else:
                tag_list = []
        else:
            tag_list = []
        
        return {
            'keywords': keyword_list,
            'search_tags': tag_list
        }
    
    def _get_landing_page_analysis(self, data):
        """Get landing page performance analysis"""
        if 'landing_page' not in data.columns or data['landing_page'].isna().all():
            return {'pages': []}
        
        pages = data[data['landing_page'].notna()].groupby('landing_page').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'ctr': 'mean',
            'media_cost_usd': 'sum'
        }).reset_index()
        
        pages = pages.sort_values('ctr', ascending=False)
        
        return {
            'pages': pages.to_dict('records'),
            'best_performing': pages.nlargest(1, 'ctr').to_dict('records')[0] if len(pages) > 0 else {}
        }
    
    def _get_platform_breakdown(self, data):
        """Get platform-wise breakdown for campaign"""
        platforms = data.groupby('ext_service_name').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'media_cost_usd': 'sum',
            'ctr': 'mean',
            'cpm': 'mean',
            'cpc': 'mean'
        }).reset_index()
        
        # Calculate percentage contribution
        total_spend = platforms['media_cost_usd'].sum()
        if total_spend > 0:
            platforms['spend_percentage'] = (platforms['media_cost_usd'] / total_spend * 100).round(2)
        else:
            platforms['spend_percentage'] = 0
        
        return platforms.to_dict('records')
    
    def get_platform_analysis(self):
        """Get platform-level analysis across all campaigns"""
        platforms = {}
        
        for platform in self.df['ext_service_name'].unique():
            platform_data = self.df[self.df['ext_service_name'] == platform]
            
            platforms[platform] = {
                'summary': {
                    'total_impressions': int(platform_data['impressions'].sum()),
                    'total_clicks': int(platform_data['clicks'].sum()),
                    'total_spend': float(platform_data['media_cost_usd'].sum()),
                    'total_reach': int(platform_data['total_reach'].sum()) if 'total_reach' in platform_data.columns else 0,
                    'avg_ctr': float(platform_data['ctr'].mean()),
                    'avg_cpm': float(platform_data['cpm'].mean()),
                    'avg_cpc': float(platform_data['cpc'].mean()),
                    'campaigns_count': int(platform_data['campaign_item_id'].nunique())
                },
                'trends': self._get_platform_trends(platform_data),
                'keywords': self._get_keyword_analysis(platform_data),
                'channels': self._get_channel_analysis(platform_data)
            }
        
        return platforms
    
    def _get_platform_trends(self, data):
        """Get platform trends over time"""
        if 'date' not in data.columns:
            return {}
        
        daily = data.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'media_cost_usd': 'sum',
            'ctr': 'mean',
            'cpm': 'mean',
            'cpc': 'mean'
        }).reset_index()
        
        daily['date'] = daily['date'].astype(str)
        
        return daily.to_dict('records')
    
    def get_cross_cutting_analysis(self):
        """Get cross-cutting insights across all data"""
        analysis = {
            'overall_metrics': {
                'total_campaigns': int(self.df['campaign_item_id'].nunique()),
                'total_spend': float(self.df['media_cost_usd'].sum()),
                'total_impressions': int(self.df['impressions'].sum()),
                'total_clicks': int(self.df['clicks'].sum()),
                'overall_ctr': float((self.df['clicks'].sum() / self.df['impressions'].sum() * 100) if self.df['impressions'].sum() > 0 else 0),
                'overall_cpm': float((self.df['media_cost_usd'].sum() / self.df['impressions'].sum() * 1000) if self.df['impressions'].sum() > 0 else 0),
                'overall_cpc': float(self.df['media_cost_usd'].sum() / self.df['clicks'].sum()) if self.df['clicks'].sum() > 0 else 0
            },
            'platform_comparison': self._get_platform_comparison(),
            'channel_comparison': self._get_channel_comparison(),
            'top_keywords': self._get_top_keywords_overall(),
            'date_range': {
                'start': str(self.df['time'].min()) if 'time' in self.df.columns else 'N/A',
                'end': str(self.df['time'].max()) if 'time' in self.df.columns else 'N/A',
                'total_days': int(self.df['date'].nunique()) if 'date' in self.df.columns else 0
            }
        }
        
        return analysis
    
    def _get_platform_comparison(self):
        """Compare platforms"""
        platforms = self.df.groupby('ext_service_name').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'media_cost_usd': 'sum',
            'ctr': 'mean',
            'cpm': 'mean',
            'cpc': 'mean',
            'campaign_item_id': 'nunique'
        }).reset_index()
        
        platforms.rename(columns={'campaign_item_id': 'campaigns_count'}, inplace=True)
        
        return platforms.to_dict('records')
    
    def _get_channel_comparison(self):
        """Compare channels across all data"""
        channels = self.df.groupby('channel_name').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'media_cost_usd': 'sum',
            'ctr': 'mean',
            'cpm': 'mean',
            'cpc': 'mean'
        }).reset_index()
        
        channels = channels.sort_values('media_cost_usd', ascending=False)
        
        return channels.to_dict('records')
    
    def _get_top_keywords_overall(self):
        """Get top performing keywords across all campaigns"""
        if 'keywords' not in self.df.columns or self.df['keywords'].isna().all():
            return []
        
        keyword_data = self.df[self.df['keywords'].notna()].copy()
        if len(keyword_data) == 0:
            return []
        
        keywords = keyword_data.groupby('keywords').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'ctr': 'mean',
            'media_cost_usd': 'sum'
        }).reset_index()
        
        keywords = keywords.sort_values('ctr', ascending=False)
        
        return keywords.head(10).to_dict('records')
    
    def get_full_analysis(self):
        """Get complete analysis of all data"""
        return {
            'summary': self.get_data_summary(),
            'cross_cutting': self.get_cross_cutting_analysis(),
            'platforms': self.get_platform_analysis()
        }