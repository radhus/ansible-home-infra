#!/bin/sh
set -e
changed=$(lbu status | wc -l)
tmp=$(mktemp)
echo alpine_lbu_changed $changed > "$tmp"
chown prometheus:prometheus "$tmp"
chmod 644 "$tmp"
mv "$tmp" "{{ textfile_directory }}/lbu_exporter.prom"
rm -f "$tmp"