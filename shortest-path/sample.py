import potpourri3d as pp3d
import numpy as np
from collections import defaultdict

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


_ = vertices.pop()

points = np.array(points)
vertices = np.array(vertices)

_solver = pp3d.EdgeFlipGeodesicSolver(points, vertices)
result = _solver.find_geodesic_path(v_start=14, v_end=22)
print(result)


d = defaultdict(int)
indices = set()
for i, j, k in vertices:
    d[tuple(sorted([i, j]))] += 1
    d[tuple(sorted([j, k]))] += 1
    d[tuple(sorted([k, i]))] += 1
    indices.add(i)
    indices.add(j)
    indices.add(k)

print(set(d.values()))

print(len(points), min(indices), max(indices))
