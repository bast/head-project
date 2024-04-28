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
