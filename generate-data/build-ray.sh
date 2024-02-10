#!/usr/bin/env bash

set -euf -o pipefail

ray_version="aca2051359fc1f6c7f5064eebf13d8b703d06f71"

wget https://github.com/bast/ray/archive/${ray_version}.zip

unzip ${ray_version}.zip
rm -f ${ray_version}.zip

cd ray-${ray_version}

cargo build --release

cd ..
mv ray-${ray_version} ray
