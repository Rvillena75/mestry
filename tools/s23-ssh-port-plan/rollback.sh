#!/data/data/com.termux/files/usr/bin/sh
# Proposed recovery script. Requires backups created before the approved change.
set -eu
umask 077
mestry_prefix=/data/data/com.termux/files/usr
export PATH="$mestry_prefix/bin:/system/bin"
mestry_backup=${1:?Usage: rollback.sh PRIVATE_BACKUP_DIR [auto]}
case "$mestry_backup" in "$HOME"/.local/state/mestry/ssh-port-8023-*) ;; *) echo 'Unexpected backup path' >&2; exit 2;; esac
case "$mestry_backup" in *'/../'*|*'/./'*) echo 'Backup path must be canonical' >&2; exit 2;; esac
[ -d "$mestry_backup" ] && [ ! -L "$mestry_backup" ]
exec 8>"$mestry_backup/migration.lock"
flock -x 8
if [ "${2:-manual}" = auto ] && [ -f "$mestry_backup/confirmed" ]; then exit 0; fi
[ -s "$mestry_backup/ssh-start.before" ] && [ -s "$mestry_backup/boot.before" ]
mestry_dropin="$mestry_prefix/etc/ssh/sshd_config.d/10-mestry-port.conf"
if [ -e "$mestry_dropin" ]; then
  cmp -s "$mestry_dropin" "$mestry_backup/10-mestry-port.conf.proposed" || { echo 'Port drop-in changed; inspect before rollback' >&2; exit 1; }
fi
# A manual rollback after pairing must first stop Horus in its own UI.
mestry_scan=$(ssh-keyscan -T 2 -p 8022 -t ed25519 127.0.0.1 2>/dev/null) || mestry_scan=''
if [ -n "$mestry_scan" ]; then
  mestry_fp=$(printf '%s\n' "$mestry_scan" | ssh-keygen -E sha256 -lf - | awk '{print $2}')
  mestry_own_fp=$(ssh-keygen -E sha256 -lf "$mestry_prefix/etc/ssh/ssh_host_ed25519_key.pub" | awk '{print $2}')
  [ "$mestry_fp" = "$mestry_own_fp" ] || { echo 'Another SSH server occupies 8022; stop Horus before rollback' >&2; exit 1; }
fi
if [ -e "$mestry_dropin" ]; then rm -- "$mestry_dropin"; fi
cp "$mestry_backup/ssh-start.before" "$HOME/bin/mestry-ssh-start.rollback"
chmod 700 "$HOME/bin/mestry-ssh-start.rollback"
mv "$HOME/bin/mestry-ssh-start.rollback" "$HOME/bin/mestry-ssh-start"
cp "$mestry_backup/boot.before" "$HOME/.termux/boot/10-mestry-sshd.rollback"
chmod 700 "$HOME/.termux/boot/10-mestry-sshd.rollback"
mv "$HOME/.termux/boot/10-mestry-sshd.rollback" "$HOME/.termux/boot/10-mestry-sshd"
"$mestry_prefix/bin/sshd" -t
mestry_policy=$("$mestry_prefix/bin/sshd" -T)
mestry_ports=$(printf '%s\n' "$mestry_policy" | awk 'tolower($1)=="port" {print $2}')
[ "$mestry_ports" = 8022 ] || { echo 'Unexpected restored port policy' >&2; exit 1; }
mestry_pid=$(cat "$mestry_prefix/var/run/sshd.pid" 2>/dev/null || true)
case "$mestry_pid" in
  ''|*[!0-9]*) "$mestry_prefix/bin/sshd" 8>&- ;;
  *) if kill -0 "$mestry_pid" 2>/dev/null && [ "$(cat "/proc/$mestry_pid/comm" 2>/dev/null)" = sshd ]; then
       kill -HUP "$mestry_pid"
     else
       "$mestry_prefix/bin/sshd" 8>&-
     fi ;;
esac
# Stop only the temporary listener whose saved PID and start time still match.
if [ -s "$mestry_backup/stage.pid" ] && [ -s "$mestry_backup/stage.starttime" ]; then
  mestry_stage_pid=$(cat "$mestry_backup/stage.pid")
  case "$mestry_stage_pid" in
    ''|*[!0-9]*) ;;
    *) if [ "$mestry_stage_pid" != "$mestry_pid" ] &&
          [ "$(cat "/proc/$mestry_stage_pid/comm" 2>/dev/null)" = sshd ] &&
          [ "$(awk '{print $22}' "/proc/$mestry_stage_pid/stat" 2>/dev/null)" = "$(cat "$mestry_backup/stage.starttime")" ]; then
         kill -TERM "$mestry_stage_pid"
       fi ;;
  esac
fi
printf 'Rollback requested: Termux 8022. Verify a fresh connection; WSL and S25 may need port 8022.\n'
printf 'Keys and authentication settings were not replaced.\n'
