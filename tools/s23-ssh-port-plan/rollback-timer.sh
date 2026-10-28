#!/data/data/com.termux/files/usr/bin/sh
# Temporary, on-phone 5-minute guard; run only during the approved cutover.
set -eu
mestry_backup=${1:?Private backup directory required}
mestry_count=0
while [ "$mestry_count" -lt 60 ]; do
  [ ! -f "$mestry_backup/confirmed" ] || exit 0
  sleep 5
  mestry_count=$((mestry_count + 1))
done
exec /data/data/com.termux/files/usr/bin/sh "$mestry_backup/rollback.sh" "$mestry_backup" auto
