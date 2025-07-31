"""
Enhanced Report Service - Generates different types of reports for various audiences
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
import base64
import os
from io import BytesIO

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

from app.models.analysis import (
    AnalysisResults, ChartData, CompetitorInsight, ImprovementArea, 
    CompetitiveRoadmap, Priority
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class ReportType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_REPORT = "detailed_report"

class EnhancedReportService:
    """Service for generating enhanced PDF reports with different types"""
    
    def __init__(self):
        self.logger = logger
        # Set up matplotlib for better charts
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def generate_report(
        self,
        report_type: ReportType,
        analysis_result: AnalysisResults,
        charts: List[ChartData],
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea],
        roadmap: Optional[CompetitiveRoadmap] = None,
        collected_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate a PDF report based on the specified type
        Returns raw PDF bytes for direct download and saves locally if configured
        """
        try:
            self.logger.info(f"Generating {report_type} report for {analysis_result.brand_name}")
            
            # Generate PDF bytes
            if report_type == ReportType.EXECUTIVE_SUMMARY:
                pdf_bytes = self._generate_executive_summary(
                    analysis_result, competitor_insights, improvement_areas, roadmap
                )
            elif report_type == ReportType.DETAILED_REPORT:
                pdf_bytes = self._generate_detailed_report(
                    analysis_result, charts, competitor_insights, improvement_areas, 
                    roadmap, collected_data
                )
            else:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            # Save locally if configured
            if settings.SAVE_REPORTS_LOCALLY:
                filename = self.get_filename(report_type, analysis_result.analysis_id, analysis_result.brand_name)
                local_path = self._save_report_locally(pdf_bytes, filename)
                self.logger.info(f"Report saved locally: {local_path}")
            
            return pdf_bytes
                
        except Exception as e:
            self.logger.error(f"Failed to generate {report_type} report: {str(e)}")
            raise
    
    def _generate_executive_summary(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea],
        roadmap: Optional[CompetitiveRoadmap] = None
    ) -> bytes:
        """Generate executive summary report for C-level audience"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, 
            leftMargin=0.75*inch, rightMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )
        
        # Professional styles for executive audience
        styles = self._get_executive_styles()
        story = []
        
        # === COVER PAGE ===
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("EXECUTIVE SUMMARY", styles['title']))
        story.append(Paragraph("Brand Competitive Analysis", styles['subtitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive info box
        exec_data = [
            ['Brand', analysis_result.brand_name],
            ['Analysis Date', datetime.now().strftime("%B %d, %Y")],
            ['Overall Score', f"{analysis_result.overall_comparison.brand_score:.1%}"],
            ['Market Position', analysis_result.overall_comparison.brand_ranking],
            ['Confidence Level', f"{analysis_result.confidence_score:.1%}"]
        ]
        
        exec_table = Table(exec_data, colWidths=[2*inch, 3*inch])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.Color(0.1, 0.3, 0.6)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(exec_table)
        story.append(PageBreak())
        
        # === KEY FINDINGS ===
        story.append(Paragraph("KEY FINDINGS", styles['section']))
        
        # Performance overview
        gap = analysis_result.overall_comparison.gap
        if gap > 0:
            performance_text = f"<b>Market Advantage:</b> {analysis_result.brand_name} leads competitors by {gap:.1%}, indicating strong market position."
        else:
            performance_text = f"<b>Performance Gap:</b> {analysis_result.brand_name} trails market leaders by {abs(gap):.1%}, requiring strategic intervention."
        
        story.append(Paragraph(performance_text, styles['body']))
        story.append(Spacer(1, 0.2*inch))
        
        # Top 3 critical insights
        story.append(Paragraph("<b>Critical Insights:</b>", styles['subsection']))
        
        high_priority_areas = [area for area in improvement_areas if area.priority == Priority.HIGH][:3]
        for i, area in enumerate(high_priority_areas, 1):
            insight_text = f"<b>{i}. {area.area}:</b> Current performance at {area.current_score:.1%}, target {area.target_score:.1%}. {area.description}"
            story.append(Paragraph(insight_text, styles['body']))
            story.append(Spacer(1, 0.1*inch))
        
        # === COMPETITIVE LANDSCAPE ===
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("COMPETITIVE LANDSCAPE", styles['section']))
        
        if competitor_insights:
            primary_competitor = max(competitor_insights, key=lambda x: x.comparison_score)
            
            comp_text = f"""
            <b>Primary Competitor:</b> {primary_competitor.competitor_name} (Score: {primary_competitor.comparison_score:.1%})<br/>
            <b>Their Strengths:</b> {', '.join(primary_competitor.strengths[:3])}<br/>
            <b>Their Weaknesses:</b> {', '.join(primary_competitor.weaknesses[:3])}<br/>
            <b>Our Opportunity:</b> {', '.join(primary_competitor.opportunities[:2])}
            """
            story.append(Paragraph(comp_text, styles['body']))
        
        # === STRATEGIC ROADMAP (if available) ===
        if roadmap:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("12-MONTH STRATEGIC ROADMAP", styles['section']))
            
            story.append(Paragraph(f"<b>Strategic Vision:</b> {roadmap.strategic_vision}", styles['body']))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph(f"<b>Market Opportunity:</b> {roadmap.market_opportunity}", styles['body']))
            story.append(Spacer(1, 0.2*inch))
            
            # Quarterly themes
            story.append(Paragraph("<b>Quarterly Execution Plan:</b>", styles['subsection']))
            for quarter in roadmap.quarterly_roadmaps:
                quarter_text = f"<b>{quarter.quarter}:</b> {quarter.quarter_theme} - {quarter.quarter_budget or 'Budget TBD'}"
                story.append(Paragraph(quarter_text, styles['body']))
            
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"<b>Total Investment:</b> {roadmap.total_estimated_budget or 'TBD'}", styles['highlight']))
        
        # === RECOMMENDATIONS ===
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("EXECUTIVE RECOMMENDATIONS", styles['section']))
        
        # Top 3 recommendations
        recommendations = [
            "Immediate focus on high-priority improvement areas to close competitive gaps",
            "Invest in competitive intelligence systems for real-time market monitoring",
            "Implement quarterly roadmap execution with dedicated cross-functional teams"
        ]
        
        if roadmap:
            recommendations.append(f"Secure {roadmap.total_estimated_budget or 'estimated budget'} for 12-month strategic initiatives")
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"<b>{i}.</b> {rec}", styles['body']))
            story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _generate_detailed_report(
        self,
        analysis_result: AnalysisResults,
        charts: List[ChartData],
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea],
        roadmap: Optional[CompetitiveRoadmap] = None,
        collected_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate comprehensive detailed report for operational teams"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=0.5*inch, rightMargin=0.5*inch,
            topMargin=0.5*inch, bottomMargin=0.5*inch
        )
        
        styles = self._get_detailed_styles()
        story = []
        
        # === COVER PAGE ===
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("COMPREHENSIVE BRAND ANALYSIS", styles['title']))
        story.append(Paragraph("Detailed Competitive Intelligence Report", styles['subtitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Detailed info table
        detail_data = [
            ['Analysis ID', analysis_result.analysis_id],
            ['Brand Name', analysis_result.brand_name],
            ['Primary Competitor', analysis_result.competitor_name or 'Market Analysis'],
            ['Analysis Date', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Report Type', 'Comprehensive Analysis'],
            ['Confidence Score', f"{analysis_result.confidence_score:.1%}"],
            ['Data Sources', f"{len(collected_data.keys()) if collected_data else 'N/A'} sources analyzed"]
        ]
        
        detail_table = Table(detail_data, colWidths=[2.5*inch, 3.5*inch])
        detail_table.setStyle(self._get_table_style())
        story.append(detail_table)
        story.append(PageBreak())
        
        # === EXECUTIVE SUMMARY ===
        story.append(Paragraph("EXECUTIVE SUMMARY", styles['section']))
        
        summary_text = f"""
        This comprehensive analysis of {analysis_result.brand_name} reveals a current market performance 
        score of {analysis_result.overall_comparison.brand_score:.1%}, positioning the brand {analysis_result.overall_comparison.brand_ranking}. 
        The analysis identified {len(improvement_areas)} key improvement areas, with {len([a for a in improvement_areas if a.priority == Priority.HIGH])} 
        classified as high priority requiring immediate attention.
        """
        story.append(Paragraph(summary_text, styles['body']))
        story.append(Spacer(1, 0.3*inch))
        
        # === PERFORMANCE ANALYSIS ===
        story.append(Paragraph("DETAILED PERFORMANCE ANALYSIS", styles['section']))
        
        # Overall comparison table
        perf_data = [
            ['Metric', analysis_result.brand_name, 'Competitor Average', 'Gap', 'Status'],
            ['Overall Score', f"{analysis_result.overall_comparison.brand_score:.1%}", 
             f"{analysis_result.overall_comparison.competitor_score:.1%}",
             f"{analysis_result.overall_comparison.gap:+.1%}",
             "Leading" if analysis_result.overall_comparison.gap > 0 else "Trailing"]
        ]
        
        # Add detailed comparisons
        for category, comparison in analysis_result.detailed_comparison.items():
            status = "Leading" if comparison.difference > 0 else "Trailing"
            perf_data.append([
                category.replace('_', ' ').title(),
                f"{comparison.brand_score:.1%}",
                f"{comparison.competitor_score:.1%}",
                f"{comparison.difference:+.1%}",
                status
            ])
        
        perf_table = Table(perf_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 0.8*inch, 1*inch])
        perf_table.setStyle(self._get_performance_table_style())
        story.append(perf_table)
        story.append(Spacer(1, 0.3*inch))
        
        # === COMPETITIVE INTELLIGENCE ===
        story.append(Paragraph("COMPETITIVE INTELLIGENCE", styles['section']))
        
        for competitor in competitor_insights:
            story.append(Paragraph(f"Competitor: {competitor.competitor_name}", styles['subsection']))
            story.append(Paragraph(f"Performance Score: {competitor.comparison_score:.1%}", styles['highlight']))
            
            # SWOT-style analysis
            comp_data = [
                ['Strengths', 'Weaknesses'],
                ['\n'.join(f"• {s}" for s in competitor.strengths[:4]), 
                 '\n'.join(f"• {w}" for w in competitor.weaknesses[:4])],
                ['Opportunities', 'Key Differences'],
                ['\n'.join(f"• {o}" for o in competitor.opportunities[:3]), 
                 '\n'.join(f"• {d}" for d in competitor.key_differences[:3])]
            ]
            
            comp_table = Table(comp_data, colWidths=[3*inch, 3*inch])
            comp_table.setStyle(self._get_swot_table_style())
            story.append(comp_table)
            story.append(Spacer(1, 0.2*inch))
        
        # === IMPROVEMENT ROADMAP ===
        story.append(PageBreak())
        story.append(Paragraph("IMPROVEMENT ROADMAP", styles['section']))
        
        # Priority matrix
        priority_data = [['Priority', 'Area', 'Current', 'Target', 'Gap', 'Timeline', 'Resources']]
        
        for area in sorted(improvement_areas, key=lambda x: (0 if x.priority == Priority.HIGH else 1 if x.priority == Priority.MEDIUM else 2)):
            priority_color = "HIGH" if area.priority == Priority.HIGH else "MED" if area.priority == Priority.MEDIUM else "LOW"
            gap = area.target_score - area.current_score
            
            priority_data.append([
                priority_color,
                area.area,
                f"{area.current_score:.1%}",
                f"{area.target_score:.1%}",
                f"+{gap:.1%}",
                area.timeline,
                f"{len(area.resources_needed)} resources"
            ])
        
        priority_table = Table(priority_data, colWidths=[0.7*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.7*inch, 1*inch, 1*inch])
        priority_table.setStyle(self._get_priority_table_style())
        story.append(priority_table)
        
        # Detailed action plans
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("DETAILED ACTION PLANS", styles['subsection']))
        
        for area in improvement_areas[:5]:  # Top 5 areas
            story.append(Paragraph(f"{area.area} Improvement Plan", styles['subheading']))
            story.append(Paragraph(f"<b>Objective:</b> {area.description}", styles['body']))
            
            action_text = f"<b>Action Items:</b><br/>"
            for i, action in enumerate(area.action_items[:4], 1):
                action_text += f"{i}. {action}<br/>"
            
            story.append(Paragraph(action_text, styles['body']))
            
            outcome_text = f"<b>Expected Outcomes:</b> {', '.join(area.expected_outcomes[:3])}"
            story.append(Paragraph(outcome_text, styles['body']))
            story.append(Spacer(1, 0.2*inch))
        
        # === QUARTERLY ROADMAP ===
        if roadmap:
            story.append(PageBreak())
            story.append(Paragraph("QUARTERLY EXECUTION ROADMAP", styles['section']))
            
            story.append(Paragraph(f"<b>Strategic Vision:</b> {roadmap.strategic_vision}", styles['body']))
            story.append(Spacer(1, 0.2*inch))
            
            for quarter in roadmap.quarterly_roadmaps:
                story.append(Paragraph(f"{quarter.quarter}: {quarter.quarter_theme}", styles['subsection']))
                
                # Goals and budget
                goals_text = f"<b>Strategic Goals:</b><br/>"
                for goal in quarter.strategic_goals:
                    goals_text += f"• {goal}<br/>"
                story.append(Paragraph(goals_text, styles['body']))
                
                story.append(Paragraph(f"<b>Quarter Budget:</b> {quarter.quarter_budget or 'TBD'}", styles['highlight']))
                
                # Actions summary
                if quarter.actions:
                    story.append(Paragraph(f"<b>Key Actions ({len(quarter.actions)}):</b>", styles['body']))
                    for action in quarter.actions[:3]:  # Top 3 actions
                        action_text = f"• <b>{action.title}</b> - {action.category} ({action.estimated_effort})"
                        story.append(Paragraph(action_text, styles['body']))
                
                story.append(Spacer(1, 0.2*inch))
            
            # Total investment
            story.append(Paragraph(f"<b>Total 12-Month Investment:</b> {roadmap.total_estimated_budget or 'TBD'}", styles['highlight']))
        
        # === APPENDIX ===
        story.append(PageBreak())
        story.append(Paragraph("APPENDIX", styles['section']))
        
        # Data sources
        if collected_data:
            story.append(Paragraph("Data Sources Analyzed", styles['subsection']))
            for key, value in collected_data.items():
                if isinstance(value, (list, dict)):
                    count = len(value) if isinstance(value, list) else len(value.keys())
                    story.append(Paragraph(f"• {key.replace('_', ' ').title()}: {count} items", styles['body']))
        
        # Methodology
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Analysis Methodology", styles['subsection']))
        methodology_text = """
        This analysis employed advanced AI-powered competitive intelligence techniques, analyzing multiple data sources 
        including market research, competitor analysis, and performance metrics. The confidence score reflects the 
        reliability of data sources and analysis depth.
        """
        story.append(Paragraph(methodology_text, styles['body']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _get_executive_styles(self):
        """Get professional styles for executive reports"""
        styles = getSampleStyleSheet()
        
        return {
            'title': ParagraphStyle('ExecutiveTitle', parent=styles['Heading1'], 
                                  fontSize=24, spaceAfter=20, alignment=TA_CENTER,
                                  textColor=colors.Color(0.1, 0.3, 0.6), fontName='Helvetica-Bold'),
            'subtitle': ParagraphStyle('ExecutiveSubtitle', parent=styles['Heading2'], 
                                     fontSize=16, spaceAfter=30, alignment=TA_CENTER,
                                     textColor=colors.Color(0.3, 0.3, 0.3), fontName='Helvetica'),
            'section': ParagraphStyle('SectionHeader', parent=styles['Heading2'], 
                                    fontSize=16, spaceAfter=15, spaceBefore=20,
                                    textColor=colors.Color(0.1, 0.3, 0.6), fontName='Helvetica-Bold'),
            'subsection': ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                       fontSize=13, spaceAfter=8, spaceBefore=8,
                                       textColor=colors.Color(0.2, 0.4, 0.7), fontName='Helvetica-Bold'),
            'body': ParagraphStyle('ExecutiveBody', parent=styles['Normal'], 
                                 fontSize=11, textColor=colors.black, fontName='Helvetica',
                                 alignment=TA_JUSTIFY, spaceAfter=6),
            'highlight': ParagraphStyle('Highlight', parent=styles['Normal'], 
                                      fontSize=12, textColor=colors.Color(0.9, 0.4, 0.1),
                                      fontName='Helvetica-Bold', spaceAfter=6)
        }
    
    def _get_detailed_styles(self):
        """Get comprehensive styles for detailed reports"""
        styles = getSampleStyleSheet()
        
        return {
            'title': ParagraphStyle('DetailedTitle', parent=styles['Heading1'], 
                                  fontSize=22, spaceAfter=15, alignment=TA_CENTER,
                                  textColor=colors.Color(0.1, 0.3, 0.6), fontName='Helvetica-Bold'),
            'subtitle': ParagraphStyle('DetailedSubtitle', parent=styles['Heading2'], 
                                     fontSize=14, spaceAfter=20, alignment=TA_CENTER,
                                     textColor=colors.Color(0.3, 0.3, 0.3), fontName='Helvetica'),
            'section': ParagraphStyle('SectionHeader', parent=styles['Heading2'], 
                                    fontSize=15, spaceAfter=12, spaceBefore=15,
                                    textColor=colors.Color(0.1, 0.3, 0.6), fontName='Helvetica-Bold'),
            'subsection': ParagraphStyle('SubSection', parent=styles['Heading3'], 
                                       fontSize=12, spaceAfter=6, spaceBefore=6,
                                       textColor=colors.Color(0.2, 0.4, 0.7), fontName='Helvetica-Bold'),
            'subheading': ParagraphStyle('SubHeading', parent=styles['Heading4'], 
                                       fontSize=11, spaceAfter=4, spaceBefore=8,
                                       textColor=colors.Color(0.3, 0.3, 0.3), fontName='Helvetica-Bold'),
            'body': ParagraphStyle('DetailedBody', parent=styles['Normal'], 
                                 fontSize=10, textColor=colors.black, fontName='Helvetica',
                                 alignment=TA_LEFT, spaceAfter=4),
            'highlight': ParagraphStyle('Highlight', parent=styles['Normal'], 
                                      fontSize=11, textColor=colors.Color(0.9, 0.4, 0.1),
                                      fontName='Helvetica-Bold', spaceAfter=4)
        }
    
    def _get_table_style(self):
        """Standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.Color(0.1, 0.3, 0.6)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
    def _get_performance_table_style(self):
        """Performance table with conditional formatting"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.3, 0.6)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
        ])
    
    def _get_swot_table_style(self):
        """SWOT analysis table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.5, 0.8)),
            ('BACKGROUND', (0, 2), (-1, 2), colors.Color(0.2, 0.5, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (0, 3), (-1, 3), colors.Color(0.95, 0.95, 0.95)),
        ])
    
    def _get_priority_table_style(self):
        """Priority matrix table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.1, 0.3, 0.6)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
        ])
    
    def _save_report_locally(self, pdf_bytes: bytes, filename: str) -> str:
        """
        Save PDF report to local storage
        Returns the full path of the saved file
        """
        try:
            # Get the reports directory from settings
            reports_dir = settings.REPORTS_DIRECTORY
            
            # Convert to absolute path if it's relative
            if not os.path.isabs(reports_dir):
                reports_dir = os.path.abspath(reports_dir)
            
            # Create directory if it doesn't exist
            os.makedirs(reports_dir, exist_ok=True)
            
            # Full path for the file
            file_path = os.path.join(reports_dir, filename)
            
            # Write PDF bytes to file
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            self.logger.info(f"Report saved successfully: {file_path} ({len(pdf_bytes)} bytes)")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to save report locally: {str(e)}")
            # Don't raise exception here - local save failure shouldn't break the API response
            return ""
    
    def get_filename(self, report_type: ReportType, analysis_id: str, brand_name: str) -> str:
        """Generate appropriate filename for the report type"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_brand = "".join(c for c in brand_name if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        
        if report_type == ReportType.EXECUTIVE_SUMMARY:
            return f"{clean_brand}_Executive_Summary_{timestamp}.pdf"
        else:
            return f"{clean_brand}_Detailed_Analysis_{timestamp}.pdf"
