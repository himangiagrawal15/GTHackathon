"""
AI Insights Generator using Google Gemini API
"""

import google.generativeai as genai
from config import AI_CONFIG
import json

class AIInsightsGenerator:
    def __init__(self):
        self.enabled = AI_CONFIG.get('enabled', False)
        
        if self.enabled:
            api_key = AI_CONFIG.get('api_key')
            if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
                print("⚠️  Warning: Gemini API key not configured. Using fallback insights.")
                self.enabled = False
            else:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(AI_CONFIG.get('model', 'gemini-1.5-flash'))
                print("✅ Gemini AI enabled for insights generation")
    
    def generate_executive_summary(self, cross_analysis):
        """Generate executive summary from overall data"""
        if not self.enabled:
            return self._fallback_executive_summary(cross_analysis)
        
        try:
            metrics = cross_analysis['overall_metrics']
            platforms = cross_analysis['platform_comparison']
            
            prompt = f"""You are an expert AdTech analyst. Analyze this advertising campaign data and provide a concise executive summary.

DATA:
- Total Campaigns: {metrics['total_campaigns']}
- Total Spend: ${metrics['total_spend']:,.2f}
- Total Impressions: {metrics['total_impressions']:,}
- Total Clicks: {metrics['total_clicks']:,}
- Overall CTR: {metrics['overall_ctr']:.2f}%
- Overall CPM: ${metrics['overall_cpm']:.2f}
- Overall CPC: ${metrics['overall_cpc']:.2f}

PLATFORM PERFORMANCE:
{self._format_platforms(platforms)}

Provide a professional 3-4 sentence executive summary that:
1. Highlights overall performance
2. Identifies the best performing platform and why
3. Gives 1-2 key actionable recommendations

Keep it concise and business-focused."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating AI insight: {e}")
            return self._fallback_executive_summary(cross_analysis)
    
    def generate_platform_insight(self, platform_name, platform_data):
        """Generate insights for a specific platform"""
        if not self.enabled:
            return self._fallback_platform_insight(platform_name, platform_data)
        
        try:
            summary = platform_data['summary']
            
            prompt = f"""You are an AdTech analyst. Analyze this {platform_name} campaign performance.

PLATFORM: {platform_name}

METRICS:
- Campaigns: {summary['campaigns_count']}
- Total Spend: ${summary['total_spend']:,.2f}
- Impressions: {summary['total_impressions']:,}
- Clicks: {summary['total_clicks']:,}
- Average CTR: {summary['avg_ctr']:.2f}%
- Average CPM: ${summary['avg_cpm']:.2f}
- Average CPC: ${summary['avg_cpc']:.2f}

Provide a 2-3 sentence analysis that:
1. Evaluates the performance (good/needs improvement)
2. Compares key metrics to industry standards (typical CTR for this platform is 1.5-3%)
3. Suggests one specific optimization

Be professional and actionable."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating platform insight: {e}")
            return self._fallback_platform_insight(platform_name, platform_data)
    
    def generate_campaign_insight(self, campaign_id, analysis):
        """Generate insights for a specific campaign"""
        if not self.enabled:
            return self._fallback_campaign_insight(campaign_id, analysis)
        
        try:
            summary = analysis['summary']
            channels = analysis['channels']['by_channel']
            
            # Find best and worst channels
            best_channel = max(channels, key=lambda x: x['ctr']) if channels else None
            worst_channel = min(channels, key=lambda x: x['ctr']) if channels else None
            
            prompt = f"""Analyze this advertising campaign performance.

CAMPAIGN ID: {campaign_id}

OVERVIEW:
- Duration: {summary['days_running']} days
- Total Spend: ${summary['total_spend']:,.2f}
- Budget: ${summary['budget']:,.2f}
- Impressions: {summary['total_impressions']:,}
- Clicks: {summary['total_clicks']:,}
- CTR: {summary['avg_ctr']:.2f}%
- CPM: ${summary['avg_cpm']:.2f}
- CPC: ${summary['avg_cpc']:.2f}

CHANNELS:
- Best: {best_channel['channel_name'] if best_channel else 'N/A'} ({best_channel['ctr']:.2f}% CTR if best_channel else 'N/A')
- Worst: {worst_channel['channel_name'] if worst_channel else 'N/A'} ({worst_channel['ctr']:.2f}% CTR if worst_channel else 'N/A')

Provide 2-3 sentences that:
1. Assess overall campaign performance (budget utilization, efficiency)
2. Identify what's working well
3. Give ONE specific recommendation to improve results

Be direct and actionable."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating campaign insight: {e}")
            return self._fallback_campaign_insight(campaign_id, analysis)
    
    def generate_recommendations(self, cross_analysis):
        """Generate overall recommendations"""
        if not self.enabled:
            return self._fallback_recommendations(cross_analysis)
        
        try:
            metrics = cross_analysis['overall_metrics']
            channels = cross_analysis['channel_comparison']
            
            top_channel = max(channels, key=lambda x: x['ctr']) if channels else None
            
            prompt = f"""As an AdTech consultant, provide strategic recommendations based on this campaign data.

OVERALL PERFORMANCE:
- Total Campaigns: {metrics['total_campaigns']}
- Total Spend: ${metrics['total_spend']:,.2f}
- Overall CTR: {metrics['overall_ctr']:.2f}%
- Overall CPC: ${metrics['overall_cpc']:.2f}

TOP CHANNEL: {top_channel['channel_name'] if top_channel else 'N/A'} ({top_channel['ctr']:.2f}% CTR if top_channel else 'N/A')

Provide 3 specific, actionable recommendations to:
1. Improve overall campaign performance
2. Optimize budget allocation
3. Increase ROI

Number them 1-3 and keep each to 1 sentence. Be concrete and actionable."""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._fallback_recommendations(cross_analysis)
    
    # Fallback methods (used when AI is disabled or fails)
    
    def _format_platforms(self, platforms):
        """Format platform data for prompt"""
        result = []
        for p in platforms:
            result.append(f"- {p['ext_service_name']}: {p['ctr']:.2f}% CTR, ${p['media_cost_usd']:,.0f} spend")
        return "\n".join(result)
    
    def _fallback_executive_summary(self, cross_analysis):
        """Fallback summary when AI is not available"""
        metrics = cross_analysis['overall_metrics']
        platforms = cross_analysis['platform_comparison']
        
        best_platform = max(platforms, key=lambda x: x['ctr'])
        
        return f"""The advertising campaigns generated {metrics['total_impressions']:,} impressions and {metrics['total_clicks']:,} clicks across {metrics['total_campaigns']} campaigns, with a total spend of ${metrics['total_spend']:,.2f}. The overall CTR of {metrics['overall_ctr']:.2f}% indicates {'strong' if metrics['overall_ctr'] > 2 else 'moderate'} engagement. {best_platform['ext_service_name']} delivered the highest CTR at {best_platform['ctr']:.2f}%, demonstrating superior audience targeting and creative effectiveness. Consider reallocating budget towards high-performing platforms and optimizing underperforming campaigns through A/B testing and refined audience segmentation."""
    
    def _fallback_platform_insight(self, platform_name, platform_data):
        """Fallback platform insight"""
        summary = platform_data['summary']
        
        return f"""{platform_name} managed {summary['campaigns_count']} campaigns with {summary['total_impressions']:,} total impressions and an average CTR of {summary['avg_ctr']:.2f}%. The average CPC of ${summary['avg_cpc']:.2f} indicates {'efficient' if summary['avg_cpc'] < 2 else 'moderate'} cost per engagement. {'Strong performance suggests effective audience targeting. Continue current strategy while exploring expansion opportunities.' if summary['avg_ctr'] > 2 else 'Performance indicates room for improvement. Consider optimizing ad creatives, refining targeting parameters, and testing new audience segments.'}"""
    
    def _fallback_campaign_insight(self, campaign_id, analysis):
        """Fallback campaign insight"""
        summary = analysis['summary']
        channels = analysis['channels']['by_channel']
        
        best_channel = max(channels, key=lambda x: x['ctr']) if channels else None
        
        return f"""Campaign {campaign_id} ran for {summary['days_running']} days, generating {summary['total_clicks']:,} clicks from {summary['total_impressions']:,} impressions with a {summary['avg_ctr']:.2f}% CTR. Total spend of ${summary['total_spend']:,.2f} resulted in an average CPC of ${summary['avg_cpc']:.2f}. {f"{best_channel['channel_name']} delivered the highest CTR at {best_channel['ctr']:.2f}%, demonstrating strong channel-message fit. Consider increasing investment in this channel." if best_channel else ""} {'The campaign is performing well relative to budget. Focus on scaling successful elements.' if summary['total_spend'] < summary['budget'] * 0.8 else 'Campaign is approaching budget limits. Evaluate ROI and consider budget reallocation if underperforming.'}"""
    
    def _fallback_recommendations(self, cross_analysis):
        """Fallback recommendations"""
        metrics = cross_analysis['overall_metrics']
        channels = cross_analysis['channel_comparison']
        
        top_channel = max(channels, key=lambda x: x['ctr']) if channels else None
        
        return f"""1. Reallocate budget towards {top_channel['channel_name'] if top_channel else 'high-performing channels'} which shows superior engagement rates.
2. Implement A/B testing on underperforming campaigns to identify optimization opportunities in creative and targeting.
3. Consider pausing campaigns with CTR below 1.5% and reallocating budget to campaigns exceeding 3% CTR for improved overall ROI."""
