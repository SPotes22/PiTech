#!/bin/bash
set -euo pipefail

./scripts/run_scanner.sh
python src/main.py
