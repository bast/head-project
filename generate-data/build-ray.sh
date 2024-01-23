#!/usr/bin/env bash

set -euf -o pipefail

wget https://github.com/bast/ray/archive/main.zip

unzip main.zip

cd ray-main

cargo build --release
