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
    indices = set()
    for i, j, k in vertices:
        d[tuple(sorted([i, j]))] += 1
        d[tuple(sorted([j, k]))] += 1
        d[tuple(sorted([k, i]))] += 1
        indices.add(i)
        indices.add(j)
        indices.add(k)

    stats = defaultdict(int)
    for v in d.values():
        stats[v] += 1
    print(stats)
    print(min(indices), max(indices))


def cycle(i, j, k):
    return [tuple(sorted([i, j])), tuple(sorted([j, k])), tuple(sorted([k, i]))]


def filter_problem_triangles(vertices):
    d = defaultdict(int)
    edge_to_triangles = defaultdict(list)

    all_triangles = set()
    for i, j, k in vertices:
        ijk = tuple(sorted([i, j, k]))
        all_triangles.add(ijk)
        for ij in cycle(i, j, k):
            d[ij] += 1
            edge_to_triangles[ij].append(ijk)

    problem_triangles = set()
    for k, v in d.items():
        if v > 2:
            for triangle in edge_to_triangles[k]:
                problem_triangles.add(triangle)

    # set of triangles that are not problem triangles
    good_triangles = all_triangles - problem_triangles

    return list(good_triangles)


points, vertices = read_mesh("data.txt")
get_stats(vertices)

vertices = filter_problem_triangles(vertices)
get_stats(vertices)
