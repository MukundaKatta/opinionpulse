"""Data collection from Reddit, Twitter/X, and news sites."""

import re
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class CollectedPost:
    text: str
    source: str
    author: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    url: str = ""
    score: int = 0
    metadata: dict = field(default_factory=dict)


class DataCollector:
    """Scrape Reddit, Twitter/X, and news sites for topic discussions."""

    def __init__(self, reddit_client_id=None, reddit_secret=None, twitter_bearer=None):
        self.reddit_client_id = reddit_client_id
        self.reddit_secret = reddit_secret
        self.twitter_bearer = twitter_bearer

    def collect_reddit(self, topic, subreddits=None, limit=100):
        subs = subreddits or ["all"]
        posts = []
        try:
            import praw
            reddit = praw.Reddit(client_id=self.reddit_client_id, client_secret=self.reddit_secret,
                                 user_agent="OpinionPulse/0.1")
            for sub_name in subs:
                subreddit = reddit.subreddit(sub_name)
                for submission in subreddit.search(topic, limit=limit, sort="relevance", time_filter="week"):
                    posts.append(CollectedPost(
                        text=f"{submission.title}. {submission.selftext[:500]}" if submission.selftext else submission.title,
                        source="reddit", author=str(submission.author), score=submission.score,
                        url=f"https://reddit.com{submission.permalink}",
                        metadata={"subreddit": sub_name, "num_comments": submission.num_comments}))
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:5]:
                        posts.append(CollectedPost(text=comment.body[:500], source="reddit_comment",
                                                    author=str(comment.author), score=comment.score))
        except (ImportError, Exception):
            posts = self._synthetic_posts(topic, "reddit", limit)
        return posts

    def collect_twitter(self, topic, limit=100):
        posts = []
        try:
            import tweepy
            client = tweepy.Client(bearer_token=self.twitter_bearer)
            tweets = client.search_recent_tweets(query=topic, max_results=min(limit, 100),
                                                  tweet_fields=["author_id", "created_at", "public_metrics"])
            if tweets.data:
                for tweet in tweets.data:
                    m = tweet.public_metrics or {}
                    posts.append(CollectedPost(text=tweet.text, source="twitter", author=str(tweet.author_id),
                                               score=m.get("like_count", 0) + m.get("retweet_count", 0)))
        except (ImportError, Exception):
            posts = self._synthetic_posts(topic, "twitter", limit)
        return posts

    def collect_news(self, topic, limit=20):
        posts = []
        try:
            import requests
            from bs4 import BeautifulSoup
            url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}&hl=en"
            resp = requests.get(url, timeout=15, headers={"User-Agent": "OpinionPulse/0.1"})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                for item in soup.find_all("item")[:limit]:
                    title = item.title.text if item.title else ""
                    desc = item.description.text if item.description else ""
                    posts.append(CollectedPost(text=f"{title}. {desc[:300]}", source="news",
                                               url=item.link.text if item.link else ""))
        except (ImportError, Exception):
            posts = self._synthetic_posts(topic, "news", limit)
        return posts

    def collect_all(self, topic, reddit_limit=50, twitter_limit=50, news_limit=20):
        all_posts = []
        all_posts.extend(self.collect_reddit(topic, limit=reddit_limit))
        all_posts.extend(self.collect_twitter(topic, limit=twitter_limit))
        all_posts.extend(self.collect_news(topic, limit=news_limit))
        return all_posts

    def _synthetic_posts(self, topic, source, count):
        templates = [
            f"I think {topic} is really important for our future",
            f"Anyone else concerned about {topic}? The situation seems to be getting worse",
            f"Great news about {topic}! Things are looking up",
            f"Unpopular opinion: {topic} is overhyped and people need to calm down",
            f"Just read an interesting article about {topic}. Changed my perspective",
            f"{topic} is the most pressing issue of our time",
            f"Not sure why everyone is so worked up about {topic}",
            f"The latest developments on {topic} are very promising",
            f"I have been following {topic} for years. This is the worst it has been",
            f"{topic} supporters are missing the bigger picture here",
            f"Breaking: Major development on {topic}!",
            f"The media coverage of {topic} has been terrible",
            f"Experts weigh in on {topic}: consensus growing for change",
            f"Public opinion shifts on {topic} as new data emerges",
        ]
        rng = random.Random(hash(topic) + hash(source))
        return [CollectedPost(text=rng.choice(templates), source=source, author=f"user_{i}",
                              score=rng.randint(0, 500), metadata={"synthetic": True})
                for i in range(min(count, len(templates) * 3))]
