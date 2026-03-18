# opinionpulse

**Multi-agent public opinion analysis assistant — track sentiment, narratives, and discourse shifts**

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-proprietary-red)

## Install
```bash
pip install -e ".[dev]"
```

## Quick Start
```python
from src.core import Opinionpulse
 instance = Opinionpulse()
r = instance.collect_data(input="test")
```

## CLI
```bash
python -m src status
python -m src run --input "data"
```

## API
| Method | Description |
|--------|-------------|
| `collect_data()` | Collect data |
| `analyze_sentiment()` | Analyze sentiment |
| `track_narrative()` | Track narrative |
| `detect_shift()` | Detect shift |
| `generate_report()` | Generate report |
| `get_trends()` | Get trends |
| `get_stats()` | Get stats |
| `reset()` | Reset |

## Test
```bash
pytest tests/ -v
```

## License
(c) 2026 Officethree Technologies. All Rights Reserved.
