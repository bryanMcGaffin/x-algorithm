"""
Post Generator Agent

Generates optimized text and image posts based on:
- Niche profile
- Current trends
- Past performance
- Algorithm requirements
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random

from .base_generator import (
    BaseContentGenerator, ContentPiece, NicheProfile,
    TrendData, PerformanceHistory
)


# High-performing hook templates by format
HOOK_TEMPLATES = {
    "hot_take": [
        "Unpopular opinion: {topic}",
        "Most people get {topic} completely wrong.",
        "The harsh truth about {topic} no one wants to hear:",
        "Stop doing {action}. Here's why:",
        "I was wrong about {topic}. Here's what I learned:",
    ],
    "question": [
        "What if {topic} isn't what we think?",
        "Why does everyone ignore {topic}?",
        "Have you ever wondered why {topic}?",
        "What's your take on {topic}?",
        "Am I the only one who thinks {topic}?",
    ],
    "story": [
        "I just discovered something about {topic}...",
        "This changed everything I knew about {topic}:",
        "3 years ago, I knew nothing about {topic}. Now...",
        "The moment I realized {topic} changed my life:",
        "Here's a story about {topic} that nobody tells:",
    ],
    "list": [
        "{number} things about {topic} that will surprise you:",
        "The top {number} mistakes in {topic}:",
        "{number} secrets about {topic} nobody shares:",
        "Here are {number} ways to master {topic}:",
        "{number} facts about {topic} that changed my mind:",
    ],
    "comparison": [
        "{topic_a} vs {topic_b}: The real difference",
        "Why {topic_a} beats {topic_b} every time:",
        "The {topic_a} vs {topic_b} debate is over. Here's why:",
        "Everyone chooses {topic_a}. Smart people choose {topic_b}.",
    ],
    "prediction": [
        "In 2 years, {topic} will be completely different.",
        "Here's what's coming next for {topic}:",
        "My prediction: {topic} is about to explode.",
        "The future of {topic} is not what you expect:",
    ],
    "standard": [
        "Here's the thing about {topic}:",
        "Let's talk about {topic}.",
        "Something I've been thinking about: {topic}",
        "An observation about {topic}:",
    ],
    "behind_scenes": [
        "Behind the scenes of {topic}:",
        "What nobody sees about {topic}:",
        "The reality of {topic} nobody shows you:",
        "Here's what {topic} actually looks like:",
    ],
}

# Call-to-action templates
CTA_TEMPLATES = [
    "What do you think?",
    "Agree or disagree?",
    "Drop your thoughts below 👇",
    "Repost if this resonates.",
    "Follow for more on {topic}.",
    "Save this for later.",
    "What would you add?",
    "Tag someone who needs this.",
    "Bookmark this one.",
    "",  # No CTA sometimes performs better
]

# Content body templates by format
BODY_TEMPLATES = {
    "hot_take": [
        "The conventional wisdom says {conventional}. But here's the reality: {reality}. "
        "The difference between {good_outcome} and {bad_outcome} often comes down to this one thing.",

        "{topic} isn't about {misconception}. It's about {truth}. "
        "Once you understand this, everything changes.",

        "Everyone focuses on {obvious_thing}. But the real winners focus on {hidden_thing}. "
        "This is why most people struggle with {topic}.",
    ],
    "story": [
        "When I started with {topic}, I made every mistake possible. "
        "{specific_mistake} cost me {consequence}. "
        "The turning point came when I realized {insight}. "
        "Now I {result}.",

        "Last {time_period}, something happened that changed my perspective on {topic}. "
        "{event_description}. The lesson? {lesson}.",
    ],
    "list": [
        "1. {point_1}\n2. {point_2}\n3. {point_3}\n\nThe last one is often overlooked but makes the biggest difference.",

        "• {point_1}\n• {point_2}\n• {point_3}\n\nMost people only focus on the first one. "
        "The best focus on all three.",
    ],
    "question": [
        "I've been thinking about {topic} a lot lately. "
        "The more I dig in, the more I realize {insight}. "
        "But I'm curious what others think.",

        "{topic} seems straightforward until you look deeper. "
        "{observation}. This makes me wonder {question}.",
    ],
    "comparison": [
        "{topic_a}: {description_a}\n\n{topic_b}: {description_b}\n\n"
        "The difference? {key_difference}. Choose accordingly.",

        "People argue about {topic_a} vs {topic_b}. "
        "The truth is {nuanced_take}. Context matters more than the choice itself.",
    ],
    "prediction": [
        "Based on {evidence}, I expect {topic} to {change} within {timeframe}. "
        "Here's why: {reasoning}. "
        "The smart move right now is {action}.",

        "{topic} is at an inflection point. "
        "The signals are clear: {signal_1}, {signal_2}, {signal_3}. "
        "Those who see this early will {advantage}.",
    ],
    "standard": [
        "{insight_about_topic}. "
        "This is why {implication}. "
        "{actionable_takeaway}.",

        "Something I've noticed about {topic}: {observation}. "
        "It's subtle but it makes all the difference in {outcome}.",
    ],
    "behind_scenes": [
        "What people see: {surface}\n\nWhat's actually happening: {reality}\n\n"
        "The gap between these two is where {value} lives.",

        "Everyone shows {polished_version}. "
        "Here's what it actually takes: {real_work}. "
        "The {topic} journey is messier than it looks.",
    ],
}


class PostGeneratorAgent(BaseContentGenerator):
    """
    Generates optimized posts (text and image posts).

    Adapts based on:
    - Performance data
    - Trending topics
    - Niche alignment
    - Algorithm signals
    """

    def __init__(self, niche: NicheProfile):
        super().__init__(niche)
        self.hook_performance: Dict[str, float] = {}
        self.cta_performance: Dict[str, float] = {}

    def get_content_type(self) -> str:
        return "text_post"

    def generate(self, count: int = 1, **kwargs) -> List[ContentPiece]:
        """
        Generate optimized posts.

        Args:
            count: Number of posts to generate
            include_image: Whether to suggest images
            format_type: Force a specific format (optional)
            topic: Force a specific topic (optional)

        Returns:
            List of ContentPiece objects
        """
        include_image = kwargs.get("include_image", False)
        forced_format = kwargs.get("format_type", None)
        forced_topic = kwargs.get("topic", None)

        posts = []
        for _ in range(count):
            # Select format and topics
            format_type = forced_format or self._select_format()
            topics = [forced_topic] if forced_topic else self._select_topics(2)

            # Generate hook
            hook = self._generate_hook(format_type, topics[0] if topics else "this")

            # Generate body
            body = self._generate_body(format_type, topics)

            # Generate CTA
            cta = self._generate_cta(topics[0] if topics else None)

            # Select hashtags
            hashtags = self._select_hashtags(topics)

            # Generate media suggestions if needed
            media = []
            if include_image or random.random() < 0.3:  # 30% chance of suggesting media
                media = self._generate_media_suggestions(topics, body)

            # Determine optimal posting time
            posting_time = self._get_optimal_posting_time()

            # Incorporate trends
            incorporated_trends = []
            if self.trend_data:
                for topic in topics:
                    if topic in self.trend_data.trending_topics:
                        incorporated_trends.append(topic)

            # Create content piece
            content = ContentPiece(
                content_type="image_post" if media else "text_post",
                main_text=body,
                hook=hook,
                cta=cta,
                hashtags=hashtags,
                media_suggestions=media,
                optimal_posting_time=posting_time,
                topics_used=topics,
                trends_incorporated=incorporated_trends,
                format_type=format_type,
                confidence_score=self._calculate_confidence(format_type, topics),
            )

            # Calculate algorithm alignment
            content.algorithm_alignment_score = self._calculate_algorithm_score(content)
            content.predicted_engagement_rate = self._predict_engagement(content)
            content.predicted_dwell_time = self._predict_dwell_time(content)

            posts.append(content)

        return posts

    def _generate_hook(self, format_type: str, topic: str) -> str:
        """Generate attention-grabbing hook."""
        templates = HOOK_TEMPLATES.get(format_type, HOOK_TEMPLATES["standard"])
        template = self._weighted_choice(templates, self.hook_performance)

        # Fill in template
        hook = template.format(
            topic=topic,
            action=f"doing {topic} this way",
            number=random.choice([3, 5, 7]),
            topic_a=topic,
            topic_b=self._get_contrasting_topic(topic),
        )

        return hook

    def _generate_body(self, format_type: str, topics: List[str]) -> str:
        """Generate main content body."""
        templates = BODY_TEMPLATES.get(format_type, BODY_TEMPLATES["standard"])
        template = random.choice(templates)

        topic = topics[0] if topics else "this subject"
        secondary = topics[1] if len(topics) > 1 else "related areas"

        # Create context-aware fills
        fills = {
            "topic": topic,
            "conventional": f"the standard approach to {topic}",
            "reality": f"{topic} requires a different mindset",
            "good_outcome": "success",
            "bad_outcome": "frustration",
            "misconception": "the obvious approach",
            "truth": "understanding the fundamentals",
            "obvious_thing": "the surface level",
            "hidden_thing": "the underlying principles",
            "specific_mistake": f"misunderstanding {topic}",
            "consequence": "wasted time and effort",
            "insight": f"the core principle of {topic}",
            "result": f"approach {topic} completely differently",
            "time_period": random.choice(["week", "month", "year"]),
            "event_description": f"I encountered a situation with {topic}",
            "lesson": f"{topic} is more nuanced than it appears",
            "point_1": f"Understanding the basics of {topic}",
            "point_2": f"Applying {topic} consistently",
            "point_3": f"Adapting {topic} to your situation",
            "observation": f"{topic} has hidden complexity",
            "question": f"what we're missing about {topic}",
            "topic_a": topic,
            "topic_b": secondary,
            "description_a": f"the traditional view of {topic}",
            "description_b": f"the modern approach to {topic}",
            "key_difference": "execution and context",
            "nuanced_take": "both have their place",
            "evidence": "current patterns",
            "change": "evolve significantly",
            "timeframe": random.choice(["6 months", "1 year", "2 years"]),
            "reasoning": f"the fundamentals of {topic} are shifting",
            "action": "to prepare now",
            "signal_1": "increased interest",
            "signal_2": "shifting dynamics",
            "signal_3": "emerging patterns",
            "advantage": "benefit significantly",
            "insight_about_topic": f"The key to {topic} is consistency",
            "implication": "most approaches fail",
            "actionable_takeaway": "Focus on the fundamentals first",
            "surface": f"the polished version of {topic}",
            "reality": f"the messy truth of {topic}",
            "value": f"real {topic} mastery",
            "polished_version": "the highlight reel",
            "real_work": "the daily grind",
        }

        try:
            body = template.format(**fills)
        except KeyError:
            body = f"Here's what I've learned about {topic}: the key is understanding the fundamentals and applying them consistently. Most people overcomplicate it."

        return body

    def _generate_cta(self, topic: Optional[str]) -> str:
        """Generate call-to-action."""
        template = self._weighted_choice(CTA_TEMPLATES, self.cta_performance)

        if not template:
            return ""

        if topic and "{topic}" in template:
            return template.format(topic=topic)
        return template

    def _select_hashtags(self, topics: List[str]) -> List[str]:
        """Select relevant hashtags."""
        hashtags = []

        # Add niche hashtags
        if self.niche.hashtags:
            hashtags.extend(random.sample(
                self.niche.hashtags,
                min(2, len(self.niche.hashtags))
            ))

        # Add trending hashtags if relevant
        if self.trend_data and self.trend_data.trending_hashtags:
            for h in self.trend_data.trending_hashtags[:5]:
                if any(t.lower() in h.lower() for t in topics):
                    hashtags.append(h)
                    break

        return hashtags[:3]  # Max 3 hashtags

    def _generate_media_suggestions(
        self, topics: List[str], body: str
    ) -> List[str]:
        """Generate media/image suggestions."""
        suggestions = []

        topic = topics[0] if topics else "the topic"

        media_types = [
            f"Screenshot or infographic about {topic}",
            f"Chart or graph showing {topic} data",
            f"Behind-the-scenes photo related to {topic}",
            f"Quote graphic with key insight about {topic}",
            f"Before/after comparison related to {topic}",
            f"Step-by-step visual guide for {topic}",
        ]

        suggestions.append(random.choice(media_types))

        return suggestions

    def _get_optimal_posting_time(self) -> int:
        """Determine optimal posting time (hour 0-23)."""
        # Use learned best times if available
        if self.niche.best_posting_times:
            return random.choice(self.niche.best_posting_times)

        # Default optimal times (UTC)
        optimal_times = [9, 12, 15, 18, 21]
        return random.choice(optimal_times)

    def _get_contrasting_topic(self, topic: str) -> str:
        """Get a contrasting topic for comparisons."""
        if len(self.niche.primary_topics) > 1:
            others = [t for t in self.niche.primary_topics if t != topic]
            if others:
                return random.choice(others)
        return "the alternative"

    def _weighted_choice(
        self, options: List[str], weights: Dict[str, float]
    ) -> str:
        """Make weighted random choice based on performance."""
        if not weights:
            return random.choice(options)

        weighted_options = []
        for opt in options:
            weight = weights.get(opt, 1.0)
            weight += random.random() * self.creativity_factor
            weighted_options.append((opt, weight))

        weighted_options.sort(key=lambda x: x[1], reverse=True)

        # Pick from top options with some randomness
        top_n = max(1, len(weighted_options) // 2)
        return random.choice([o[0] for o in weighted_options[:top_n]])

    def _calculate_confidence(
        self, format_type: str, topics: List[str]
    ) -> float:
        """Calculate confidence score for generated content."""
        confidence = 0.5  # Base

        # Boost for proven format
        if format_type in self.format_weights:
            confidence += 0.1 * min(1.0, self.format_weights[format_type])

        # Boost for proven topics
        for topic in topics:
            if topic in self.topic_weights:
                confidence += 0.05 * min(1.0, self.topic_weights[topic])

        # Boost for trending content
        if self.trend_data:
            for topic in topics:
                if topic in self.trend_data.trending_topics:
                    confidence += 0.1

        return min(1.0, confidence)

    def _predict_engagement(self, content: ContentPiece) -> float:
        """Predict engagement rate based on content features."""
        # Base rate from performance history
        if self.performance_history:
            base_rate = sum(p.engagement_rate for p in self.performance_history[-20:]) / min(20, len(self.performance_history))
        else:
            base_rate = 0.03

        # Adjustments
        rate = base_rate

        # Hook bonus
        if content.hook:
            rate *= 1.2

        # Media bonus
        if content.media_suggestions:
            rate *= 1.3

        # Format multipliers
        format_multipliers = {
            "hot_take": 1.3,
            "question": 1.2,
            "story": 1.25,
            "list": 1.1,
            "prediction": 1.15,
        }
        rate *= format_multipliers.get(content.format_type, 1.0)

        # Trend bonus
        if content.trends_incorporated:
            rate *= 1.2

        return rate

    def _predict_dwell_time(self, content: ContentPiece) -> float:
        """Predict dwell time in seconds."""
        # Base dwell time from character count
        chars = content.get_character_count()
        base_dwell = chars / 20  # ~20 chars per second reading

        # Format multipliers (some formats encourage longer reading)
        format_multipliers = {
            "story": 1.5,
            "list": 1.3,
            "comparison": 1.4,
            "standard": 1.0,
        }
        base_dwell *= format_multipliers.get(content.format_type, 1.0)

        # Media bonus
        if content.media_suggestions:
            base_dwell += 3  # Extra seconds for image viewing

        return base_dwell

    def generate_variations(
        self, base_content: ContentPiece, count: int = 3
    ) -> List[ContentPiece]:
        """Generate variations of a base content piece for A/B testing."""
        variations = []

        for i in range(count):
            # Vary the hook
            new_hook = self._generate_hook(
                base_content.format_type,
                base_content.topics_used[0] if base_content.topics_used else "this"
            )

            # Vary the CTA
            new_cta = self._generate_cta(
                base_content.topics_used[0] if base_content.topics_used else None
            )

            variation = ContentPiece(
                content_type=base_content.content_type,
                main_text=base_content.main_text,
                hook=new_hook,
                cta=new_cta,
                hashtags=base_content.hashtags,
                media_suggestions=base_content.media_suggestions,
                optimal_posting_time=base_content.optimal_posting_time,
                topics_used=base_content.topics_used,
                trends_incorporated=base_content.trends_incorporated,
                format_type=base_content.format_type,
                confidence_score=base_content.confidence_score * 0.9,  # Slightly lower for variations
            )

            variation.algorithm_alignment_score = self._calculate_algorithm_score(variation)
            variation.predicted_engagement_rate = self._predict_engagement(variation)
            variation.predicted_dwell_time = self._predict_dwell_time(variation)

            variations.append(variation)

        return variations
