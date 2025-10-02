#!/usr/bin/env bash
set -euo pipefail

# ================================================================================
# Clean Lambda Layer Builder for CodeChat
# ================================================================================
# Builds only the essential layer needed for current Lambda functions:
# - query-handler layer (contains Pinecone, OpenAI, PyYAML dependencies)
# - get-repositories function needs no external dependencies (uses only std lib)
# ================================================================================

# -------------------- Config --------------------
PY_CMD="${PY_CMD:-python3.13}"   # must match Lambda runtime (python3.13)
TARGET_DIR="${TARGET_DIR:-python}"
PUBLISH="${PUBLISH:-false}"      # set true or pass --publish to publish via AWS CLI

# Define only the layers we actually need
declare -A LAYERS=(
    ["query-handler"]="lambda_layer_query_handler_requirements.txt"
)

# -------------------- Args --------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --publish)         PUBLISH=true; shift ;;
    -h|--help)         
        echo "Usage: $0 [--publish] [--help]"
        echo "  --publish  Publish layers to AWS after building"
        echo "  --help     Show this help message"
        echo ""
        echo "Available layers:"
        for layer in "${!LAYERS[@]}"; do
            echo "  - $layer (${LAYERS[$layer]})"
        done
        exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# -------------------- Build function --------------------
build_layer() {
    local layer_name="$1"
    local req_file="$2"
    local out_zip="lambda-layer-${layer_name}.zip"
    
    echo ""
    echo "🔨 Building layer: $layer_name"
    echo "   Requirements: $req_file"
    echo "   Output: $out_zip"
    
    # Guard: check requirements file exists
    if [[ ! -f "$req_file" ]]; then
        echo "❌ Requirements file not found: $req_file"
        return 1
    fi
    
    # Clean up
    rm -rf "$TARGET_DIR" "$out_zip"
    mkdir -p "$TARGET_DIR"
    
    # Show versions
    echo "🔧 Using:"
    echo "   Python: $("$PY_CMD" --version 2>&1)"
    echo "   Pip:    $("$PY_CMD" -m pip --version 2>&1)"
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    "$PY_CMD" -m pip install --upgrade pip
    "$PY_CMD" -m pip install -r "$req_file" --no-cache-dir --target "$TARGET_DIR"
    
    # Create zip file
    echo "🗜️  Creating zip file..."
    zip -r "$out_zip" "$TARGET_DIR" >/dev/null
    
    # Show size
    local size=$(ls -lh "$out_zip" | awk '{print $5}')
    echo "✅ Layer built: $out_zip ($size)"
    
    # Optional publish to AWS
    if [[ "$PUBLISH" == "true" ]]; then
        publish_layer "$layer_name" "$out_zip"
    fi
    
    # Clean up target directory
    rm -rf "$TARGET_DIR"
}

# -------------------- Publish function --------------------
publish_layer() {
    local layer_name="$1"
    local zip_file="$2"
    local full_layer_name="codechat-${layer_name}-dependencies"
    
    if ! command -v aws >/dev/null 2>&1; then
        echo "❌ AWS CLI not found; install or remove --publish"
        return 1
    fi
    
    echo "☁️  Publishing $layer_name to AWS Lambda..."
    aws lambda publish-layer-version \
        --layer-name "$full_layer_name" \
        --compatible-runtimes "python3.13" \
        --compatible-architectures "x86_64" "arm64" \
        --zip-file "fileb://$zip_file" \
        --query 'LayerVersionArn' \
        --output text
    
    echo "✅ Published: $full_layer_name"
}

# -------------------- Guards --------------------
echo "🚀 Building CodeChat Lambda Layers"
echo "=================================="

# Best-effort OS check
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    echo "ℹ️  Building on $NAME $VERSION"
fi

# Check Python installation
if ! command -v "$PY_CMD" >/dev/null 2>&1; then
    echo "❌ $PY_CMD not found. Please install Python 3.13"
    echo "   On Amazon Linux: sudo dnf install -y python3.13 python3.13-pip"
    echo "   On macOS: brew install python@3.13"
    exit 1
fi

# Check zip command
if ! command -v zip >/dev/null 2>&1; then
    echo "❌ zip command not found. Please install zip utility"
    exit 1
fi

# -------------------- Build all layers --------------------
echo "📋 Layers to build: ${!LAYERS[@]}"
echo ""

total_layers=${#LAYERS[@]}
current=1

for layer_name in "${!LAYERS[@]}"; do
    req_file="${LAYERS[$layer_name]}"
    echo "[$current/$total_layers] Building $layer_name..."
    build_layer "$layer_name" "$req_file"
    ((current++))
done

# -------------------- Summary --------------------
echo ""
echo "🎯 Build Complete!"
echo "=================="
echo "Built layers:"
for zip_file in lambda-layer-*.zip; do
    if [[ -f "$zip_file" ]]; then
        size=$(ls -lh "$zip_file" | awk '{print $5}')
        echo "  📦 $zip_file ($size)"
    fi
done

echo ""
echo "💡 Next steps:"
echo "   1. Deploy with Terraform: cd infra && terraform apply"
echo "   2. Or publish layers manually: $0 --publish"

# Note about get-repositories
echo ""
echo "ℹ️  Note: get-repositories Lambda doesn't need a layer (uses only Python stdlib)"