"""
Cross-Testing Agent

Performs systematic A/B testing and cross-analysis:
- Tests content variations
- Compares strategies
- Validates hypotheses
- Generates statistically significant insights
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math
import random
import uuid


class TestStatus(Enum):
    """Test status states."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(Enum):
    """Types of tests."""
    AB_TEST = "ab_test"           # Two variations
    MULTIVARIATE = "multivariate"  # Multiple variables
    TIME_BASED = "time_based"      # Same content, different times
    FORMAT_BASED = "format_based"  # Same content, different formats
    TOPIC_BASED = "topic_based"    # Same format, different topics


@dataclass
class TestVariant:
    """A variant in a test."""
    variant_id: str
    name: str
    description: str
    content: Dict[str, Any]  # Content configuration

    # Results
    impressions: int = 0
    engagements: int = 0
    follows: int = 0
    engagement_rate: float = 0
    conversion_rate: float = 0

    def update_metrics(self):
        """Update calculated metrics."""
        if self.impressions > 0:
            self.engagement_rate = self.engagements / self.impressions
            self.conversion_rate = self.follows / self.impressions


@dataclass
class Test:
    """A cross-test configuration and results."""
    test_id: str
    name: str
    hypothesis: str
    test_type: TestType
    status: TestStatus

    variants: List[TestVariant]

    # Configuration
    min_sample_size: int
    confidence_level: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Results
    winner: Optional[str] = None
    statistical_significance: float = 0
    confidence_interval: Tuple[float, float] = (0, 0)
    insights: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "hypothesis": self.hypothesis,
            "type": self.test_type.value,
            "status": self.status.value,
            "variants": [
                {
                    "name": v.name,
                    "engagement_rate": f"{v.engagement_rate:.2%}",
                    "impressions": v.impressions,
                }
                for v in self.variants
            ],
            "winner": self.winner,
            "statistical_significance": f"{self.statistical_significance:.0%}",
            "insights": self.insights,
        }


@dataclass
class CrossTestReport:
    """Report from cross-testing analysis."""
    generated_at: datetime
    total_tests: int
    completed_tests: int

    # Key findings
    winning_strategies: List[Dict[str, Any]]
    losing_strategies: List[Dict[str, Any]]
    inconclusive_tests: List[str]

    # Aggregate insights
    best_performing: Dict[str, Any]
    recommendations: List[str]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at.isoformat(),
            "tests": {
                "total": self.total_tests,
                "completed": self.completed_tests,
            },
            "winning_strategies": self.winning_strategies,
            "losing_strategies": self.losing_strategies,
            "best_performing": self.best_performing,
            "recommendations": self.recommendations,
        }


class CrossTestingAgent:
    """
    Manages systematic testing of content strategies.

    Features:
    - A/B testing framework
    - Multi-variate testing
    - Statistical significance calculation
    - Automated insight generation
    - Test scheduling and tracking
    """

    def __init__(self):
        self.tests: Dict[str, Test] = {}
        self.completed_tests: List[Test] = []

    def create_ab_test(
        self,
        name: str,
        hypothesis: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        min_sample_size: int = 100,
        confidence_level: float = 0.95
    ) -> Test:
        """
        Create an A/B test.

        Args:
            name: Test name
            hypothesis: What we're testing
            variant_a: Control variant config
            variant_b: Treatment variant config
            min_sample_size: Minimum impressions per variant
            confidence_level: Required confidence level

        Returns:
            Test object
        """
        test_id = str(uuid.uuid4())[:8]

        test = Test(
            test_id=test_id,
            name=name,
            hypothesis=hypothesis,
            test_type=TestType.AB_TEST,
            status=TestStatus.DRAFT,
            variants=[
                TestVariant(
                    variant_id=f"{test_id}_a",
                    name="Control (A)",
                    description=variant_a.get("description", "Control variant"),
                    content=variant_a,
                ),
                TestVariant(
                    variant_id=f"{test_id}_b",
                    name="Treatment (B)",
                    description=variant_b.get("description", "Treatment variant"),
                    content=variant_b,
                ),
            ],
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
        )

        self.tests[test_id] = test
        return test

    def create_multivariate_test(
        self,
        name: str,
        hypothesis: str,
        variants: List[Dict[str, Any]],
        min_sample_size: int = 50,
        confidence_level: float = 0.90
    ) -> Test:
        """Create a multi-variate test with multiple variants."""
        test_id = str(uuid.uuid4())[:8]

        test_variants = []
        for i, var_config in enumerate(variants):
            test_variants.append(TestVariant(
                variant_id=f"{test_id}_{i}",
                name=var_config.get("name", f"Variant {i+1}"),
                description=var_config.get("description", ""),
                content=var_config,
            ))

        test = Test(
            test_id=test_id,
            name=name,
            hypothesis=hypothesis,
            test_type=TestType.MULTIVARIATE,
            status=TestStatus.DRAFT,
            variants=test_variants,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
        )

        self.tests[test_id] = test
        return test

    def start_test(self, test_id: str) -> bool:
        """Start a test."""
        if test_id not in self.tests:
            return False

        test = self.tests[test_id]
        test.status = TestStatus.ACTIVE
        test.start_time = datetime.now()
        return True

    def record_result(
        self,
        test_id: str,
        variant_id: str,
        impressions: int,
        engagements: int,
        follows: int = 0
    ):
        """Record results for a variant."""
        if test_id not in self.tests:
            return

        test = self.tests[test_id]
        for variant in test.variants:
            if variant.variant_id == variant_id:
                variant.impressions += impressions
                variant.engagements += engagements
                variant.follows += follows
                variant.update_metrics()
                break

        # Check if test should be completed
        self._check_test_completion(test)

    def _check_test_completion(self, test: Test):
        """Check if test has enough data to conclude."""
        # All variants need minimum sample size
        all_sufficient = all(
            v.impressions >= test.min_sample_size
            for v in test.variants
        )

        if all_sufficient:
            self._analyze_test(test)

    def _analyze_test(self, test: Test):
        """Analyze test results and determine winner."""
        if len(test.variants) < 2:
            return

        # Calculate statistical significance
        if test.test_type == TestType.AB_TEST:
            significance, winner, ci = self._calculate_ab_significance(test)
        else:
            significance, winner, ci = self._calculate_multivariate_significance(test)

        test.statistical_significance = significance
        test.confidence_interval = ci

        if significance >= test.confidence_level:
            test.winner = winner
            test.status = TestStatus.COMPLETED
            test.end_time = datetime.now()
            test.insights = self._generate_test_insights(test)
            self.completed_tests.append(test)

    def _calculate_ab_significance(self, test: Test) -> Tuple[float, str, Tuple[float, float]]:
        """Calculate A/B test statistical significance using z-test."""
        a = test.variants[0]
        b = test.variants[1]

        # Z-test for proportions
        p1 = a.engagement_rate
        p2 = b.engagement_rate
        n1 = a.impressions
        n2 = b.impressions

        if n1 == 0 or n2 == 0:
            return 0, "", (0, 0)

        # Pooled proportion
        p_pool = (a.engagements + b.engagements) / (n1 + n2)

        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

        if se == 0:
            return 0, "", (0, 0)

        # Z-score
        z = (p2 - p1) / se

        # Convert to confidence (two-tailed)
        from math import erf
        confidence = erf(abs(z) / math.sqrt(2))

        # Winner
        if p2 > p1:
            winner = b.name
        else:
            winner = a.name

        # Confidence interval for difference
        diff = p2 - p1
        margin = 1.96 * se  # 95% CI
        ci = (diff - margin, diff + margin)

        return confidence, winner, ci

    def _calculate_multivariate_significance(
        self, test: Test
    ) -> Tuple[float, str, Tuple[float, float]]:
        """Calculate multivariate test significance."""
        # Find best variant
        best_variant = max(test.variants, key=lambda v: v.engagement_rate)
        second_best = sorted(test.variants, key=lambda v: v.engagement_rate, reverse=True)[1]

        # Compare best to second best
        temp_test = Test(
            test_id="temp",
            name="temp",
            hypothesis="temp",
            test_type=TestType.AB_TEST,
            status=TestStatus.ACTIVE,
            variants=[second_best, best_variant],
            min_sample_size=test.min_sample_size,
            confidence_level=test.confidence_level,
        )

        return self._calculate_ab_significance(temp_test)

    def _generate_test_insights(self, test: Test) -> List[str]:
        """Generate insights from completed test."""
        insights = []

        if test.winner:
            winner_variant = next(v for v in test.variants if v.name == test.winner)
            loser_variants = [v for v in test.variants if v.name != test.winner]

            # Primary insight
            insights.append(
                f"'{test.winner}' won with {winner_variant.engagement_rate:.2%} engagement rate "
                f"(significance: {test.statistical_significance:.0%})"
            )

            # Comparison insights
            for loser in loser_variants:
                lift = ((winner_variant.engagement_rate / max(0.001, loser.engagement_rate)) - 1) * 100
                insights.append(f"Outperformed '{loser.name}' by {lift:.0f}%")

            # Hypothesis validation
            insights.append(f"Hypothesis '{test.hypothesis}' was {'validated' if lift > 0 else 'partially validated'}")

        return insights

    def get_active_tests(self) -> List[Test]:
        """Get all active tests."""
        return [t for t in self.tests.values() if t.status == TestStatus.ACTIVE]

    def get_test_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for new tests based on gaps."""
        recommendations = []

        # Check what hasn't been tested
        tested_dimensions = set()
        for test in self.completed_tests:
            tested_dimensions.add(test.test_type.value)

        # Recommend untested dimensions
        all_dimensions = [
            ("Hook types", "Test different hook styles (question vs statement vs number)"),
            ("Content length", "Test short vs long form content"),
            ("Posting times", "Test morning vs evening posting"),
            ("Visual vs text", "Test image posts vs text-only"),
            ("CTA placement", "Test CTA at beginning vs end"),
            ("Emotional triggers", "Test curiosity vs fear vs aspiration"),
        ]

        for name, description in all_dimensions:
            if name.lower() not in str(tested_dimensions).lower():
                recommendations.append({
                    "test_name": name,
                    "description": description,
                    "priority": "high" if "Hook" in name or "Visual" in name else "medium",
                })

        return recommendations[:5]

    def generate_report(self) -> CrossTestReport:
        """Generate comprehensive cross-testing report."""
        winning_strategies = []
        losing_strategies = []
        inconclusive = []

        for test in self.completed_tests:
            if test.winner:
                winner_variant = next(v for v in test.variants if v.name == test.winner)
                winning_strategies.append({
                    "test": test.name,
                    "winner": test.winner,
                    "engagement_rate": f"{winner_variant.engagement_rate:.2%}",
                    "significance": f"{test.statistical_significance:.0%}",
                    "insight": test.insights[0] if test.insights else "",
                })

                for loser in test.variants:
                    if loser.name != test.winner:
                        losing_strategies.append({
                            "test": test.name,
                            "loser": loser.name,
                            "engagement_rate": f"{loser.engagement_rate:.2%}",
                        })
            else:
                inconclusive.append(test.name)

        # Find overall best performing
        best_performing = {}
        if winning_strategies:
            best = max(winning_strategies, key=lambda x: float(x["engagement_rate"].rstrip('%')))
            best_performing = {
                "strategy": best["winner"],
                "from_test": best["test"],
                "engagement_rate": best["engagement_rate"],
            }

        # Generate recommendations
        recommendations = []
        for win in winning_strategies[:3]:
            recommendations.append(f"Continue using '{win['winner']}' strategy from '{win['test']}' test")
        for rec in self.get_test_recommendations()[:2]:
            recommendations.append(f"Test: {rec['test_name']} - {rec['description']}")

        return CrossTestReport(
            generated_at=datetime.now(),
            total_tests=len(self.tests),
            completed_tests=len(self.completed_tests),
            winning_strategies=winning_strategies,
            losing_strategies=losing_strategies,
            inconclusive_tests=inconclusive,
            best_performing=best_performing,
            recommendations=recommendations,
        )

    def suggest_next_test(self) -> Dict[str, Any]:
        """Suggest the next test to run based on gaps and priorities."""
        recommendations = self.get_test_recommendations()

        if recommendations:
            top_rec = recommendations[0]
            return {
                "name": top_rec["test_name"],
                "description": top_rec["description"],
                "suggested_variants": self._generate_suggested_variants(top_rec["test_name"]),
                "priority": top_rec["priority"],
            }

        return {
            "name": "General engagement test",
            "description": "Test basic content variations",
            "suggested_variants": [
                {"name": "Control", "description": "Current best practice"},
                {"name": "Variation", "description": "New approach to test"},
            ],
            "priority": "medium",
        }

    def _generate_suggested_variants(self, test_name: str) -> List[Dict[str, str]]:
        """Generate suggested variants for a test type."""
        suggestions = {
            "Hook types": [
                {"name": "Question hook", "description": "Start with a question"},
                {"name": "Number hook", "description": "Start with a number/statistic"},
                {"name": "Bold statement", "description": "Start with a bold claim"},
            ],
            "Content length": [
                {"name": "Short (< 150 chars)", "description": "Concise, punchy content"},
                {"name": "Medium (150-250 chars)", "description": "Standard length"},
                {"name": "Long (> 250 chars)", "description": "Detailed content"},
            ],
            "Posting times": [
                {"name": "Morning (8-10 AM)", "description": "Early morning post"},
                {"name": "Lunch (12-2 PM)", "description": "Midday post"},
                {"name": "Evening (6-8 PM)", "description": "Evening prime time"},
            ],
        }

        return suggestions.get(test_name, [
            {"name": "Control", "description": "Current approach"},
            {"name": "Variation", "description": "New approach"},
        ])
