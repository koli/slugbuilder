#!/usr/bin/env bash
set -eo pipefail

/bin/sh -c '/builder/build.sh | tee /tmp/build.log'
