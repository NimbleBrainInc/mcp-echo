#!/bin/bash
# Build MCPB bundle with vendored dependencies
# Usage: ./scripts/build-bundle.sh [output_dir] [version]
#
# If running on macOS, uses Docker to build Linux-compatible bundle.
# If running on Linux, builds directly.

set -e

OUTPUT_DIR="${1:-.}"
VERSION="${2:-0.0.1}"
BUNDLE_NAME="mcp-echo"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Detect platform
if [[ "$(uname)" == "Darwin" ]]; then
    echo "Building bundle in Docker (for Linux compatibility)..."

    docker run --rm \
        -v "$PROJECT_ROOT:/build:ro" \
        -v "$OUTPUT_DIR:/output" \
        -e DEBIAN_FRONTEND=noninteractive \
        python:3.14-slim bash -c '
set -e
apt-get update -qq && apt-get install -qq -y zip > /dev/null 2>&1
pip install --quiet --root-user-action=ignore uv

mkdir -p /tmp/bundle/deps /tmp/src

# Copy source files
cp /build/manifest.json /tmp/bundle/
cp -r /build/src/mcp_echo /tmp/bundle/

# Copy project for uv
cp -r /build/* /tmp/src/
cd /tmp/src

# Vendor dependencies
uv pip install --target /tmp/bundle/deps .

# Create bundle
cd /tmp/bundle
zip -qr /output/'"$BUNDLE_NAME"'-v'"$VERSION"'.mcpb .
'
else
    echo "Building bundle directly..."

    BUNDLE_DIR=$(mktemp -d)
    trap "rm -rf $BUNDLE_DIR" EXIT

    mkdir -p "$BUNDLE_DIR/deps"

    cp "$PROJECT_ROOT/manifest.json" "$BUNDLE_DIR/"
    cp -r "$PROJECT_ROOT/src/mcp_echo" "$BUNDLE_DIR/"

    uv pip install --target "$BUNDLE_DIR/deps" "$PROJECT_ROOT"

    cd "$BUNDLE_DIR"
    zip -qr "$OUTPUT_DIR/$BUNDLE_NAME-v$VERSION.mcpb" .
fi

echo "Bundle created: $OUTPUT_DIR/$BUNDLE_NAME-v$VERSION.mcpb"
