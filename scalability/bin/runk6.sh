#!/bin/bash

function k6run {
    echo "## $1"
    k6 run $1.js \
        --out json=logs/log-$1.json \
        --out csv=logs/log-$1.csv \
        --quiet
}

mkdir -p logs

# k6run 0_debug
k6run 1_normal
k6run 2_compliance
k6run 3_compliance_early
k6run 4_compliance_mid
k6run 5_compliance_peak
k6run 6_compliance_tail
k6run 7_auditing_bau
k6run 8_research
