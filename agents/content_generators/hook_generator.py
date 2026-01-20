"""
Hook Generator Agent

Specialized agent for generating high-converting hooks.
Hooks are the most critical element - they determine if content gets consumed.

Based on analysis of viral content patterns and algorithm signals.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import random

from .base_generator import BaseContentGenerator, NicheProfile


@dataclass
class Hook:
    """Generated hook with metadata."""
    text: str
    hook_type: str
    strength_score: float
    scroll_stop_probability: float
    target_emotion: str
    word_count: int
    uses_power_words: bool
    opens_curiosity_gap: bool

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "hook_type": self.hook_type,
            "strength_score": self.strength_score,
            "scroll_stop_probability": self.scroll_stop_probability,
            "target_emotion": self.target_emotion,
            "word_count": self.word_count,
            "uses_power_words": self.uses_power_words,
            "opens_curiosity_gap": self.opens_curiosity_gap,
        }


# Power words that increase engagement
POWER_WORDS = {
    "urgency": ["now", "immediately", "stop", "urgent", "critical", "don't", "never"],
    "curiosity": ["secret", "hidden", "unknown", "discovered", "revealed", "truth"],
    "emotion": ["shocking", "insane", "incredible", "unbelievable", "wild", "crazy"],
    "exclusivity": ["only", "rare", "few", "exclusive", "insider", "elite"],
    "authority": ["proven", "guaranteed", "definitive", "ultimate", "complete", "master"],
    "simplicity": ["simple", "easy", "quick", "fast", "instant", "effortless"],
    "fear": ["mistake", "avoid", "wrong", "fail", "lose", "miss", "risk"],
    "benefit": ["free", "save", "gain", "win", "unlock", "transform", "breakthrough"],
}

# Hook patterns by type
HOOK_PATTERNS = {
    "curiosity_gap": {
        "patterns": [
            "I discovered something about {topic} that changes everything.",
            "The {topic} secret that {authority_figure} don't want you to know.",
            "What I learned about {topic} after {impressive_stat}.",
            "There's a reason {topic} isn't working for you. It's not what you think.",
            "The hidden truth about {topic}:",
        ],
        "emotion": "curiosity",
        "strength_base": 0.75,
    },
    "contrarian": {
        "patterns": [
            "Unpopular opinion: {topic} is completely misunderstood.",
            "Everything you've heard about {topic} is wrong.",
            "Stop doing {common_advice}. Here's why:",
            "The {topic} advice that's actually hurting you:",
            "Why the 'best' {topic} advice is actually the worst:",
        ],
        "emotion": "surprise",
        "strength_base": 0.80,
    },
    "direct_benefit": {
        "patterns": [
            "How to {benefit} with {topic} (no {common_obstacle}).",
            "The {topic} shortcut that saved me {impressive_stat}.",
            "{topic}: How to go from {bad_state} to {good_state}.",
            "Master {topic} in {timeframe}. Here's exactly how:",
            "The only {topic} guide you'll ever need:",
        ],
        "emotion": "desire",
        "strength_base": 0.70,
    },
    "story_hook": {
        "patterns": [
            "I just {action} with {topic}. Here's what happened:",
            "The moment I realized {topic} changed everything:",
            "{time_period} ago, I knew nothing about {topic}. Now...",
            "This {topic} story will change how you think:",
            "Let me tell you about the {topic} mistake that cost me {consequence}:",
        ],
        "emotion": "anticipation",
        "strength_base": 0.72,
    },
    "social_proof": {
        "patterns": [
            "Why {impressive_number} people are wrong about {topic}:",
            "What {authority_figure} taught me about {topic}:",
            "The {topic} strategy used by {successful_group}:",
            "{impressive_stat} of experts agree on this {topic} principle:",
            "I interviewed {number} {experts} about {topic}. Key insight:",
        ],
        "emotion": "trust",
        "strength_base": 0.68,
    },
    "list_hook": {
        "patterns": [
            "{number} {topic} {things} that will {benefit}:",
            "The top {number} {topic} mistakes (and how to fix them):",
            "{number} things about {topic} I wish I knew earlier:",
            "{number} {topic} rules that changed my life:",
            "Only {number} things matter in {topic}. Here they are:",
        ],
        "emotion": "anticipation",
        "strength_base": 0.65,
    },
    "question_hook": {
        "patterns": [
            "Why isn't your {topic} working?",
            "What if everything you know about {topic} is wrong?",
            "Have you ever wondered why {topic} feels so hard?",
            "What separates {good_outcome} from {bad_outcome} in {topic}?",
            "Ready to finally understand {topic}?",
        ],
        "emotion": "curiosity",
        "strength_base": 0.67,
    },
    "fear_hook": {
        "patterns": [
            "The {topic} mistake that's costing you {consequence}.",
            "If you're doing this with {topic}, stop immediately.",
            "The silent {topic} killer nobody talks about:",
            "This {topic} habit is destroying your {value}.",
            "Warning: {topic} can {negative_outcome} if you {common_action}.",
        ],
        "emotion": "fear",
        "strength_base": 0.78,
    },
}


class HookGeneratorAgent(BaseContentGenerator):
    """
    Specialized agent for generating high-converting hooks.

    Hooks determine scroll-stop rate which directly impacts:
    - Initial engagement
    - Dwell time (algorithm signal)
    - Share/save rate
    """

    def __init__(self, niche: NicheProfile):
        super().__init__(niche)
        self.hook_type_performance: Dict[str, float] = {}

    def get_content_type(self) -> str:
        return "hook"

    def generate(self, count: int = 1, **kwargs) -> List[Hook]:
        """
        Generate optimized hooks.

        Args:
            count: Number of hooks to generate
            topic: Topic for hook
            hook_type: Force specific hook type
            target_emotion: Target emotion to evoke

        Returns:
            List of Hook objects
        """
        forced_topic = kwargs.get("topic", None)
        forced_type = kwargs.get("hook_type", None)
        target_emotion = kwargs.get("target_emotion", None)

        hooks = []
        for _ in range(count):
            topics = [forced_topic] if forced_topic else self._select_topics(1)
            topic = topics[0] if topics else "this"

            # Select hook type
            if forced_type:
                hook_type = forced_type
            elif target_emotion:
                hook_type = self._select_type_for_emotion(target_emotion)
            else:
                hook_type = self._select_best_hook_type()

            # Generate hook
            hook = self._generate_hook(hook_type, topic)
            hooks.append(hook)

        return hooks

    def _select_best_hook_type(self) -> str:
        """Select hook type based on performance data."""
        hook_types = list(HOOK_PATTERNS.keys())

        if not self.hook_type_performance:
            # Default to high-performing types
            return random.choice(["curiosity_gap", "contrarian", "fear_hook"])

        # Weighted selection based on performance
        weights = []
        for ht in hook_types:
            base_strength = HOOK_PATTERNS[ht]["strength_base"]
            performance = self.hook_type_performance.get(ht, 1.0)
            weight = base_strength * performance
            weight += random.random() * self.creativity_factor
            weights.append(weight)

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for ht, w in zip(hook_types, weights):
            cumulative += w
            if r <= cumulative:
                return ht

        return "curiosity_gap"

    def _select_type_for_emotion(self, emotion: str) -> str:
        """Select hook type that targets specific emotion."""
        for hook_type, data in HOOK_PATTERNS.items():
            if data["emotion"] == emotion:
                return hook_type
        return "curiosity_gap"

    def _generate_hook(self, hook_type: str, topic: str) -> Hook:
        """Generate a hook of specified type."""
        pattern_data = HOOK_PATTERNS[hook_type]
        pattern = random.choice(pattern_data["patterns"])

        # Create fills
        fills = self._create_hook_fills(topic)

        # Generate hook text
        try:
            text = pattern.format(**fills)
        except KeyError:
            text = f"Here's what you need to know about {topic}:"

        # Analyze hook
        uses_power_words = self._check_power_words(text)
        opens_gap = self._check_curiosity_gap(text)

        # Calculate strength
        strength = self._calculate_hook_strength(
            hook_type, text, uses_power_words, opens_gap
        )

        # Calculate scroll stop probability
        scroll_stop = self._calculate_scroll_stop_probability(strength, hook_type)

        return Hook(
            text=text,
            hook_type=hook_type,
            strength_score=strength,
            scroll_stop_probability=scroll_stop,
            target_emotion=pattern_data["emotion"],
            word_count=len(text.split()),
            uses_power_words=uses_power_words,
            opens_curiosity_gap=opens_gap,
        )

    def _create_hook_fills(self, topic: str) -> Dict[str, str]:
        """Create template fills for hook generation."""
        return {
            "topic": topic,
            "authority_figure": random.choice(["experts", "top performers", "industry leaders"]),
            "impressive_stat": random.choice(["10,000 hours", "5 years", "1000+ experiments"]),
            "common_advice": f"the standard {topic} approach",
            "benefit": random.choice(["10x your results", "save hours", "achieve mastery"]),
            "common_obstacle": random.choice(["the usual struggle", "wasted time", "common mistakes"]),
            "bad_state": "frustrated beginner",
            "good_state": "confident practitioner",
            "timeframe": random.choice(["30 days", "one month", "weeks, not years"]),
            "action": random.choice(["tested this", "discovered something", "made a breakthrough"]),
            "time_period": random.choice(["2 years", "6 months", "Last year"]),
            "consequence": random.choice(["time", "money", "opportunity"]),
            "impressive_number": random.choice(["90%", "most", "millions of"]),
            "successful_group": random.choice(["top 1%", "industry leaders", "successful creators"]),
            "number": random.choice(["3", "5", "7"]),
            "experts": random.choice(["experts", "professionals", "leaders"]),
            "things": random.choice(["secrets", "lessons", "principles", "rules"]),
            "good_outcome": "success",
            "bad_outcome": "failure",
            "value": random.choice(["results", "progress", "potential"]),
            "negative_outcome": "backfire",
            "common_action": "ignore this",
        }

    def _check_power_words(self, text: str) -> bool:
        """Check if hook contains power words."""
        text_lower = text.lower()
        for category, words in POWER_WORDS.items():
            for word in words:
                if word in text_lower:
                    return True
        return False

    def _check_curiosity_gap(self, text: str) -> bool:
        """Check if hook opens a curiosity gap."""
        gap_indicators = [
            "...", ":", "here's", "here is", "this is",
            "why", "how", "what", "secret", "truth", "discover",
            "learn", "found", "realized"
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in gap_indicators)

    def _calculate_hook_strength(
        self,
        hook_type: str,
        text: str,
        uses_power_words: bool,
        opens_gap: bool
    ) -> float:
        """Calculate overall hook strength."""
        # Base strength from hook type
        base = HOOK_PATTERNS[hook_type]["strength_base"]

        # Adjustments
        if uses_power_words:
            base += 0.08
        if opens_gap:
            base += 0.10

        # Length optimization (8-15 words is ideal)
        word_count = len(text.split())
        if 8 <= word_count <= 15:
            base += 0.05
        elif word_count > 20:
            base -= 0.10

        # Performance history
        if hook_type in self.hook_type_performance:
            base *= self.hook_type_performance[hook_type]

        return min(1.0, max(0.0, base))

    def _calculate_scroll_stop_probability(
        self,
        strength: float,
        hook_type: str
    ) -> float:
        """Calculate probability of stopping scroll."""
        # Base from strength
        prob = strength * 0.7

        # Type multipliers
        type_multipliers = {
            "contrarian": 1.15,
            "fear_hook": 1.12,
            "curiosity_gap": 1.10,
            "story_hook": 1.05,
            "direct_benefit": 1.00,
            "social_proof": 0.98,
            "list_hook": 0.95,
            "question_hook": 1.02,
        }
        prob *= type_multipliers.get(hook_type, 1.0)

        return min(0.95, prob)

    def generate_variations(self, topic: str, count: int = 5) -> List[Hook]:
        """Generate multiple hook variations for A/B testing."""
        hooks = []

        # Generate one of each type
        types_to_use = random.sample(list(HOOK_PATTERNS.keys()), min(count, len(HOOK_PATTERNS)))

        for hook_type in types_to_use:
            hook = self._generate_hook(hook_type, topic)
            hooks.append(hook)

        # Sort by strength
        hooks.sort(key=lambda h: h.strength_score, reverse=True)

        return hooks[:count]

    def record_hook_performance(self, hook: Hook, engagement_rate: float):
        """Record performance for learning."""
        # Update hook type performance
        current = self.hook_type_performance.get(hook.hook_type, 1.0)
        alpha = 0.2  # Learning rate

        # Normalize engagement rate (assume 3% is baseline)
        performance_score = engagement_rate / 0.03

        self.hook_type_performance[hook.hook_type] = (
            alpha * performance_score + (1 - alpha) * current
        )

    def get_hook_recommendations(self, topic: str) -> Dict[str, Hook]:
        """Get recommended hooks by use case."""
        return {
            "highest_converting": self.generate(1, topic=topic, hook_type="contrarian")[0],
            "safest_choice": self.generate(1, topic=topic, hook_type="direct_benefit")[0],
            "story_driven": self.generate(1, topic=topic, hook_type="story_hook")[0],
            "curiosity_driven": self.generate(1, topic=topic, hook_type="curiosity_gap")[0],
            "fear_driven": self.generate(1, topic=topic, hook_type="fear_hook")[0],
        }
