#!/usr/bin/env bash
# Renders the share image and PNG icons with the Chrome already on this PC.
# Run from the project root: bash scripts/og/render.sh
set -e
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
out="$(cd "$(dirname "$0")/../../public" && pwd -W 2>/dev/null || pwd)"
shot() { "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size="$2" --screenshot="$out/$3" "http://127.0.0.1:8765/scripts/og/$1${4:+?$4}" 2>/dev/null; }
# Web fonts only load over http, so serve the project root for the capture.
( cd "$root" && exec python -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 ) &
server=$!
trap 'kill $server 2>/dev/null' EXIT
sleep 1
shot og-card.html 1200,630 og-image.png
shot icon.html 180,180 apple-touch-icon.png 180
shot icon.html 32,32 favicon-32.png 32
echo "Rendered og-image.png, apple-touch-icon.png, favicon-32.png into public/"
