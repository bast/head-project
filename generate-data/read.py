from simnibs import read_msh

result = read_msh("m2m_test/test.msh")


i_list, j_list, k_list = [], [], []
for e, (i, j, k, l) in enumerate(result.elm.node_number_list):
    if l == -1:
        if result.elm.tag1[e] == 1005:
            i_list.append(i - 1)
            j_list.append(j - 1)
            k_list.append(k - 1)


num_vertices = max(i_list + j_list + k_list) + 1
faces = zip(i_list, j_list, k_list)
num_faces = len(i_list)

print(num_vertices)
for i in range(num_vertices):
    vertex = result.nodes[i + 1]
    print(vertex[0], vertex[1], vertex[2])

print(num_faces)
for i, j, k in faces:
    print(i, j, k)
