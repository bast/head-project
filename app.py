from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go


from geodesic import create_solver, find_path
from head_points import find_reference_points
from utils import (
    draw_path,
    nearest_vertex_noddy,
    create_mesh,
    filter_vertices,
    path_distance,
    read_mesh,
    read_ply,
    remove_unreferenced_indices,
)


def is_float(x) -> bool:
    if x is None:
        return False
    try:
        float(x)
        return True
    except ValueError:
        return False


def floats_are_different(a: float, b: float, eps=1e-6) -> bool:
    if a is None or b is None:
        return True
    return abs(a - b) > eps


points, vertices = read_mesh("data.txt")


points, vertices = filter_vertices(points, vertices)
points, vertices = remove_unreferenced_indices(points, vertices)


mesh = create_mesh(points, vertices)
solver = create_solver(points, vertices)


fig = go.Figure(data=[mesh])
fig.update_layout(
    autosize=False,
    width=1000,
    height=1000,
)


all_ref_points = find_reference_points(mesh)

for i in all_ref_points:
    fig.add_trace(
        go.Scatter3d(
            x=[mesh.x[i]],
            y=[mesh.y[i]],
            z=[mesh.z[i]],
            mode="markers",
            name=f"ref point {i}",
            marker=dict(size=3, color="red", opacity=0.8),
        )
    )


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(children="App title", style={"textAlign": "center"}),
        dcc.Graph(id="graph-content", figure=fig),
        html.I("Reference point"),
        html.Br(),
        dcc.Input(
            id="reference_point_x",
            type="text",
            placeholder="x",
            style={"marginRight": "10px"},
        ),
        dcc.Input(
            id="reference_point_y",
            type="text",
            placeholder="y",
            style={"marginRight": "10px"},
        ),
        dcc.Input(
            id="reference_point_z",
            type="text",
            placeholder="z",
            style={"marginRight": "10px"},
        ),
        dcc.Store(id="state"),
    ]
)


def draw_reference_point(reference_point, state) -> bool:
    x, y, z = reference_point
    if not (is_float(x) and is_float(y) and is_float(z)):
        return False

    x = float(x)
    y = float(y)
    z = float(z)

    if state["reference_point"] is None:
        return True

    x_prev, y_prev, z_prev = tuple(state["reference_point"])

    if (
        floats_are_different(x, x_prev)
        or floats_are_different(y, y_prev)
        or floats_are_different(z, z_prev)
    ):
        return True


# @callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
@callback(
    Output("graph-content", "figure"),
    Output("state", "data"),
    Input("graph-content", "clickData"),
    Input("reference_point_x", "value"),
    Input("reference_point_y", "value"),
    Input("reference_point_z", "value"),
    State("graph-content", "figure"),
    State("graph-content", "relayoutData"),  # Capture current view settings
    State("state", "data"),
)
def update_graph(
    clickData,
    reference_point_x,
    reference_point_y,
    reference_point_z,
    figure,
    relayoutData,
    state,
):
    state = state or {
        "reference_point": None,
    }
    print("state", state)

    if draw_reference_point(
        (reference_point_x, reference_point_y, reference_point_z), state
    ):
        reference_point_x = float(reference_point_x)
        reference_point_y = float(reference_point_y)
        reference_point_z = float(reference_point_z)

        state["reference_point"] = (
            reference_point_x,
            reference_point_y,
            reference_point_z,
        )

        surface_point_index = nearest_vertex_noddy(
            reference_point_x,
            reference_point_y,
            reference_point_z,
            points,
        )
        surface_point_x, surface_point_y, surface_point_z = points[surface_point_index]

        figure["data"] = [e for e in figure["data"] if not "reference" in e["name"]]

        figure["data"].append(
            go.Scatter3d(
                x=[reference_point_x],
                y=[reference_point_y],
                z=[reference_point_z],
                mode="markers",
                marker=dict(size=5, color="gray"),
                name="reference point",
            )
        )
        figure["data"].append(
            go.Scatter3d(
                x=[reference_point_x, surface_point_x],
                y=[reference_point_y, surface_point_y],
                z=[reference_point_z, surface_point_z],
                mode="lines",
                line=dict(
                    color="blue",
                    width=5,
                    dash="dash",
                ),
                name="reference distance",
            )
        )
        figure["data"].append(
            go.Scatter3d(
                x=[surface_point_x],
                y=[surface_point_y],
                z=[surface_point_z],
                mode="markers",
                marker=dict(size=5, color="green"),
                name="reference surface point",
            )
        )

        path_pts = find_path(
            solver, v_start=all_ref_points[0], v_end=surface_point_index
        )
        distance = path_distance(path_pts)

        line = draw_path(
            path_pts,
            color="blue",
            dash="dash",
            name="shortest path to reference: {:.2f} mm".format(distance),
        )
        figure["data"].append(line)

        return figure, state

    if clickData is not None:
        clicked_point = clickData["points"][0]
        coords = (clicked_point["x"], clicked_point["y"], clicked_point["z"])

        clicked_index = clicked_point["pointNumber"]

        distance = 0.0
        # Add the distance as an annotation near the last clicked point
        annotation = {
            "text": f"Distance: {distance:.2f}",
            "xref": "paper",  # Use 'paper' for positioning relative to the entire plot
            "yref": "paper",
            "x": 0.05,  # X position in paper coordinates (0 is left, 1 is right)
            "y": 0.95,  # Y position in paper coordinates (0 is bottom, 1 is top)
            "showarrow": False,  # No arrow needed
            "font": {"size": 12},
            "bgcolor": "white",  # Background color for better visibility
            "bordercolor": "black",
            "borderwidth": 1,
        }
        figure["layout"]["annotations"] = [annotation]

        clicked_point_trace = go.Scatter3d(
            x=[coords[0]],
            y=[coords[1]],
            z=[coords[2]],
            mode="markers",
            marker=dict(size=5, color="blue"),
            name="Clicked Point",
        )

        # Remove the last clicked point and edges
        figure["data"] = [
            trace
            for trace in figure["data"]
            if trace["name"] not in ["Clicked Point", "edge"]
        ]

        figure["data"].append(clicked_point_trace)

        # Apply the captured view settings to maintain orientation
        if relayoutData and "scene.camera" in relayoutData:
            figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

        return figure, state
    return figure, state


if __name__ == "__main__":
    app.run(debug=True)
#   app.run()
