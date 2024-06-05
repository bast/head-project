def _distance_squared(p1, p2) -> float:
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return dx * dx + dy * dy + dz * dz


def nearest_vertex_noddy(point, vertices) -> int:
    min_dist = float("inf")
    min_j = -1
    for j, q in enumerate(vertices):
        d = _distance_squared(point, q)
        if d < min_dist:
            min_dist = d
            min_j = j
    return min_j
