# OpinionPulse

Multi-agent public opinion analysis and narrative tracking platform.

## Features

- **Data Collection**: Scrape Reddit, Twitter/X, and news sites for topic discussions
- **Sentiment Analysis**: Fine-grained 5-class sentiment with aspect-based decomposition
- **Narrative Tracking**: Identify and track evolving narratives and talking points
- **Demographic Analysis**: Estimate opinion distribution across demographic segments
- **Trend Detection**: Detect shifts, viral moments, and emerging topics
- **Report Generation**: Create comprehensive reports with charts and summaries
- **FastAPI Server**: Real-time analysis API

## Quick Start

```python
from opinionpulse.collector import DataCollector
from opinionpulse.sentiment import SentimentAnalyzer

collector = DataCollector()
posts = collector.collect_all("artificial intelligence")

analyzer = SentimentAnalyzer()
results = analyzer.batch_analyze([p.text for p in posts])
print(f"Mean sentiment: {results['mean_score']:.2f}")
```

## API

```bash
uvicorn opinionpulse.api:app --port 8000
```

## Installation

```bash
pip install -e ".[full]"
```

## Testing

```bash
pytest tests/
```

## License

MIT
