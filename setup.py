from setuptools import setup, find_packages

setup(
    name="opinionpulse",
    version="0.1.0",
    description="Multi-agent public opinion analysis and narrative tracking platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MukundaKatta",
    url="https://github.com/MukundaKatta/opinionpulse",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["numpy>=1.24", "pydantic>=2.0", "fastapi>=0.100"],
    extras_require={
        "full": ["transformers>=4.30", "praw>=7.7", "tweepy>=4.14", "matplotlib>=3.7", "pandas>=2.0"],
        "dev": ["pytest>=7.0", "httpx>=0.24"],
    },
)
