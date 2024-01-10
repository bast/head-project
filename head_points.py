import numpy as np


def find_closest_vertex(axis1, axis2):
    # Calculate the squared distances from the x-y axis intersection
    distances_squared = np.square(axis1) + np.square(axis2)

    # Find the index of the vertex with the minimum squared distance
    closest_vertex_index = np.argmin(distances_squared)

    return closest_vertex_index


def find_closest_vertex_conditional(mesh, condition):
    """
    Condition 0: z > 0 (top of head)
    Condition 1: x > 0 (front of head)
    Condition 2: x < 0 (back of head)
    Condition 3: y > 0 (left of head)
    Condition 4: y < 0 (right of head)
    """

    if condition == 0:
        temp_array = np.where(np.array(mesh.z) > 0)[0]
        axis1 = mesh.x
        axis2 = mesh.y
    elif condition == 1:
        temp_array = np.where(np.array(mesh.x) > 0)[0]
        axis1 = mesh.z
        axis2 = mesh.y
    elif condition == 2:
        temp_array = np.where(np.array(mesh.x) < 0)[0]
        axis1 = mesh.z
        axis2 = mesh.y
    elif condition == 3:
        temp_array = np.where(np.array(mesh.y) > 0)[0]
        axis1 = mesh.z
        axis2 = mesh.x
    elif condition == 4:
        temp_array = np.where(np.array(mesh.y) < 0)[0]
        axis1 = mesh.z
        axis2 = mesh.x

    temp_axis1 = np.array(axis1)[temp_array]
    temp_axis2 = np.array(axis2)[temp_array]
    temp_idx = find_closest_vertex(temp_axis1, temp_axis2)

    # map back to original index
    idx = temp_array[temp_idx]

    return idx


def find_reference_points(mesh):
    points = []
    for condition in range(5):
        points.append(find_closest_vertex_conditional(mesh, condition))

    return points
