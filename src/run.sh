#!/usr/bin/env bash

set -euo pipefail

# if venv.sif does not exist
if [ ! -f venv.sif ]; then
    singularity pull https://github.com/bast/apptainer-venv/releases/download/0.6.0/venv.sif
fi

env TMS_DEBUG=1 ./venv.sif python app.py --input-directory=${HOME}/tmp/ernie_data --debug
