from src.core import OpinionTracker
def test_init(): assert OpinionTracker().get_stats()["ops"] == 0
def test_op(): c = OpinionTracker(); c.collect_data(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = OpinionTracker(); [c.collect_data() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = OpinionTracker(); c.collect_data(); c.reset(); assert c.get_stats()["ops"] == 0
