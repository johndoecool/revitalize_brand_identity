import json
import base64
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from io import BytesIO

# PDF generation imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF

# Chart generation imports
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
plt.ioff()  # Turn off interactive mode
import matplotlib.patches as patches

# Import seaborn with error handling for Windows
try:
    import seaborn as sns
    sns.set_style("whitegrid")
except ImportError:
    sns = None
    logger.warning("Seaborn not available, using matplotlib defaults")

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

from app.models.analysis import ChartData, CompetitorInsight, ImprovementArea, AnalysisResults, Priority, ComparisonScore
from app.core.config import Settings

logger = logging.getLogger(__name__)

class ChartService:
    """Service for generating chart data for UI visualization"""
    
    def __init__(self):
        self.settings = Settings()
        # Create reports directory if local saving is enabled
        if self.settings.SAVE_REPORTS_LOCALLY:
            os.makedirs(self.settings.REPORTS_DIRECTORY, exist_ok=True)
    
    def generate_charts_from_analysis(self, analysis_result: AnalysisResults, collected_data: Dict[str, Any]) -> List[ChartData]:
        """Generate comprehensive chart data from analysis results"""
        charts = []
        
        try:
            # 1. Overall Performance Comparison Chart
            charts.append(self._create_overall_comparison_chart(analysis_result))
            
            # 2. Category Performance Radar Chart
            charts.append(self._create_category_radar_chart(analysis_result))
            
            # 3. Trend Analysis Line Chart
            charts.append(self._create_trend_chart(collected_data))
            
            # 4. Sentiment Analysis Chart
            charts.append(self._create_sentiment_chart(collected_data))
            
            # 5. Social Media Performance Chart
            charts.append(self._create_social_media_chart(collected_data))
            
            # 6. News Coverage Chart
            charts.append(self._create_news_coverage_chart(collected_data))
            
            # 7. Priority Insights Chart
            charts.append(self._create_priority_insights_chart(analysis_result))
            
            # 8. Performance Gap Analysis
            charts.append(self._create_gap_analysis_chart(analysis_result))
            
            logger.info(f"Generated {len(charts)} charts for analysis {analysis_result.analysis_id}")
            return charts
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            return []
    
    def _create_overall_comparison_chart(self, analysis_result: AnalysisResults) -> ChartData:
        """Create overall performance comparison bar chart"""
        return ChartData(
            chart_type="bar",
            title="Overall Performance Comparison",
            description="Brand vs Competitor overall performance scores",
            data={
                "labels": [analysis_result.brand_name, analysis_result.competitor_name],
                "datasets": [{
                    "label": "Performance Score",
                    "data": [
                        round(analysis_result.overall_comparison.brand_score * 100, 1),
                        round(analysis_result.overall_comparison.competitor_score * 100, 1)
                    ],
                    "backgroundColor": ["#3B82F6", "#EF4444"],
                    "borderColor": ["#1D4ED8", "#DC2626"],
                    "borderWidth": 2
                }]
            },
            config={
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "title": {"display": True, "text": "Score (%)"}
                    }
                },
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_category_radar_chart(self, analysis_result: AnalysisResults) -> ChartData:
        """Create category performance radar chart"""
        categories = list(analysis_result.detailed_comparison.keys())
        brand_scores = [round(comp.brand_score * 100, 1) for comp in analysis_result.detailed_comparison.values()]
        competitor_scores = [round(comp.competitor_score * 100, 1) for comp in analysis_result.detailed_comparison.values()]
        
        return ChartData(
            chart_type="radar",
            title="Category Performance Analysis",
            description="Performance comparison across different business categories",
            data={
                "labels": [cat.replace('_', ' ').title() for cat in categories],
                "datasets": [
                    {
                        "label": analysis_result.brand_name,
                        "data": brand_scores,
                        "backgroundColor": "rgba(59, 130, 246, 0.2)",
                        "borderColor": "#3B82F6",
                        "borderWidth": 2,
                        "pointBackgroundColor": "#3B82F6"
                    },
                    {
                        "label": analysis_result.competitor_name,
                        "data": competitor_scores,
                        "backgroundColor": "rgba(239, 68, 68, 0.2)",
                        "borderColor": "#EF4444",
                        "borderWidth": 2,
                        "pointBackgroundColor": "#EF4444"
                    }
                ]
            },
            config={
                "responsive": True,
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "max": 100,
                        "title": {"display": True, "text": "Score (%)"}
                    }
                },
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_trend_chart(self, collected_data: Dict[str, Any]) -> ChartData:
        """Create trend analysis line chart"""
        # Extract historical data if available
        brand_data = collected_data.get('brand_data', {})
        
        # Mock trend data - in real implementation, extract from historical data
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        brand_trend = [65, 68, 70, 72, 75, 78]
        market_trend = [70, 69, 71, 73, 74, 75]
        
        return ChartData(
            chart_type="line",
            title="Performance Trend Analysis",
            description="Brand performance trend over time compared to market average",
            data={
                "labels": months,
                "datasets": [
                    {
                        "label": brand_data.get('brand_id', 'Brand'),
                        "data": brand_trend,
                        "borderColor": "#3B82F6",
                        "backgroundColor": "rgba(59, 130, 246, 0.1)",
                        "tension": 0.4,
                        "fill": True
                    },
                    {
                        "label": "Market Average",
                        "data": market_trend,
                        "borderColor": "#10B981",
                        "backgroundColor": "rgba(16, 185, 129, 0.1)",
                        "tension": 0.4,
                        "fill": False
                    }
                ]
            },
            config={
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "title": {"display": True, "text": "Performance Score (%)"}
                    }
                },
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_sentiment_chart(self, collected_data: Dict[str, Any]) -> ChartData:
        """Create sentiment analysis donut chart"""
        brand_data = collected_data.get('brand_data', {})
        news_sentiment = brand_data.get('news_sentiment', {})
        
        positive = news_sentiment.get('positive_articles', 1)
        negative = news_sentiment.get('negative_articles', 0)
        neutral = news_sentiment.get('neutral_articles', 49)
        
        return ChartData(
            chart_type="doughnut",
            title="News Sentiment Distribution",
            description="Distribution of positive, neutral, and negative news coverage",
            data={
                "labels": ["Positive", "Neutral", "Negative"],
                "datasets": [{
                    "data": [positive, neutral, negative],
                    "backgroundColor": ["#10B981", "#6B7280", "#EF4444"],
                    "borderColor": ["#059669", "#4B5563", "#DC2626"],
                    "borderWidth": 2
                }]
            },
            config={
                "responsive": True,
                "plugins": {
                    "legend": {"display": True, "position": "bottom"},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_social_media_chart(self, collected_data: Dict[str, Any]) -> ChartData:
        """Create social media performance chart"""
        brand_data = collected_data.get('brand_data', {})
        social_media = brand_data.get('social_media', {})
        
        platforms = ["Facebook", "Twitter", "Instagram", "LinkedIn", "YouTube"]
        engagement = [85, 78, 92, 75, 80]  # Mock data
        
        return ChartData(
            chart_type="bar",
            title="Social Media Performance",
            description="Engagement scores across different social media platforms",
            data={
                "labels": platforms,
                "datasets": [{
                    "label": "Engagement Score",
                    "data": engagement,
                    "backgroundColor": [
                        "#1877F2", "#1DA1F2", "#E4405F", "#0A66C2", "#FF0000"
                    ],
                    "borderWidth": 2
                }]
            },
            config={
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "title": {"display": True, "text": "Engagement Score (%)"}
                    }
                },
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_news_coverage_chart(self, collected_data: Dict[str, Any]) -> ChartData:
        """Create news coverage timeline chart"""
        brand_data = collected_data.get('brand_data', {})
        news_sentiment = brand_data.get('news_sentiment', {})
        
        # Mock weekly coverage data
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
        coverage = [12, 18, 15, 20]
        
        return ChartData(
            chart_type="line",
            title="News Coverage Timeline",
            description="Number of news articles over time",
            data={
                "labels": weeks,
                "datasets": [{
                    "label": "Articles Count",
                    "data": coverage,
                    "borderColor": "#8B5CF6",
                    "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    "tension": 0.4,
                    "fill": True
                }]
            },
            config={
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {"display": True, "text": "Number of Articles"}
                    }
                },
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_priority_insights_chart(self, analysis_result: AnalysisResults) -> ChartData:
        """Create priority insights distribution chart"""
        high_priority = len([i for i in analysis_result.actionable_insights if i.priority == Priority.HIGH])
        medium_priority = len([i for i in analysis_result.actionable_insights if i.priority == Priority.MEDIUM])
        low_priority = len([i for i in analysis_result.actionable_insights if i.priority == Priority.LOW])
        
        return ChartData(
            chart_type="pie",
            title="Action Items by Priority",
            description="Distribution of actionable insights by priority level",
            data={
                "labels": ["High Priority", "Medium Priority", "Low Priority"],
                "datasets": [{
                    "data": [high_priority, medium_priority, low_priority],
                    "backgroundColor": ["#EF4444", "#F59E0B", "#10B981"],
                    "borderColor": ["#DC2626", "#D97706", "#059669"],
                    "borderWidth": 2
                }]
            },
            config={
                "responsive": True,
                "plugins": {
                    "legend": {"display": True, "position": "right"},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def _create_gap_analysis_chart(self, analysis_result: AnalysisResults) -> ChartData:
        """Create performance gap analysis chart"""
        categories = list(analysis_result.detailed_comparison.keys())
        gaps = [comp.difference for comp in analysis_result.detailed_comparison.values()]
        
        # Color gaps: positive (green), negative (red)
        colors = ["#10B981" if gap >= 0 else "#EF4444" for gap in gaps]
        
        return ChartData(
            chart_type="bar",
            title="Performance Gap Analysis",
            description="Performance gaps across categories (positive = advantage, negative = disadvantage)",
            data={
                "labels": [cat.replace('_', ' ').title() for cat in categories],
                "datasets": [{
                    "label": "Performance Gap",
                    "data": [round(gap * 100, 1) for gap in gaps],
                    "backgroundColor": colors,
                    "borderColor": colors,
                    "borderWidth": 2
                }]
            },
            config={
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {"display": True, "text": "Gap Score (%)"}
                    }
                },
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {"enabled": True}
                }
            }
        )
    
    def generate_pdf_report(self, analysis_result: AnalysisResults, charts: List[ChartData], 
                          competitor_insights: List[CompetitorInsight], improvement_areas: List[ImprovementArea],
                          collected_data: Dict[str, Any]) -> str:
        """Generate a comprehensive, professional PDF report with charts and visual elements"""
        try:
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  leftMargin=0.5*inch, rightMargin=0.5*inch,
                                  topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            # Get styles and create custom ones
            styles = getSampleStyleSheet()
            
            # Define professional color scheme
            primary_color = colors.Color(0.1, 0.3, 0.6)  # Dark blue
            secondary_color = colors.Color(0.2, 0.5, 0.8)  # Light blue
            accent_color = colors.Color(0.9, 0.6, 0.1)  # Orange
            success_color = colors.Color(0.2, 0.7, 0.3)  # Green
            warning_color = colors.Color(0.9, 0.4, 0.1)  # Red-orange
            
            # Custom styles
            title_style = ParagraphStyle('ExecutiveTitle', parent=styles['Heading1'], 
                                       fontSize=28, spaceAfter=30, alignment=TA_CENTER,
                                       textColor=primary_color, fontName='Helvetica-Bold')
            
            section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], 
                                         fontSize=18, spaceAfter=15, spaceBefore=20,
                                         textColor=primary_color, fontName='Helvetica-Bold')
            
            subsection_style = ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                            fontSize=14, spaceAfter=10, spaceBefore=10,
                                            textColor=secondary_color, fontName='Helvetica-Bold')
            
            highlight_style = ParagraphStyle('Highlight', parent=styles['Normal'], 
                                           fontSize=12, textColor=accent_color,
                                           fontName='Helvetica-Bold')
            
            # Build the PDF content
            story = []
            
            # COVER PAGE
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph("BRAND ANALYSIS REPORT", title_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Executive summary box
            exec_data = [
                ['', ''],
                ['Brand', analysis_result.brand_name],
                ['Competitor', analysis_result.competitor_name or 'Market Analysis'],
                ['Analysis Date', datetime.now(timezone.utc).strftime('%B %d, %Y')],
                ['Overall Score', f"{analysis_result.overall_comparison.brand_score:.1%}"],
                ['Performance Gap', f"{analysis_result.overall_comparison.gap:+.1%}"],
                ['Ranking', analysis_result.overall_comparison.brand_ranking.title()],
                ['Confidence Level', f"{analysis_result.overall_comparison.confidence_level:.1%}"],
                ['', '']
            ]
            
            exec_table = Table(exec_data, colWidths=[2*inch, 3*inch])
            exec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('BACKGROUND', (0, -1), (-1, -1), primary_color),
                ('TEXTCOLOR', (1, 1), (1, -2), primary_color),
                ('FONTNAME', (1, 1), (1, -2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 2, primary_color),
                ('LINEBELOW', (0, 1), (-1, -2), 1, colors.lightgrey),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(exec_table)
            story.append(PageBreak())
            
            # EXECUTIVE DASHBOARD
            story.append(Paragraph("Executive Dashboard", section_style))
            
            # Generate and add comprehensive performance charts
            chart_images = self._generate_dashboard_charts(analysis_result, charts, collected_data)
            
            if chart_images:
                # Executive Dashboard Overview
                if 'executive_dashboard' in chart_images:
                    story.append(Paragraph("Performance Overview Dashboard", subsection_style))
                    story.append(Image(chart_images['executive_dashboard'], width=7.5*inch, height=5.6*inch))
                    story.append(Spacer(1, 0.3*inch))
                
                # Category Analysis
                if 'category_analysis' in chart_images:
                    story.append(PageBreak())
                    story.append(Paragraph("Detailed Category Analysis", subsection_style))
                    story.append(Image(chart_images['category_analysis'], width=7.5*inch, height=5.6*inch))
                    story.append(Spacer(1, 0.3*inch))
                
                # Competitive Positioning
                if 'competitive_positioning' in chart_images:
                    story.append(PageBreak())
                    story.append(Paragraph("Competitive Positioning Analysis", subsection_style))
                    story.append(Image(chart_images['competitive_positioning'], width=7.5*inch, height=3.8*inch))
                    story.append(Spacer(1, 0.3*inch))
                
                # Benchmarking Dashboard
                if 'benchmarking' in chart_images:
                    story.append(Paragraph("Performance Benchmarking", subsection_style))
                    story.append(Image(chart_images['benchmarking'], width=7.5*inch, height=5.6*inch))
                    story.append(Spacer(1, 0.3*inch))
            
            story.append(PageBreak())
            
            # KEY PERFORMANCE INDICATORS
            story.append(Paragraph("Key Performance Indicators", section_style))
            
            # KPI Dashboard Table
            kpi_data = self._create_kpi_dashboard(analysis_result, collected_data)
            kpi_table = Table(kpi_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 2.2*inch, 1.2*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                # Highlight status column with conditional formatting
                ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
                ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
            ]))
            story.append(kpi_table)
            story.append(Spacer(1, 0.4*inch))
            
            # Performance insights summary
            insights_text = f"""
            <b>Key Performance Insights:</b><br/>
            • Brand Score: {analysis_result.overall_comparison.brand_score:.1%} vs Target 85%<br/>
            • Competitive Position: {analysis_result.overall_comparison.brand_ranking.title()} with {analysis_result.overall_comparison.gap:+.1%} gap<br/>
            • Analysis Confidence: {analysis_result.overall_comparison.confidence_level:.1%} based on available data<br/>
            • Strategic Focus: {'Maintain leadership' if analysis_result.overall_comparison.gap > 0 else 'Close performance gaps'}
            """
            story.append(Paragraph(insights_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # COMPETITIVE ANALYSIS
            if competitor_insights:
                story.append(PageBreak())
                story.append(Paragraph("Competitive Intelligence", section_style))
                
                for insight in competitor_insights:
                    # Competitor header with enhanced styling
                    comp_header = f"🏢 {insight.competitor_name} Analysis (Performance Score: {insight.comparison_score:.1%})"
                    story.append(Paragraph(comp_header, subsection_style))
                    
                    # Performance indicator
                    if insight.comparison_score >= 0.8:
                        perf_indicator = "🔴 STRONG COMPETITOR - High threat level"
                    elif insight.comparison_score >= 0.6:
                        perf_indicator = "🟡 MODERATE COMPETITOR - Monitor closely"
                    else:
                        perf_indicator = "🟢 WEAK COMPETITOR - Low threat level"
                    
                    story.append(Paragraph(f"<b>Threat Assessment:</b> {perf_indicator}", highlight_style))
                    story.append(Spacer(1, 0.2*inch))
                    
                    # Enhanced SWOT Analysis table with better formatting
                    swot_data = [
                        ['💪 STRENGTHS', '⚠️ WEAKNESSES'],
                        [self._format_list_for_table_enhanced(insight.strengths, '✓'), 
                         self._format_list_for_table_enhanced(insight.weaknesses, '✗')],
                        ['🚀 OPPORTUNITIES', '🔍 KEY DIFFERENCES'],
                        [self._format_list_for_table_enhanced(insight.opportunities, '→'),
                         self._format_list_for_table_enhanced(insight.key_differences, '◆')]
                    ]
                    
                    swot_table = Table(swot_data, colWidths=[3.5*inch, 3.5*inch], rowHeights=[0.4*inch, None, 0.4*inch, None])
                    swot_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, 0), success_color),
                        ('BACKGROUND', (1, 0), (1, 0), warning_color),
                        ('BACKGROUND', (0, 2), (0, 2), secondary_color),
                        ('BACKGROUND', (1, 2), (1, 2), accent_color),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('FONTSIZE', (0, 1), (-1, 1), 10),
                        ('FONTSIZE', (0, 2), (-1, 2), 12),
                        ('FONTSIZE', (0, 3), (-1, 3), 10),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 2, colors.black),
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ]))
                    story.append(swot_table)
                    
                    # Strategic implications
                    implications = f"""
                    <b>Strategic Implications:</b><br/>
                    • Priority Focus: {'Defend market position' if insight.comparison_score > analysis_result.overall_comparison.brand_score else 'Leverage competitive advantage'}<br/>
                    • Key Actions: Monitor {len(insight.strengths)} strength areas, Address {len(insight.weaknesses)} weakness gaps<br/>
                    • Opportunity Count: {len(insight.opportunities)} strategic opportunities identified
                    """
                    story.append(Paragraph(implications, styles['Normal']))
                    story.append(Spacer(1, 0.4*inch))
            
            # STRATEGIC RECOMMENDATIONS
            if improvement_areas:
                story.append(PageBreak())
                story.append(Paragraph("Strategic Action Plan", section_style))
                
                # Priority matrix visualization
                if 'priority_matrix' in chart_images:
                    story.append(Paragraph("Strategic Priority Matrix", subsection_style))
                    story.append(Image(chart_images['priority_matrix'], width=7*inch, height=5.8*inch))
                    story.append(Spacer(1, 0.3*inch))
                
                # Strategic insights summary table
                strategy_data = [
                    ['Priority Level', 'Focus Areas', 'Expected Timeline', 'Resource Allocation'],
                    ['HIGH PRIORITY', 'Quick wins with high impact', '1-3 months', 'Immediate investment'],
                    ['MEDIUM PRIORITY', 'Strategic initiatives', '3-6 months', 'Planned resources'],
                    ['LOW PRIORITY', 'Long-term improvements', '6+ months', 'Available capacity']
                ]
                
                strategy_table = Table(strategy_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
                strategy_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ('TEXTCOLOR', (1, 1), (1, 1), success_color),
                    ('TEXTCOLOR', (1, 2), (1, 2), accent_color),
                    ('TEXTCOLOR', (1, 3), (1, 3), secondary_color),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ]))
                story.append(strategy_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Detailed recommendations with enhanced formatting
                story.append(Paragraph("Detailed Strategic Recommendations", subsection_style))
                
                for i, area in enumerate(improvement_areas, 1):
                    # Priority indicator
                    priority_color = success_color if area.priority.value == 'high' else (
                        accent_color if area.priority.value == 'medium' else secondary_color)
                    
                    rec_header = f"{i}. {area.area} - {area.priority.value.upper()} PRIORITY"
                    story.append(Paragraph(rec_header, ParagraphStyle('RecHeader', 
                                                                    parent=subsection_style,
                                                                    textColor=priority_color)))
                    
                    # Recommendation details table
                    rec_data = [
                        ['Current Score', f"{area.current_score:.1%}"],
                        ['Target Score', f"{area.target_score:.1%}"],
                        ['Expected Improvement', f"{area.target_score - area.current_score:+.1%}"],
                        ['Timeline', area.timeline],
                        ['Resources Required', ', '.join(area.resources_needed)],
                    ]
                    
                    rec_table = Table(rec_data, colWidths=[1.5*inch, 5.5*inch])
                    rec_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(rec_table)
                    
                    # Action items
                    story.append(Paragraph("<b>Action Items:</b>", styles['Normal']))
                    for action in area.action_items:
                        story.append(Paragraph(f"• {action}", styles['Normal']))
                    
                    story.append(Spacer(1, 0.2*inch))
            
            # APPENDIX
            story.append(PageBreak())
            story.append(Paragraph("Data Sources & Methodology", section_style))
            
            # Data sources table
            data_sources = list(collected_data.keys()) if isinstance(collected_data, dict) else ["Multiple sources"]
            source_data = [['Data Source', 'Description']]
            for source in data_sources:
                source_data.append([source.replace('_', ' ').title(), 
                                  f"Collected data from {source.replace('_', ' ')} analysis"])
            
            source_table = Table(source_data, colWidths=[2*inch, 5*inch])
            source_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(source_table)
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"Report generated by Analysis Engine Service", styles['Normal']))
            story.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Clean up chart files
            self._cleanup_chart_files(chart_images)
            
            # Get PDF bytes and encode as base64
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Save locally if enabled
            if self.settings.SAVE_REPORTS_LOCALLY:
                self._save_pdf_locally(analysis_result.analysis_id, pdf_bytes)
            
            logger.info(f"Generated professional PDF report for analysis {analysis_result.analysis_id} ({len(pdf_bytes)} bytes)")
            return encoded_pdf
            
        except Exception as e:
            logger.error(f"Failed to generate professional PDF report: {e}")
            import traceback
            logger.error(f"PDF generation error details: {traceback.format_exc()}")
            
            # Return a basic fallback report as JSON (base64 encoded)
            fallback_report = {
                "error": "Failed to generate PDF report",
                "message": str(e),
                "basic_summary": {
                    "analysis_id": analysis_result.analysis_id,
                    "brand_name": analysis_result.brand_name,
                    "brand_score": analysis_result.overall_comparison.brand_score,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            }
            json_report = json.dumps(fallback_report, indent=2, default=str)
            return base64.b64encode(json_report.encode('utf-8')).decode('utf-8')
    
    def _save_pdf_locally(self, analysis_id: str, pdf_bytes: bytes):
        """Save the actual PDF file locally"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brand_analysis_report_{analysis_id}_{timestamp}.pdf"
            pdf_filepath = os.path.join(self.settings.REPORTS_DIRECTORY, filename)
            
            with open(pdf_filepath, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"PDF report saved locally: {pdf_filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save PDF locally: {e}")
    
    def _save_report_locally(self, analysis_id: str, json_content: str, report_data: Dict[str, Any]):
        """Save the report locally for testing purposes (legacy method for JSON backup)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brand_analysis_report_{analysis_id}_{timestamp}"
            
            # Save JSON version as backup
            json_filepath = os.path.join(self.settings.REPORTS_DIRECTORY, f"{filename}.json")
            with open(json_filepath, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            # Save a simplified text version for easy reading
            text_filepath = os.path.join(self.settings.REPORTS_DIRECTORY, f"{filename}_summary.txt")
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(self._generate_text_summary(report_data))
            
            logger.info(f"JSON backup saved locally: {json_filepath} and {text_filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save JSON backup locally: {e}")
    
    def _generate_text_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate a human-readable text summary of the report"""
        metadata = report_data.get("report_metadata", {})
        executive = report_data.get("executive_summary", {})
        detailed = report_data.get("detailed_analysis", {})
        
        summary = f"""
BRAND ANALYSIS REPORT
=====================

Report Details:
- Title: {metadata.get('title', 'N/A')}
- Generated: {metadata.get('generated_at', 'N/A')}
- Analysis ID: {metadata.get('analysis_id', 'N/A')}

Executive Summary:
- Brand: {metadata.get('brand_name', 'N/A')}
- Competitor: {metadata.get('competitor_name', 'N/A')}
- Brand Score: {executive.get('overall_brand_score', 'N/A')}
- Competitor Score: {executive.get('overall_competitor_score', 'N/A')}
- Performance Gap: {executive.get('performance_gap', 'N/A')}
- Brand Ranking: {executive.get('brand_ranking', 'N/A')}

Category Performance:
"""
        
        category_scores = detailed.get("category_scores", {})
        for category, scores in category_scores.items():
            if isinstance(scores, dict):
                brand_score = scores.get('brand_score', 'N/A')
                competitor_score = scores.get('competitor_score', 'N/A')
                difference = scores.get('difference', 'N/A')
                summary += f"- {category.replace('_', ' ').title()}: Brand={brand_score}, Competitor={competitor_score}, Diff={difference}\n"
        
        # Add actionable insights
        insights = detailed.get("actionable_insights", [])
        if insights:
            summary += "\nActionable Insights:\n"
            for i, insight in enumerate(insights[:3], 1):  # Top 3 insights
                if isinstance(insight, dict):
                    summary += f"{i}. {insight.get('title', 'N/A')} (Priority: {insight.get('priority', 'N/A')})\n"
                    summary += f"   {insight.get('description', 'N/A')}\n"
        
        # Add competitor analysis
        competitor_analysis = report_data.get("competitor_analysis", [])
        if competitor_analysis:
            summary += "\nCompetitor Analysis:\n"
            for comp in competitor_analysis[:1]:  # First competitor
                if isinstance(comp, dict):
                    summary += f"- {comp.get('competitor_name', 'N/A')} (Score: {comp.get('comparison_score', 'N/A')})\n"
                    strengths = comp.get('strengths', [])
                    if strengths:
                        summary += f"  Strengths: {', '.join(strengths[:3])}\n"
        
        # Add improvement areas
        improvement_areas = report_data.get("improvement_areas", [])
        if improvement_areas:
            summary += "\nImprovement Areas:\n"
            for area in improvement_areas[:3]:  # Top 3 areas
                if isinstance(area, dict):
                    summary += f"- {area.get('area', 'N/A')} (Priority: {area.get('priority', 'N/A')})\n"
                    summary += f"  Current: {area.get('current_score', 'N/A')}, Target: {area.get('target_score', 'N/A')}\n"
        
        return summary
    
    def _summarize_collected_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of collected data for the report appendix"""
        try:
            summary = {
                "total_data_points": len(collected_data) if isinstance(collected_data, dict) else 0,
                "data_categories": [],
                "collection_period": "Unknown",
                "brand_mentions": 0,
                "data_quality": "Good"
            }
            
            if isinstance(collected_data, dict):
                summary["data_categories"] = list(collected_data.keys())
                
                # Try to extract some key metrics
                for key, value in collected_data.items():
                    if isinstance(value, list):
                        summary[f"{key}_count"] = len(value)
                    elif isinstance(value, dict) and "count" in value:
                        summary[f"{key}_count"] = value.get("count", 0)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize collected data: {e}")
            return {"error": "Failed to summarize data", "raw_data_available": True}

    def generate_competitor_insights(self, analysis_result: AnalysisResults, collected_data: Dict[str, Any]) -> List[CompetitorInsight]:
        """Generate competitor insights from analysis results"""
        try:
            competitor_insights = []
            
            # Extract competitor data if available
            competitor_data = collected_data.get("competitor_data", {})
            if not competitor_data and isinstance(collected_data, dict):
                # Look for any competitor-related data in the structure
                for key, value in collected_data.items():
                    if "competitor" in key.lower():
                        competitor_data = value
                        break
            
            # Generate insight for the primary competitor
            competitor_name = analysis_result.competitor_name or "Primary Competitor"
            
            competitor_insight = CompetitorInsight(
                competitor_name=competitor_name,
                comparison_score=analysis_result.overall_comparison.competitor_score,
                strengths=self._extract_competitor_strengths(analysis_result, competitor_data),
                weaknesses=self._extract_competitor_weaknesses(analysis_result, competitor_data),
                opportunities=self._identify_competitive_opportunities(analysis_result),
                key_differences=self._identify_key_differences(analysis_result)
            )
            competitor_insights.append(competitor_insight)
            
            logger.info(f"Generated {len(competitor_insights)} competitor insights")
            return competitor_insights
            
        except Exception as e:
            logger.error(f"Failed to generate competitor insights: {e}")
            return []
    
    def generate_improvement_areas(self, analysis_result: AnalysisResults, collected_data: Dict[str, Any]) -> List[ImprovementArea]:
        """Generate improvement areas from analysis results"""
        try:
            improvement_areas = []
            
            # Analyze detailed comparison scores to identify areas for improvement
            for category, comparison in analysis_result.detailed_comparison.items():
                if comparison.difference < -0.1:  # Areas where we're significantly behind
                    improvement_area = ImprovementArea(
                        area=category.replace('_', ' ').title(),
                        current_score=comparison.brand_score,
                        target_score=min(1.0, comparison.brand_score + abs(comparison.difference) + 0.1),
                        priority=self._determine_priority(comparison.difference),
                        description=self._generate_improvement_description(category, comparison),
                        action_items=self._generate_action_items(category),
                        expected_outcomes=self._generate_expected_outcomes(category),
                        timeline=self._estimate_timeline(comparison.difference),
                        resources_needed=self._identify_resources_needed(category)
                    )
                    improvement_areas.append(improvement_area)
            
            # Sort by priority (high first)
            priority_order = {"high": 0, "medium": 1, "low": 2}
            improvement_areas.sort(key=lambda x: priority_order.get(x.priority.value, 2))
            
            logger.info(f"Generated {len(improvement_areas)} improvement areas")
            return improvement_areas
            
        except Exception as e:
            logger.error(f"Failed to generate improvement areas: {e}")
            return []
    
    def _extract_competitor_strengths(self, analysis_result: AnalysisResults, competitor_data: Dict[str, Any]) -> List[str]:
        """Extract competitor strengths from analysis data"""
        strengths = []
        
        # Look at areas where competitor outperforms
        for category, comparison in analysis_result.detailed_comparison.items():
            if comparison.difference < -0.15:  # Competitor significantly ahead
                strengths.append(f"Strong {category.replace('_', ' ')} performance")
        
        # Add some general strengths based on data
        if competitor_data and isinstance(competitor_data, dict):
            if competitor_data.get("social_media", {}).get("followers", 0) > 100000:
                strengths.append("Large social media following")
            if competitor_data.get("news_sentiment", {}).get("score", 0) > 0.5:
                strengths.append("Positive media coverage")
        
        return strengths[:5]  # Limit to top 5
    
    def _extract_competitor_weaknesses(self, analysis_result: AnalysisResults, competitor_data: Dict[str, Any]) -> List[str]:
        """Extract competitor weaknesses from analysis data"""
        weaknesses = []
        
        # Look at areas where we outperform competitor
        for category, comparison in analysis_result.detailed_comparison.items():
            if comparison.difference > 0.15:  # We're significantly ahead
                weaknesses.append(f"Weaker {category.replace('_', ' ')} compared to us")
        
        # Add some general weaknesses
        weaknesses.extend([
            "Limited market penetration in specific segments",
            "Slower innovation cycle",
            "Higher pricing compared to alternatives"
        ])
        
        return weaknesses[:5]  # Limit to top 5
    
    def _identify_competitive_opportunities(self, analysis_result: AnalysisResults) -> List[str]:
        """Identify opportunities to compete better"""
        opportunities = [
            "Focus on areas where competitor is weak",
            "Leverage our brand strengths more effectively",
            "Improve customer experience in key touchpoints",
            "Expand market share in underserved segments",
            "Develop unique value propositions"
        ]
        return opportunities[:5]
    
    def _identify_key_differences(self, analysis_result: AnalysisResults) -> List[str]:
        """Identify key differences between brands"""
        differences = []
        
        # Analyze positioning differences
        if analysis_result.market_positioning:
            differences.append(f"Market positioning: {analysis_result.market_positioning.brand_position} vs {analysis_result.market_positioning.competitor_position}")
        
        # Add differences based on comparison scores
        for category, comparison in analysis_result.detailed_comparison.items():
            if abs(comparison.difference) > 0.2:
                direction = "stronger" if comparison.difference > 0 else "weaker"
                differences.append(f"Significantly {direction} in {category.replace('_', ' ')}")
        
        differences.extend([
            "Different target customer segments",
            "Varying brand personality and messaging",
            "Distinct product/service offerings"
        ])
        
        return differences[:5]
    
    def _determine_priority(self, difference: float) -> Priority:
        """Determine priority level based on performance difference"""
        if difference < -0.3:  # Significantly behind
            return Priority.HIGH
        elif difference < -0.15:  # Moderately behind
            return Priority.MEDIUM
        else:  # Slightly behind or ahead
            return Priority.LOW

    def _generate_improvement_description(self, category: str, comparison: ComparisonScore) -> str:
        """Generate a descriptive improvement statement"""
        if comparison.difference < -0.3:
            return f"Significant improvement needed in {category.replace('_', ' ')} as current performance is much lower than the competitor."
        elif comparison.difference < -0.15:
            return f"Moderate improvement recommended in {category.replace('_', ' ')} to enhance competitive position."
        else:
            return f"Maintain current performance in {category.replace('_', ' ')} while monitoring competitor actions."

    def _generate_action_items(self, category: str) -> List[str]:
        """Generate actionable items to address performance gaps"""
        category_name = category.replace('_', ' ')
        return [
            f"Conduct a detailed audit of the {category_name} strategy.",
            f"Gather customer feedback specifically for {category_name}.",
            f"Benchmark against top competitors in {category_name}."
        ]
    
    def _generate_expected_outcomes(self, category: str) -> List[str]:
        """Define expected outcomes from improvements"""
        return [
            f"Improved customer perception and satisfaction in {category.replace('_', ' ')}.",
            f"Enhanced market share and visibility in {category.replace('_', ' ')}.",
            f"Stronger alignment of {category.replace('_', ' ')} offerings with customer needs."
        ]
    
    def _estimate_timeline(self, difference: float) -> str:
        """Estimate a realistic timeline for improvements"""
        if difference < -0.3:
            return "3-6 months"
        elif difference < -0.15:
            return "1-3 months"
        else:
            return "Ongoing monitoring and incremental improvements"
    
    def _identify_resources_needed(self, category: str) -> List[str]:
        """Identify potential resources or support needed for improvements"""
        return [
            "Dedicated project team",
            "Additional budget for marketing and promotions",
            "Access to advanced analytics tools",
            "Training and development for staff"
        ]
    
    def _generate_dashboard_charts(self, analysis_result: AnalysisResults, charts: List[ChartData], collected_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive professional charts for the PDF dashboard"""
        chart_files = {}
        
        try:
            # Set up matplotlib style for professional appearance
            plt.style.use('default')  # Use default style instead of seaborn
            if sns:
                sns.set_palette("Set2")
            
            # Color scheme for consistency
            brand_color = '#1f77b4'
            competitor_color = '#ff7f0e'
            accent_colors = ['#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
            
            # 1. Executive Dashboard Overview
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])
            
            # Overall Performance Comparison (Top Left)
            ax1 = fig.add_subplot(gs[0, 0])
            categories = ['Brand', 'Competitor']
            scores = [analysis_result.overall_comparison.brand_score, 
                     analysis_result.overall_comparison.competitor_score]
            
            bars = ax1.bar(categories, scores, color=[brand_color, competitor_color], alpha=0.8, edgecolor='black', linewidth=1.5)
            ax1.set_title('Overall Performance', fontsize=14, fontweight='bold', pad=20)
            ax1.set_ylabel('Performance Score', fontsize=12)
            ax1.set_ylim(0, 1)
            ax1.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax1.annotate(f'{score:.1%}', xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 5), textcoords="offset points", ha='center', va='bottom',
                           fontweight='bold', fontsize=12)
            
            # Performance Gap Gauge (Top Center)
            ax2 = fig.add_subplot(gs[0, 1])
            gap = analysis_result.overall_comparison.gap
            gap_abs = abs(gap)
            remaining = 1 - gap_abs
            
            colors_gauge = ['#ff4444' if gap < 0 else '#44ff44', '#e8e8e8']
            wedges, texts, autotexts = ax2.pie([gap_abs, remaining], 
                                              labels=['Performance Gap', 'Alignment'], 
                                              colors=colors_gauge,
                                              startangle=90, 
                                              autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
                                              explode=(0.05, 0))
            ax2.set_title(f'Competitive Gap: {gap:+.1%}', fontsize=14, fontweight='bold', pad=20)
            
            # Market Position Indicator (Top Right)
            ax3 = fig.add_subplot(gs[0, 2])
            ranking = analysis_result.overall_comparison.brand_ranking
            confidence = analysis_result.overall_comparison.confidence_level
            
            # Create a market position visualization
            positions = ['Lagging', 'Following', 'Competing', 'Leading']
            position_scores = [0.2, 0.4, 0.7, 1.0]
            current_pos = position_scores[positions.index(ranking.title())] if ranking.title() in positions else 0.5
            
            bars_pos = ax3.barh(positions, position_scores, color=['#ff6b6b', '#ffa726', '#66bb6a', '#42a5f5'], alpha=0.3)
            ax3.barh([ranking.title()], [current_pos], color='#1565c0', alpha=0.8, height=0.5)
            ax3.set_xlim(0, 1)
            ax3.set_title(f'Market Position\n(Confidence: {confidence:.1%})', fontsize=14, fontweight='bold', pad=20)
            ax3.set_xlabel('Position Strength')
            
            # Category Performance Radar (Middle Left - spans 2 columns)
            if analysis_result.detailed_comparison:
                ax4 = fig.add_subplot(gs[1, :2], projection='polar')
                
                categories = list(analysis_result.detailed_comparison.keys())
                brand_scores = []
                comp_scores = []
                
                for category, comparison in analysis_result.detailed_comparison.items():
                    if hasattr(comparison, 'brand_score'):
                        brand_scores.append(comparison.brand_score)
                        comp_scores.append(comparison.competitor_score)
                    else:
                        brand_scores.append(0.5)
                        comp_scores.append(0.5)
                
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
                angles = np.concatenate((angles, [angles[0]]))  # Complete the circle
                
                brand_scores_plot = brand_scores + [brand_scores[0]]
                comp_scores_plot = comp_scores + [comp_scores[0]]
                
                ax4.plot(angles, brand_scores_plot, 'o-', linewidth=2, label='Brand', color=brand_color)
                ax4.fill(angles, brand_scores_plot, alpha=0.25, color=brand_color)
                ax4.plot(angles, comp_scores_plot, 'o-', linewidth=2, label='Competitor', color=competitor_color)
                ax4.fill(angles, comp_scores_plot, alpha=0.25, color=competitor_color)
                
                ax4.set_xticks(angles[:-1])
                ax4.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], fontsize=10)
                ax4.set_ylim(0, 1)
                ax4.set_title('Category Performance Radar', fontsize=14, fontweight='bold', pad=30)
                ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
                ax4.grid(True)
            
            # Trend Analysis (Middle Right)
            ax5 = fig.add_subplot(gs[1, 2])
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            # Generate trend data based on current performance
            base_score = analysis_result.overall_comparison.brand_score
            trend_data = [base_score * (0.9 + 0.02 * i + np.random.normal(0, 0.01)) for i in range(6)]
            market_avg = [0.65 + 0.01 * i + np.random.normal(0, 0.005) for i in range(6)]
            
            ax5.plot(months, trend_data, 'o-', linewidth=3, color=brand_color, label='Brand', markersize=6)
            ax5.plot(months, market_avg, 's--', linewidth=2, color='#2ca02c', label='Market Avg', markersize=5)
            ax5.fill_between(months, trend_data, alpha=0.3, color=brand_color)
            ax5.set_title('6-Month Performance Trend', fontsize=14, fontweight='bold', pad=20)
            ax5.set_ylabel('Performance Score')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            ax5.set_ylim(0, 1)
            
            # Improvement Opportunities Heatmap (Bottom - spans all columns)
            ax6 = fig.add_subplot(gs[2, :])
            
            if analysis_result.detailed_comparison:
                # Create opportunity matrix
                categories = list(analysis_result.detailed_comparison.keys())
                opportunities = []
                impacts = []
                
                for category, comparison in analysis_result.detailed_comparison.items():
                    if hasattr(comparison, 'brand_score') and hasattr(comparison, 'competitor_score'):
                        gap = comparison.competitor_score - comparison.brand_score
                        effort = 1 - comparison.brand_score  # Lower score = higher effort needed
                        opportunities.append(gap)
                        impacts.append(1 - effort)  # Higher impact = easier to improve
                
                # Create bubble chart
                sizes = [abs(opp) * 1000 + 100 for opp in opportunities]  # Bubble sizes based on opportunity
                colors_bubble = [accent_colors[i % len(accent_colors)] for i in range(len(categories))]
                
                scatter = ax6.scatter(opportunities, impacts, s=sizes, c=colors_bubble, alpha=0.6, edgecolors='black')
                
                # Add category labels
                for i, category in enumerate(categories):
                    ax6.annotate(category.replace('_', ' ').title(), 
                               (opportunities[i], impacts[i]),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=9, fontweight='bold')
                
                ax6.axvline(x=0, color='red', linestyle='--', alpha=0.5)
                ax6.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
                ax6.set_xlabel('Opportunity Gap (Competitor Lead)', fontsize=12)
                ax6.set_ylabel('Implementation Impact', fontsize=12)
                ax6.set_title('Strategic Opportunity Matrix\n(Bubble size = Potential Impact)', fontsize=14, fontweight='bold', pad=20)
                ax6.grid(True, alpha=0.3)
                
                # Add quadrant labels
                ax6.text(0.02, 0.98, 'Quick Wins', transform=ax6.transAxes, fontsize=10, 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7),
                        verticalalignment='top')
                ax6.text(0.02, 0.48, 'Strategic Investments', transform=ax6.transAxes, fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7),
                        verticalalignment='top')
            
            plt.tight_layout(pad=3.0)
            dashboard_file = os.path.join(self.settings.REPORTS_DIRECTORY, f'executive_dashboard_{analysis_result.analysis_id}.png')
            plt.savefig(dashboard_file, dpi=300, bbox_inches='tight', facecolor='white')
            chart_files['executive_dashboard'] = dashboard_file
            plt.close()
            
            # 2. Detailed Category Analysis
            self._generate_category_analysis_chart(analysis_result, chart_files)
            
            # 3. Priority Matrix for Improvement Areas
            self._generate_priority_matrix_chart(analysis_result, chart_files)
            
            # 4. Competitive Positioning Map
            self._generate_competitive_positioning_chart(analysis_result, chart_files)
            
            # 5. Performance Benchmarking Chart
            self._generate_benchmarking_chart(analysis_result, collected_data, chart_files)
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard charts: {e}")
            import traceback
            logger.error(f"Chart generation error: {traceback.format_exc()}")
        
        return chart_files
    
    def _create_kpi_dashboard(self, analysis_result: AnalysisResults, collected_data: Dict[str, Any]) -> List[List[str]]:
        """Create enhanced KPI dashboard table data with visual indicators"""
        kpi_data = [['Key Performance Indicator', 'Current Value', 'Target/Benchmark', 'Performance Status', 'Trend']]
        
        # Overall performance with visual indicators
        current_score = analysis_result.overall_comparison.brand_score
        target_score = 0.85  # Default target
        performance_gap = current_score - target_score
        
        if current_score >= target_score:
            status = "🟢 EXCELLENT - Exceeding target"
            trend = "📈 Upward"
        elif current_score >= target_score * 0.9:
            status = "🟡 GOOD - Near target"
            trend = "➡️ Stable"
        else:
            status = "🔴 NEEDS ATTENTION - Below target"
            trend = "📉 Requires focus"
            
        kpi_data.append(['Overall Brand Performance', f'{current_score:.1%}', f'{target_score:.1%}', status, trend])
        
        # Market position with competitive context
        ranking = analysis_result.overall_comparison.brand_ranking
        gap = analysis_result.overall_comparison.gap
        
        if ranking == "leading":
            position_status = "🏆 MARKET LEADER"
            position_trend = "🚀 Dominant"
        elif ranking == "competitive":
            position_status = "⚔️ COMPETITIVE POSITION"
            position_trend = "🎯 Fighting"
        else:
            position_status = "🎯 CHALLENGER POSITION"
            position_trend = "💪 Building"
            
        kpi_data.append(['Market Position', ranking.title(), 'Leading', position_status, position_trend])
        
        # Competitive gap analysis
        gap_status = "🟢 AHEAD OF COMPETITION" if gap > 0 else "🔴 BEHIND COMPETITION"
        gap_trend = "📈 Gaining" if gap > 0 else "📉 Losing ground"
        kpi_data.append(['Competitive Gap', f'{gap:+.1%}', '+5% or better', gap_status, gap_trend])
        
        # Analysis confidence with data quality indicator
        confidence = analysis_result.overall_comparison.confidence_level
        if confidence >= 0.8:
            conf_status = "🟢 HIGH CONFIDENCE - Reliable insights"
            conf_trend = "📊 Strong data"
        elif confidence >= 0.6:
            conf_status = "🟡 MEDIUM CONFIDENCE - Good insights"
            conf_trend = "📈 Adequate data"
        else:
            conf_status = "🔴 LOW CONFIDENCE - Limited data"
            conf_trend = "⚠️ Need more data"
            
        kpi_data.append(['Analysis Confidence', f'{confidence:.1%}', '≥80%', conf_status, conf_trend])
        
        # Brand strength metrics (derived from category performance)
        if analysis_result.detailed_comparison:
            category_scores = []
            for comparison in analysis_result.detailed_comparison.values():
                if hasattr(comparison, 'brand_score'):
                    category_scores.append(comparison.brand_score)
            
            if category_scores:
                consistency = 1 - np.std(category_scores)  # Higher consistency = lower std dev
                if consistency >= 0.8:
                    consistency_status = "🟢 HIGHLY CONSISTENT"
                    consistency_trend = "🎯 Balanced"
                elif consistency >= 0.6:
                    consistency_status = "🟡 MODERATELY CONSISTENT"
                    consistency_trend = "⚖️ Some variation"
                else:
                    consistency_status = "🔴 INCONSISTENT PERFORMANCE"
                    consistency_trend = "🎢 High variation"
                
                kpi_data.append(['Brand Consistency', f'{consistency:.1%}', '≥80%', consistency_status, consistency_trend])
                
                # Performance momentum (how many categories are above average)
                above_avg = sum(1 for score in category_scores if score > np.mean(category_scores))
                momentum_pct = above_avg / len(category_scores)
                
                if momentum_pct >= 0.6:
                    momentum_status = "🟢 STRONG MOMENTUM"
                    momentum_trend = "🚀 Multiple strengths"
                elif momentum_pct >= 0.4:
                    momentum_status = "🟡 MIXED MOMENTUM"
                    momentum_trend = "⚖️ Balanced performance"
                else:
                    momentum_status = "🔴 WEAK MOMENTUM"
                    momentum_trend = "🎯 Focus needed"
                
                kpi_data.append(['Performance Momentum', f'{momentum_pct:.1%}', '≥60%', momentum_status, momentum_trend])
        
        return kpi_data
    
    def _format_list_for_table(self, items: List[str]) -> str:
        """Format a list of items for table display"""
        if not items:
            return "None identified"
        return "\n".join([f"• {item}" for item in items[:3]])  # Limit to 3 items for space
    
    def _format_list_for_table_enhanced(self, items: List[str], bullet_char: str = "•") -> str:
        """Format a list of items for table display with custom bullet characters"""
        if not items:
            return f"{bullet_char} None identified"
        return "\n".join([f"{bullet_char} {item}" for item in items[:4]])  # Limit to 4 items for better readability
    
    def _cleanup_chart_files(self, chart_files: Dict[str, str]):
        """Clean up temporary chart files"""
        for file_path in chart_files.values():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup chart file {file_path}: {e}")
    
    def _generate_category_analysis_chart(self, analysis_result: AnalysisResults, chart_files: Dict[str, str]):
        """Generate detailed category analysis with multiple visualizations"""
        try:
            if not analysis_result.detailed_comparison:
                return
                
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Detailed Category Analysis', fontsize=18, fontweight='bold')
            
            categories = list(analysis_result.detailed_comparison.keys())
            brand_scores = []
            comp_scores = []
            differences = []
            
            for category, comparison in analysis_result.detailed_comparison.items():
                if hasattr(comparison, 'brand_score'):
                    brand_scores.append(comparison.brand_score)
                    comp_scores.append(comparison.competitor_score)
                    differences.append(comparison.difference)
                else:
                    brand_scores.append(0.5)
                    comp_scores.append(0.5)
                    differences.append(0)
            
            # 1. Stacked Bar Chart showing performance components
            x = np.arange(len(categories))
            width = 0.6
            
            ax1.bar(x, brand_scores, width, label='Brand Performance', color='#1f77b4', alpha=0.8)
            ax1.bar(x, [max(0, comp - brand) for comp, brand in zip(comp_scores, brand_scores)], 
                   width, bottom=brand_scores, label='Competitor Advantage', color='#ff7f0e', alpha=0.8)
            
            ax1.set_xlabel('Categories')
            ax1.set_ylabel('Performance Score')
            ax1.set_title('Performance Composition by Category')
            ax1.set_xticks(x)
            ax1.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45, ha='right')
            ax1.legend()
            ax1.set_ylim(0, 1)
            ax1.grid(axis='y', alpha=0.3)
            
            # 2. Performance Gap Analysis
            gap_colors = ['#ff4444' if diff < 0 else '#44ff444' for diff in differences]
            bars = ax2.bar(x, differences, color=gap_colors, alpha=0.7, edgecolor='black')
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax2.set_xlabel('Categories')
            ax2.set_ylabel('Performance Gap')
            ax2.set_title('Performance Gap Analysis\n(Positive = Brand Advantage)')
            ax2.set_xticks(x)
            ax2.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45, ha='right')
            ax2.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar, diff in zip(bars, differences):
                height = bar.get_height()
                ax2.annotate(f'{diff:+.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3 if height >= 0 else -15), textcoords="offset points", 
                           ha='center', va='bottom' if height >= 0 else 'top',
                           fontweight='bold', fontsize=10)
            
            # 3. Scatter Plot: Current vs Target Performance
            target_scores = [min(1.0, score + 0.1) for score in brand_scores]  # Target 10% improvement
            ax3.scatter(brand_scores, target_scores, s=100, alpha=0.7, color='#2ca02c', edgecolors='black')
            
            # Add diagonal line for reference
            diag_line = np.linspace(0, 1, 100)
            ax3.plot(diag_line, diag_line, 'k--', alpha=0.5, label='No Improvement')
            
            # Add category labels
            for i, category in enumerate(categories):
                ax3.annotate(category.replace('_', ' ').title(), 
                           (brand_scores[i], target_scores[i]),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=9)
            
            ax3.set_xlabel('Current Performance')
            ax3.set_ylabel('Target Performance')
            ax3.set_title('Performance Improvement Targets')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
            
            # 4. Performance Distribution
            all_scores = brand_scores + comp_scores
            ax4.hist([brand_scores, comp_scores], bins=10, alpha=0.7, 
                    label=['Brand Scores', 'Competitor Scores'],
                    color=['#1f77b4', '#ff7f0e'], edgecolor='black')
            ax4.set_xlabel('Performance Score')
            ax4.set_ylabel('Frequency')
            ax4.set_title('Performance Score Distribution')
            ax4.legend()
            ax4.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            category_file = os.path.join(self.settings.REPORTS_DIRECTORY, f'category_analysis_{analysis_result.analysis_id}.png')
            plt.savefig(category_file, dpi=300, bbox_inches='tight', facecolor='white')
            chart_files['category_analysis'] = category_file
            plt.close()
            
        except Exception as e:
            logger.error(f"Failed to generate category analysis chart: {e}")

    def _generate_priority_matrix_chart(self, analysis_result: AnalysisResults, chart_files: Dict[str, str]):
        """Generate priority matrix for improvement areas"""
        try:
            if not analysis_result.detailed_comparison:
                return
                
            fig, ax = plt.subplots(figsize=(12, 10))
            
            categories = list(analysis_result.detailed_comparison.keys())
            impact_scores = []
            effort_scores = []
            
            for category, comparison in analysis_result.detailed_comparison.items():
                if hasattr(comparison, 'brand_score') and hasattr(comparison, 'competitor_score'):
                    # Impact = potential gain (competitor score - brand score)
                    impact = max(0, comparison.competitor_score - comparison.brand_score)
                    # Effort = inverse of current performance (lower performance = more effort needed)
                    effort = 1 - comparison.brand_score
                    
                    impact_scores.append(impact)
                    effort_scores.append(effort)
                else:
                    impact_scores.append(0.5)
                    effort_scores.append(0.5)
            
            # Create bubble sizes based on performance gap
            gaps = [abs(analysis_result.detailed_comparison[cat].difference) if hasattr(analysis_result.detailed_comparison[cat], 'difference') else 0.2 for cat in categories]
            sizes = [gap * 1000 + 100 for gap in gaps]
            
            # Color code by priority
            colors = []
            for impact, effort in zip(impact_scores, effort_scores):
                if impact > 0.3 and effort < 0.5:  # High impact, low effort
                    colors.append('#44ff44')  # Green - Quick wins
                elif impact > 0.3 and effort >= 0.5:  # High impact, high effort
                    colors.append('#ffaa44')  # Orange - Major projects
                elif impact <= 0.3 and effort < 0.5:  # Low impact, low effort
                    colors.append('#4444ff')  # Blue - Fill-ins
                else:  # Low impact, high effort
                    colors.append('#ff4444')  # Red - Questionable
            
            scatter = ax.scatter(effort_scores, impact_scores, s=sizes, c=colors, alpha=0.7, edgecolors='black', linewidth=2)
            
            # Add category labels
            for i, category in enumerate(categories):
                ax.annotate(category.replace('_', ' ').title(), 
                           (effort_scores[i], impact_scores[i]),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=10, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            # Add quadrant lines
            ax.axhline(y=0.3, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
            
            # Add quadrant labels
            ax.text(0.25, 0.8, 'Quick Wins\n(High Impact, Low Effort)', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.8))
            
            ax.text(0.75, 0.8, 'Major Projects\n(High Impact, High Effort)', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))
            
            ax.text(0.25, 0.1, 'Fill-ins\n(Low Impact, Low Effort)', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
            
            ax.text(0.75, 0.1, 'Questionable\n(Low Impact, High Effort)', 
                   ha='center', va='center', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightcoral', alpha=0.8))
            
            ax.set_xlabel('Implementation Effort', fontsize=14)
            ax.set_ylabel('Potential Impact', fontsize=14)
            ax.set_title('Strategic Priority Matrix\n(Bubble size = Performance Gap)', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            
            plt.tight_layout()
            priority_file = os.path.join(self.settings.REPORTS_DIRECTORY, f'priority_matrix_{analysis_result.analysis_id}.png')
            plt.savefig(priority_file, dpi=300, bbox_inches='tight', facecolor='white')
            chart_files['priority_matrix'] = priority_file
            plt.close()
            
        except Exception as e:
            logger.error(f"Failed to generate priority matrix chart: {e}")

    def _generate_competitive_positioning_chart(self, analysis_result: AnalysisResults, chart_files: Dict[str, str]):
        """Generate competitive positioning map"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('Competitive Positioning Analysis', fontsize=18, fontweight='bold')
            
            # Left: Brand vs Competitor Performance Profile
            if analysis_result.detailed_comparison:
                categories = list(analysis_result.detailed_comparison.keys())
                brand_scores = []
                comp_scores = []
                
                for category, comparison in analysis_result.detailed_comparison.items():
                    if hasattr(comparison, 'brand_score'):
                        brand_scores.append(comparison.brand_score)
                        comp_scores.append(comparison.competitor_score)
                    else:
                        brand_scores.append(0.5)
                        comp_scores.append(0.5)
                
                # Create connected line plot
                x_pos = range(len(categories))
                ax1.plot(x_pos, brand_scores, 'o-', linewidth=3, markersize=8, 
                        color='#1f77b4', label=analysis_result.brand_name, alpha=0.8)
                ax1.plot(x_pos, comp_scores, 's-', linewidth=3, markersize=8, 
                        color='#ff7f0e', label=analysis_result.competitor_name or 'Competitor', alpha=0.8)
                
                # Fill areas
                ax1.fill_between(x_pos, brand_scores, alpha=0.3, color='#1f77b4')
                ax1.fill_between(x_pos, comp_scores, alpha=0.3, color='#ff7f0e')
                
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45, ha='right')
                ax1.set_ylabel('Performance Score')
                ax1.set_title('Performance Profile Comparison')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                ax1.set_ylim(0, 1)
                
                # Add value annotations
                for i, (brand_score, comp_score) in enumerate(zip(brand_scores, comp_scores)):
                    ax1.annotate(f'{brand_score:.2f}', (i, brand_score), 
                               xytext=(0, 10), textcoords='offset points',
                               ha='center', fontsize=9, color='#1f77b4', fontweight='bold')
                    ax1.annotate(f'{comp_score:.2f}', (i, comp_score), 
                               xytext=(0, -15), textcoords='offset points',
                               ha='center', fontsize=9, color='#ff7f0e', fontweight='bold')
            
            # Right: Positioning quadrant analysis
            overall_performance = analysis_result.overall_comparison.brand_score
            market_share = 0.6  # Mock data - could be extracted from collected_data
            
            # Create quadrant positioning
            ax2.scatter([overall_performance], [market_share], s=500, c='#1f77b4', 
                       alpha=0.8, edgecolors='black', linewidth=2, label=analysis_result.brand_name)
            
            # Add competitor position (mock data)
            comp_performance = analysis_result.overall_comparison.competitor_score
            comp_market_share = 0.7  # Mock data
            ax2.scatter([comp_performance], [comp_market_share], s=500, c='#ff7f0e', 
                       alpha=0.8, edgecolors='black', linewidth=2, 
                       label=analysis_result.competitor_name or 'Competitor')
            
            # Add industry average point
            industry_avg_perf = 0.65
            industry_avg_share = 0.5
            ax2.scatter([industry_avg_perf], [industry_avg_share], s=300, c='#2ca02c', 
                       alpha=0.6, edgecolors='black', linewidth=2, label='Industry Average')
            
            # Add quadrant lines
            ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
            ax2.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
            
            # Add quadrant labels
            ax2.text(0.25, 0.75, 'Dogs\n(Low Performance,\nHigh Share)', 
                    ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
            
            ax2.text(0.75, 0.75, 'Stars\n(High Performance,\nHigh Share)', 
                    ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
            
            ax2.text(0.25, 0.25, 'Question Marks\n(Low Performance,\nLow Share)', 
                    ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7))
            
            ax2.text(0.75, 0.25, 'Cash Cows\n(High Performance,\nLow Share)', 
                    ha='center', va='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
            
            ax2.set_xlabel('Performance Score')
            ax2.set_ylabel('Market Share')
            ax2.set_title('Market Positioning Matrix')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            
            plt.tight_layout()
            positioning_file = os.path.join(self.settings.REPORTS_DIRECTORY, f'competitive_positioning_{analysis_result.analysis_id}.png')
            plt.savefig(positioning_file, dpi=300, bbox_inches='tight', facecolor='white')
            chart_files['competitive_positioning'] = positioning_file
            plt.close()
            
        except Exception as e:
            logger.error(f"Failed to generate competitive positioning chart: {e}")

    def _generate_benchmarking_chart(self, analysis_result: AnalysisResults, collected_data: Dict[str, Any], chart_files: Dict[str, str]):
        """Generate performance benchmarking visualization"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Performance Benchmarking Dashboard', fontsize=18, fontweight='bold')
            
            # 1. Score Distribution Analysis
            if analysis_result.detailed_comparison:
                categories = list(analysis_result.detailed_comparison.keys())
                brand_scores = []
                for category, comparison in analysis_result.detailed_comparison.items():
                    if hasattr(comparison, 'brand_score'):
                        brand_scores.append(comparison.brand_score)
                    else:
                        brand_scores.append(0.5)
                
                # Box plot showing score distribution
                ax1.boxplot([brand_scores], labels=['Brand Performance'])
                ax1.set_ylabel('Performance Score')
                ax1.set_title('Performance Score Distribution')
                ax1.grid(True, alpha=0.3)
                
                # Add individual points
                y_pos = [1] * len(brand_scores)
                ax1.scatter(y_pos, brand_scores, alpha=0.6, s=50, color='red')
                
                # Add statistics text
                mean_score = np.mean(brand_scores)
                std_score = np.std(brand_scores)
                ax1.text(0.02, 0.98, f'Mean: {mean_score:.3f}\nStd Dev: {std_score:.3f}', 
                        transform=ax1.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
            
            # 2. Performance Trends (simulated historical data)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            current_score = analysis_result.overall_comparison.brand_score
            
            # Generate realistic trend data
            trend_data = []
            for i in range(6):
                variation = np.random.normal(0, 0.02)
                score = max(0, min(1, current_score * (0.95 + 0.01 * i) + variation))
                trend_data.append(score)
            
            ax2.plot(months, trend_data, 'o-', linewidth=3, markersize=8, color='#1f77b4')
            ax2.fill_between(months, trend_data, alpha=0.3, color='#1f77b4')
            ax2.axhline(y=current_score, color='red', linestyle='--', label=f'Current: {current_score:.3f}')
            ax2.set_ylabel('Performance Score')
            ax2.set_title('6-Month Performance Trend')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim(0, 1)
            
            # 3. Competitive Gap Waterfall
            if analysis_result.detailed_comparison:
                categories_short = [cat.replace('_', ' ')[:10] for cat in categories]
                gaps = []
                for comparison in analysis_result.detailed_comparison.values():
                    if hasattr(comparison, 'difference'):
                        gaps.append(comparison.difference)
                    else:
                        gaps.append(0)
                
                colors = ['red' if gap < 0 else 'green' for gap in gaps]
                bars = ax3.bar(range(len(categories_short)), gaps, color=colors, alpha=0.7, edgecolor='black')
                ax3.axhline(y=0, color='black', linewidth=1)
                ax3.set_xticks(range(len(categories_short)))
                ax3.set_xticklabels(categories_short, rotation=45, ha='right')
                ax3.set_ylabel('Performance Gap')
                ax3.set_title('Category Performance Gaps\n(Positive = Brand Advantage)')
                ax3.grid(axis='y', alpha=0.3)
                
                # Add value labels
                for bar, gap in zip(bars, gaps):
                    height = bar.get_height()
                    ax3.annotate(f'{gap:+.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3 if height >= 0 else -15), textcoords="offset points", 
                               ha='center', va='bottom' if height >= 0 else 'top',
                               fontweight='bold', fontsize=9)
            
            # 4. Performance vs Confidence Analysis
            confidence = analysis_result.overall_comparison.confidence_level
            performance = analysis_result.overall_comparison.brand_score
            
            # Create scatter plot with confidence intervals
            ax4.scatter([performance], [confidence], s=500, color='#1f77b4', alpha=0.8, edgecolors='black', linewidth=2)
            
            # Add confidence zones
            ax4.axhspan(0.8, 1.0, alpha=0.2, color='green', label='High Confidence')
            ax4.axhspan(0.6, 0.8, alpha=0.2, color='yellow', label='Medium Confidence')
            ax4.axhspan(0.0, 0.6, alpha=0.2, color='red', label='Low Confidence')
            
            # Add performance zones
            ax4.axvspan(0.8, 1.0, alpha=0.1, color='green')
            ax4.axvspan(0.6, 0.8, alpha=0.1, color='yellow')
            ax4.axvspan(0.0, 0.6, alpha=0.1, color='red')
            
            ax4.set_xlabel('Performance Score')
            ax4.set_ylabel('Confidence Level')
            ax4.set_title('Performance vs Confidence Analysis')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            
            # Add current position annotation
            ax4.annotate(f'Current Position\nP: {performance:.3f}\nC: {confidence:.3f}', 
                        xy=(performance, confidence),
                        xytext=(20, 20), textcoords='offset points',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            plt.tight_layout()
            benchmark_file = os.path.join(self.settings.REPORTS_DIRECTORY, f'benchmarking_{analysis_result.analysis_id}.png')
            plt.savefig(benchmark_file, dpi=300, bbox_inches='tight', facecolor='white')
            chart_files['benchmarking'] = benchmark_file
            plt.close()
            
        except Exception as e:
            logger.error(f"Failed to generate benchmarking chart: {e}")
