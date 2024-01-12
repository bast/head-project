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
        #     dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
        dcc.Graph(id="graph-content", figure=fig),
    ]
)


# @callback(Output("graph-content", "figure"), Input("dropdown-selection", "value"))
@callback(
    Output("graph-content", "figure"),
    Input("graph-content", "clickData"),
    State("graph-content", "figure"),
    State("graph-content", "relayoutData"),  # Capture current view settings
)
def update_graph(clickData, existing_figure, relayoutData):
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
        existing_figure["layout"]["annotations"] = [annotation]

        clicked_point_trace = go.Scatter3d(
            x=[coords[0]],
            y=[coords[1]],
            z=[coords[2]],
            mode="markers",
            marker=dict(size=5, color="blue"),
            name="Clicked Point",
        )

        # Remove the last clicked point and edges
        existing_figure["data"] = [
            trace
            for trace in existing_figure["data"]
            if trace["name"] not in ["Clicked Point", "edge"]
        ]
        existing_figure["data"].append(clicked_point_trace)

        existing_figure["data"].append(line)

        # Apply the captured view settings to maintain orientation
        if relayoutData and "scene.camera" in relayoutData:
            existing_figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

        return existing_figure
    return existing_figure


if __name__ == "__main__":
    app.run(debug=True)
#   app.run()
