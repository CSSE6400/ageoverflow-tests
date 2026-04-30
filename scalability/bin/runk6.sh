#!/bin/bash

function k6run {
    echo "## $1"
    k6 run $1.js \
        --quiet
}

mkdir -p logs

# k6run 0_debug
k6run 1_normal
k6run 3_compliance_early
