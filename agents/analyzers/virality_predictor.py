"""
Virality Predictor Agent

Predicts viral potential of content before posting:
- Analyzes content features
- Compares to viral patterns
- Scores viral probability
- Suggests improvements
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import re
import math


@dataclass
class ViralityScore:
    """Viral potential score breakdown."""
    overall_score: float  # 0-100
    probability: float    # 0-1

    # Component scores (0-1)
    hook_score: float
    emotional_score: float
    shareability_score: float
    timing_score: float
    format_score: float
    topic_score: float

    # Flags
    has_viral_pattern: bool
    viral_patterns_detected: List[str]

    # Recommendations
    improvements: List[str]
    optimized_version: Optional[str]

    def to_dict(self) -> dict:
        return {
            "overall_score": f"{self.overall_score:.0f}/100",
            "viral_probability": f"{self.probability:.0%}",
            "components": {
                "hook": f"{self.hook_score:.0%}",
                "emotional": f"{self.emotional_score:.0%}",
                "shareability": f"{self.shareability_score:.0%}",
                "timing": f"{self.timing_score:.0%}",
                "format": f"{self.format_score:.0%}",
                "topic": f"{self.topic_score:.0%}",
            },
            "viral_patterns": self.viral_patterns_detected,
            "improvements": self.improvements,
        }


# Viral content features
VIRAL_HOOKS = [
    r"unpopular opinion",
    r"hot take",
    r"nobody talks about",
    r"i (just )?(discovered|learned|realized)",
    r"stop (doing|scrolling)",
    r"the truth about",
    r"secret",
    r"\d+ (things|ways|tips|lessons|mistakes)",
    r"thread",
    r"🧵",
    r"controversial",
    r"harsh truth",
    r"here'?s (the thing|what|why)",
]

EMOTIONAL_TRIGGERS = {
    "curiosity": ["secret", "hidden", "discover", "revealed", "truth", "why", "how"],
    "fear": ["mistake", "wrong", "fail", "avoid", "never", "stop", "warning"],
    "aspiration": ["success", "achieve", "master", "grow", "transform", "level up"],
    "surprise": ["actually", "really", "truth is", "plot twist", "unexpected"],
    "belonging": ["everyone", "most people", "you're not alone", "we all"],
    "urgency": ["now", "today", "immediately", "don't wait", "before it's too late"],
}

SHAREABILITY_MARKERS = [
    "save this",
    "bookmark",
    "share this",
    "repost",
    "tag someone",
    "follow for more",
    "comment below",
    "what do you think",
]

FORMAT_SCORES = {
    "thread": 0.85,
    "video_long": 0.80,
    "video_short": 0.75,
    "image_post": 0.70,
    "text_post": 0.60,
    "quote_tweet": 0.55,
    "reply": 0.40,
}


class ViralityPredictorAgent:
    """
    Predicts viral potential of content.

    Uses multiple signals:
    - Hook analysis
    - Emotional triggers
    - Shareability markers
    - Format optimization
    - Topic trending
    - Historical patterns
    """

    def __init__(self, trending_topics: List[str] = None):
        self.trending_topics = trending_topics or []
        self.prediction_history: List[Tuple[str, ViralityScore, float]] = []  # (content, prediction, actual)

        # Learned weights from feedback
        self.hook_weight: float = 0.25
        self.emotional_weight: float = 0.20
        self.shareability_weight: float = 0.15
        self.timing_weight: float = 0.10
        self.format_weight: float = 0.15
        self.topic_weight: float = 0.15

    def predict(
        self,
        content: str,
        content_type: str = "text_post",
        topics: List[str] = None,
        posting_hour: int = None
    ) -> ViralityScore:
        """
        Predict viral potential of content.

        Args:
            content: The content text
            content_type: Type of content
            topics: Topics covered
            posting_hour: Planned posting hour (UTC)

        Returns:
            ViralityScore with breakdown and recommendations
        """
        topics = topics or []
        posting_hour = posting_hour if posting_hour is not None else 12

        # Analyze components
        hook_score, hook_patterns = self._analyze_hook(content)
        emotional_score, emotions = self._analyze_emotions(content)
        shareability_score = self._analyze_shareability(content)
        timing_score = self._analyze_timing(posting_hour)
        format_score = self._analyze_format(content_type)
        topic_score = self._analyze_topics(topics)

        # Calculate overall score
        overall = (
            hook_score * self.hook_weight +
            emotional_score * self.emotional_weight +
            shareability_score * self.shareability_weight +
            timing_score * self.timing_weight +
            format_score * self.format_weight +
            topic_score * self.topic_weight
        ) * 100

        # Calculate probability (sigmoid transformation)
        probability = 1 / (1 + math.exp(-0.1 * (overall - 50)))

        # Check for viral patterns
        has_viral = len(hook_patterns) > 0 or emotional_score > 0.7

        # Generate improvements
        improvements = self._generate_improvements(
            content, hook_score, emotional_score, shareability_score,
            format_score, topic_score
        )

        # Generate optimized version
        optimized = self._generate_optimized_version(content, improvements)

        return ViralityScore(
            overall_score=overall,
            probability=probability,
            hook_score=hook_score,
            emotional_score=emotional_score,
            shareability_score=shareability_score,
            timing_score=timing_score,
            format_score=format_score,
            topic_score=topic_score,
            has_viral_pattern=has_viral,
            viral_patterns_detected=hook_patterns + list(emotions),
            improvements=improvements,
            optimized_version=optimized if overall < 70 else None,
        )

    def _analyze_hook(self, content: str) -> Tuple[float, List[str]]:
        """Analyze hook strength."""
        content_lower = content.lower()
        first_line = content.split('\n')[0].lower()

        patterns_found = []
        score = 0.3  # Base score

        # Check viral hooks
        for pattern in VIRAL_HOOKS:
            if re.search(pattern, first_line):
                patterns_found.append(pattern)
                score += 0.15

        # Length analysis (shorter hooks = stronger)
        words = first_line.split()
        if 3 <= len(words) <= 12:
            score += 0.1
        elif len(words) > 20:
            score -= 0.1

        # Starts with number
        if re.match(r'^\d+', first_line):
            score += 0.1
            patterns_found.append("number_start")

        # Question hook
        if first_line.endswith('?'):
            score += 0.08
            patterns_found.append("question")

        return min(1.0, score), patterns_found

    def _analyze_emotions(self, content: str) -> Tuple[float, set]:
        """Analyze emotional triggers."""
        content_lower = content.lower()
        emotions_triggered = set()
        score = 0.3

        for emotion, triggers in EMOTIONAL_TRIGGERS.items():
            for trigger in triggers:
                if trigger in content_lower:
                    emotions_triggered.add(emotion)
                    score += 0.1
                    break

        # Bonus for multiple emotions
        if len(emotions_triggered) >= 2:
            score += 0.1
        if len(emotions_triggered) >= 3:
            score += 0.15

        return min(1.0, score), emotions_triggered

    def _analyze_shareability(self, content: str) -> float:
        """Analyze shareability markers."""
        content_lower = content.lower()
        score = 0.4  # Base

        for marker in SHAREABILITY_MARKERS:
            if marker in content_lower:
                score += 0.1

        # Brevity bonus (easier to share)
        if len(content) < 200:
            score += 0.1
        elif len(content) > 500:
            score -= 0.1

        # Quotable content (has clear takeaway)
        if any(word in content_lower for word in ["key:", "takeaway:", "lesson:", "tip:"]):
            score += 0.1

        return min(1.0, score)

    def _analyze_timing(self, hour: int) -> float:
        """Analyze posting time score."""
        # Peak engagement hours (UTC)
        peak_hours = {9, 12, 15, 18, 21}
        good_hours = {8, 10, 11, 13, 14, 16, 17, 19, 20, 22}

        if hour in peak_hours:
            return 0.9
        elif hour in good_hours:
            return 0.7
        else:
            return 0.4

    def _analyze_format(self, content_type: str) -> float:
        """Analyze format score."""
        return FORMAT_SCORES.get(content_type, 0.5)

    def _analyze_topics(self, topics: List[str]) -> float:
        """Analyze topic relevance and trending."""
        if not topics:
            return 0.5

        score = 0.5

        # Check trending topics
        for topic in topics:
            topic_lower = topic.lower()
            for trending in self.trending_topics:
                if topic_lower in trending.lower() or trending.lower() in topic_lower:
                    score += 0.2

        return min(1.0, score)

    def _generate_improvements(
        self,
        content: str,
        hook_score: float,
        emotional_score: float,
        shareability_score: float,
        format_score: float,
        topic_score: float
    ) -> List[str]:
        """Generate improvement suggestions."""
        improvements = []

        if hook_score < 0.6:
            improvements.append("Strengthen the hook - start with a number, question, or bold statement")

        if emotional_score < 0.5:
            improvements.append("Add emotional triggers - curiosity, surprise, or urgency")

        if shareability_score < 0.5:
            improvements.append("Add a call-to-action (save, share, comment)")

        if format_score < 0.7:
            improvements.append("Consider converting to a thread or adding media for higher reach")

        if topic_score < 0.6:
            improvements.append("Connect to a trending topic for better discovery")

        # Content-specific
        if len(content) > 400:
            improvements.append("Content is long - consider breaking into a thread")

        if not any(char in content for char in ['?', '!', '...']):
            improvements.append("Add punctuation variety for emphasis")

        return improvements[:5]

    def _generate_optimized_version(
        self,
        content: str,
        improvements: List[str]
    ) -> Optional[str]:
        """Generate optimized version of content."""
        # Simple optimization suggestions
        lines = content.split('\n')
        first_line = lines[0] if lines else content

        optimized_hooks = [
            f"Here's the truth about {first_line[:50]}:",
            f"Stop doing this: {first_line[:50]}",
            f"3 things about {first_line[:50]}:",
            f"Unpopular opinion: {first_line[:50]}",
        ]

        # Return suggested hook + original
        import random
        new_hook = random.choice(optimized_hooks)

        return f"{new_hook}\n\n{content}"

    def record_actual_performance(
        self,
        content: str,
        prediction: ViralityScore,
        actual_engagement_rate: float
    ):
        """Record actual performance for learning."""
        self.prediction_history.append((content, prediction, actual_engagement_rate))

        # Adjust weights based on accuracy
        self._update_weights()

    def _update_weights(self):
        """Update prediction weights based on feedback."""
        if len(self.prediction_history) < 10:
            return

        # Simple learning: increase weight of components that correlate with actual performance
        recent = self.prediction_history[-20:]

        correlations = {
            "hook": [],
            "emotional": [],
            "shareability": [],
            "timing": [],
            "format": [],
            "topic": [],
        }

        for content, prediction, actual in recent:
            # Calculate correlation contribution
            for key in correlations:
                score = getattr(prediction, f"{key}_score")
                correlations[key].append(score * actual)

        # Adjust weights (simple moving average)
        alpha = 0.1
        for key, values in correlations.items():
            if values:
                avg = sum(values) / len(values)
                current = getattr(self, f"{key}_weight")
                new_weight = alpha * avg + (1 - alpha) * current
                setattr(self, f"{key}_weight", max(0.05, min(0.4, new_weight)))

    def get_viral_checklist(self) -> List[Dict[str, str]]:
        """Get checklist for viral content."""
        return [
            {"item": "Strong hook in first line", "importance": "Critical"},
            {"item": "Emotional trigger (curiosity, surprise, fear)", "importance": "High"},
            {"item": "Clear, quotable takeaway", "importance": "High"},
            {"item": "Call-to-action (save, share, reply)", "importance": "Medium"},
            {"item": "Optimal posting time", "importance": "Medium"},
            {"item": "Relevant trending topic", "importance": "Medium"},
            {"item": "Appropriate format (thread for depth)", "importance": "Medium"},
            {"item": "Visual element if possible", "importance": "Medium"},
        ]

    def batch_predict(
        self,
        contents: List[Dict[str, Any]]
    ) -> List[Tuple[Dict, ViralityScore]]:
        """Predict viral potential for multiple pieces of content."""
        results = []

        for item in contents:
            score = self.predict(
                content=item.get("content", ""),
                content_type=item.get("content_type", "text_post"),
                topics=item.get("topics", []),
                posting_hour=item.get("posting_hour", 12),
            )
            results.append((item, score))

        # Sort by viral potential
        results.sort(key=lambda x: x[1].overall_score, reverse=True)
        return results
