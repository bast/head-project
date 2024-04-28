from dash import Dash, html, dcc, callback, Output, Input, State
import argparse
import os
import plotly.graph_objects as go


from figure_elements import create_mesh, draw_point, draw_line
from geodesic import create_solver, find_path
from guess_locations import approximate_locations
from distance import nearest_vertex_noddy
from file_io import read_mesh
from reference_point import reference_point_moved


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


def get_list_of_files(directory: str) -> list:
    surface_files = [f for f in os.listdir(directory) if f.endswith(".txt")]
    surface_files.remove("outside-only.txt")
    surface_files = ["1010.txt"]  # for testing
    return sorted(surface_files)


args = parse_args()

surface_files = get_list_of_files(args.input_directory)


mesh = {}

for surface in surface_files:
    points, vertices = read_mesh(os.path.join(args.input_directory, surface))
    mesh[surface] = create_mesh(
        points=points, vertices=vertices, name=surface, color="lightblue", opacity=0.2
    )

points, vertices = read_mesh(os.path.join(args.input_directory, "outside-only.txt"))
mesh["outside-only"] = create_mesh(
    points=points,
    vertices=vertices,
    name="outside-only",
    color="lightpink",
    opacity=0.5,
)
solver = create_solver(points, vertices)


fig = go.Figure(data=[mesh["outside-only"]])

fig.update_layout(
    autosize=False,
    width=900,
    height=900,
)


locations = approximate_locations(mesh["outside-only"])

for location, index in locations.items():
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
                            options=["aim point"] + list(locations.keys()),
                            value="aim point",
                        ),
                    ],
                    style={"padding": 10, "background-color": "lightblue"},
                ),
                html.Div(
                    children=[
                        html.H3("show path"),
                        dcc.Checklist(
                            id="selected_paths",
                            options=[
                                "left tragus - vertex",
                                "right tragus - vertex",
                                "nasion - vertex",
                                "inion - vertex",
                                "cf left - cf front",
                                "cf right - cf front",
                            ],
                        ),
                    ],
                    style={"padding": 10, "background-color": "lightcoral"},
                ),
                html.Div(
                    children=[
                        html.H3("show surface"),
                        dcc.Checklist(
                            id="selected_surfaces",
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


def detect_changes_in_list(list_selected, list_state):
    to_remove = []
    to_add = []

    if list_selected != list_state:
        if list_state:
            previous_set = set(list_state)
        else:
            previous_set = set()

        to_remove = previous_set - set(list_selected)
        to_add = set(list_selected) - previous_set

    return to_remove, to_add


def remove_from_figure(figure, to_remove):
    if to_remove:
        figure["data"] = [
            trace for trace in figure["data"] if trace["name"] not in to_remove
        ]


def add_path_to_figure(figure, path, locations, solver):
    a, b = path.split(" - ")
    v_start, v_end = locations[a], locations[b]
    _distance, shortest_path = find_path(solver, v_start, v_end)
    figure["data"].append(
        draw_line(
            shortest_path,
            color="black",
            dash="dash",
            name=path,
        )
    )


@callback(
    Output("graph-content", "figure"),
    Output("state", "data"),
    Input("graph-content", "clickData"),
    Input("reference_point_x", "value"),
    Input("reference_point_y", "value"),
    Input("reference_point_z", "value"),
    Input("location", "value"),
    Input("selected_paths", "value"),
    Input("selected_surfaces", "value"),
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
    selected_paths,
    selected_surfaces,
    figure,
    relayoutData,
    state,
):
    state = state or {
        "reference_point": None,
        "selected_surfaces": None,
        "selected_paths": None,
        "clicked_index": None,
        "locations": locations,
    }

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

        v_start = locations["vertex"]
        v_end = surface_point_index
        distance, path = find_path(solver, v_start, v_end)

        figure["data"].append(
            draw_line(
                path,
                color="blue",
                dash=None,
                name="distance from vertex (Y): {:.2f} mm".format(distance),
            )
        )

        return figure, state

    # we clicked on the graph or on a radio button or checkbox
    if clickData is not None:

        # update surfaces
        surfaces_to_remove, surfaces_to_add = detect_changes_in_list(
            selected_surfaces, state["selected_surfaces"]
        )
        remove_from_figure(figure, surfaces_to_remove)
        for surface in surfaces_to_add:
            figure["data"].append(mesh[surface])
        state["selected_surfaces"] = selected_surfaces

        # update paths
        paths_to_remove, paths_to_add = detect_changes_in_list(
            selected_paths, state["selected_paths"]
        )
        remove_from_figure(figure, paths_to_remove)
        for path in paths_to_add:
            add_path_to_figure(figure, path, state["locations"], solver)
        state["selected_paths"] = selected_paths

        # update points
        clicked_point = clickData["points"][0]
        clicked_index = clicked_point["pointNumber"]
        if clicked_index != state["clicked_index"]:
            remove_from_figure(figure, [location])

            # draw new clicked point
            figure["data"].append(
                draw_point(
                    (clicked_point["x"], clicked_point["y"], clicked_point["z"]),
                    color="blue",
                    name=location,
                )
            )

            state["locations"][location] = clicked_index

            # was the clicked point part of a selected path?
            if state["selected_paths"]:
                for path in state["selected_paths"]:
                    a, b = path.split(" - ")
                    if a == location or b == location:
                        remove_from_figure(figure, [path])
                        add_path_to_figure(figure, path, state["locations"], solver)

        state["clicked_index"] = clicked_index

        # apply the captured view settings to maintain orientation
        if relayoutData and "scene.camera" in relayoutData:
            figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

        return figure, state

    return figure, state


if __name__ == "__main__":
    app.run(debug=args.debug)
