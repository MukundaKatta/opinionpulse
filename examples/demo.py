"""Example: Track public opinion on a topic."""

from opinionpulse.collector import DataCollector
from opinionpulse.sentiment import SentimentAnalyzer
from opinionpulse.narratives import NarrativeTracker
from opinionpulse.trends import TrendDetector
from opinionpulse.demographics import DemographicAnalyzer
from opinionpulse.report import ReportGenerator


def main():
    topic = "artificial intelligence"
    print(f"=== OpinionPulse: Analyzing '{topic}' ===\n")

    collector = DataCollector()
    posts = collector.collect_all(topic, reddit_limit=30, twitter_limit=30, news_limit=10)
    print(f"Collected {len(posts)} posts from {len(set(p.source for p in posts))} sources\n")

    analyzer = SentimentAnalyzer()
    sentiment_data = analyzer.batch_analyze([p.text for p in posts])
    print(f"Sentiment: mean={sentiment_data['mean_score']:.2f}, "
          f"positive={sentiment_data['positive_pct']:.1f}%, negative={sentiment_data['negative_pct']:.1f}%")
    print(f"Distribution: {sentiment_data['distribution']}\n")

    tracker = NarrativeTracker(min_mentions=2)
    sentiments = sentiment_data["results"]
    narratives = tracker.identify_narratives(posts, sentiments)
    print(f"Found {len(narratives)} narratives:")
    for n in narratives[:5]:
        print(f"  - {n.summary} (mentions={n.mention_count}, sentiment={n.sentiment_avg:.2f})")

    detector = TrendDetector()
    trends = detector.detect_all(posts, sentiment_scores=[s.score for s in sentiments])
    print(f"\nDetected {len(trends)} trends:")
    for t in trends[:5]:
        print(f"  - [{t.trend_type}] {t.description}")

    demo_analyzer = DemographicAnalyzer()
    demographics = demo_analyzer.analyze_demographics(posts, sentiments)
    print(f"\nDemographic segments: {len(demographics)}")
    for d in demographics:
        print(f"  - {d.name}: sentiment={d.sentiment_avg:.2f}, leaning={d.leaning}, size={d.size_estimate}")

    gen = ReportGenerator()
    report = gen.generate_report(topic, sentiment_data, narratives, trends)
    print(f"\n{'=' * 50}")
    print(gen.to_text(report))


if __name__ == "__main__":
    main()
