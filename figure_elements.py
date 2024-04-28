import plotly.graph_objects as go


def draw_point(point, color, name):
    x, y, z = point

    return go.Scatter3d(
        x=[x],
        y=[y],
        z=[z],
        mode="markers",
        marker=dict(
            color=color,
            size=4,
        ),
        name=name,
    )


def draw_line(points, color, dash, name):
    x, y, z = zip(*points)

    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        line=dict(
            color=color,
            width=5,
            dash=dash,
        ),
        name=name,
    )


def create_mesh(points, vertices, name, color, opacity):
    x, y, z = zip(*points)
    i, j, k = zip(*vertices)

    return go.Mesh3d(
        x=x,
        y=y,
        z=z,
        color=color,
        opacity=opacity,
        i=i,
        j=j,
        k=k,
        name=name,
        # for some reason, hover info in dash is buggy without this
        hovertemplate="x: %{x}<br>y: %{y}<br>z: %{z}<extra></extra>",
    )
