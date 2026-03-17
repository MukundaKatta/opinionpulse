"""Trend detection — detect shifts, viral moments, emerging topics."""

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np


@dataclass
class Trend:
    topic: str
    trend_type: str       # emerging, viral, shifting, declining
    strength: float       # 0.0 to 1.0
    velocity: float       # rate of change
    volume: int
    sentiment_shift: float
    first_seen: str
    description: str = ""


class TrendDetector:
    """Detect shifts in opinion, viral moments, and emerging topics."""

    def __init__(self, window_size=50, viral_threshold=3.0, emergence_threshold=2.0):
        self.window_size = window_size
        self.viral_threshold = viral_threshold
        self.emergence_threshold = emergence_threshold
        self._topic_history = {}
        self._volume_baseline = {}

    def detect_emerging_topics(self, posts, previous_posts=None):
        """Find topics that are new or rapidly growing in mentions."""
        current_words = self._extract_topic_words(posts)
        prev_words = self._extract_topic_words(previous_posts) if previous_posts else Counter()

        emerging = []
        for word, count in current_words.most_common(50):
            prev_count = prev_words.get(word, 0)
            if prev_count == 0 and count >= 3:
                emerging.append(Trend(topic=word, trend_type="emerging", strength=min(1.0, count / 10),
                                      velocity=float(count), volume=count, sentiment_shift=0.0,
                                      first_seen=datetime.utcnow().isoformat(),
                                      description=f"New topic '{word}' with {count} mentions"))
            elif prev_count > 0:
                growth = (count - prev_count) / max(prev_count, 1)
                if growth > self.emergence_threshold:
                    emerging.append(Trend(topic=word, trend_type="emerging", strength=min(1.0, growth / 5),
                                          velocity=growth, volume=count, sentiment_shift=0.0,
                                          first_seen=datetime.utcnow().isoformat(),
                                          description=f"'{word}' growing {growth:.1f}x ({prev_count} -> {count})"))
        return sorted(emerging, key=lambda t: t.strength, reverse=True)[:10]

    def detect_viral_moments(self, posts, time_window_minutes=60):
        """Detect sudden spikes in engagement/mentions."""
        if len(posts) < 5:
            return []

        scores = [p.score if hasattr(p, "score") else 0 for p in posts]
        mean_score = np.mean(scores) if scores else 0
        std_score = np.std(scores) if scores else 1

        viral = []
        for i, post in enumerate(posts):
            score = scores[i]
            if std_score > 0:
                z = (score - mean_score) / std_score
            else:
                z = 0

            if z > self.viral_threshold:
                text = post.text if hasattr(post, "text") else str(post)
                viral.append(Trend(
                    topic=text[:80], trend_type="viral", strength=min(1.0, z / 5),
                    velocity=z, volume=score, sentiment_shift=0.0,
                    first_seen=post.timestamp if hasattr(post, "timestamp") else datetime.utcnow().isoformat(),
                    description=f"Viral post (z-score={z:.1f}, score={score})"))

        return sorted(viral, key=lambda t: t.strength, reverse=True)[:5]

    def detect_sentiment_shifts(self, sentiment_scores, window=None):
        """Detect significant shifts in sentiment over time."""
        if len(sentiment_scores) < 10:
            return []

        w = window or self.window_size
        shifts = []

        # Compare rolling windows
        for i in range(w, len(sentiment_scores)):
            recent = np.mean(sentiment_scores[i - w // 2: i])
            older = np.mean(sentiment_scores[i - w: i - w // 2])
            shift = recent - older

            if abs(shift) > 0.3:
                direction = "positive" if shift > 0 else "negative"
                shifts.append(Trend(
                    topic=f"sentiment_{direction}_shift", trend_type="shifting",
                    strength=min(1.0, abs(shift)), velocity=shift,
                    volume=w, sentiment_shift=shift,
                    first_seen=datetime.utcnow().isoformat(),
                    description=f"Sentiment shifted {direction} by {abs(shift):.2f} (from {older:.2f} to {recent:.2f})"))

        # Deduplicate: only keep the strongest shift
        if shifts:
            shifts.sort(key=lambda t: t.strength, reverse=True)
            return shifts[:3]
        return []

    def detect_all(self, posts, previous_posts=None, sentiment_scores=None):
        """Run all trend detection methods and combine results."""
        trends = []
        trends.extend(self.detect_emerging_topics(posts, previous_posts))
        trends.extend(self.detect_viral_moments(posts))
        if sentiment_scores:
            trends.extend(self.detect_sentiment_shifts(sentiment_scores))
        trends.sort(key=lambda t: t.strength, reverse=True)
        return trends

    def _extract_topic_words(self, posts):
        if not posts:
            return Counter()
        stopwords = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
                     "was", "one", "our", "has", "have", "been", "this", "that", "with", "they",
                     "from", "will", "what", "when", "who", "how", "more", "some", "than", "them",
                     "its", "also", "into", "just", "about", "would", "there", "their", "could",
                     "other", "very", "much", "like", "then", "think", "really", "people"}
        all_words = []
        for p in posts:
            text = p.text if hasattr(p, "text") else str(p)
            words = re.findall(r"\b[a-z]{4,}\b", text.lower())
            all_words.extend(w for w in words if w not in stopwords)
        return Counter(all_words)
