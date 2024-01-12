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


# keep only points and triangles where z > 0
def filter_vertices(points, vertices):
    new_points = []
    indices = {}
    j = 0
    for i, (x, y, z) in enumerate(points):
        if z > 0.0:
            indices[i] = j
            new_points.append((x, y, z))
            j += 1

    new_vertices = []
    for i, j, k in vertices:
        if i in indices and j in indices and k in indices:
            new_vertices.append((indices[i], indices[j], indices[k]))

    return new_points, new_vertices


def remove_unreferenced_indices(points, vertices):
    indices = set()
    for i, j, k in vertices:
        indices.add(i)
        indices.add(j)
        indices.add(k)

    new_points = []
    new_indices = {}
    j = 0
    for i in indices:
        new_points.append(points[i])
        new_indices[i] = j
        j += 1

    new_vertices = []
    for i, j, k in vertices:
        new_vertices.append((new_indices[i], new_indices[j], new_indices[k]))

    return new_points, new_vertices


points = []
for p in V:
    x, y, z = tuple(p.tolist())
    points.append((x, y, z))

vertices = []
for v in F:
    i, j, k = tuple(v.tolist())
    vertices.append((i, j, k))


points, vertices = filter_vertices(points, vertices)
points, vertices = remove_unreferenced_indices(points, vertices)

points = np.array(points)
vertices = np.array(vertices)

_solver = pp3d.EdgeFlipGeodesicSolver(points, vertices)
result = _solver.find_geodesic_path(v_start=0, v_end=3)
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
