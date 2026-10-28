# MESTRY — Evidencias, pruebas y control de integridad

Fecha local: **2026-10-26**, America/Santiago, UTC−03:00. Inicio observado: **17:52:30**. La recolección de sistema/red/sincronización se realizó durante esta sesión; el primer control de integridad posterior a la redacción fue **18:11:10**. Los resultados históricos conservan sus propias fechas UTC/locales. No se trata la fecha de lectura de un registro como fecha de repetición de su prueba.

## Método, alcance y minimización

Se usaron comandos de inspección locales, consultas Windows, SQL selectivo de lectura y metadata de Drive. Los resultados se resumen aquí; los originales de validación siguen en sus rutas, sin copiarse a una nueva colección. Los únicos archivos añadidos al árbol MESTRY fueron los cinco Markdown solicitados; las pruebas locales usaron temporales que limpiaron al terminar. No se guardaron dumps de cuentas, configuración confidencial, logcat, historial personal, contraseñas, claves privadas o tokens.

El registro agrupa comandos repetidos de búsqueda/lectura por operación y declara sus límites. Los bloques son **registro de lo ejecutado**, no instrucciones para reejecutar scripts antiguos. Los tests seleccionados usan fixtures/temporales, mocks y análisis local; no se ejecutaron suites que requiriesen listeners, dispositivos, instalación o APIs externas. Se usó `python3 -B`/`PYTHONDONTWRITEBYTECODE=1` para evitar nuevos `.pyc`.

Los estados y hallazgos se consultan en [01](01_ESTADO_ACTUAL_MESTRY.md); rutas/flujos en [02](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md); decisiones y componentes en [03](03_TRAZABILIDAD_ARQUITECTONICA.md); siguientes tareas en [04](04_PLAN_DE_CONTINUIDAD.md).

## E01 — Entorno, inventario y ausencia de Git

Contexto: WSL, 26/10, desde `/home/developer/proyectos/mestry`.

Comandos ejecutados: `pwd`, `date --iso-8601=seconds`, `uname -a`, `df -h / /mnt/c`, `free -h`, `ls -la`; comprobación de `AGENTS.md` en ancestros y búsqueda con `rg --files`; `git rev-parse --show-toplevel`, `git status --short --branch`, `git log -1 --format='%H %cI %s'`; inventario Python de rutas/tamaños/extensiones; `find /home/developer/proyectos -maxdepth 4 -type d -name .git`.

Resultados: Ubuntu 24.04 sobre WSL2, kernel `6.18.33.1-microsoft-standard-WSL2`, x86_64. `/`: 1.007G total, 63G usados, 893G disponibles según salida human-readable de `df`; C: 476G total, 406G usados, 70G disponibles. `free`: 11 GiB totales visibles a WSL, unos 10 GiB disponibles en esa muestra, swap 4 GiB sin uso. **No son recursos del S23.**

Inventario inicial: **1.803 archivos / 66.129.015 bytes**; 78 Markdown en todo el árbol, 22 directamente bajo `docs/`; dos Markdown en raíz. No hay `.git`, `.gitignore`, `.github` ni manifiesto de proyecto global. Los comandos Git terminaron con «not a git repository». No existe rama/commit ni estado de cambios sin confirmar que pueda informarse como propio de MESTRY. Se localizaron `.git` de `app_fotos` y `app_gastos`, ajenos a MESTRY.

No se encontró `AGENTS.md` aplicable al árbol principal/ancestros examinados. Se leyó el `AGENTS.md` de la copia upstream piloto8 antes de revisar sus fuentes. Describe bridge liviano, Kotlin/Compose/OkHttp y responsabilidades por controlador; sus defaults históricos no prevalecen sobre el parche del piloto ni sobre las restricciones actuales del usuario.

Raíz/workspace modo 0755, sin symlink; búsqueda Python no encontró symlinks internos. El inventario no prueba permisos de escritura Android/Drive.

## E02 — Descubrimiento documental

Se ejecutaron búsquedas `rg --files` por Jarvis/MESTRY y una búsqueda Python por **los cinco nombres exactos ausentes**. Raíces explícitas: `/home/developer/proyectos`, `/home/developer/IPRE`, Documents/Desktop/Downloads del perfil Windows y, al descubrirse, `Villevault`. La primera búsqueda acotada examinó **2.674 directorios**, sin errores de acceso ni corte temporal; Villevault añadió **1.045 directorios**, sin corte temporal. También hubo una búsqueda exploratoria por el home, sin usarla como prueba de cobertura exhaustiva.

Exclusiones de recorrido incluyeron `.git`, node_modules, build, venv/.venv, runtime, `.cache`, `.local`, `.codex`, `.gradle`, AppData, `.entorno` y `analisis_codex`; en Villevault además papelera y temporales Drive. **No se afirma que se revisaron todos los discos, cuentas, contenedores o directorios excluidos.**

Resultado: ninguna coincidencia de los cinco archivos históricos solicitados; el ADR Drive sí está en raíz. Se inspeccionaron README, decisiones, informes técnicos, planes, guías y handoffs. La tabla de [03](03_TRAZABILIDAD_ARQUITECTONICA.md) identifica propósito, relación y vigencia. Búsquedas cloud relacionadas: E13.

## E03 — Fuente congelada y criterios normativos

Archivo: [ADR Drive original](../../../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md), versión 1.0 del 19/10. Se leyeron sus decisiones, alcance, fronteras, sincronización, seguridad, aceptación, compatibilidad y ADR; pseudocódigo/esquemas se trataron como diseño, no como código ejecutado.

SHA-256 inicial y posterior: `02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031`.

Referencias verificables: §1 D-01–D-15; §20.3 AC-01–AC-12; §26 compatibilidad con fuentes ausentes; §29 ADR 001–011. El documento declara implementación no presumida y distingue explícitamente SQLite/FTS5, WorkManager y embeddings de decisiones congeladas. No se modificó.

## E04 — Fuentes, procedencia y dependencias

Se leyó [source-pins.json](../../../tools/s25-codex-client/source-pins.json), se contrastaron SHA-256 de cada `after_sha256` y del [parche](../../../tools/s25-codex-client/mestry-pilot1.patch) con la copia:

`/home/developer/.cache/mestry/s25-auto-vpn-20261022T034500Z/reproduced-pilot8`

Resultado: **68 archivos esperados, cero ausentes, cero diferencias**; hash del parche coincide: `342b44089b8ce39876b4b4f723fb480bbaf4c93825da8bf5995d84facff8401b`. Procedencia declarada: upstream commit `538d65f67e34907789237fc71f56e8ca95d9f3cb`, archivo upstream SHA-256 `ff8d68e74d4045268a80dde2d9e55f6e131825ee14ddac2a2e5b4dd40dff501e`. No se descargó de nuevo upstream ni se hizo `git fetch`; la procedencia se apoya en pins/registros existentes, no en nueva validación de red.

La copia no tiene `.git`. Existe wrapper JAR y su SHA-256 coincide con el pin, pero no `node_modules/ws/package.json` en esa copia. Se leyeron package.json/package-lock, `.gitignore`, Gradle y manifiesto Android. Versiones declaradas: Node requerido ≥20; `ws ^8.18.3` (resolución **8.20.1** en lockfile v3, sin módulo instalado en esa copia); Gradle 8.13 con distribución y hash fijados; Android Gradle Plugin 8.13.2; Kotlin/Compose plugin 2.2.0; Compose BOM 2024.09.00; activity-compose 1.12.2; OkHttp 4.12.0; compile/target SDK 36, min SDK 26. Piloto8 versionCode 10008. Dependencias bootstrap OAuth: `google-auth==2.62.0`, `google-auth-oauthlib==1.5.0`.

El `.gitignore` upstream excluye node_modules, builds, gradle, keystores y archivos de planificación, entre otros. **No protege un árbol que se sincroniza por otro programa con otros filtros.** No existe `.gitignore` principal MESTRY. No se encontró CI propia en raíz ni `.github` en la copia revisada.

Herramientas actuales leídas con `--version`/`command -v`: Python 3.12.3, Node v22.23.1, Git 2.43.0, npm, SSH, rclone y ADB Windows; Java/javac no resueltos en el PATH consultado. No se ejecutó compilación ni se instaló `ws`. No se consultaron registros de versiones/CVE: **no se adjudica obsolescencia o vulnerabilidad específica sin esa evidencia**.

## E05 — Revisión estática funcional y de fronteras

Archivos principales leídos: [drive_browser.py](../../../tools/horus_publish/drive_browser.py), [publisher.py](../../../tools/horus_publish/publisher.py), [pilot-policy.mjs](../../../tools/s25-codex-client/pilot-policy.mjs), [horus_keepalive.py](../../../tools/s23-remote-access/horus_keepalive.py), preflight/control/upgrade/tests y fuentes de launcher Horus conservadas en caché.

Observaciones respaldadas por código: navegador con operaciones `state`, `folder.enable`, `assign`, `list`, `read`; raíz habilitada/ascendencia y papelera verificadas; sin seguir shortcuts; lectura texto/Markdown o exportación texto Docs, otros formatos delegados a Drive; proyecto fijo `/workspace/projects/mestry-horus-smoke`. No se encontró feed incremental/cursor de corpus, índice RAG o Core de producto integrado.

El publicador acota fixture/destino/tamaño y registra IDs/journal antes de publicar; pruebas de idempotencia/readback separadas del flujo de navegador. La política bridge valida header en tiempo constante, sesiones/rutas reales y política efectiva `never / dangerFullAccess`. La fuente advierte que es ACL de aplicación, **no sandbox del SO**. El watchdog no mata bridge vivo y falla cerrado si no puede confirmar propiedad/estado.

Manifiesto Android piloto8: backup deshabilitado, servicio VPN de aplicación no exportado y foreground, paquetes Tailscale/ConnectBot consultables, cleartext permitido para transporte loopback. Eso no verifica el estado instalado hoy, ni autoriza exponer WS fuera del túnel. No se observaron componentes de voz, teclado/overlay, Reasoning Engine, Free Model Broker, Calendar/Canvas/Gmail o Device Agent autónomo integrados en las fuentes revisadas.

## E06 — Pruebas realizadas durante esta auditoría

Se revisó el código de prueba antes de seleccionar suites. Comandos ejecutados desde el workspace, todos con finalización correcta:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tools/horus_publish -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tools/s23-remote-access -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tools -p 'test_horus_pair_s25.py'
node --test tools/s25-codex-client/pilot-policy.test.mjs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/s25-codex-client python3 -B -m unittest test_helpers.HelperTests.test_private_pairing_write_and_stale_process_refusal test_helpers.HelperTests.test_install_refuses_wrong_profile_before_writing test_helpers.HelperTests.test_upgrade_checks_hashes_and_tracks_unfinished_turns
```

| Suite | Resultado directo | Qué demuestra / qué no demuestra |
|---|---|---|
| Publicador/navegador/Picker Python | **54/54**, OK, 0,709 s | Validación, permisos/límites e idempotencia con Drive falso y operaciones simuladas; no autoriza Google ni publica |
| Watchdog/observación de red-historial | **8/8**, OK, 0,004 s | Fallo cerrado y clasificación de evidencia con mocks; no prueba un fallo real/recuperación de Android |
| Límites helper emparejamiento | **13/13**, OK, 0,009 s | Sanitización/validación y transporte simulado; no empareja teléfonos ni usa contraseñas reales |
| Política Node | **3/3**, cero fallos/omitidos, duración total ≈82,6 ms | Headers, política real requerida, sesiones, rutas y escapes de symlinks con fixtures locales; no arranca bridge |
| Helpers seleccionados | **3/3**, OK, 0,020 s | Escritura privada temporal, rechazo de perfil incorrecto antes de instalar y comprobación de manifests/turnos incompletos; no despliega ni hace SSH real |

Total **81 casos actuales: 78 Python + 3 Node, sin fallos**. Los tiempos pertenecen a esta máquina WSL y no son benchmarks del S23. Además se ejecutó `ast.parse` en **34 archivos Python bajo `tools/`**, sin errores; no generó bytecode. Los 65 `.py` del inventario completo también incluyen evidencia/fixtures históricos: no son 65 módulos productivos.

Se omitió deliberadamente `test_staging_serves_only_fixed_code_artifact_and_closes_on_stop`, que crea listener/subproceso de staging. Tampoco se ejecutaron tests de integración/handshake Node con bridge o suite upstream completa: falta `ws` en la copia piloto8 y varias pruebas abren sockets. No se ejecutó npm install/audit, Gradle, instrumentación Android ni simulación de caídas. No se suman estos 81 casos a los conteos históricos como si fueran capacidades o pruebas independientes adicionales del producto.

## E07 — ADB y desviación de proceso host

Comando ejecutado: `adb.exe devices -l`, utilizando el ADB Windows existente en el SDK Android del perfil Windows. Resultado: **lista de dispositivos vacía**. Antes de la lista ADB emitió:

```text
daemon not running; starting now at tcp:5037
daemon started successfully
```

Esta consulta **inició automáticamente el daemon host**, pese a haberse tratado como enumeración. Es una excepción real a la regla de no modificar procesos; no se presenta la ejecución como enteramente libre de efectos. Posteriormente Windows observó `adb` PID 8532. **No hubo comandos ADB shell, input, install, push/pull, forward/reverse o reinicio sobre teléfonos durante esta auditoría.** No se paró el servidor para ocultar/revertir la observación mediante otra mutación.

Resultado de auditoría Android actual: **BLOQUEADO / SIN ACCESO**. La ausencia de dispositivos no permite afirmar Android/servicios/paquetes actuales. Mejora operativa futura: comprobar proceso/puerto host antes de invocar una herramienta que puede autoarrancar su daemon.

## E08 — SSH y ruta privada al S23

Se inspeccionó `ssh -G mestry-s23` filtrando únicamente host, usuario, puerto, identityfile, strict checking y campos de salto conocidos, sin abrir claves privadas. El alias conservado apunta a `192.0.2.15:8023`, usuario Termux `u0_a348`, identidad dedicada y verificación estricta. Es configuración existente, no dirección LAN vigente reconfirmada.

Comando real de sonda:

```sh
timeout 12 ssh -o BatchMode=yes -o ConnectTimeout=7 -o ConnectionAttempts=1 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ControlMaster=no mestry-s23 'printf "MESTRY_READONLY\n"; id; uname -m'
```

Resultado: `No route to host`; **el comando remoto no se ejecutó**. Se intentó además `socket.create_connection(('192.0.2.11', 8023), timeout=3)` en Python: **TimeoutError**. No hubo login ni solicitud de contraseña; no se cambiaron alias, known_hosts o rutas. No se intentó entrar al perfil privado Horus desde WSL.

No se resolvió `tailscale` como ejecutable WSL. Estas sondas no diagnostican el estado Android ni descartan acceso desde S25: solo prueban falta de acceso desde este entorno en ese momento.

## E09 — rclone, script, filtros y activación

Comandos/operaciones: `rclone version`; `rclone bisync --help` filtrado a flags pertinentes; lectura de `/home/developer/sincronizar-mestry.sh` y filtros; Python `RawConfigParser` sobre configuración, **mostrando solo tipo/scope/presencia de campos sensibles y modo**; búsqueda selectiva de invocaciones del script en historial shell; inventario de procesos por nombre; `crontab -l`; `systemctl --user list-timers --all`, servicios de usuario y `systemctl list-timers --all`; búsquedas de referencias rclone/mestry en directorios de scripts/unidades.

Resultado: rclone **v1.75.2**, Ubuntu 24.04/amd64; remote `gdrive`, tipo Drive, scope declarado `drive`, configuración 0600. No se volcó configuración ni se ejecutó rclone contra la nube. El script y los flags se detallan en [02 §4](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md#4-rclone-wsl-flujo-reconstruido).

Rutas persistentes verificables:

- Script: `/home/developer/sincronizar-mestry.sh`, modo 0644, mtime 22/10 01:11:43 local.
- Filtros: `/home/developer/.config/rclone/mestry-bisync.filters`, modo 0644, mtime 22/10 12:35:06 local, SHA-256 `13cf61725e39a04bc718db077bdc6c059f2d195ee94e6e16ff6cbdc81d373d2d`. Su MD5 calculado coincide con el archivo de control existente.
- Logs: `~/.local/state/mestry-bisync/IPRE.log` y `proyectos.log`, modo 0640; 105.204 y 13.094 líneas respectivamente.
- Estado/listados: `~/.cache/rclone/bisync/` y lock `~/.local/state/mestry-bisync/sync.lock`.

Se leyeron finales/resultados de logs en memoria, no se copiaron logs completos. `IPRE.log` contiene **tres líneas nivel ERROR**, incluido fallo por permiso al abrir un JAR y aborto que pedía resync. Su última ejecución termina correctamente el 22/10 13:00:39. `proyectos.log` no contiene líneas nivel ERROR y termina correctamente el 22/10 15:22:37. **Buscar la palabra error dentro de una ruta no cuenta como línea ERROR**; se corrigió ese posible sesgo usando el delimitador de nivel. Avisos de symlinks omitidos son limitaciones, no razón para activar `--copy-links` automáticamente.

No había rclone activo en las muestras de procesos. `crontab -l`: no crontab del usuario. Solo se vio un timer de usuario ajeno a MESTRY y 12 timers de sistema comunes; no referencias de sincronización MESTRY en los lugares examinados. El historial seleccionado contiene preview/init y validación shell del script; no prueba un horario recurrente. No se ejecutó `preview`, `init`, `run`, `sync`, `copy`, `bisync` o `resync` durante esta auditoría.

## E10 — Listados históricos frente al workspace local

Se leyeron:

`~/.cache/rclone/bisync/home_developer_proyectos..gdrive_.path1.lst`

`~/.cache/rclone/bisync/home_developer_proyectos..gdrive_.path2.lst`

Cabeceras: 22/10/2026, **18:22:37 UTC**. Ambos aportan el mismo conjunto de rutas/tamaños inspeccionado. Hay **1.840 entradas MESTRY incluyendo directorios; 1.793 son archivos**. No se confunden ambos conteos.

Comparación con el inventario inicial: 1.793 rutas de archivos comunes, ninguna diferencia de tamaño; cero archivos del listado ausentes localmente; diez locales adicionales, todos `.pyc` preexistentes. Los listados tienen campos de hash ausentes (`-`): **no hay prueba de igualdad de bytes actual, ni consulta cloud del 26/10**.

En el listado path2 de todo `proyectos`, coincidencias de ruta: `/.git/` **5.066 entradas**; `/build/` **5.655**; `/node_modules/` y `/__pycache__/` cero. Se observaron las rutas `.git/config` de proyectos vecinos sin abrir sus contenidos. Búsqueda por clases de archivos sensibles (`.env`, keystores, signing properties, token.json, credentials.json, id_ed25519/id_rsa) sin coincidencias en las expresiones empleadas; no cubre cualquier posible nombre/formato secreto.

## E11 — Windows, programas, procesos y tareas

Consultas PowerShell ejecutadas en modo no interactivo: `Get-CimInstance Win32_OperatingSystem`; `Get-Process` filtrado por nombres pertinentes; `Get-Service` filtrado; `Get-ScheduledTask` y metadatos de tareas seleccionadas; `Get-ItemProperty` de claves de software instalado; `Get-AppxPackage` para FolderSync; `Get-PSDrive`; `Get-Item`/`Get-ChildItem` para raíz Villevault y directorios de datos de la app. No se abrieron aplicaciones ni se activaron tareas.

Resultados: Windows **11 Home Single Language**, versión `10.0.26300`; Google Drive **132.0.0.0** registrado; FolderSync Desktop Appx **2.13.0.0**. La consulta Appx fue necesaria: la primera búsqueda de programas de escritorio por registro no detectaba ese paquete; no se concluyó prematuramente que FolderSync estuviera ausente.

La enumeración de tareas Windows informó **OK, 236 tareas**, cero coincidencias MESTRY/rclone/FolderSync o ejecución WSL en el filtro utilizado. Esto no excluye el scheduler interno de FolderSync ni tareas de nombre/acción no reconocidos. Unidades filesystem visibles C: y D:; no se atribuye contenido inspeccionado de D: ni una unidad Drive montada.

Se observó SuperDisplay **Running / Automatic**, diferente de Stopped / Auto histórico. No se consultó/modificó su política de recuperación actual ni se lo detuvo. No se encontró GoogleDriveFS o rclone en la consulta de procesos pertinentes; una consulta posterior por executable path del paquete FolderSync no devolvió procesos. La raíz Villevault y sus directorios inmediatos no mostraron reparse link. No se deduce que todo archivo descendiente sea una copia independiente.

## E12 — FolderSync Desktop: configuración y resultados persistidos

Se descubrió la DB mediante listado de rutas, sin abrir la aplicación. Ruta completa en [02 §5](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md#5-foldersync-desktop-windows). Lectura Python SQLite con URI `mode=ro&immutable=1` y `PRAGMA query_only=ON`. Hay DB/WAL/SHM; no se hizo checkpoint, backup o copia de sus bytes. **No se acredita cobertura de todos los frames WAL pendientes.**

Se consultaron nombres/esquemas de tablas y **columnas explícitas permitidas**. Para `accounts`, solo id, tipo, loginValidated, conversión Docs y archived; no se seleccionaron loginName/password/accessKey/accessSecret ni valores de credenciales. Para pares, no se seleccionaron passwords de cifrado ni changes tokens. Se analizaron errores en memoria y solo se emitieron categoría/tipo y contadores; sin rutas personales de documentos o cuerpos de error completos.

Proyección reproducible de consultas principales:

```sql
SELECT id, accountType, loginValidated, convertGoogleDocsFiles, archived
FROM accounts;
SELECT id, isEnabled, leftAccountId, leftFolderDisplayPath,
       rightAccountId, rightFolderId, rightFolderDisplayPath,
       syncStatus, syncDirection, syncLastRun, syncDeletionEnabled,
       syncUseRecycleBin, syncReplaceFileRule, syncConflictRule,
       syncDisableChecksumCalculation, syncMonitorDeviceFolder,
       syncModeBackup, remoteChangesCheckEnabled
FROM v2_folderpairs;
SELECT id, folderPairId, cronString, enabled, requireCharging,
       requireVpn, useWifiConnection, useEthernetConnection
FROM v2_folderpair_schedules;
SELECT id, status, createdDate, endSyncTime, filesChecked,
       length(errors), source
FROM v2_sync_logs;
SELECT syncLogId, logType, count(*), sum(dataTransferred)
FROM v2_sync_log_items GROUP BY syncLogId, logType;
```

Se consultaron además contadores/filtros y campos de política indicados en [02](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md). Resultado: dos conexiones (local/GoogleDrive), un par v2 habilitado, tres schedules habilitados, cero filtros v2 y cuatro registros de ejecución. Tablas legacy folderpairs/synclogs vacías: no equivalen a ausencia del par v2.

Último registro termina **23/10 01:03:21.224 local**, `SyncFailed`, coherente con `syncLastRun` 1792728201224. Estados: una cancelación, tres fallos, **cero éxitos finales observados**. La ejecución 2 registra 131.643 TransferFile / 11.789.247.602 bytes, 12.239 CreatedFolder y seis TransferError. Filas de estado: 143.882; log items: 143.888. Esos conceptos no se suman como documentos únicos ni acreditan integridad cloud.

Conteos de patrones sobre `itemKey`: node_modules 97.320, build 10.482, `.git/` 2.637; pueden solaparse. La expresión `mestry/` no encontró entradas, pero no demuestra que ninguna nota haga referencia al proyecto. La falta de filtros y la presencia de dependencias son evidencia suficiente del riesgo de alcance. No se diagnosticó la causa final de errores solo a partir de términos de permiso/cuota.

## E13 — Lecturas mediante Google Drive conectado

Se aplicó la habilidad `google-drive:google-drive` para descubrimiento/metadata. Herramientas ejecutadas:

- `google_drive_search(query="MESTRY", topn=30, best_effort_fetch=false)`: resultados vacíos.
- `google_drive_search(query="Jarvis", topn=20, best_effort_fetch=false)`: resultados vacíos.
- `google_drive_get_file_metadata` sobre raíz piloto `DRIVE_FOLDER_02_EXAMPLE`, solicitando solo id/nombre/MIME/papelera/fecha/capacidades/padres: **404 NOT_FOUND**.
- La misma herramienta sobre antiguo Horus `DRIVE_FOLDER_01_EXAMPLE`, metadata mínima: **404 NOT_FOUND**.

No se solicitaron contenidos personales, exportaciones, escrituras, restauración o reautorización. No se usó una cuenta alternativa ni se intentó ampliar acceso para sortear el resultado. **404 significa recurso no resoluble para esta conexión; no determina eliminación, cuenta equivocada o revocación concreta.** La cuenta de este conector no se equipara con OAuth Termux/rclone/FolderSync. No se ejecutó rclone remoto como fallback porque podría renovar/persistir credenciales y no aporta la configuración Android faltante.

## E14 — Seguridad y revisión de exposición

Se inspeccionaron permisos/rutas y exclusiones; no se copiaron secretos. El scanner local buscó encabezados de clave privada, campos JSON de access/refresh token con valores de apariencia real y formato de clave secreta OpenAI, sin emitir valores coincidentes. Resultado inicial: **cero coincidencias en archivos de texto examinados**; se excluyeron PNG/bytecode. Los patrones son acotados, no una certificación de ausencia de secretos en capturas, binarios, nombres inusuales o sistemas inaccesibles.

La configuración rclone 0600 y la separación UID Termux/Horus histórica son controles positivos dentro de su alcance. Scope declarado amplio en rclone y filtros sin política general de secretos son riesgos pendientes; **no se observó una credencial concreta publicada por sincronización**. La DB FolderSync contiene esquema de campos de autenticación, que no se seleccionaron; no se adjudica su formato de cifrado por la existencia de una columna.

No se inspeccionaron ACL efectivas Google, grants actuales del S23, permisos de almacenamiento compartido Android, identidad de cada cuenta, cifrado integral o recuperación desde respaldo. Son límites explícitos de la revisión de seguridad.

## Evidencias históricas: pruebas no repetidas

Estas evidencias se **leyeron durante la auditoría**, pero sus experimentos no se ejecutaron de nuevo. Un resultado histórico puede sustentar «IMPLEMENTADO Y VERIFICADO» en su fecha/alcance; el funcionamiento actual inaccesible sigue sin confirmación.

| ID | Fecha/contexto original | Referencia verificable | Resultado y límite conservado |
|---|---|---|---|
| H01 | 20/10, EXP06, Codex local en S23 | [summary.json Horus](../../validation/mestry-horus-20261020T194336Z/summary.json), [flags efectivos](../../validation/mestry-horus-20261020T194336Z/codex_effective_flags.json), [recursos finales](../../validation/mestry-horus-20261020T194336Z/final_resources.json), [informe](../../HORUS_REPORT.md) | PASS histórico: Horus 1.0.4/Alpine 3.24.0, Codex 0.163.0, dos tareas sintéticas; cinco pruebas independientes en teléfono y hashes coincidentes. Recursos son muestras posteriores, no pico. Login y aceptación de danger-full-access con origen humano explícito. Estado remoto apagado en EXP06 actualizado por experimentos posteriores |
| H02 | 21/10, app r4 y continuidad de acceso | [result.json r4](../../validation/mestry-s25-resumed-20261021T154810Z/result.json), [handoff r4](../../validation/mestry-s25-resumed-20261021T154810Z/HANDOFF.md), [tarea SSH previa](../../validation/mestry-horus-s25-task-20261020T235104Z/result.json) | Interrupción verificada en servidor; reapertura con caché objetivo ausente recupera contenido desde servidor; proyecto/fixtures contrastados independientemente. Reintento de publicación devuelve revisión existente sin incremento de journal. Política on-request de r4 fue cambiada después, no sigue vigente por este registro |
| H03 | Cierre 22/10 03:38:10 UTC, Drive/piloto7 | [result.json](../../validation/mestry-s25-drive-ui-20261021T200418Z/result.json), [handoff](../../validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md) | APK r7 instalado con firma/datos; raíz MESTRY autorizada, activa y asignada; refresh nativo; UI y controles verificados. Cero documentos autorizados visibles. Subcarpetas/previews con fixtures. Never/dangerFullAccess comprobado en respuesta real. Antiguo Review/Horus en papelera y escritor sin redirección. Conteos de pruebas históricos: Node55/política3/helpers4/broker46/Picker8/renderer8/parser6, con navegador20 en S23 sobre API fake; no sumarlos como aceptación actual de corpus |
| H04 | 22/10, piloto8, continuación 07:40–07:54 UTC | [handoff](../../validation/mestry-s23-remote-access-20261022T034500Z/HANDOFF.md), [validation-summary](../../validation/mestry-s23-remote-access-20261022T034500Z/continuation-20261022/validation-summary.json), [readiness final](../../validation/mestry-s23-remote-access-20261022T034500Z/continuation-20261022/final-readiness.json), [watchdog](../../validation/mestry-s23-remote-access-20261022T034500Z/continuation-20261022/keepalive-running-verified.json) | APK r8/10008, SSH privado, loopback/hello y cinco session.sync frescos por celular verificados. Regreso a 10,764 s conserva VPN; salida sin tareas observada entre 30,744–31,680 s; Desconectar observado a 0,163 s después de retornar la pulsación. Watchdog saludable y ocho regresiones históricas. NO PASS: tarea activa real, cargador/PC apagado, reposo prolongado, 24 h, caída real UID/bridge y Boot |
| H05 | 20/10, auditoría de sistema y EXP02–EXP05 | [auditoría S23](../../S23_SERVER_AUDIT.md), [inventario](../../validation/mestry-s23-audit-20261020T034416Z/applications_inventory_current.csv), [Debian](../../DEBIAN13_MINIMAL_REPORT.md), [X11](../../TERMUX_X11_REPORT.md), [sandbox](../../CODEX_SANDBOX_REPORT.md) | Android16/ABI/arranque e inventario de su fecha; Termux/Boot; Debian y X11 mínimos aceptados. Sandbox app oficial falla antes del payload en configuración del kernel. No se instaló app gráfica oficial. Ese bloqueo no invalida el posterior piloto Horus aceptado con otro modo de acceso |
| H06 | 21/10, publicación y OAuth de producción | [publicación live](../../validation/mestry-horus-drive-live-20261021T040010Z/result.json), [OAuth producción](../../validation/mestry-oauth-production-confirmed-20261021T055110Z/result.json), [guía/destino](../../HORUS_DRIVE_PUBLISH.md) | Dos revisiones privadas, readback SHA-256, revisión anterior conservada, reintento idempotente y lectura S25 confirmada. Refresh nativo separado de tests fake. Estado remoto actualizado después por H03; no se afirma publicador operativo hoy. Renovación tras más de siete días sigue pendiente; referencia de seguimiento no antes del 29/10 06:08 UTC, todavía futura a esta auditoría |

La observación celular inicial que confundía `NOT_VPN`, el primer ensayo con Wi-Fi reactivada y la primera lectura incompleta del watchdog constan como instrumentación inconclusa en H04. Se conserva su corrección y no se reutilizan esos archivos como evidencia PASS. El resultado global `PASS_WITH_EXPLICIT_PENDING_ITEMS` no significa 24/7.

## Pruebas no ejecutadas y límites de acceso

| Prueba/recurso | Motivo | Estado que debe conservarse |
|---|---|---|
| Lectura actual de sistema/instalación Codex/configuración S23 y documentos desde ese Codex | Cero ADB, SSH/TCP sin acceso. El usuario ya valida Codex, no se reinstala | **BLOQUEADO / SIN ACCESO** actual; **REPORTADO POR USUARIO** y pruebas históricas identificadas |
| Pares FolderSync Android, almacenamiento compartido y permisos persistentes | Sin acceso al dispositivo; no son deducibles de la DB Windows | **BLOQUEADO / SIN ACCESO** |
| Bytes cloud, cuenta/grants actuales, última sincronización global, permisos de raíces | Conector sin resultados/404; no se renovaron tokens ni usó otra cuenta | **BLOQUEADO / SIN ACCESO**; no se afirma borrado o réplica completa |
| Pruebas de escritura, concurrencia, eliminación y recuperación documental en carpeta sincronizada | Tarea limitada a auditoría; requiere autorización específica y área sintética | **PENDIENTE**, procedimiento propuesto en [02](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md) |
| Publicación, OAuth, ampliación del destino/allowlist o creación de fixture Drive | Excluido por alcance y destino histórico en papelera | **PENDIENTE**, no repetir pasos de preparación históricos |
| Nuevos turnos de modelo o APIs pagadas | No autorizados/necesarios para inspección | No ejecutados; ninguna inferencia nueva atribuida a la auditoría |
| Suite Node completa, integración con sockets, helper staging y compilación Android | Falta dependencia ws en copia revisada; listeners/compilación producirían otros efectos/artefactos | No ejecutadas; solo E06 es prueba actual |
| PC apagado, cargador de pared, reposo prolongado, Doze y 24 h | Condiciones físicas no ensayadas; no se fuerza desconexión de servicios | **PENDIENTE** |
| Reinicio/caída de bridge o UID para recuperación | Mutaciones prohibidas durante auditoría y sin autorización específica | **PENDIENTE** |
| Cinco originales arquitectónicos, corpus real, Note20 | Recursos no localizados/accesibles en el alcance | **BLOQUEADO / SIN ACCESO**, sin reconstrucción inventada |
| Vulnerabilidades/últimas versiones y fuentes web de investigación de 19/10 | Auditoría de lo disponible, sin afirmación de novedad ni CVE específica | No evaluadas; las recomendaciones no dependen de actualizar paquetes |

## Control final

Primera comparación posterior a redacción: **2026-10-26 18:11:10 −03:00**. Excluyendo únicamente `docs/auditorias/2026-10-26/`, el árbol original conserva **1.803 archivos, 66.129.015 bytes y el mismo SHA-256 agregado**:

`2890103c7c452459a8177b942eff316c994b858c7749fa9482260fd1b67cbd7b`

Algoritmo reproducible: ordenar rutas relativas de archivos; para cada una concatenar `ruta + NUL + SHA256(bytes).hexdigest() + LF` en UTF-8; calcular SHA-256 de la secuencia. La raíz no tenía symlinks. Esto verifica **nombres y contenido** del árbol original, no procesos, metadatos/permisos o estado cloud. No se registró un manifiesto adicional fuera de los cinco documentos autorizados.

Además se compararon **14 archivos protegidos externos** respecto a la muestra previa a la redacción: configuración/filtros/control rclone, archivos existentes de `.ssh`, script de sincronización y DB/WAL/SHM FolderSync. **Cero diferencias de contenido**. No se publican sus hashes individuales ni contenido de credenciales. La comparación no demuestra inmutabilidad de aplicaciones inaccesibles ni descarta cambios en memoria.

El ADR conserva su SHA-256 indicado en E03. No se invocaron comandos para configurar Codex, sincronizar, instalar/desinstalar, desplegar, abrir callback OAuth, iniciar turnos, publicar, detener servicios o reiniciar dispositivos. Los tests locales temporales fueron los seleccionados en E06.

**Excepción de funcionamiento/procesos: E07, arranque automático de ADB Windows.** No es correcto afirmar que la auditoría no produjo absolutamente ningún cambio de proceso. Sí se puede afirmar que no se cambió configuración o funcionamiento de Codex/sincronizadores mediante acciones de control y no se enviaron comandos a teléfonos. No se garantiza su salud presente por falta de acceso.

Control de cierre de esta sesión: **cinco entregables exactos**, **89 enlaces locales comprobados**, cero archivos destino o anclas faltantes, cero coincidencias de los patrones de secretos/correos en los informes. Revisión de coherencia: 81 pruebas actuales separadas de las históricas; 1/6 fuentes originales disponibles; 12 AC abiertos sin porcentajes; estados actuales inaccesibles separados de PASS históricos; ausencia de Git sin commit inventado; diagramas y tablas distinguen configuración de transferencia actual. Segunda comprobación de los 14 archivos externos a las **18:16:41 −03:00**, sin diferencias. El árbol original y el ADR mantienen los hashes anteriores. La última validación documental repite únicamente integridad/enlaces/patrones; no reejecuta pruebas de comportamiento.
