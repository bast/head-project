def _is_float(x) -> bool:
    if x is None:
        return False
    try:
        float(x)
        return True
    except ValueError:
        return False


def _floats_are_different(a: float, b: float, eps=1e-6) -> bool:
    if a is None or b is None:
        return True
    return abs(a - b) > eps


def reference_point_moved(reference_point, state) -> bool:
    x, y, z = reference_point
    if not (_is_float(x) and _is_float(y) and _is_float(z)):
        return False

    x = float(x)
    y = float(y)
    z = float(z)

    if state["reference_point"] is None:
        return True

    x_prev, y_prev, z_prev = tuple(state["reference_point"])

    if (
        _floats_are_different(x, x_prev)
        or _floats_are_different(y, y_prev)
        or _floats_are_different(z, z_prev)
    ):
        return True
