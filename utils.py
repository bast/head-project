import plotly.graph_objects as go
import potpourri3d as pp3d


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


def create_line(points):
    x, y, z = zip(*points)

    line = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        line=dict(
            color="blue",
            width=5,
        ),
        name="Extra Lines",
    )

    return line


def create_mesh(points, vertices):
    x, y, z = zip(*points)
    i, j, k = zip(*vertices)

    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        color="lightpink",
        opacity=0.50,
        i=i,
        j=j,
        k=k,
        name="y",
        # for some reason, hover info in dash is buggy without this
        hovertemplate="x: %{x}<br>y: %{y}<br>z: %{z}<extra></extra>",
    )

    return mesh


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


def read_ply(file_name):
    V, F = pp3d.read_mesh(file_name)

    vertices = []
    for t in V:
        x, y, z = tuple(t.tolist())
        vertices.append((x, y, z))

    faces = []
    for t in F:
        i, j, k = tuple(t.tolist())
        faces.append((i, j, k))

    return vertices, faces
