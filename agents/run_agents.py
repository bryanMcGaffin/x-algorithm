#!/usr/bin/env python3
"""
X Algorithm Agent Runner

Unified runner for all volume analysis agents:
1. Volume Analyst - Analyzes suggested schedules against algorithm
2. Testing Agent - Simulates different configurations
3. Optimization Agent - Finds theoretical optimal quantities

Usage:
    python run_agents.py [--mode MODE] [--target FOLLOWERS]

Modes:
    analyze  - Run volume analyst on playbook schedules
    test     - Run testing agent simulations
    optimize - Run full optimization analysis (default)
    all      - Run all agents sequentially
"""

import argparse
import sys
from datetime import datetime

# Import agents
from algorithm_model import AlgorithmParams, print_diversity_analysis, print_time_constraints
from volume_analyst import VolumeAnalystAgent, get_playbook_schedules
from testing_agent import TestingAgent
from optimization_agent import OptimizationAgent, run_full_optimization


def run_analyze_mode(target: int = 10000):
    """Run volume analysis on playbook schedules."""
    print("\n" + "=" * 80)
    print("MODE: VOLUME ANALYSIS")
    print(f"Analyzing playbook schedules against X algorithm (target: {target:,} followers)")
    print("=" * 80)

    agent = VolumeAnalystAgent()
    schedules = get_playbook_schedules()

    results = agent.compare_schedules(schedules, target_followers=target)

    for analysis in results:
        agent.print_analysis(analysis)

    # Summary
    print("\n" + "=" * 80)
    print("RANKING BY ALGORITHM ALIGNMENT")
    print("=" * 80)
    print(f"\n{'Rank':<6} {'Schedule':<30} {'Score':<10} {'Days':<10} {'Effort':<10}")
    print("-" * 80)

    for i, a in enumerate(results, 1):
        print(
            f"{i:<6} "
            f"{a.schedule_name:<30} "
            f"{a.algorithm_alignment_score:<10} "
            f"{a.calendar_days_to_10k:<10} "
            f"{a.total_effort_hours:.1f} hrs"
        )

    return results


def run_test_mode(target: int = 10000):
    """Run testing agent simulations."""
    print("\n" + "=" * 80)
    print("MODE: SIMULATION TESTING")
    print(f"Testing volume configurations (target: {target:,} followers)")
    print("=" * 80)

    agent = TestingAgent()
    configs = agent.generate_focused_grid()

    print(f"\n🧪 Generated {len(configs)} test configurations")
    print("   Running simulations with 3 runs per config for averaging...")

    results = agent.run_test_suite(configs, num_runs=3)

    # Print results by different metrics
    print("\n" + "=" * 80)
    print("TOP 10 FASTEST TO 10K")
    agent.print_results_table(
        agent.get_top_results("days_to_10k", 10, ascending=True),
        "Fastest Configurations"
    )

    print("\n" + "=" * 80)
    print("TOP 10 MOST EFFICIENT")
    agent.print_results_table(
        agent.get_top_results("effort_per_follower", 10, ascending=True),
        "Most Efficient Configurations"
    )

    print("\n" + "=" * 80)
    print("TOP 10 HIGHEST ALGORITHM SCORE")
    agent.print_results_table(
        agent.get_top_results("algorithm_score", 10, ascending=False),
        "Best Algorithm Alignment"
    )

    # Pareto optimal
    pareto = agent.get_pareto_optimal()
    print("\n" + "=" * 80)
    print(f"PARETO-OPTIMAL SET ({len(pareto)} configurations)")
    agent.print_results_table(pareto, "Pareto-Optimal")

    return results


def run_optimize_mode(target: int = 10000):
    """Run full optimization analysis."""
    print("\n" + "=" * 80)
    print("MODE: OPTIMIZATION")
    print(f"Finding theoretical optimal quantities (target: {target:,} followers)")
    print("=" * 80)

    report = run_full_optimization()
    return report


def run_all_modes(target: int = 10000):
    """Run all agents sequentially."""
    print("\n" + "=" * 80)
    print("MODE: FULL ANALYSIS")
    print(f"Running all agents (target: {target:,} followers)")
    print("=" * 80)

    # Algorithm fundamentals
    print("\n\n" + "=" * 80)
    print("PART 1: ALGORITHM FUNDAMENTALS")
    print("=" * 80)
    params = AlgorithmParams()
    print_diversity_analysis(params)
    print_time_constraints(target, params)

    # Volume analysis
    print("\n\n" + "=" * 80)
    print("PART 2: PLAYBOOK SCHEDULE ANALYSIS")
    print("=" * 80)
    analyze_results = run_analyze_mode(target)

    # Testing
    print("\n\n" + "=" * 80)
    print("PART 3: SIMULATION TESTING")
    print("=" * 80)
    test_results = run_test_mode(target)

    # Optimization
    print("\n\n" + "=" * 80)
    print("PART 4: OPTIMIZATION ANALYSIS")
    print("=" * 80)
    opt_report = run_optimize_mode(target)

    # Final summary
    print("\n\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    print("\n📊 THEORETICAL OPTIMAL CONFIGURATION:")
    print(f"   Posts per day: {opt_report.content_mix_optimal['posts_per_day']}")
    print(f"   Threads per week: {opt_report.content_mix_optimal['threads_per_week']}")
    print(f"   Long videos per week: {opt_report.content_mix_optimal['long_videos_per_week']}")
    print(f"   Engagement hours: {opt_report.engagement_sweet_spot}")
    print(f"\n   Minimum calendar time: {opt_report.absolute_minimum_days} days "
          f"({opt_report.absolute_minimum_days // 7} weeks)")

    print("\n🎯 RECOMMENDED CONFIGURATIONS BY GOAL:")
    print(f"   • Fastest: {opt_report.fastest_config.days_to_10k} days / "
          f"{opt_report.fastest_config.total_effort_hours:.0f} hrs total")
    print(f"   • Most Efficient: {opt_report.most_efficient_config.days_to_10k} days / "
          f"{opt_report.most_efficient_config.total_effort_hours:.0f} hrs total")
    print(f"   • Balanced: {opt_report.balanced_config.days_to_10k} days / "
          f"{opt_report.balanced_config.total_effort_hours:.0f} hrs total")
    print(f"   • Sustainable: {opt_report.sustainable_config.days_to_10k} days / "
          f"{opt_report.sustainable_config.total_effort_hours:.0f} hrs total")

    return {
        'analyze': analyze_results,
        'test': test_results,
        'optimize': opt_report,
    }


def main():
    parser = argparse.ArgumentParser(
        description="X Algorithm Volume Analysis Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_agents.py --mode analyze
    python run_agents.py --mode test
    python run_agents.py --mode optimize
    python run_agents.py --mode all --target 10000
        """
    )

    parser.add_argument(
        '--mode',
        choices=['analyze', 'test', 'optimize', 'all'],
        default='optimize',
        help='Which agent(s) to run (default: optimize)'
    )

    parser.add_argument(
        '--target',
        type=int,
        default=10000,
        help='Target follower count (default: 10000)'
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("X ALGORITHM VOLUME ANALYSIS AGENT SYSTEM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if args.mode == 'analyze':
        return run_analyze_mode(args.target)
    elif args.mode == 'test':
        return run_test_mode(args.target)
    elif args.mode == 'optimize':
        return run_optimize_mode(args.target)
    elif args.mode == 'all':
        return run_all_modes(args.target)


if __name__ == "__main__":
    main()
