# MESTRY — Evidencias y límites de la investigación

Fecha local: **2026-10-26**, America/Santiago (UTC−03:00). Inicio 20:32:06. Alcance: lectura de cinco informes previos/ADR, inspección actual de los dispositivos, código existente y documentación oficial; siete documentos nuevos. No se implementó el diseño ni se ejecutaron los protocolos de [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md).

## Método y estados de evidencia

**Observado** corresponde a una consulta actual. **Histórico/documentado** conserva su fecha original. **Inferido** es una conclusión del código/arquitectura y se declara su límite. **Propuesto/pendiente** no es configuración entregada. Permiso/grant, archivo, proceso, servicio, hello, tarea, recuperación y disponibilidad son comprobaciones distintas.

Primero se leyeron los cinco [informes de auditoría](../../auditorias/2026-10-26/01_ESTADO_ACTUAL_MESTRY.md), el ADR Drive y handoff piloto8. Los originales congelados no se editaron. La memoria de sesiones se usó para ubicar el handoff/límites, contrastados con archivos reales. No se copiaron contraseñas, claves privadas, tokens, DB activas o conversaciones.

## 1. Registro de inspección actual

| ID / contexto | Comprobaciones ejecutadas | Resultado y límite |
|---|---|---|
| L01 — WSL, inicio 20:32 | `pwd`, fecha local, inventario/hash Python, búsqueda AGENTS, lectura de los cinco informes/ADR | 1.808 archivos /66.245.027 bytes iniciales; sin Git principal. Hash agregado y de informes conservados para cierre. No se inventa rama/commit |
| L02 — Windows, servidor ADB existente | PowerShell `Get-Process adb`, `Get-NetTCPConnection -LocalPort 5037 -State Listen`; conexión .NET al listener existente y consulta protocolo `host:devices-l` | PID10168 ya escuchaba127.0.0.1:5037. S23 serialS23_SERIAL, S25S25_SERIAL, ambos estado device. **No se ejecutó adb.exe/start-server/kill-server ni se abrió listener nuevo** |
| L03 — S23/Termux, lectura actual | Propiedades/IP por ADB; SSH alias existente con BatchMode, StrictHostKeyChecking y UpdateHostKeys=no; `id`, `pwd`, `command -v`, `df` | S23 IP192.0.2.15; SSH8023 funciona como UID 10348, home privado Termux. Python/sftp/proot-distro presentes; git/node/npm/rsync/rclone no resueltos en ese PATH. No se entró en filesystem Horus |
| L04 — S23/Horus | `getprop`, `ps -A -o USER,PID,PPID,NAME` sin args, paquete, provider público **status** una vez, servicios, uptime, SHA-256 del APK instalado | ModeloSM-S918B, Android 16/API36, ARM64, parche2026-09-05, green; Horus 1.0.4 enabled=true/configured=true/**stopped**. No Node/Codex/Dropbear/servicio terminal en muestra. APK coincide con oficial por hash. Provider puede despertar proceso app, sin iniciar remoto |
| L05 — S25 | Modelo/SDK/ABI, package info de app piloto, procesos/servicios pertinentes y ajustes VPN de lectura | SM-S938B, Android 16/API36, ARM64; piloto8/10008 instalado. Procesos cliente/ConnectBot/Tailscale no observados en muestra. Always-on/lockdown null. No se abrió app ni probó turno/túnel actual |
| L06 — FolderSync S23 | Package info/UID, appops de lectura, grants URI persistentes, directorios conocidos y metadatos externos de app | 4.14.0, UID 10353/proceso presente. MANAGE_EXTERNAL_STORAGE permitido a nivel UID; SAF persistido lectura/escritura para Documents/Mestry. DB privada denegada; carpetas backup/external/temp sin export encontrado. No exportación/depuración nueva |
| L07 — árbol compartido S23 | `ls -ld/-1` en Documents/Mestry y ramas limitadas; hashes ADR/pins/parche en copia MESTRY; búsqueda Jarvis acotada al repo | Existe `Villegol/Proyectos/mestry`. Tres archivos coinciden con WSL por SHA-256. **No existe allí docs/auditorias/2026-10-26** en la consulta; muestra concreta de diferencia, no diagnóstico de su causa. Una búsqueda amplia previa terminó por timeout y es inconclusa |
| L08 — FolderSync Desktop | PowerShell Appx/OS; sqlite3 Python `mode=ro&immutable=1`, query_only; proyección de pares/schedules/logs/filtros | Windows 11 10.0.26300, Desktop 2.13.0.0; mismo único par TwoWay Villevault, sin filtros, borrados0, conflictoSkip, reemplazoIfNewer/checksum deshabilitado. Misma cancelación/tres fallos. No se acredita todo WAL ni estado en memoria |
| L09 — rclone WSL | Lectura script/filtros y config proyectada sin valores secretos; finales de logs; procesos por nombre; `crontab -l`; versión | v1.75.2, remote gdrive/scope declarado drive, config0600. Últimos éxitos 22/10, sin rclone activo/crontab. Corrección del porcentaje en source oficial fijada abajo. No se ejecutó sync/copy/bisync/mount/dry-run |
| L10 — código/herramientas/sesiones locales | Readlink/package.json Codex, config TOML con whitelist, conteo metadata sessions, lectura fuentes/pins/launcher/manifest; `file /usr/bin/node`, versiones; AST | Codex paqueteWSL 0.164.0; CODEX_HOME `.codex-account-2`,40 archivos de sesión contados sin leer cuerpos. Python 3.12.3, Node 22.23.1, Git 2.43.0, rsync 3.2.7, glibc 2.39/x86_64.34 fuentes tools Python parsean sin errores |
| L11 — metadata Drive conectado | Plugin Drive `get_file_metadata` a cuatro IDs conocidos con campos mínimos id/name/MIME/trashed/parents/modifiedTime | Las cuatro consultas devolvieron **404 NOT_FOUND**. No prueban eliminación ni cuenta equivocada concreta; no se reautorizó ni usó otra cuenta. No se hicieron lecturas nativas con refresh que pudiera persistir tokens |
| L12 — broker Termux actual | Python por SSH, lista de nombres/modos/tamaños de estado; lectura de browser.json y SELECT seguro de journal folder; GET loopback health sin autenticación | Estado existe, archivos privados 600; raíz navegador/asignación conservadas, destino escritor histórico conservado. `http://127.0.0.1:8787/healthz` no respondió (URLError). No se leyeron valores OAuth, no refresh ni escrituras |

Las lecturas Android se enviaron mediante el protocolo del servidor ADB ya activo: seleccionar transporte por serial, ejecutar únicamente comandos shell de lectura y cerrar conexión. El helper de inspección existió solo en memoria de la herramienta; no se instaló script en teléfono/host. La lectura tenía límite de salida/timeout. No se usó shell de otra app, run-as/root, input UI, am start, service start/stop, pair, forward o reboot.

## 2. Valores y rutas que sustentan las conclusiones

### Hashes comparados

| Archivo | WSL y copia S23 compartida |
|---|---|
| ADR Drive | `02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031` |
| tools/s25-codex-client/source-pins.json | `c390ad81f55fef5f5342a50eece81bfd299b62c03abe0257c6fd7615a0eee663` |
| tools/s25-codex-client/mestry-pilot1.patch | `342b44089b8ce39876b4b4f723fb480bbaf4c93825da8bf5995d84facff8401b` |

Esto prueba tres igualdades de bytes en las muestras. No prueba igualdad de todo el proyecto, actualidad cloud, modo de sincronización Android ni acceso de Horus a la copia. Los cinco informes previos existen en WSL y su directorio no estaba en la copia compartida S23: no se declaró sincronización completa.

APK Horus leído sin copiarlo: `bf67340c4dd8321636c158902d0bf7b5a4684a23eae982d0026d45e348cb3430`, igual a release1.0.4. Su fuente local/tag `2f8f8a2faebd3d0fbd11dd83340bdcfbac437369` permite deducir mapeo `<filesDir>/horus/workspaces/default`→guest`/workspace`, home SSH y harness homes separados. **No se pudo listar ese workspace privado actual**; no se confunde inferencia del código verificado con inventario de sus archivos.

### Recursos S23, primera muestra

MemTotal7.242.340KiB; MemAvailable3.988.424KiB; `/data` total232.847.308KiB, usado33.789.964KiB, disponible198.926.272KiB. Son aproximadamente6,9068GiB visibles al kernel,3,8037GiB disponibles y189,7109GiB de disco disponible. No identifican capacidad comercial ni convierten swap/RAM Plus en RAM física. USB alimentaba el equipo; batería80%, temperatura25,2°C y thermal 0 reportado por status. Uptime5061,89s al inicio de muestras, creciendo después. No se causó reinicio ni se atribuye la ausencia del servicio a una causa concreta.

### Datos privados conservados

La inspección Termux accedió por SSH autorizado a su home, no a Horus. El navegador conserva raíz `DRIVE_FOLDER_02_EXAMPLE`, assignment al proyecto sintético; journal folder conserva `DRIVE_FOLDER_01_EXAMPLE`. No se extrajeron cuenta/token/client secrets. Presencia/mode600 no prueban validez actual de OAuth. Las cuatro raíces L11 incluyen la del piloto y los IDs de proyectos/IPRE/Villevault de [02](02_MAPA_SINCRONIZACION_REAL.md), todas no resolubles por el conector de esta sesión.

## 3. Corrección técnica: max-delete en bisync1.75.2

La auditoría anterior se apoyó en ayuda heredada que describe max-delete como cantidad. La documentación específica y **source de la misma versión instalada** aclaran el comportamiento de bisync: `excessDeletes` calcula una razón `deleted/oldCount` y la compara con `MaxDelete/100.0`; el mensaje de aborto usa porcentaje. [deltas.go v1.75.2, función excessDeletes](https://raw.githubusercontent.com/rclone/rclone/v1.75.2/cmd/bisync/deltas.go).

Por tanto `--max-delete 20` **no es protección de veinte archivos**. Es un umbral del 20% en ese control de bisync. Esto aumenta el impacto potencial sobre un árbol grande; no prueba que haya ocurrido un borrado. No se ejecutó una sincronización para probarlo. Los informes previos permanecen íntegros, y [01](01_AUDITORIA_ENTORNO_CODEX.md)/[02](02_MAPA_SINCRONIZACION_REAL.md) registran la errata.

## 4. Pruebas realizadas, históricas y excluidas

**Actuales:** conectividad/identidad mediante servidor ADB existente, SSH Termux, permisos/metadata/filesystem compartido, hashes de tres archivos y APK, lectura de logs/DB persistida, health loopback sin token y AST de 34 fuentes. Todas las conclusiones se restringen a sus resultados; se conserva el fallo health y la búsqueda timeout como fallos/inconclusos.

**Históricas, no repetidas:** las 81 pruebas locales de la auditoría anterior, tareas Codex, interrupción/recuperación, publicación de dos revisiones, UI Drive y celular/keepalive del 20–22/10. Remisiones verificables: [evidencias anteriores](../../auditorias/2026-10-26/05_EVIDENCIAS_Y_PRUEBAS.md), [handoff piloto8](../../validation/mestry-s23-remote-access-20261022T034500Z/HANDOFF.md), [handoff Drive](../../validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md). No se agregan esos conteos a un nuevo benchmark ni se usa PASS histórico para el estado actual detenido.

**No ejecutadas:** turnos de modelo, inferencia pagada/adicional, compilaciones, instalaciones, Git init/commit/push/fetch, transferencias/sync reales, mounts, cambios de filtros/permisos/cuentas, copias de sesiones o credenciales, backups/restores, publicación cloud, export de configuración Android, apertura de UI, reinicio/caída/24h. Los14 ensayos T01–T14 de [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md) son protocolos futuros.

## 5. Limitaciones actuales

Pares completos FolderSync Android y sus IDs/último resultado permanecen inaccesibles sin UI/export seguro autorizado; un grant SAF no resuelve esos campos. Horus privado no se leyó desde WSL/ADB ni se arrancó su remoto para facilitar inspección. No se inventariaron versiones actuales de node/git/compiler dentro del guest, inventario exacto de sesiones Codex S23 ni sus recursos por proyecto.

No se probó conexión actual S25/Windows al mismo hilo, traslado de un proyecto entre plataformas, ejecutabilidad de todas sus dependencias, integridad de backups o autonomía con PC apagado. El espacio Drive libre es reporte humano, no cuota consultada. Búsqueda amplia de originales en Android fue incompleta; los originales no localizados no se reconstruyen. Las puntuaciones arquitectónicas son juicios de diseño, no rendimiento, SLA ni disponibilidad observados.

Los mecanismos propuestos dependen de que los escritores participen en el control. DangerFullAccess/una shell del mismo UID no quedan confinados por una ACL o lease cooperativa. Antes de prometer exclusión fuerte o recuperación sin intervención deben resolverse esas condiciones de aceptación.

## 6. Fuentes primarias consultadas

Consulta web: **26/10/2026**. Se abrieron las páginas oficiales y, para puntos críticos, se localizaron los apartados/código pertinentes. Se resume su aplicación sin copiar manuales; documentación de producto actual **no prueba compatibilidad con la versión instalada** ni que una capacidad esté activada en MESTRY. Las conclusiones de diseño son inferencias propias sobre esas fuentes y el inventario.

| ID | Fuente primaria | Qué sustenta y qué no |
|---|---|---|
| S01 | [OpenAI app-server](https://learn.chatgpt.com/docs/app-server) | Hilos/lectura/reanudación, transportes y avisos experimentales; no migración de una ejecución viva ni compatibilidad automática del bridge propio |
| S02 | [OpenAI comandos CLI](https://learn.chatgpt.com/docs/developer-commands) | Resume y modo remoto documentados actualmente; comprobar flags/esquema de0.163/0.164 antes de emplearlos |
| S03 | [OpenAI variables](https://learn.chatgpt.com/docs/config-file/environment-variables) | CODEX_HOME y separación de ubicaciones; no copiar auth/session state por asumir home default |
| S04 | [Horus releases](https://github.com/scarif-labs/horus/releases), [fuente fijada1.0.4](https://github.com/scarif-labs/horus/tree/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369) | APK/hash y procedencia; código local de ese tag confirma paths/binds/provider/manifest. La release de rootfs separada no se interpreta como migración instalada |
| S05 | [FolderSync automatización](https://foldersync.io/docs/help/automation/), [filtros](https://foldersync.io/docs/help/filters/), [conflictos](https://foldersync.io/docs/faq/sync/), [servicios](https://foldersync.io/docs/help/supportedservices/), [CLI](https://foldersync.io/docs/help/cli/) | Capacidades de pares/SFTP/automatización y semántica de conflictos; no configura ni revela los pares privados del S23 |
| S06 | [rclone bisync](https://rclone.org/bisync/), [source v1.75.2](https://raw.githubusercontent.com/rclone/rclone/v1.75.2/cmd/bisync/deltas.go) | Listados, conflictos y umbral porcentual; source fija la corrección del informe anterior |
| S07 | [rclone copy](https://rclone.org/commands/rclone_copy/), [sync](https://rclone.org/commands/rclone_sync/) | Copy no elimina extras; sync modifica destino/borrados. Copy no convierte destinos mutables en backup versionado |
| S08 | [rclone mount](https://rclone.org/commands/rclone_mount/), [backend Drive](https://rclone.org/drive/) | VFS, permisos/enlaces traducidos y alcance backend; no POSIX completo compartido entre apps ni FUSE Android probado |
| S09 | [Git bundle](https://git-scm.com/docs/git-bundle), [update-ref](https://git-scm.com/docs/git-update-ref) | Transferencia de objetos/refs y actualización con old-oid; no transfiere por sí sola trabajo sin commit, DB o procesos |
| S10 | [Git fetch](https://git-scm.com/docs/git-fetch) | Recepción de objetos/refs; no implementación automática de lease, backup o promoción segura del working tree |
| S11 | [rsync oficial](https://download.samba.org/pub/rsync/rsync.1) | Copia/deltas/atributos por SSH; requiere extremos compatibles y no snapshot global de DB activas |
| S12 | [Python venv](https://docs.python.org/3/library/venv.html), [tags de plataforma PyPA](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/) | Rutas/ABI/CPU/plataforma/libc y reconstrucción de entornos, no garantía de build determinista sin inputs completos |
| S13 | [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/), [addons Node](https://nodejs.org/api/addons.html) | Lock coherente, eliminación del destino node_modules y módulos nativos; no autoriza reinstalar ni actualiza el Node existente |
| S14 | [SQLite Backup API](https://sqlite.org/backup.html), [WAL](https://sqlite.org/wal.html), [riesgos de copia](https://sqlite.org/howtocorrupt.html) | Coherencia/locks/journals y restauración; no API de migración oficial de Codex ni licencia para copiar internals activos |
| S15 | [Android all-files](https://developer.android.com/training/data-storage/manage-all-files) | Permiso amplio no concede datos privados de otra app; SAF sigue reglas propias |
| S16 | [Doze](https://developer.android.com/training/monitoring-device-state/doze-standby), [restricciones foreground](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start) | Condiciones Android de ejecución/arranque; wake lock o exención no constituyen SLA |
| S17 | [Cambios Android 16](https://developer.android.com/about/versions/16/behavior-changes-all) | Cuotas JobScheduler/WorkManager incluso en ciertos casos con foreground; no se ejecutaron comandos de override mostrados por la guía |
| S18 | [Direct Boot](https://developer.android.com/privacy-and-security/direct-boot) | CE tras primer desbloqueo y componentes explícitos para Direct Boot; no mover secretos a DE ni desactivar bloqueo para lograr disponibilidad |
| S19 | [Termux:Boot oficial](https://github.com/termux/termux-boot/blob/master/README.md) | Scripts y wake lock de arranque bajo su UID; no control automático del provider Horus ni prueba de recuperación completa |
| S20 | [Tailscale Android](https://tailscale.com/docs/install/android), [split tunneling](https://tailscale.com/docs/features/client/android-app-split-tunneling) | Cliente Android/red por aplicaciones; no acredita policy/grants actuales del panel ni un túnel abierto |
| S21 | [VS Code Remote-SSH](https://code.visualstudio.com/docs/remote/ssh) | Limitación oficial para hosts Alpine/non-glibc; no invalidación de SFTP/terminal u otros clientes |
| S22 | [Android Studio requisitos](https://developer.android.com/studio/install#linux) | Linux ARM no soportado para Studio actual; no prueba de imposibilidad de cada toolchain comunitario |
| S23 | [Syncthing FAQ](https://docs.syncthing.net/users/faq.html), [retiro oficial wrapper Android](https://forum.syncthing.net/t/discontinuing-syncthing-android/23002) | Capacidades P2P y necesidad de evaluar soporte del wrapper por separado; no se seleccionó/instaló un fork |
| S24 | [rclone changelog](https://rclone.org/changelog/), [subidas Drive](https://developers.google.com/workspace/drive/api/guides/manage-uploads) | Release1.75.2 del 09/10 y opciones de upload, incluida reanudación; no valida uploader actual de backups ni concede permisos |

Incidencias de investigación: `/changes/` rclone no accesible por herramienta, resuelto con `/changelog/`; Wiki Alpine respondió403 y no se usó como evidencia concluyente; rutas adivinadas `bisync.go` y config-locations de OpenAI devolvieron404, no se atribuyó contenido. Sí se obtuvo `deltas.go`1.75.2 y documentación OpenAI de variables/app-server. Los resultados de búsqueda secundarios no sustentan conclusiones técnicas; se priorizaron las fuentes primarias anteriores.

## 7. Respuestas verificables a los 14 criterios de investigación

| Pregunta | Respuesta y referencia |
|---|---|
| 1 Workspace principal | Privado Horus/S23; conservar instalación, no carpeta SAF como checkout activo. [01](01_AUDITORIA_ENTORNO_CODEX.md), [05](05_ARQUITECTURA_RECOMENDADA.md) |
| 2 Acceso desde dispositivos | S25 existente; Windows/helper SSH compatible pendiente; otros clientes por identidad/alcance, sin abrir puertos públicos. [05](05_ARQUITECTURA_RECOMENDADA.md) |
| 3 Archivos a replicar | Fuente/config portable, inputs/resultados únicos y artefactos cerrados por manifiesto; no todo home. [03](03_PORTABILIDAD_Y_PERSISTENCIA.md) |
| 4 Dependencias independientes | Por SO/CPU/libc/runtime/ABI/rutas/toolchain; conservar cápsulas locales en lugar de trasplantar. [03](03_PORTABILIDAD_Y_PERSISTENCIA.md) |
| 5 Ejecutabilidad | Aceptación por target y restauración; no declararla por tener lockfile. [03](03_PORTABILIDAD_Y_PERSISTENCIA.md), [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md) |
| 6 Sesiones Codex | Mismo backend conserva hilo; dos instalaciones usan handoff, no DB viva compartida. [03](03_PORTABILIDAD_Y_PERSISTENCIA.md) |
| 7 Inicio/cierre WSL | Preflight/propiedad/base; entrega con recibos, dependencias y backup. [05](05_ARQUITECTURA_RECOMENDADA.md) |
| 8 S23 continuo/bajo demanda | Servicio/health y documentos según sus pares, publicación de entregas/backup por eventos; no polling masivo de todas las dependencias. [02](02_MAPA_SINCRONIZACION_REAL.md), [05](05_ARQUITECTURA_RECOMENDADA.md) |
| 9 Papel de herramientas | Drive originales/recuperación; FolderSync documentos; Git versiones; SSH transporte; rclone artefactos/réplicas con política. [02](02_MAPA_SINCRONIZACION_REAL.md), [04](04_COMPARACION_ARQUITECTURAS.md) |
| 10 Conflictos | Propietario/época, admisión, base/CAS y staging; límite ante actores no cooperantes del mismo UID. [05](05_ARQUITECTURA_RECOMENDADA.md) |
| 11 PC apagado | S23 sirve última confirmada si runtime/red vivos; backup autónomo S23 todavía pendiente. [05](05_ARQUITECTURA_RECOMENDADA.md) |
| 12 Recuperación | Capas de backup, journal/UNKNOWN y restore por target; primer desbloqueo/arranque no automático garantizado. [05](05_ARQUITECTURA_RECOMENDADA.md), [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md) |
| 13 Conservar/corregir/reemplazar | Conservar Codex/Horus/S25/SSH; revisar pares y espejos operativos; reemplazar patrón de copia de estado vivo, no plataformas por defecto. [04](04_COMPARACION_ARQUITECTURAS.md) |
| 14 Pruebas pendientes24/7 | I1–I3 y T01–T14; PC apagado/restore/24h/reinicio, con aceptación explícita de intervención. [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md) |

## Control de calidad e integridad

Línea base de esta investigación:1.808 archivos /66.245.027 bytes, SHA-256 agregado `dc31ac91dd10b4c25318d4a4f64e32ff2bc0103a71eb4e9f16390f08f9194821`. Algoritmo: rutas relativas ordenadas; por archivo `ruta + NUL + SHA256(bytes).hexdigest() + LF`, UTF-8; SHA-256 del conjunto. Excluir solo esta nueva carpeta al comparar. Los cinco informes anteriores y ADR tienen huellas de inicio independientes.

Se tomaron huellas de 14 archivos protegidos externos: rclone/config/filtros, SSH, script y DB/WAL/SHM FolderSync Desktop, sin imprimir material privado. El control final comprobará su contenido; no certifica estado en memoria, atimes ni archivos privados de teléfonos inaccesibles.

No hubo arranque del daemon ADB: se reutilizó el existente. **Efecto limitado de lectura:** consultar status puede crear el proceso proveedor Android Horus; se observó ese proceso después, sin servicio remoto/Node/Codex. No se activó backend, ni se configuró o detuvo sincronizador/servicio. Por ello se evita la afirmación absoluta de inspección enteramente pasiva a nivel de todo proceso Android.

Control realizado a las **21:08:10 −03:00**: siete entregables exactos, 43 enlaces locales sin destino/ancla faltante, 43 URLs de referencia registradas, fences de código equilibrados y cero coincidencias de claves privadas/access-refresh tokens/API keys/correos en los patrones aplicados a los nuevos informes. No es certificación de ausencia de todo secreto en sistemas inaccesibles o imágenes históricas.

Los 1.808 archivos originales / 66.245.027 bytes conservan exactamente el SHA-256 agregado de inicio; los cinco informes anteriores y el ADR mantienen sus huellas. Los 14 archivos protegidos externos no presentan diferencias. La última revisión repite únicamente enlaces/patrones/integridad después de ajustes documentales; no vuelve a ejecutar pruebas funcionales ni consultas de servicios.

Coherencia revisada: D0–D4 no se confunden; I2 permite backup sintético con transporte PC existente y no depende de la autonomía de I3; las 81 pruebas anteriores siguen históricas; los 34 análisis sintácticos actuales no se declaran aceptación del diseño; el 20% de bisync queda corregido; copia compartida no se llama workspace Horus; servicios detenidos no se declaran saludables; Windows/helper/coordinador/Git/cápsulas siguen propuestos. No hay aprobación de implementación implícita ni cambios en arquitectura congelada.
