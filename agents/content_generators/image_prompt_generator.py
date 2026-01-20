"""
Image Prompt Generator Agent

Generates optimized image prompts/descriptions for:
- AI image generation tools (Midjourney, DALL-E, etc.)
- Image selection guidance
- Visual content strategy
- Algorithm-optimized visual content
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random

from .base_generator import BaseContentGenerator, NicheProfile


@dataclass
class ImagePrompt:
    """Generated image prompt with metadata."""
    prompt: str
    image_type: str
    style: str
    mood: str
    colors: List[str]
    composition: str
    platform_optimization: str
    scroll_stop_potential: float
    alt_text_suggestion: str

    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "image_type": self.image_type,
            "style": self.style,
            "mood": self.mood,
            "colors": self.colors,
            "composition": self.composition,
            "platform_optimization": self.platform_optimization,
            "scroll_stop_potential": self.scroll_stop_potential,
            "alt_text_suggestion": self.alt_text_suggestion,
        }


# Image types optimized for X algorithm
IMAGE_TYPES = {
    "infographic": {
        "description": "Data visualization or process explanation",
        "scroll_stop": 0.75,
        "dwell_bonus": 1.5,
        "best_for": ["educational", "listicle", "breakdown"],
    },
    "quote_graphic": {
        "description": "Text-based quote or insight",
        "scroll_stop": 0.65,
        "dwell_bonus": 1.2,
        "best_for": ["hot_take", "contrarian", "wisdom"],
    },
    "before_after": {
        "description": "Comparison or transformation visual",
        "scroll_stop": 0.80,
        "dwell_bonus": 1.4,
        "best_for": ["story", "results", "comparison"],
    },
    "behind_scenes": {
        "description": "Authentic, unpolished look",
        "scroll_stop": 0.70,
        "dwell_bonus": 1.3,
        "best_for": ["story", "personal", "authentic"],
    },
    "data_chart": {
        "description": "Graph, chart, or data visualization",
        "scroll_stop": 0.72,
        "dwell_bonus": 1.6,
        "best_for": ["breakdown", "analysis", "trend"],
    },
    "meme_format": {
        "description": "Relatable meme or humor",
        "scroll_stop": 0.85,
        "dwell_bonus": 1.1,
        "best_for": ["humor", "relatable", "viral"],
    },
    "screenshot": {
        "description": "Screenshot of results, DMs, or proof",
        "scroll_stop": 0.78,
        "dwell_bonus": 1.2,
        "best_for": ["proof", "results", "story"],
    },
    "carousel_slide": {
        "description": "Single slide for carousel/thread",
        "scroll_stop": 0.70,
        "dwell_bonus": 1.8,
        "best_for": ["educational", "thread", "listicle"],
    },
}

# Visual styles
VISUAL_STYLES = {
    "minimal": {
        "colors": ["white", "black", "one accent"],
        "composition": "clean, lots of whitespace",
        "best_niches": ["tech", "productivity", "business"],
    },
    "bold": {
        "colors": ["high contrast", "saturated", "eye-catching"],
        "composition": "dynamic, attention-grabbing",
        "best_niches": ["marketing", "fitness", "motivation"],
    },
    "professional": {
        "colors": ["navy", "gray", "subtle accent"],
        "composition": "structured, grid-based",
        "best_niches": ["finance", "consulting", "B2B"],
    },
    "creative": {
        "colors": ["vibrant", "unique combinations", "gradients"],
        "composition": "artistic, expressive",
        "best_niches": ["design", "art", "creative"],
    },
    "authentic": {
        "colors": ["natural", "warm", "unfiltered"],
        "composition": "candid, real-looking",
        "best_niches": ["personal brand", "lifestyle", "coaching"],
    },
    "dark_mode": {
        "colors": ["dark background", "neon accents", "high contrast text"],
        "composition": "modern, tech-forward",
        "best_niches": ["tech", "crypto", "gaming"],
    },
}

# AI image generation prompt templates
AI_PROMPT_TEMPLATES = {
    "infographic": [
        "Clean infographic about {topic}, {style} style, {colors}, showing {content}, professional design, high quality, detailed",
        "Data visualization infographic for {topic}, {style} aesthetic, {content}, clear hierarchy, modern design",
        "Educational infographic explaining {topic}, {style} design, {colors}, step-by-step visual, minimalist",
    ],
    "quote_graphic": [
        "Quote graphic with text '{quote}', {style} design, {colors} color scheme, typography focus, social media optimized",
        "Inspirational quote design about {topic}, {style} aesthetic, bold typography, {colors}, clean background",
        "Text-based graphic featuring insight about {topic}, {style} style, {colors}, modern typography",
    ],
    "conceptual": [
        "Conceptual illustration representing {topic}, {style} style, {colors}, metaphorical visual, thought-provoking",
        "Abstract representation of {topic} concept, {style} design, {colors}, modern art style, symbolic",
        "Visual metaphor for {topic}, {style} aesthetic, {colors}, creative interpretation, professional",
    ],
    "scene": [
        "Professional scene showing {scenario}, {style} lighting, {colors} tones, realistic, high quality",
        "Lifestyle image depicting {scenario}, {style} mood, {colors} palette, authentic feel",
        "{scenario} scene, {style} photography style, {colors} color grading, aspirational",
    ],
}


class ImagePromptAgent(BaseContentGenerator):
    """
    Generates optimized image prompts for visual content.

    Images boost engagement by:
    - 1.2-1.5x more impressions than text-only
    - Higher dwell time (algorithm signal)
    - Better scroll-stop rate
    - Increased save/bookmark rate
    """

    def __init__(self, niche: NicheProfile):
        super().__init__(niche)
        self.image_type_performance: Dict[str, float] = {}
        self.style_performance: Dict[str, float] = {}
        self.niche_style = self._determine_niche_style()

    def get_content_type(self) -> str:
        return "image_prompt"

    def _determine_niche_style(self) -> str:
        """Determine best visual style for niche."""
        niche_name = self.niche.name.lower()

        for style, data in VISUAL_STYLES.items():
            if any(n in niche_name for n in data["best_niches"]):
                return style

        return "minimal"  # Default

    def generate(self, count: int = 1, **kwargs) -> List[ImagePrompt]:
        """
        Generate image prompts.

        Args:
            count: Number of prompts to generate
            image_type: Force specific type (infographic, quote_graphic, etc.)
            style: Force specific style
            topic: Topic for image
            content_text: Associated post text (for context)
            for_ai_generation: If True, returns AI tool prompts

        Returns:
            List of ImagePrompt objects
        """
        forced_type = kwargs.get("image_type", None)
        forced_style = kwargs.get("style", None)
        forced_topic = kwargs.get("topic", None)
        content_text = kwargs.get("content_text", "")
        for_ai = kwargs.get("for_ai_generation", True)

        prompts = []
        for _ in range(count):
            # Select type and style
            image_type = forced_type or self._select_image_type(content_text)
            style = forced_style or self._select_style()

            # Get topic
            topics = [forced_topic] if forced_topic else self._select_topics(1)
            topic = topics[0] if topics else "this subject"

            # Generate prompt
            prompt = self._generate_prompt(image_type, style, topic, content_text, for_ai)
            prompts.append(prompt)

        return prompts

    def _select_image_type(self, content_text: str = "") -> str:
        """Select image type based on content and performance."""
        image_types = list(IMAGE_TYPES.keys())

        # Content-based selection
        content_lower = content_text.lower()
        if any(word in content_lower for word in ["data", "stat", "number", "percent"]):
            return "data_chart"
        elif any(word in content_lower for word in ["before", "after", "transform"]):
            return "before_after"
        elif any(word in content_lower for word in ["step", "how to", "guide"]):
            return "infographic"
        elif any(word in content_lower for word in ["quote", "said", "wisdom"]):
            return "quote_graphic"

        # Performance-based selection
        if not self.image_type_performance:
            return random.choice(["infographic", "quote_graphic", "before_after"])

        weights = []
        for it in image_types:
            base = IMAGE_TYPES[it]["scroll_stop"]
            perf = self.image_type_performance.get(it, 1.0)
            weight = base * perf + random.random() * self.creativity_factor
            weights.append(weight)

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for it, w in zip(image_types, weights):
            cumulative += w
            if r <= cumulative:
                return it

        return "infographic"

    def _select_style(self) -> str:
        """Select visual style."""
        if not self.style_performance:
            return self.niche_style

        styles = list(VISUAL_STYLES.keys())
        weights = [self.style_performance.get(s, 1.0) for s in styles]

        # Boost niche-appropriate style
        niche_idx = styles.index(self.niche_style) if self.niche_style in styles else 0
        weights[niche_idx] *= 1.5

        total = sum(weights)
        r = random.random() * total
        cumulative = 0

        for s, w in zip(styles, weights):
            cumulative += w
            if r <= cumulative:
                return s

        return self.niche_style

    def _generate_prompt(
        self,
        image_type: str,
        style: str,
        topic: str,
        content_text: str,
        for_ai: bool
    ) -> ImagePrompt:
        """Generate complete image prompt."""
        style_data = VISUAL_STYLES[style]
        type_data = IMAGE_TYPES[image_type]

        # Get colors
        colors = style_data["colors"]
        if isinstance(colors, list):
            color_str = ", ".join(colors[:2])
        else:
            color_str = colors

        # Generate AI prompt if needed
        if for_ai and image_type in AI_PROMPT_TEMPLATES:
            templates = AI_PROMPT_TEMPLATES[image_type]
            template = random.choice(templates)

            # Extract quote if present
            quote = self._extract_quote(content_text) or f"Key insight about {topic}"

            prompt_text = template.format(
                topic=topic,
                style=style,
                colors=color_str,
                content=f"key points about {topic}",
                quote=quote,
                scenario=f"professional working on {topic}",
            )
        else:
            prompt_text = self._generate_description_prompt(
                image_type, style, topic, content_text
            )

        # Calculate scroll stop potential
        scroll_stop = type_data["scroll_stop"]
        if style in ["bold", "dark_mode"]:
            scroll_stop *= 1.1

        # Generate alt text suggestion
        alt_text = self._generate_alt_text(image_type, topic)

        return ImagePrompt(
            prompt=prompt_text,
            image_type=image_type,
            style=style,
            mood=self._get_mood(style),
            colors=colors if isinstance(colors, list) else [colors],
            composition=style_data["composition"],
            platform_optimization="1:1 ratio, high contrast, readable at small size",
            scroll_stop_potential=min(0.95, scroll_stop),
            alt_text_suggestion=alt_text,
        )

    def _generate_description_prompt(
        self,
        image_type: str,
        style: str,
        topic: str,
        content_text: str
    ) -> str:
        """Generate descriptive prompt for manual creation."""
        type_data = IMAGE_TYPES[image_type]
        style_data = VISUAL_STYLES[style]

        return f"""
IMAGE TYPE: {image_type.replace('_', ' ').title()}
DESCRIPTION: {type_data['description']}

TOPIC: {topic}
CONTENT CONTEXT: {content_text[:100] if content_text else 'General topic post'}

VISUAL STYLE: {style.replace('_', ' ').title()}
- Colors: {', '.join(style_data['colors']) if isinstance(style_data['colors'], list) else style_data['colors']}
- Composition: {style_data['composition']}

RECOMMENDATIONS:
- Use high contrast for mobile visibility
- Keep text minimal and readable
- Include visual hierarchy
- Consider 1:1 aspect ratio for feed
- Ensure brand consistency

PLATFORM OPTIMIZATION:
- File size under 5MB
- PNG for graphics, JPG for photos
- Test visibility at thumbnail size
        """.strip()

    def _extract_quote(self, content_text: str) -> Optional[str]:
        """Extract potential quote from content."""
        if not content_text:
            return None

        # Look for quotable segments
        sentences = content_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 100:
                return sentence

        return None

    def _get_mood(self, style: str) -> str:
        """Get mood associated with style."""
        moods = {
            "minimal": "calm, focused, professional",
            "bold": "energetic, confident, attention-grabbing",
            "professional": "trustworthy, serious, competent",
            "creative": "inspiring, unique, expressive",
            "authentic": "genuine, relatable, warm",
            "dark_mode": "modern, tech-savvy, sophisticated",
        }
        return moods.get(style, "professional")

    def _generate_alt_text(self, image_type: str, topic: str) -> str:
        """Generate accessible alt text suggestion."""
        templates = {
            "infographic": f"Infographic explaining key concepts about {topic}",
            "quote_graphic": f"Quote graphic with insight about {topic}",
            "before_after": f"Before and after comparison showing {topic} transformation",
            "behind_scenes": f"Behind the scenes look at {topic}",
            "data_chart": f"Chart showing data and trends related to {topic}",
            "meme_format": f"Meme about {topic}",
            "screenshot": f"Screenshot showing {topic} results",
            "carousel_slide": f"Slide explaining {topic}",
        }
        return templates.get(image_type, f"Image related to {topic}")

    def generate_carousel(
        self,
        topic: str,
        num_slides: int = 5,
        style: Optional[str] = None
    ) -> List[ImagePrompt]:
        """Generate prompts for a carousel/thread with images."""
        style = style or self.niche_style
        prompts = []

        slide_types = [
            ("title", "Bold title slide with hook about {topic}"),
            ("point", "Slide explaining key point about {topic}"),
            ("point", "Slide with second insight about {topic}"),
            ("point", "Slide with third lesson about {topic}"),
            ("cta", "Closing slide with call-to-action for {topic}"),
        ]

        for i, (slide_type, description) in enumerate(slide_types[:num_slides]):
            prompt = ImagePrompt(
                prompt=f"Carousel slide {i+1}/{num_slides}: {description.format(topic=topic)}. Style: {style}",
                image_type="carousel_slide",
                style=style,
                mood=self._get_mood(style),
                colors=VISUAL_STYLES[style]["colors"],
                composition="centered text, consistent branding, slide number visible",
                platform_optimization="1:1 ratio, cohesive with other slides",
                scroll_stop_potential=0.75 if i == 0 else 0.65,
                alt_text_suggestion=f"Carousel slide {i+1} about {topic}",
            )
            prompts.append(prompt)

        return prompts

    def get_image_recommendations(self, content_type: str) -> Dict[str, str]:
        """Get image recommendations by content type."""
        recommendations = {
            "text_post": {
                "best_types": ["quote_graphic", "infographic"],
                "when_to_use": "Add image to boost engagement by 1.3x",
                "tip": "Use when post has quotable insight",
            },
            "thread": {
                "best_types": ["carousel_slide", "infographic"],
                "when_to_use": "First tweet and key points",
                "tip": "Consistent style across all thread images",
            },
            "video": {
                "best_types": ["thumbnail"],
                "when_to_use": "Custom thumbnail increases CTR",
                "tip": "Face + text + high contrast",
            },
            "educational": {
                "best_types": ["infographic", "data_chart", "before_after"],
                "when_to_use": "Visualize concepts and data",
                "tip": "Make complex simple through visuals",
            },
        }
        return recommendations.get(content_type, recommendations["text_post"])
