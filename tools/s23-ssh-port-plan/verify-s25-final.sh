#!/data/data/com.termux/files/usr/bin/sh
# One-time verifier for this migration, invoked by the user from the S25.
set -eu
umask 077
mestry_state="$HOME/.local/state/mestry/ssh-port-8023-20261020T222743Z"
[ "${SSH_CONNECTION##* }" = 8023 ] || { echo 'Reconnect to port 8023 first.' >&2; exit 1; }
mestry_source=${SSH_CONNECTION%% *}
[ "$mestry_source" = 192.0.2.13 ] || { echo 'Source differs from the S25 authenticated during staging; ask the operator to verify it.' >&2; exit 1; }
mestry_canonical=$(cat "$PREFIX/var/run/sshd.pid")
case "$mestry_canonical" in ''|*[!0-9]*) exit 1;; esac
mestry_walk=$$
mestry_found=no
mestry_steps=0
while [ "$mestry_steps" -lt 20 ]; do
  if [ "$mestry_walk" = "$mestry_canonical" ]; then mestry_found=yes; break; fi
  case "$mestry_walk" in ''|0|1|*[!0-9]*) break;; esac
  mestry_walk=$(awk '/^PPid:/ {print $2}' "/proc/$mestry_walk/status")
  mestry_steps=$((mestry_steps + 1))
done
[ "$mestry_found" = yes ] || { echo 'This is an older SSH session. Disconnect, reconnect to 8023 and run again.' >&2; exit 1; }
exec 8>"$mestry_state/migration.lock"
flock -x 8
mestry_policy=$(sshd -T)
[ "$(printf '%s\n' "$mestry_policy" | awk 'tolower($1)=="port" {print $2}')" = 8023 ]
[ -s "$mestry_state/wsl-final-confirmed" ]
[ "$(sha256sum "$HOME/.ssh/authorized_keys" | awk '{print $1}')" = 31d62780157ee7714a7cc1f145d1825ccda9ab761eda38bf92fb492a8f1c7e59 ]
printf 'UTC='; date -u '+%Y-%m-%dT%H:%M:%SZ'
printf 'USER='; whoami
printf 'SSH_CONNECTION=%s\n' "$SSH_CONNECTION"
printf 'CANONICAL_ANCESTOR=%s\n' "$mestry_canonical"
{ printf 'S25 canonical 8023 verified at '; date -u '+%Y-%m-%dT%H:%M:%SZ'; } > "$mestry_state/s25-final-confirmed"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$mestry_state/confirmed"
printf 'MESTRY_S25_CANONICAL_8023=PASS\nRollback guard confirmed.\n'
