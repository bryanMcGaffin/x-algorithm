"""
Performance Analyzer Agent

Analyzes content performance to learn what works:
- Engagement patterns
- Content effectiveness
- Timing optimization
- Audience insights
- Growth metrics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import math


@dataclass
class ContentPerformance:
    """Performance data for a single piece of content."""
    content_id: str
    content_type: str
    format_type: str
    topics: List[str]
    posted_at: datetime
    text_preview: str

    # Raw metrics
    impressions: int = 0
    likes: int = 0
    replies: int = 0
    retweets: int = 0
    quotes: int = 0
    bookmarks: int = 0
    profile_clicks: int = 0
    link_clicks: int = 0
    follows: int = 0
    video_views: int = 0
    video_watch_time: float = 0  # seconds

    # Calculated metrics
    engagement_rate: float = 0
    viral_coefficient: float = 0
    conversion_rate: float = 0
    quality_score: float = 0

    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.impressions > 0:
            # Engagement rate (weighted)
            total_engagement = (
                self.likes * 1 +
                self.replies * 2 +
                self.retweets * 2 +
                self.quotes * 3 +
                self.bookmarks * 1.5 +
                self.profile_clicks * 0.5
            )
            self.engagement_rate = total_engagement / self.impressions

            # Viral coefficient (amplification)
            self.viral_coefficient = (self.retweets + self.quotes) / max(1, self.likes)

            # Conversion rate (follows per impression)
            self.conversion_rate = self.follows / self.impressions

            # Quality score (composite)
            self.quality_score = (
                self.engagement_rate * 40 +
                self.viral_coefficient * 30 +
                self.conversion_rate * 1000 * 30
            ) / 100


@dataclass
class PerformanceInsight:
    """Actionable insight from performance analysis."""
    category: str
    finding: str
    confidence: float
    action: str
    impact_estimate: str


@dataclass
class PerformanceReport:
    """Complete performance analysis report."""
    period_start: datetime
    period_end: datetime
    total_posts: int

    # Aggregate metrics
    total_impressions: int
    total_engagements: int
    total_followers_gained: int
    avg_engagement_rate: float
    avg_viral_coefficient: float

    # Breakdowns
    by_content_type: Dict[str, Dict[str, float]]
    by_format: Dict[str, Dict[str, float]]
    by_topic: Dict[str, Dict[str, float]]
    by_day_of_week: Dict[str, Dict[str, float]]
    by_hour: Dict[int, Dict[str, float]]

    # Top performers
    top_posts: List[ContentPerformance]
    worst_posts: List[ContentPerformance]

    # Insights
    insights: List[PerformanceInsight]

    # Trends
    engagement_trend: str  # "improving", "stable", "declining"
    growth_rate: float  # followers per day

    def to_dict(self) -> dict:
        return {
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat(),
            },
            "summary": {
                "total_posts": self.total_posts,
                "total_impressions": self.total_impressions,
                "total_engagements": self.total_engagements,
                "followers_gained": self.total_followers_gained,
                "avg_engagement_rate": f"{self.avg_engagement_rate:.2%}",
                "avg_viral_coefficient": f"{self.avg_viral_coefficient:.2f}",
            },
            "by_content_type": self.by_content_type,
            "by_format": self.by_format,
            "by_topic": self.by_topic,
            "insights": [{"finding": i.finding, "action": i.action} for i in self.insights],
            "engagement_trend": self.engagement_trend,
            "growth_rate": f"{self.growth_rate:.1f} followers/day",
        }


class PerformanceAnalyzerAgent:
    """
    Analyzes content performance to optimize strategy.

    Features:
    - Track all content metrics
    - Identify patterns in high-performing content
    - Learn optimal timing
    - Calculate content effectiveness scores
    - Generate actionable insights
    """

    def __init__(self):
        self.content_history: List[ContentPerformance] = []
        self.reports: List[PerformanceReport] = []

        # Learning accumulators
        self.type_performance: Dict[str, List[float]] = defaultdict(list)
        self.format_performance: Dict[str, List[float]] = defaultdict(list)
        self.topic_performance: Dict[str, List[float]] = defaultdict(list)
        self.timing_performance: Dict[str, List[float]] = defaultdict(list)

    def record_performance(self, content: ContentPerformance):
        """Record performance of a content piece."""
        content.calculate_metrics()
        self.content_history.append(content)

        # Update learning accumulators
        self.type_performance[content.content_type].append(content.engagement_rate)
        self.format_performance[content.format_type].append(content.engagement_rate)

        for topic in content.topics:
            self.topic_performance[topic].append(content.engagement_rate)

        day = content.posted_at.strftime("%A")
        hour = content.posted_at.hour
        self.timing_performance[f"day_{day}"].append(content.engagement_rate)
        self.timing_performance[f"hour_{hour}"].append(content.engagement_rate)

    def analyze(
        self,
        period_days: int = 30,
        min_posts: int = 10
    ) -> Optional[PerformanceReport]:
        """
        Analyze performance over a period.

        Args:
            period_days: Days to analyze
            min_posts: Minimum posts required for analysis

        Returns:
            PerformanceReport or None if insufficient data
        """
        period_end = datetime.now()
        period_start = period_end - timedelta(days=period_days)

        # Filter content in period
        period_content = [
            c for c in self.content_history
            if period_start <= c.posted_at <= period_end
        ]

        if len(period_content) < min_posts:
            return None

        # Calculate aggregates
        total_impressions = sum(c.impressions for c in period_content)
        total_engagements = sum(
            c.likes + c.replies + c.retweets + c.quotes + c.bookmarks
            for c in period_content
        )
        total_follows = sum(c.follows for c in period_content)

        engagement_rates = [c.engagement_rate for c in period_content if c.engagement_rate > 0]
        viral_coefficients = [c.viral_coefficient for c in period_content if c.viral_coefficient > 0]

        avg_engagement = statistics.mean(engagement_rates) if engagement_rates else 0
        avg_viral = statistics.mean(viral_coefficients) if viral_coefficients else 0

        # Breakdown by dimensions
        by_content_type = self._breakdown_by_dimension(period_content, "content_type")
        by_format = self._breakdown_by_dimension(period_content, "format_type")
        by_topic = self._breakdown_by_topics(period_content)
        by_day = self._breakdown_by_day(period_content)
        by_hour = self._breakdown_by_hour(period_content)

        # Identify top and worst performers
        sorted_content = sorted(period_content, key=lambda c: c.quality_score, reverse=True)
        top_posts = sorted_content[:5]
        worst_posts = sorted_content[-5:] if len(sorted_content) >= 10 else []

        # Generate insights
        insights = self._generate_insights(
            period_content, by_content_type, by_format, by_topic, by_day, by_hour
        )

        # Calculate trends
        engagement_trend = self._calculate_trend(period_content)
        growth_rate = total_follows / period_days if period_days > 0 else 0

        report = PerformanceReport(
            period_start=period_start,
            period_end=period_end,
            total_posts=len(period_content),
            total_impressions=total_impressions,
            total_engagements=total_engagements,
            total_followers_gained=total_follows,
            avg_engagement_rate=avg_engagement,
            avg_viral_coefficient=avg_viral,
            by_content_type=by_content_type,
            by_format=by_format,
            by_topic=by_topic,
            by_day_of_week=by_day,
            by_hour=by_hour,
            top_posts=top_posts,
            worst_posts=worst_posts,
            insights=insights,
            engagement_trend=engagement_trend,
            growth_rate=growth_rate,
        )

        self.reports.append(report)
        return report

    def _breakdown_by_dimension(
        self,
        content: List[ContentPerformance],
        dimension: str
    ) -> Dict[str, Dict[str, float]]:
        """Break down performance by a dimension."""
        grouped = defaultdict(list)

        for c in content:
            key = getattr(c, dimension, "unknown")
            grouped[key].append(c)

        result = {}
        for key, items in grouped.items():
            engagement_rates = [c.engagement_rate for c in items]
            result[key] = {
                "count": len(items),
                "avg_engagement_rate": statistics.mean(engagement_rates) if engagement_rates else 0,
                "avg_impressions": statistics.mean([c.impressions for c in items]),
                "total_follows": sum(c.follows for c in items),
            }

        return result

    def _breakdown_by_topics(
        self,
        content: List[ContentPerformance]
    ) -> Dict[str, Dict[str, float]]:
        """Break down performance by topic."""
        topic_content = defaultdict(list)

        for c in content:
            for topic in c.topics:
                topic_content[topic].append(c)

        result = {}
        for topic, items in topic_content.items():
            engagement_rates = [c.engagement_rate for c in items]
            result[topic] = {
                "count": len(items),
                "avg_engagement_rate": statistics.mean(engagement_rates) if engagement_rates else 0,
                "avg_viral_coefficient": statistics.mean([c.viral_coefficient for c in items]),
            }

        return result

    def _breakdown_by_day(
        self,
        content: List[ContentPerformance]
    ) -> Dict[str, Dict[str, float]]:
        """Break down performance by day of week."""
        day_content = defaultdict(list)

        for c in content:
            day = c.posted_at.strftime("%A")
            day_content[day].append(c)

        result = {}
        for day, items in day_content.items():
            engagement_rates = [c.engagement_rate for c in items]
            result[day] = {
                "count": len(items),
                "avg_engagement_rate": statistics.mean(engagement_rates) if engagement_rates else 0,
            }

        return result

    def _breakdown_by_hour(
        self,
        content: List[ContentPerformance]
    ) -> Dict[int, Dict[str, float]]:
        """Break down performance by hour."""
        hour_content = defaultdict(list)

        for c in content:
            hour = c.posted_at.hour
            hour_content[hour].append(c)

        result = {}
        for hour, items in hour_content.items():
            engagement_rates = [c.engagement_rate for c in items]
            result[hour] = {
                "count": len(items),
                "avg_engagement_rate": statistics.mean(engagement_rates) if engagement_rates else 0,
            }

        return result

    def _generate_insights(
        self,
        content: List[ContentPerformance],
        by_type: Dict,
        by_format: Dict,
        by_topic: Dict,
        by_day: Dict,
        by_hour: Dict
    ) -> List[PerformanceInsight]:
        """Generate actionable insights from analysis."""
        insights = []

        # Best content type
        if by_type:
            best_type = max(by_type.items(), key=lambda x: x[1].get("avg_engagement_rate", 0))
            if best_type[1]["count"] >= 3:
                insights.append(PerformanceInsight(
                    category="content_type",
                    finding=f"{best_type[0]} content has highest engagement ({best_type[1]['avg_engagement_rate']:.2%})",
                    confidence=min(0.9, 0.5 + best_type[1]["count"] * 0.05),
                    action=f"Increase {best_type[0]} content production",
                    impact_estimate="10-20% engagement improvement",
                ))

        # Best format
        if by_format:
            best_format = max(by_format.items(), key=lambda x: x[1].get("avg_engagement_rate", 0))
            if best_format[1]["count"] >= 3:
                insights.append(PerformanceInsight(
                    category="format",
                    finding=f"{best_format[0]} format performs best ({best_format[1]['avg_engagement_rate']:.2%})",
                    confidence=min(0.9, 0.5 + best_format[1]["count"] * 0.05),
                    action=f"Use {best_format[0]} format more often",
                    impact_estimate="5-15% engagement improvement",
                ))

        # Best topic
        if by_topic:
            best_topic = max(by_topic.items(), key=lambda x: x[1].get("avg_engagement_rate", 0))
            if best_topic[1]["count"] >= 2:
                insights.append(PerformanceInsight(
                    category="topic",
                    finding=f"'{best_topic[0]}' topic resonates most ({best_topic[1]['avg_engagement_rate']:.2%})",
                    confidence=min(0.85, 0.4 + best_topic[1]["count"] * 0.1),
                    action=f"Create more content about '{best_topic[0]}'",
                    impact_estimate="15-25% engagement improvement",
                ))

        # Best timing
        if by_day:
            best_day = max(by_day.items(), key=lambda x: x[1].get("avg_engagement_rate", 0))
            insights.append(PerformanceInsight(
                category="timing",
                finding=f"{best_day[0]} has highest engagement",
                confidence=0.7,
                action=f"Prioritize important content for {best_day[0]}",
                impact_estimate="5-10% engagement improvement",
            ))

        if by_hour:
            best_hours = sorted(by_hour.items(), key=lambda x: x[1].get("avg_engagement_rate", 0), reverse=True)[:3]
            best_hour_str = ", ".join(f"{h[0]}:00" for h in best_hours)
            insights.append(PerformanceInsight(
                category="timing",
                finding=f"Best posting hours: {best_hour_str}",
                confidence=0.65,
                action="Schedule content around these hours",
                impact_estimate="5-15% reach improvement",
            ))

        # Content diversity insight
        type_count = len(by_type)
        if type_count < 3:
            insights.append(PerformanceInsight(
                category="diversity",
                finding="Limited content type diversity",
                confidence=0.8,
                action="Experiment with more content types (threads, videos)",
                impact_estimate="Broader audience reach",
            ))

        return insights

    def _calculate_trend(self, content: List[ContentPerformance]) -> str:
        """Calculate engagement trend over time."""
        if len(content) < 10:
            return "stable"

        # Sort by date
        sorted_content = sorted(content, key=lambda c: c.posted_at)

        # Compare first half vs second half
        mid = len(sorted_content) // 2
        first_half = sorted_content[:mid]
        second_half = sorted_content[mid:]

        first_avg = statistics.mean([c.engagement_rate for c in first_half])
        second_avg = statistics.mean([c.engagement_rate for c in second_half])

        if second_avg > first_avg * 1.1:
            return "improving"
        elif second_avg < first_avg * 0.9:
            return "declining"
        else:
            return "stable"

    def get_best_performing(self, dimension: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get best performing values for a dimension."""
        if dimension == "content_type":
            data = self.type_performance
        elif dimension == "format":
            data = self.format_performance
        elif dimension == "topic":
            data = self.topic_performance
        else:
            data = self.timing_performance

        averages = {
            k: statistics.mean(v) if v else 0
            for k, v in data.items()
        }

        sorted_items = sorted(averages.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_n]

    def get_optimal_posting_times(self) -> Dict[str, Any]:
        """Get optimal posting times based on performance."""
        day_perf = {}
        hour_perf = {}

        for key, values in self.timing_performance.items():
            if key.startswith("day_"):
                day = key.replace("day_", "")
                day_perf[day] = statistics.mean(values) if values else 0
            elif key.startswith("hour_"):
                hour = int(key.replace("hour_", ""))
                hour_perf[hour] = statistics.mean(values) if values else 0

        best_days = sorted(day_perf.items(), key=lambda x: x[1], reverse=True)[:3]
        best_hours = sorted(hour_perf.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "best_days": [d[0] for d in best_days],
            "best_hours": [h[0] for h in best_hours],
            "avoid_days": [d[0] for d in sorted(day_perf.items(), key=lambda x: x[1])[:2]],
            "avoid_hours": [h[0] for h in sorted(hour_perf.items(), key=lambda x: x[1])[:3]],
        }

    def export_learnings(self) -> Dict[str, Any]:
        """Export learned performance patterns."""
        return {
            "best_content_types": self.get_best_performing("content_type"),
            "best_formats": self.get_best_performing("format"),
            "best_topics": self.get_best_performing("topic"),
            "optimal_timing": self.get_optimal_posting_times(),
            "total_content_analyzed": len(self.content_history),
        }
