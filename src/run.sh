#!/usr/bin/env bash

set -euo pipefail

# if venv.sif does not exist
if [ ! -f venv.sif ]; then
    singularity pull https://github.com/bast/apptainer-venv/releases/download/0.4.0/venv.sif
fi

./venv.sif python app.py --input-directory=${HOME}/tmp/ernie_data --debug
