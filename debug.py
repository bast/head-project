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


points, vertices = read_mesh("data.txt")


def sorted(i, j):
    return (i, j) if i < j else (j, i)


from collections import defaultdict

d = defaultdict(int)
for i, j, k in vertices:
    d[sorted(i, j)] += 1
    d[sorted(j, k)] += 1
    d[sorted(k, i)] += 1

stats = defaultdict(int)
for v in d.values():
    stats[v] += 1
print(stats)
