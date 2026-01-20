"""
Testing Agent

Simulates different posting volume configurations against the X algorithm
to find optimal strategies through systematic testing.
"""

import itertools
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random
import math

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
class SimulationResult:
    """Results from a single simulation run."""
    config_id: str
    posts_per_day: int
    threads_per_week: int
    videos_per_week: int
    long_videos_per_week: int
    engagement_hours: float
    hours_between_posts: float

    # Outcomes
    effective_posts_per_day: float
    efficiency: float
    days_to_1k: int
    days_to_5k: int
    days_to_10k: int
    total_effort_hours_to_10k: float
    effort_per_follower: float  # hours per follower
    algorithm_score: float

    # Detailed metrics
    avg_daily_impressions: int
    avg_engagement_rate: float
    viral_probability: float


@dataclass
class TestConfiguration:
    """A configuration to test."""
    posts_per_day: int
    threads_per_week: int
    videos_per_week: int
    long_videos_per_week: int
    engagement_hours: float
    hours_between_posts: float


class TestingAgent:
    """
    Systematically tests volume configurations against the algorithm.

    Generates test configurations, simulates outcomes, and records results
    for optimization analysis.
    """

    def __init__(self, params: AlgorithmParams = None, seed: int = 42):
        self.params = params or AlgorithmParams()
        self.diversity_model = AuthorDiversityModel(self.params)
        self.growth_model = FollowerGrowthModel(self.params)
        self.time_model = TimeConstraintsModel(self.params)
        random.seed(seed)
        self.results: List[SimulationResult] = []

    def generate_test_grid(self) -> List[TestConfiguration]:
        """
        Generate a grid of configurations to test.

        Tests combinations of:
        - Posts per day: 1-8
        - Threads per week: 0-5
        - Videos per week: 0-5
        - Long videos: 0 to videos_per_week
        - Engagement hours: 0.25-2.5
        - Hours between posts: 2-8
        """
        configs = []

        posts_options = [1, 2, 3, 4, 5, 6, 8]
        threads_options = [0, 1, 2, 3, 4, 5]
        videos_options = [0, 1, 2, 3, 4, 5]
        engagement_options = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5]
        spacing_options = [2, 3, 4, 5, 6, 8]

        for posts in posts_options:
            for threads in threads_options:
                for videos in videos_options:
                    for long_vids in range(min(videos + 1, 4)):  # Limit combinations
                        for engagement in engagement_options:
                            # Only test a few spacing options to reduce combinations
                            spacing = max(2, min(8, 24 // posts)) if posts > 0 else 24
                            configs.append(TestConfiguration(
                                posts_per_day=posts,
                                threads_per_week=threads,
                                videos_per_week=videos,
                                long_videos_per_week=long_vids,
                                engagement_hours=engagement,
                                hours_between_posts=spacing,
                            ))

        # Deduplicate
        seen = set()
        unique_configs = []
        for c in configs:
            key = (c.posts_per_day, c.threads_per_week, c.videos_per_week,
                   c.long_videos_per_week, c.engagement_hours)
            if key not in seen:
                seen.add(key)
                unique_configs.append(c)

        return unique_configs

    def generate_focused_grid(self) -> List[TestConfiguration]:
        """
        Generate a focused grid around expected optimal ranges.
        """
        configs = []

        # Focus on reasonable ranges based on algorithm analysis
        posts_options = [2, 3, 4, 5]
        threads_options = [1, 2, 3, 4]
        videos_options = [1, 2, 3]
        engagement_options = [0.5, 0.75, 1.0, 1.25, 1.5]

        for posts, threads, videos, engagement in itertools.product(
            posts_options, threads_options, videos_options, engagement_options
        ):
            for long_ratio in [0.5, 0.75, 1.0]:
                long_vids = max(1, int(videos * long_ratio))
                spacing = max(3, 16 // posts)

                configs.append(TestConfiguration(
                    posts_per_day=posts,
                    threads_per_week=threads,
                    videos_per_week=videos,
                    long_videos_per_week=long_vids,
                    engagement_hours=engagement,
                    hours_between_posts=spacing,
                ))

        return configs

    def simulate_growth(
        self,
        config: TestConfiguration,
        target_followers: int = 10000,
        starting_followers: int = 0,
        max_days: int = 365,
    ) -> SimulationResult:
        """
        Simulate follower growth for a configuration.
        """
        # Calculate effective posts
        effective_posts = self.diversity_model.get_effective_posts_per_day(config.posts_per_day)
        efficiency = effective_posts / config.posts_per_day if config.posts_per_day > 0 else 0

        # Base quality score (affected by effort distribution)
        # More posts with same effort = lower quality per post
        effort_per_post = (
            config.engagement_hours * 0.3 +  # Engagement quality
            (config.threads_per_week / 7) * 0.3 +  # Thread effort
            (config.long_videos_per_week / 7) * 0.3  # Video effort
        ) / max(config.posts_per_day, 1)

        quality_score = min(0.8, 0.3 + effort_per_post * 0.5)

        # Content bonuses
        thread_dwell_bonus = 1 + (config.threads_per_week / 7) * 0.5
        video_vqv_bonus = 1 + (config.long_videos_per_week / 7) * self.params.VQV_WEIGHT * 0.3
        engagement_bonus = 1 + config.engagement_hours * 0.1

        # Combined quality multiplier
        quality_multiplier = quality_score * thread_dwell_bonus * video_vqv_bonus * engagement_bonus

        # Base impressions (grows with follower count)
        def get_daily_impressions(followers: int) -> int:
            base = 200 + followers * 0.15  # 15% of followers see posts + base discovery
            return int(base * effective_posts * quality_multiplier)

        # Engagement rate (affected by content quality and engagement time)
        base_engagement = 0.02 + config.engagement_hours * 0.005
        engagement_rate = min(0.10, base_engagement * quality_score)

        # Follower conversion funnel
        profile_click_rate = 0.02 + quality_score * 0.02
        follow_conversion = 0.03 + (config.threads_per_week / 7) * 0.01

        # Viral probability (chance of a post going viral per day)
        # Higher with quality content and engagement
        viral_prob = min(0.05, quality_score * 0.02 * (1 + config.engagement_hours * 0.1))
        viral_follower_boost = random.randint(300, 1500)

        # Simulate day by day
        followers = starting_followers
        days_to_1k = None
        days_to_5k = None
        days_to_10k = None
        total_impressions = 0

        for day in range(1, max_days + 1):
            # Daily impressions
            impressions = get_daily_impressions(followers)
            total_impressions += impressions

            # Organic followers
            engaged = impressions * engagement_rate
            profile_clicks = engaged * profile_click_rate
            new_followers = int(profile_clicks * follow_conversion)

            # Viral boost (random chance)
            if random.random() < viral_prob:
                new_followers += viral_follower_boost

            followers += max(new_followers, 1)  # At least 1 follower per day with effort

            # Check milestones
            if days_to_1k is None and followers >= 1000:
                days_to_1k = day
            if days_to_5k is None and followers >= 5000:
                days_to_5k = day
            if days_to_10k is None and followers >= target_followers:
                days_to_10k = day
                break

        # If didn't reach 10k, estimate
        if days_to_10k is None:
            if followers > starting_followers:
                daily_rate = (followers - starting_followers) / max_days
                remaining = target_followers - followers
                days_to_10k = max_days + int(remaining / daily_rate)
            else:
                days_to_10k = 999

        # Apply time floor
        time_constraints = self.time_model.get_minimum_calendar_days(target_followers)
        min_days = time_constraints['total_minimum_days']
        days_to_10k = max(days_to_10k, min_days)
        if days_to_1k:
            days_to_1k = max(days_to_1k, 14)  # 2 week minimum
        if days_to_5k:
            days_to_5k = max(days_to_5k, 35)  # 5 week minimum

        # Calculate effort
        daily_effort = (
            config.posts_per_day * 0.2 +  # 12 min per post AI-assisted
            (config.threads_per_week / 7) * 0.75 +
            (config.videos_per_week / 7) * 0.5 +
            config.engagement_hours +
            0.25  # Planning/analytics
        )
        total_effort = daily_effort * days_to_10k
        effort_per_follower = total_effort / target_followers

        # Algorithm alignment score
        algorithm_score = self._calculate_algorithm_score(config, efficiency, quality_multiplier)

        # Generate config ID
        config_id = (
            f"P{config.posts_per_day}_T{config.threads_per_week}_"
            f"V{config.videos_per_week}L{config.long_videos_per_week}_"
            f"E{config.engagement_hours}"
        )

        return SimulationResult(
            config_id=config_id,
            posts_per_day=config.posts_per_day,
            threads_per_week=config.threads_per_week,
            videos_per_week=config.videos_per_week,
            long_videos_per_week=config.long_videos_per_week,
            engagement_hours=config.engagement_hours,
            hours_between_posts=config.hours_between_posts,
            effective_posts_per_day=round(effective_posts, 2),
            efficiency=round(efficiency, 3),
            days_to_1k=days_to_1k or 999,
            days_to_5k=days_to_5k or 999,
            days_to_10k=days_to_10k,
            total_effort_hours_to_10k=round(total_effort, 1),
            effort_per_follower=round(effort_per_follower, 4),
            algorithm_score=round(algorithm_score, 1),
            avg_daily_impressions=total_impressions // max(day, 1),
            avg_engagement_rate=round(engagement_rate, 4),
            viral_probability=round(viral_prob, 4),
        )

    def _calculate_algorithm_score(
        self,
        config: TestConfiguration,
        efficiency: float,
        quality_multiplier: float,
    ) -> float:
        """Calculate algorithm alignment score."""
        score = 0

        # Efficiency (0-25)
        score += efficiency * 25

        # Quality multiplier (0-25)
        score += min(quality_multiplier / 2, 1) * 25

        # Content diversity (0-25)
        if config.threads_per_week >= 2:
            score += 10
        if config.long_videos_per_week >= 2:
            score += 10
        if config.videos_per_week > config.long_videos_per_week:
            score += 5

        # Engagement balance (0-25)
        if 0.75 <= config.engagement_hours <= 1.5:
            score += 25
        elif 0.5 <= config.engagement_hours <= 2.0:
            score += 15
        else:
            score += 5

        return min(score, 100)

    def run_test_suite(
        self,
        configs: List[TestConfiguration] = None,
        num_runs: int = 1,
    ) -> List[SimulationResult]:
        """
        Run simulations on all configurations.

        Args:
            configs: Configurations to test (uses focused grid if None)
            num_runs: Number of simulation runs per config (for averaging)
        """
        if configs is None:
            configs = self.generate_focused_grid()

        print(f"\n🧪 Running {len(configs)} configurations...")

        self.results = []
        for i, config in enumerate(configs):
            if (i + 1) % 50 == 0:
                print(f"   Progress: {i+1}/{len(configs)}")

            # Run multiple times and average (for stochastic elements)
            run_results = []
            for _ in range(num_runs):
                result = self.simulate_growth(config)
                run_results.append(result)

            # Average the results
            if num_runs > 1:
                avg_result = self._average_results(run_results)
            else:
                avg_result = run_results[0]

            self.results.append(avg_result)

        return self.results

    def _average_results(self, results: List[SimulationResult]) -> SimulationResult:
        """Average multiple simulation runs."""
        n = len(results)
        first = results[0]

        return SimulationResult(
            config_id=first.config_id,
            posts_per_day=first.posts_per_day,
            threads_per_week=first.threads_per_week,
            videos_per_week=first.videos_per_week,
            long_videos_per_week=first.long_videos_per_week,
            engagement_hours=first.engagement_hours,
            hours_between_posts=first.hours_between_posts,
            effective_posts_per_day=first.effective_posts_per_day,
            efficiency=first.efficiency,
            days_to_1k=int(sum(r.days_to_1k for r in results) / n),
            days_to_5k=int(sum(r.days_to_5k for r in results) / n),
            days_to_10k=int(sum(r.days_to_10k for r in results) / n),
            total_effort_hours_to_10k=round(sum(r.total_effort_hours_to_10k for r in results) / n, 1),
            effort_per_follower=round(sum(r.effort_per_follower for r in results) / n, 4),
            algorithm_score=round(sum(r.algorithm_score for r in results) / n, 1),
            avg_daily_impressions=int(sum(r.avg_daily_impressions for r in results) / n),
            avg_engagement_rate=round(sum(r.avg_engagement_rate for r in results) / n, 4),
            viral_probability=round(sum(r.viral_probability for r in results) / n, 4),
        )

    def get_top_results(
        self,
        metric: str = "days_to_10k",
        n: int = 10,
        ascending: bool = True,
    ) -> List[SimulationResult]:
        """Get top N results by a metric."""
        sorted_results = sorted(
            self.results,
            key=lambda x: getattr(x, metric),
            reverse=not ascending,
        )
        return sorted_results[:n]

    def get_pareto_optimal(self) -> List[SimulationResult]:
        """
        Find Pareto-optimal configurations.

        A configuration is Pareto-optimal if no other configuration
        is better in all objectives (time, effort, algorithm score).
        """
        pareto = []

        for result in self.results:
            dominated = False

            for other in self.results:
                if other is result:
                    continue

                # Check if 'other' dominates 'result'
                # Domination: better or equal in all, strictly better in at least one
                better_time = other.days_to_10k <= result.days_to_10k
                better_effort = other.total_effort_hours_to_10k <= result.total_effort_hours_to_10k
                better_score = other.algorithm_score >= result.algorithm_score

                strictly_better = (
                    other.days_to_10k < result.days_to_10k or
                    other.total_effort_hours_to_10k < result.total_effort_hours_to_10k or
                    other.algorithm_score > result.algorithm_score
                )

                if better_time and better_effort and better_score and strictly_better:
                    dominated = True
                    break

            if not dominated:
                pareto.append(result)

        return pareto

    def print_results_table(self, results: List[SimulationResult], title: str = "Results"):
        """Print results in a formatted table."""
        print(f"\n{'='*100}")
        print(f"{title}")
        print(f"{'='*100}")

        header = (
            f"{'Config':<25} "
            f"{'Posts':<6} "
            f"{'Thrds':<6} "
            f"{'Vids':<6} "
            f"{'Eng.H':<6} "
            f"{'Eff.':<6} "
            f"{'Days':<6} "
            f"{'Hours':<8} "
            f"{'Score':<6}"
        )
        print(header)
        print("-" * 100)

        for r in results[:20]:  # Limit display
            row = (
                f"{r.config_id:<25} "
                f"{r.posts_per_day:<6} "
                f"{r.threads_per_week:<6} "
                f"{r.videos_per_week:<6} "
                f"{r.engagement_hours:<6} "
                f"{r.efficiency:.0%:<6} "
                f"{r.days_to_10k:<6} "
                f"{r.total_effort_hours_to_10k:<8} "
                f"{r.algorithm_score:<6}"
            )
            print(row)


def main():
    """Run the testing agent."""
    print("\n" + "=" * 70)
    print("X ALGORITHM TESTING AGENT")
    print("Simulating volume configurations against algorithm")
    print("=" * 70)

    agent = TestingAgent()

    # Run focused test suite
    configs = agent.generate_focused_grid()
    print(f"\nGenerated {len(configs)} test configurations")

    results = agent.run_test_suite(configs, num_runs=3)

    # Get results by different metrics
    print("\n" + "=" * 70)
    print("TOP 10 BY FASTEST TIME TO 10K")
    agent.print_results_table(
        agent.get_top_results("days_to_10k", 10, ascending=True),
        "Fastest Time to 10K"
    )

    print("\n" + "=" * 70)
    print("TOP 10 BY LOWEST EFFORT (hours to 10K)")
    agent.print_results_table(
        agent.get_top_results("total_effort_hours_to_10k", 10, ascending=True),
        "Lowest Total Effort"
    )

    print("\n" + "=" * 70)
    print("TOP 10 BY HIGHEST ALGORITHM SCORE")
    agent.print_results_table(
        agent.get_top_results("algorithm_score", 10, ascending=False),
        "Highest Algorithm Alignment"
    )

    print("\n" + "=" * 70)
    print("TOP 10 BY EFFICIENCY (effort per follower)")
    agent.print_results_table(
        agent.get_top_results("effort_per_follower", 10, ascending=True),
        "Most Efficient (lowest hours per follower)"
    )

    # Pareto optimal
    pareto = agent.get_pareto_optimal()
    print("\n" + "=" * 70)
    print(f"PARETO-OPTIMAL CONFIGURATIONS ({len(pareto)} found)")
    print("(No configuration beats these in ALL of: time, effort, algorithm score)")
    agent.print_results_table(pareto, "Pareto-Optimal Set")

    return agent


if __name__ == "__main__":
    main()
