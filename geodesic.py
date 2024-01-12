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
    return points
