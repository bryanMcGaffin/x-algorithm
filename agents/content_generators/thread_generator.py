"""
Thread Generator Agent

Generates high-engagement threads optimized for:
- Maximum dwell time (3x signal weight)
- Story arc and readability
- Hook strength
- Algorithm alignment
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random

from .base_generator import (
    BaseContentGenerator, ContentPiece, NicheProfile,
    TrendData
)


# Thread hook templates (first tweet)
THREAD_HOOKS = {
    "educational": [
        "{topic} explained in {n} simple steps:\n\n(Thread 🧵)",
        "Everything you need to know about {topic}:\n\n(Save this thread)",
        "I spent {time} learning about {topic}.\n\nHere's what I wish I knew earlier:\n\n🧵",
        "The complete guide to {topic}:\n\n(Bookmark this)",
        "{topic} masterclass:\n\n{n} lessons that took me {time} to learn.\n\n🧵👇",
    ],
    "story": [
        "The story of how {outcome}:\n\n(Thread)",
        "This is the craziest thing I've learned about {topic}:\n\n🧵",
        "{time} ago, I {starting_point}.\n\nToday, I {ending_point}.\n\nHere's exactly what happened:\n\n🧵",
        "I made every mistake possible with {topic}.\n\nHere's what I learned:\n\n(Thread)",
        "Let me tell you about the time {event}:\n\n🧵",
    ],
    "listicle": [
        "{n} {things} about {topic} that will change your perspective:\n\n🧵",
        "{n} lessons from {source}:\n\n(Thread)",
        "The top {n} mistakes people make with {topic}:\n\n🧵👇",
        "{n} {things} I wish I knew about {topic} sooner:\n\n(Save this)",
        "{n} rules for {topic} that nobody talks about:\n\n🧵",
    ],
    "breakdown": [
        "I analyzed {source}.\n\nHere's what I found:\n\n🧵",
        "Breaking down {topic}:\n\nThe complete analysis.\n\n(Thread)",
        "How {subject} really works:\n\nA deep dive.\n\n🧵",
        "The {topic} breakdown you've been waiting for:\n\n👇",
        "I reverse-engineered {subject}.\n\nHere's the playbook:\n\n🧵",
    ],
    "controversial": [
        "Unpopular opinion: Most advice about {topic} is wrong.\n\nHere's the truth:\n\n🧵",
        "Hot take on {topic}:\n\n(Thread)",
        "Why everything you know about {topic} might be backwards:\n\n🧵",
        "The {topic} advice that everyone gives but nobody should follow:\n\n(Thread)",
        "I'm going to upset some people with this {topic} thread:\n\n🧵",
    ],
}

# Thread body templates (middle tweets)
THREAD_BODY_TEMPLATES = {
    "point": [
        "{number}. {main_point}\n\n{explanation}\n\n{example}",
        "{number}/ {main_point}\n\n{why_it_matters}",
        "→ {main_point}\n\n{details}\n\n{takeaway}",
        "Lesson {number}:\n\n{main_point}\n\n{context}",
    ],
    "story_beat": [
        "{transition}\n\n{event}\n\n{reaction}",
        "Then something changed:\n\n{turning_point}",
        "The breakthrough came when:\n\n{insight}",
        "But here's what I didn't expect:\n\n{surprise}",
    ],
    "elaboration": [
        "Let me explain:\n\n{explanation}",
        "Here's what this means:\n\n{implication}",
        "Why does this matter?\n\n{significance}",
        "The key insight:\n\n{insight}",
    ],
}

# Thread closing templates (last tweet)
THREAD_CLOSINGS = [
    "TL;DR:\n\n{summary}\n\nFollow @{handle} for more on {topic}.",
    "Summary:\n\n{summary}\n\nRepost the first tweet if this helped.\n\nFollow for more.",
    "That's it.\n\n{key_takeaway}\n\nSave this thread.\nFollow for daily {topic} insights.",
    "Key takeaway:\n\n{key_takeaway}\n\nIf you found this valuable:\n\n1. Follow @{handle}\n2. Repost the first tweet\n3. Reply with your thoughts",
    "To recap:\n\n{summary}\n\n♻️ Repost to help others\n👤 Follow @{handle} for more",
]


class ThreadGeneratorAgent(BaseContentGenerator):
    """
    Generates optimized threads for maximum engagement.

    Threads are high-value because:
    - 3x dwell time signal weight
    - Higher engagement (replies, bookmarks)
    - Better follower conversion
    - Showcase expertise
    """

    def __init__(self, niche: NicheProfile, handle: str = "your_handle"):
        super().__init__(niche)
        self.handle = handle
        self.thread_performance: Dict[str, float] = {}

    def get_content_type(self) -> str:
        return "thread"

    def generate(self, count: int = 1, **kwargs) -> List[ContentPiece]:
        """
        Generate optimized threads.

        Args:
            count: Number of threads to generate
            thread_length: Number of tweets (default 7)
            thread_type: Force specific type (educational, story, listicle, breakdown, controversial)
            topic: Force specific topic

        Returns:
            List of ContentPiece objects with thread_continuation
        """
        thread_length = kwargs.get("thread_length", 7)
        thread_type = kwargs.get("thread_type", None)
        forced_topic = kwargs.get("topic", None)

        threads = []
        for _ in range(count):
            # Select type and topic
            if not thread_type:
                thread_type = self._select_thread_type()

            topics = [forced_topic] if forced_topic else self._select_topics(2)
            main_topic = topics[0] if topics else "this subject"

            # Generate thread components
            hook = self._generate_thread_hook(thread_type, main_topic, thread_length)
            body_tweets = self._generate_thread_body(thread_type, main_topic, thread_length - 2)
            closing = self._generate_thread_closing(main_topic)

            # Compile full thread
            full_thread = [hook] + body_tweets + [closing]

            # Get hashtags for first tweet
            hashtags = self._select_hashtags(topics)

            # Determine optimal posting time
            posting_time = self._get_optimal_posting_time()

            # Check for trends
            incorporated_trends = []
            if self.trend_data:
                for topic in topics:
                    if topic in self.trend_data.trending_topics:
                        incorporated_trends.append(topic)

            # Create content piece
            content = ContentPiece(
                content_type="thread",
                main_text=hook,  # First tweet
                hook=hook,
                cta=closing,
                hashtags=hashtags,
                media_suggestions=self._suggest_thread_media(main_topic, thread_length),
                thread_continuation=full_thread[1:],  # Rest of thread
                optimal_posting_time=posting_time,
                topics_used=topics,
                trends_incorporated=incorporated_trends,
                format_type=thread_type,
                confidence_score=self._calculate_confidence(thread_type, topics),
            )

            # Calculate metrics
            content.algorithm_alignment_score = self._calculate_thread_algorithm_score(content)
            content.predicted_engagement_rate = self._predict_thread_engagement(content)
            content.predicted_dwell_time = self._predict_thread_dwell_time(content, thread_length)

            threads.append(content)

            # Reset thread_type for next iteration if not forced
            if not kwargs.get("thread_type"):
                thread_type = None

        return threads

    def _select_thread_type(self) -> str:
        """Select thread type based on performance."""
        types = list(THREAD_HOOKS.keys())

        if not self.thread_performance:
            return random.choice(types)

        # Weighted selection
        weights = [self.thread_performance.get(t, 1.0) for t in types]
        weights = [w + random.random() * self.creativity_factor for w in weights]

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for t, w in zip(types, weights):
            cumulative += w
            if r <= cumulative:
                return t

        return "educational"

    def _generate_thread_hook(self, thread_type: str, topic: str, length: int) -> str:
        """Generate compelling first tweet."""
        templates = THREAD_HOOKS.get(thread_type, THREAD_HOOKS["educational"])
        template = random.choice(templates)

        fills = {
            "topic": topic,
            "n": length - 1,  # Exclude hook from count
            "time": random.choice(["100 hours", "6 months", "2 years", "1000+ hours"]),
            "outcome": f"I mastered {topic}",
            "starting_point": f"knew nothing about {topic}",
            "ending_point": f"understand {topic} deeply",
            "event": f"I discovered the truth about {topic}",
            "things": random.choice(["insights", "lessons", "tips", "principles", "rules"]),
            "source": random.choice([f"top performers in {topic}", f"100+ case studies", f"the best in {topic}"]),
            "subject": topic,
        }

        try:
            return template.format(**fills)
        except KeyError:
            return f"Everything you need to know about {topic}:\n\n(Thread 🧵)"

    def _generate_thread_body(self, thread_type: str, topic: str, num_tweets: int) -> List[str]:
        """Generate middle tweets of thread."""
        tweets = []

        if thread_type in ["educational", "listicle"]:
            templates = THREAD_BODY_TEMPLATES["point"]
            for i in range(num_tweets):
                template = random.choice(templates)
                fills = {
                    "number": i + 1,
                    "main_point": self._generate_point(topic, i),
                    "explanation": f"This is crucial because it affects how you approach {topic}.",
                    "example": f"For example, when dealing with {topic}, this makes all the difference.",
                    "why_it_matters": f"Understanding this changed my approach to {topic}.",
                    "details": f"The key is to apply this consistently in your {topic} journey.",
                    "takeaway": "Don't skip this step.",
                    "context": f"I learned this the hard way with {topic}.",
                }
                try:
                    tweet = template.format(**fills)
                except KeyError:
                    tweet = f"{i + 1}. Key insight about {topic}: This is essential to understand."
                tweets.append(tweet)

        elif thread_type == "story":
            story_beats = [
                f"It started when I first encountered {topic}. I had no idea what I was doing.",
                f"The first mistake I made: thinking {topic} was simple. It's not.",
                f"Then I discovered something that changed everything about {topic}.",
                f"The turning point came when I realized the real key to {topic}.",
                f"After that, things started clicking. {topic.title()} became clearer.",
                f"The biggest lesson: {topic} requires patience and consistency.",
                f"Now I approach {topic} completely differently.",
            ]
            tweets = story_beats[:num_tweets]

        elif thread_type == "breakdown":
            tweets = [
                f"First, let's understand the fundamentals of {topic}.",
                f"The core components of {topic}:\n\n• Component 1\n• Component 2\n• Component 3",
                f"How these pieces fit together in {topic}:",
                f"The common misconception about {topic}:",
                f"What the best practitioners of {topic} do differently:",
                f"The actionable takeaway for {topic}:",
            ][:num_tweets]

        elif thread_type == "controversial":
            tweets = [
                f"The mainstream advice says one thing about {topic}. The reality is different.",
                f"Here's what they don't tell you about {topic}:",
                f"The inconvenient truth: most {topic} advice is generic and unhelpful.",
                f"What actually works with {topic}:",
                f"Why this matters more than the popular opinion:",
                f"The bottom line on {topic}:",
            ][:num_tweets]

        else:
            # Default educational style
            for i in range(num_tweets):
                tweets.append(f"{i + 1}. Key point about {topic}:\n\nThis is an important aspect to understand and apply.")

        return tweets

    def _generate_point(self, topic: str, index: int) -> str:
        """Generate a specific point for educational threads."""
        points = [
            f"Start with the fundamentals of {topic}",
            f"Consistency matters more than intensity in {topic}",
            f"The 80/20 rule applies to {topic}",
            f"Avoid the common trap of overcomplicating {topic}",
            f"Build systems, not just goals for {topic}",
            f"Learn from failures in {topic}",
            f"Seek feedback early and often with {topic}",
            f"Document your {topic} journey",
            f"Connect with others in {topic}",
            f"Stay patient - {topic} takes time",
        ]
        return points[index % len(points)]

    def _generate_thread_closing(self, topic: str) -> str:
        """Generate compelling closing tweet."""
        template = random.choice(THREAD_CLOSINGS)

        fills = {
            "summary": f"Master the fundamentals, stay consistent, keep learning about {topic}.",
            "key_takeaway": f"Success with {topic} comes from understanding these principles and applying them daily.",
            "topic": topic,
            "handle": self.handle,
        }

        try:
            return template.format(**fills)
        except KeyError:
            return f"That's the thread.\n\nFollow @{self.handle} for more {topic} insights.\n\nRepost if this helped."

    def _select_hashtags(self, topics: List[str]) -> List[str]:
        """Select hashtags for thread."""
        hashtags = []

        if self.niche.hashtags:
            hashtags.extend(random.sample(
                self.niche.hashtags,
                min(2, len(self.niche.hashtags))
            ))

        return hashtags[:2]  # Fewer hashtags for threads

    def _suggest_thread_media(self, topic: str, length: int) -> List[str]:
        """Suggest media for thread tweets."""
        suggestions = [
            f"Tweet 1: Eye-catching graphic with thread title about {topic}",
            f"Tweet {length // 2}: Infographic or diagram explaining key concept",
            f"Tweet {length}: Summary graphic or call-to-action image",
        ]
        return suggestions

    def _get_optimal_posting_time(self) -> int:
        """Get optimal posting time for threads."""
        # Threads perform best in morning/early afternoon
        if self.niche.best_posting_times:
            morning_times = [t for t in self.niche.best_posting_times if 8 <= t <= 14]
            if morning_times:
                return random.choice(morning_times)

        return random.choice([9, 10, 11, 14])

    def _calculate_thread_algorithm_score(self, content: ContentPiece) -> float:
        """Calculate algorithm alignment for threads."""
        score = 0.6  # Base score (threads inherently score well)

        # Thread length bonus
        thread_length = 1 + len(content.thread_continuation)
        if 5 <= thread_length <= 10:
            score += 0.15  # Optimal length
        elif thread_length > 10:
            score += 0.10  # Still good but slightly less optimal

        # Hook quality
        if "🧵" in content.hook or "Thread" in content.hook:
            score += 0.05

        # Media suggestions
        if content.media_suggestions:
            score += 0.1

        return min(1.0, score)

    def _predict_thread_engagement(self, content: ContentPiece) -> float:
        """Predict thread engagement rate."""
        # Threads typically get higher engagement
        base_rate = 0.05  # Higher base than single posts

        # Type multipliers
        type_multipliers = {
            "educational": 1.2,
            "story": 1.3,
            "listicle": 1.1,
            "breakdown": 1.15,
            "controversial": 1.4,
        }
        base_rate *= type_multipliers.get(content.format_type, 1.0)

        # Trend bonus
        if content.trends_incorporated:
            base_rate *= 1.2

        return base_rate

    def _predict_thread_dwell_time(self, content: ContentPiece, length: int) -> float:
        """Predict thread dwell time."""
        # ~15-20 seconds per tweet in a thread
        base_dwell = length * 17

        # Story threads get more dwell time
        if content.format_type == "story":
            base_dwell *= 1.3

        return base_dwell
