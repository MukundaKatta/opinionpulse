"""Narrative tracking — identify and track evolving narratives and talking points."""

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np


@dataclass
class Narrative:
    id: str
    keywords: list
    summary: str
    sentiment_avg: float
    mention_count: int
    first_seen: str
    last_seen: str
    example_texts: list = field(default_factory=list)
    momentum: float = 0.0


class NarrativeTracker:
    """Identify, cluster, and track evolving narratives in public discourse."""

    STOPWORDS = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
                 "was", "one", "our", "out", "has", "have", "been", "this", "that",
                 "with", "they", "from", "will", "what", "when", "who", "how", "which",
                 "more", "some", "than", "them", "its", "also", "into", "just", "about",
                 "would", "there", "their", "could", "other", "very", "much", "like", "then"}

    def __init__(self, min_mentions=3, similarity_threshold=0.3):
        self.min_mentions = min_mentions
        self.similarity_threshold = similarity_threshold
        self._narratives = {}

    def extract_keywords(self, text, top_n=10):
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        filtered = [w for w in words if w not in self.STOPWORDS]
        return [w for w, _ in Counter(filtered).most_common(top_n)]

    def _jaccard(self, a, b):
        s1, s2 = set(a), set(b)
        union = s1 | s2
        return len(s1 & s2) / len(union) if union else 0.0

    def identify_narratives(self, posts, sentiments=None):
        post_kws = [self.extract_keywords(p.text if hasattr(p, "text") else str(p), 8) for p in posts]
        n = len(posts)
        clusters, assigned = [], set()

        for i in range(n):
            if i in assigned:
                continue
            cluster = [i]
            assigned.add(i)
            for j in range(i + 1, n):
                if j not in assigned and self._jaccard(post_kws[i], post_kws[j]) >= self.similarity_threshold:
                    cluster.append(j)
                    assigned.add(j)
            if len(cluster) >= self.min_mentions:
                clusters.append(cluster)

        narratives = []
        for idx, cluster in enumerate(clusters):
            all_kws, examples, scores = [], [], []
            for i in cluster:
                all_kws.extend(post_kws[i])
                examples.append((posts[i].text if hasattr(posts[i], "text") else str(posts[i]))[:200])
                if sentiments and i < len(sentiments):
                    scores.append(sentiments[i].score if hasattr(sentiments[i], "score") else 0)
            top_kws = [w for w, _ in Counter(all_kws).most_common(5)]
            now = datetime.utcnow().isoformat()
            narr = Narrative(id=f"narrative_{idx}", keywords=top_kws,
                             summary=f"Narrative about {', '.join(top_kws[:3])}",
                             sentiment_avg=float(np.mean(scores)) if scores else 0.0,
                             mention_count=len(cluster), first_seen=now, last_seen=now,
                             example_texts=examples[:3])
            narratives.append(narr)
            self._narratives[narr.id] = narr
        return narratives

    def track_evolution(self, new_posts, new_sentiments=None):
        new_narratives = self.identify_narratives(new_posts, new_sentiments)
        for nn in new_narratives:
            matched = False
            for eid, existing in self._narratives.items():
                if eid == nn.id:
                    continue
                if self._jaccard(nn.keywords, existing.keywords) > 0.5:
                    existing.mention_count += nn.mention_count
                    existing.last_seen = nn.last_seen
                    existing.sentiment_avg = (existing.sentiment_avg + nn.sentiment_avg) / 2
                    existing.momentum = nn.mention_count / max(existing.mention_count, 1) - 0.5
                    matched = True
                    break
            if not matched:
                nn.momentum = 1.0
                self._narratives[nn.id] = nn
        return list(self._narratives.values())

    def get_trending(self, top_n=5):
        return sorted(self._narratives.values(), key=lambda n: n.momentum, reverse=True)[:top_n]
