#!/bin/bash

function k6run {
    echo "## $1"
    k6 run $1.js \
        --out json=logs/log-$1.json \
        --out csv=logs/log-$1.csv \
        --quiet
}

mkdir -p logs

k6run 0_debug