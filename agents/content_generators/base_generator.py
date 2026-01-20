"""
Base Content Generator

Foundation class for all content generation agents with:
- Trend integration
- Niche optimization
- Performance learning
- Algorithm alignment
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import hashlib
import random


@dataclass
class NicheProfile:
    """Profile defining a content niche."""
    name: str
    description: str
    primary_topics: List[str]
    secondary_topics: List[str]
    tone: str  # professional, casual, humorous, educational, provocative
    target_audience: List[str]
    competitor_accounts: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # Learned preferences
    best_performing_topics: Dict[str, float] = field(default_factory=dict)
    best_performing_formats: Dict[str, float] = field(default_factory=dict)
    best_posting_times: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "primary_topics": self.primary_topics,
            "secondary_topics": self.secondary_topics,
            "tone": self.tone,
            "target_audience": self.target_audience,
            "competitor_accounts": self.competitor_accounts,
            "hashtags": self.hashtags,
            "keywords": self.keywords,
            "best_performing_topics": self.best_performing_topics,
            "best_performing_formats": self.best_performing_formats,
            "best_posting_times": self.best_posting_times,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NicheProfile":
        return cls(**data)


@dataclass
class TrendData:
    """Current trend information."""
    trending_topics: List[str]
    trending_hashtags: List[str]
    viral_formats: List[str]  # e.g., "hot take", "thread breakdown", "meme"
    current_events: List[str]
    seasonal_relevance: List[str]
    competitor_activity: List[Dict[str, Any]]

    # Trend scores (0-1)
    topic_scores: Dict[str, float] = field(default_factory=dict)
    hashtag_scores: Dict[str, float] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.now)

    def is_stale(self, max_age_hours: int = 4) -> bool:
        """Check if trend data needs refresh."""
        age = datetime.now() - self.timestamp
        return age > timedelta(hours=max_age_hours)


@dataclass
class PerformanceHistory:
    """Historical performance data for learning."""
    content_id: str
    content_type: str
    content_text: str
    topics: List[str]
    format_type: str
    posted_at: datetime

    # Performance metrics
    impressions: int = 0
    likes: int = 0
    replies: int = 0
    retweets: int = 0
    quotes: int = 0
    bookmarks: int = 0
    profile_clicks: int = 0
    follows: int = 0
    dwell_time_seconds: float = 0

    # Calculated metrics
    engagement_rate: float = 0
    viral_coefficient: float = 0
    follower_conversion_rate: float = 0

    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.impressions > 0:
            total_engagements = (self.likes + self.replies * 2 +
                               self.retweets * 2 + self.quotes * 3 +
                               self.bookmarks + self.profile_clicks * 0.5)
            self.engagement_rate = total_engagements / self.impressions
            self.follower_conversion_rate = self.follows / self.impressions
            self.viral_coefficient = (self.retweets + self.quotes) / max(1, self.likes)


@dataclass
class ContentPiece:
    """Generated content piece."""
    content_type: str
    main_text: str
    hook: Optional[str] = None
    cta: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    media_suggestions: List[str] = field(default_factory=list)
    thread_continuation: List[str] = field(default_factory=list)
    optimal_posting_time: Optional[int] = None  # Hour 0-23

    # Generation metadata
    topics_used: List[str] = field(default_factory=list)
    trends_incorporated: List[str] = field(default_factory=list)
    format_type: str = "standard"
    confidence_score: float = 0.5

    # Algorithm alignment
    predicted_engagement_rate: float = 0.03
    predicted_dwell_time: float = 5.0
    algorithm_alignment_score: float = 0.5

    def get_full_text(self) -> str:
        """Get complete post text."""
        parts = []
        if self.hook:
            parts.append(self.hook)
        parts.append(self.main_text)
        if self.cta:
            parts.append(self.cta)
        if self.hashtags:
            parts.append(" ".join(f"#{h}" for h in self.hashtags[:3]))
        return "\n\n".join(parts)

    def get_character_count(self) -> int:
        """Get total character count."""
        return len(self.get_full_text())

    def to_dict(self) -> dict:
        return {
            "content_type": self.content_type,
            "main_text": self.main_text,
            "hook": self.hook,
            "cta": self.cta,
            "hashtags": self.hashtags,
            "media_suggestions": self.media_suggestions,
            "thread_continuation": self.thread_continuation,
            "optimal_posting_time": self.optimal_posting_time,
            "topics_used": self.topics_used,
            "trends_incorporated": self.trends_incorporated,
            "format_type": self.format_type,
            "confidence_score": self.confidence_score,
            "predicted_engagement_rate": self.predicted_engagement_rate,
            "predicted_dwell_time": self.predicted_dwell_time,
            "algorithm_alignment_score": self.algorithm_alignment_score,
            "full_text": self.get_full_text(),
            "character_count": self.get_character_count(),
        }


class BaseContentGenerator(ABC):
    """
    Base class for all content generation agents.

    Features:
    - Trend-aware generation
    - Niche optimization
    - Performance-based learning
    - Algorithm alignment
    """

    def __init__(self, niche: NicheProfile):
        self.niche = niche
        self.performance_history: List[PerformanceHistory] = []
        self.trend_data: Optional[TrendData] = None

        # Learning weights (updated based on performance)
        self.topic_weights: Dict[str, float] = {t: 1.0 for t in niche.primary_topics}
        self.format_weights: Dict[str, float] = {}
        self.hook_weights: Dict[str, float] = {}

        # Generation parameters
        self.creativity_factor: float = 0.3  # 0 = safe, 1 = experimental
        self.trend_weight: float = 0.4  # How much to weight trending content
        self.performance_weight: float = 0.5  # How much to weight past performance

    @abstractmethod
    def generate(self, count: int = 1, **kwargs) -> List[ContentPiece]:
        """Generate content pieces."""
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """Return the content type this generator produces."""
        pass

    def update_trends(self, trend_data: TrendData):
        """Update with fresh trend data."""
        self.trend_data = trend_data
        self._recalculate_weights()

    def record_performance(self, performance: PerformanceHistory):
        """Record and learn from content performance."""
        performance.calculate_metrics()
        self.performance_history.append(performance)
        self._learn_from_performance(performance)

    def _learn_from_performance(self, performance: PerformanceHistory):
        """Update weights based on performance."""
        # Calculate performance score
        score = (performance.engagement_rate * 100 +
                performance.viral_coefficient * 50 +
                performance.follower_conversion_rate * 1000)

        # Update topic weights
        for topic in performance.topics:
            if topic in self.topic_weights:
                # Exponential moving average
                alpha = 0.2
                self.topic_weights[topic] = (
                    alpha * score + (1 - alpha) * self.topic_weights[topic]
                )

        # Update format weights
        format_type = performance.format_type
        if format_type not in self.format_weights:
            self.format_weights[format_type] = 1.0
        alpha = 0.2
        self.format_weights[format_type] = (
            alpha * score + (1 - alpha) * self.format_weights[format_type]
        )

    def _recalculate_weights(self):
        """Recalculate generation weights based on trends and history."""
        if not self.trend_data:
            return

        # Boost weights for trending topics
        for topic in self.niche.primary_topics:
            trend_score = self.trend_data.topic_scores.get(topic, 0)
            if topic in self.topic_weights:
                self.topic_weights[topic] *= (1 + trend_score * self.trend_weight)

        # Normalize weights
        if self.topic_weights:
            max_weight = max(self.topic_weights.values())
            if max_weight > 0:
                self.topic_weights = {
                    k: v / max_weight for k, v in self.topic_weights.items()
                }

    def _select_topics(self, count: int = 2) -> List[str]:
        """Select topics weighted by performance and trends."""
        if not self.topic_weights:
            return random.sample(self.niche.primary_topics,
                               min(count, len(self.niche.primary_topics)))

        # Weighted random selection
        topics = list(self.topic_weights.keys())
        weights = list(self.topic_weights.values())

        # Add some randomness based on creativity factor
        weights = [w + random.random() * self.creativity_factor for w in weights]

        # Normalize
        total = sum(weights)
        weights = [w / total for w in weights]

        selected = []
        for _ in range(min(count, len(topics))):
            r = random.random()
            cumulative = 0
            for topic, weight in zip(topics, weights):
                cumulative += weight
                if r <= cumulative and topic not in selected:
                    selected.append(topic)
                    break

        return selected if selected else topics[:count]

    def _select_format(self) -> str:
        """Select content format based on performance."""
        formats = ["standard", "hot_take", "question", "story", "list",
                  "comparison", "prediction", "behind_scenes"]

        if not self.format_weights:
            return random.choice(formats)

        # Weighted selection with creativity
        weights = [self.format_weights.get(f, 1.0) for f in formats]
        weights = [w + random.random() * self.creativity_factor for w in weights]

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for format_type, weight in zip(formats, weights):
            cumulative += weight
            if r <= cumulative:
                return format_type

        return "standard"

    def _incorporate_trends(self, content: str) -> str:
        """Incorporate trending elements into content."""
        if not self.trend_data or random.random() > self.trend_weight:
            return content

        # Add trending hashtag if relevant
        relevant_hashtags = [
            h for h in self.trend_data.trending_hashtags
            if any(topic.lower() in h.lower() for topic in self.niche.primary_topics)
        ]

        if relevant_hashtags:
            content += f" #{random.choice(relevant_hashtags)}"

        return content

    def _calculate_algorithm_score(self, content: ContentPiece) -> float:
        """Calculate how well content aligns with algorithm preferences."""
        score = 0.5  # Base score

        # Length optimization
        char_count = content.get_character_count()
        if 100 <= char_count <= 200:
            score += 0.1  # Optimal length
        elif char_count > 250:
            score -= 0.05  # Too long

        # Hook presence
        if content.hook:
            score += 0.1

        # CTA presence
        if content.cta:
            score += 0.05

        # Media suggestions
        if content.media_suggestions:
            score += 0.1

        # Trend incorporation
        if content.trends_incorporated:
            score += 0.05 * len(content.trends_incorporated)

        return min(1.0, max(0.0, score))

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of historical performance."""
        if not self.performance_history:
            return {"total_posts": 0, "avg_engagement_rate": 0}

        total = len(self.performance_history)
        avg_engagement = sum(p.engagement_rate for p in self.performance_history) / total
        avg_viral = sum(p.viral_coefficient for p in self.performance_history) / total
        avg_conversion = sum(p.follower_conversion_rate for p in self.performance_history) / total

        # Best performing content
        best = max(self.performance_history, key=lambda p: p.engagement_rate)

        return {
            "total_posts": total,
            "avg_engagement_rate": avg_engagement,
            "avg_viral_coefficient": avg_viral,
            "avg_follower_conversion": avg_conversion,
            "best_performing_topics": dict(sorted(
                self.topic_weights.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "best_performing_format": max(self.format_weights.items(),
                                         key=lambda x: x[1])[0] if self.format_weights else "standard",
            "best_post": {
                "text": best.content_text[:100],
                "engagement_rate": best.engagement_rate,
            }
        }

    def export_state(self) -> dict:
        """Export generator state for persistence."""
        return {
            "niche": self.niche.to_dict(),
            "topic_weights": self.topic_weights,
            "format_weights": self.format_weights,
            "hook_weights": self.hook_weights,
            "creativity_factor": self.creativity_factor,
            "trend_weight": self.trend_weight,
            "performance_weight": self.performance_weight,
        }

    def import_state(self, state: dict):
        """Import generator state from persistence."""
        if "topic_weights" in state:
            self.topic_weights = state["topic_weights"]
        if "format_weights" in state:
            self.format_weights = state["format_weights"]
        if "hook_weights" in state:
            self.hook_weights = state["hook_weights"]
        if "creativity_factor" in state:
            self.creativity_factor = state["creativity_factor"]
        if "trend_weight" in state:
            self.trend_weight = state["trend_weight"]
        if "performance_weight" in state:
            self.performance_weight = state["performance_weight"]
