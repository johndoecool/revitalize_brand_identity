import pytest
from unittest.mock import MagicMock
from app.services.report_service import ReportService
from app.models.analysis import (
    AnalysisResults, OverallComparison, ComparisonScore, 
    ActionableInsight, Strength, MarketPositioning, Priority
)
from datetime import datetime

@pytest.fixture
def report_service():
    return ReportService()

@pytest.fixture
def sample_analysis_results():
    return AnalysisResults(
        analysis_id="test_123",
        area_id="self_service_portal",
        brand_name="Test Brand",
        competitor_name="Test Competitor",
        overall_comparison=OverallComparison(
            brand_score=0.76,
            competitor_score=0.84,
            gap=-0.08,
            brand_ranking="second"
        ),
        detailed_comparison={
            "user_experience": ComparisonScore(
                brand_score=0.82,
                competitor_score=0.89,
                difference=-0.07,
                insight="Competitor has superior UX design"
            ),
            "feature_completeness": ComparisonScore(
                brand_score=0.75,
                competitor_score=0.82,
                difference=-0.07,
                insight="Brand lacks advanced features"
            )
        },
        actionable_insights=[
            ActionableInsight(
                priority=Priority.HIGH,
                category="feature_development",
                title="Implement Advanced Features",
                description="Develop advanced mobile banking features",
                estimated_effort="3-4 months",
                expected_impact="Increase score by 0.15",
                implementation_steps=["Research", "Design", "Develop", "Test"]
            )
        ],
        strengths_to_maintain=[
            Strength(
                area="security",
                description="Strong security measures",
                recommendation="Continue investing in security"
            )
        ],
        market_positioning=MarketPositioning(
            brand_position="Traditional banking",
            competitor_position="Digital banking",
            differentiation_opportunity="Focus on personalized service"
        ),
        confidence_score=0.87
    )

@pytest.mark.asyncio
async def test_generate_analysis_report(report_service, sample_analysis_results):
    """Test comprehensive analysis report generation"""
    report = await report_service.generate_analysis_report(sample_analysis_results)
    
    assert "report_id" in report
    assert "generated_at" in report
    assert "executive_summary" in report
    assert "detailed_analysis" in report
    assert "actionable_insights" in report
    assert "market_positioning" in report
    assert "confidence_metrics" in report
    
    # Check executive summary
    exec_summary = report["executive_summary"]
    assert "Test Brand" in exec_summary["overview"]
    assert "Test Competitor" in exec_summary["overview"]

@pytest.mark.asyncio
async def test_generate_comparison_report(report_service, sample_analysis_results):
    """Test comparison report generation"""
    report = await report_service.generate_comparison_report(sample_analysis_results)
    
    assert "comparison_summary" in report
    assert "category_breakdown" in report
    assert "recommendations" in report
    
    # Check comparison summary
    summary = report["comparison_summary"]
    assert summary["brand"] == "Test Brand"
    assert summary["competitor"] == "Test Competitor"
    assert "overall_winner" in summary

def test_generate_executive_summary(report_service, sample_analysis_results):
    """Test executive summary generation"""
    summary = report_service._generate_executive_summary(sample_analysis_results)
    
    assert "overview" in summary
    assert "key_finding" in summary
    assert "primary_recommendation" in summary
    assert "confidence_level" in summary
    assert "Test Brand" in summary["overview"]

def test_generate_detailed_comparison(report_service, sample_analysis_results):
    """Test detailed comparison generation"""
    comparison = report_service._generate_detailed_comparison(sample_analysis_results)
    
    assert "user_experience" in comparison
    assert "feature_completeness" in comparison
    
    ux_data = comparison["user_experience"]
    assert "brand_performance" in ux_data
    assert "competitor_performance" in ux_data
    assert "gap_analysis" in ux_data
    assert "strategic_insight" in ux_data

def test_generate_insights_report(report_service, sample_analysis_results):
    """Test insights report generation"""
    insights = report_service._generate_insights_report(sample_analysis_results)
    
    assert "insights_summary" in insights
    assert "prioritized_insights" in insights
    
    # Check summary
    summary = insights["insights_summary"]
    assert "total_recommendations" in summary
    assert "high_priority_count" in summary
    
    # Check prioritized insights
    prioritized = insights["prioritized_insights"]
    assert "high_priority" in prioritized
    assert "medium_priority" in prioritized
    assert "low_priority" in prioritized

def test_generate_positioning_report(report_service, sample_analysis_results):
    """Test market positioning report generation"""
    positioning = report_service._generate_positioning_report(sample_analysis_results)
    
    assert "current_positioning" in positioning
    assert "strategic_recommendations" in positioning
    assert "brand_strengths" in positioning
    
    # Check current positioning
    current = positioning["current_positioning"]
    assert current["brand_position"] == "Traditional banking"
    assert current["competitor_position"] == "Digital banking"

def test_determine_winner(report_service, sample_analysis_results):
    """Test winner determination logic"""
    winner = report_service._determine_winner(sample_analysis_results.overall_comparison)
    assert winner == "competitor"  # Since competitor score (0.84) > brand score (0.76)

def test_extract_key_differentiators(report_service, sample_analysis_results):
    """Test key differentiators extraction"""
    differentiators = report_service._extract_key_differentiators(sample_analysis_results)
    
    assert isinstance(differentiators, list)
    assert len(differentiators) <= 3  # Should return top 3
    
    if differentiators:
        diff = differentiators[0]
        assert "category" in diff
        assert "advantage" in diff
        assert "magnitude" in diff

def test_format_category_breakdown(report_service, sample_analysis_results):
    """Test category breakdown formatting"""
    breakdown = report_service._format_category_breakdown(
        sample_analysis_results.detailed_comparison
    )
    
    assert "user_experience" in breakdown
    assert "feature_completeness" in breakdown
    
    ux_data = breakdown["user_experience"]
    assert "brand_score" in ux_data
    assert "competitor_score" in ux_data
    assert "performance_gap" in ux_data
    assert "recommendation" in ux_data

def test_format_recommendations(report_service, sample_analysis_results):
    """Test recommendations formatting"""
    recommendations = report_service._format_recommendations(
        sample_analysis_results.actionable_insights
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) == 1
    
    rec = recommendations[0]
    assert rec["title"] == "Implement Advanced Features"
    assert rec["priority"] == "high"
    assert "next_steps" in rec

def test_generate_category_recommendation(report_service):
    """Test category recommendation generation"""
    # Test advantage scenario
    scores_advantage = MagicMock()
    scores_advantage.difference = 0.15
    rec = report_service._generate_category_recommendation(scores_advantage)
    assert "Maintain competitive advantage" in rec
    
    # Test disadvantage scenario
    scores_disadvantage = MagicMock()
    scores_disadvantage.difference = -0.15
    rec = report_service._generate_category_recommendation(scores_disadvantage)
    assert "Priority area for improvement" in rec
    
    # Test neutral scenario
    scores_neutral = MagicMock()
    scores_neutral.difference = 0.05
    rec = report_service._generate_category_recommendation(scores_neutral)
    assert "Monitor competitive position" in rec

def test_generate_success_metrics(report_service, sample_analysis_results):
    """Test success metrics generation"""
    insight = sample_analysis_results.actionable_insights[0]
    metrics = report_service._generate_success_metrics(insight)
    
    assert isinstance(metrics, list)
    assert len(metrics) > 0
    
    # Should return feature development metrics
    assert any("adoption" in metric.lower() for metric in metrics)

def test_calculate_data_quality(report_service, sample_analysis_results):
    """Test data quality calculation"""
    quality_score = report_service._calculate_data_quality(sample_analysis_results)
    
    assert 0 <= quality_score <= 1
    assert isinstance(quality_score, float)

def test_calculate_recommendation_strength(report_service, sample_analysis_results):
    """Test recommendation strength calculation"""
    strength_score = report_service._calculate_recommendation_strength(sample_analysis_results)
    
    assert 0 <= strength_score <= 1
    assert isinstance(strength_score, float)

def test_calculate_recommendation_strength_no_insights(report_service):
    """Test recommendation strength with no insights"""
    from app.models.analysis import AnalysisResults, OverallComparison, MarketPositioning
    
    results_no_insights = AnalysisResults(
        analysis_id="test",
        area_id="test",
        brand_name="Test",
        competitor_name="Test",
        overall_comparison=OverallComparison(
            brand_score=0.5, competitor_score=0.5, gap=0.0, brand_ranking="tie"
        ),
        detailed_comparison={},
        actionable_insights=[],  # No insights
        strengths_to_maintain=[],
        market_positioning=MarketPositioning(
            brand_position="", competitor_position="", differentiation_opportunity=""
        ),
        confidence_score=0.5
    )
    
    strength_score = report_service._calculate_recommendation_strength(results_no_insights)
    assert strength_score == 0.0

if __name__ == "__main__":
    pytest.main([__file__])
