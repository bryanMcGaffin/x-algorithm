"""
Comparison & Optimization Agent

Reviews simulation results and finds theoretical optimal quantities
for rapid and sustained X account growth.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import math

from algorithm_model import (
    AlgorithmParams,
    AuthorDiversityModel,
    TimeConstraintsModel,
)
from testing_agent import TestingAgent, SimulationResult, TestConfiguration


@dataclass
class OptimalConfiguration:
    """An optimal configuration with its rationale."""
    name: str
    description: str

    # Configuration
    posts_per_day: int
    threads_per_week: int
    videos_per_week: int
    long_videos_per_week: int
    engagement_hours: float
    hours_between_posts: float

    # Outcomes
    days_to_10k: int
    total_effort_hours: float
    algorithm_score: float
    efficiency: float

    # Rationale
    why_optimal: List[str]
    tradeoffs: List[str]


@dataclass
class OptimizationReport:
    """Complete optimization analysis report."""
    fastest_config: OptimalConfiguration
    most_efficient_config: OptimalConfiguration
    balanced_config: OptimalConfiguration
    sustainable_config: OptimalConfiguration

    # Theoretical limits
    absolute_minimum_days: int
    minimum_effort_hours: float

    # Key findings
    findings: List[str]
    recommendations: List[str]

    # Algorithm insights
    diversity_sweet_spot: int
    engagement_sweet_spot: float
    content_mix_optimal: Dict[str, int]


class OptimizationAgent:
    """
    Analyzes test results to find optimal configurations.

    Objectives:
    1. Fastest time to 10K (minimize calendar days)
    2. Most efficient (minimize total effort hours)
    3. Best balanced (optimize time × effort)
    4. Most sustainable (maintainable long-term)
    """

    def __init__(self, params: AlgorithmParams = None):
        self.params = params or AlgorithmParams()
        self.diversity_model = AuthorDiversityModel(self.params)
        self.time_model = TimeConstraintsModel(self.params)

    def analyze_results(
        self,
        results: List[SimulationResult],
    ) -> OptimizationReport:
        """
        Analyze simulation results to find optimal configurations.
        """
        if not results:
            raise ValueError("No results to analyze")

        # Find optimal by different criteria
        fastest = self._find_fastest(results)
        most_efficient = self._find_most_efficient(results)
        balanced = self._find_balanced(results)
        sustainable = self._find_sustainable(results)

        # Calculate theoretical limits
        absolute_min_days = self._calculate_absolute_minimum_days()
        min_effort = self._calculate_minimum_effort()

        # Generate findings
        findings = self._generate_findings(results, fastest, most_efficient, balanced)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            fastest, most_efficient, balanced, sustainable
        )

        # Algorithm insights
        diversity_sweet_spot = self._find_diversity_sweet_spot()
        engagement_sweet_spot = self._find_engagement_sweet_spot(results)
        content_mix = self._find_optimal_content_mix(results)

        return OptimizationReport(
            fastest_config=fastest,
            most_efficient_config=most_efficient,
            balanced_config=balanced,
            sustainable_config=sustainable,
            absolute_minimum_days=absolute_min_days,
            minimum_effort_hours=min_effort,
            findings=findings,
            recommendations=recommendations,
            diversity_sweet_spot=diversity_sweet_spot,
            engagement_sweet_spot=engagement_sweet_spot,
            content_mix_optimal=content_mix,
        )

    def _find_fastest(self, results: List[SimulationResult]) -> OptimalConfiguration:
        """Find configuration with fastest time to 10K."""
        fastest = min(results, key=lambda x: x.days_to_10k)

        return OptimalConfiguration(
            name="Fastest Growth",
            description="Minimizes calendar time to 10K followers",
            posts_per_day=fastest.posts_per_day,
            threads_per_week=fastest.threads_per_week,
            videos_per_week=fastest.videos_per_week,
            long_videos_per_week=fastest.long_videos_per_week,
            engagement_hours=fastest.engagement_hours,
            hours_between_posts=fastest.hours_between_posts,
            days_to_10k=fastest.days_to_10k,
            total_effort_hours=fastest.total_effort_hours_to_10k,
            algorithm_score=fastest.algorithm_score,
            efficiency=fastest.efficiency,
            why_optimal=[
                f"Reaches 10K in {fastest.days_to_10k} days ({fastest.days_to_10k//7} weeks)",
                f"High content volume ({fastest.posts_per_day} posts/day) with {fastest.efficiency:.0%} efficiency",
                f"Strong content mix: {fastest.threads_per_week} threads + {fastest.long_videos_per_week} long videos/week",
            ],
            tradeoffs=[
                f"Requires {fastest.total_effort_hours_to_10k:.0f} total hours of effort",
                f"Daily commitment: ~{fastest.total_effort_hours_to_10k/fastest.days_to_10k:.1f} hours/day",
                "High intensity may be difficult to sustain",
            ],
        )

    def _find_most_efficient(self, results: List[SimulationResult]) -> OptimalConfiguration:
        """Find configuration with lowest effort per follower."""
        # Filter out unreasonably slow configs
        viable = [r for r in results if r.days_to_10k < 300]
        most_efficient = min(viable, key=lambda x: x.effort_per_follower)

        return OptimalConfiguration(
            name="Most Efficient",
            description="Minimizes effort per follower gained",
            posts_per_day=most_efficient.posts_per_day,
            threads_per_week=most_efficient.threads_per_week,
            videos_per_week=most_efficient.videos_per_week,
            long_videos_per_week=most_efficient.long_videos_per_week,
            engagement_hours=most_efficient.engagement_hours,
            hours_between_posts=most_efficient.hours_between_posts,
            days_to_10k=most_efficient.days_to_10k,
            total_effort_hours=most_efficient.total_effort_hours_to_10k,
            algorithm_score=most_efficient.algorithm_score,
            efficiency=most_efficient.efficiency,
            why_optimal=[
                f"Only {most_efficient.effort_per_follower:.4f} hours per follower",
                f"Total effort: {most_efficient.total_effort_hours_to_10k:.0f} hours to 10K",
                f"High posting efficiency: {most_efficient.efficiency:.0%}",
            ],
            tradeoffs=[
                f"Takes {most_efficient.days_to_10k} days ({most_efficient.days_to_10k//7} weeks)",
                "Slower growth means longer time to monetization",
                "May lose momentum with lower volume",
            ],
        )

    def _find_balanced(self, results: List[SimulationResult]) -> OptimalConfiguration:
        """Find configuration that balances time and effort."""
        # Score = time_rank + effort_rank (lower is better)
        time_sorted = sorted(results, key=lambda x: x.days_to_10k)
        effort_sorted = sorted(results, key=lambda x: x.total_effort_hours_to_10k)

        combined_scores = []
        for r in results:
            time_rank = time_sorted.index(r)
            effort_rank = effort_sorted.index(r)
            # Weight time slightly higher
            score = time_rank * 1.2 + effort_rank
            combined_scores.append((score, r))

        balanced = min(combined_scores, key=lambda x: x[0])[1]

        return OptimalConfiguration(
            name="Balanced Growth",
            description="Optimal balance of speed and effort",
            posts_per_day=balanced.posts_per_day,
            threads_per_week=balanced.threads_per_week,
            videos_per_week=balanced.videos_per_week,
            long_videos_per_week=balanced.long_videos_per_week,
            engagement_hours=balanced.engagement_hours,
            hours_between_posts=balanced.hours_between_posts,
            days_to_10k=balanced.days_to_10k,
            total_effort_hours=balanced.total_effort_hours_to_10k,
            algorithm_score=balanced.algorithm_score,
            efficiency=balanced.efficiency,
            why_optimal=[
                f"Balanced: {balanced.days_to_10k} days with {balanced.total_effort_hours_to_10k:.0f} hours",
                f"Daily effort: ~{balanced.total_effort_hours_to_10k/balanced.days_to_10k:.1f} hours/day",
                f"Algorithm alignment: {balanced.algorithm_score}/100",
            ],
            tradeoffs=[
                "Not the absolute fastest option",
                "Not the absolute most efficient option",
                "Represents best compromise for most users",
            ],
        )

    def _find_sustainable(self, results: List[SimulationResult]) -> OptimalConfiguration:
        """Find configuration that's sustainable long-term."""
        # Sustainable = low daily effort + reasonable time
        viable = [r for r in results if r.days_to_10k < 200]

        for r in viable:
            r._daily_effort = r.total_effort_hours_to_10k / r.days_to_10k

        # Target 1.5-2.5 hours/day as sustainable
        sustainable_candidates = [
            r for r in viable
            if 1.0 <= r._daily_effort <= 2.5
        ]

        if sustainable_candidates:
            # Among sustainable, pick fastest
            sustainable = min(sustainable_candidates, key=lambda x: x.days_to_10k)
        else:
            # Fallback to lowest daily effort
            sustainable = min(viable, key=lambda x: x._daily_effort)

        return OptimalConfiguration(
            name="Sustainable Growth",
            description="Maintainable long-term with work/life balance",
            posts_per_day=sustainable.posts_per_day,
            threads_per_week=sustainable.threads_per_week,
            videos_per_week=sustainable.videos_per_week,
            long_videos_per_week=sustainable.long_videos_per_week,
            engagement_hours=sustainable.engagement_hours,
            hours_between_posts=sustainable.hours_between_posts,
            days_to_10k=sustainable.days_to_10k,
            total_effort_hours=sustainable.total_effort_hours_to_10k,
            algorithm_score=sustainable.algorithm_score,
            efficiency=sustainable.efficiency,
            why_optimal=[
                f"Only ~{sustainable._daily_effort:.1f} hours/day commitment",
                f"Achievable alongside other responsibilities",
                f"Reaches 10K in {sustainable.days_to_10k//7} weeks",
            ],
            tradeoffs=[
                "Takes longer than intensive approaches",
                "Lower volume means less viral lottery tickets",
                "Requires patience and consistency",
            ],
        )

    def _calculate_absolute_minimum_days(self) -> int:
        """Calculate theoretical minimum days to 10K."""
        constraints = self.time_model.get_minimum_calendar_days(10000)
        return constraints['total_minimum_days']

    def _calculate_minimum_effort(self) -> float:
        """Calculate theoretical minimum effort hours."""
        # Minimum: 1 post/day × 15 min + 30 min engagement + 15 min other
        min_daily = 0.25 + 0.5 + 0.25  # 1 hour
        min_days = self._calculate_absolute_minimum_days()
        return min_daily * min_days

    def _find_diversity_sweet_spot(self) -> int:
        """Find optimal posts per day before diminishing returns."""
        table = self.diversity_model.get_diminishing_returns_table(10)

        for posts, effective, marginal in table:
            if marginal < 0.35:  # Below 35% marginal value
                return posts - 1

        return 4  # Default

    def _find_engagement_sweet_spot(self, results: List[SimulationResult]) -> float:
        """Find optimal engagement hours."""
        # Group by engagement hours, find which produces best avg days_to_10k
        by_engagement = {}
        for r in results:
            eng = r.engagement_hours
            if eng not in by_engagement:
                by_engagement[eng] = []
            by_engagement[eng].append(r.days_to_10k)

        best_eng = None
        best_avg = float('inf')

        for eng, days_list in by_engagement.items():
            avg = sum(days_list) / len(days_list)
            if avg < best_avg:
                best_avg = avg
                best_eng = eng

        return best_eng or 1.0

    def _find_optimal_content_mix(self, results: List[SimulationResult]) -> Dict[str, int]:
        """Find optimal content mix."""
        # Find config with best algorithm score among fast growers
        fast = [r for r in results if r.days_to_10k < 100]
        if not fast:
            fast = sorted(results, key=lambda x: x.days_to_10k)[:20]

        best = max(fast, key=lambda x: x.algorithm_score)

        return {
            "posts_per_day": best.posts_per_day,
            "threads_per_week": best.threads_per_week,
            "videos_per_week": best.videos_per_week,
            "long_videos_per_week": best.long_videos_per_week,
        }

    def _generate_findings(
        self,
        results: List[SimulationResult],
        fastest: OptimalConfiguration,
        efficient: OptimalConfiguration,
        balanced: OptimalConfiguration,
    ) -> List[str]:
        """Generate key findings from analysis."""
        findings = []

        # Diversity finding
        posts_3 = [r for r in results if r.posts_per_day == 3]
        posts_4 = [r for r in results if r.posts_per_day == 4]
        posts_6 = [r for r in results if r.posts_per_day == 6]

        if posts_3 and posts_4 and posts_6:
            avg_3 = sum(r.efficiency for r in posts_3) / len(posts_3)
            avg_4 = sum(r.efficiency for r in posts_4) / len(posts_4)
            avg_6 = sum(r.efficiency for r in posts_6) / len(posts_6)

            findings.append(
                f"📊 Diversity Penalty Impact: 3 posts={avg_3:.0%} eff, "
                f"4 posts={avg_4:.0%} eff, 6 posts={avg_6:.0%} eff"
            )

        # Time floor finding
        min_days = min(r.days_to_10k for r in results)
        findings.append(
            f"⏱️  Absolute Time Floor: {min_days} days ({min_days//7} weeks) "
            f"regardless of effort intensity"
        )

        # Engagement finding
        low_eng = [r for r in results if r.engagement_hours <= 0.5]
        high_eng = [r for r in results if r.engagement_hours >= 1.5]

        if low_eng and high_eng:
            avg_low = sum(r.days_to_10k for r in low_eng) / len(low_eng)
            avg_high = sum(r.days_to_10k for r in high_eng) / len(high_eng)
            diff = ((avg_low - avg_high) / avg_low) * 100

            findings.append(
                f"💬 Engagement Impact: High engagement (1.5+ hrs) reaches 10K "
                f"{diff:.0f}% faster than low engagement (0.5 hrs)"
            )

        # Content type finding
        with_threads = [r for r in results if r.threads_per_week >= 2]
        without_threads = [r for r in results if r.threads_per_week == 0]

        if with_threads and without_threads:
            avg_with = sum(r.days_to_10k for r in with_threads) / len(with_threads)
            avg_without = sum(r.days_to_10k for r in without_threads) / len(without_threads)

            findings.append(
                f"📝 Thread Impact: 2+ threads/week = avg {avg_with:.0f} days vs "
                f"{avg_without:.0f} days without"
            )

        # Video finding
        with_long_vids = [r for r in results if r.long_videos_per_week >= 2]
        without_vids = [r for r in results if r.videos_per_week == 0]

        if with_long_vids and without_vids:
            avg_with = sum(r.algorithm_score for r in with_long_vids) / len(with_long_vids)
            avg_without = sum(r.algorithm_score for r in without_vids) / len(without_vids)

            findings.append(
                f"🎥 Video Impact: Long videos boost algorithm score by "
                f"+{avg_with - avg_without:.0f} points on average"
            )

        return findings

    def _generate_recommendations(
        self,
        fastest: OptimalConfiguration,
        efficient: OptimalConfiguration,
        balanced: OptimalConfiguration,
        sustainable: OptimalConfiguration,
    ) -> List[str]:
        """Generate actionable recommendations."""
        return [
            f"🚀 For fastest growth: {fastest.posts_per_day} posts/day, "
            f"{fastest.threads_per_week} threads, {fastest.engagement_hours}h engagement "
            f"→ {fastest.days_to_10k} days",

            f"💡 For efficiency: {efficient.posts_per_day} posts/day is optimal - "
            f"more posts have diminishing returns due to diversity penalty",

            f"⚖️  Balanced recommendation: {balanced.posts_per_day} posts + "
            f"{balanced.threads_per_week} threads + {balanced.long_videos_per_week} long videos/week",

            f"🌱 For sustainability: {sustainable.posts_per_day} posts/day with "
            f"{sustainable.engagement_hours}h engagement = only "
            f"~{sustainable.total_effort_hours/sustainable.days_to_10k:.1f}h/day",

            f"📈 Optimal posting cadence: 3-4 posts/day spaced 4+ hours apart",

            f"🎯 Content mix for algorithm: {balanced.threads_per_week} threads + "
            f"{balanced.long_videos_per_week} long videos (>45s) per week minimum",
        ]

    def print_report(self, report: OptimizationReport):
        """Print the optimization report."""
        print("\n" + "=" * 80)
        print("X ALGORITHM OPTIMIZATION REPORT")
        print("Theoretical Optimal Configurations for 0→10K Growth")
        print("=" * 80)

        # Theoretical limits
        print(f"\n📊 THEORETICAL LIMITS")
        print(f"   Absolute minimum calendar time: {report.absolute_minimum_days} days")
        print(f"   Minimum total effort: {report.minimum_effort_hours:.0f} hours")

        # Algorithm insights
        print(f"\n🔬 ALGORITHM INSIGHTS")
        print(f"   Diversity sweet spot: {report.diversity_sweet_spot} posts/day")
        print(f"   Engagement sweet spot: {report.engagement_sweet_spot} hours/day")
        print(f"   Optimal content mix:")
        for k, v in report.content_mix_optimal.items():
            print(f"      - {k}: {v}")

        # Configurations
        configs = [
            report.fastest_config,
            report.most_efficient_config,
            report.balanced_config,
            report.sustainable_config,
        ]

        for config in configs:
            print(f"\n{'='*80}")
            print(f"🎯 {config.name.upper()}")
            print(f"   {config.description}")
            print(f"{'='*80}")

            print(f"\n   Configuration:")
            print(f"   • Posts/day: {config.posts_per_day}")
            print(f"   • Threads/week: {config.threads_per_week}")
            print(f"   • Videos/week: {config.videos_per_week} ({config.long_videos_per_week} long)")
            print(f"   • Engagement: {config.engagement_hours} hours/day")
            print(f"   • Post spacing: {config.hours_between_posts} hours")

            print(f"\n   Outcomes:")
            print(f"   • Days to 10K: {config.days_to_10k} ({config.days_to_10k//7} weeks)")
            print(f"   • Total effort: {config.total_effort_hours:.0f} hours")
            print(f"   • Algorithm score: {config.algorithm_score}/100")
            print(f"   • Efficiency: {config.efficiency:.0%}")

            print(f"\n   Why optimal:")
            for reason in config.why_optimal:
                print(f"   ✓ {reason}")

            print(f"\n   Tradeoffs:")
            for tradeoff in config.tradeoffs:
                print(f"   • {tradeoff}")

        # Key findings
        print(f"\n{'='*80}")
        print("📋 KEY FINDINGS")
        print("=" * 80)
        for finding in report.findings:
            print(f"   {finding}")

        # Recommendations
        print(f"\n{'='*80}")
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        for rec in report.recommendations:
            print(f"   {rec}")

        # Summary table
        print(f"\n{'='*80}")
        print("📊 SUMMARY COMPARISON")
        print("=" * 80)
        print(f"\n{'Strategy':<20} {'Posts':<8} {'Threads':<8} {'Videos':<8} "
              f"{'Engage':<8} {'Days':<8} {'Hours':<8}")
        print("-" * 80)

        for config in configs:
            print(
                f"{config.name:<20} "
                f"{config.posts_per_day:<8} "
                f"{config.threads_per_week:<8} "
                f"{config.long_videos_per_week:<8} "
                f"{config.engagement_hours:<8} "
                f"{config.days_to_10k:<8} "
                f"{config.total_effort_hours:<8.0f}"
            )


def run_full_optimization():
    """Run complete optimization analysis."""
    print("\n" + "=" * 80)
    print("RUNNING FULL X ALGORITHM OPTIMIZATION")
    print("=" * 80)

    # Step 1: Run testing agent
    print("\n📊 Step 1: Running simulations...")
    testing_agent = TestingAgent()
    configs = testing_agent.generate_focused_grid()
    results = testing_agent.run_test_suite(configs, num_runs=3)

    print(f"   Completed {len(results)} simulations")

    # Step 2: Run optimization analysis
    print("\n🔬 Step 2: Analyzing results...")
    opt_agent = OptimizationAgent()
    report = opt_agent.analyze_results(results)

    # Step 3: Print report
    print("\n📋 Step 3: Generating report...")
    opt_agent.print_report(report)

    return report


def main():
    """Run the optimization agent."""
    report = run_full_optimization()
    return report


if __name__ == "__main__":
    main()
