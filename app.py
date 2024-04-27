from dash import Dash, html, dcc, callback, Output, Input, State

from figure_elements import create_mesh_figure, draw_point, draw_line


from geodesic import create_solver, find_path
from head_points import find_reference_points
from utils import (
    nearest_vertex_noddy,
    read_mesh,
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


points, vertices = read_mesh("outside-only.txt")


solver = create_solver(points, vertices)


fig = create_mesh_figure(points, vertices)


all_ref_points = find_reference_points(points, vertices)

for i in all_ref_points:
    fig.add_trace(
        draw_point(
            points[i],
            color="red",
            name=f"ref point {i}",
        )
    )

# debugging
# bad_indices = [1472, 22914]
# for index in bad_indices:
#     dot = points[index]
#     fig.add_trace(
#         draw_point(
#             dot,
#             color="purple",
#             name="Bad",
#         )
#     )


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
        dcc.RadioItems(
            id="location",
            options=[
                "Vertex",
                "Nasion",
                "Inion",
                "Left tragus",
                "Right tragus",
                "Circumference front",
                "Circumference back",
                "Circumference left",
                "Circumference right",
            ],
            value="Vertex",
        ),
        dcc.Store(id="state"),
    ]
)


def reference_point_moved(reference_point, state) -> bool:
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


@callback(
    Output("graph-content", "figure"),
    Output("state", "data"),
    Input("graph-content", "clickData"),
    Input("reference_point_x", "value"),
    Input("reference_point_y", "value"),
    Input("reference_point_z", "value"),
    Input("location", "value"),
    State("graph-content", "figure"),
    State("graph-content", "relayoutData"),  # Capture current view settings
    State("state", "data"),
)
def update_graph(
    clickData,
    reference_point_x,
    reference_point_y,
    reference_point_z,
    location,
    figure,
    relayoutData,
    state,
):
    state = state or {
        "reference_point": None,
    }
    print("state", state)
    print("location", location)

    if reference_point_moved(
        (reference_point_x, reference_point_y, reference_point_z), state
    ):
        reference_point = (
            float(reference_point_x),
            float(reference_point_y),
            float(reference_point_z),
        )

        state["reference_point"] = reference_point

        surface_point_index = nearest_vertex_noddy(
            reference_point,
            points,
        )
        surface_point = points[surface_point_index]

        figure["data"] = [
            trace
            for trace in figure["data"]
            if not ("reference" in trace["name"] or "distance" in trace["name"])
        ]

        figure["data"].append(
            draw_point(
                reference_point,
                color="gray",
                name="reference point",
            )
        )
        figure["data"].append(
            draw_line(
                [reference_point, surface_point],
                color="gray",
                dash="dash",
                name="line to reference surface point",
            )
        )
        figure["data"].append(
            draw_point(
                surface_point,
                color="green",
                name="reference surface point",
            )
        )

        distance, path = find_path(
            solver, v_start=all_ref_points[0], v_end=surface_point_index
        )

        figure["data"].append(
            draw_line(
                path,
                color="blue",
                dash=None,
                name="distance from vertex (Y): {:.2f} mm".format(distance),
            )
        )

        return figure, state

    if clickData is not None:
        clicked_point = clickData["points"][0]
        coords = (clicked_point["x"], clicked_point["y"], clicked_point["z"])

        # clicked_index = clicked_point["pointNumber"]

        # remove the last clicked point and edges
        figure["data"] = [
            trace
            for trace in figure["data"]
            if trace["name"] not in ["Clicked Point", "edge"]
        ]

        figure["data"].append(
            draw_point(
                coords,
                color="blue",
                name="Clicked Point",
            )
        )

        # apply the captured view settings to maintain orientation
        if relayoutData and "scene.camera" in relayoutData:
            figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

        return figure, state
    return figure, state


if __name__ == "__main__":
    app.run(debug=True)
#   app.run()
