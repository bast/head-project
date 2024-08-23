from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
import argparse
import os
import plotly.graph_objects as go


from figure_elements import create_mesh, draw_point, draw_line
from geodesic import create_solver, find_path, find_x_index
from distance import nearest_vertex_noddy
from file_io import read_mesh
from reference_point import reference_point_moved
from mni import convert_mni_to_subject


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


def read_eeg_locations(directory, points):
    eeg_locations = {}
    with open(
        os.path.join(directory, "eeg-positions", "EEG10-10_Cutini_2011.csv"), "r"
    ) as f:
        for line in f.read().splitlines():
            for _, x, y, z, position in [line.split(",")]:
                vertex = nearest_vertex_noddy((float(x), float(y), float(z)), points)
                eeg_locations[position] = vertex

    return eeg_locations


def get_list_of_files(directory: str) -> list:
    surface_files = [f for f in os.listdir(directory) if f.endswith(".txt")]
    surface_files.remove("outside-surface.txt")
    return sorted(surface_files)


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


args = parse_args()

surface_files = get_list_of_files(os.path.join(args.input_directory, "meshes"))


mesh = {}

for surface in surface_files:
    points, vertices = read_mesh(os.path.join(args.input_directory, "meshes", surface))
    mesh[surface] = create_mesh(
        points=points, vertices=vertices, name=surface, color="lightblue", opacity=0.2
    )

points, vertices = read_mesh(
    os.path.join(args.input_directory, "meshes", "outside-surface.txt")
)
mesh["outside-surface"] = create_mesh(
    points=points,
    vertices=vertices,
    name="outside-surface",
    color="lightpink",
    opacity=0.5,
)
solver = create_solver(points, vertices)


fig = go.Figure(data=[mesh["outside-surface"]])

fig.update_layout(
    autosize=False,
    width=1200,
    height=1200,
    scene_camera=dict(eye=dict(x=-1.25, y=1.25, z=1.25)),
    margin=dict(l=0, r=0, t=0, b=0),
)


eeg_locations = read_eeg_locations(args.input_directory, points)

# EEG positions
for location, index in eeg_locations.items():
    fig.add_traces(
        draw_point(
            points[index],
            color="red",
            name=f"{location} (EEG)",
            visible=True,
            text=location,
        )
    )

# guides
circumference_points = []
for a, b in [
    ("Cz", "LPA"),
    ("Cz", "RPA"),
    ("Cz", "Nz"),
    ("Cz", "Iz"),
    ("T7", "Fpz"),
    ("T8", "Fpz"),
]:
    _distance, shortest_path = find_path(solver, eeg_locations[a], eeg_locations[b])
    fig.add_traces(
        draw_line(
            shortest_path,
            color="black",
            dash="dash",
            name=f"guide {a} - {b}",
            visible=True,
        )
    )
    if (a, b) in [("T7", "Fpz"), ("T8", "Fpz")]:
        circumference_points.extend(shortest_path)


circumference_indices = list(
    map(lambda x: nearest_vertex_noddy(x, points), circumference_points)
)


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "TMS location"

app.layout = html.Div(
    [
        html.Div(
            children=[
                dcc.Graph(id="graph-content", figure=fig),
                html.Div(
                    children=[
                        html.Br(),
                        html.Div(
                            children=[
                                dbc.Label("reference point (MNI coordinates)"),
                                dbc.Input(
                                    id="reference_point_x",
                                    type="text",
                                    placeholder="x",
                                    style={"marginRight": "10px"},
                                ),
                                dbc.Input(
                                    id="reference_point_y",
                                    type="text",
                                    placeholder="y",
                                    style={"marginRight": "10px"},
                                ),
                                dbc.Input(
                                    id="reference_point_z",
                                    type="text",
                                    placeholder="z",
                                    style={"marginRight": "10px"},
                                ),
                            ],
                        ),
                        # html.Br(),
                        # html.Div(
                        #     children=[
                        #         html.Button(
                        #             "Set position 1", id="button_1", n_clicks=0
                        #         ),
                        #         html.Button(
                        #             "Set position 2", id="button_2", n_clicks=0
                        #         ),
                        #     ],
                        # ),
                        html.Br(),
                        html.Div(
                            children=[
                                dbc.Label("options"),
                                dbc.Checklist(
                                    id="show_eeg",
                                    options=[
                                        "Show EEG positions",
                                    ],
                                    value=["Show EEG positions"],
                                ),
                                dbc.Checklist(
                                    id="show_guides",
                                    options=[
                                        "Show guides",
                                    ],
                                    value=["Show guides"],
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Div(
                            children=[
                                dbc.Label("show surface"),
                                dbc.Checklist(
                                    id="selected_surfaces",
                                    options=surface_files,
                                ),
                            ],
                        ),
                    ],
                    style={"display": "flex", "flexDirection": "column"},
                ),
            ],
            style={"display": "flex", "flexDirection": "row"},
        ),
        dcc.Store(id="state"),
    ]
)


@callback(
    Output("graph-content", "figure"),
    Output("state", "data"),
    #   Input("button_1", "n_clicks"),
    #   Input("button_2", "n_clicks"),
    Input("reference_point_x", "value"),
    Input("reference_point_y", "value"),
    Input("reference_point_z", "value"),
    Input("show_eeg", "value"),
    Input("show_guides", "value"),
    Input("selected_surfaces", "value"),
    State("graph-content", "figure"),
    State("graph-content", "relayoutData"),  # capture current view settings
    State("state", "data"),
)
def update_graph(
    # button_1,
    # button_2,
    reference_point_x,
    reference_point_y,
    reference_point_z,
    show_eeg,
    show_guides,
    selected_surfaces,
    figure,
    relayoutData,
    state,
):
    # comment about the selected_surfaces solution:
    # Alternatively this could have been done using "visible"
    # which would have simplified the code. Unfortunately, it
    # made the app a lot slower since then all meshes are loaded
    # in memory.
    state = state or {
        "reference_point": None,
        "selected_surfaces": None,
    }

    # toggles whether we see EEG positions
    for trace in figure["data"]:
        if "EEG" in trace["name"]:
            trace["visible"] = show_eeg == ["Show EEG positions"]

    # toggles whether we see guides
    for trace in figure["data"]:
        if "guide" in trace["name"]:
            trace["visible"] = show_guides == ["Show guides"]

    #   # debugging
    #   if "button_1" == ctx.triggered_id:
    #       reference_point_x = -38.0
    #       reference_point_y = 44.0
    #       reference_point_z = 26.0
    #   if "button_2" == ctx.triggered_id:
    #       reference_point_x = 38.0
    #       reference_point_y = 44.0
    #       reference_point_z = 26.0

    if reference_point_moved(
        (reference_point_x, reference_point_y, reference_point_z), state
    ):
        x_subject, y_subject, z_subject = convert_mni_to_subject(
            reference_point_x,
            reference_point_y,
            reference_point_z,
            os.path.join(args.input_directory, "m2m_data"),
        )

        reference_point = (x_subject, y_subject, z_subject)

        state["reference_point"] = reference_point

        surface_point_index = nearest_vertex_noddy(
            reference_point,
            points,
        )
        surface_point = points[surface_point_index]

        figure["data"] = [
            trace for trace in figure["data"] if not ("reference" in trace["name"])
        ]

        figure["data"].extend(
            draw_point(
                reference_point,
                color="#202020",
                name="reference point",
                visible=True,
                text="reference point",
            )
        )
        figure["data"].extend(
            draw_line(
                [reference_point, surface_point],
                color="#202020",
                dash="dash",
                name="line to reference surface point",
                visible=True,
            )
        )
        figure["data"].extend(
            draw_point(
                surface_point,
                color="green",
                name="reference surface point",
                visible=True,
                text="surface point",
            )
        )

        distance_y, path_y = find_path(solver, eeg_locations["Cz"], surface_point_index)
        figure["data"].extend(
            draw_line(
                path_y,
                color="blue",
                dash="solid",
                name=f"reference Y distance",
                visible=True,
                text=f"Y = {distance_y:.1f} mm",
            )
        )

        index_x = find_x_index(solver, circumference_indices, surface_point_index)
        distance_x, path_x = find_path(solver, eeg_locations["Fpz"], index_x)
        figure["data"].extend(
            draw_line(
                path_x,
                color="blue",
                dash="solid",
                name=f"reference X distance",
                visible=True,
                text=f"X = {distance_x:.1f} mm",
            )
        )

    # update surfaces
    surfaces_to_remove, surfaces_to_add = detect_changes_in_list(
        selected_surfaces, state["selected_surfaces"]
    )
    figure["data"] = [
        trace for trace in figure["data"] if trace["name"] not in surfaces_to_remove
    ]
    for surface in surfaces_to_add:
        figure["data"].append(mesh[surface])
    state["selected_surfaces"] = selected_surfaces

    # apply the captured view settings to maintain orientation
    if relayoutData and "scene.camera" in relayoutData:
        figure["layout"]["scene"]["camera"] = relayoutData["scene.camera"]

    return figure, state


if __name__ == "__main__":
    app.run(debug=args.debug)
