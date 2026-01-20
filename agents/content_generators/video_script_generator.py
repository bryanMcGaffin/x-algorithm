"""
Video Script Generator Agent

Generates optimized video scripts for:
- Short videos (< 45s) for quick engagement
- Long videos (> 45s) for VQV (Video Quality Views) bonus
- Maximum retention and completion rate
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import random

from .base_generator import (
    BaseContentGenerator, ContentPiece, NicheProfile
)


@dataclass
class VideoScript:
    """Complete video script with timing."""
    title: str
    hook: str  # First 3 seconds
    body_sections: List[Dict[str, str]]  # [{content, duration, visual_note}]
    cta: str
    total_duration_seconds: int
    caption: str  # Post caption
    hashtags: List[str]

    # Optimization metrics
    hook_strength: float = 0.0
    retention_prediction: float = 0.0
    vqv_eligible: bool = False

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "hook": self.hook,
            "body_sections": self.body_sections,
            "cta": self.cta,
            "total_duration": self.total_duration_seconds,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "hook_strength": self.hook_strength,
            "retention_prediction": self.retention_prediction,
            "vqv_eligible": self.vqv_eligible,
        }


# Video hook templates (first 3 seconds - CRITICAL)
VIDEO_HOOKS = {
    "shock": [
        "Stop scrolling. This changes everything about {topic}.",
        "I can't believe I'm sharing this about {topic}.",
        "This {topic} hack is insane.",
        "Nobody talks about this {topic} secret.",
        "Delete everything you know about {topic}.",
    ],
    "question": [
        "Why does everyone get {topic} so wrong?",
        "What if I told you {topic} is a lie?",
        "Want to know the real truth about {topic}?",
        "Have you ever wondered why {topic}?",
        "Can you handle the truth about {topic}?",
    ],
    "promise": [
        "In 30 seconds, you'll understand {topic}.",
        "This will save you hours with {topic}.",
        "The {topic} shortcut nobody shows you.",
        "{topic} in under a minute. Let's go.",
        "Master {topic} faster than anyone.",
    ],
    "story": [
        "So this happened with {topic}...",
        "I learned this about {topic} the hard way.",
        "The {topic} mistake that changed everything.",
        "Let me tell you about {topic}.",
        "This {topic} story is wild.",
    ],
    "direct": [
        "Here's the thing about {topic}.",
        "{topic}. Let's break it down.",
        "Quick {topic} breakdown for you.",
        "{number} things about {topic}. Ready?",
        "The truth about {topic}:",
    ],
}

# Video body section templates
VIDEO_BODY_SECTIONS = {
    "educational": [
        {"content": "First, understand this about {topic}:", "duration": 8, "visual": "Text overlay with key point"},
        {"content": "The key insight is {insight}.", "duration": 10, "visual": "B-roll or demonstration"},
        {"content": "Here's how to apply this:", "duration": 12, "visual": "Step-by-step visual"},
        {"content": "The result? {outcome}.", "duration": 5, "visual": "Before/after or result showcase"},
    ],
    "story": [
        {"content": "It started when {beginning}.", "duration": 8, "visual": "Setting the scene"},
        {"content": "Then {complication} happened.", "duration": 10, "visual": "Building tension"},
        {"content": "The turning point: {insight}.", "duration": 12, "visual": "Revelation moment"},
        {"content": "Now {resolution}.", "duration": 8, "visual": "Resolution and outcome"},
    ],
    "listicle": [
        {"content": "Number one: {point_1}", "duration": 10, "visual": "Point 1 visual"},
        {"content": "Number two: {point_2}", "duration": 10, "visual": "Point 2 visual"},
        {"content": "Number three: {point_3}", "duration": 10, "visual": "Point 3 visual"},
        {"content": "Bonus: {bonus_point}", "duration": 8, "visual": "Bonus reveal"},
    ],
    "comparison": [
        {"content": "Most people do {common_way}.", "duration": 8, "visual": "Common approach"},
        {"content": "But here's what actually works: {better_way}.", "duration": 12, "visual": "Better approach"},
        {"content": "The difference is {key_difference}.", "duration": 10, "visual": "Side-by-side comparison"},
        {"content": "Try this instead.", "duration": 5, "visual": "Call to action visual"},
    ],
}

# Video CTA templates
VIDEO_CTAS = [
    "Follow for more {topic} content.",
    "Save this. You'll need it.",
    "Share this with someone learning {topic}.",
    "Comment if you want part two.",
    "Drop a follow if this helped.",
    "More {topic} tips on my profile.",
]


class VideoScriptAgent(BaseContentGenerator):
    """
    Generates optimized video scripts.

    Two modes:
    - Short (< 45s): Quick engagement, no VQV
    - Long (45-180s): VQV eligible, higher dwell time signal
    """

    def __init__(self, niche: NicheProfile):
        super().__init__(niche)
        self.hook_performance: Dict[str, float] = {}
        self.format_performance: Dict[str, float] = {}

    def get_content_type(self) -> str:
        return "video"

    def generate(self, count: int = 1, **kwargs) -> List[ContentPiece]:
        """
        Generate video scripts.

        Args:
            count: Number of scripts to generate
            duration: Target duration ("short" < 45s, "long" >= 45s)
            format_type: Force specific format
            topic: Force specific topic

        Returns:
            List of ContentPiece objects with video scripts
        """
        duration_type = kwargs.get("duration", "long")  # Default to VQV-eligible
        format_type = kwargs.get("format_type", None)
        forced_topic = kwargs.get("topic", None)

        videos = []
        for _ in range(count):
            topics = [forced_topic] if forced_topic else self._select_topics(2)
            main_topic = topics[0] if topics else "this"

            if not format_type:
                format_type = self._select_video_format()

            # Generate script
            script = self._generate_script(
                main_topic,
                format_type,
                duration_type
            )

            # Create content piece
            content = ContentPiece(
                content_type="video_long" if script.vqv_eligible else "video_short",
                main_text=script.caption,
                hook=script.hook,
                cta=script.cta,
                hashtags=script.hashtags,
                media_suggestions=[f"VIDEO SCRIPT:\n{self._format_script(script)}"],
                optimal_posting_time=self._get_optimal_posting_time(),
                topics_used=topics,
                trends_incorporated=[],
                format_type=format_type,
                confidence_score=script.hook_strength,
            )

            # Calculate metrics
            content.algorithm_alignment_score = self._calculate_video_algorithm_score(script)
            content.predicted_engagement_rate = self._predict_video_engagement(script)
            content.predicted_dwell_time = float(script.total_duration_seconds)

            videos.append(content)

            # Reset format for next iteration
            if not kwargs.get("format_type"):
                format_type = None

        return videos

    def _select_video_format(self) -> str:
        """Select video format based on performance."""
        formats = list(VIDEO_BODY_SECTIONS.keys())

        if not self.format_performance:
            return random.choice(formats)

        weights = [self.format_performance.get(f, 1.0) for f in formats]
        weights = [w + random.random() * self.creativity_factor for w in weights]

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for fmt, w in zip(formats, weights):
            cumulative += w
            if r <= cumulative:
                return fmt

        return "educational"

    def _generate_script(
        self,
        topic: str,
        format_type: str,
        duration_type: str
    ) -> VideoScript:
        """Generate complete video script."""
        # Determine target duration
        if duration_type == "short":
            target_duration = random.randint(25, 40)
        else:
            target_duration = random.randint(50, 90)

        # Generate hook
        hook_type = self._select_hook_type()
        hook = self._generate_hook(hook_type, topic)
        hook_duration = 3  # Always 3 seconds for hook

        # Generate body sections
        body_sections = self._generate_body_sections(
            format_type,
            topic,
            target_duration - hook_duration - 5  # Leave room for CTA
        )

        # Generate CTA
        cta = self._generate_cta(topic)

        # Calculate actual duration
        body_duration = sum(s["duration"] for s in body_sections)
        total_duration = hook_duration + body_duration + 5  # 5s for CTA

        # Generate caption
        caption = self._generate_caption(topic, format_type)

        # Select hashtags
        hashtags = self._select_video_hashtags(topic)

        # Create script
        script = VideoScript(
            title=f"{format_type.title()} video about {topic}",
            hook=hook,
            body_sections=body_sections,
            cta=cta,
            total_duration_seconds=total_duration,
            caption=caption,
            hashtags=hashtags,
            hook_strength=self._calculate_hook_strength(hook_type, hook),
            retention_prediction=self._predict_retention(format_type, total_duration),
            vqv_eligible=total_duration >= 45,
        )

        return script

    def _select_hook_type(self) -> str:
        """Select hook type based on performance."""
        hook_types = list(VIDEO_HOOKS.keys())

        if not self.hook_performance:
            return random.choice(hook_types)

        weights = [self.hook_performance.get(h, 1.0) for h in hook_types]
        weights = [w + random.random() * self.creativity_factor for w in weights]

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for ht, w in zip(hook_types, weights):
            cumulative += w
            if r <= cumulative:
                return ht

        return "direct"

    def _generate_hook(self, hook_type: str, topic: str) -> str:
        """Generate video hook."""
        templates = VIDEO_HOOKS.get(hook_type, VIDEO_HOOKS["direct"])
        template = random.choice(templates)

        return template.format(
            topic=topic,
            number=random.choice([3, 5, 7])
        )

    def _generate_body_sections(
        self,
        format_type: str,
        topic: str,
        target_duration: int
    ) -> List[Dict[str, str]]:
        """Generate body sections fitting target duration."""
        templates = VIDEO_BODY_SECTIONS.get(format_type, VIDEO_BODY_SECTIONS["educational"])

        # Adjust sections to fit duration
        sections = []
        current_duration = 0

        fills = {
            "topic": topic,
            "insight": f"the core principle of {topic}",
            "outcome": f"better results with {topic}",
            "beginning": f"I started learning {topic}",
            "complication": "I hit a wall",
            "resolution": f"I understand {topic} much better",
            "point_1": f"Master the basics of {topic}",
            "point_2": f"Practice {topic} consistently",
            "point_3": f"Learn from others in {topic}",
            "bonus_point": f"The secret sauce for {topic}",
            "common_way": f"the obvious approach to {topic}",
            "better_way": f"the optimized approach to {topic}",
            "key_difference": "efficiency and results",
        }

        for template in templates:
            if current_duration >= target_duration:
                break

            section = {
                "content": template["content"].format(**fills),
                "duration": template["duration"],
                "visual_note": template["visual"],
            }
            sections.append(section)
            current_duration += template["duration"]

        return sections

    def _generate_cta(self, topic: str) -> str:
        """Generate video CTA."""
        template = random.choice(VIDEO_CTAS)
        return template.format(topic=topic)

    def _generate_caption(self, topic: str, format_type: str) -> str:
        """Generate post caption for video."""
        captions = {
            "educational": f"Quick breakdown of {topic} 👇\n\nSave this for later.",
            "story": f"My {topic} journey in 60 seconds.\n\nThis changed everything.",
            "listicle": f"Top tips for {topic}:\n\nWatch till the end for the bonus.",
            "comparison": f"The right way vs wrong way to approach {topic}.\n\nWhich do you do?",
        }
        return captions.get(format_type, f"Everything about {topic} in one video.")

    def _select_video_hashtags(self, topic: str) -> List[str]:
        """Select hashtags for video."""
        hashtags = []

        if self.niche.hashtags:
            hashtags.extend(random.sample(
                self.niche.hashtags,
                min(2, len(self.niche.hashtags))
            ))

        # Add topic-specific
        hashtags.append(topic.replace(" ", "").lower())

        return hashtags[:3]

    def _get_optimal_posting_time(self) -> int:
        """Get optimal posting time for videos."""
        # Videos perform well in evening
        if self.niche.best_posting_times:
            evening_times = [t for t in self.niche.best_posting_times if 17 <= t <= 22]
            if evening_times:
                return random.choice(evening_times)

        return random.choice([12, 18, 19, 20, 21])

    def _calculate_hook_strength(self, hook_type: str, hook: str) -> float:
        """Calculate hook strength."""
        strength = 0.5

        # Type bonuses
        type_bonuses = {
            "shock": 0.2,
            "question": 0.15,
            "promise": 0.18,
            "story": 0.12,
            "direct": 0.08,
        }
        strength += type_bonuses.get(hook_type, 0.1)

        # Length penalty (shorter hooks are better)
        if len(hook) < 50:
            strength += 0.1
        elif len(hook) > 100:
            strength -= 0.1

        return min(1.0, max(0.0, strength))

    def _predict_retention(self, format_type: str, duration: int) -> float:
        """Predict video retention rate."""
        # Base retention decreases with length
        if duration <= 30:
            base_retention = 0.7
        elif duration <= 60:
            base_retention = 0.55
        else:
            base_retention = 0.4

        # Format bonuses
        format_bonuses = {
            "story": 0.1,
            "listicle": 0.05,
            "educational": 0.08,
            "comparison": 0.07,
        }
        base_retention += format_bonuses.get(format_type, 0)

        return base_retention

    def _calculate_video_algorithm_score(self, script: VideoScript) -> float:
        """Calculate algorithm alignment for video."""
        score = 0.5

        # VQV bonus
        if script.vqv_eligible:
            score += 0.2

        # Hook strength
        score += script.hook_strength * 0.2

        # Retention prediction
        score += script.retention_prediction * 0.1

        # Optimal duration (45-90s is sweet spot)
        if 45 <= script.total_duration_seconds <= 90:
            score += 0.1

        return min(1.0, score)

    def _predict_video_engagement(self, script: VideoScript) -> float:
        """Predict video engagement rate."""
        base_rate = 0.05  # Videos have higher engagement

        # VQV bonus
        if script.vqv_eligible:
            base_rate *= 1.3

        # Hook strength multiplier
        base_rate *= (1 + script.hook_strength * 0.5)

        return base_rate

    def _format_script(self, script: VideoScript) -> str:
        """Format script for display."""
        lines = [
            f"TITLE: {script.title}",
            f"DURATION: {script.total_duration_seconds}s {'(VQV ELIGIBLE)' if script.vqv_eligible else ''}",
            "",
            "=== HOOK (0-3s) ===",
            script.hook,
            "",
            "=== BODY ===",
        ]

        current_time = 3
        for i, section in enumerate(script.body_sections):
            end_time = current_time + section["duration"]
            lines.append(f"[{current_time}-{end_time}s] {section['content']}")
            lines.append(f"  VISUAL: {section['visual_note']}")
            current_time = end_time

        lines.extend([
            "",
            "=== CTA (last 5s) ===",
            script.cta,
            "",
            f"CAPTION: {script.caption}",
            f"HASHTAGS: {' '.join('#' + h for h in script.hashtags)}",
        ])

        return "\n".join(lines)

    def generate_short_video(self, topic: str = None) -> ContentPiece:
        """Convenience method for short video."""
        return self.generate(count=1, duration="short", topic=topic)[0]

    def generate_long_video(self, topic: str = None) -> ContentPiece:
        """Convenience method for VQV-eligible long video."""
        return self.generate(count=1, duration="long", topic=topic)[0]
