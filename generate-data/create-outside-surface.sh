#!/usr/bin/env bash

set -euf -o pipefail

ray/target/release/ray --input-file data/all.txt --output-file data/outside-only.txt
