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
