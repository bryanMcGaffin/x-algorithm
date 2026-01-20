"""
Trend Analyzer Agent

Analyzes trends to inform content strategy:
- Trending topics in niche
- Viral content patterns
- Seasonal relevance
- Competitor activity
- Hashtag performance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import random
import math


class TrendStrength(Enum):
    """Trend strength levels."""
    EMERGING = "emerging"      # Just starting
    GROWING = "growing"        # Building momentum
    PEAK = "peak"             # Maximum interest
    DECLINING = "declining"    # Past peak
    EVERGREEN = "evergreen"   # Always relevant


@dataclass
class Trend:
    """Individual trend data."""
    name: str
    category: str
    strength: TrendStrength
    relevance_score: float      # 0-1, how relevant to niche
    velocity: float             # Rate of change
    volume: int                 # Search/mention volume
    sentiment: float            # -1 to 1
    related_topics: List[str]
    peak_time_estimate: Optional[datetime] = None
    recommended_action: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "strength": self.strength.value,
            "relevance_score": self.relevance_score,
            "velocity": self.velocity,
            "volume": self.volume,
            "sentiment": self.sentiment,
            "related_topics": self.related_topics,
            "peak_time_estimate": self.peak_time_estimate.isoformat() if self.peak_time_estimate else None,
            "recommended_action": self.recommended_action,
        }


@dataclass
class TrendReport:
    """Complete trend analysis report."""
    generated_at: datetime
    niche: str

    # Trend categories
    hot_trends: List[Trend]           # Act now
    emerging_trends: List[Trend]      # Prepare content
    evergreen_topics: List[Trend]     # Always works
    declining_trends: List[Trend]     # Avoid

    # Insights
    top_hashtags: List[Dict[str, Any]]
    competitor_trends: List[Dict[str, Any]]
    content_gaps: List[str]
    timing_recommendations: Dict[str, Any]

    # Overall scores
    trend_opportunity_score: float
    content_freshness_needed: float

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at.isoformat(),
            "niche": self.niche,
            "hot_trends": [t.to_dict() for t in self.hot_trends],
            "emerging_trends": [t.to_dict() for t in self.emerging_trends],
            "evergreen_topics": [t.to_dict() for t in self.evergreen_topics],
            "declining_trends": [t.to_dict() for t in self.declining_trends],
            "top_hashtags": self.top_hashtags,
            "competitor_trends": self.competitor_trends,
            "content_gaps": self.content_gaps,
            "timing_recommendations": self.timing_recommendations,
            "trend_opportunity_score": self.trend_opportunity_score,
            "content_freshness_needed": self.content_freshness_needed,
        }


@dataclass
class ViralPattern:
    """Pattern identified in viral content."""
    pattern_type: str
    description: str
    frequency: float           # How often it appears in viral content
    engagement_multiplier: float
    examples: List[str]
    best_for_content_types: List[str]


class TrendAnalyzerAgent:
    """
    Analyzes trends and patterns to optimize content timing and topics.

    Features:
    - Real-time trend detection
    - Niche relevance filtering
    - Viral pattern identification
    - Competitor monitoring
    - Content gap analysis
    """

    def __init__(self, niche_topics: List[str], competitors: List[str] = None):
        self.niche_topics = niche_topics
        self.competitors = competitors or []
        self.trend_history: List[TrendReport] = []
        self.viral_patterns: List[ViralPattern] = []

        # Initialize viral patterns
        self._initialize_viral_patterns()

    def _initialize_viral_patterns(self):
        """Initialize known viral content patterns."""
        self.viral_patterns = [
            ViralPattern(
                pattern_type="contrarian",
                description="Takes opposite stance from conventional wisdom",
                frequency=0.25,
                engagement_multiplier=2.5,
                examples=["Unpopular opinion:", "Everyone gets this wrong:"],
                best_for_content_types=["text_post", "thread"],
            ),
            ViralPattern(
                pattern_type="story_arc",
                description="Personal story with transformation",
                frequency=0.20,
                engagement_multiplier=2.2,
                examples=["X years ago I...", "This changed everything:"],
                best_for_content_types=["thread", "video_long"],
            ),
            ViralPattern(
                pattern_type="data_reveal",
                description="Surprising data or statistics",
                frequency=0.15,
                engagement_multiplier=2.0,
                examples=["I analyzed 1000...", "The data shows:"],
                best_for_content_types=["thread", "image_post"],
            ),
            ViralPattern(
                pattern_type="simplification",
                description="Complex topic made simple",
                frequency=0.18,
                engagement_multiplier=1.8,
                examples=["Explained simply:", "In 60 seconds:"],
                best_for_content_types=["video_short", "thread", "infographic"],
            ),
            ViralPattern(
                pattern_type="list_format",
                description="Numbered list of insights",
                frequency=0.22,
                engagement_multiplier=1.6,
                examples=["7 things about...", "Top 5 mistakes:"],
                best_for_content_types=["thread", "carousel"],
            ),
            ViralPattern(
                pattern_type="behind_scenes",
                description="Authentic, unfiltered look",
                frequency=0.12,
                engagement_multiplier=1.9,
                examples=["What nobody shows:", "The reality of:"],
                best_for_content_types=["video_long", "image_post"],
            ),
            ViralPattern(
                pattern_type="prediction",
                description="Future-focused speculation",
                frequency=0.10,
                engagement_multiplier=1.7,
                examples=["In 5 years:", "What's coming next:"],
                best_for_content_types=["text_post", "thread"],
            ),
            ViralPattern(
                pattern_type="comparison",
                description="X vs Y comparison",
                frequency=0.14,
                engagement_multiplier=1.8,
                examples=["X vs Y:", "The difference between:"],
                best_for_content_types=["image_post", "video_short"],
            ),
        ]

    def analyze_trends(self, external_data: Dict[str, Any] = None) -> TrendReport:
        """
        Perform comprehensive trend analysis.

        Args:
            external_data: Optional external trend data (from APIs, scraping, etc.)

        Returns:
            TrendReport with all trend insights
        """
        # Simulate trend analysis (in production, would use real data)
        trends = self._identify_trends(external_data)

        # Categorize trends
        hot_trends = [t for t in trends if t.strength == TrendStrength.PEAK]
        emerging_trends = [t for t in trends if t.strength in [TrendStrength.EMERGING, TrendStrength.GROWING]]
        evergreen_topics = [t for t in trends if t.strength == TrendStrength.EVERGREEN]
        declining_trends = [t for t in trends if t.strength == TrendStrength.DECLINING]

        # Analyze hashtags
        top_hashtags = self._analyze_hashtags()

        # Monitor competitors
        competitor_trends = self._analyze_competitors()

        # Find content gaps
        content_gaps = self._identify_content_gaps(trends)

        # Generate timing recommendations
        timing = self._generate_timing_recommendations()

        # Calculate scores
        opportunity_score = self._calculate_opportunity_score(trends)
        freshness_needed = self._calculate_freshness_need(trends)

        report = TrendReport(
            generated_at=datetime.now(),
            niche=", ".join(self.niche_topics[:3]),
            hot_trends=hot_trends,
            emerging_trends=emerging_trends,
            evergreen_topics=evergreen_topics,
            declining_trends=declining_trends,
            top_hashtags=top_hashtags,
            competitor_trends=competitor_trends,
            content_gaps=content_gaps,
            timing_recommendations=timing,
            trend_opportunity_score=opportunity_score,
            content_freshness_needed=freshness_needed,
        )

        self.trend_history.append(report)
        return report

    def _identify_trends(self, external_data: Dict[str, Any] = None) -> List[Trend]:
        """Identify trends relevant to niche."""
        trends = []

        # Simulated trend generation (would use real data in production)
        for topic in self.niche_topics:
            # Create evergreen trend
            trends.append(Trend(
                name=f"{topic} fundamentals",
                category=topic,
                strength=TrendStrength.EVERGREEN,
                relevance_score=0.95,
                velocity=0.0,
                volume=5000,
                sentiment=0.6,
                related_topics=[f"{topic} basics", f"{topic} guide"],
                recommended_action="Always include in content mix",
            ))

            # Simulate trending variation
            if random.random() > 0.5:
                strength = random.choice([TrendStrength.EMERGING, TrendStrength.GROWING, TrendStrength.PEAK])
                trends.append(Trend(
                    name=f"{topic} 2024 update",
                    category=topic,
                    strength=strength,
                    relevance_score=0.85,
                    velocity=random.uniform(0.5, 2.0),
                    volume=random.randint(1000, 10000),
                    sentiment=random.uniform(0.3, 0.8),
                    related_topics=[f"new {topic}", f"{topic} changes"],
                    peak_time_estimate=datetime.now() + timedelta(days=random.randint(1, 14)),
                    recommended_action="Create content now" if strength == TrendStrength.PEAK else "Prepare content",
                ))

        # Add cross-niche trends
        cross_trends = [
            ("AI tools", TrendStrength.PEAK, 0.7),
            ("Productivity", TrendStrength.EVERGREEN, 0.6),
            ("Remote work", TrendStrength.GROWING, 0.5),
        ]

        for name, strength, relevance in cross_trends:
            if any(topic.lower() in name.lower() for topic in self.niche_topics) or random.random() > 0.5:
                trends.append(Trend(
                    name=name,
                    category="cross-niche",
                    strength=strength,
                    relevance_score=relevance,
                    velocity=random.uniform(0.3, 1.5),
                    volume=random.randint(5000, 50000),
                    sentiment=random.uniform(0.4, 0.7),
                    related_topics=[],
                    recommended_action=self._get_action_for_strength(strength),
                ))

        return trends

    def _get_action_for_strength(self, strength: TrendStrength) -> str:
        """Get recommended action for trend strength."""
        actions = {
            TrendStrength.EMERGING: "Monitor and prepare content",
            TrendStrength.GROWING: "Create content soon",
            TrendStrength.PEAK: "Post immediately",
            TrendStrength.DECLINING: "Avoid unless unique angle",
            TrendStrength.EVERGREEN: "Include in regular rotation",
        }
        return actions.get(strength, "Evaluate further")

    def _analyze_hashtags(self) -> List[Dict[str, Any]]:
        """Analyze hashtag performance and trends."""
        hashtags = []

        for topic in self.niche_topics:
            tag = topic.lower().replace(" ", "")
            hashtags.append({
                "hashtag": f"#{tag}",
                "volume": random.randint(1000, 100000),
                "growth_rate": random.uniform(-0.1, 0.3),
                "competition": random.choice(["low", "medium", "high"]),
                "recommendation": "Use regularly" if random.random() > 0.3 else "Use occasionally",
            })

        # Sort by volume
        hashtags.sort(key=lambda x: x["volume"], reverse=True)
        return hashtags[:10]

    def _analyze_competitors(self) -> List[Dict[str, Any]]:
        """Analyze competitor content and trends."""
        competitor_data = []

        for competitor in self.competitors[:5]:
            competitor_data.append({
                "handle": competitor,
                "recent_themes": random.sample(self.niche_topics, min(2, len(self.niche_topics))),
                "top_performing_format": random.choice(["thread", "video", "image_post"]),
                "posting_frequency": random.choice(["high", "medium", "low"]),
                "engagement_trend": random.choice(["increasing", "stable", "decreasing"]),
                "content_gap": f"Not covering {random.choice(self.niche_topics)} deeply",
            })

        return competitor_data

    def _identify_content_gaps(self, trends: List[Trend]) -> List[str]:
        """Identify gaps in content coverage."""
        gaps = []

        # Check for underserved topics
        for trend in trends:
            if trend.relevance_score > 0.7 and trend.strength in [TrendStrength.EMERGING, TrendStrength.GROWING]:
                gaps.append(f"Early content opportunity: {trend.name}")

        # Generic gaps
        gaps.extend([
            "Beginner-friendly content for new followers",
            "Case studies and real examples",
            "Comparison content between popular tools/methods",
            "Behind-the-scenes and process content",
        ])

        return gaps[:5]

    def _generate_timing_recommendations(self) -> Dict[str, Any]:
        """Generate content timing recommendations."""
        return {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_hours_utc": [9, 12, 15, 18, 21],
            "avoid": ["Saturday late night", "Sunday morning"],
            "thread_timing": "Tuesday-Thursday, 9-11 AM UTC",
            "video_timing": "Wednesday-Friday, 6-8 PM UTC",
            "engagement_windows": [
                {"start": 8, "end": 10, "activity": "Reply to overnight engagement"},
                {"start": 12, "end": 14, "activity": "Lunch break posting"},
                {"start": 17, "end": 20, "activity": "Evening prime time"},
            ],
        }

    def _calculate_opportunity_score(self, trends: List[Trend]) -> float:
        """Calculate overall trend opportunity score."""
        if not trends:
            return 0.5

        # Weight by relevance and strength
        total_score = 0
        for trend in trends:
            strength_weight = {
                TrendStrength.PEAK: 1.0,
                TrendStrength.GROWING: 0.8,
                TrendStrength.EMERGING: 0.6,
                TrendStrength.EVERGREEN: 0.5,
                TrendStrength.DECLINING: 0.2,
            }.get(trend.strength, 0.5)

            total_score += trend.relevance_score * strength_weight

        return min(1.0, total_score / len(trends))

    def _calculate_freshness_need(self, trends: List[Trend]) -> float:
        """Calculate how much fresh content is needed."""
        # More hot/emerging trends = more need for fresh content
        hot_count = sum(1 for t in trends if t.strength in [TrendStrength.PEAK, TrendStrength.GROWING])
        return min(1.0, hot_count / max(1, len(trends)) * 2)

    def get_viral_patterns(self) -> List[ViralPattern]:
        """Get known viral content patterns."""
        return self.viral_patterns

    def get_recommended_patterns(self, content_type: str) -> List[ViralPattern]:
        """Get viral patterns recommended for a content type."""
        return [
            p for p in self.viral_patterns
            if content_type in p.best_for_content_types
        ]

    def get_content_calendar_suggestions(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate content calendar suggestions based on trends."""
        suggestions = []

        latest_report = self.trend_history[-1] if self.trend_history else self.analyze_trends()

        for day in range(days):
            date = datetime.now() + timedelta(days=day)
            day_name = date.strftime("%A")

            # Select trend-aligned topics
            if latest_report.hot_trends:
                hot_topic = random.choice(latest_report.hot_trends).name
            else:
                hot_topic = random.choice(self.niche_topics)

            if latest_report.evergreen_topics:
                evergreen_topic = random.choice(latest_report.evergreen_topics).name
            else:
                evergreen_topic = random.choice(self.niche_topics)

            suggestions.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day_name,
                "trending_content": {
                    "topic": hot_topic,
                    "format": "thread" if day_name in ["Tuesday", "Wednesday"] else "text_post",
                    "timing": "morning",
                },
                "evergreen_content": {
                    "topic": evergreen_topic,
                    "format": "video_short" if day_name in ["Thursday", "Friday"] else "text_post",
                    "timing": "afternoon",
                },
                "engagement_focus": latest_report.timing_recommendations.get("engagement_windows", []),
            })

        return suggestions
