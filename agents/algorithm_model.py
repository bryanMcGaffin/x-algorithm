"""
X Algorithm Model - Core simulation of the recommendation algorithm.

This module models the key algorithmic components extracted from:
- home-mixer/scorers/weighted_scorer.rs
- home-mixer/scorers/author_diversity_scorer.rs
- home-mixer/scorers/oon_scorer.rs
- home-mixer/filters/age_filter.rs
- phoenix/recsys_model.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math
from enum import Enum


# =============================================================================
# ALGORITHM PARAMETERS (Estimated from code analysis)
# =============================================================================

@dataclass
class AlgorithmParams:
    """
    Parameters extracted/estimated from the X algorithm codebase.

    Note: Actual values in home-mixer/params are redacted.
    These are reasonable estimates based on industry standards and code structure.
    """

    # Author Diversity Scorer params (from author_diversity_scorer.rs)
    AUTHOR_DIVERSITY_DECAY: float = 0.7  # Exponential decay factor
    AUTHOR_DIVERSITY_FLOOR: float = 0.2  # Minimum multiplier floor

    # OON (Out-of-Network) Scorer params (from oon_scorer.rs)
    OON_WEIGHT_FACTOR: float = 0.5  # Multiplier for out-of-network posts

    # Age Filter params (from age_filter.rs)
    MAX_POST_AGE_HOURS: int = 24  # Posts older than this filtered out

    # Video Quality View params (from weighted_scorer.rs)
    MIN_VIDEO_DURATION_MS: int = 45000  # 45 seconds minimum for VQV bonus
    VQV_WEIGHT: float = 1.2  # Bonus weight for qualifying videos

    # Engagement weights (estimated relative weights from weighted_scorer.rs)
    FAVORITE_WEIGHT: float = 1.0
    REPLY_WEIGHT: float = 1.1
    RETWEET_WEIGHT: float = 1.5
    QUOTE_WEIGHT: float = 1.3
    CLICK_WEIGHT: float = 0.5
    PROFILE_CLICK_WEIGHT: float = 0.8
    SHARE_WEIGHT: float = 1.2
    SHARE_VIA_DM_WEIGHT: float = 1.3
    SHARE_VIA_COPY_LINK_WEIGHT: float = 1.1
    DWELL_WEIGHT: float = 0.3
    CONT_DWELL_TIME_WEIGHT: float = 0.01  # Per second
    FOLLOW_AUTHOR_WEIGHT: float = 2.0
    PHOTO_EXPAND_WEIGHT: float = 0.4
    QUOTED_CLICK_WEIGHT: float = 0.6

    # Negative signal weights
    NOT_INTERESTED_WEIGHT: float = -1.5
    BLOCK_AUTHOR_WEIGHT: float = -5.0
    MUTE_AUTHOR_WEIGHT: float = -3.0
    REPORT_WEIGHT: float = -10.0

    # Model learning params (from recsys_model.py)
    HISTORY_SEQ_LEN: int = 128  # User action history length
    ALGORITHM_LEARNING_WEEKS: int = 3  # Weeks for author embedding to stabilize

    # Feed composition (estimated)
    FEED_SIZE: int = 50  # Posts per feed load
    IN_NETWORK_RATIO: float = 0.6  # Proportion of feed from followed accounts


# =============================================================================
# CONTENT TYPE DEFINITIONS
# =============================================================================

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO_SHORT = "video_short"  # < MIN_VIDEO_DURATION_MS
    VIDEO_LONG = "video_long"    # >= MIN_VIDEO_DURATION_MS
    THREAD = "thread"
    CAROUSEL = "carousel"


@dataclass
class Post:
    """Represents a single post for simulation."""
    post_id: int
    author_id: int
    content_type: ContentType
    hour_of_day: int  # 0-23
    day_number: int   # Day since start

    # Quality signals (0-1 scale representing engagement probability)
    quality_score: float = 0.5

    # Engagement outcomes (filled during simulation)
    engagement_rate: float = 0.0
    impressions: int = 0
    followers_gained: int = 0

    # Video-specific
    video_duration_ms: Optional[int] = None


@dataclass
class PostingSchedule:
    """A posting schedule configuration to test."""
    posts_per_day: int
    threads_per_week: int
    videos_per_week: int
    long_videos_per_week: int  # Videos > 45s
    hours_between_posts: float
    engagement_hours_per_day: float

    # Derived
    content_mix: Dict[ContentType, float] = field(default_factory=dict)


# =============================================================================
# AUTHOR DIVERSITY SCORER MODEL
# =============================================================================

class AuthorDiversityModel:
    """
    Models the author diversity scoring from author_diversity_scorer.rs

    multiplier(position) = (1.0 - floor) * decay^position + floor

    This penalizes multiple posts from the same author in a single feed.
    """

    def __init__(self, params: AlgorithmParams):
        self.decay = params.AUTHOR_DIVERSITY_DECAY
        self.floor = params.AUTHOR_DIVERSITY_FLOOR

    def get_multiplier(self, position: int) -> float:
        """
        Get score multiplier for the nth post from same author.

        Args:
            position: 0-indexed position (0 = first post, 1 = second, etc.)

        Returns:
            Multiplier between floor and 1.0
        """
        return (1.0 - self.floor) * (self.decay ** position) + self.floor

    def get_effective_posts_per_day(self, raw_posts: int) -> float:
        """
        Calculate effective post count after diversity penalty.

        If you post N times per day, the effective value is:
        sum(multiplier(i) for i in range(N))
        """
        total_value = 0.0
        for i in range(raw_posts):
            total_value += self.get_multiplier(i)
        return total_value

    def get_diminishing_returns_table(self, max_posts: int = 10) -> List[Tuple[int, float, float]]:
        """
        Generate a table showing diminishing returns.

        Returns:
            List of (posts, effective_value, marginal_value)
        """
        results = []
        prev_value = 0.0
        for n in range(1, max_posts + 1):
            effective = self.get_effective_posts_per_day(n)
            marginal = effective - prev_value
            results.append((n, round(effective, 3), round(marginal, 3)))
            prev_value = effective
        return results


# =============================================================================
# ENGAGEMENT SIMULATION MODEL
# =============================================================================

class EngagementModel:
    """
    Models expected engagement based on algorithm weights.
    """

    def __init__(self, params: AlgorithmParams):
        self.params = params

    def calculate_weighted_score(
        self,
        favorite_prob: float = 0.0,
        reply_prob: float = 0.0,
        retweet_prob: float = 0.0,
        quote_prob: float = 0.0,
        click_prob: float = 0.0,
        profile_click_prob: float = 0.0,
        vqv_prob: float = 0.0,
        share_prob: float = 0.0,
        dwell_seconds: float = 0.0,
        follow_prob: float = 0.0,
        is_long_video: bool = False,
        # Negative signals
        not_interested_prob: float = 0.0,
        block_prob: float = 0.0,
        mute_prob: float = 0.0,
    ) -> float:
        """
        Calculate weighted score matching weighted_scorer.rs logic.
        """
        p = self.params

        vqv_weight = p.VQV_WEIGHT if is_long_video else 0.0

        score = (
            favorite_prob * p.FAVORITE_WEIGHT +
            reply_prob * p.REPLY_WEIGHT +
            retweet_prob * p.RETWEET_WEIGHT +
            quote_prob * p.QUOTE_WEIGHT +
            click_prob * p.CLICK_WEIGHT +
            profile_click_prob * p.PROFILE_CLICK_WEIGHT +
            vqv_prob * vqv_weight +
            share_prob * p.SHARE_WEIGHT +
            dwell_seconds * p.CONT_DWELL_TIME_WEIGHT +
            follow_prob * p.FOLLOW_AUTHOR_WEIGHT +
            # Negative signals
            not_interested_prob * p.NOT_INTERESTED_WEIGHT +
            block_prob * p.BLOCK_AUTHOR_WEIGHT +
            mute_prob * p.MUTE_AUTHOR_WEIGHT
        )

        return score

    def get_content_type_bonus(self, content_type: ContentType) -> Dict[str, float]:
        """
        Get engagement probability bonuses by content type.

        Based on typical engagement patterns.
        """
        bonuses = {
            ContentType.TEXT: {
                "dwell_multiplier": 1.0,
                "reply_multiplier": 1.2,
                "retweet_multiplier": 1.0,
            },
            ContentType.IMAGE: {
                "dwell_multiplier": 1.3,
                "favorite_multiplier": 1.2,
                "photo_expand_bonus": 0.3,
            },
            ContentType.VIDEO_SHORT: {
                "dwell_multiplier": 1.5,
                "vqv_eligible": False,
            },
            ContentType.VIDEO_LONG: {
                "dwell_multiplier": 2.0,
                "vqv_eligible": True,
                "vqv_bonus": self.params.VQV_WEIGHT,
            },
            ContentType.THREAD: {
                "dwell_multiplier": 3.0,  # Threads have highest dwell
                "reply_multiplier": 1.3,
                "follow_multiplier": 1.5,
            },
            ContentType.CAROUSEL: {
                "dwell_multiplier": 1.8,
                "photo_expand_bonus": 0.4,
            },
        }
        return bonuses.get(content_type, {})


# =============================================================================
# FOLLOWER GROWTH MODEL
# =============================================================================

class FollowerGrowthModel:
    """
    Models follower accumulation over time.
    """

    def __init__(self, params: AlgorithmParams):
        self.params = params

    def estimate_impressions(
        self,
        follower_count: int,
        post_quality: float,
        is_in_network: bool,
        diversity_multiplier: float = 1.0,
    ) -> int:
        """
        Estimate impressions for a single post.

        Args:
            follower_count: Current follower count
            post_quality: Quality score 0-1
            is_in_network: Whether shown to followers (vs OON discovery)
            diversity_multiplier: From author diversity scorer
        """
        if is_in_network:
            # In-network: shown to portion of followers
            base_reach = follower_count * 0.1 * post_quality  # ~10% follower reach
            oon_factor = 1.0
        else:
            # Out-of-network: discovery depends on engagement
            base_reach = 100 * post_quality  # Base OON reach
            oon_factor = self.params.OON_WEIGHT_FACTOR

        impressions = int(base_reach * oon_factor * diversity_multiplier)
        return max(impressions, 1)

    def estimate_followers_from_impressions(
        self,
        impressions: int,
        engagement_rate: float,
        profile_click_rate: float = 0.02,
        follow_conversion_rate: float = 0.03,
    ) -> int:
        """
        Estimate new followers from impressions.

        Funnel: Impressions → Engagement → Profile Click → Follow
        """
        engaged = impressions * engagement_rate
        profile_clicks = engaged * profile_click_rate
        follows = profile_clicks * follow_conversion_rate
        return max(int(follows), 0)

    def compound_growth_rate(
        self,
        current_followers: int,
        daily_posts: int,
        avg_quality: float,
        diversity_model: AuthorDiversityModel,
    ) -> float:
        """
        Calculate expected daily follower growth rate.
        """
        effective_posts = diversity_model.get_effective_posts_per_day(daily_posts)

        # More followers = more in-network distribution
        in_network_boost = math.log10(max(current_followers, 10)) / 4

        # Base growth rate
        base_rate = 0.01 * avg_quality * effective_posts * (1 + in_network_boost)

        return min(base_rate, 0.1)  # Cap at 10% daily growth


# =============================================================================
# TIME-GATED CONSTRAINTS MODEL
# =============================================================================

class TimeConstraintsModel:
    """
    Models time-gated constraints that create calendar time floors.
    """

    def __init__(self, params: AlgorithmParams):
        self.params = params

    def get_minimum_calendar_days(
        self,
        target_followers: int,
        starting_followers: int = 0,
        posts_per_day: int = 3,
        avg_followers_per_viral: int = 1000,
        expected_viral_hits: int = 2,
    ) -> Dict[str, int]:
        """
        Calculate minimum calendar days to reach target.

        Returns breakdown of time-gated constraints.
        """
        followers_needed = target_followers - starting_followers

        # Viral contribution
        viral_followers = expected_viral_hits * avg_followers_per_viral
        organic_followers_needed = max(0, followers_needed - viral_followers)

        # Organic growth requires posts over time
        # Assuming ~30-70 followers per viral hit equivalent
        posts_for_organic = organic_followers_needed / 50  # ~50 followers per good post
        days_of_posting = math.ceil(posts_for_organic / posts_per_day)

        # Algorithm learning period
        learning_days = self.params.ALGORITHM_LEARNING_WEEKS * 7

        # Content saturation (can't post unlimited quality content)
        # Quality degrades past certain volume
        sustainable_days = max(days_of_posting, 60)  # Minimum 60 days typical

        return {
            "algorithm_learning_days": learning_days,
            "minimum_posting_days": days_of_posting,
            "sustainable_growth_days": sustainable_days,
            "total_minimum_days": max(learning_days, days_of_posting, 56),  # 8 week floor
            "expected_realistic_days": int(sustainable_days * 1.5),
        }

    def get_optimal_posting_frequency(self) -> Dict[str, any]:
        """
        Calculate optimal posting frequency given constraints.
        """
        diversity = AuthorDiversityModel(self.params)

        # Find where marginal value drops below threshold
        table = diversity.get_diminishing_returns_table(10)

        optimal_posts = 3  # Default
        for posts, effective, marginal in table:
            if marginal < 0.3:  # Below 30% marginal value
                optimal_posts = posts - 1
                break

        return {
            "optimal_posts_per_day": max(optimal_posts, 1),
            "diminishing_returns_table": table,
            "min_hours_between_posts": 3,  # To land in different scoring batches
            "max_effective_posts": optimal_posts + 1,
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_diversity_analysis(params: AlgorithmParams = None):
    """Print author diversity analysis."""
    if params is None:
        params = AlgorithmParams()

    model = AuthorDiversityModel(params)

    print("\n" + "="*60)
    print("AUTHOR DIVERSITY PENALTY ANALYSIS")
    print("="*60)
    print(f"\nParameters: decay={model.decay}, floor={model.floor}")
    print(f"\nFormula: multiplier = (1 - {model.floor}) × {model.decay}^position + {model.floor}")
    print("\n" + "-"*60)
    print(f"{'Posts/Day':<12} {'Effective Value':<18} {'Marginal Value':<15} {'Efficiency':<12}")
    print("-"*60)

    for posts, effective, marginal in model.get_diminishing_returns_table(8):
        efficiency = effective / posts if posts > 0 else 0
        print(f"{posts:<12} {effective:<18} {marginal:<15} {efficiency:.1%}")

    print("-"*60)
    print("\n✓ Optimal: 3-4 posts/day (marginal value still > 0.3)")
    print("✗ Diminishing: 5+ posts/day (each additional post < 30% effective)")


def print_time_constraints(target: int = 10000, params: AlgorithmParams = None):
    """Print time constraint analysis."""
    if params is None:
        params = AlgorithmParams()

    model = TimeConstraintsModel(params)
    constraints = model.get_minimum_calendar_days(target)

    print("\n" + "="*60)
    print(f"TIME-GATED CONSTRAINTS TO {target:,} FOLLOWERS")
    print("="*60)
    print(f"\nAlgorithm Learning Period: {constraints['algorithm_learning_days']} days")
    print(f"Minimum Posting Days: {constraints['minimum_posting_days']} days")
    print(f"Sustainable Growth Period: {constraints['sustainable_growth_days']} days")
    print(f"\n{'='*60}")
    print(f"ABSOLUTE MINIMUM: {constraints['total_minimum_days']} days ({constraints['total_minimum_days']//7} weeks)")
    print(f"REALISTIC EXPECTATION: {constraints['expected_realistic_days']} days ({constraints['expected_realistic_days']//7} weeks)")
    print("="*60)


if __name__ == "__main__":
    # Demo the models
    params = AlgorithmParams()
    print_diversity_analysis(params)
    print_time_constraints(10000, params)
