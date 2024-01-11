import potpourri3d as pp3d
import numpy as np

V, F = pp3d.read_mesh("bunny_small.ply")

print(V)
print(F)

# shares precomputation for repeated solves
path_solver = pp3d.EdgeFlipGeodesicSolver(V, F)

path_pts = path_solver.find_geodesic_path(v_start=14, v_end=22)

# path_pts is a Vx3 numpy array of points forming the path
print(path_pts)


points = []
for p in V:
    x, y, z = tuple(p.tolist())
    points.append((x, y, z))

vertices = []
for v in F:
    i, j, k = tuple(v.tolist())
    vertices.append((i, j, k))


points = np.array(points)
vertices = np.array(vertices)

_solver = pp3d.EdgeFlipGeodesicSolver(points, vertices)
result = _solver.find_geodesic_path(v_start=14, v_end=22)
print(result)


def sorted(i, j):
    return (i, j) if i < j else (j, i)


from collections import defaultdict

d = defaultdict(int)
for i, j, k in vertices:
    d[sorted(i, j)] += 1
    d[sorted(j, k)] += 1
    d[sorted(k, i)] += 1

print(set(d.values()))
