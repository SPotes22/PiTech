#!/bin/bash
set -euo pipefail

echo "🔍 Ejecutando Repo Scanner (simulado)..."
python src/scanner/pre_deploy_scan.py

echo "📊 Reporte simulado completado"
