#!/bin/zsh

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

cd "$PROJECT_ROOT" || exit 1
python3 cartoon_render.py images/input/Me.jpg images/output/me_cartoon.png "$@"
