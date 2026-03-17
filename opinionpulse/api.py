"""FastAPI endpoints for real-time opinion analysis."""

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from opinionpulse.collector import DataCollector
from opinionpulse.sentiment import SentimentAnalyzer
from opinionpulse.narratives import NarrativeTracker
from opinionpulse.trends import TrendDetector
from opinionpulse.demographics import DemographicAnalyzer
from opinionpulse.report import ReportGenerator

app = FastAPI(title="OpinionPulse API", version="0.1.0")

collector = DataCollector()
analyzer = SentimentAnalyzer()
narrative_tracker = NarrativeTracker()
trend_detector = TrendDetector()
demographic_analyzer = DemographicAnalyzer()
report_generator = ReportGenerator()


class AnalyzeRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    sources: list = Field(default=["reddit", "twitter", "news"])
    limit: int = Field(50, ge=1, le=500)


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_topic(request: AnalyzeRequest):
    posts = collector.collect_all(request.topic, reddit_limit=request.limit,
                                  twitter_limit=request.limit, news_limit=min(request.limit, 20))
    if not posts:
        raise HTTPException(404, "No data found for topic")

    texts = [p.text for p in posts]
    sentiment_data = analyzer.batch_analyze(texts)
    sentiments = sentiment_data["results"]
    narratives = narrative_tracker.identify_narratives(posts, sentiments)
    trends = trend_detector.detect_all(posts, sentiment_scores=[s.score for s in sentiments])
    demographics = demographic_analyzer.analyze_demographics(posts, sentiments)

    report = report_generator.generate_report(request.topic, sentiment_data, narratives, trends)

    return {
        "topic": request.topic, "posts_analyzed": len(posts),
        "sentiment": {"mean": sentiment_data["mean_score"], "distribution": sentiment_data["distribution"],
                      "positive_pct": sentiment_data["positive_pct"], "negative_pct": sentiment_data["negative_pct"]},
        "narratives": [{"keywords": n.keywords, "summary": n.summary, "sentiment": n.sentiment_avg,
                        "mentions": n.mention_count} for n in narratives[:5]],
        "trends": [{"topic": t.topic, "type": t.trend_type, "strength": t.strength} for t in trends[:5]],
        "demographics": [{"segment": d.name, "sentiment": d.sentiment_avg, "leaning": d.leaning}
                         for d in demographics],
        "summary": report.summary,
    }


@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    result = analyzer.analyze(request.text)
    return {"label": result.label, "score": result.score, "confidence": result.confidence,
            "probabilities": result.probabilities}


@app.get("/narratives/{topic}")
async def get_narratives(topic: str):
    posts = collector.collect_all(topic, reddit_limit=50, twitter_limit=50, news_limit=10)
    texts = [p.text for p in posts]
    sentiments = [analyzer.analyze(t) for t in texts]
    narratives = narrative_tracker.identify_narratives(posts, sentiments)
    return {"topic": topic, "narratives": [{"id": n.id, "keywords": n.keywords, "summary": n.summary,
                                             "sentiment": n.sentiment_avg, "mentions": n.mention_count}
                                            for n in narratives]}


@app.get("/trends/{topic}")
async def get_trends(topic: str):
    posts = collector.collect_all(topic, reddit_limit=100, twitter_limit=100, news_limit=20)
    sentiments = [analyzer.analyze(p.text).score for p in posts]
    trends = trend_detector.detect_all(posts, sentiment_scores=sentiments)
    return {"topic": topic, "trends": [{"topic": t.topic, "type": t.trend_type,
                                         "strength": t.strength, "description": t.description}
                                        for t in trends]}
