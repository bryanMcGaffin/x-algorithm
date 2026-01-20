"""
Content Growth Orchestrator

The master controller that orchestrates all agents into a self-improving
content growth system. This is the brain that:
- Coordinates all generators and analyzers
- Implements the feedback loop
- Drives exponential improvement over time
- Adapts strategy based on results
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import os

# Content generators
from content_generators.base_generator import NicheProfile, TrendData, ContentPiece
from content_generators.post_generator import PostGeneratorAgent
from content_generators.thread_generator import ThreadGeneratorAgent
from content_generators.video_script_generator import VideoScriptAgent
from content_generators.reply_generator import ReplyGeneratorAgent
from content_generators.hook_generator import HookGeneratorAgent
from content_generators.image_prompt_generator import ImagePromptAgent

# Analyzers
from analyzers.trend_analyzer import TrendAnalyzerAgent
from analyzers.performance_analyzer import PerformanceAnalyzerAgent, ContentPerformance
from analyzers.niche_analyzer import NicheAnalyzerAgent
from analyzers.virality_predictor import ViralityPredictorAgent
from analyzers.cross_tester import CrossTestingAgent
from analyzers.result_analyzer import ResultAnalyzerAgent, ContentResult

# Optimal values
from optimal_values import (
    CONTENT_OPTIMAL_VALUES, ENGAGEMENT_OPTIMAL_VALUES,
    DailyOptimalSchedule, get_optimal_schedule, ContentType
)


@dataclass
class DailyContentPlan:
    """A complete daily content plan."""
    date: str
    generated_at: datetime

    # Content pieces
    posts: List[ContentPiece]
    threads: List[ContentPiece]
    videos: List[ContentPiece]
    replies: List[ContentPiece]

    # Schedule
    posting_schedule: List[Dict[str, Any]]

    # Engagement plan
    engagement_targets: List[str]
    engagement_hours: float

    # A/B tests active
    active_tests: List[str]

    # Predictions
    predicted_impressions: int
    predicted_engagements: int
    predicted_follows: int

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "content_summary": {
                "posts": len(self.posts),
                "threads": len(self.threads),
                "videos": len(self.videos),
                "replies": len(self.replies),
            },
            "posting_schedule": self.posting_schedule,
            "engagement_plan": {
                "targets": len(self.engagement_targets),
                "hours": self.engagement_hours,
            },
            "predictions": {
                "impressions": self.predicted_impressions,
                "engagements": self.predicted_engagements,
                "follows": self.predicted_follows,
            },
        }


@dataclass
class SystemState:
    """Current state of the growth system."""
    current_followers: int
    goal_followers: int
    days_active: int

    # Performance metrics
    total_impressions: int
    total_engagements: int
    total_content_posted: int

    # Learning metrics
    prediction_accuracy: float
    top_performing_types: List[str]
    top_performing_topics: List[str]

    # Progress
    days_to_goal: Optional[int]
    on_track: bool
    growth_rate: float


class ContentGrowthOrchestrator:
    """
    Master orchestrator for the content growth system.

    Responsibilities:
    1. Initialize and coordinate all agents
    2. Generate daily content plans
    3. Process results and update all agents
    4. Drive continuous optimization
    5. Track progress toward goals
    """

    def __init__(
        self,
        niche_name: str,
        niche_keywords: List[str],
        target_audience: List[str],
        follower_goal: int = 10000,
        starting_followers: int = 0,
        handle: str = "your_handle"
    ):
        """
        Initialize the orchestrator.

        Args:
            niche_name: Primary niche (e.g., "AI/Machine Learning")
            niche_keywords: Key topics in niche
            target_audience: Target audience segments
            follower_goal: Follower goal (default 10K)
            starting_followers: Current follower count
            handle: X handle
        """
        self.handle = handle
        self.follower_goal = follower_goal

        # Create niche profile
        self.niche = NicheProfile(
            name=niche_name,
            description=f"Content about {niche_name}",
            primary_topics=niche_keywords[:5],
            secondary_topics=niche_keywords[5:10] if len(niche_keywords) > 5 else [],
            tone="professional",
            target_audience=target_audience,
            hashtags=[kw.lower().replace(" ", "") for kw in niche_keywords[:5]],
            keywords=niche_keywords,
        )

        # Initialize content generators
        self.post_generator = PostGeneratorAgent(self.niche)
        self.thread_generator = ThreadGeneratorAgent(self.niche, handle)
        self.video_generator = VideoScriptAgent(self.niche)
        self.reply_generator = ReplyGeneratorAgent(self.niche)
        self.hook_generator = HookGeneratorAgent(self.niche)
        self.image_generator = ImagePromptAgent(self.niche)

        # Initialize analyzers
        self.trend_analyzer = TrendAnalyzerAgent(niche_keywords)
        self.performance_analyzer = PerformanceAnalyzerAgent()
        self.niche_analyzer = NicheAnalyzerAgent(niche_name, niche_keywords)
        self.virality_predictor = ViralityPredictorAgent(niche_keywords)
        self.cross_tester = CrossTestingAgent()
        self.result_analyzer = ResultAnalyzerAgent(follower_goal, starting_followers)

        # State tracking
        self.start_date = datetime.now()
        self.daily_plans: List[DailyContentPlan] = []
        self.optimization_history: List[Dict[str, Any]] = []

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the system with baseline analysis.

        Returns:
            Initialization report
        """
        # Analyze niche
        niche_report = self.niche_analyzer.analyze()

        # Get initial trends
        trend_report = self.trend_analyzer.analyze_trends()

        # Update generators with trend data
        trend_data = TrendData(
            trending_topics=trend_report.trending_topics if hasattr(trend_report, 'trending_topics') else [],
            trending_hashtags=[h["hashtag"] for h in trend_report.top_hashtags],
            viral_formats=[p.pattern_type for p in self.trend_analyzer.get_viral_patterns()[:3]],
            current_events=[],
            seasonal_relevance=[],
            competitor_activity=trend_report.competitor_trends,
        )

        self.post_generator.update_trends(trend_data)
        self.thread_generator.update_trends(trend_data)
        self.video_generator.update_trends(trend_data)

        return {
            "status": "initialized",
            "niche_analysis": niche_report.to_dict(),
            "trend_analysis": trend_report.to_dict(),
            "ready_to_generate": True,
        }

    def generate_daily_plan(
        self,
        strategy: str = "maximum",
        date: str = None
    ) -> DailyContentPlan:
        """
        Generate a complete daily content plan.

        Args:
            strategy: "maximum", "efficient", or "sustainable"
            date: Date for plan (default: today)

        Returns:
            DailyContentPlan
        """
        date = date or datetime.now().strftime("%Y-%m-%d")
        schedule = get_optimal_schedule(strategy)

        # Get fresh trends
        trend_report = self.trend_analyzer.analyze_trends()

        # Generate posts
        posts = self.post_generator.generate(
            count=int(schedule.text_posts + schedule.image_posts),
            include_image=True
        )

        # Generate threads
        threads = []
        if schedule.threads >= 0.5:  # At least half a thread per day = include
            threads = self.thread_generator.generate(count=1)

        # Generate videos
        videos = []
        if schedule.video_short + schedule.video_long >= 1:
            if schedule.video_long >= 0.5:
                videos.append(self.video_generator.generate_long_video())
            if schedule.video_short >= 1:
                videos.append(self.video_generator.generate_short_video())

        # Generate reply templates
        replies = self.reply_generator.generate(count=min(5, schedule.replies))

        # Predict virality for each piece
        all_content = posts + threads + videos
        for content in all_content:
            viral_score = self.virality_predictor.predict(
                content=content.get_full_text(),
                content_type=content.content_type,
                topics=content.topics_used,
            )
            content.confidence_score = viral_score.probability
            content.predicted_engagement_rate = viral_score.probability * 0.08  # Rough conversion

        # Create posting schedule
        posting_schedule = self._create_posting_schedule(posts, threads, videos)

        # Calculate predictions
        total_predicted_impressions = sum(
            self._estimate_impressions(c) for c in all_content
        )
        total_predicted_engagements = sum(
            self._estimate_impressions(c) * c.predicted_engagement_rate
            for c in all_content
        )
        total_predicted_follows = int(total_predicted_engagements * 0.02)

        plan = DailyContentPlan(
            date=date,
            generated_at=datetime.now(),
            posts=posts,
            threads=threads,
            videos=videos,
            replies=replies,
            posting_schedule=posting_schedule,
            engagement_targets=self._get_engagement_targets(trend_report),
            engagement_hours=schedule.engagement_hours,
            active_tests=[t.name for t in self.cross_tester.get_active_tests()],
            predicted_impressions=int(total_predicted_impressions),
            predicted_engagements=int(total_predicted_engagements),
            predicted_follows=total_predicted_follows,
        )

        self.daily_plans.append(plan)
        return plan

    def _create_posting_schedule(
        self,
        posts: List[ContentPiece],
        threads: List[ContentPiece],
        videos: List[ContentPiece]
    ) -> List[Dict[str, Any]]:
        """Create optimal posting schedule."""
        schedule = []
        optimal_hours = [9, 12, 15, 18, 21]  # UTC

        all_content = []
        for post in posts:
            all_content.append(("post", post))
        for thread in threads:
            all_content.append(("thread", thread))
        for video in videos:
            all_content.append(("video", video))

        # Distribute across optimal hours
        for i, (content_type, content) in enumerate(all_content):
            hour = optimal_hours[i % len(optimal_hours)]
            schedule.append({
                "time": f"{hour:02d}:00 UTC",
                "content_type": content_type,
                "content_preview": content.main_text[:50] + "...",
                "predicted_engagement": f"{content.predicted_engagement_rate:.2%}",
            })

        # Sort by time
        schedule.sort(key=lambda x: x["time"])
        return schedule

    def _get_engagement_targets(self, trend_report) -> List[str]:
        """Get engagement targets based on trends."""
        targets = []

        # Target trending content creators
        for comp in trend_report.competitor_trends[:3]:
            targets.append(f"Engage with @{comp['handle']}'s content")

        # Target trending topics
        for trend in trend_report.hot_trends[:3]:
            targets.append(f"Reply to posts about '{trend.name}'")

        return targets

    def _estimate_impressions(self, content: ContentPiece) -> int:
        """Estimate impressions for content."""
        base_impressions = {
            "text_post": 500,
            "image_post": 800,
            "video_short": 1200,
            "video_long": 2000,
            "thread": 3000,
        }
        base = base_impressions.get(content.content_type, 500)

        # Adjust by algorithm alignment
        multiplier = 0.5 + content.algorithm_alignment_score

        return int(base * multiplier)

    def record_content_result(
        self,
        content_id: str,
        content: ContentPiece,
        actual_metrics: Dict[str, int]
    ):
        """
        Record actual results for content.

        Args:
            content_id: Unique identifier
            content: Original content piece
            actual_metrics: Dict with impressions, engagements, follows, etc.
        """
        # Create result object
        result = ContentResult(
            content_id=content_id,
            content_type=content.content_type,
            format_type=content.format_type,
            topics=content.topics_used,
            posted_at=datetime.now(),
            content_text=content.main_text[:200],
            predicted_engagement_rate=content.predicted_engagement_rate,
            predicted_viral_score=content.confidence_score,
            predicted_dwell_time=content.predicted_dwell_time,
            algorithm_alignment_score=content.algorithm_alignment_score,
            actual_impressions=actual_metrics.get("impressions", 0),
            actual_engagements=actual_metrics.get("engagements", 0),
            actual_follows=actual_metrics.get("follows", 0),
        )

        # Record in analyzers
        self.result_analyzer.record_result(result)

        perf = ContentPerformance(
            content_id=content_id,
            content_type=content.content_type,
            format_type=content.format_type,
            topics=content.topics_used,
            posted_at=datetime.now(),
            text_preview=content.main_text[:100],
            impressions=actual_metrics.get("impressions", 0),
            likes=actual_metrics.get("likes", 0),
            replies=actual_metrics.get("replies", 0),
            retweets=actual_metrics.get("retweets", 0),
            quotes=actual_metrics.get("quotes", 0),
            bookmarks=actual_metrics.get("bookmarks", 0),
            profile_clicks=actual_metrics.get("profile_clicks", 0),
            follows=actual_metrics.get("follows", 0),
        )
        self.performance_analyzer.record_performance(perf)

        # Update generators with feedback
        self._update_generators_from_result(result)

    def _update_generators_from_result(self, result: ContentResult):
        """Update all generators based on result."""
        # Update virality predictor
        self.virality_predictor.record_actual_performance(
            result.content_text,
            self.virality_predictor.predict(result.content_text),
            result.actual_engagement_rate
        )

        # Update topic weights in generators
        for topic in result.topics:
            if result.performance_vs_expected == "above":
                self.post_generator.topic_weights[topic] = \
                    self.post_generator.topic_weights.get(topic, 1.0) * 1.1
            elif result.performance_vs_expected == "below":
                self.post_generator.topic_weights[topic] = \
                    self.post_generator.topic_weights.get(topic, 1.0) * 0.9

    def run_optimization_cycle(self) -> Dict[str, Any]:
        """
        Run a full optimization cycle.

        This is the key function for exponential improvement:
        1. Analyze recent results
        2. Generate optimization recommendations
        3. Update all agent parameters
        4. Generate improvement report

        Returns:
            Optimization report
        """
        # Analyze results
        result_report = self.result_analyzer.analyze(period_days=7)
        performance_report = self.performance_analyzer.analyze(period_days=7)

        if not result_report or result_report.total_content_analyzed == 0:
            return {"status": "insufficient_data", "message": "Need more content data"}

        # Get optimizations
        optimizations = result_report.optimizations

        # Apply optimizations to generators
        self._apply_optimizations(optimizations)

        # Record optimization
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "changes": {
                "creativity_factor": optimizations.creativity_factor_adjustment,
                "trend_weight": optimizations.trend_weight_adjustment,
                "top_content_types": list(optimizations.content_type_weights.keys())[:3],
                "top_topics": optimizations.recommended_engagement_focus[:3],
            },
            "metrics_before": {
                "engagement_rate": f"{result_report.overall_engagement_rate:.2%}",
                "growth_rate": f"{result_report.growth_rate_per_day:.1f}/day",
            },
        }
        self.optimization_history.append(optimization_record)

        return {
            "status": "optimized",
            "result_analysis": result_report.to_dict(),
            "recommendations": [
                {"rec": r.recommendation, "impact": r.impact_estimate}
                for r in result_report.recommendations[:5]
            ],
            "optimizations_applied": optimization_record["changes"],
            "progress": {
                "current_followers": result_report.current_followers,
                "goal": result_report.goal_followers,
                "days_to_goal": result_report.days_to_goal,
                "on_track": result_report.on_track,
            },
        }

    def _apply_optimizations(self, optimizations):
        """Apply optimizations to all generators."""
        # Update creativity factor
        for gen in [self.post_generator, self.thread_generator, self.video_generator]:
            gen.creativity_factor = max(0.1, min(0.8,
                gen.creativity_factor + optimizations.creativity_factor_adjustment
            ))
            gen.trend_weight = max(0.1, min(0.8,
                gen.trend_weight + optimizations.trend_weight_adjustment
            ))

        # Update topic weights
        for topic, weight in optimizations.topic_weights.items():
            self.post_generator.topic_weights[topic] = weight
            self.thread_generator.topic_weights[topic] = weight

        # Update format weights
        for format_type, weight in optimizations.format_weights.items():
            self.post_generator.format_weights[format_type] = weight

        # Update niche best performing data
        self.niche.best_performing_topics = optimizations.topic_weights
        self.niche.best_posting_times = optimizations.recommended_posting_times

    def get_system_state(self) -> SystemState:
        """Get current system state."""
        result_report = self.result_analyzer.analyze(period_days=30)

        days_active = (datetime.now() - self.start_date).days

        return SystemState(
            current_followers=self.result_analyzer.current_followers,
            goal_followers=self.follower_goal,
            days_active=days_active,
            total_impressions=sum(r.actual_impressions for r in self.result_analyzer.content_results),
            total_engagements=sum(r.actual_engagements for r in self.result_analyzer.content_results),
            total_content_posted=len(self.result_analyzer.content_results),
            prediction_accuracy=1 - (result_report.avg_prediction_error if result_report else 0),
            top_performing_types=list(result_report.optimizations.content_type_weights.keys())[:3] if result_report else [],
            top_performing_topics=result_report.optimizations.recommended_engagement_focus[:3] if result_report else [],
            days_to_goal=result_report.days_to_goal if result_report else None,
            on_track=result_report.on_track if result_report else False,
            growth_rate=result_report.growth_rate_per_day if result_report else 0,
        )

    def export_state(self, filepath: str):
        """Export system state for persistence."""
        state = {
            "niche": self.niche.to_dict(),
            "result_analyzer": self.result_analyzer.export_state(),
            "post_generator": self.post_generator.export_state(),
            "thread_generator": self.thread_generator.export_state(),
            "optimization_history": self.optimization_history,
            "start_date": self.start_date.isoformat(),
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def import_state(self, filepath: str):
        """Import system state from persistence."""
        with open(filepath, 'r') as f:
            state = json.load(f)

        if "result_analyzer" in state:
            self.result_analyzer.import_state(state["result_analyzer"])

        if "post_generator" in state:
            self.post_generator.import_state(state["post_generator"])

        if "thread_generator" in state:
            self.thread_generator.import_state(state["thread_generator"])

        if "optimization_history" in state:
            self.optimization_history = state["optimization_history"]

        if "start_date" in state:
            self.start_date = datetime.fromisoformat(state["start_date"])

    def get_quick_start_guide(self) -> str:
        """Get quick start guide for using the system."""
        return """
# Content Growth System - Quick Start Guide

## 1. Initialize
```python
from orchestrator import ContentGrowthOrchestrator

system = ContentGrowthOrchestrator(
    niche_name="Your Niche",
    niche_keywords=["keyword1", "keyword2", "keyword3"],
    target_audience=["audience1", "audience2"],
    follower_goal=10000,
    starting_followers=0,
    handle="your_handle"
)

init_report = system.initialize()
```

## 2. Generate Daily Content Plan
```python
plan = system.generate_daily_plan(strategy="maximum")

# Access content
for post in plan.posts:
    print(post.get_full_text())

for thread in plan.threads:
    print("Thread:", thread.main_text)
    for tweet in thread.thread_continuation:
        print("  -", tweet)
```

## 3. Record Results (After Posting)
```python
system.record_content_result(
    content_id="unique_id",
    content=plan.posts[0],
    actual_metrics={
        "impressions": 1000,
        "engagements": 50,
        "likes": 30,
        "replies": 10,
        "retweets": 5,
        "follows": 3,
    }
)
```

## 4. Run Optimization Cycle (Weekly)
```python
optimization = system.run_optimization_cycle()
print(optimization["recommendations"])
```

## 5. Check Progress
```python
state = system.get_system_state()
print(f"Followers: {state.current_followers}/{state.goal_followers}")
print(f"Days to goal: {state.days_to_goal}")
print(f"On track: {state.on_track}")
```

## 6. Save/Load State
```python
system.export_state("growth_system_state.json")
system.import_state("growth_system_state.json")
```
"""


def main():
    """Demo the orchestrator."""
    print("=" * 70)
    print("CONTENT GROWTH ORCHESTRATOR - DEMO")
    print("=" * 70)

    # Initialize system
    system = ContentGrowthOrchestrator(
        niche_name="AI/Machine Learning",
        niche_keywords=[
            "artificial intelligence", "machine learning", "deep learning",
            "neural networks", "data science", "AI tools", "ChatGPT",
            "automation", "productivity", "tech trends"
        ],
        target_audience=["developers", "tech enthusiasts", "entrepreneurs"],
        follower_goal=10000,
        starting_followers=0,
        handle="ai_growth_demo"
    )

    print("\n## Initializing System...")
    init_report = system.initialize()
    print(f"Status: {init_report['status']}")

    print("\n## Generating Daily Content Plan...")
    plan = system.generate_daily_plan(strategy="maximum")

    print(f"\nDaily Plan for {plan.date}:")
    print(f"  Posts: {len(plan.posts)}")
    print(f"  Threads: {len(plan.threads)}")
    print(f"  Videos: {len(plan.videos)}")
    print(f"  Predicted follows: {plan.predicted_follows}")

    print("\n## Sample Post:")
    if plan.posts:
        post = plan.posts[0]
        print(f"Type: {post.content_type}")
        print(f"Format: {post.format_type}")
        print(f"Text:\n{post.get_full_text()[:300]}...")
        print(f"Predicted engagement: {post.predicted_engagement_rate:.2%}")

    print("\n## Sample Thread:")
    if plan.threads:
        thread = plan.threads[0]
        print(f"First tweet: {thread.main_text[:100]}...")
        print(f"Thread length: {1 + len(thread.thread_continuation)} tweets")

    print("\n## Posting Schedule:")
    for item in plan.posting_schedule[:5]:
        print(f"  {item['time']}: {item['content_type']} - {item['predicted_engagement']}")

    print("\n## Quick Start Guide:")
    print(system.get_quick_start_guide())


if __name__ == "__main__":
    main()
