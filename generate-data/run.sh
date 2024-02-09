#!/usr/bin/env bash

set -euf -o pipefail

if [ ! -f simnibs.sif ]; then
    singularity build --fakeroot simnibs.sif simnibs.def
fi

time ./simnibs.sif charm --forcerun --forceqform test T1_somedata.nii.gz
# real	60m20.219s
# user	192m18.608s
# sys	49m12.418s

time ./simnibs.sif simnibs_python read.py --input-mesh="m2m_test/test.msh" --output-path="data"
# real 0m11.969s
# user 0m11.120s
# sys  0m2.611s
