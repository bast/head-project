import potpourri3d as pp3d

V, F = pp3d.read_mesh("bunny_small.ply")

print(V)
print(F)

# shares precomputation for repeated solves
path_solver = pp3d.EdgeFlipGeodesicSolver(V, F)

path_pts = path_solver.find_geodesic_path(v_start=14, v_end=22)

# path_pts is a Vx3 numpy array of points forming the path
print(path_pts)
