from collections import defaultdict


def read_mesh(datafile):
    points = []
    vertices = []

    with open(datafile, "r") as f:
        # how many points?
        n = int(f.readline())
        for _ in range(n):
            _x, _y, _z = map(float, f.readline().split())
            points.append((_x, _y, _z))
        # how many triangles?
        n = int(f.readline())
        for _ in range(n):
            _i, _j, _k = map(int, f.readline().split())
            vertices.append((_i, _j, _k))

    return points, vertices


def get_stats(vertices):
    d = defaultdict(int)
    for i, j, k in vertices:
        d[tuple(sorted([i, j]))] += 1
        d[tuple(sorted([j, k]))] += 1
        d[tuple(sorted([k, i]))] += 1

    stats = defaultdict(int)
    for v in d.values():
        stats[v] += 1
    print(stats)


points, vertices = read_mesh("data.txt")
get_stats(vertices)
