#!/usr/bin/env bash
# Local preview for the Steve Ostermiller Advisory site.
#
# Why this exists: opening index.html directly (file:// or some preview panels)
# can drop the external stylesheet, so the page looks unstyled. Serving it over
# a local web server resolves assets correctly and shows the fully styled page —
# exactly like GitHub Pages will.
#
# Usage:  ./serve.sh          (defaults to port 8010)
#         ./serve.sh 9000     (custom port)

cd "$(dirname "$0")" || exit 1
PORT="${1:-8010}"
echo "Steve Ostermiller Advisory — serving at http://localhost:${PORT}"
echo "Open that URL in your browser. Press Ctrl+C to stop."
python3 -m http.server "${PORT}"
