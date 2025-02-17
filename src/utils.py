def seconds_to_time_str(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}min")
    if sec:
        parts.append(f"{sec}s")

    return " ".join(parts)


def repetitions_to_str(reps: int) -> str:
    time = "times" if reps > 1 else "time"
    return f"{reps} {time}"


def duration_input_to_seconds(value: str):
    cleaned = value.replace(":", "")

    seconds = 0

    if not cleaned:
        return seconds

    if len(cleaned) >= 2:
        seconds += int(cleaned[0:2]) * 3600  # Add hours

    if len(cleaned) >= 4:
        seconds += int(cleaned[2:4]) * 60  # Add minutes

    if len(cleaned) >= 6:
        seconds += int(cleaned[4:6])  # Add seconds

    return seconds
