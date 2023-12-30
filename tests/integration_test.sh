#!/bin/bash
set -e

# Runs the program repeatedly in fully automated mode and checks that it terminates correctly.

NUM_SIMULATIONS=2
for i in $(seq 1 $NUM_SIMULATIONS); do
  echo "===== Running simulation $i ====="
  python application/main.py <<- EOF
	2
	1
	EOF
done
