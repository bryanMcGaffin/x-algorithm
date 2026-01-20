"""
Optimal Values Model for X Algorithm Growth

This module defines the optimal values for every type of content and interaction
that affects the X algorithm, based on analysis of the recommendation system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json


class ContentType(Enum):
    """All content types that affect the algorithm."""
    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_SHORT = "video_short"       # < 45 seconds
    VIDEO_LONG = "video_long"         # > 45 seconds (VQV eligible)
    THREAD = "thread"
    QUOTE_TWEET = "quote_tweet"
    REPLY = "reply"
    POLL = "poll"
    SPACE = "space"
    ARTICLE = "article"               # Long-form notes


class EngagementType(Enum):
    """All engagement types that affect the algorithm."""
    LIKE = "like"
    REPLY = "reply"
    RETWEET = "retweet"
    QUOTE = "quote"
    BOOKMARK = "bookmark"
    SHARE = "share"
    PROFILE_CLICK = "profile_click"
    FOLLOW = "follow"
    DWELL_TIME = "dwell_time"
    VIDEO_WATCH = "video_watch"
    LINK_CLICK = "link_click"


@dataclass
class ContentOptimalValues:
    """Optimal values for a specific content type."""
    content_type: ContentType

    # Volume optimal
    min_per_day: int
    optimal_per_day: int
    max_per_day: int           # Before diminishing returns hurt

    # Timing optimal
    min_hours_between: float
    optimal_hours_between: float
    best_posting_hours: List[int]  # 0-23 UTC

    # Algorithm weight factors
    base_score_weight: float   # Relative weight in algorithm
    engagement_multiplier: float
    dwell_time_weight: float

    # Quality thresholds
    min_length: Optional[int] = None
    optimal_length: Optional[int] = None
    max_length: Optional[int] = None

    # Special bonuses
    has_vqv_bonus: bool = False
    has_thread_bonus: bool = False
    media_bonus: float = 1.0

    # Negative signals
    spam_threshold: int = 20   # Posts per day before spam detection
    fatigue_threshold: int = 10  # Before follower fatigue

    # Conversion metrics
    avg_impressions_per_post: int = 500
    avg_engagement_rate: float = 0.03
    avg_follower_conversion: float = 0.001


@dataclass
class EngagementOptimalValues:
    """Optimal values for engagement activities."""
    engagement_type: EngagementType

    # Volume optimal (what you GIVE, which triggers reciprocity)
    min_per_day: int
    optimal_per_day: int
    max_per_day: int

    # Algorithm signal strength (what you RECEIVE)
    signal_weight: float       # From weighted_scorer.rs
    decay_half_life_hours: float

    # Reciprocity factors
    reciprocity_rate: float    # Likelihood of return engagement
    relationship_weight: float  # How much it strengthens follow graph

    # Quality guidelines
    min_dwell_before: int = 0  # Seconds to dwell before engaging
    thoughtful_threshold: int = 0  # Character count for thoughtful replies


# ============================================================================
# OPTIMAL VALUES DATABASE
# ============================================================================

CONTENT_OPTIMAL_VALUES: Dict[ContentType, ContentOptimalValues] = {

    ContentType.TEXT_POST: ContentOptimalValues(
        content_type=ContentType.TEXT_POST,
        min_per_day=2,
        optimal_per_day=4,
        max_per_day=8,
        min_hours_between=2,
        optimal_hours_between=4,
        best_posting_hours=[9, 12, 15, 18, 21],  # UTC
        base_score_weight=1.0,
        engagement_multiplier=1.0,
        dwell_time_weight=1.0,
        min_length=50,
        optimal_length=200,
        max_length=280,
        media_bonus=1.0,
        spam_threshold=15,
        fatigue_threshold=10,
        avg_impressions_per_post=500,
        avg_engagement_rate=0.03,
        avg_follower_conversion=0.001,
    ),

    ContentType.IMAGE_POST: ContentOptimalValues(
        content_type=ContentType.IMAGE_POST,
        min_per_day=1,
        optimal_per_day=3,
        max_per_day=6,
        min_hours_between=3,
        optimal_hours_between=5,
        best_posting_hours=[10, 14, 19],
        base_score_weight=1.2,  # Images get slight boost
        engagement_multiplier=1.3,
        dwell_time_weight=1.5,  # Images increase dwell
        min_length=20,
        optimal_length=100,
        max_length=280,
        media_bonus=1.2,
        spam_threshold=12,
        fatigue_threshold=8,
        avg_impressions_per_post=800,
        avg_engagement_rate=0.04,
        avg_follower_conversion=0.0015,
    ),

    ContentType.VIDEO_SHORT: ContentOptimalValues(
        content_type=ContentType.VIDEO_SHORT,
        min_per_day=0,
        optimal_per_day=2,
        max_per_day=4,
        min_hours_between=4,
        optimal_hours_between=6,
        best_posting_hours=[12, 18, 21],
        base_score_weight=1.3,
        engagement_multiplier=1.4,
        dwell_time_weight=2.0,
        min_length=10,  # seconds
        optimal_length=30,
        max_length=44,  # Just under VQV threshold
        has_vqv_bonus=False,
        media_bonus=1.5,
        spam_threshold=8,
        fatigue_threshold=6,
        avg_impressions_per_post=1200,
        avg_engagement_rate=0.05,
        avg_follower_conversion=0.002,
    ),

    ContentType.VIDEO_LONG: ContentOptimalValues(
        content_type=ContentType.VIDEO_LONG,
        min_per_day=0,
        optimal_per_day=1,
        max_per_day=2,
        min_hours_between=6,
        optimal_hours_between=12,
        best_posting_hours=[12, 19],
        base_score_weight=1.5,
        engagement_multiplier=1.6,
        dwell_time_weight=3.0,  # High dwell time signal
        min_length=45,  # seconds - VQV threshold
        optimal_length=90,
        max_length=180,
        has_vqv_bonus=True,  # Video Quality Views bonus
        media_bonus=2.0,
        spam_threshold=4,
        fatigue_threshold=3,
        avg_impressions_per_post=2000,
        avg_engagement_rate=0.06,
        avg_follower_conversion=0.003,
    ),

    ContentType.THREAD: ContentOptimalValues(
        content_type=ContentType.THREAD,
        min_per_day=0,
        optimal_per_day=1,
        max_per_day=2,
        min_hours_between=8,
        optimal_hours_between=24,
        best_posting_hours=[9, 14],  # Morning and afternoon
        base_score_weight=1.4,
        engagement_multiplier=1.5,
        dwell_time_weight=3.0,  # Threads = high dwell
        min_length=3,  # tweets in thread
        optimal_length=7,
        max_length=15,
        has_thread_bonus=True,
        media_bonus=1.3,
        spam_threshold=3,
        fatigue_threshold=2,
        avg_impressions_per_post=3000,
        avg_engagement_rate=0.05,
        avg_follower_conversion=0.004,
    ),

    ContentType.QUOTE_TWEET: ContentOptimalValues(
        content_type=ContentType.QUOTE_TWEET,
        min_per_day=0,
        optimal_per_day=2,
        max_per_day=5,
        min_hours_between=2,
        optimal_hours_between=4,
        best_posting_hours=[10, 13, 16, 20],
        base_score_weight=1.2,
        engagement_multiplier=1.3,
        dwell_time_weight=1.2,
        min_length=30,
        optimal_length=150,
        max_length=280,
        media_bonus=1.0,
        spam_threshold=10,
        fatigue_threshold=7,
        avg_impressions_per_post=600,
        avg_engagement_rate=0.035,
        avg_follower_conversion=0.0012,
    ),

    ContentType.REPLY: ContentOptimalValues(
        content_type=ContentType.REPLY,
        min_per_day=5,
        optimal_per_day=20,
        max_per_day=50,
        min_hours_between=0,
        optimal_hours_between=0.25,
        best_posting_hours=list(range(8, 23)),  # All waking hours
        base_score_weight=0.8,  # Lower for own reach
        engagement_multiplier=2.0,  # But high for relationship building
        dwell_time_weight=0.5,
        min_length=20,
        optimal_length=100,
        max_length=280,
        media_bonus=1.0,
        spam_threshold=100,
        fatigue_threshold=60,
        avg_impressions_per_post=100,
        avg_engagement_rate=0.10,  # High engagement on replies
        avg_follower_conversion=0.005,  # Good for conversions
    ),

    ContentType.POLL: ContentOptimalValues(
        content_type=ContentType.POLL,
        min_per_day=0,
        optimal_per_day=0.3,  # ~2 per week
        max_per_day=1,
        min_hours_between=24,
        optimal_hours_between=72,
        best_posting_hours=[11, 15],
        base_score_weight=1.3,
        engagement_multiplier=2.0,  # Polls drive engagement
        dwell_time_weight=1.5,
        min_length=2,  # options
        optimal_length=4,
        max_length=4,
        media_bonus=1.0,
        spam_threshold=2,
        fatigue_threshold=1,
        avg_impressions_per_post=1500,
        avg_engagement_rate=0.08,
        avg_follower_conversion=0.002,
    ),

    ContentType.SPACE: ContentOptimalValues(
        content_type=ContentType.SPACE,
        min_per_day=0,
        optimal_per_day=0.14,  # ~1 per week
        max_per_day=0.5,
        min_hours_between=48,
        optimal_hours_between=168,  # Weekly
        best_posting_hours=[19, 20, 21],  # Evening
        base_score_weight=2.0,
        engagement_multiplier=3.0,
        dwell_time_weight=5.0,  # Massive dwell time
        min_length=15,  # minutes
        optimal_length=45,
        max_length=120,
        media_bonus=1.0,
        spam_threshold=1,
        fatigue_threshold=1,
        avg_impressions_per_post=5000,
        avg_engagement_rate=0.10,
        avg_follower_conversion=0.01,
    ),

    ContentType.ARTICLE: ContentOptimalValues(
        content_type=ContentType.ARTICLE,
        min_per_day=0,
        optimal_per_day=0.14,  # ~1 per week
        max_per_day=0.5,
        min_hours_between=48,
        optimal_hours_between=168,
        best_posting_hours=[9, 14],
        base_score_weight=1.5,
        engagement_multiplier=1.8,
        dwell_time_weight=4.0,
        min_length=500,  # words
        optimal_length=1500,
        max_length=5000,
        media_bonus=1.2,
        spam_threshold=1,
        fatigue_threshold=1,
        avg_impressions_per_post=2500,
        avg_engagement_rate=0.04,
        avg_follower_conversion=0.005,
    ),
}


ENGAGEMENT_OPTIMAL_VALUES: Dict[EngagementType, EngagementOptimalValues] = {

    EngagementType.LIKE: EngagementOptimalValues(
        engagement_type=EngagementType.LIKE,
        min_per_day=10,
        optimal_per_day=50,
        max_per_day=200,
        signal_weight=0.5,  # From weighted_scorer.rs
        decay_half_life_hours=24,
        reciprocity_rate=0.05,
        relationship_weight=0.3,
        min_dwell_before=2,
    ),

    EngagementType.REPLY: EngagementOptimalValues(
        engagement_type=EngagementType.REPLY,
        min_per_day=5,
        optimal_per_day=30,
        max_per_day=100,
        signal_weight=1.0,  # Replies weighted heavily
        decay_half_life_hours=48,
        reciprocity_rate=0.20,
        relationship_weight=0.8,
        min_dwell_before=10,
        thoughtful_threshold=50,  # Characters for thoughtful reply
    ),

    EngagementType.RETWEET: EngagementOptimalValues(
        engagement_type=EngagementType.RETWEET,
        min_per_day=2,
        optimal_per_day=10,
        max_per_day=30,
        signal_weight=1.0,
        decay_half_life_hours=12,
        reciprocity_rate=0.10,
        relationship_weight=0.5,
        min_dwell_before=5,
    ),

    EngagementType.QUOTE: EngagementOptimalValues(
        engagement_type=EngagementType.QUOTE,
        min_per_day=0,
        optimal_per_day=5,
        max_per_day=15,
        signal_weight=1.0,
        decay_half_life_hours=36,
        reciprocity_rate=0.25,
        relationship_weight=0.7,
        min_dwell_before=15,
        thoughtful_threshold=100,
    ),

    EngagementType.BOOKMARK: EngagementOptimalValues(
        engagement_type=EngagementType.BOOKMARK,
        min_per_day=0,
        optimal_per_day=10,
        max_per_day=50,
        signal_weight=0.4,
        decay_half_life_hours=168,  # Long decay
        reciprocity_rate=0.0,  # Private
        relationship_weight=0.2,
        min_dwell_before=5,
    ),

    EngagementType.SHARE: EngagementOptimalValues(
        engagement_type=EngagementType.SHARE,
        min_per_day=0,
        optimal_per_day=3,
        max_per_day=10,
        signal_weight=1.5,
        decay_half_life_hours=24,
        reciprocity_rate=0.0,  # External
        relationship_weight=0.1,
        min_dwell_before=10,
    ),

    EngagementType.PROFILE_CLICK: EngagementOptimalValues(
        engagement_type=EngagementType.PROFILE_CLICK,
        min_per_day=5,
        optimal_per_day=30,
        max_per_day=100,
        signal_weight=0.3,
        decay_half_life_hours=12,
        reciprocity_rate=0.0,
        relationship_weight=0.4,
        min_dwell_before=0,
    ),

    EngagementType.FOLLOW: EngagementOptimalValues(
        engagement_type=EngagementType.FOLLOW,
        min_per_day=5,
        optimal_per_day=20,
        max_per_day=50,
        signal_weight=2.0,
        decay_half_life_hours=720,  # Long-term signal
        reciprocity_rate=0.30,  # Follow-back rate
        relationship_weight=1.0,
        min_dwell_before=30,
    ),

    EngagementType.DWELL_TIME: EngagementOptimalValues(
        engagement_type=EngagementType.DWELL_TIME,
        min_per_day=30,  # minutes total
        optimal_per_day=90,
        max_per_day=300,
        signal_weight=0.1,  # Per second
        decay_half_life_hours=24,
        reciprocity_rate=0.0,
        relationship_weight=0.5,
        min_dwell_before=0,
    ),

    EngagementType.VIDEO_WATCH: EngagementOptimalValues(
        engagement_type=EngagementType.VIDEO_WATCH,
        min_per_day=5,
        optimal_per_day=20,
        max_per_day=50,
        signal_weight=0.5,  # Per video
        decay_half_life_hours=24,
        reciprocity_rate=0.0,
        relationship_weight=0.3,
        min_dwell_before=0,
    ),

    EngagementType.LINK_CLICK: EngagementOptimalValues(
        engagement_type=EngagementType.LINK_CLICK,
        min_per_day=0,
        optimal_per_day=10,
        max_per_day=30,
        signal_weight=0.6,
        decay_half_life_hours=12,
        reciprocity_rate=0.0,
        relationship_weight=0.2,
        min_dwell_before=5,
    ),
}


@dataclass
class DailyOptimalSchedule:
    """Complete optimal daily schedule for maximum growth."""

    # Content creation
    text_posts: int = 4
    image_posts: int = 2
    video_short: int = 1
    video_long: int = 1
    threads: float = 0.7  # ~5/week
    quote_tweets: int = 2
    replies: int = 20
    polls: float = 0.3  # ~2/week

    # Engagement activities (giving)
    likes_given: int = 50
    replies_given: int = 30
    retweets_given: int = 10
    quotes_given: int = 5
    follows_given: int = 20

    # Time allocation (hours)
    content_creation_hours: float = 2.0
    engagement_hours: float = 1.5
    research_hours: float = 0.5

    def get_total_content_pieces(self) -> float:
        """Total content pieces per day."""
        return (self.text_posts + self.image_posts +
                self.video_short + self.video_long +
                self.threads + self.quote_tweets + self.polls)

    def get_effective_value(self) -> float:
        """Calculate total effective value accounting for diversity penalty."""
        # Simplified EV calculation
        from algorithm_model import AuthorDiversityModel, AlgorithmParams
        diversity = AuthorDiversityModel(AlgorithmParams())

        total_posts = int(self.text_posts + self.image_posts +
                         self.video_short + self.video_long)
        base_ev = diversity.get_effective_posts_per_day(total_posts)

        # Add thread and quote tweet bonuses
        thread_bonus = self.threads * 1.5  # Threads worth more
        quote_bonus = self.quote_tweets * 0.8

        return base_ev + thread_bonus + quote_bonus

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "content": {
                "text_posts": self.text_posts,
                "image_posts": self.image_posts,
                "video_short": self.video_short,
                "video_long": self.video_long,
                "threads": self.threads,
                "quote_tweets": self.quote_tweets,
                "replies": self.replies,
                "polls": self.polls,
            },
            "engagement": {
                "likes_given": self.likes_given,
                "replies_given": self.replies_given,
                "retweets_given": self.retweets_given,
                "quotes_given": self.quotes_given,
                "follows_given": self.follows_given,
            },
            "time_allocation": {
                "content_creation_hours": self.content_creation_hours,
                "engagement_hours": self.engagement_hours,
                "research_hours": self.research_hours,
            }
        }


# Maximum growth schedule (effort is not a constraint)
MAXIMUM_GROWTH_SCHEDULE = DailyOptimalSchedule(
    text_posts=6,
    image_posts=2,
    video_short=2,
    video_long=1,
    threads=1.0,  # Daily
    quote_tweets=3,
    replies=30,
    polls=0.5,
    likes_given=100,
    replies_given=50,
    retweets_given=15,
    quotes_given=8,
    follows_given=30,
    content_creation_hours=3.0,
    engagement_hours=2.0,
    research_hours=0.5,
)

# Efficient growth schedule (optimizing for time)
EFFICIENT_GROWTH_SCHEDULE = DailyOptimalSchedule(
    text_posts=4,
    image_posts=1,
    video_short=1,
    video_long=0.5,
    threads=0.5,
    quote_tweets=2,
    replies=15,
    polls=0.3,
    likes_given=30,
    replies_given=20,
    retweets_given=5,
    quotes_given=3,
    follows_given=15,
    content_creation_hours=1.5,
    engagement_hours=1.0,
    research_hours=0.25,
)

# Sustainable growth schedule (long-term)
SUSTAINABLE_GROWTH_SCHEDULE = DailyOptimalSchedule(
    text_posts=3,
    image_posts=1,
    video_short=0.5,
    video_long=0.3,
    threads=0.3,
    quote_tweets=1,
    replies=10,
    polls=0.2,
    likes_given=20,
    replies_given=15,
    retweets_given=3,
    quotes_given=2,
    follows_given=10,
    content_creation_hours=1.0,
    engagement_hours=0.75,
    research_hours=0.25,
)


def get_optimal_schedule(strategy: str = "maximum") -> DailyOptimalSchedule:
    """Get optimal schedule by strategy name."""
    schedules = {
        "maximum": MAXIMUM_GROWTH_SCHEDULE,
        "efficient": EFFICIENT_GROWTH_SCHEDULE,
        "sustainable": SUSTAINABLE_GROWTH_SCHEDULE,
    }
    return schedules.get(strategy, MAXIMUM_GROWTH_SCHEDULE)


def print_optimal_values_summary():
    """Print a summary of all optimal values."""
    print("=" * 80)
    print("OPTIMAL VALUES SUMMARY")
    print("=" * 80)

    print("\n## Content Types\n")
    print(f"{'Type':<15} {'Optimal/day':<12} {'Max/day':<10} {'Base Weight':<12} {'Dwell Weight':<12}")
    print("-" * 65)

    for ct, values in CONTENT_OPTIMAL_VALUES.items():
        print(f"{ct.value:<15} {values.optimal_per_day:<12} {values.max_per_day:<10} "
              f"{values.base_score_weight:<12.1f} {values.dwell_time_weight:<12.1f}")

    print("\n## Engagement Types\n")
    print(f"{'Type':<15} {'Optimal/day':<12} {'Signal Wt':<12} {'Reciprocity':<12}")
    print("-" * 55)

    for et, values in ENGAGEMENT_OPTIMAL_VALUES.items():
        print(f"{et.value:<15} {values.optimal_per_day:<12} "
              f"{values.signal_weight:<12.1f} {values.reciprocity_rate:<12.0%}")


if __name__ == "__main__":
    print_optimal_values_summary()
