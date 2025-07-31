"""
Roadmap Service - Generates competitive roadmaps based on analysis results
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models.analysis import (
    CompetitiveRoadmap, QuarterlyRoadmap, RoadmapAction, 
    RoadmapPhase, Priority, AnalysisResults, CompetitorInsight,
    ImprovementArea
)
import uuid

logger = logging.getLogger(__name__)

class RoadmapService:
    """Service for generating competitive roadmaps"""
    
    def __init__(self):
        self.logger = logger
    
    async def generate_competitive_roadmap(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea],
        collected_data: Optional[Dict[str, Any]] = None
    ) -> CompetitiveRoadmap:
        """
        Generate a comprehensive competitive roadmap based on analysis results
        """
        try:
            self.logger.info(f"Generating competitive roadmap for brand: {analysis_result.brand_name}")
            
            # Extract key competitive intelligence
            competitive_summary = self._generate_competitive_summary(
                analysis_result, competitor_insights
            )
            
            # Define strategic vision based on gaps and opportunities
            strategic_vision = self._generate_strategic_vision(
                analysis_result, competitor_insights, improvement_areas
            )
            
            # Identify market opportunity
            market_opportunity = self._identify_market_opportunity(
                analysis_result, competitor_insights
            )
            
            # Determine competitive advantages to leverage
            competitive_advantages = self._extract_competitive_advantages(
                analysis_result, competitor_insights
            )
            
            # Generate quarterly roadmaps
            quarterly_roadmaps = await self._generate_quarterly_roadmaps(
                analysis_result, competitor_insights, improvement_areas
            )
            
            # Calculate total budget estimate
            total_budget = self._calculate_total_budget(quarterly_roadmaps)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                analysis_result, competitor_insights, improvement_areas
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                analysis_result, competitor_insights, improvement_areas
            )
            
            roadmap = CompetitiveRoadmap(
                roadmap_id=f"roadmap_{uuid.uuid4().hex[:8]}",
                brand_name=analysis_result.brand_name,
                competitor_analysis_summary=competitive_summary,
                strategic_vision=strategic_vision,
                market_opportunity=market_opportunity,
                competitive_advantages=competitive_advantages,
                quarterly_roadmaps=quarterly_roadmaps,
                total_estimated_budget=total_budget,
                risk_factors=risk_factors,
                generated_at=datetime.now(timezone.utc),
                confidence_score=confidence_score
            )
            
            self.logger.info(f"Successfully generated roadmap with {len(quarterly_roadmaps)} quarters")
            return roadmap
            
        except Exception as e:
            self.logger.error(f"Failed to generate competitive roadmap: {str(e)}")
            raise
    
    def _generate_competitive_summary(
        self, 
        analysis_result: AnalysisResults, 
        competitor_insights: List[CompetitorInsight]
    ) -> str:
        """Generate a summary of competitive analysis"""
        
        gap = analysis_result.overall_comparison.gap
        brand_ranking = analysis_result.overall_comparison.brand_ranking
        
        if gap > 0:
            performance_desc = f"currently leading with a {abs(gap):.1%} advantage"
        else:
            performance_desc = f"trailing by {abs(gap):.1%}"
        
        competitor_count = len(competitor_insights)
        top_competitor = max(competitor_insights, key=lambda x: x.comparison_score) if competitor_insights else None
        
        summary = f"""
        {analysis_result.brand_name} is {performance_desc} against primary competitors. 
        Analysis of {competitor_count} key competitors reveals {brand_ranking} market position. 
        {f"Primary threat: {top_competitor.competitor_name} with strong performance in {', '.join(top_competitor.strengths[:2])}." if top_competitor else ""}
        Key differentiators identified include {', '.join(analysis_result.market_positioning.differentiation_opportunity.split('.')[:2])}.
        """.strip().replace('\n        ', ' ')
        
        return summary
    
    def _generate_strategic_vision(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea]
    ) -> str:
        """Generate 12-month strategic vision"""
        
        high_priority_areas = [area.area for area in improvement_areas if area.priority == Priority.HIGH]
        
        vision = f"""
        Transform {analysis_result.brand_name} into a market leader by addressing critical gaps in 
        {', '.join(high_priority_areas[:3])} while leveraging strengths in {analysis_result.market_positioning.brand_position}. 
        Achieve {analysis_result.overall_comparison.brand_score + 0.15:.1%} overall performance score through 
        systematic competitive positioning and customer experience optimization.
        """.strip().replace('\n        ', ' ')
        
        return vision
    
    def _identify_market_opportunity(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight]
    ) -> str:
        """Identify key market opportunity"""
        
        # Find common weaknesses across competitors
        competitor_weaknesses = {}
        for insight in competitor_insights:
            for weakness in insight.weaknesses:
                competitor_weaknesses[weakness] = competitor_weaknesses.get(weakness, 0) + 1
        
        common_weakness = max(competitor_weaknesses.items(), key=lambda x: x[1])[0] if competitor_weaknesses else "digital transformation"
        
        opportunity = f"""
        Capture market share through superior {common_weakness} capabilities. 
        {analysis_result.market_positioning.differentiation_opportunity} 
        Target opportunity: {analysis_result.market_positioning.target_audience or 'underserved customer segments'} 
        with enhanced value proposition.
        """.strip().replace('\n        ', ' ')
        
        return opportunity
    
    def _extract_competitive_advantages(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight]
    ) -> List[str]:
        """Extract competitive advantages to leverage"""
        
        advantages = []
        
        # From strengths to maintain
        for strength in analysis_result.strengths_to_maintain[:3]:
            advantages.append(f"Proven strength in {strength.area}: {strength.description[:100]}...")
        
        # From market positioning
        advantages.append(f"Strategic positioning: {analysis_result.market_positioning.brand_position}")
        
        # From competitor analysis - areas where all competitors are weak
        if competitor_insights:
            all_competitor_weaknesses = set(competitor_insights[0].weaknesses)
            for insight in competitor_insights[1:]:
                all_competitor_weaknesses &= set(insight.weaknesses)
            
            if all_competitor_weaknesses:
                advantages.append(f"Market gap opportunity: {list(all_competitor_weaknesses)[0]}")
        
        return advantages[:5]  # Limit to 5 key advantages
    
    async def _generate_quarterly_roadmaps(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea]
    ) -> List[QuarterlyRoadmap]:
        """Generate detailed quarterly roadmaps"""
        
        quarters = []
        
        # Sort improvement areas by priority
        sorted_areas = sorted(improvement_areas, key=lambda x: (
            0 if x.priority == Priority.HIGH else 1 if x.priority == Priority.MEDIUM else 2,
            -x.target_score
        ))
        
        # Q1: Foundation and Quick Wins
        q1_actions = self._generate_q1_actions(analysis_result, sorted_areas[:3])
        q1 = QuarterlyRoadmap(
            quarter=RoadmapPhase.Q1,
            quarter_theme="Foundation & Quick Wins",
            strategic_goals=[
                "Establish competitive monitoring systems",
                "Address highest-priority performance gaps",
                "Implement foundational improvements"
            ],
            actions=q1_actions,
            quarter_budget=self._calculate_quarter_budget(q1_actions),
            success_criteria=[
                "15% improvement in top priority areas",
                "Competitive monitoring system operational",
                "Team alignment on strategic direction"
            ]
        )
        quarters.append(q1)
        
        # Q2: Competitive Positioning
        q2_actions = self._generate_q2_actions(analysis_result, sorted_areas[2:5], competitor_insights)
        q2 = QuarterlyRoadmap(
            quarter=RoadmapPhase.Q2,
            quarter_theme="Competitive Positioning",
            strategic_goals=[
                "Differentiate from key competitors",
                "Strengthen market position",
                "Launch competitive initiatives"
            ],
            actions=q2_actions,
            quarter_budget=self._calculate_quarter_budget(q2_actions),
            success_criteria=[
                "Clear differentiation established",
                "Market share growth initiated",
                "Competitor response analysis complete"
            ]
        )
        quarters.append(q2)
        
        # Q3: Market Leadership
        q3_actions = self._generate_q3_actions(analysis_result, sorted_areas[4:], competitor_insights)
        q3 = QuarterlyRoadmap(
            quarter=RoadmapPhase.Q3,
            quarter_theme="Market Leadership",
            strategic_goals=[
                "Establish thought leadership",
                "Scale successful initiatives",
                "Expand competitive advantages"
            ],
            actions=q3_actions,
            quarter_budget=self._calculate_quarter_budget(q3_actions),
            success_criteria=[
                "Industry recognition achieved",
                "Scalable processes implemented",
                "Sustained competitive advantage"
            ]
        )
        quarters.append(q3)
        
        # Q4: Optimization and Future Planning
        q4_actions = self._generate_q4_actions(analysis_result, improvement_areas)
        q4 = QuarterlyRoadmap(
            quarter=RoadmapPhase.Q4,
            quarter_theme="Optimization & Future Planning",
            strategic_goals=[
                "Optimize all initiatives",
                "Plan next year strategy",
                "Consolidate market position"
            ],
            actions=q4_actions,
            quarter_budget=self._calculate_quarter_budget(q4_actions),
            success_criteria=[
                "Target performance scores achieved",
                "Next year strategy defined",
                "Market leadership position secured"
            ]
        )
        quarters.append(q4)
        
        return quarters
    
    def _generate_q1_actions(
        self, 
        analysis_result: AnalysisResults, 
        priority_areas: List[ImprovementArea]
    ) -> List[RoadmapAction]:
        """Generate Q1 foundation actions"""
        
        actions = []
        
        # Competitive monitoring setup
        actions.append(RoadmapAction(
            action_id=f"q1_monitor_{uuid.uuid4().hex[:6]}",
            title="Establish Competitive Intelligence System",
            description="Implement automated monitoring of competitor activities, pricing, and market positioning",
            category="Strategic Intelligence",
            priority=Priority.HIGH,
            estimated_effort="4-6 weeks",
            expected_impact="Real-time competitive awareness and rapid response capability",
            success_metrics=["Daily competitor updates", "Weekly intelligence reports", "Response time < 48 hours"],
            dependencies=[],
            budget_estimate="$15,000 - $25,000"
        ))
        
        # Address top priority areas
        for i, area in enumerate(priority_areas):
            action_id = f"q1_improve_{uuid.uuid4().hex[:6]}"
            actions.append(RoadmapAction(
                action_id=action_id,
                title=f"Improve {area.area}",
                description=f"Focus on {area.description}. Target improvement from {area.current_score:.1%} to {min(area.target_score, area.current_score + 0.15):.1%}",
                category=area.area,
                priority=area.priority,
                estimated_effort=area.timeline,
                expected_impact=f"Enhanced competitive position in {area.area}",
                success_metrics=[f"{metric} improvement" for metric in area.expected_outcomes[:3]],
                dependencies=[],
                budget_estimate=self._estimate_action_budget(area.resources_needed)
            ))
        
        return actions
    
    def _generate_q2_actions(
        self, 
        analysis_result: AnalysisResults, 
        improvement_areas: List[ImprovementArea],
        competitor_insights: List[CompetitorInsight]
    ) -> List[RoadmapAction]:
        """Generate Q2 competitive positioning actions"""
        
        actions = []
        
        # Competitive differentiation
        if competitor_insights:
            top_competitor = max(competitor_insights, key=lambda x: x.comparison_score)
            actions.append(RoadmapAction(
                action_id=f"q2_diff_{uuid.uuid4().hex[:6]}",
                title=f"Differentiate from {top_competitor.competitor_name}",
                description=f"Develop unique positioning to counter {top_competitor.competitor_name}'s strengths in {', '.join(top_competitor.strengths[:2])}",
                category="Market Positioning",
                priority=Priority.HIGH,
                estimated_effort="6-8 weeks",
                expected_impact="Clear market differentiation and reduced competitive pressure",
                success_metrics=["Unique value proposition defined", "Market perception shifted", "Customer preference improved"],
                dependencies=[],
                budget_estimate="$30,000 - $50,000"
            ))
        
        # Continue improvement areas
        for area in improvement_areas:
            if area.priority in [Priority.HIGH, Priority.MEDIUM]:
                actions.append(RoadmapAction(
                    action_id=f"q2_enhance_{uuid.uuid4().hex[:6]}",
                    title=f"Enhance {area.area} Capabilities",
                    description=area.description,
                    category=area.area,
                    priority=area.priority,
                    estimated_effort=area.timeline,
                    expected_impact=f"Competitive advantage in {area.area}",
                    success_metrics=area.expected_outcomes,
                    dependencies=[],
                    budget_estimate=self._estimate_action_budget(area.resources_needed)
                ))
        
        return actions[:5]  # Limit to 5 actions per quarter
    
    def _generate_q3_actions(
        self, 
        analysis_result: AnalysisResults, 
        improvement_areas: List[ImprovementArea],
        competitor_insights: List[CompetitorInsight]
    ) -> List[RoadmapAction]:
        """Generate Q3 market leadership actions"""
        
        actions = []
        
        # Thought leadership
        actions.append(RoadmapAction(
            action_id=f"q3_leader_{uuid.uuid4().hex[:6]}",
            title="Establish Industry Thought Leadership",
            description="Launch content marketing, speaking engagements, and industry partnerships to establish market leadership",
            category="Brand Leadership",
            priority=Priority.HIGH,
            estimated_effort="8-10 weeks",
            expected_impact="Industry recognition and enhanced brand authority",
            success_metrics=["Industry awards/recognition", "Speaking opportunities", "Media mentions"],
            dependencies=[],
            budget_estimate="$40,000 - $60,000"
        ))
        
        # Scale successful initiatives
        for area in improvement_areas:
            if area.priority == Priority.MEDIUM:
                actions.append(RoadmapAction(
                    action_id=f"q3_scale_{uuid.uuid4().hex[:6]}",
                    title=f"Scale {area.area} Success",
                    description=f"Expand and scale successful improvements in {area.area}",
                    category=area.area,
                    priority=Priority.MEDIUM,
                    estimated_effort="6-8 weeks",
                    expected_impact=f"Market leadership in {area.area}",
                    success_metrics=[f"Scaled {metric}" for metric in area.expected_outcomes[:2]],
                    dependencies=[],
                    budget_estimate=self._estimate_action_budget(area.resources_needed, scale_factor=1.5)
                ))
        
        return actions[:4]
    
    def _generate_q4_actions(
        self, 
        analysis_result: AnalysisResults, 
        improvement_areas: List[ImprovementArea]
    ) -> List[RoadmapAction]:
        """Generate Q4 optimization actions"""
        
        actions = []
        
        # Performance optimization
        actions.append(RoadmapAction(
            action_id=f"q4_optimize_{uuid.uuid4().hex[:6]}",
            title="Optimize All Performance Areas",
            description="Fine-tune and optimize all initiatives to achieve target performance scores",
            category="Performance Optimization",
            priority=Priority.HIGH,
            estimated_effort="6-8 weeks",
            expected_impact="Achievement of all target performance metrics",
            success_metrics=["Target scores achieved", "Process efficiency improved", "ROI maximized"],
            dependencies=[],
            budget_estimate="$20,000 - $35,000"
        ))
        
        # Strategic planning for next year
        actions.append(RoadmapAction(
            action_id=f"q4_strategy_{uuid.uuid4().hex[:6]}",
            title="Develop Next Year Strategic Plan",
            description="Comprehensive strategic planning for the following year based on competitive learnings",
            category="Strategic Planning",
            priority=Priority.MEDIUM,
            estimated_effort="4-6 weeks",
            expected_impact="Clear strategic direction for continued growth",
            success_metrics=["Strategic plan completed", "Budget allocated", "Team aligned"],
            dependencies=[],
            budget_estimate="$10,000 - $20,000"
        ))
        
        return actions
    
    def _calculate_quarter_budget(self, actions: List[RoadmapAction]) -> str:
        """Calculate total budget for a quarter"""
        total_min = 0
        total_max = 0
        
        for action in actions:
            if action.budget_estimate:
                # Parse budget estimates like "$15,000 - $25,000"
                budget_str = action.budget_estimate.replace('$', '').replace(',', '')
                if ' - ' in budget_str:
                    min_val, max_val = budget_str.split(' - ')
                    total_min += int(min_val)
                    total_max += int(max_val)
                else:
                    # Single value
                    val = int(budget_str)
                    total_min += val
                    total_max += val
        
        if total_min == total_max:
            return f"${total_min:,}"
        else:
            return f"${total_min:,} - ${total_max:,}"
    
    def _calculate_total_budget(self, quarterly_roadmaps: List[QuarterlyRoadmap]) -> str:
        """Calculate total 12-month budget"""
        total_min = 0
        total_max = 0
        
        for quarter in quarterly_roadmaps:
            if quarter.quarter_budget:
                budget_str = quarter.quarter_budget.replace('$', '').replace(',', '')
                if ' - ' in budget_str:
                    min_val, max_val = budget_str.split(' - ')
                    total_min += int(min_val)
                    total_max += int(max_val)
                else:
                    val = int(budget_str)
                    total_min += val
                    total_max += val
        
        if total_min == total_max:
            return f"${total_min:,}"
        else:
            return f"${total_min:,} - ${total_max:,}"
    
    def _estimate_action_budget(self, resources_needed: List[str], scale_factor: float = 1.0) -> str:
        """Estimate budget based on required resources"""
        base_cost = len(resources_needed) * 5000  # $5k per resource type
        scaled_cost = int(base_cost * scale_factor)
        
        # Add variation
        min_cost = int(scaled_cost * 0.8)
        max_cost = int(scaled_cost * 1.2)
        
        return f"${min_cost:,} - ${max_cost:,}"
    
    def _identify_risk_factors(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea]
    ) -> List[str]:
        """Identify key risk factors"""
        
        risks = []
        
        # Competitive risks
        if competitor_insights:
            strong_competitors = [c for c in competitor_insights if c.comparison_score > 0.8]
            if strong_competitors:
                risks.append(f"Strong competitor response: {strong_competitors[0].competitor_name} may counter initiatives")
        
        # Performance risks
        high_priority_count = len([a for a in improvement_areas if a.priority == Priority.HIGH])
        if high_priority_count > 3:
            risks.append("Resource constraints: Multiple high-priority areas may strain execution capacity")
        
        # Market risks
        if analysis_result.overall_comparison.gap < -0.2:
            risks.append("Market position: Significant performance gap may require aggressive investment")
        
        # Execution risks
        risks.append("Change management: Organization alignment critical for successful transformation")
        risks.append("Budget constraints: Economic conditions may impact available investment")
        
        return risks[:5]  # Limit to top 5 risks
    
    def _calculate_confidence_score(
        self,
        analysis_result: AnalysisResults,
        competitor_insights: List[CompetitorInsight],
        improvement_areas: List[ImprovementArea]
    ) -> float:
        """Calculate confidence score for the roadmap"""
        
        base_confidence = analysis_result.confidence_score
        
        # Adjust based on data quality
        if len(competitor_insights) >= 3:
            base_confidence += 0.05  # More competitor data = higher confidence
        
        if len(improvement_areas) >= 5:
            base_confidence += 0.03  # More improvement areas = better understanding
        
        # Adjust based on performance gap
        gap = abs(analysis_result.overall_comparison.gap)
        if gap > 0.3:
            base_confidence -= 0.05  # Large gaps = more uncertainty
        
        return min(0.95, max(0.7, base_confidence))  # Keep within reasonable bounds
