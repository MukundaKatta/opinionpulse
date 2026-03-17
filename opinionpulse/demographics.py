"""Demographic analysis — estimate opinion distribution across demographics."""

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


@dataclass
class DemographicSegment:
    name: str
    size_estimate: int
    sentiment_avg: float
    sentiment_std: float
    top_concerns: list = field(default_factory=list)
    leaning: str = "neutral"


class DemographicAnalyzer:
    """Estimate opinion distribution across demographic segments.

    Uses proxy signals from language patterns, platform usage, and
    stated affiliations to infer demographic breakdowns.
    """

    SEGMENT_SIGNALS = {
        "young_adults": {"keywords": ["gen z", "college", "student", "university", "tiktok", "dorm"],
                         "platforms": ["twitter", "reddit"]},
        "professionals": {"keywords": ["career", "industry", "corporate", "salary", "market", "business"],
                          "platforms": ["news"]},
        "parents": {"keywords": ["kids", "children", "family", "school", "parenting"],
                    "platforms": ["reddit"]},
        "retirees": {"keywords": ["retirement", "pension", "grandchildren", "medicare", "social security"],
                     "platforms": ["news"]},
        "tech_community": {"keywords": ["developer", "programming", "startup", "tech", "ai", "software", "code"],
                           "platforms": ["reddit", "twitter"]},
    }

    def __init__(self):
        self._segments = {}

    def analyze_demographics(self, posts, sentiments):
        """Estimate demographic breakdown from posts and their sentiments."""
        segments = {}

        for seg_name, signals in self.SEGMENT_SIGNALS.items():
            matching_indices = []
            for i, post in enumerate(posts):
                text = (post.text if hasattr(post, "text") else str(post)).lower()
                source = post.source if hasattr(post, "source") else ""

                keyword_match = any(kw in text for kw in signals["keywords"])
                platform_match = source in signals.get("platforms", [])

                if keyword_match or platform_match:
                    matching_indices.append(i)

            if not matching_indices:
                continue

            seg_sentiments = [sentiments[i].score if hasattr(sentiments[i], "score") else sentiments[i]
                              for i in matching_indices if i < len(sentiments)]

            if not seg_sentiments:
                continue

            avg = float(np.mean(seg_sentiments))
            leaning = "positive" if avg > 0.15 else ("negative" if avg < -0.15 else "neutral")

            # Extract top concerns from matching posts
            from collections import Counter
            import re
            words = []
            for i in matching_indices:
                text = (posts[i].text if hasattr(posts[i], "text") else str(posts[i])).lower()
                words.extend(re.findall(r"\b[a-z]{4,}\b", text))
            stopwords = {"this", "that", "with", "from", "they", "have", "been", "about", "would", "their",
                         "could", "other", "very", "much", "like", "just", "also", "more", "some"}
            words = [w for w in words if w not in stopwords and w not in signals["keywords"]]
            top_concerns = [w for w, _ in Counter(words).most_common(5)]

            segments[seg_name] = DemographicSegment(
                name=seg_name, size_estimate=len(matching_indices),
                sentiment_avg=avg, sentiment_std=float(np.std(seg_sentiments)),
                top_concerns=top_concerns, leaning=leaning)

        self._segments = segments
        return list(segments.values())

    def compare_segments(self):
        """Compare sentiment across demographic segments."""
        if not self._segments:
            return {}
        return {
            "segments": {name: {"sentiment": s.sentiment_avg, "size": s.size_estimate, "leaning": s.leaning}
                         for name, s in self._segments.items()},
            "most_positive": max(self._segments.values(), key=lambda s: s.sentiment_avg).name if self._segments else None,
            "most_negative": min(self._segments.values(), key=lambda s: s.sentiment_avg).name if self._segments else None,
            "most_divided": max(self._segments.values(), key=lambda s: s.sentiment_std).name if self._segments else None,
        }
