from src.utils import seconds_to_time_str


def test_seconds_to_time_str_default():
    result = seconds_to_time_str(3967)
    assert result == "1h 6min 7s"


def test_seconds_to_time_str_no_hour():
    result = seconds_to_time_str(367)
    assert result == "6min 7s"


def test_seconds_to_time_str_no_minute():
    result = seconds_to_time_str(3607)
    assert result == "1h 7s"


def test_seconds_to_time_str_no_minute_no_hour():
    result = seconds_to_time_str(7)
    assert result == "7s"
