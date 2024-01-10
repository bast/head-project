import numpy as np
import plotly.graph_objects as go

def create_mesh(datafile):
    xs = []
    ys = []
    zs = []
    i_s = []
    j_s = []
    k_s = []
    with open(datafile, "r") as f:
        # how many points?
        n = int(f.readline())
        for _ in range(n):
            x, y, z = map(float, f.readline().split())
            xs.append(x)
            ys.append(y)
            zs.append(z)
        # how many triangles?
        n = int(f.readline())
        for _ in range(n):
            i, j, k = map(int, f.readline().split())
            i_s.append(i)
            j_s.append(j)
            k_s.append(k)

    mesh = go.Mesh3d(
                x=xs,
                y=ys,
                z=zs,
                color="lightpink",
                opacity=0.50,
                i=i_s,
                j=j_s,
                k=k_s,
                name="y",
                # for some reason, hoverinfo in dash is buggy without this --v
                hovertemplate='x: %{x}<br>y: %{y}<br>z: %{z}<extra></extra>' 
            )
    
    return mesh