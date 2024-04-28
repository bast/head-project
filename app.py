from dash import Dash, html, dcc, callback, Output, Input, State
import argparse
import os


from figure_elements import create_mesh_figure, draw_point, draw_line
from geodesic import create_solver, find_path
from head_points import find_reference_points
from distance import nearest_vertex_noddy
from file_io import read_mesh


def parse_args():
    parser = argparse.ArgumentParser(description="Run the TMS location app.")
    parser.add_argument(
        "--input-directory",
        type=str,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    return parser.parse_args()


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


def get_list_of_files(directory: str) -> list:
    surface_files = [f for f in os.listdir(directory) if f.endswith(".txt")]
    surface_files.remove("outside-only.txt")
    return sorted(surface_files)


args = parse_args()


input_file = os.path.join(args.input_directory, "outside-only.txt")
points, vertices = read_mesh(input_file)


surface_files = get_list_of_files(args.input_directory)


solver = create_solver(points, vertices)


fig, mesh = create_mesh_figure(points, vertices)


all_ref_points = find_reference_points(mesh)
print(all_ref_points)

for location, index in all_ref_points.items():
    fig.add_trace(
        draw_point(
            points[index],
            color="red",
            name=location,
        )
    )


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(children="TMS location", style={"textAlign": "center"}),
        dcc.Graph(id="graph-content", figure=fig),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("reference point"),
                        dcc.Input(
                            id="reference_point_x",
                            type="text",
                            placeholder="x",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        dcc.Input(
                            id="reference_point_y",
                            type="text",
                            placeholder="y",
                            style={"marginRight": "10px"},
                        ),
                        html.Br(),
                        dcc.Input(
                            id="reference_point_z",
                            type="text",
                            placeholder="z",
                            style={"marginRight": "10px"},
                        ),
                    ],
                    style={"padding": 10, "background-color": "gray"},
                ),
                html.Div(
                    children=[
                        html.H3("(re)locate point"),
                        dcc.RadioItems(
                            id="location",
                            options=[
                                "some point",
                                "vertex",
                                "nasion",
                                "inion",
                                "left tragus",
                                "right tragus",
                                "circumference front",
                            ],
                            value="some point",
                        ),
                    ],
                    style={"padding": 10, "background-color": "lightblue"},
                ),
                html.Div(
                    children=[
                        html.H3("show path"),
                        dcc.Checklist(
                            id="show_path",
                            options=[
                                "foo",
                                "bar1",
                                "bar2",
                                "bar3",
                                "bar4",
                                "bar5",
                            ],
                        ),
                    ],
                    style={"padding": 10, "background-color": "lightcoral"},
                ),
                html.Div(
                    children=[
                        html.H3("show surface"),
                        dcc.Checklist(
                            id="show_surface",
                            options=surface_files,
                        ),
                    ],
                    style={"padding": 10, "background-color": "lightgreen"},
                ),
            ],
            style={"display": "flex"},
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
    Input("show_path", "value"),
    Input("show_surface", "value"),
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
    show_path,
    show_surface,
    figure,
    relayoutData,
    state,
):
    state = state or {
        "reference_point": None,
        "selected_location": "some point",
    }
    print("state", state)

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

        index = all_ref_points["vertex"]
        distance, path = find_path(solver, v_start=index, v_end=surface_point_index)

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

        if location == state["selected_location"]:
            # remove the old point
            figure["data"] = [
                trace
                for trace in figure["data"]
                if trace["name"] not in [location, "edge"]
            ]

            # draw new clicked point
            figure["data"].append(
                draw_point(
                    (clicked_point["x"], clicked_point["y"], clicked_point["z"]),
                    color="blue",
                    name=location,
                )
            )

        else:
            state["selected_location"] = location

        # apply the captured view settings to maintain orientation
        if relayoutData and "scene.camera" in relayoutData:
            figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

        return figure, state

    return figure, state


if __name__ == "__main__":
    app.run(debug=args.debug)
