import plotly.graph_objects as go


def draw_point(point, color, name, visible, text=None):
    x, y, z = point

    visible = True if visible else "legendonly"

    result = [
        go.Scatter3d(
            x=[x],
            y=[y],
            z=[z],
            mode="markers",
            marker=dict(
                color=color,
                size=4,
            ),
            name=name,
            showlegend=False,
            visible=visible,
        )
    ]

    if text:
        result.append(
            go.Scatter3d(
                x=[x],
                y=[y],
                z=[z],
                mode="text",
                name=name,
                text=[text],
                textfont=dict(
                    color=color,
                    size=12,
                ),
                textposition="top right",
                showlegend=False,
                visible=visible,
            )
        )

    return result


def draw_line(points, color, dash, name, visible, text=None, text_size=20):
    x, y, z = zip(*points)

    visible = True if visible else "legendonly"

    result = [
        go.Scatter3d(
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
            showlegend=False,
            visible=visible,
        )
    ]

    if text:
        num_points = len(points)
        half = num_points // 2

        result.append(
            go.Scatter3d(
                x=[x[half]],
                y=[y[half]],
                z=[z[half]],
                mode="text",
                name=name,
                text=[text],
                textfont=dict(
                    color=color,
                    size=text_size,
                ),
                textposition="top right",
                showlegend=False,
                visible=visible,
            )
        )

    return result


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
    )
