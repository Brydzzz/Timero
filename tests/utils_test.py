from utils.time_strings import duration_input_to_seconds, seconds_to_time_str


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


def test_duration_input_to_seconds_default():
    result = duration_input_to_seconds("01:06:07")
    assert result == 3967


def test_duration_input_to_seconds_no_hour():
    result = duration_input_to_seconds("00:06:07")
    assert result == 367


def test_duration_input_to_seconds_no_minute():
    result = duration_input_to_seconds("01:00:07")
    assert result == 3607


def test_duration_input_to_seconds_no_minute_no_hour():
    result = duration_input_to_seconds("00:00:07")
    assert result == 7
