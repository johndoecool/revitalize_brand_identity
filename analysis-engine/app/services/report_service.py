import json
import logging
from datetime import datetime
from typing import Dict, Any
from app.models.analysis import AnalysisResults

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.report_templates = {
            "executive_summary": self._generate_executive_summary,
            "detailed_comparison": self._generate_detailed_comparison,
            "actionable_insights": self._generate_insights_report,
            "market_positioning": self._generate_positioning_report
        }
    
    async def generate_analysis_report(self, results: AnalysisResults) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        """
        try:
            report = {
                "report_id": f"report_{results.analysis_id}",
                "generated_at": datetime.utcnow().isoformat(),
                "analysis_id": results.analysis_id,
                "executive_summary": self._generate_executive_summary(results),
                "detailed_analysis": self._generate_detailed_comparison(results),
                "actionable_insights": self._generate_insights_report(results),
                "market_positioning": self._generate_positioning_report(results),
                "confidence_metrics": {
                    "overall_confidence": results.confidence_score,
                    "data_quality_score": self._calculate_data_quality(results),
                    "recommendation_strength": self._calculate_recommendation_strength(results)
                }
            }
            
            logger.info(f"Generated comprehensive report for analysis: {results.analysis_id}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise Exception(f"Report generation failed: {str(e)}")
    
    async def generate_comparison_report(self, results: AnalysisResults) -> Dict[str, Any]:
        """
        Generate formatted comparison report
        """
        return {
            "comparison_summary": {
                "brand": results.brand_name,
                "competitor": results.competitor_name,
                "area": results.area_id,
                "overall_winner": self._determine_winner(results.overall_comparison),
                "performance_gap": abs(results.overall_comparison.gap),
                "key_differentiators": self._extract_key_differentiators(results)
            },
            "category_breakdown": self._format_category_breakdown(results.detailed_comparison),
            "recommendations": self._format_recommendations(results.actionable_insights[:3])  # Top 3
        }
    
    def _generate_executive_summary(self, results: AnalysisResults) -> Dict[str, Any]:
        """
        Generate executive summary section
        """
        winner = "brand" if results.overall_comparison.brand_score > results.overall_comparison.competitor_score else "competitor"
        gap_percentage = abs(results.overall_comparison.gap) * 100
        
        return {
            "overview": f"{results.brand_name} vs {results.competitor_name} analysis in {results.area_id}",
            "key_finding": f"{'Competitive disadvantage' if winner == 'competitor' else 'Competitive advantage'} with {gap_percentage:.1f}% performance gap",
            "primary_recommendation": results.actionable_insights[0].title if results.actionable_insights else "No recommendations available",
            "confidence_level": f"{results.confidence_score * 100:.0f}%",
            "analysis_date": results.analysis_timestamp.isoformat()
        }
    
    def _generate_detailed_comparison(self, results: AnalysisResults) -> Dict[str, Any]:
        """
        Generate detailed comparison section
        """
        comparison_details = {}
        
        for category, scores in results.detailed_comparison.items():
            comparison_details[category] = {
                "brand_performance": f"{scores.brand_score * 100:.0f}%",
                "competitor_performance": f"{scores.competitor_score * 100:.0f}%",
                "gap_analysis": f"{scores.difference * 100:+.1f}%",
                "strategic_insight": scores.insight,
                "competitive_status": "Leading" if scores.difference > 0 else "Lagging" if scores.difference < -0.05 else "Competitive"
            }
        
        return comparison_details
    
    def _generate_insights_report(self, results: AnalysisResults) -> Dict[str, Any]:
        """
        Generate actionable insights report
        """
        insights_by_priority = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        for insight in results.actionable_insights:
            priority_key = f"{insight.priority.value}_priority"
            insights_by_priority[priority_key].append({
                "title": insight.title,
                "description": insight.description,
                "category": insight.category,
                "effort_estimate": insight.estimated_effort,
                "expected_impact": insight.expected_impact,
                "implementation_roadmap": insight.implementation_steps,
                "success_metrics": self._generate_success_metrics(insight)
            })
        
        return {
            "insights_summary": {
                "total_recommendations": len(results.actionable_insights),
                "high_priority_count": len(insights_by_priority["high_priority"]),
                "quick_wins": len([i for i in results.actionable_insights if "month" in i.estimated_effort and "1-2" in i.estimated_effort])
            },
            "prioritized_insights": insights_by_priority
        }
    
    def _generate_positioning_report(self, results: AnalysisResults) -> Dict[str, Any]:
        """
        Generate market positioning report
        """
        return {
            "current_positioning": {
                "brand_position": results.market_positioning.brand_position,
                "competitor_position": results.market_positioning.competitor_position,
                "market_gap": results.market_positioning.differentiation_opportunity
            },
            "strategic_recommendations": {
                "positioning_strategy": results.market_positioning.differentiation_opportunity,
                "competitive_advantages": [strength.area for strength in results.strengths_to_maintain],
                "areas_for_improvement": [insight.category for insight in results.actionable_insights[:3]]
            },
            "brand_strengths": [
                {
                    "strength": strength.area,
                    "description": strength.description,
                    "strategic_value": strength.recommendation
                } for strength in results.strengths_to_maintain
            ]
        }
    
    def _determine_winner(self, comparison) -> str:
        """
        Determine the winning brand in overall comparison
        """
        if comparison.brand_score > comparison.competitor_score:
            return "brand"
        elif comparison.competitor_score > comparison.brand_score:
            return "competitor"
        else:
            return "tie"
    
    def _extract_key_differentiators(self, results: AnalysisResults) -> list:
        """
        Extract key differentiating factors
        """
        differentiators = []
        
        for category, scores in results.detailed_comparison.items():
            if abs(scores.difference) > 0.1:  # Significant difference
                differentiators.append({
                    "category": category,
                    "advantage": "brand" if scores.difference > 0 else "competitor",
                    "magnitude": abs(scores.difference)
                })
        
        # Sort by magnitude and return top 3
        differentiators.sort(key=lambda x: x["magnitude"], reverse=True)
        return differentiators[:3]
    
    def _format_category_breakdown(self, detailed_comparison: Dict) -> Dict[str, Any]:
        """
        Format category breakdown for report
        """
        formatted = {}
        
        for category, scores in detailed_comparison.items():
            formatted[category] = {
                "brand_score": scores.brand_score,
                "competitor_score": scores.competitor_score,
                "performance_gap": scores.difference,
                "insight": scores.insight,
                "recommendation": self._generate_category_recommendation(scores)
            }
        
        return formatted
    
    def _format_recommendations(self, insights: list) -> list:
        """
        Format top recommendations for report
        """
        formatted_recommendations = []
        
        for insight in insights:
            formatted_recommendations.append({
                "title": insight.title,
                "priority": insight.priority.value,
                "category": insight.category,
                "description": insight.description,
                "business_impact": insight.expected_impact,
                "implementation_timeline": insight.estimated_effort,
                "next_steps": insight.implementation_steps[:3]  # Top 3 steps
            })
        
        return formatted_recommendations
    
    def _generate_category_recommendation(self, scores) -> str:
        """
        Generate category-specific recommendation
        """
        if scores.difference > 0.1:
            return "Maintain competitive advantage and continue investment"
        elif scores.difference < -0.1:
            return "Priority area for improvement - immediate action required"
        else:
            return "Monitor competitive position and optimize incrementally"
    
    def _generate_success_metrics(self, insight) -> list:
        """
        Generate success metrics for insights
        """
        category_metrics = {
            "user_experience": ["User satisfaction score", "Task completion rate", "Time to complete actions"],
            "feature_development": ["Feature adoption rate", "User engagement metrics", "Customer feedback scores"],
            "security": ["Security incident reduction", "Compliance audit scores", "Customer trust metrics"],
            "performance": ["Page load times", "System uptime", "Error rates"]
        }
        
        return category_metrics.get(insight.category, ["Customer satisfaction", "Business impact metrics", "Competitive position"])
    
    def _calculate_data_quality(self, results: AnalysisResults) -> float:
        """
        Calculate data quality score
        """
        quality_factors = []
        
        # Check completeness of comparison data
        if results.detailed_comparison and len(results.detailed_comparison) >= 3:
            quality_factors.append(0.3)
        
        # Check insights quality
        if results.actionable_insights and len(results.actionable_insights) >= 2:
            quality_factors.append(0.3)
        
        # Check market positioning completeness
        if results.market_positioning and results.market_positioning.differentiation_opportunity:
            quality_factors.append(0.2)
        
        # Check strengths analysis
        if results.strengths_to_maintain:
            quality_factors.append(0.2)
        
        return sum(quality_factors)
    
    def _calculate_recommendation_strength(self, results: AnalysisResults) -> float:
        """
        Calculate recommendation strength score
        """
        if not results.actionable_insights:
            return 0.0
        
        strength_factors = []
        
        # Check for high-priority recommendations
        high_priority_count = len([i for i in results.actionable_insights if i.priority.value == "high"])
        if high_priority_count > 0:
            strength_factors.append(0.4)
        
        # Check for detailed implementation steps
        detailed_insights = len([i for i in results.actionable_insights if len(i.implementation_steps) >= 3])
        if detailed_insights >= 2:
            strength_factors.append(0.3)
        
        # Check for quantified impact
        quantified_insights = len([i for i in results.actionable_insights if any(char.isdigit() for char in i.expected_impact)])
        if quantified_insights >= 1:
            strength_factors.append(0.3)
        
        return sum(strength_factors)
