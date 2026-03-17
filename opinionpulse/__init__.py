"""OpinionPulse - Public Opinion Analysis Platform."""
__version__ = "0.1.0"

from opinionpulse.collector import DataCollector
from opinionpulse.sentiment import SentimentAnalyzer

__all__ = ["DataCollector", "SentimentAnalyzer"]
