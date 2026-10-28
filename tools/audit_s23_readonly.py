#!/usr/bin/env python3
"""Read-only Android/Termux audit; writes evidence ONLY on the WSL host.

No package installs, settings writes, process kills, forced idle, battery resets,
screen actions, root, remote files, or service starts. Every remote command is
listed below. Package-manager metadata is minimized before saving.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import time


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def execute(argv, timeout=45):
    started = utc()
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return dict(started_utc=started, ended_utc=utc(), returncode=p.returncode,
                    stdout=p.stdout.replace('\r', ''), stderr=p.stderr.replace('\r', ''))
    except subprocess.TimeoutExpired:
        return dict(started_utc=started, ended_utc=utc(), returncode=124,
                    stdout='', stderr='Host timeout; no remote state change requested.')


def minimize_packages(raw):
    """Keep installed-package facts, not intent extras, signatures or account data."""
    packages = {}
    current = None
    for line in raw.splitlines():
        m = re.match(r'  Package \[([^]]+)\]', line)
        if m:
            # Updated system apps occur again under "Hidden system packages".
            # Keep the first (active) entry rather than overwriting with the ROM APK.
            current = m[1] if m[1] not in packages else None
            if current:
                packages[current] = []
        elif current and re.match(
            r'\s+(userId=|appId=|sharedUser=|codePath=|versionCode=|versionName=|'
            r'flags=|pkgFlags=|privateFlags=|firstInstallTime=|lastUpdateTime=|'
            r'installerPackageName=|initiatingPackageName=|originatingPackageName=|'
            r'installSource=|User 0:|stopped=|enabled=|hidden=|suspended=|'
            r'android\.permission\.(RECEIVE_BOOT_COMPLETED|FOREGROUND_SERVICE|'
            r'REQUEST_IGNORE_BATTERY_OPTIMIZATIONS|BIND_ACCESSIBILITY_SERVICE|'
            r'SYSTEM_ALERT_WINDOW|POST_NOTIFICATIONS|SCHEDULE_EXACT_ALARM|'
            r'USE_EXACT_ALARM)|enabledComponents:|disabledComponents:)', line):
            packages[current].append(line.strip())
    return json.dumps(packages, indent=2, ensure_ascii=False) + '\n'


def selected_lines(raw, pattern):
    return '\n'.join(x for x in raw.splitlines() if re.search(pattern, x)) + '\n'


def minimize_battery(raw):
    # Do not retain the vendor history wholesale: it contains battery QR data.
    return selected_lines(raw, r'^Current Battery Service state:|^  (AC powered:|USB powered:|Wireless powered:|Dock powered:|Max charging current:|Max charging voltage:|Charge counter:|status:|health:|present:|level:|scale:|voltage:|temperature:|technology:|current now:|charge counter:)|^ mProtectBatteryMode:|^ mProtectionThreshold:|^ mMaximumProtectionThreshold:|ACTION_POPUP_BATTERY_DETERIORATION')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ssh', default='mestry-s23')
    ap.add_argument('--output', type=pathlib.Path)
    ap.add_argument('--sample-count', type=int, default=1)
    ap.add_argument('--sample-interval', type=int, default=30)
    args = ap.parse_args()
    if not 1 <= args.sample_count <= 12 or not 0 <= args.sample_interval <= 60:
        ap.error('sample-count 1..12; sample-interval 0..60 seconds')
    run_id = 'mestry-s23-audit-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = args.output or pathlib.Path('docs/validation') / run_id
    out.mkdir(parents=True, exist_ok=False)
    devices = execute(['adb.exe', 'devices', '-l'])
    matches = re.findall(r'^\S+\s+device\s+.*model:SM_S918B\b.*transport_id:(\d+)', devices['stdout'], re.M)
    if len(matches) != 1:
        raise SystemExit('Expected exactly one authorized SM-S918B; no device queries executed.')
    transport = matches[0]
    base = ['adb.exe', '-t', transport, 'shell']
    ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', args.ssh]
    manifest = dict(run_id=run_id, started_utc=utc(), scope='read-only; no root; host-only output',
                    device_selection='one authorized SM-S918B; serial omitted', probes=[])

    def probe(name, channel, command, transform=None, timeout=45):
        print(f'{utc()} {name}', flush=True)
        res = execute((base if channel == 'adb' else ssh) + [command], timeout)
        if transform:
            res['stdout'] = transform(res['stdout'])
        file = name + '.txt'
        body = res['stdout'] + ('\n[stderr]\n' + res['stderr'] if res['stderr'] else '')
        (out / file).write_text(body)
        manifest['probes'].append(dict(name=name, channel=channel, command=command,
                                      **{k:v for k,v in res.items() if k not in ('stdout', 'stderr')},
                                      file=file, sha256=hashlib.sha256(body.encode()).hexdigest()))
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')

    probe('identity', 'adb', "id; uname -r; for p in ro.product.model ro.product.device ro.product.cpu.abilist ro.build.version.release ro.build.version.sdk ro.build.display.id ro.build.version.security_patch ro.build.version.oneui ro.build.version.sep ro.boot.verifiedbootstate ro.boot.flash.locked ro.boot.vbmeta.device_state ro.boot.sales_code ro.csc.sales_code; do printf '%s=' \"$p\"; getprop \"$p\"; done; cat /proc/uptime")
    for name, flags in [('packages_all', '-U --show-versioncode -i'),
                        ('packages_system', '-s'), ('packages_user', '-3'),
                        ('packages_disabled', '-d'), ('packages_enabled', '-e')]:
        probe(name, 'adb', 'pm list packages --user 0 ' + flags)
    probe('package_metadata', 'adb', 'dumpsys package packages', minimize_packages, timeout=90)
    probe('launcher_components', 'adb', 'cmd package query-activities --brief --user 0 -a android.intent.action.MAIN -c android.intent.category.LAUNCHER')
    probe('webview', 'adb', 'dumpsys webviewupdate')
    probe('services_registered', 'adb', 'service list')
    probe('services_active', 'adb', 'dumpsys activity services',
          lambda s: selected_lines(s, r'ServiceRecord\{|app=ProcessRecord|isForeground=|foregroundId=|foregroundServiceType=|startRequested=|restartCount=|restartDelay=|nextRestartTime=|createTime=|lastActivity=|executingStart=|destroyTime=|restartTime='))
    probe('processes_persistent', 'adb', 'dumpsys activity processes',
          lambda s: selected_lines(s, r'Process LRU|ProcessRecord\{|\*APP\*|\*PERS\*|persistent=|isPersistent=|hasForegroundServices=|foregroundServices=|oom:|curAdj=|setAdj=|curProcState=|setProcState=|maxAdj=|cached=|empty=|mAllowLowerMemLevel=|mLastMemoryLevel=|mProcessLimit=|mMaxCachedProcesses=|mMaxEmptyProcesses=|mTotalPersistentProcs=|mNumNonCachedProcs=|mNumCachedHiddenProcs=|mNumServiceProcs=|mNumNonCachedProcs=|mNumCachedHiddenProcs=|mNumServiceProcs='))
    probe('termux_service', 'adb', 'dumpsys activity services com.termux',
          lambda s: selected_lines(s, r'ServiceRecord\{|app=ProcessRecord|isForeground=|foregroundId=|foregroundServiceType=|startRequested=|restartCount=|restartDelay=|nextRestartTime=|createTime=|lastActivity=|executingStart=|destroyTime=|restartTime='))
    probe('ram_plus_settings', 'adb', "for n in global system secure; do printf '[%s]\\n' \"$n\"; settings list \"$n\" | grep -Ei '^(ram_expand|zram|swap|low_power|adaptive_battery|app_standby|always_on|aod_mode|protect_battery|battery_protection|battery_protection_threshold|sem_enhanced_cpu_responsiveness|enhanced_processing|performance_mode|automatic_power_save|adaptive_power_saving|auto_restart|auto_optimization|app_auto_restriction|sleep|screen_off_timeout|stay_on_while_plugged_in|wifi_sleep_policy|wifi_power_save|cached_apps_freezer|activity_manager_constants|device_idle_constants|development_settings_enabled|adb_enabled|adb_wifi_enabled|monitor_phantom_procs|default_input_method|accessibility_enabled|enabled_accessibility_services|autofill_service|assistant|voice_interaction_service|private_dns_mode|private_dns_specifier)[^=]*='; done",
          lambda s: '\n'.join(x for x in s.splitlines() if not x.startswith('private_dns_specifier=')) + '\n')
    probe('idle', 'adb', 'dumpsys deviceidle',
          lambda s: selected_lines(s, r'Whitelist|whitelist|[Cc]om\.termux|m[A-Za-z]+=(true|false|ACTIVE|INACTIVE|IDLE|SENSING|LOCATING|IDLE_PENDING|LIGHT_IDLE|OVERRIDE|[0-9])|^(  )?(system|user),'))
    probe('idle_whitelist', 'adb', 'cmd deviceidle whitelist')
    probe('power', 'adb', 'dumpsys power',
          lambda s: selected_lines(s, r'mWakefulness=|mIsPowered=|mPlugType=|mBatteryLevel=|mBatteryLevelLow=|mIsPowerSaveMode=|mDeviceIdleMode=|mLightDeviceIdleMode=|mLowPowerStandby|mWakeLockSummary=|mLastWakeTime=|mLastSleepTime=|mLastUserActivityTime=|mScreenOffTimeoutSetting=|mStayOnWhilePluggedInSetting=|mStayOn=|Wake Locks:|PARTIAL_WAKE_LOCK|FULL_WAKE_LOCK|SCREEN_BRIGHT_WAKE_LOCK|Display Power:|mHoldingWakeLock|mIsInteractionPowerHintEnabled=|termux|Termux|Low power mode|Settings:|mSettingBatterySaverEnabled=|mEnabled=|mAdaptiveEnabled='))
    probe('thermal', 'adb', 'dumpsys thermalservice')
    probe('battery', 'adb', 'dumpsys battery', minimize_battery)
    probe('battery_sysfs', 'adb', "for p in status capacity voltage_now current_now current_avg charge_counter charge_full charge_full_design temp cycle_count; do printf '%s=' \"$p\"; cat \"/sys/class/power_supply/battery/$p\"; done")
    probe('storage', 'adb', 'df -k /data /storage/emulated/0 /system /vendor /product /system_ext /apex /metadata /cache; cat /proc/partitions')
    probe('mounts', 'adb', "cat /proc/mounts | grep -E ' /(data|system|vendor|product|system_ext|metadata|cache)( |/)'")
    probe('zram', 'adb', "cat /proc/swaps; for z in /sys/block/zram*; do printf '%s\\n' \"$z\"; for p in disksize comp_algorithm mm_stat bd_stat backing_dev initstate io_stat mem_limit; do printf '%s=' \"$p\"; cat \"$z/$p\"; done; done; printf 'swappiness='; cat /proc/sys/vm/swappiness")
    probe('vmstat', 'adb', 'cat /proc/vmstat')
    probe('cpu_online', 'adb', 'cat /sys/devices/system/cpu/online; for p in /sys/devices/system/cpu/cpufreq/policy*; do printf "%s " "$p"; cat "$p/scaling_cur_freq" "$p/cpuinfo_max_freq"; done')
    probe('cpuinfo', 'adb', 'dumpsys cpuinfo')
    probe('memory_policy', 'adb', "for p in ro.lmk.use_psi ro.lmk.use_minfree_levels ro.lmk.low_ram ro.config.low_ram ro.lmk.kill_heaviest_task ro.lmk.thrashing_limit ro.lmk.swap_free_low_percentage ro.lmk.swap_util_max ro.slmk.dha_cached_max ro.slmk.dha_empty_max; do printf '%s=' \"$p\"; getprop \"$p\"; done; device_config get activity_manager max_phantom_processes; device_config get activity_manager max_cached_processes; settings get global settings_enable_monitor_phantom_procs")
    probe('activity_settings', 'adb', 'dumpsys activity settings',
          lambda s: selected_lines(s, r'max_phantom|phantom|MAX_CACHED|MAX_EMPTY|CUR_MAX|background_settle|power_check|cached_apps|freez|mForceBackgroundCheck|mMaxCached|mMaxEmpty|mNumCached|mNumEmpty|mProcessLimit'))
    probe('cached_optimizer', 'adb', 'dumpsys activity cao')
    probe('lmk_stats', 'adb', 'dumpsys activity lmk')
    probe('roles_labeled', 'adb', 'for r in BROWSER SMS DIALER HOME; do printf "[%s]\\n" "$r"; cmd role get-role-holders --user 0 "android.app.role.$r"; done')
    probe('user_ids', 'adb', 'pm list users',
          lambda s: re.sub(r'UserInfo\{(\d+):[^:}]+:', r'UserInfo{\1:[name-omitted]:', s))
    probe('apex_modules', 'adb', 'pm list packages --apex-only --show-versioncode')
    probe('network_settings', 'adb', 'for k in airplane_mode_on wifi_on bluetooth_on mobile_data; do printf "%s=" "$k"; settings get global "$k"; done; printf "gsm.sim.state="; getprop gsm.sim.state')
    probe('loop_backing', 'adb', 'cat /sys/block/loop52/loop/backing_file; cat /sys/block/loop52/size; cat /proc/diskstats | grep -E "loop52|zram0"')
    probe('termux_appops', 'adb', 'cmd appops get --user 0 com.termux')
    probe('termux_standby', 'adb', 'am get-standby-bucket --user 0 com.termux')
    probe('termux_exit_info', 'adb', 'dumpsys activity exit-info com.termux',
          lambda s: '\n'.join(x for x in s.splitlines() if not re.search(r'(?i)description=|trace=|traceFile=|packageUid=', x)) + '\n')
    probe('termux_notifications', 'adb', 'dumpsys package com.termux',
          lambda s: selected_lines(s, r'User 0:|versionCode=|versionName=|flags=|pkgFlags=|firstInstallTime=|lastUpdateTime=|android.permission.(POST_NOTIFICATIONS|WAKE_LOCK|REQUEST_IGNORE_BATTERY_OPTIMIZATIONS|FOREGROUND_SERVICE|RECEIVE_BOOT_COMPLETED).*granted='))
    probe('ssh_termux', 'ssh', "id; uname -m; printf 'Termux version='; printenv TERMUX_VERSION; printf 'Termux source='; printenv TERMUX_APK_RELEASE; dpkg-query -W -f='${binary:Package} ${Version}\\n' openssh termux-services proot proot-distro termux-api termux-boot termux-x11-nightly tmux 2>&1; ps -o pid,ppid,rss,etime,comm -u \"$(id -u)\"; printf '\\nListening policy\\n'; sshd -T 2>/dev/null | grep -Ei '^(Port|ListenAddress|PasswordAuthentication|PubkeyAuthentication|PermitRootLogin|AllowTcpForwarding|GatewayPorts|ClientAliveInterval|ClientAliveCountMax) '; printf '\\nService directory names only\\n'; if [ -d \"$PREFIX/var/service\" ]; then ls -1 \"$PREFIX/var/service\"; else printf 'absent\\n'; fi; printf '\\nBoot script names only\\n'; if [ -d \"$HOME/.termux/boot\" ]; then ls -1 \"$HOME/.termux/boot\"; else printf 'absent\\n'; fi; printf '\\nTermux local filesystem\\n'; df -Pk \"$HOME\" \"$PREFIX\"")
    probe('termux_package_status', 'ssh', "dpkg-query -W -f='${binary:Package} ${db:Status-Abbrev} ${Version}\\n' openssh termux-services termux-api tmux; ps -o pid,ppid,rss,etime,comm -u \"$(id -u)\"; for s in \"$PREFIX\"/var/service/*; do if [ -d \"$s\" ]; then printf '%s\\n' \"$s\"; for f in run finish down; do if [ -e \"$s/$f\" ]; then ls -l \"$s/$f\"; fi; done; fi; done")
    probe('termux_permission_grants', 'adb', 'dumpsys package com.termux',
          lambda s: selected_lines(s, r'android.permission.(POST_NOTIFICATIONS|WAKE_LOCK|REQUEST_IGNORE_BATTERY_OPTIMIZATIONS|FOREGROUND_SERVICE|RECEIVE_BOOT_COMPLETED)|User 0:|versionName='))
    for i in range(args.sample_count):
        if i:
            time.sleep(args.sample_interval)
        probe(f'sample_{i:02d}_meminfo', 'adb', 'cat /proc/meminfo; cat /proc/pressure/memory; cat /proc/pressure/cpu; cat /proc/pressure/io; cat /proc/uptime')
        probe(f'sample_{i:02d}_cpu_stat', 'adb', 'cat /proc/stat; cat /proc/uptime')
        probe(f'sample_{i:02d}_ps', 'adb', 'ps -A -o USER,PID,PPID,RSS,VSZ,STAT,NAME')
        probe(f'sample_{i:02d}_dumpsys_meminfo', 'adb', 'dumpsys meminfo', timeout=60)
        probe(f'sample_{i:02d}_power', 'adb', 'dumpsys power',
              lambda s: selected_lines(s, r'mWakefulness=|mIsPowered=|mBatteryLevel=|mDeviceIdleMode=|mLightDeviceIdleMode=|Wake Locks:|PARTIAL_WAKE_LOCK|Display Power:'))
        probe(f'sample_{i:02d}_battery', 'adb', 'dumpsys battery',
              lambda s: selected_lines(s, r'AC powered:|USB powered:|Wireless powered:|status:|health:|level:|voltage:|temperature:|Charge counter:|Max charging current:|Max charging voltage:'))
    manifest['ended_utc'] = utc()
    manifest['collector_sha256'] = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(output=str(out), probes=len(manifest['probes']),
                          nonzero=[x['name'] for x in manifest['probes'] if x['returncode']]), indent=2))


if __name__ == '__main__':
    main()
