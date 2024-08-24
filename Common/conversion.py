async def SecondsToString(ss: int):
    if ss is None:
        return "0"
    _duration = {
        'hours': ss // 3600,
        'minutes': ss % 3600 // 60,
        'seconds': ss % 60
    }
    return f"{_duration['hours']:02d}:{_duration['minutes']:02d}:{_duration['seconds']:02d}"