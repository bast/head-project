#!/usr/bin/env bash

set -euf -o pipefail

ray_version="0998e93117accf5740c43af06fa194712dd6199f"

wget https://github.com/bast/ray/archive/${ray_version}.zip

unzip ${ray_version}.zip
rm -f ${ray_version}.zip

cd ray-${ray_version}

cargo build --release
