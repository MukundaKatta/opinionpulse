"""Report generation — create visual reports with charts and summaries."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import numpy as np


@dataclass
class Report:
    title: str
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    sections: list = field(default_factory=list)
    summary: str = ""
    data: dict = field(default_factory=dict)


class ReportGenerator:
    """Create visual reports with charts and summaries from opinion analysis."""

    def __init__(self):
        self._reports = []

    def generate_report(self, topic, sentiment_data, narratives=None, trends=None):
        """Generate a comprehensive opinion analysis report."""
        sections = []

        # Overview section
        overview = self._build_overview(topic, sentiment_data)
        sections.append({"title": "Overview", "content": overview})

        # Sentiment breakdown
        sentiment_section = self._build_sentiment_section(sentiment_data)
        sections.append({"title": "Sentiment Analysis", "content": sentiment_section})

        # Narratives
        if narratives:
            narr_section = self._build_narratives_section(narratives)
            sections.append({"title": "Key Narratives", "content": narr_section})

        # Trends
        if trends:
            trend_section = self._build_trends_section(trends)
            sections.append({"title": "Trends", "content": trend_section})

        summary = self._generate_summary(topic, sentiment_data, narratives, trends)

        report = Report(title=f"Opinion Analysis: {topic}", sections=sections, summary=summary,
                        data={"topic": topic, "sentiment": sentiment_data, "n_narratives": len(narratives or []),
                              "n_trends": len(trends or [])})
        self._reports.append(report)
        return report

    def _build_overview(self, topic, sentiment_data):
        n = sentiment_data.get("count", 0)
        mean = sentiment_data.get("mean_score", 0)
        pos = sentiment_data.get("positive_pct", 0)
        neg = sentiment_data.get("negative_pct", 0)
        neu = sentiment_data.get("neutral_pct", 0)
        return {
            "topic": topic, "total_posts_analyzed": n, "overall_sentiment": mean,
            "sentiment_label": "positive" if mean > 0.1 else ("negative" if mean < -0.1 else "neutral"),
            "breakdown": {"positive": f"{pos:.1f}%", "negative": f"{neg:.1f}%", "neutral": f"{neu:.1f}%"},
        }

    def _build_sentiment_section(self, sentiment_data):
        dist = sentiment_data.get("distribution", {})
        results = sentiment_data.get("results", [])
        scores = [r.score if hasattr(r, "score") else r for r in results]
        return {
            "distribution": dist, "mean": sentiment_data.get("mean_score", 0),
            "std": sentiment_data.get("std_score", 0),
            "histogram": self._build_histogram(scores) if scores else {},
        }

    def _build_histogram(self, scores, bins=10):
        if not scores:
            return {}
        counts, edges = np.histogram(scores, bins=bins, range=(-1, 1))
        return {"counts": counts.tolist(), "edges": edges.tolist()}

    def _build_narratives_section(self, narratives):
        return [{"id": n.id, "keywords": n.keywords[:5], "summary": n.summary,
                 "sentiment": n.sentiment_avg, "mentions": n.mention_count,
                 "momentum": n.momentum, "examples": n.example_texts[:2]}
                for n in narratives[:10]]

    def _build_trends_section(self, trends):
        return [{"topic": t.topic, "type": t.trend_type, "strength": t.strength,
                 "velocity": t.velocity, "description": t.description}
                for t in trends[:10]]

    def _generate_summary(self, topic, sentiment_data, narratives, trends):
        mean = sentiment_data.get("mean_score", 0)
        n = sentiment_data.get("count", 0)
        parts = [f"Analysis of {n} posts about '{topic}'."]

        if mean > 0.2:
            parts.append(f"Overall sentiment is strongly positive ({mean:.2f}).")
        elif mean > 0.05:
            parts.append(f"Overall sentiment is mildly positive ({mean:.2f}).")
        elif mean < -0.2:
            parts.append(f"Overall sentiment is strongly negative ({mean:.2f}).")
        elif mean < -0.05:
            parts.append(f"Overall sentiment is mildly negative ({mean:.2f}).")
        else:
            parts.append(f"Overall sentiment is neutral ({mean:.2f}).")

        if narratives:
            top = narratives[0]
            parts.append(f"Dominant narrative: {top.summary} ({top.mention_count} mentions).")

        if trends:
            emerging = [t for t in trends if t.trend_type == "emerging"]
            if emerging:
                parts.append(f"Emerging topics: {', '.join(t.topic for t in emerging[:3])}.")

        return " ".join(parts)

    def to_text(self, report):
        """Convert report to plain text format."""
        lines = [f"{'=' * 60}", f"  {report.title}", f"  Generated: {report.generated_at}", f"{'=' * 60}", ""]
        lines.append(f"SUMMARY: {report.summary}")
        lines.append("")
        for section in report.sections:
            lines.append(f"--- {section['title']} ---")
            content = section["content"]
            if isinstance(content, dict):
                for k, v in content.items():
                    lines.append(f"  {k}: {v}")
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        lines.append(f"  - {item.get('summary', item.get('topic', str(item)))}")
            lines.append("")
        return "\n".join(lines)

    def generate_chart_data(self, sentiment_data):
        """Generate data structures for chart rendering."""
        results = sentiment_data.get("results", [])
        scores = [r.score if hasattr(r, "score") else r for r in results]
        dist = sentiment_data.get("distribution", {})
        return {
            "pie_chart": {"labels": list(dist.keys()), "values": list(dist.values())},
            "histogram": self._build_histogram(scores),
            "timeline": {"scores": scores, "indices": list(range(len(scores)))},
        }
