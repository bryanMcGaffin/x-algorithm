"""
Result Analyzer Agent

The central brain that analyzes all results and optimizes the system:
- Compares real progress vs predictions
- Analyzes content performance vs algorithm expectations
- Identifies optimization opportunities
- Updates all agent parameters
- Drives exponential improvement
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json


@dataclass
class ContentResult:
    """Result data for a single piece of content."""
    content_id: str
    content_type: str
    format_type: str
    topics: List[str]
    posted_at: datetime
    content_text: str

    # Predictions (from agents)
    predicted_engagement_rate: float
    predicted_viral_score: float
    predicted_dwell_time: float
    algorithm_alignment_score: float

    # Actual results
    actual_impressions: int = 0
    actual_engagements: int = 0
    actual_engagement_rate: float = 0
    actual_follows: int = 0
    actual_viral_coefficient: float = 0

    # Analysis
    prediction_error: float = 0
    performance_vs_expected: str = ""  # "above", "below", "at"
    key_factors: List[str] = field(default_factory=list)

    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.actual_impressions > 0:
            self.actual_engagement_rate = self.actual_engagements / self.actual_impressions

        # Prediction error
        if self.predicted_engagement_rate > 0:
            self.prediction_error = abs(
                self.actual_engagement_rate - self.predicted_engagement_rate
            ) / self.predicted_engagement_rate

        # Performance classification
        if self.actual_engagement_rate > self.predicted_engagement_rate * 1.2:
            self.performance_vs_expected = "above"
        elif self.actual_engagement_rate < self.predicted_engagement_rate * 0.8:
            self.performance_vs_expected = "below"
        else:
            self.performance_vs_expected = "at"


@dataclass
class OptimizationRecommendation:
    """A specific optimization recommendation."""
    category: str
    recommendation: str
    impact_estimate: str
    confidence: float
    based_on: str  # Evidence


@dataclass
class SystemOptimization:
    """System-wide optimization updates."""
    # Weight adjustments
    content_type_weights: Dict[str, float]
    format_weights: Dict[str, float]
    topic_weights: Dict[str, float]
    timing_weights: Dict[int, float]

    # Strategy adjustments
    recommended_content_mix: Dict[str, float]
    recommended_posting_times: List[int]
    recommended_engagement_focus: List[str]

    # Generator parameters
    creativity_factor_adjustment: float
    trend_weight_adjustment: float
    performance_weight_adjustment: float


@dataclass
class ResultAnalysisReport:
    """Comprehensive result analysis report."""
    generated_at: datetime
    analysis_period_days: int
    total_content_analyzed: int

    # Performance summary
    overall_engagement_rate: float
    overall_follower_growth: int
    growth_rate_per_day: float

    # Prediction accuracy
    avg_prediction_error: float
    prediction_accuracy_trend: str

    # Content performance
    top_performing_content: List[ContentResult]
    underperforming_content: List[ContentResult]

    # Pattern analysis
    successful_patterns: List[Dict[str, Any]]
    failing_patterns: List[Dict[str, Any]]

    # Recommendations
    recommendations: List[OptimizationRecommendation]

    # System optimizations
    optimizations: SystemOptimization

    # Progress tracking
    days_to_goal: Optional[int]
    current_followers: int
    goal_followers: int
    on_track: bool

    def to_dict(self) -> dict:
        return {
            "summary": {
                "period_days": self.analysis_period_days,
                "content_analyzed": self.total_content_analyzed,
                "engagement_rate": f"{self.overall_engagement_rate:.2%}",
                "follower_growth": self.overall_follower_growth,
                "growth_per_day": f"{self.growth_rate_per_day:.1f}",
            },
            "prediction_accuracy": {
                "avg_error": f"{self.avg_prediction_error:.0%}",
                "trend": self.prediction_accuracy_trend,
            },
            "patterns": {
                "successful": self.successful_patterns[:5],
                "failing": self.failing_patterns[:3],
            },
            "recommendations": [
                {"rec": r.recommendation, "impact": r.impact_estimate}
                for r in self.recommendations[:5]
            ],
            "progress": {
                "current": self.current_followers,
                "goal": self.goal_followers,
                "days_remaining": self.days_to_goal,
                "on_track": self.on_track,
            },
        }


class ResultAnalyzerAgent:
    """
    Central brain that analyzes all results and drives system optimization.

    This is the key agent for exponential improvement:
    - Compares predictions to reality
    - Identifies what's working and what's not
    - Updates all other agents' parameters
    - Tracks progress toward goals
    - Generates optimization recommendations
    """

    def __init__(self, follower_goal: int = 10000, starting_followers: int = 0):
        self.follower_goal = follower_goal
        self.starting_followers = starting_followers
        self.current_followers = starting_followers

        self.content_results: List[ContentResult] = []
        self.analysis_history: List[ResultAnalysisReport] = []

        # Learning state
        self.learned_patterns: Dict[str, float] = {}
        self.prediction_calibration: Dict[str, float] = defaultdict(lambda: 1.0)

    def record_result(self, result: ContentResult):
        """Record a content result."""
        result.calculate_metrics()
        self.content_results.append(result)

        # Update current follower count
        self.current_followers += result.actual_follows

        # Learn from result
        self._learn_from_result(result)

    def _learn_from_result(self, result: ContentResult):
        """Learn from a single result to improve predictions."""
        # Update pattern weights
        pattern_key = f"{result.content_type}_{result.format_type}"

        if pattern_key not in self.learned_patterns:
            self.learned_patterns[pattern_key] = result.actual_engagement_rate
        else:
            # Exponential moving average
            alpha = 0.2
            self.learned_patterns[pattern_key] = (
                alpha * result.actual_engagement_rate +
                (1 - alpha) * self.learned_patterns[pattern_key]
            )

        # Update prediction calibration
        if result.predicted_engagement_rate > 0:
            actual_vs_predicted = result.actual_engagement_rate / result.predicted_engagement_rate
            self.prediction_calibration[result.content_type] = (
                0.1 * actual_vs_predicted +
                0.9 * self.prediction_calibration[result.content_type]
            )

    def analyze(self, period_days: int = 7) -> ResultAnalysisReport:
        """
        Perform comprehensive result analysis.

        Args:
            period_days: Days to analyze

        Returns:
            ResultAnalysisReport with insights and optimizations
        """
        cutoff = datetime.now() - timedelta(days=period_days)
        period_results = [r for r in self.content_results if r.posted_at >= cutoff]

        if not period_results:
            return self._empty_report(period_days)

        # Calculate performance summary
        total_engagements = sum(r.actual_engagements for r in period_results)
        total_impressions = sum(r.actual_impressions for r in period_results)
        total_follows = sum(r.actual_follows for r in period_results)

        overall_engagement_rate = total_engagements / max(1, total_impressions)
        growth_per_day = total_follows / period_days

        # Prediction accuracy
        prediction_errors = [r.prediction_error for r in period_results if r.prediction_error > 0]
        avg_error = statistics.mean(prediction_errors) if prediction_errors else 0

        # Get top and bottom performers
        sorted_results = sorted(period_results, key=lambda r: r.actual_engagement_rate, reverse=True)
        top_performing = sorted_results[:5]
        underperforming = sorted_results[-5:] if len(sorted_results) >= 10 else []

        # Analyze patterns
        successful_patterns = self._analyze_successful_patterns(top_performing)
        failing_patterns = self._analyze_failing_patterns(underperforming)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            period_results, successful_patterns, failing_patterns
        )

        # Generate system optimizations
        optimizations = self._generate_optimizations(period_results)

        # Progress tracking
        days_to_goal = self._estimate_days_to_goal(growth_per_day)
        on_track = days_to_goal is not None and days_to_goal <= 120  # 4 months

        # Prediction accuracy trend
        accuracy_trend = self._calculate_accuracy_trend()

        report = ResultAnalysisReport(
            generated_at=datetime.now(),
            analysis_period_days=period_days,
            total_content_analyzed=len(period_results),
            overall_engagement_rate=overall_engagement_rate,
            overall_follower_growth=total_follows,
            growth_rate_per_day=growth_per_day,
            avg_prediction_error=avg_error,
            prediction_accuracy_trend=accuracy_trend,
            top_performing_content=top_performing,
            underperforming_content=underperforming,
            successful_patterns=successful_patterns,
            failing_patterns=failing_patterns,
            recommendations=recommendations,
            optimizations=optimizations,
            days_to_goal=days_to_goal,
            current_followers=self.current_followers,
            goal_followers=self.follower_goal,
            on_track=on_track,
        )

        self.analysis_history.append(report)
        return report

    def _analyze_successful_patterns(
        self, top_content: List[ContentResult]
    ) -> List[Dict[str, Any]]:
        """Analyze patterns in successful content."""
        patterns = []

        # Group by content type
        type_counts = defaultdict(int)
        type_engagement = defaultdict(list)
        format_counts = defaultdict(int)
        topic_counts = defaultdict(int)

        for content in top_content:
            type_counts[content.content_type] += 1
            type_engagement[content.content_type].append(content.actual_engagement_rate)
            format_counts[content.format_type] += 1
            for topic in content.topics:
                topic_counts[topic] += 1

        # Content type patterns
        for ctype, count in type_counts.items():
            if count >= 2:
                avg_eng = statistics.mean(type_engagement[ctype])
                patterns.append({
                    "pattern": f"Content type: {ctype}",
                    "frequency": count,
                    "avg_engagement": f"{avg_eng:.2%}",
                    "insight": f"{ctype} consistently performs well",
                })

        # Format patterns
        for format_type, count in format_counts.items():
            if count >= 2:
                patterns.append({
                    "pattern": f"Format: {format_type}",
                    "frequency": count,
                    "insight": f"{format_type} format drives engagement",
                })

        # Topic patterns
        for topic, count in topic_counts.items():
            if count >= 2:
                patterns.append({
                    "pattern": f"Topic: {topic}",
                    "frequency": count,
                    "insight": f"'{topic}' resonates with audience",
                })

        return patterns

    def _analyze_failing_patterns(
        self, bottom_content: List[ContentResult]
    ) -> List[Dict[str, Any]]:
        """Analyze patterns in underperforming content."""
        patterns = []

        type_counts = defaultdict(int)
        format_counts = defaultdict(int)

        for content in bottom_content:
            type_counts[content.content_type] += 1
            format_counts[content.format_type] += 1

        for ctype, count in type_counts.items():
            if count >= 2:
                patterns.append({
                    "pattern": f"Content type: {ctype}",
                    "frequency": count,
                    "insight": f"{ctype} underperforming - reduce or improve",
                })

        for format_type, count in format_counts.items():
            if count >= 2:
                patterns.append({
                    "pattern": f"Format: {format_type}",
                    "frequency": count,
                    "insight": f"{format_type} format not resonating",
                })

        return patterns

    def _generate_recommendations(
        self,
        results: List[ContentResult],
        successful: List[Dict],
        failing: List[Dict]
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations."""
        recommendations = []

        # From successful patterns
        for pattern in successful[:3]:
            recommendations.append(OptimizationRecommendation(
                category="content_strategy",
                recommendation=f"Increase {pattern['pattern']} content",
                impact_estimate="10-20% engagement improvement",
                confidence=0.7,
                based_on=f"Top performer analysis: {pattern['frequency']} of top posts",
            ))

        # From failing patterns
        for pattern in failing[:2]:
            recommendations.append(OptimizationRecommendation(
                category="content_strategy",
                recommendation=f"Reduce or improve {pattern['pattern']} content",
                impact_estimate="Avoid 5-10% engagement loss",
                confidence=0.6,
                based_on=f"Underperformer analysis: {pattern['frequency']} of bottom posts",
            ))

        # Timing recommendations
        hour_performance = defaultdict(list)
        for r in results:
            hour_performance[r.posted_at.hour].append(r.actual_engagement_rate)

        if hour_performance:
            best_hour = max(hour_performance.items(), key=lambda x: statistics.mean(x[1]))
            recommendations.append(OptimizationRecommendation(
                category="timing",
                recommendation=f"Prioritize posting at {best_hour[0]}:00",
                impact_estimate="5-10% reach improvement",
                confidence=0.6,
                based_on=f"Best performing hour: {statistics.mean(best_hour[1]):.2%} avg engagement",
            ))

        # Prediction calibration
        if self.prediction_calibration:
            worst_calibration = min(
                self.prediction_calibration.items(),
                key=lambda x: abs(1 - x[1])
            )
            if abs(1 - worst_calibration[1]) > 0.3:
                recommendations.append(OptimizationRecommendation(
                    category="prediction",
                    recommendation=f"Recalibrate {worst_calibration[0]} predictions",
                    impact_estimate="Better content selection",
                    confidence=0.8,
                    based_on=f"Prediction off by {abs(1 - worst_calibration[1]):.0%}",
                ))

        return recommendations

    def _generate_optimizations(
        self, results: List[ContentResult]
    ) -> SystemOptimization:
        """Generate system-wide optimizations."""
        # Calculate optimal weights
        content_type_performance = defaultdict(list)
        format_performance = defaultdict(list)
        topic_performance = defaultdict(list)
        timing_performance = defaultdict(list)

        for r in results:
            content_type_performance[r.content_type].append(r.actual_engagement_rate)
            format_performance[r.format_type].append(r.actual_engagement_rate)
            for topic in r.topics:
                topic_performance[topic].append(r.actual_engagement_rate)
            timing_performance[r.posted_at.hour].append(r.actual_engagement_rate)

        # Normalize to weights
        def to_weights(perf_dict: Dict[str, List[float]]) -> Dict[str, float]:
            if not perf_dict:
                return {}
            avgs = {k: statistics.mean(v) for k, v in perf_dict.items()}
            max_avg = max(avgs.values()) if avgs else 1
            return {k: v / max_avg for k, v in avgs.items()}

        content_weights = to_weights(content_type_performance)
        format_weights = to_weights(format_performance)
        topic_weights = to_weights(topic_performance)
        timing_weights = {k: statistics.mean(v) for k, v in timing_performance.items()}

        # Recommended content mix
        total_weight = sum(content_weights.values()) or 1
        content_mix = {k: v / total_weight for k, v in content_weights.items()}

        # Best posting times
        sorted_times = sorted(timing_weights.items(), key=lambda x: x[1], reverse=True)
        best_times = [t[0] for t in sorted_times[:5]]

        # Engagement focus (top topics)
        sorted_topics = sorted(topic_weights.items(), key=lambda x: x[1], reverse=True)
        engagement_focus = [t[0] for t in sorted_topics[:5]]

        # Parameter adjustments based on prediction accuracy
        avg_error = statistics.mean([r.prediction_error for r in results if r.prediction_error > 0]) if results else 0

        return SystemOptimization(
            content_type_weights=content_weights,
            format_weights=format_weights,
            topic_weights=topic_weights,
            timing_weights=timing_weights,
            recommended_content_mix=content_mix,
            recommended_posting_times=best_times,
            recommended_engagement_focus=engagement_focus,
            creativity_factor_adjustment=-0.1 if avg_error > 0.5 else 0.1,  # More conservative if predictions are off
            trend_weight_adjustment=0.05,  # Slightly increase trend focus
            performance_weight_adjustment=0.1 if len(results) > 50 else 0,  # Increase performance weight with data
        )

    def _estimate_days_to_goal(self, growth_rate: float) -> Optional[int]:
        """Estimate days to reach follower goal."""
        remaining = self.follower_goal - self.current_followers
        if remaining <= 0:
            return 0
        if growth_rate <= 0:
            return None
        return int(remaining / growth_rate)

    def _calculate_accuracy_trend(self) -> str:
        """Calculate if prediction accuracy is improving."""
        if len(self.analysis_history) < 2:
            return "insufficient_data"

        recent_errors = [r.avg_prediction_error for r in self.analysis_history[-5:]]
        if len(recent_errors) < 2:
            return "insufficient_data"

        if recent_errors[-1] < recent_errors[0] * 0.9:
            return "improving"
        elif recent_errors[-1] > recent_errors[0] * 1.1:
            return "declining"
        else:
            return "stable"

    def _empty_report(self, period_days: int) -> ResultAnalysisReport:
        """Generate empty report when no data."""
        return ResultAnalysisReport(
            generated_at=datetime.now(),
            analysis_period_days=period_days,
            total_content_analyzed=0,
            overall_engagement_rate=0,
            overall_follower_growth=0,
            growth_rate_per_day=0,
            avg_prediction_error=0,
            prediction_accuracy_trend="no_data",
            top_performing_content=[],
            underperforming_content=[],
            successful_patterns=[],
            failing_patterns=[],
            recommendations=[],
            optimizations=SystemOptimization(
                content_type_weights={},
                format_weights={},
                topic_weights={},
                timing_weights={},
                recommended_content_mix={},
                recommended_posting_times=[9, 12, 15, 18, 21],
                recommended_engagement_focus=[],
                creativity_factor_adjustment=0,
                trend_weight_adjustment=0,
                performance_weight_adjustment=0,
            ),
            days_to_goal=None,
            current_followers=self.current_followers,
            goal_followers=self.follower_goal,
            on_track=False,
        )

    def get_calibration_factors(self) -> Dict[str, float]:
        """Get prediction calibration factors for other agents."""
        return dict(self.prediction_calibration)

    def get_learned_patterns(self) -> Dict[str, float]:
        """Get learned pattern weights for other agents."""
        return self.learned_patterns.copy()

    def export_state(self) -> Dict[str, Any]:
        """Export agent state for persistence."""
        return {
            "follower_goal": self.follower_goal,
            "current_followers": self.current_followers,
            "learned_patterns": self.learned_patterns,
            "prediction_calibration": dict(self.prediction_calibration),
            "results_count": len(self.content_results),
        }

    def import_state(self, state: Dict[str, Any]):
        """Import agent state from persistence."""
        self.follower_goal = state.get("follower_goal", 10000)
        self.current_followers = state.get("current_followers", 0)
        self.learned_patterns = state.get("learned_patterns", {})
        for k, v in state.get("prediction_calibration", {}).items():
            self.prediction_calibration[k] = v
