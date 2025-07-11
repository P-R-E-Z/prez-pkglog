#!/bin/bash

# Reads package names from stdin and logs them using prez-pkglog.
# This script is called by the pacman hook.

set -euo pipefail

while read -r line; do
    action=$(echo "$line" | cut -d' ' -f1)
    pkg_name=$(echo "$line" | cut -d' ' -f2)

    case "$action" in
        installed)
            /usr/bin/prez-pkglog install "$pkg_name" "pacman" --scope system
            ;;
        removed)
            /usr/bin/prez-pkglog remove "$pkg_name" "pacman" --scope system
            ;;
    esac
done 