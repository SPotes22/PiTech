#!/bin/bash

# 🕸️ PiTech - Safe File Writer en Bash
# De Chromebook llorón a script que compila el alma

KEYS_DIR=".keys"
TEMPLATES_DIR="templates"

create_directories() {
    echo "🕸️ Creando estructura PiTech..."
    mkdir -p "$KEYS_DIR" "$TEMPLATES_DIR"
}

generate_keys() {
    echo "🔐 Generando claves PiCoin..."
    
    if [[ -f "$KEYS_DIR/private.pem" && -f "$KEYS_DIR/public.pem" ]]; then
        echo "✓ Claves existentes cargadas"
        return 0
    fi
    
    # Generar clave privada
    openssl genrsa -out "$KEYS_DIR/private.pem" 3072 2>/dev/null
    chmod 600 "$KEYS_DIR/private.pem"
    
    # Extraer clave pública
    openssl rsa -in "$KEYS_DIR/private.pem" -pubout -out "$KEYS_DIR/public.pem" 2>/dev/null
    
    echo "✓ Nuevas claves generadas"
}

get_picoin_id() {
    local pub_key=$(cat "$KEYS_DIR/public.pem")
    local fingerprint=$(echo -n "$pub_key" | sha3sum -a 256 | cut -d' ' -f1)
    echo "PIC-${fingerprint:0:8}-${fingerprint: -4}"
}

sign_content() {
    local content="$1"
    local signature_file=$(mktemp)
    
    echo -n "$content" | openssl dgst -sha256 -sign "$KEYS_DIR/private.pem" -out "$signature_file"
    cat "$signature_file" | xxd -p | tr -d '\n'
    rm -f "$signature_file"
}

get_local_ip() {
    local ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    [[ -z "$ip" ]] && echo "unknown" || echo "$ip"
}

create_base_template() {
    cat > "$TEMPLATES_DIR/base.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
</head>
<body>
    <div id="app">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
EOF
    echo "✓ Template base creado: $TEMPLATES_DIR/base.html"
}

save_signed_file() {
    local content="$1"
    local filename="$2"
    
    local picoin_id=$(get_picoin_id)
    local signature=$(sign_content "$content")
    local nonce=$(openssl rand -hex 16)
    local ip=$(get_local_ip)
    local timestamp=$(date -Iseconds)
    
    # Crear archivo firmado
    cat > "$filename" << EOF
{
  "picoin_id": "$picoin_id",
  "timestamp": "$timestamp", 
  "nonce": "$nonce",
  "source_ip": "$ip",
  "content": $(jq -a <<< "$content"),
  "signature": "$signature",
  "public_key": "$(cat $KEYS_DIR/public.pem | sed ':a;N;$!ba;s/\n/\\n/g')"
}
EOF
    
    echo "✓ Archivo firmado: $filename"
    create_verification_script "$filename"
}

create_verification_script() {
    local filename="$1"
    local base_name=$(basename "$filename")
    local verify_script="verify_${base_name%.*}.sh"
    
    cat > "$verify_script" << EOF
#!/bin/bash
# 🕸️ PiTech Verification Script
# Verificación de integridad y autenticidad

verify_file() {
    local file="\$1"
    
    if [[ ! -f "\$file" ]]; then
        echo "✗ Archivo no encontrado: \$file"
        return 1
    fi
    
    # Extraer datos del JSON
    local content=\$(jq -r '.content' "\$file" 2>/dev/null)
    local signature=\$(jq -r '.signature' "\$file" 2>/dev/null)
    local public_key=\$(jq -r '.public_key' "\$file" 2>/dev/null)
    
    if [[ -z "\$content" || -z "\$signature" ]]; then
        echo "✗ Estructura JSON inválida"
        return 1
    fi
    
    # Verificar firma
    echo -n "\$content" > /tmp/content_to_verify.txt
    echo "\$signature" | xxd -p -r > /tmp/signature.bin
    echo "\$public_key" > /tmp/public_key.pem
    
    if openssl dgst -sha256 -verify /tmp/public_key.pem -signature /tmp/signature.bin /tmp/content_to_verify.txt >/dev/null 2>&1; then
        echo "✓ Firma válida - Archivo auténtico"
        local picoin_id=\$(jq -r '.picoin_id' "\$file")
        echo "✓ PiCoin ID: \$picoin_id"
        return 0
    else
        echo "✗ Firma inválida - Archivo comprometido"
        return 1
    fi
}

# Verificar archivo
verify_file "$filename"
EOF
    
    chmod +x "$verify_script"
    echo "✓ Script de verificación creado: $verify_script"
}

# 🚀 MAIN SCRIPT
main() {
    echo "🕸️ Iniciando PiTech Safe File Writer..."
    echo "   De programador individual a herramienta para todos"
    echo ""
    
    create_directories
    generate_keys
    create_base_template
    
    # Contenido de ejemplo (filosofía PiTech)
    local content="EL SCRIPT MÁS SEGURO ES EL QUE NO EXISTE.
#Anti-tamper test  
#Programar para todos, no solo para máquinas
#De Chromebook entre clases a legado que compila

Status = Log[0]
return 1
EOF"
    
    save_signed_file "$content" "secure_arachne_file.json"
    
    echo ""
    echo "✅ ¡ROMPIMOS EL TECHO! 🕸️"
    echo "   Archivo seguro creado con PiCoin ID: $(get_picoin_id)"
    echo ""
    echo "🔍 Verificar con: ./verify_secure_arachne_file.sh"
    echo ""
    echo "# La paloma no es que ah, mierda. Se genere sola."
    echo "# Ella es dedicacion y adiccion."
}

# Solo ejecutar si es el script principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
