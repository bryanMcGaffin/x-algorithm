"""
Reply Generator Agent

Generates optimized replies for:
- Building relationships (high reciprocity signal)
- Gaining visibility on high-traffic posts
- Converting viewers to followers
- Driving engagement back to profile
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random

from .base_generator import (
    BaseContentGenerator, ContentPiece, NicheProfile
)


@dataclass
class TargetPost:
    """Information about the post to reply to."""
    author_handle: str
    author_followers: int
    post_content: str
    post_topic: str
    engagement_count: int  # Total engagements
    is_viral: bool = False
    is_in_niche: bool = True


# Reply templates by strategy
REPLY_TEMPLATES = {
    "value_add": [
        "Great point about {topic}. I'd add that {insight}. This changed my approach.",
        "This resonates. In my experience with {topic}, {personal_insight}.",
        "Underrated aspect of {topic}: {additional_point}. Most people miss this.",
        "The key here is {key_insight}. {topic} becomes much clearer with this lens.",
        "Building on this - {extension}. The combination is powerful.",
    ],
    "question": [
        "Interesting take on {topic}. Have you found that {question}?",
        "Curious - how do you handle {scenario} with {topic}?",
        "Love this. What's your view on {related_aspect}?",
        "This makes me wonder about {curiosity}. Thoughts?",
        "Great insight. How long did it take you to figure this out about {topic}?",
    ],
    "agreement_plus": [
        "This is exactly right about {topic}. The part about {specific} is key.",
        "100%. {topic} is often overcomplicated. This nails it.",
        "Saving this. The {specific} point is something more people need to hear.",
        "Couldn't agree more. {topic} changed for me when I understood this.",
        "Spot on. This is the {topic} advice I wish I had years ago.",
    ],
    "story": [
        "This reminds me of when {story_hook}. {topic} works exactly like this.",
        "Had a similar realization about {topic}. {brief_story}",
        "Learning this about {topic} the hard way taught me {lesson}.",
        "My experience with {topic}: {experience}. Your post explains why.",
        "Exactly what happened when I {action}. {topic} is counterintuitive.",
    ],
    "contrarian": [
        "Interesting perspective. I'd push back slightly on {point} - {counter}.",
        "Mostly agree, but {nuance} about {topic} matters here.",
        "Good take. Though I've seen {alternative} work well for {topic} too.",
        "This is true for most, but {exception}. Context matters with {topic}.",
        "Solid advice. One caveat about {topic}: {caveat}.",
    ],
    "amplification": [
        "This deserves more attention. {topic} insight like this is rare.",
        "Bookmarking this {topic} thread. Everyone needs to see this.",
        "The {topic} breakdown I didn't know I needed. Sharing with my network.",
        "If you're learning about {topic}, start here. Gold.",
        "More people need to understand this about {topic}. Reposting.",
    ],
}

# CTA additions for replies (subtle profile driving)
REPLY_CTAS = [
    "",  # Often no CTA is best
    "",
    "",  # Weight toward no CTA
    "I write about this a lot.",
    "Been exploring this topic recently.",
    "Happy to share more if helpful.",
]


class ReplyGeneratorAgent(BaseContentGenerator):
    """
    Generates optimized replies for engagement and growth.

    Strategy:
    - Reply to larger accounts (exposure)
    - Reply to peers (relationship building)
    - Reply to viral content (visibility)
    - Add genuine value (not spam)
    """

    def __init__(self, niche: NicheProfile):
        super().__init__(niche)
        self.strategy_performance: Dict[str, float] = {}

    def get_content_type(self) -> str:
        return "reply"

    def generate(self, count: int = 1, **kwargs) -> List[ContentPiece]:
        """
        Generate replies for target posts.

        Args:
            count: Number of replies to generate
            target_post: TargetPost object with post info
            strategy: Force specific strategy (value_add, question, etc.)

        Returns:
            List of ContentPiece reply objects
        """
        target_post = kwargs.get("target_post", None)
        forced_strategy = kwargs.get("strategy", None)

        replies = []
        for _ in range(count):
            # Select strategy
            strategy = forced_strategy or self._select_strategy(target_post)

            # Get topic from target post or niche
            if target_post:
                topic = target_post.post_topic
            else:
                topics = self._select_topics(1)
                topic = topics[0] if topics else "this"

            # Generate reply
            reply_text = self._generate_reply(strategy, topic, target_post)

            # Optionally add subtle CTA
            cta = self._select_cta()

            # Create content piece
            content = ContentPiece(
                content_type="reply",
                main_text=reply_text,
                hook=None,
                cta=cta,
                hashtags=[],  # No hashtags in replies
                media_suggestions=[],
                optimal_posting_time=None,  # Reply ASAP
                topics_used=[topic],
                trends_incorporated=[],
                format_type=strategy,
                confidence_score=self._calculate_reply_confidence(strategy, target_post),
            )

            # Calculate metrics
            content.algorithm_alignment_score = self._calculate_reply_algorithm_score(content, target_post)
            content.predicted_engagement_rate = self._predict_reply_engagement(strategy, target_post)

            replies.append(content)

        return replies

    def _select_strategy(self, target_post: Optional[TargetPost]) -> str:
        """Select reply strategy based on context and performance."""
        strategies = list(REPLY_TEMPLATES.keys())

        # Context-based selection
        if target_post:
            if target_post.is_viral:
                # Viral posts: value_add or amplification works best
                strategies = ["value_add", "amplification", "agreement_plus"]
            elif target_post.author_followers > 50000:
                # Large accounts: questions or value_add
                strategies = ["question", "value_add", "story"]
            elif target_post.author_followers < 5000:
                # Peers: any strategy works
                pass

        if not self.strategy_performance:
            return random.choice(strategies)

        # Weighted selection
        weights = [self.strategy_performance.get(s, 1.0) for s in strategies]
        weights = [w + random.random() * self.creativity_factor for w in weights]

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for s, w in zip(strategies, weights):
            cumulative += w
            if r <= cumulative:
                return s

        return "value_add"

    def _generate_reply(
        self,
        strategy: str,
        topic: str,
        target_post: Optional[TargetPost]
    ) -> str:
        """Generate reply text."""
        templates = REPLY_TEMPLATES.get(strategy, REPLY_TEMPLATES["value_add"])
        template = random.choice(templates)

        # Create context-aware fills
        fills = {
            "topic": topic,
            "insight": f"consistency matters more than intensity with {topic}",
            "personal_insight": f"small daily progress compounds over time",
            "additional_point": f"the fundamentals are often overlooked",
            "key_insight": f"understanding the 'why' behind {topic}",
            "extension": f"combining this with deliberate practice",
            "question": f"this scales with team size",
            "scenario": "edge cases",
            "related_aspect": f"the long-term implications",
            "curiosity": f"how this applies to different contexts",
            "specific": f"the core principle",
            "story_hook": f"I first started with {topic}",
            "brief_story": "the struggle was real but worth it",
            "lesson": "patience is underrated",
            "experience": "trial and error taught me a lot",
            "action": f"applied this to {topic}",
            "point": "the main approach",
            "counter": "context sometimes requires flexibility",
            "nuance": "the timing aspect",
            "alternative": "a different approach",
            "exception": "certain situations call for adjustment",
            "caveat": "don't skip the basics",
        }

        try:
            reply = template.format(**fills)
        except KeyError:
            reply = f"Great insight about {topic}. This resonates with my experience."

        return reply

    def _select_cta(self) -> str:
        """Select subtle CTA (usually none)."""
        return random.choice(REPLY_CTAS)

    def _calculate_reply_confidence(
        self,
        strategy: str,
        target_post: Optional[TargetPost]
    ) -> float:
        """Calculate confidence in reply quality."""
        confidence = 0.5

        # Strategy performance boost
        if strategy in self.strategy_performance:
            confidence += 0.1 * min(1.0, self.strategy_performance[strategy])

        # Target post context boost
        if target_post:
            if target_post.is_in_niche:
                confidence += 0.15
            if target_post.is_viral:
                confidence += 0.1

        return min(1.0, confidence)

    def _calculate_reply_algorithm_score(
        self,
        content: ContentPiece,
        target_post: Optional[TargetPost]
    ) -> float:
        """Calculate algorithm alignment for reply."""
        score = 0.4  # Base (replies have lower direct reach)

        # Length optimization (50-150 chars is ideal for replies)
        length = len(content.main_text)
        if 50 <= length <= 150:
            score += 0.15
        elif length > 200:
            score -= 0.05

        # Value-add strategies score better
        if content.format_type in ["value_add", "question", "story"]:
            score += 0.1

        # Target post relevance
        if target_post and target_post.is_in_niche:
            score += 0.1

        return min(1.0, score)

    def _predict_reply_engagement(
        self,
        strategy: str,
        target_post: Optional[TargetPost]
    ) -> float:
        """Predict reply engagement likelihood."""
        base_rate = 0.10  # Replies typically get good engagement

        # Strategy multipliers
        strategy_multipliers = {
            "question": 1.4,  # Questions encourage response
            "contrarian": 1.3,  # Controversy drives engagement
            "value_add": 1.2,
            "story": 1.15,
            "agreement_plus": 1.0,
            "amplification": 0.9,
        }
        base_rate *= strategy_multipliers.get(strategy, 1.0)

        # Target post factors
        if target_post:
            if target_post.is_viral:
                base_rate *= 1.5  # More visibility
            if target_post.author_followers > 50000:
                base_rate *= 0.8  # Harder to get noticed
            elif target_post.author_followers < 5000:
                base_rate *= 1.3  # More likely to respond

        return base_rate

    def generate_batch_for_targets(
        self,
        target_posts: List[TargetPost]
    ) -> List[ContentPiece]:
        """Generate replies for multiple target posts."""
        replies = []
        for target in target_posts:
            reply = self.generate(count=1, target_post=target)[0]
            replies.append(reply)
        return replies

    def get_reply_priorities(self) -> Dict[str, str]:
        """Get reply priority guidelines."""
        return {
            "highest": "Viral posts in your niche (first 30 min)",
            "high": "Large accounts (50K+) posting about your topics",
            "medium": "Peer accounts (similar size) for relationship building",
            "lower": "Older posts with good engagement",
            "timing": "Reply within 30 min of post for best visibility",
            "frequency": "20-30 thoughtful replies per day optimal",
        }
