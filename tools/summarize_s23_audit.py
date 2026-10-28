#!/usr/bin/env python3
"""Derive inventory, classifications and measurements from local audit evidence.

Offline only. Removal candidates are explicit packages observed in this S23 audit,
not a transferable debloat list. Unknown packages stay uncertain and protected.
"""
import argparse
import collections
import csv
import json
import pathlib
import re


def names(text):
    return set(text.split())


MESTRY = names('com.termux com.termux.boot org.fdroid.fdroid')
FIRST = names('''com.facebook.appmanager com.facebook.services com.facebook.system
com.sec.android.daemonapp com.samsung.android.kidsinstaller
com.samsung.android.app.watchmanagerstub com.samsung.accessory.budsunitemgr''')
OPTIONAL = FIRST | names('''com.google.android.youtube com.google.android.gm
com.google.android.apps.maps com.google.android.apps.tachyon
com.microsoft.skydrive com.google.android.projection.gearhead
com.samsung.android.game.gamehome com.samsung.android.game.gametools
com.samsung.android.aremoji com.samsung.android.app.camera.sticker.facearavatar.preload
com.samsung.android.stickercenter com.samsung.android.dynamiclock
com.samsung.android.widget.pictureframe com.samsung.android.app.reminder
com.samsung.android.app.clipboardedge com.samsung.android.app.taskedge
com.samsung.android.service.peoplestripe com.android.dreams.phototable
com.android.egg com.mygalaxy.service com.sec.android.app.vepreload
com.sec.android.app.ve.vebgm com.samsung.android.video''')
FUTURE = names('''com.google.android.apps.docs com.android.chrome
com.samsung.android.samsungpass com.samsung.android.samsungpassautofill
com.samsung.android.authfw com.osp.app.signin com.samsung.android.privateaccesstokens
com.samsung.android.accessibility.talkback com.samsung.accessibility
com.google.android.apps.accessibility.voiceaccess
com.google.audio.hearing.visualization.accessibility.scribe
com.samsung.android.app.smartcapture com.sec.android.app.camera
com.sec.android.gallery3d com.sec.android.mimage.photoretouching
com.samsung.android.app.interpreter com.samsung.android.sdk.ocr
com.samsung.android.sdk.handwriting com.samsung.android.scs
com.samsung.android.intellivoiceservice com.google.android.tts com.samsung.SMT
com.samsung.android.bixby.agent com.samsung.android.bixby.wakeup
com.samsung.android.bixbyvision.framework com.samsung.android.visionintelligence
com.samsung.android.scloud com.samsung.android.shortcutbackupservice
com.samsung.android.mcfds com.samsung.android.mcfserver
com.samsung.android.mcf.autohotspot com.samsung.android.mdx com.samsung.android.mdx.kit
com.microsoft.appmanager com.samsung.android.inputshare
com.samsung.android.hwresourceshare com.samsung.android.hwresourceshare.storage
com.samsung.android.smartmirroring com.samsung.android.audiomirroring
com.samsung.android.service.stplatform com.samsung.android.service.tagservice
com.samsung.android.beaconmanager com.samsung.android.fmm
com.sec.android.easyMover com.sec.android.easyMover.Agent
com.samsung.android.smartswitchassistant com.android.bluetooth
com.android.bluetoothmidiservice com.android.nfc com.android.apps.tag
com.android.companiondevicemanager com.android.virtualdevicemanager
com.android.virtualmachine.res com.samsung.android.service.aircommand
com.samsung.android.aircommandmanager com.samsung.android.app.aodservice
com.samsung.android.themestore com.samsung.android.themecenter
com.samsung.knox.securefolder com.samsung.android.knox.containercore
com.android.managedprovisioning com.android.euicc com.google.android.euicc
com.samsung.euicc com.samsung.android.dialer com.samsung.android.incallui
com.google.android.apps.messaging com.samsung.android.messaging
com.samsung.android.app.telephonyui com.samsung.android.calendar
com.android.providers.calendar com.google.android.syncadapters.calendar
com.samsung.android.app.contacts com.samsung.android.providers.contacts
com.google.android.googlequicksearchbox com.google.android.apps.bard
com.google.ar.core com.google.android.apps.aiwallpapers
com.android.printspooler com.android.bips com.google.android.printservice.recommendation
com.android.traceur com.android.dynsystem com.android.devicediagnostics''')
ESSENTIAL = names('''android com.android.systemui com.android.settings
com.android.settings.intelligence com.sec.android.app.launcher
com.samsung.android.honeyboard com.android.shell com.android.inputdevices
com.google.android.gms com.google.android.gsf com.android.vending
com.google.android.webview com.google.android.packageinstaller
com.google.android.permissioncontroller com.android.certinstaller
com.android.keychain com.android.credentialmanager com.google.android.rkpdapp
com.google.android.verifier com.google.android.configupdater
com.google.android.modulemetadata com.google.android.sdksandbox
com.google.android.ext.services com.google.android.ext.shared
com.google.android.documentsui com.android.externalstorage
com.android.hotspot2.osulogin com.android.wifi.dialog
com.google.android.providers.media.module com.samsung.android.providers.media
com.android.providers.downloads com.android.providers.downloads.ui
com.android.intentresolver com.android.vpndialogs com.android.proxyhandler
com.android.pacprocessor com.android.phone com.android.server.telecom
com.android.se com.qualcomm.qti.gpudrivers.kalama.api33 com.samsung.gamedriver.sm8550
com.wssyncmldm com.sec.android.soagent com.sec.android.app.samsungapps
com.samsung.android.app.updatecenter com.samsung.android.app.omcagent
com.samsung.android.lool com.sec.android.sdhms com.samsung.android.sm.devicesecurity
com.samsung.android.game.gos com.samsung.android.rampart
com.samsung.android.biometrics.app.setting com.samsung.android.kgclient
com.samsung.android.privacydashboard com.samsung.android.networkstack
com.samsung.android.wcmurlsnetworkstack com.google.android.networkstack
com.google.android.networkstack.tethering com.google.android.captiveportallogin
com.samsung.android.net.wifi.wifiguider com.samsung.android.server.wifi.mobilewips
com.samsung.android.networkdiagnostic com.samsung.android.wifi.ai
com.google.android.apps.carrier.carrierwifi com.sec.android.app.bluetoothagent
com.samsung.android.emergency com.sec.android.emergencylauncher
com.sec.android.app.safetyassurance com.google.android.cellbroadcastreceiver
com.google.android.cellbroadcastservice com.samsung.safetyinformation
com.samsung.android.settingshelper com.samsung.android.scpm com.sec.spp.push''')


def category(pkg, uid, shared):
    if pkg in MESTRY:
        return 'necesarias_mestry', 'Termux o canal actual de mantenimiento F-Droid; conservar.', '', 'alto si se elimina'
    if pkg in ESSENTIAL:
        return 'esenciales_android', 'Base Android/OEM, red, seguridad, actualizaciones o gestión térmica; conservar de forma operativa.', '', 'alto'
    if pkg in OPTIONAL:
        if uid in {'1000', '1001', '2000'} or shared:
            return 'inciertas', 'Función opcional pero comparte UID; no proponer deshabilitar sin resolver dependencias.', '', 'alto o no determinado'
        return 'prescindibles', 'Función de consumo ajena al servidor; presencia, versión y ruta comprobadas; independencia completa pendiente de ensayo.', ('lote_1' if pkg in FIRST else 'posterior'), 'bajo relativo; prueba y aprobación pendientes'
    if pkg in FUTURE or pkg.startswith('com.samsung.SMT.lang_'):
        return 'compatibilidad_futura', 'Conservar para autenticación, mantenimiento, periféricos, UI, captura o integraciones futuras; necesidad específica por validar.', '', 'medio/alto según integración'
    if (pkg.startswith(('com.android.internal.', 'com.google.android.overlay.', 'com.samsung.internal.', 'android.auto_generated_', 'com.monotype.'))
            or 'overlay' in pkg.lower() or '.resources' in pkg or pkg.startswith('com.android.providers.')
            or pkg.startswith(('com.sec.ims', 'com.sec.epdg', 'com.qualcomm.', 'com.qti.', 'vendor.qti.', 'com.samsung.android.knox.', 'com.knox.', 'com.samsung.klms'))
            or uid in {'1000', '1001', '2000'}):
        return 'esenciales_android', 'Conservación preventiva de recurso, proveedor, hardware o UID privilegiado; no demuestra que cada paquete sea técnicamente indispensable.', '', 'alto o no determinado'
    return 'inciertas', 'Dependencias y uso no acreditados en este firmware; mantener.', '', 'no determinado'


def read(p, name):
    return (p / (name + '.txt')).read_text()


def process_memory(raw, section, end):
    block = raw.split(section, 1)[1].split(end, 1)[0]
    return [dict(kib=int(k.replace(',', '')), process=n, pid=int(pid))
            for k,n,pid in re.findall(r'^\s*([\d,]+)K: (.*?) \(pid (\d+)', block, re.M)]


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('evidence', type=pathlib.Path)
    ap.add_argument('--current', action='store_true', help='Use the user-installed Boot update snapshot; memory remains explicitly from the first baseline.')
    args = ap.parse_args()
    p = args.evidence
    source_prefix = 'boot_' if args.current else ''
    output_suffix = '_current' if args.current else ''
    meta_file = p / ('boot_package_metadata.txt' if args.current else 'package_metadata_current.txt')
    if not meta_file.exists(): meta_file = p / 'package_metadata.txt'
    meta = json.loads(meta_file.read_text())
    package_sets = {n:set(re.findall(r'^package:(\S+)',read(p,source_prefix+'packages_'+n),re.M))
                    for n in ['all','system','user','enabled','disabled']}
    all_pkgs = package_sets['all']
    assert package_sets['system'].isdisjoint(package_sets['user'])
    assert package_sets['system'] | package_sets['user'] == all_pkgs
    assert package_sets['enabled'].isdisjoint(package_sets['disabled'])
    assert package_sets['enabled'] | package_sets['disabled'] == all_pkgs
    assert all_pkgs <= meta.keys()
    all_lines = dict(re.findall(r'^package:(\S+)(.*)$', read(p,source_prefix+'packages_all'), re.M))
    raw = read(p,'sample_00_dumpsys_meminfo')
    pss = process_memory(raw, 'Total PSS by process:', 'Total PSS by OOM adjustment:')
    rss = process_memory(raw, 'Total RSS by process:', 'Total RSS by OOM adjustment:')
    persistent = set(re.findall(r'\*PERS\*.*? \d+:([^/]+)/',read(p,'processes_persistent')))
    records = set(re.findall(r'ServiceRecord\{\S+ u0 ([^ }]+)',read(p,'services_active')))
    rows = []
    for pkg in sorted(all_pkgs):
        lines = meta[pkg]
        def value(prefix):
            return next((x[len(prefix):] for x in lines if x.startswith(prefix)), '')
        uid_match = re.search(r'\buid:(\d+)', all_lines[pkg])
        uid = uid_match[1] if uid_match else ''
        shared = value('sharedUser=')
        cat, basis, priority, risk = category(pkg, uid, shared)
        pm = [x for x in pss if x['process']==pkg or x['process'].startswith(pkg+':')]
        rm = [x for x in rss if x['process']==pkg or x['process'].startswith(pkg+':')]
        e = re.search(r'\benabled=(\d+)', value('User 0:'))
        version = re.search(r'\bversionCode:(\d+)',all_lines[pkg])
        target = re.search(r'\btargetSdk=(\d+)',value('versionCode='))
        rows.append(dict(package=pkg, type='sistema' if pkg in package_sets['system'] else 'usuario',
                         enabled_pm=pkg in package_sets['enabled'], enabled_setting_raw=e[1] if e else '',
                         uid=uid, version_code_pm=version[1] if version else '',
                         version_name_active=value('versionName='), target_sdk_active=target[1] if target else '',
                         apk_path_active=value('codePath='), updated_system_app='UPDATED_SYSTEM_APP' in value('flags='),
                         shared_uid=shared, category=cat, category_basis=basis, priority=priority, risk=risk,
                         pss_kib_first=sum(x['kib'] for x in pm) if pm else '',
                         rss_kib_first=sum(x['kib'] for x in rm) if rm else '',
                         process_names=';'.join(x['process'] for x in pm),
                         service_records=sum(x.startswith(pkg+'/') for x in records),
                         persistent_process=any(x==pkg or x.startswith(pkg+':') for x in persistent),
                         memory_snapshot='baseline_before_user_installed_boot' if (p/'boot_update_manifest.json').exists() else 'sample_00',
                         evidence=f'{source_prefix}packages_all.txt;{meta_file.name};sample_00_dumpsys_meminfo.txt;services_active.txt'))
    write_csv(p/f'applications_inventory{output_suffix}.csv',rows)
    write_csv(p/f'removal_candidates{output_suffix}.csv',[x for x in rows if x['category']=='prescindibles'])
    write_csv(p/'processes_pss_first.csv',pss)
    write_csv(p/'processes_rss_first.csv',rss)
    samples=[]
    for f in sorted(p.glob('sample_*_meminfo.txt')):
        if not re.fullmatch(r'sample_\d{2}_meminfo\.txt', f.name):
            continue
        s=f.read_text(); mem={k:int(v) for k,v in re.findall(r'^(\w+):\s*(\d+) kB',s,re.M)}
        psi=re.findall(r'^(some|full) avg10=([\d.]+) avg60=([\d.]+) avg300=([\d.]+) total=(\d+)',s,re.M)
        row={'sample':f.stem,**{k:mem[k] for k in ['MemTotal','MemAvailable','MemFree','Cached','Buffers','SReclaimable','SUnreclaim','SwapTotal','SwapFree']}}
        row['SwapUsed']=mem['SwapTotal']-mem['SwapFree']
        row['zram_physical_kib']=mem.get('zram0','')
        row['memory_psi_some_avg10']=float(psi[0][1]);row['memory_psi_full_avg10']=float(psi[1][1])
        samples.append(row)
    write_csv(p/'memory_samples.csv',samples)
    summary=dict(counts={n:len(s) for n,s in package_sets.items()},
                 inventory_snapshot='after_user_installed_boot' if args.current else 'initial',
                 resource_snapshot='initial; not a before/after performance comparison',
                 categories=dict(collections.Counter(x['category'] for x in rows)),
                 first_batch=sorted(FIRST & all_pkgs),
                 candidates_enabled=sum(x['category']=='prescindibles' and x['enabled_pm'] for x in rows),
                 candidates_disabled=sum(x['category']=='prescindibles' and not x['enabled_pm'] for x in rows),
                 mem_available_gib=[round(x['MemAvailable']/1048576,4) for x in samples],
                 persistent_processes=sorted(persistent),
                 service_records=len(records), registered_service_lines=len(read(p,'services_registered').splitlines())-1,
                 metadata_only_packages=sorted(set(meta)-all_pkgs),
                 measurement_note='PSS aggregates per package; missing memory means not observed, not zero savings. RSS shares pages and is not additive. Categories are operational recommendations, not dependency proofs.')
    if (p/'baseline_cpu_stat.txt').exists() and (p/'cpu_stat_after.txt').exists():
        def cpu(n):
            s=read(p,n);v=list(map(int,re.search(r'^cpu\s+(.+)',s,re.M)[1].split()))[:8]
            up=float(re.findall(r'^(\d+\.\d+) \d+\.\d+$',s,re.M)[-1])
            return v,up
        before,t0=cpu('baseline_cpu_stat');after,t1=cpu('cpu_stat_after')
        delta=[b-a for a,b in zip(before,after)];total=sum(delta)
        summary['cpu_interval']=dict(seconds=round(t1-t0,2),cpu_busy_percent_of_8_cores=round(100*(total-delta[3]-delta[4])/total,3),iowait_percent=round(100*delta[4]/total,3),ticks_delta=delta,note='Read-only interval with USB and audit overhead; not electrical power or unplugged idle. Guest columns excluded to avoid double counting.')
    (p/f'summary{output_suffix}.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
