from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from data_processor import DataProcessor
from ai_insights import AIInsightsGenerator
import pandas as pd
import numpy as np

class ReportGenerator:
    def __init__(self, df, output_folder):
        self.df = df
        self.output_folder = output_folder
        self.processor = DataProcessor(df)
        self.ai_generator = AIInsightsGenerator()  # Initialize AI generator
        self.chart_folder = os.path.join(output_folder, 'charts')
        os.makedirs(self.chart_folder, exist_ok=True)
        
        # Set style
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def generate_comprehensive_report(self, report_type='comprehensive'):
        """Generate the main comprehensive PDF report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"AdTech_Report_{timestamp}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                               topMargin=0.5*inch, bottomMargin=0.5*inch,
                               leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        story = []
        styles = self._get_styles()
        
        # Cover Page
        story.extend(self._create_cover_page(styles))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(styles))
        story.append(PageBreak())
        
        # Platform-Level Analysis
        story.extend(self._create_platform_analysis(styles))
        story.append(PageBreak())
        
        # Campaign-Level Analysis
        campaigns = self.df['campaign_item_id'].unique()
        for i, campaign_id in enumerate(campaigns[:20]):  # Limit to 20 campaigns for demo
            story.extend(self._create_campaign_report(campaign_id, styles))
            if i < len(campaigns) - 1:
                story.append(PageBreak())
        
        # Cross-Cutting Insights
        story.extend(self._create_cross_cutting_analysis(styles))
        
        # Build PDF
        doc.build(story)
        
        # Clean up chart files
        self._cleanup_charts()
        
        return filepath
    
    def _get_styles(self):
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        # Body style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=12,
            leading=16
        ))
        
        # Insight box style
        styles.add(ParagraphStyle(
            name='InsightBox',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            backColor=colors.HexColor('#ecf0f1'),
            borderPadding=10,
            spaceAfter=12,
            leading=16
        ))
        
        return styles
    
    def _create_cover_page(self, styles):
        """Create cover page"""
        story = []
        
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("AdTech Performance Report", styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        summary = self.processor.get_data_summary()
        
        cover_data = [
            ['Total Campaigns', str(summary['campaigns']['total'])],
            ['Total Spend', f"${summary['total_spend']:,.2f}"],
            ['Total Impressions', f"{summary['total_impressions']:,}"],
            ['Total Clicks', f"{summary['total_clicks']:,}"],
            ['Overall CTR', f"{summary['overall_ctr']:.2f}%"],
            ['Date Range', f"{summary['date_range']['start']} to {summary['date_range']['end']}"],
            ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = Table(cover_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(table)
        
        return story
    
    def _create_executive_summary(self, styles):
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get cross-cutting analysis
        cross_analysis = self.processor.get_cross_cutting_analysis()
        
        # Generate LLM insight
        insight = self._generate_executive_insight(cross_analysis)
        story.append(Paragraph(insight, styles['InsightBox']))
        story.append(Spacer(1, 0.3*inch))
        
        # Overall metrics table
        metrics = cross_analysis['overall_metrics']
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Campaigns', str(metrics['total_campaigns'])],
            ['Total Spend', f"${metrics['total_spend']:,.2f}"],
            ['Total Impressions', f"{metrics['total_impressions']:,}"],
            ['Total Clicks', f"{metrics['total_clicks']:,}"],
            ['Overall CTR', f"{metrics['overall_ctr']:.2f}%"],
            ['Overall CPM', f"${metrics['overall_cpm']:.2f}"],
            ['Overall CPC', f"${metrics['overall_cpc']:.2f}"]
        ]
        
        table = Table(metrics_data, colWidths=[3*inch, 3*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        
        # Platform comparison chart
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Platform Performance Comparison", styles['CustomHeading2']))
        
        chart_path = self._create_platform_comparison_chart(cross_analysis['platform_comparison'])
        if chart_path:
            img = Image(chart_path, width=6*inch, height=3.5*inch)
            story.append(img)
        
        return story
    
    def _create_platform_analysis(self, styles):
        """Create platform-level analysis section"""
        story = []
        
        story.append(Paragraph("Platform-Level Analysis", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        platforms_analysis = self.processor.get_platform_analysis()
        
        for platform_name, platform_data in platforms_analysis.items():
            story.append(Paragraph(f"Platform: {platform_name}", styles['CustomHeading2']))
            
            # Platform summary
            summary = platform_data['summary']
            summary_data = [
                ['Metric', 'Value'],
                ['Total Impressions', f"{summary['total_impressions']:,}"],
                ['Total Clicks', f"{summary['total_clicks']:,}"],
                ['Total Spend', f"${summary['total_spend']:,.2f}"],
                ['Average CTR', f"{summary['avg_ctr']:.2f}%"],
                ['Average CPM', f"${summary['avg_cpm']:.2f}"],
                ['Average CPC', f"${summary['avg_cpc']:.2f}"],
                ['Campaigns Count', str(summary['campaigns_count'])]
            ]
            
            table = Table(summary_data, colWidths=[3*inch, 3*inch])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
            
            # Platform insight
            insight = self._generate_platform_insight(platform_name, platform_data)
            story.append(Paragraph(insight, styles['InsightBox']))
            story.append(Spacer(1, 0.2*inch))
            
            # Trends chart
            if platform_data['trends']:
                chart_path = self._create_platform_trends_chart(platform_name, platform_data['trends'])
                if chart_path:
                    img = Image(chart_path, width=6*inch, height=3*inch)
                    story.append(img)
            
            story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_campaign_report(self, campaign_id, styles):
        """Create detailed report for a single campaign"""
        story = []
        
        analysis = self.processor.get_campaign_analysis(campaign_id)
        if not analysis:
            return story
        
        story.append(Paragraph(f"Campaign Analysis: {campaign_id}", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Campaign Summary
        summary = analysis['summary']
        summary_data = [
            ['Metric', 'Value'],
            ['Total Impressions', f"{summary['total_impressions']:,}"],
            ['Total Clicks', f"{summary['total_clicks']:,}"],
            ['Total Spend', f"${summary['total_spend']:,.2f}"],
            ['Average CTR', f"{summary['avg_ctr']:.2f}%"],
            ['Average CPM', f"${summary['avg_cpm']:.2f}"],
            ['Average CPC', f"${summary['avg_cpc']:.2f}"],
            ['Days Running', str(summary['days_running'])],
            ['Budget', f"${summary['budget']:,.2f}"],
            ['Platforms', ', '.join(summary['platforms'])],
            ['Channels', ', '.join(summary['channels'])]
        ]
        
        table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(self._get_table_style())
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Campaign insight
        insight = self._generate_campaign_insight(campaign_id, analysis)
        story.append(Paragraph(insight, styles['InsightBox']))
        story.append(Spacer(1, 0.2*inch))
        
        # Trends
        if analysis['trends'] and analysis['trends'].get('daily'):
            story.append(Paragraph("Performance Trends", styles['CustomHeading2']))
            chart_path = self._create_campaign_trends_chart(campaign_id, analysis['trends'])
            if chart_path:
                img = Image(chart_path, width=6*inch, height=3*inch)
                story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        # Channel Analysis
        if analysis['channels']['by_channel']:
            story.append(Paragraph("Channel Performance", styles['CustomHeading2']))
            
            channel_data = [['Channel', 'Impressions', 'Clicks', 'CTR', 'Spend']]
            for channel in analysis['channels']['by_channel'][:5]:
                channel_data.append([
                    channel['channel_name'],
                    f"{int(channel['impressions']):,}",
                    f"{int(channel['clicks']):,}",
                    f"{channel['ctr']:.2f}%",
                    f"${channel['media_cost_usd']:,.2f}"
                ])
            
            table = Table(channel_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])
            table.setStyle(self._get_table_style())
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        # Platform breakdown chart
        if analysis['platforms']:
            chart_path = self._create_platform_breakdown_chart(campaign_id, analysis['platforms'])
            if chart_path:
                story.append(Paragraph("Platform Distribution", styles['CustomHeading2']))
                img = Image(chart_path, width=5*inch, height=3*inch)
                story.append(img)
        
        return story
    
    def _create_cross_cutting_analysis(self, styles):
        """Create cross-cutting insights section"""
        story = []
        
        story.append(Paragraph("Cross-Cutting Insights", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        cross_analysis = self.processor.get_cross_cutting_analysis()
        
        # Top performing channels
        story.append(Paragraph("Top Performing Channels", styles['CustomHeading2']))
        channels = cross_analysis['channel_comparison']
        if channels:
            channel_data = [['Channel', 'Impressions', 'Clicks', 'CTR', 'Spend']]
            for channel in channels[:5]:
                channel_data.append([
                    channel['channel_name'],
                    f"{int(channel['impressions']):,}",
                    f"{int(channel['clicks']):,}",
                    f"{channel['ctr']:.2f}%",
                    f"${channel['media_cost_usd']:,.2f}"
                ])
            
            table = Table(channel_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])
            table.setStyle(self._get_table_style())
            story.append(table)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Top keywords
        if cross_analysis['top_keywords']:
            story.append(Paragraph("Top Performing Keywords", styles['CustomHeading2']))
            
            keyword_data = [['Keyword', 'Impressions', 'Clicks', 'CTR']]
            for keyword in cross_analysis['top_keywords'][:10]:
                keyword_data.append([
                    str(keyword['keywords'])[:30],
                    f"{int(keyword['impressions']):,}",
                    f"{int(keyword['clicks']):,}",
                    f"{keyword['ctr']:.2f}%"
                ])
            
            table = Table(keyword_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            table.setStyle(self._get_table_style())
            story.append(table)
        
        return story
    
    def _create_platform_comparison_chart(self, platform_data):
        """Create platform comparison chart"""
        if not platform_data:
            return None
        
        df = pd.DataFrame(platform_data)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # CTR comparison
        axes[0].bar(df['ext_service_name'], df['ctr'], color=['#3498db', '#e74c3c', '#2ecc71'])
        axes[0].set_title('CTR by Platform')
        axes[0].set_ylabel('CTR (%)')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Spend comparison
        axes[1].bar(df['ext_service_name'], df['media_cost_usd'], color=['#3498db', '#e74c3c', '#2ecc71'])
        axes[1].set_title('Spend by Platform')
        axes[1].set_ylabel('Spend ($)')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        chart_path = os.path.join(self.chart_folder, f'platform_comparison_{datetime.now().timestamp()}.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_platform_trends_chart(self, platform_name, trends_data):
        """Create platform trends chart"""
        if not trends_data:
            return None
        
        df = pd.DataFrame(trends_data)
        if len(df) == 0:
            return None
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 6))
        
        # CTR trend
        axes[0].plot(df['date'], df['ctr'], marker='o', color='#3498db', linewidth=2)
        axes[0].set_title(f'{platform_name} - CTR Trend')
        axes[0].set_ylabel('CTR (%)')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)
        
        # Spend trend
        axes[1].plot(df['date'], df['media_cost_usd'], marker='o', color='#e74c3c', linewidth=2)
        axes[1].set_title(f'{platform_name} - Spend Trend')
        axes[1].set_ylabel('Spend ($)')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        chart_path = os.path.join(self.chart_folder, f'platform_trends_{platform_name}_{datetime.now().timestamp()}.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_campaign_trends_chart(self, campaign_id, trends):
        """Create campaign trends chart"""
        if not trends.get('daily'):
            return None
        
        df = pd.DataFrame(trends['daily'])
        if len(df) == 0:
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # CTR trend
        axes[0, 0].plot(df['date'], df['ctr'], marker='o', color='#3498db', linewidth=2)
        axes[0, 0].set_title('Daily CTR')
        axes[0, 0].set_ylabel('CTR (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Spend trend
        axes[0, 1].plot(df['date'], df['media_cost_usd'], marker='o', color='#e74c3c', linewidth=2)
        axes[0, 1].set_title('Daily Spend')
        axes[0, 1].set_ylabel('Spend ($)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Impressions trend
        axes[1, 0].plot(df['date'], df['impressions'], marker='o', color='#2ecc71', linewidth=2)
        axes[1, 0].set_title('Daily Impressions')
        axes[1, 0].set_ylabel('Impressions')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Clicks trend
        axes[1, 1].plot(df['date'], df['clicks'], marker='o', color='#f39c12', linewidth=2)
        axes[1, 1].set_title('Daily Clicks')
        axes[1, 1].set_ylabel('Clicks')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        chart_path = os.path.join(self.chart_folder, f'campaign_trends_{campaign_id}_{datetime.now().timestamp()}.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_platform_breakdown_chart(self, campaign_id, platforms):
        """Create platform breakdown pie chart"""
        if not platforms:
            return None
        
        df = pd.DataFrame(platforms)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        colors_list = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        ax.pie(df['spend_percentage'], labels=df['ext_service_name'], autopct='%1.1f%%',
               colors=colors_list[:len(df)], startangle=90)
        ax.set_title('Spend Distribution by Platform')
        
        chart_path = os.path.join(self.chart_folder, f'platform_breakdown_{campaign_id}_{datetime.now().timestamp()}.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _get_table_style(self):
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ])
    
    def _generate_executive_insight(self, cross_analysis):
        """Generate executive-level insight using AI"""
        insight = self.ai_generator.generate_executive_summary(cross_analysis)
        return insight
    
    def _generate_platform_insight(self, platform_name, platform_data):
        """Generate platform-specific insight using AI"""
        insight = self.ai_generator.generate_platform_insight(platform_name, platform_data)
        return insight
    
    def _generate_campaign_insight(self, campaign_id, analysis):
        """Generate campaign-specific insight using AI"""
        insight = self.ai_generator.generate_campaign_insight(campaign_id, analysis)
        return insight
    
    def _cleanup_charts(self):
        """Clean up generated chart files"""
        for file in os.listdir(self.chart_folder):
            file_path = os.path.join(self.chart_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")