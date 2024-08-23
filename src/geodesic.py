import potpourri3d as pp3d
import numpy as np


def create_solver(vertices, faces):
    vertices = np.array(vertices)
    faces = np.array(faces)
    return pp3d.EdgeFlipGeodesicSolver(vertices, faces)


def find_path(solver, v_start, v_end):
    points = []
    for p in solver.find_geodesic_path(v_start, v_end):
        x, y, z = tuple(p.tolist())
        points.append((x, y, z))
    return _path_length(points), points


def _distance_point_path(point, path) -> float:
    min_distance = float("inf")
    for p in path:
        distance = _distance_squared(point, p)
        if distance < min_distance:
            min_distance = distance
    return min_distance**0.5


def _distance_squared(p1, p2) -> float:
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return dx * dx + dy * dy + dz * dz


def _distance(p1, p2) -> float:
    return _distance_squared(p1, p2) ** 0.5


def _path_length(points) -> float:
    result = 0.0
    for p1, p2 in zip(points[:-1], points[1:]):
        result += _distance(p1, p2)
    return result


# for each point along the circumference, we compute the shortest path to Cz
# then for each of these paths we compute the distance to the surface point
# the path with the shortest distance is the one that defines the point along
# the circumference
def find_x_index(solver, circumference_indices, cz_index, surface_point):
    min_distance = float("inf")
    for i in circumference_indices:
        _, path = find_path(solver, i, cz_index)
        distance = _distance_point_path(surface_point, path)
        if distance < min_distance:
            min_distance = distance
            x_index = i
    return x_index
