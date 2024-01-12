#!/usr/bin/env bash

set -euo pipefail

# if venv.sif does not exist
if [ ! -f venv.sif ]; then
    singularity pull https://github.com/bast/singularity-venv/releases/download/0.3.0/venv.sif
fi

./venv.sif python app.py
