#!/bin/bash
# 🕸️ PiTech Verification Script
# Verificación de integridad y autenticidad

verify_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "✗ Archivo no encontrado: $file"
        return 1
    fi
    
    # Extraer datos del JSON
    local content=$(jq -r '.content' "$file" 2>/dev/null)
    local signature=$(jq -r '.signature' "$file" 2>/dev/null)
    local public_key=$(jq -r '.public_key' "$file" 2>/dev/null)
    
    if [[ -z "$content" || -z "$signature" ]]; then
        echo "✗ Estructura JSON inválida"
        return 1
    fi
    
    # Verificar firma
    echo -n "$content" > /tmp/content_to_verify.txt
    echo "$signature" | xxd -p -r > /tmp/signature.bin
    echo "$public_key" > /tmp/public_key.pem
    
    if openssl dgst -sha256 -verify /tmp/public_key.pem -signature /tmp/signature.bin /tmp/content_to_verify.txt >/dev/null 2>&1; then
        echo "✓ Firma válida - Archivo auténtico"
        local picoin_id=$(jq -r '.picoin_id' "$file")
        echo "✓ PiCoin ID: $picoin_id"
        return 0
    else
        echo "✗ Firma inválida - Archivo comprometido"
        return 1
    fi
}

# Verificar archivo
verify_file "secure_arachne_file.json"
