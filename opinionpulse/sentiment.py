"""Sentiment analysis with fine-grained (5-class) and aspect-based analysis."""

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SentimentScore:
    label: str
    score: float
    confidence: float
    probabilities: dict = field(default_factory=dict)


@dataclass
class AspectSentiment:
    aspect: str
    sentiment: SentimentScore
    mentions: int = 1
    snippets: list = field(default_factory=list)


class SentimentAnalyzer:
    """Fine-grained 5-class sentiment analysis with aspect-based decomposition."""

    POSITIVE = {"good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "best",
                "happy", "excited", "support", "agree", "progress", "improvement", "success",
                "positive", "beneficial", "promising", "optimistic", "hope", "brilliant", "perfect",
                "outstanding", "impressive", "effective", "strong", "gain", "innovative", "growth", "opportunity"}
    NEGATIVE = {"bad", "terrible", "awful", "horrible", "worst", "hate", "angry", "upset",
                "concerned", "worried", "disagree", "decline", "failure", "problem", "crisis",
                "negative", "harmful", "dangerous", "pessimistic", "fear", "disaster", "corrupt",
                "disappointing", "weak", "loss", "threat", "risk", "damage", "waste", "broken",
                "unfair", "misleading", "fraud", "scandal", "controversy", "protest"}
    VERY_POS = {"excellent", "amazing", "wonderful", "fantastic", "outstanding", "brilliant", "perfect"}
    VERY_NEG = {"terrible", "awful", "horrible", "worst", "disaster", "corrupt", "fraud", "scandal"}
    INTENSIFIERS = {"very", "extremely", "incredibly", "absolutely", "completely", "totally"}
    NEGATORS = {"not", "no", "never", "neither", "nor", "hardly", "barely"}

    def analyze(self, text):
        words = re.findall(r"\b[a-z]+\b", text.lower())
        pos_score, neg_score, very_pos, very_neg = 0.0, 0.0, 0, 0
        for i, word in enumerate(words):
            mult = 1.0
            for j in range(max(0, i - 3), i):
                if words[j] in self.NEGATORS:
                    mult *= -1.0
                    break
            for j in range(max(0, i - 2), i):
                if words[j] in self.INTENSIFIERS:
                    mult *= 1.5
            if word in self.POSITIVE:
                if mult > 0:
                    pos_score += abs(mult)
                    if word in self.VERY_POS:
                        very_pos += 1
                else:
                    neg_score += abs(mult)
            elif word in self.NEGATIVE:
                if mult > 0:
                    neg_score += abs(mult)
                    if word in self.VERY_NEG:
                        very_neg += 1
                else:
                    pos_score += abs(mult)

        total = max(len(words) * 0.05, 1)
        raw = float(np.clip((pos_score - neg_score) / total, -1.0, 1.0))

        if raw > 0.4 or very_pos > 0:
            label = "very_positive"
        elif raw > 0.1:
            label = "positive"
        elif raw < -0.4 or very_neg > 0:
            label = "very_negative"
        elif raw < -0.1:
            label = "negative"
        else:
            label = "neutral"

        confidence = min(1.0, (pos_score + neg_score) / max(total, 1))
        probs = {l: 0.0 for l in ["very_negative", "negative", "neutral", "positive", "very_positive"]}
        probs[label] = max(0.4, confidence)
        rem = 1.0 - probs[label]
        for l in probs:
            if l != label:
                probs[l] = rem / 4

        return SentimentScore(label=label, score=raw, confidence=confidence, probabilities=probs)

    def analyze_aspects(self, text, aspects=None):
        if aspects is None:
            aspects = self._extract_aspects(text)
        results = []
        sentences = re.split(r"[.!?]+", text)
        for aspect in aspects:
            relevant = [s for s in sentences if aspect.lower() in s.lower()]
            if not relevant:
                continue
            sentiment = self.analyze(" ".join(relevant))
            results.append(AspectSentiment(aspect=aspect, sentiment=sentiment,
                                           mentions=len(relevant), snippets=[s.strip() for s in relevant[:3]]))
        return results

    def _extract_aspects(self, text):
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        freq = {}
        for w in words:
            if w not in self.POSITIVE and w not in self.NEGATIVE and w not in self.INTENSIFIERS:
                freq[w] = freq.get(w, 0) + 1
        return [w for w, c in sorted(freq.items(), key=lambda x: -x[1]) if c >= 2][:10]

    def batch_analyze(self, texts):
        results = [self.analyze(t) for t in texts]
        scores = [r.score for r in results]
        dist = {}
        for r in results:
            dist[r.label] = dist.get(r.label, 0) + 1
        n = len(results)
        return {
            "results": results, "count": n,
            "mean_score": float(np.mean(scores)), "std_score": float(np.std(scores)),
            "distribution": dist,
            "positive_pct": sum(1 for r in results if r.score > 0.1) / n * 100,
            "negative_pct": sum(1 for r in results if r.score < -0.1) / n * 100,
            "neutral_pct": sum(1 for r in results if abs(r.score) <= 0.1) / n * 100,
        }
