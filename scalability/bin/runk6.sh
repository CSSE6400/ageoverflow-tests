#!/bin/bash

function k6run {
    echo "## $1"
    k6 run $1.js --summary-export=$1.summary.json \
        --quiet
}

mkdir -p logs

# k6run 0_debug
k6run 1_normal
k6run 2_curiosity
k6run 3_compliance_early
sleep 2m
k6run 4_compliance_mid
sleep 2m
k6run 5_compliance_peak
sleep 5m
k6run 6_compliance_tail
sleep 5m
k6run 7_auditing_bau
k6run 8_research
