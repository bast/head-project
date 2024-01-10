import plotly.graph_objects as go


def create_mesh(datafile):
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
        # for some reason, hoverinfo in dash is buggy without this --v
        hovertemplate="x: %{x}<br>y: %{y}<br>z: %{z}<extra></extra>",
    )

    return mesh
