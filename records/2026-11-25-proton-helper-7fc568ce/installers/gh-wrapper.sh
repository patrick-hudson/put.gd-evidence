#!/bin/sh
# Exact-argument stand-in for the Bun advisory query only (#2025 P6 installer audit); snapshot fetched on the workstation.
if [ "$*" = "api --paginate repos/oven-sh/bun/security-advisories?per_page=100" ]; then exec cat "$HOME/work/p6r-audit/bun-advisories.json"; fi
echo "p6r gh wrapper: refusing $*" >&2; exit 1
