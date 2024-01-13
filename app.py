from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go


from geodesic import create_solver, find_path
from head_points import find_reference_points
from utils import (
    create_line,
    create_mesh,
    filter_vertices,
    path_distance,
    read_mesh,
    read_ply,
    remove_unreferenced_indices,
)


def isfloat(x) -> bool:
    if x is None:
        return False
    try:
        float(x)
        return True
    except ValueError:
        return False


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
        html.H1(children="Title of Dash App", style={"textAlign": "center"}),
        dcc.Graph(id="graph-content", figure=fig),
        html.I("Reference point"),
        html.Br(),
        dcc.Input(
            id="reference_x",
            type="text",
            placeholder="x",
            style={"marginRight": "10px"},
        ),
        dcc.Input(
            id="reference_y",
            type="text",
            placeholder="y",
            style={"marginRight": "10px"},
        ),
        dcc.Input(
            id="reference_z",
            type="text",
            placeholder="z",
            style={"marginRight": "10px"},
        ),
        dcc.Store(id="mymemory"),
    ]
)


# @callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
@callback(
    Output("graph-content", "figure"),
    Input("graph-content", "clickData"),
    Input("reference_x", "value"),
    Input("reference_y", "value"),
    Input("reference_z", "value"),
    State("graph-content", "figure"),
    State("graph-content", "relayoutData"),  # Capture current view settings
)
def update_graph(
    clickData, reference_x, reference_y, reference_z, figure, relayoutData
):
    if clickData is not None:
        clicked_point = clickData["points"][0]
        coords = (clicked_point["x"], clicked_point["y"], clicked_point["z"])

        clicked_index = clicked_point["pointNumber"]

        path_pts = find_path(solver, v_start=all_ref_points[0], v_end=clicked_index)
        line = create_line(path_pts)

        distance = path_distance(path_pts)

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

        if isfloat(reference_x) and isfloat(reference_y) and isfloat(reference_z):
            refernce_point = go.Scatter3d(
                x=[reference_x],
                y=[reference_y],
                z=[reference_z],
                mode="markers",
                marker=dict(size=5, color="gray"),
                name="reference point",
            )
            figure["data"].append(refernce_point)

        # Remove the last clicked point and edges
        figure["data"] = [
            trace
            for trace in figure["data"]
            if trace["name"] not in ["Clicked Point", "edge"]
        ]

        figure["data"].append(clicked_point_trace)

        figure["data"].append(line)

        # Apply the captured view settings to maintain orientation
        if relayoutData and "scene.camera" in relayoutData:
            figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

        return figure
    return figure


if __name__ == "__main__":
    app.run(debug=True)
#   app.run()
