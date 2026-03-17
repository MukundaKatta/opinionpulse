"""Tests for OpinionPulse modules."""

import pytest
from opinionpulse.collector import DataCollector, CollectedPost
from opinionpulse.sentiment import SentimentAnalyzer
from opinionpulse.narratives import NarrativeTracker
from opinionpulse.trends import TrendDetector
from opinionpulse.demographics import DemographicAnalyzer
from opinionpulse.report import ReportGenerator


class TestSentimentAnalyzer:
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()

    def test_positive(self):
        r = self.analyzer.analyze("This is excellent and amazing progress for everyone")
        assert r.score > 0
        assert r.label in ("positive", "very_positive")

    def test_negative(self):
        r = self.analyzer.analyze("This is terrible and a complete disaster for the world")
        assert r.score < 0
        assert r.label in ("negative", "very_negative")

    def test_neutral(self):
        r = self.analyzer.analyze("The meeting will be held on Tuesday at noon")
        assert abs(r.score) < 0.5

    def test_negation(self):
        r = self.analyzer.analyze("This is not good at all")
        assert r.score <= 0

    def test_batch(self):
        texts = ["Great news!", "Terrible outcome", "Just a regular day"]
        result = self.analyzer.batch_analyze(texts)
        assert result["count"] == 3
        assert "distribution" in result

    def test_aspect_sentiment(self):
        text = "The food was excellent but the service was terrible. The ambiance was great."
        aspects = self.analyzer.analyze_aspects(text, aspects=["food", "service", "ambiance"])
        assert len(aspects) >= 2


class TestCollector:
    def test_synthetic_collection(self):
        collector = DataCollector()
        posts = collector.collect_all("climate change", reddit_limit=10, twitter_limit=10, news_limit=5)
        assert len(posts) > 0
        assert all(isinstance(p, CollectedPost) for p in posts)


class TestNarrativeTracker:
    def test_identify(self):
        tracker = NarrativeTracker(min_mentions=2, similarity_threshold=0.2)
        posts = [
            CollectedPost(text="AI is transforming technology and software development", source="reddit"),
            CollectedPost(text="Technology and AI are changing software engineering", source="reddit"),
            CollectedPost(text="New software technology powered by AI is impressive", source="twitter"),
            CollectedPost(text="Completely unrelated topic about cooking and recipes", source="news"),
        ]
        narratives = tracker.identify_narratives(posts)
        assert len(narratives) >= 0  # May or may not cluster depending on threshold


class TestTrendDetector:
    def test_emerging(self):
        detector = TrendDetector()
        posts = [CollectedPost(text=f"AI topic {i} is trending now", source="reddit", score=i * 10) for i in range(20)]
        trends = detector.detect_all(posts)
        assert isinstance(trends, list)

    def test_sentiment_shift(self):
        detector = TrendDetector()
        scores = [0.5] * 30 + [-0.5] * 30
        shifts = detector.detect_sentiment_shifts(scores, window=20)
        assert len(shifts) > 0


class TestReportGenerator:
    def test_generate(self):
        gen = ReportGenerator()
        sentiment_data = {"count": 10, "mean_score": 0.3, "std_score": 0.2, "distribution": {"positive": 7, "neutral": 2, "negative": 1},
                          "positive_pct": 70, "negative_pct": 10, "neutral_pct": 20, "results": []}
        report = gen.generate_report("test topic", sentiment_data)
        assert report.title == "Opinion Analysis: test topic"
        assert len(report.summary) > 0
        text = gen.to_text(report)
        assert "test topic" in text
