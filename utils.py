from datetime import timedelta


def humanize(delta: timedelta) -> str:
    seconds = delta.total_seconds()
    parts = []

    for unit in ('seconds', 'minutes', 'hours', 'days'):
        seconds, mod = divmod(seconds, 60)
        mod = int(mod)
        if mod == 0:
            continue
        elif mod == 1:
            unit = unit[:-1]
        parts.append(f'{mod} {unit}')
    parts.reverse()

    return (
        ', '.join(parts[:-1]) +
        (' and ' if len(parts) > 1 else '') +
        f'{parts[-1]} ago'
    )
