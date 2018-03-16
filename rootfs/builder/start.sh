#!/usr/bin/env bash
set -eo pipefail

/builder/build.sh | tee /tmp/build.log
