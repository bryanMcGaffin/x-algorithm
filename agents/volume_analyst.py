"""
Volume Analyst Agent

Compares suggested posting volumes against the X algorithm constraints.
Analyzes whether proposed strategies align with algorithmic realities.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from algorithm_model import (
    AlgorithmParams,
    AuthorDiversityModel,
    EngagementModel,
    FollowerGrowthModel,
    TimeConstraintsModel,
    ContentType,
    PostingSchedule,
)


@dataclass
class VolumeAnalysis:
    """Results of volume analysis."""
    schedule_name: str
    raw_posts_per_day: int
    effective_posts_per_day: float
    efficiency_ratio: float
    daily_effective_impressions: int
    weekly_effective_impressions: int
    estimated_daily_followers: float
    estimated_weekly_followers: float
    calendar_days_to_10k: int
    total_effort_hours: float
    algorithm_alignment_score: float  # 0-100
    warnings: List[str]
    recommendations: List[str]


class VolumeAnalystAgent:
    """
    Analyzes posting volumes against X algorithm constraints.

    Compares suggested schedules to algorithm mechanics:
    - Author diversity penalty
    - Time-gated constraints
    - Engagement optimization
    - Diminishing returns
    """

    def __init__(self, params: AlgorithmParams = None):
        self.params = params or AlgorithmParams()
        self.diversity_model = AuthorDiversityModel(self.params)
        self.engagement_model = EngagementModel(self.params)
        self.growth_model = FollowerGrowthModel(self.params)
        self.time_model = TimeConstraintsModel(self.params)

    def analyze_schedule(
        self,
        schedule: PostingSchedule,
        schedule_name: str = "Custom",
        starting_followers: int = 0,
        target_followers: int = 10000,
    ) -> VolumeAnalysis:
        """
        Analyze a posting schedule against algorithm constraints.
        """
        warnings = []
        recommendations = []

        # 1. Calculate effective posts after diversity penalty
        effective_posts = self.diversity_model.get_effective_posts_per_day(
            schedule.posts_per_day
        )
        efficiency = effective_posts / schedule.posts_per_day if schedule.posts_per_day > 0 else 0

        # 2. Check for diversity penalty issues
        if schedule.posts_per_day > 4:
            penalty = 1 - efficiency
            warnings.append(
                f"⚠️  Diversity penalty: {penalty:.0%} of post value lost. "
                f"Post #{schedule.posts_per_day} only worth {self.diversity_model.get_multiplier(schedule.posts_per_day-1):.0%}"
            )
            recommendations.append(
                f"Consider reducing to 3-4 posts/day for better efficiency"
            )

        # 3. Check posting interval
        if schedule.hours_between_posts < 3:
            warnings.append(
                f"⚠️  Posts {schedule.hours_between_posts}hrs apart may land in same scoring batch"
            )
            recommendations.append("Space posts 3-4+ hours apart")

        # 4. Estimate daily followers (calibrated to realistic X growth)
        #
        # Realistic benchmarks (from successful X growth accounts):
        # - 1 post/day, minimal engagement: 5-15 followers/day
        # - 3 posts/day, 1hr engagement: 30-70 followers/day
        # - 4 posts/day, threads, videos, 1.5hr engagement: 70-150 followers/day
        # - Viral posts: 500-5000 followers each
        #
        # Model: base + content_bonus + engagement_bonus + viral_component

        # Base followers from consistent posting (scales with effective posts)
        base_daily = 12 * effective_posts  # ~12 followers per effective post

        # Thread bonus (threads have higher conversion due to dwell time + follow CTAs)
        thread_daily = schedule.threads_per_week * 10  # ~10 extra followers per thread
        thread_per_day = thread_daily / 7

        # Video bonus (especially long videos with VQV)
        video_daily = schedule.long_videos_per_week * 12  # ~12 extra per long video
        video_per_day = video_daily / 7

        # Engagement bonus (engagement drives discovery and relationships)
        engagement_daily = schedule.engagement_hours_per_day * 20  # ~20 followers per hour engaged

        # Viral component (probability-weighted average)
        # Assume ~5% chance of a post going "mini-viral" (200-800 followers) per day with good content
        viral_prob = 0.03 + (effective_posts * 0.008) + (schedule.threads_per_week / 7 * 0.03)
        avg_viral_followers = 300
        viral_daily = viral_prob * avg_viral_followers

        # Total daily followers
        daily_followers = (
            base_daily +
            thread_per_day +
            video_per_day +
            engagement_daily +
            viral_daily
        )

        # Compound growth factor (more followers = more in-network distribution)
        # OON_WEIGHT_FACTOR means followers give 2x distribution
        # Simulate average over growth period accounting for this
        avg_growth_multiplier = 1.5

        daily_followers = daily_followers * avg_growth_multiplier

        # Calculate impressions backwards for display (rough estimate)
        # Typical: ~0.5-1% of impressions convert to followers
        estimated_conversion = 0.007
        daily_impressions = int(daily_followers / estimated_conversion)
        weekly_impressions = daily_impressions * 7

        # Engagement rate (for display)
        engagement_rate = 0.03 + (schedule.engagement_hours_per_day * 0.01)

        weekly_followers = daily_followers * 7

        # 6. Calculate time to target
        followers_needed = target_followers - starting_followers
        if weekly_followers > 0:
            weeks_needed = followers_needed / weekly_followers
            days_needed = int(weeks_needed * 7)
        else:
            days_needed = 365  # Cap at 1 year

        # Apply time-gated floor
        time_constraints = self.time_model.get_minimum_calendar_days(target_followers)
        min_days = time_constraints['total_minimum_days']

        if days_needed < min_days:
            original_days = days_needed
            days_needed = min_days
            warnings.append(
                f"⚠️  Time floor applied: {original_days} → {min_days} days "
                f"(algorithm learning + posting constraints)"
            )

        # 7. Check video content
        if schedule.videos_per_week == 0:
            recommendations.append(
                "Add 2-3 videos/week to access VQV weight bonus (+20% score for qualifying videos)"
            )

        if schedule.long_videos_per_week == 0 and schedule.videos_per_week > 0:
            warnings.append(
                f"⚠️  Short videos (<45s) don't qualify for VQV bonus"
            )
            recommendations.append(
                f"Make videos >{self.params.MIN_VIDEO_DURATION_MS//1000}s to qualify for VQV weight"
            )

        # 8. Check thread content
        if schedule.threads_per_week == 0:
            recommendations.append(
                "Add 2-3 threads/week for higher dwell_time signal (3x dwell vs single posts)"
            )

        # 9. Check engagement time
        if schedule.engagement_hours_per_day < 0.5:
            warnings.append(
                "⚠️  Low engagement time limits discovery and relationship building"
            )
            recommendations.append("Increase engagement to 45-60 min/day minimum")

        # 10. Calculate total effort
        total_effort = (
            schedule.posts_per_day * 0.25 +  # 15 min per post AI-assisted
            (schedule.threads_per_week / 7) * 1.0 +  # 1 hr per thread
            (schedule.videos_per_week / 7) * 0.75 +  # 45 min per video
            schedule.engagement_hours_per_day +
            0.25  # Analytics/planning
        )

        # 11. Calculate algorithm alignment score
        alignment_score = self._calculate_alignment_score(
            schedule, effective_posts, efficiency, days_needed
        )

        return VolumeAnalysis(
            schedule_name=schedule_name,
            raw_posts_per_day=schedule.posts_per_day,
            effective_posts_per_day=round(effective_posts, 2),
            efficiency_ratio=round(efficiency, 3),
            daily_effective_impressions=daily_impressions,
            weekly_effective_impressions=weekly_impressions,
            estimated_daily_followers=round(daily_followers, 1),
            estimated_weekly_followers=round(weekly_followers, 1),
            calendar_days_to_10k=days_needed,
            total_effort_hours=round(total_effort, 2),
            algorithm_alignment_score=alignment_score,
            warnings=warnings,
            recommendations=recommendations,
        )

    def _calculate_alignment_score(
        self,
        schedule: PostingSchedule,
        effective_posts: float,
        efficiency: float,
        days_to_10k: int,
    ) -> float:
        """
        Calculate how well the schedule aligns with algorithm constraints.

        Score 0-100 based on:
        - Efficiency (not wasting posts to diversity penalty)
        - Content mix (threads + videos for signal diversity)
        - Engagement time (relationship building)
        - Time efficiency (not over-investing effort)
        """
        score = 0

        # Efficiency score (25 points max)
        if efficiency >= 0.8:
            score += 25
        elif efficiency >= 0.6:
            score += 20
        elif efficiency >= 0.4:
            score += 10
        else:
            score += 5

        # Posts per day optimality (25 points max)
        if 2 <= schedule.posts_per_day <= 4:
            score += 25
        elif schedule.posts_per_day == 1 or schedule.posts_per_day == 5:
            score += 15
        else:
            score += 5

        # Content diversity (25 points max)
        content_score = 0
        if schedule.threads_per_week >= 2:
            content_score += 10
        elif schedule.threads_per_week >= 1:
            content_score += 5

        if schedule.long_videos_per_week >= 2:
            content_score += 10
        elif schedule.long_videos_per_week >= 1:
            content_score += 5

        if schedule.videos_per_week >= schedule.long_videos_per_week + 1:
            content_score += 5

        score += min(content_score, 25)

        # Engagement balance (25 points max)
        if 0.75 <= schedule.engagement_hours_per_day <= 1.5:
            score += 25
        elif 0.5 <= schedule.engagement_hours_per_day <= 2.0:
            score += 20
        elif schedule.engagement_hours_per_day >= 0.25:
            score += 10
        else:
            score += 5

        return min(score, 100)

    def compare_schedules(
        self,
        schedules: List[Tuple[str, PostingSchedule]],
        starting_followers: int = 0,
        target_followers: int = 10000,
    ) -> List[VolumeAnalysis]:
        """
        Compare multiple schedules against algorithm.
        """
        results = []
        for name, schedule in schedules:
            analysis = self.analyze_schedule(
                schedule, name, starting_followers, target_followers
            )
            results.append(analysis)

        # Sort by algorithm alignment score
        results.sort(key=lambda x: x.algorithm_alignment_score, reverse=True)
        return results

    def print_analysis(self, analysis: VolumeAnalysis):
        """Print formatted analysis results."""
        print("\n" + "=" * 70)
        print(f"VOLUME ANALYSIS: {analysis.schedule_name}")
        print("=" * 70)

        print(f"\n📊 POSTING METRICS")
        print(f"   Raw posts/day:       {analysis.raw_posts_per_day}")
        print(f"   Effective posts/day: {analysis.effective_posts_per_day}")
        print(f"   Efficiency ratio:    {analysis.efficiency_ratio:.1%}")

        print(f"\n📈 GROWTH PROJECTIONS")
        print(f"   Daily impressions:   ~{analysis.daily_effective_impressions:,}")
        print(f"   Weekly impressions:  ~{analysis.weekly_effective_impressions:,}")
        print(f"   Daily followers:     ~{analysis.estimated_daily_followers:.0f}")
        print(f"   Weekly followers:    ~{analysis.estimated_weekly_followers:.0f}")

        print(f"\n⏱️  TIMELINE")
        print(f"   Calendar days to 10K: {analysis.calendar_days_to_10k} days")
        print(f"   Calendar weeks:       {analysis.calendar_days_to_10k // 7} weeks")
        print(f"   Calendar months:      {analysis.calendar_days_to_10k / 30:.1f} months")
        print(f"   Daily effort:         {analysis.total_effort_hours:.1f} hours")

        print(f"\n🎯 ALGORITHM ALIGNMENT SCORE: {analysis.algorithm_alignment_score}/100")

        if analysis.warnings:
            print(f"\n⚠️  WARNINGS")
            for w in analysis.warnings:
                print(f"   {w}")

        if analysis.recommendations:
            print(f"\n💡 RECOMMENDATIONS")
            for r in analysis.recommendations:
                print(f"   • {r}")

        print()


def get_playbook_schedules() -> List[Tuple[str, PostingSchedule]]:
    """
    Return the schedules from the playbook for testing.
    """
    return [
        ("Minimum (1 hr/day)", PostingSchedule(
            posts_per_day=1,
            threads_per_week=1,
            videos_per_week=1,
            long_videos_per_week=1,
            hours_between_posts=24,
            engagement_hours_per_day=0.5,
        )),
        ("Standard (2 hrs/day)", PostingSchedule(
            posts_per_day=3,
            threads_per_week=2,
            videos_per_week=2,
            long_videos_per_week=2,
            hours_between_posts=5,
            engagement_hours_per_day=0.75,
        )),
        ("Accelerated (3-4 hrs/day)", PostingSchedule(
            posts_per_day=4,
            threads_per_week=3,
            videos_per_week=3,
            long_videos_per_week=3,
            hours_between_posts=4,
            engagement_hours_per_day=1.0,
        )),
        ("Intensive (5-6 hrs/day)", PostingSchedule(
            posts_per_day=4,
            threads_per_week=5,
            videos_per_week=5,
            long_videos_per_week=4,
            hours_between_posts=4,
            engagement_hours_per_day=1.5,
        )),
        # Test edge cases
        ("Over-posting (8/day)", PostingSchedule(
            posts_per_day=8,
            threads_per_week=2,
            videos_per_week=2,
            long_videos_per_week=2,
            hours_between_posts=2,
            engagement_hours_per_day=0.5,
        )),
        ("Under-posting (content only)", PostingSchedule(
            posts_per_day=1,
            threads_per_week=0,
            videos_per_week=0,
            long_videos_per_week=0,
            hours_between_posts=24,
            engagement_hours_per_day=0.0,
        )),
    ]


def main():
    """Run volume analysis on playbook schedules."""
    agent = VolumeAnalystAgent()

    print("\n" + "=" * 70)
    print("X ALGORITHM VOLUME ANALYST AGENT")
    print("Comparing posting schedules against algorithm constraints")
    print("=" * 70)

    schedules = get_playbook_schedules()
    results = agent.compare_schedules(schedules)

    for analysis in results:
        agent.print_analysis(analysis)

    # Summary comparison
    print("\n" + "=" * 70)
    print("SUMMARY COMPARISON (Ranked by Algorithm Alignment)")
    print("=" * 70)
    print(f"\n{'Schedule':<28} {'Posts':<8} {'Eff.':<8} {'Days':<8} {'Score':<8}")
    print("-" * 70)

    for a in results:
        print(
            f"{a.schedule_name:<28} "
            f"{a.raw_posts_per_day:<8} "
            f"{a.efficiency_ratio:.0%:<8} "
            f"{a.calendar_days_to_10k:<8} "
            f"{a.algorithm_alignment_score:<8}"
        )

    # Winner
    winner = results[0]
    print(f"\n{'='*70}")
    print(f"🏆 BEST ALIGNMENT: {winner.schedule_name}")
    print(f"   Score: {winner.algorithm_alignment_score}/100")
    print(f"   Timeline: {winner.calendar_days_to_10k} days ({winner.calendar_days_to_10k//7} weeks)")
    print(f"   Daily effort: {winner.total_effort_hours:.1f} hours")
    print("=" * 70)


if __name__ == "__main__":
    main()
