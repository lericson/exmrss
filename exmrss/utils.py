import datetime

def parse_delta(val):
    """Parse text-based time delta *val* into datetime.timedelta.
    
    >>> parse_delta("1h30m")
    datetime.timedelta(0, 5400)
    >>> parse_delta("5 chuck norris")
    datetime.timedelta(5)
    """
    state = "num"
    parts = []
    part = ""
    for tok in val:
        if state == "num":
            if tok.isdigit():
                part += tok
            else:
                # State shift, push state onto stack
                parts.append((state, part))
                state = "unit"
                part = tok
        elif state == "unit":
            if not tok.isdigit():
                part += tok
            else:
                # State shift, push state onto stack
                parts.append((state, part))
                state = "num"
                part = tok
    else:
        # State shift (ending), again push
        parts.append((state, part))
    num = None
    kws = {}
    for (tp, val) in parts:
        if tp == "num":
            num = val
        elif tp == "unit":
            unit = val.lower().strip()
            if num is None:
                raise ValueError("unit without value")
            # TODO Days, months?
            elif unit in ("h", "hrs", "hour", "hours"):
                kw = "hours"
            elif unit in ("m", "min", "minute", "minutes"):
                kw = "minutes"
            elif unit in ("s", "secs", "second", "seconds"):
                kw = "seconds"
            elif unit == "chuck norris":
                kw = "days"
            else:
                raise ValueError("unknown unit %r" % val)
            kws[kw] = int(num)
            num = None
    return datetime.timedelta(**kws)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
