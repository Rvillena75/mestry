# Galaxy S23 Ultra: auditoría para servidor dedicado MESTRY

Auditoría del **20 de octubre de 2026**, desde Ubuntu/WSL mediante ADB Windows y `ssh mestry-s23`, sin root. **Recomendación: optimización selectiva y recuperación de servicios; no restablecer de fábrica.** El margen actual permite preparar la siguiente prueba de Debian, pero no demuestra que la aplicación gráfica quepa y funcione de forma estable.

**Decisión posterior del usuario:** optimización inicial suficiente; se cierra la limpieza sin deshabilitar más aplicaciones ni restablecer. Las propuestas y estados que siguen describen la auditoría original. La preparación SSH/Boot y la instalación mínima de Debian se autorizaron y completaron después: [informe Debian mínimo](DEBIAN13_MINIMAL_REPORT.md), [INSTALLATION_LOG](INSTALLATION_LOG.md). La prueba tras reinicio sigue pendiente.

La decisión confirmada del usuario es dedicar el S23 exclusivamente a MESTRY. Durante esta auditoría no se desinstalaron/deshabilitaron aplicaciones, cambiaron ajustes, reinició el teléfono ni instaló Debian/X11/la aplicación Linux. **El usuario instaló Termux:Boot**; esa intervención se registra separada de las mediciones iniciales y no se interpreta como autorización para configurar el arranque en aquella fase.

## Evidencia y alcance

Directorio de evidencia: [`mestry-s23-audit-20261020T034416Z`](validation/mestry-s23-audit-20261020T034416Z/). Contiene comandos, tiempos UTC, códigos de salida, salidas minimizadas, CSV y SHA-256. La recolección inicial fue **03:44:17–03:45:38 UTC**; las consultas complementarias y la comprobación de Boot tienen sus propios manifests. Hora de Santiago: UTC−03:00.

- [Inventario actual, 489 paquetes](validation/mestry-s23-audit-20261020T034416Z/applications_inventory_current.csv), con categoría, versión activa, ruta, UID, estado, memoria observada y motivo.
- [Candidatas y riesgos](validation/mestry-s23-audit-20261020T034416Z/removal_candidates_current.csv); [resumen inicial](validation/mestry-s23-audit-20261020T034416Z/summary.json) y [actualización del inventario](validation/mestry-s23-audit-20261020T034416Z/summary_current.json).
- [Tres muestras de memoria](validation/mestry-s23-audit-20261020T034416Z/memory_samples.csv), [procesos por PSS](validation/mestry-s23-audit-20261020T034416Z/processes_pss_first.csv) y [por RSS](validation/mestry-s23-audit-20261020T034416Z/processes_rss_first.csv).
- Manifests [inicial](validation/mestry-s23-audit-20261020T034416Z/manifest.json), [complementario](validation/mestry-s23-audit-20261020T034416Z/followup_manifest.json) y [Boot instalado por el usuario](validation/mestry-s23-audit-20261020T034416Z/boot_update_manifest.json). [Huellas de archivos](validation/mestry-s23-audit-20261020T034416Z/SHA256SUMS).

El inventario APK corresponde al **usuario Android 0**, único usuario enumerado. Además se guardaron [47 entradas APEX](validation/mestry-s23-audit-20261020T034416Z/apex_modules.txt); no se suman a los APK como si fueran aplicaciones de usuario. La metadata también enumera una biblioteca Trichrome adicional, conservada separadamente. No se consultaron cuentas, mensajes, documentos personales, claves SSH ni credenciales Wi-Fi.

**Dos momentos distintos:** antes de Boot había 488 paquetes, 485 de sistema y 3 de usuario, con 465 habilitados y 23 deshabilitados. Después hay **489, 485 y 4**, con **466 habilitados y los mismos 23 deshabilitados**. Las tablas de PSS/RSS, las tres muestras y el intervalo CPU son la línea base anterior a Boot. Sus valores asociados al inventario actual llevan `memory_snapshot=baseline_before_user_installed_boot`; no son una medición de su impacto.

## Estado comprobado

| Campo | Observación y consecuencia |
|---|---|
| Hardware | Samsung **SM-S918B / dm3q**, ABI principal `arm64-v8a`; 8 CPU lógicas enumeradas |
| Android | **16 / API 36**, build `BP4A.251205.006.S918BXXSAFZI1`, parche **2026-09-05**; no se consultó ni aplicó una OTA |
| One UI y región | Propiedad `ro.build.version.oneui=80500`, compatible con numeración **8.5**; `sep=170500`, CSC/sales code **CHO**. Se registra la propiedad; no se inspeccionó la pantalla de versión |
| Arranque | Verified Boot **green**, flash **locked**, vbmeta **locked**; consultas como UID shell 2000 y UID Termux 10348, sin root |
| Termux / SSH | **0.118.3**, origen declarado `F_DROID`, instalador F-Droid; OpenSSH **10.6p1-2**, puerto **8022**; acceso por clave desde WSL operativo |
| Termux:Boot, añadido por el usuario | **0.8.1 / versionCode 1000**, instalador `org.fdroid.fdroid`, mismo UID compartido **10348**. `stopped=false`, `notLaunched=false`, notificaciones concedidas; sin prueba de reinicio |
| Radio | `airplane_mode_on=1`; Wi-Fi operativo por SSH, estado bruto `wifi_on=2`; `bluetooth_on=1`; ambas ranuras SIM informan **ABSENT**. No cambiar el modo avión: ya está activo |
| Energía y pantalla | USB conectado, protección **80 %**, batería **80 %**, `NOT_CHARGING`, `health=GOOD`; pantalla en estado de energía **Dozing**, timeout **30 s**, AOD desactivado |
| Seguridad/compatibilidad | WebView **155.0.8059.43** activo. Chrome estaba deshabilitado y no hay titular del rol BROWSER; SMS usa Google Messages, HOME usa One UI Home |

La coincidencia de UID y el instalador de Boot son evidencia de compatibilidad del conjunto aceptado por Android; **no se obtuvo una huella criptográfica independiente del APK**. El comando opcional `check-signatures` no existe en este firmware y se registra como fallo de instrumentación.

## Memoria, CPU, temperatura y almacenamiento

Tres muestras, aproximadamente separadas por 33 s, bajo la configuración existente y con USB conectado:

| Métrica | Resultado |
|---|---|
| RAM física visible al kernel | **6,9068 GiB**; no incluye reservas ni identifica por sí sola la capacidad comercial |
| `MemAvailable` | **3,2814–3,3143 GiB**, mediana **3,2950 GiB** |
| `MemFree` | **0,3282–0,3586 GiB**; no confundir con disponible |
| Caché de archivos `Cached` | **2,6020–2,6137 GiB**, parcialmente recuperable y con solapamientos contables |
| Slab recuperable / no recuperable | **0,1867–0,1886 / ≈0,3980 GiB** |
| Swap lógico total / usado | **≈12,0000 / 1,2253–1,2297 GiB** |
| RAM física ocupada por zRAM | **≈0,4139 GiB / 423,8 MiB**, incluida en el consumo físico del sistema |
| Presión de memoria PSI, `some avg10` / `full avg10` | **0,00–0,02 % / 0,00 %** durante las muestras |
| CPU en intervalo independiente de 47,95 s | **0,896 % de la capacidad agregada de las 8 CPU**; iowait **0,003 %**, con coste de las sondas incluido |
| Temperatura inicial | Batería **26,2 °C**, AP **26,8 °C**, superficie **28,2 °C**; estado térmico Android **0 / NONE**, sin override |

El consumo de RAM no disponible ronda **3,59–3,63 GiB**, calculado como total menos disponible; no es la suma de RSS de aplicaciones. `dumpsys meminfo` incluye aproximadamente **985,5 MiB de PSS en procesos cached** en la primera captura. Parte de ese conjunto se puede recuperar automáticamente; no es ahorro incremental atribuible a desinstalar aplicaciones. La gestión de caché, PSS y prioridades se describe en [Android: asignación de memoria](https://developer.android.com/topic/performance/memory-management).

La CPU se calculó con deltas de `/proc/stat`: tiempo ocupado excluyendo idle e iowait, dividido por el total agregado, sin duplicar columnas guest. El **16 %** presente en `dumpsys cpuinfo` corresponde a una ventana histórica **00:35–00:40 del teléfono**, anterior a la captura; no se utiliza como basal actual. Los relojes impresos por cada herramienta se conservan, sin confundirlos con los timestamps UTC del host.

**Consumo eléctrico basal: no determinado de forma fiable.** Los atributos `current_now/current_avg` de sysfs están bloqueados. `dumpsys battery` expone un valor OEM de corriente, pero no se verificaron sus unidades/calibración y, con USB y protección de carga, la corriente neta de batería no representa la potencia total del servidor. Un 80 % estable tampoco significa consumo cero. No se publica una cifra en W, mAh/h ni horas de autonomía inventada.

El log OEM contiene un **aviso histórico de deterioro de batería del 07/09**. No demuestra una avería actual ni permite calcular capacidad/ciclos; tampoco `GOOD` certifica la salud física. Conviene revisar el diagnóstico de batería de Samsung antes del piloto prolongado y registrar el resultado, sin inferir porcentajes de degradación del contador propietario.

| Volumen | Estado | Interpretación |
|---|---|---|
| `/data`, Termux y almacenamiento emulado | Total **222,060 GiB**, usados **≈9,50 GiB**, libres **≈212,435 GiB**; `/data` usa **f2fs** | Es el mismo almacenamiento subyacente: no sumar home, PREFIX y `/storage/emulated/0` |
| `/system`/raíz, `/vendor`, `/product`, `/system_ext` | Imágenes **EROFS de solo lectura**, `df` marca **100 %** | Normal para imágenes empaquetadas; no es falta de espacio para Debian |
| `/cache` | Aproximadamente **753 MiB disponibles** | No necesita limpieza para este objetivo |
| `/apex` | Montaje **tmpfs** más módulos montados | No tratarlo como disco libre adicional para el rootfs |
| `/metadata` | Consulta `df` denegada | Tamaño/utilización no determinados; no intentar acceder con privilegios |

[Evidencia de particiones y montajes](validation/mestry-s23-audit-20261020T034416Z/storage.txt). Las particiones `dm-*` y sus dispositivos físicos son vistas relacionadas, no capacidades sumables. Debian deberá residir en el almacenamiento privado de Termux, sin reparticionar ni usar almacenamiento compartido como rootfs.

## RAM Plus y política Android observada

`ram_expand_size=8192`, opciones `2,4,6,8`, `zram_enabled=1`: **RAM Plus está configurado en el valor equivalente a 8 GB**. `zram0/disksize=12884901888` muestra **12 GiB de capacidad lógica**, algoritmo activo **lzo-rle**, con **`backing_dev=/dev/block/loop52`**. El respaldo tiene contadores de I/O acumulados distintos de cero. Su archivo/tamaño no son legibles como shell; no se afirma un tamaño de swap sobre UFS ni que todo el swap usado esté en almacenamiento físico.

Los primeros campos estándar de `mm_stat` muestran aproximadamente **1,23 GiB sin comprimir**, **329,4 MiB comprimidos** y **423,8 MiB asignados físicamente**, incluyendo overhead. No son tres consumos para sumar. El `bd_stat` Samsung tiene campos adicionales: no se interpreta íntegramente con el esquema upstream. [Documentación del kernel sobre zRAM](https://docs.kernel.org/admin-guide/blockdev/zram.html).

**Recomendación: conservar RAM Plus en 8 durante la preparación y el primer arranque mínimo.** No existe aquí una comparación que justifique apagarlo. Más adelante comparar **8 frente a 4** mediante la interfaz Samsung, con reinicio autorizado y la misma carga: latencia, PSI, fallos de procesos e I/O, no solo `MemFree`. La relación 8 configurados/12 lógicos es observada; no se presupone una fórmula válida para otros ajustes. Samsung documenta la selección y el reinicio, con disponibilidad dependiente del firmware: [RAM Plus](https://www.samsung.com/ae/support/mobile-devices/how-to-use-ram-plus-feature-on-my-samsung-mobile/).

La configuración efectiva muestra **`max_phantom_processes=32`**, freezer activo y **18 procesos congelados** en la consulta. LMKD registra **3 terminaciones históricas de procesos cached**; no hay registros de salida de Termux en la consulta disponible y no se atribuyen esas terminaciones a MESTRY. La ausencia de una propiedad `ro.lmk.*` no significa que el mecanismo esté desactivado: el dump efectivo sí lo muestra. Conservar LMKD, freezer y sus políticas; su función es mantener la estabilidad bajo presión. [AOSP: LMKD](https://source.android.com/docs/core/perf/lmkd).

El límite de procesos secundarios afecta al conjunto del dispositivo. Termux advierte sobre terminaciones de procesos en Android 12+; una pila gráfica con muchos hijos deberá probarse con concurrencia pequeña. No se recomienda desactivar el monitor de procesos, elevar sus límites, cambiar `swappiness`, usar `swapoff`, borrar cachés del kernel ni ajustar OOM. [Termux, limitaciones y procedencia de plugins](https://github.com/termux/termux-app).

## Procesos y servicios

Primer snapshot, MiB. PSS reparte páginas compartidas; RSS es la memoria residente vista por cada proceso y no debe sumarse para estimar ahorro.

| Proceso | PSS MiB | Lectura para MESTRY |
|---|---:|---|
| `system` | 426,2 | Núcleo de servicios Android; conservar |
| `com.android.systemui` | 373,0 | Interfaz y gestión del sistema; conservar |
| `com.google.android.gms` | 190,6 | Identidad y servicios Google; conservar; proceso `:unstable` aparte **59,4** |
| `surfaceflinger` | 165,0 | Compositor gráfico; conservar |
| `com.android.settings.intelligence` | 151,5 | Componente de Ajustes; no es una candidata por consumir RAM |
| One UI Home | 142,8 | Launcher operativo para mantenimiento y futuro agente |
| Ajustes | 123,0 | En caché, recuperable por Android |
| Proveedor de cámara Samsung | 117,7 | Servicio de hardware; conservar |
| Teclado Samsung | 113,0 | Entrada de texto y recuperación local; conservar |
| Device Care | 87,3 | En caché; conservar controles de batería, memoria y protección |
| Google Messages | 80,1 + 35,6 RCS | Titular de SMS; evaluar su función por separado, preservar autenticación/compatibilidad |
| Smart Suggestions | 77,0 + 58,7 búsqueda | **135,7** combinados; dependencia OEM incierta, fuera del primer lote |
| Termux | **67,1** | RSS **201,2 MiB**; no confundir su UI con toda la futura carga Linux |
| Routines / Rubin | 53,4 / 53,3 | Funciones OEM con UIDs compartidos; no retirar por inferencia |

`sshd` tenía **≈4,2 MiB RSS**, PID **18143**, PPID 1 y unos 50 minutos de vida en el cierre previo a Boot. Sus procesos de conexión y shells son adicionales. PPID 1 indica daemonización; **no prueba supervisión ni recuperación**.

Se conservaron **416 entradas de servicios Binder registrados**, **126 componentes `ServiceRecord` únicos** y **15 procesos marcados `*PERS*`**. Son conceptos distintos: no equivalen a 557 tareas consumiendo CPU. Los persistentes incluyen SystemUI, sistema, Phone/IMS, NetworkStack, NFC/SE, servicios Qualcomm y `sdhms`/diagnóstico Samsung. Se enumeran en [summary.json](validation/mestry-s23-audit-20261020T034416Z/summary.json); no constituyen candidatas automáticas. Un `ServiceRecord` puede estar ligado, iniciado o pendiente de recuperación; la salida minimizada conserva esos campos.

## Clasificación de aplicaciones y limpieza propuesta

La clasificación cubre los **489 APK enumerados después de instalar Boot**. Es una política operativa conservadora para este firmware, no una prueba exhaustiva de dependencias ni una lista para otros Galaxy.

| Clase | Cantidad | Criterio |
|---|---:|---|
| Esenciales para Android | **230** | Base, red, hardware, proveedores, recursos/overlays, autenticación de plataforma, actualizaciones y protecciones; incluye conservación preventiva de componentes privilegiados |
| Necesarias para MESTRY | **3** | Termux, Termux:Boot y F-Droid como canal actual de mantenimiento; F-Droid no es requisito del runtime SSH |
| Compatibilidad futura | **99** | Drive, navegador, credenciales, accesibilidad, captura, archivos, periféricos y conexiones S25; algunas estaban deshabilitadas y no se habilitan automáticamente |
| Prescindibles | **26** | Funciones de consumo candidatas condicionales: **18 habilitadas y 8 ya deshabilitadas** |
| Inciertas | **131** | Autoridad, dependencias OEM o uso no demostrados; conservar |

Primer lote recomendado **solo después de aprobación**, mediante deshabilitación reversible por paquete:

| Paquete verificado | Función identificada por paquete/ruta | Estado y beneficio esperado | Riesgo concreto |
|---|---|---|---|
| `com.facebook.appmanager` | `FBAppManager_NS` | Habilitado; no observado en PSS; reducir integración Meta | Perder gestión de apps Meta si se añaden después |
| `com.facebook.services` | `FBServices` | Habilitado; no observado en PSS | Integraciones Meta |
| `com.facebook.system` | `FBInstaller_NS` | Habilitado; no observado en PSS | Instalación/integración Meta |
| `com.sec.android.daemonapp` | Samsung Weather | Habilitado; no observado en PSS | Tiempo/widgets meteorológicos |
| `com.samsung.android.kidsinstaller` | `KidsHome_Installer` | Habilitado; no observado en PSS | Instalador de modo infantil |
| `com.samsung.android.app.watchmanagerstub` | `GearManagerStub` | Habilitado; no observado en PSS | Configuración de Galaxy Watch |
| `com.samsung.accessory.budsunitemgr` | `BudsUniteManager`, versión activa **9.0.10.1724** | Habilitado; **18,0 MiB PSS**, en caché/congelado | Integración específica de Galaxy Buds |

En la muestra ninguno de esos siete tenía proceso persistente ni `ServiceRecord`. No se detectó UID compartido en su metadata. Esto permite proponerlos con riesgo relativo bajo; **no certifica ausencia de toda dependencia Binder/privada OEM**. La tabla no promete 18 MiB de ganancia neta: esa memoria ya era candidata a recuperación por Android. No se dispone de un ahorro energético medido.

Lotes posteriores podrían revisar **Game Tools**, AR Emoji, paneles Edge opcionales, Reminder, Picture Frame, PhotoTable y Dynamic Lock, uno por vez y según las funciones del futuro agente. **Game Optimizing Service (`com.samsung.android.game.gos`) se conserva** por su relación con políticas de rendimiento; no se confunde con Game Tools. Sticker Center y Video quedan inciertos por UID compartido. Smart Suggestions, Rubin y Routines también quedan fuera: el mayor PSS aparente no basta para declarar segura su retirada.

Gmail, YouTube, Maps, Meet, OneDrive, My Galaxy, Gaming Hub y Video Editor ya estaban deshabilitados. También había otros componentes deshabilitados —incluidos Chrome, Bixby y Samsung Messages— cuya seguridad no se da por validada retrospectivamente. Consultar [los 23 originales](validation/mestry-s23-audit-20261020T034416Z/packages_disabled.txt). Mantener su estado mientras se prepara una decisión específica; repetir una deshabilitación no genera ahorro adicional.

Conservar explícitamente:

- Android/SystemUI/Ajustes/launcher/teclado, PermissionController, Package Installer, KeyChain/CredentialManager y proveedores de archivos/descargas/medios.
- NetworkStack, CaptivePortalLogin, Wi-Fi, VPN, certificados y recursos Samsung/Qualcomm. No retirar paquetes Phone/IMS/RIL por tener modo avión o no usar SIM.
- Play services/GSF/Play Store, WebView y un navegador de autenticación cuando se habilite; Samsung Pass y su Autofill **actualmente seleccionado**, biometría y `authfw`.
- `com.wssyncmldm`, `com.sec.android.soagent`, Galaxy Store/Update Center, Device Care, `sdhms`, Knox y protecciones OEM.
- Accessibility, captura y servicios de archivos para el futuro Device Agent. Mantenerlos no habilita permisos: Accessibility está desactivada y no se concedió control a ninguna app.
- Drive y componentes de conectividad S25 —MCF, Multi Control, Link to Windows, Smart View— hasta validar el transporte definitivo. No son todos esenciales al servidor, pero retirarlos ahora puede cerrar una ruta aún en evaluación.

Deshabilitar un APK de `/system` no libera su espacio en la imagen de solo lectura. Desinstalar para el usuario tampoco aumenta RAM física y puede eliminar datos. Con **212 GiB libres** no hay una razón de capacidad que justifique priorizar borrados.

## Pantalla apagada, batería y recuperación

Termux mantiene un **servicio en primer plano**, notificaciones concedidas y bucket **10 / ACTIVE**. Tiene permiso para solicitar exclusión de optimización y wakelocks, pero **no figura en la whitelist efectiva de Doze**; tampoco Boot en la consulta posterior. Tener concedido `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` no equivale a estar excluido. No se observó un wakelock parcial propio de Termux en las capturas.

La pantalla permaneció en estado de energía **Dozing**, y SSH respondió cuando `mLastSleepTime` llevaba aproximadamente **10 minutos**, con el mismo proceso `sshd`. Sin embargo, `mDeviceIdleMode=false`, USB conectado y sondas periódicas impiden considerar esto una prueba de Doze profundo o de autonomía sin PC/alimentación. Android difiere CPU/red y trabajos durante Doze; la exclusión es parcial, no inmunidad a terminaciones. [Android: Doze y App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby).

Las listas Samsung de suspensión y suspensión profunda son otra política; su pertenencia completa no se obtuvo por una API shell fiable. Revisar por interfaz Termux, Boot y, posteriormente, X11/VPN/Device Agent: **batería Sin restricciones**, exclusión de suspensión profunda y **Nunca en suspensión**, si la UI ofrece esa combinación. Registrar estados previos y confirmar luego la whitelist; no asumir que cambiar una pantalla configura todas las capas. Mantener la gestión global. [Samsung: administración de aplicaciones](https://developer.samsung.com/mobile/app-management.html).

Recuperación observada y propuesta:

| Capa | Estado actual | Recomendación pendiente |
|---|---|---|
| Proceso SSH | Daemon activo, sin `runsv`/`runsvdir` observado | Supervisor `termux-services`/runit, con reintentos espaciados y logs acotados |
| Paquete supervisor | `termux-services` figura **`un`**, no instalado; existen directorios de servicio de OpenSSH con archivo `down` | No confundir esos archivos con supervisión activa; instalar/configurar en una fase aprobada |
| Reinicio Android | Boot **ya instalado e iniciado según PackageManager**, pero **`~/.termux/boot` no existe** | Preparar script idempotente que arranque un único supervisor; no dos instancias de `sshd` |
| CPU despierta | Sin wakelock parcial Termux observado | Evaluar `termux-wake-lock` durante el servicio y su coste; liberarlo al detener el host |
| Muerte de Termux | No ensayada; un supervisor dentro del mismo UID no la resuelve por sí solo | Detectar caída, probar recuperación Android y documentar intervención manual si persiste |
| Primer desbloqueo | No ensayado tras reinicio | Diseñar considerando almacenamiento cifrado y primer desbloqueo físico; Boot no demuestra servicio antes del PIN |
| Trabajo Android futuro | Agente aún no instalado | Persistencia de colas y recuperación por APIs Android adecuadas, con tareas idempotentes |

[Termux:Boot](https://github.com/termux/termux-boot) documenta abrir la app una vez y colocar scripts; la instalación del usuario satisface solo parte del procedimiento. [Termux Services](https://github.com/termux/termux-services) documenta runit y el significado de `down`. Mantener plugins del origen compatible con Termux; no mezclar APK de otra firma.

`tmux` ayudaría a conservar una sesión ante desconexiones, pero no sustituye supervisor, Boot ni recuperación del UID. WorkManager sirve para trabajo persistente recuperable; **no es un daemon de SSH**. En Android 16 las cuotas de trabajos también alcanzan trabajos concurrentes con servicios en primer plano: [cambios de Android 16](https://developer.android.com/about/versions/16/behavior-changes-all). El primer desbloqueo y el almacenamiento de credenciales requieren diseño específico: [Direct Boot](https://developer.android.com/privacy-and-security/direct-boot). No se propone eliminar PIN, cifrado o protecciones para evitarlo.

## Configuraciones recomendadas antes de Debian

Orden propuesto; **todos los cambios del teléfono siguen pendientes de aprobación**:

1. **Preparar continuidad.** Revisar excepciones por aplicación de Termux/Boot, preparar supervisor y script Boot, y probar pantalla apagada/recuperación. Boot no necesita reinstalarse. Mantener notificación del servicio y evitar limpieza manual de Termux desde Device Care.
2. **Conservar protección al 80 %, timeout 30 s, AOD apagado, modo avión y RAM Plus actual.** Ya están configurados. Mantener bajo consumo desactivado durante el servicio; no activar rendimiento máximo global por defecto. Ventilación y carga cableada estable; comprobar temperatura bajo carga real.
3. **Revisar Bluetooth**, actualmente activado, para apagarlo solo si no se necesitan periféricos. No retirar su paquete. Las SIM ya están ausentes; no hace falta otra intervención de telefonía. NFC y otras radios no medidas no reciben una recomendación automática.
4. **Resolver mantenimiento y autenticación.** Verificar una vía de navegador actualizada: Chrome está deshabilitado y el rol BROWSER vacío. Si se elige Chrome, habilitarlo/actualizarlo requiere aprobación. Mantener WebView, Play services y Samsung Pass; verificar OTA y actualizaciones en ventana de mantenimiento, sin desactivar el sistema de actualizaciones.
5. **Si se desea limpiar ahora**, aprobar el lote de siete paquetes y deshabilitarlos uno por vez. Es opcional, con beneficio de mantenimiento probable y ahorro de recursos aún no medido. No bloquear la prueba de Debian esperando una limpieza masiva.
6. **Debian mínimo primero, gráficos después.** Un rootfs, un host activo, concurrencia pequeña y sin LLM residente ni escritorio completo de inicio. Medir de nuevo antes de añadir X11/app oficial; conservar las puertas de compatibilidad y aislamiento de [V01](VALIDATION_PLAN.md). Esta auditoría no las sustituye ni autoriza instalar.

No se confirmó por shell la configuración de reinicios automáticos de One UI. Revisarla en interfaz: acordar ventana y recuperación tras primer desbloqueo antes de depender de reinicios programados. No apagar globalmente autooptimización/seguridad por suponer que causan un problema aún no observado. Mantener la reserva DHCP/red privada y los controles SSH descritos en [INSTALLATION_LOG](INSTALLATION_LOG.md); no abrir SSH a Internet.

## Procedimientos reversibles propuestos

**No ejecutados.** Antes de cada cambio: guardar estado exacto de ese paquete/ajuste, versión, UID y medio de recuperación; conservar acceso ADB USB. Para Termux, preparar backup privado con verificación de restauración; no guardar claves ni backups sin cifrar en esta documentación.

Ejemplo limitado a un paquete del lote, con el `transport_id` verificado en ese momento:

```bash
# SOLO DESPUÉS DE APROBACIÓN. Sustituir TRANSPORT_ID por el del S23 actual.
adb.exe -t TRANSPORT_ID shell pm disable-user --user 0 com.facebook.appmanager

# Reversión del estado original observado (enabled=0 / default):
adb.exe -t TRANSPORT_ID shell pm default-state --user 0 com.facebook.appmanager
```

`pm enable` deja estado explícito 1; para los siete candidatos, volver a **default-state** restaura el 0 original. Si otro paquete tenía estado 1, 2, 3 o componentes alterados, restaurar su estado propio. El procedimiento no se aplica a los 23 que ya estaban deshabilitados. No generar un script de deshabilitación masiva.

Para batería/suspensión/Bluetooth, volver al valor previo registrado en UI; para RAM Plus, seleccionar de nuevo **8** y reiniciar solo en ventana autorizada. Para supervisor/Boot, conservar copia de configuraciones y revertir únicamente lo añadido; comprobar que queda un `sshd` disponible antes de cerrar el acceso de mantenimiento. Detener el supervisor antes de pasar a una instancia manual para evitar conflictos de puerto.

No se recomienda desinstalar en esta primera fase. `install-existing` solo sirve si el paquete sigue disponible para Android: no recupera datos borrados ni cualquier APK de usuario. Un reset no es una reversión de limpieza selectiva; requiere restauración de datos y configuración.

## Restablecimiento frente a optimización selectiva

| Criterio | Optimización selectiva | Restablecimiento |
|---|---|---|
| Problema observado que resuelve | Excepciones de servicio, arranque y funciones concretas sobrantes | No se observó una corrupción que lo exija |
| Android/OEM preinstalado | Conserva base y estados conocidos | No sustituye firmware por Android mínimo; la base OEM permanece y pueden volver estados predeterminados |
| Memoria/CPU esperadas | Ganancia por medir; objetivo principal es continuidad | No hay evidencia para prometer más RAM o CPU que con limpieza selectiva |
| Datos y cuentas | Cambios acotados, sin borrado inicial | Borra datos/configuración; permite separación de un perfil personal previo si esa fuera una necesidad confirmada |
| Acceso preparado | Conserva Termux, SSH Ed25519, ADB y Boot | Requiere reconstruir red/depuración, Termux/Boot, SSH/host keys, autorizaciones y ajustes |
| Mantenimiento y reversión | Paquete a paquete, trazable | Respaldo/restauración y posible verificación de cuentas; más intervención física |

Solo había tres apps de usuario y unos 9,5 GiB usados antes de Boot: **no hay una acumulación de apps demostrada que justifique reiniciar desde cero**. No se inspeccionaron cuentas ni contenido personal, por lo que tampoco se declara que esté libre de datos personales. Un reset podría justificarse después por separación de identidades, corrupción persistente o una reconstrucción deliberada; ninguna es una ventaja de rendimiento demostrada aquí. [Samsung: alcance y requisitos del restablecimiento](https://www.samsung.com/us/support/answer/ANS10002030/).

## Plan de pruebas antes y después

No ejecutar cambios ni estos ensayos que alteren estado sin aprobar su fase. Mantener firmware, RAM Plus, alimentación, radio, pantalla, espera inicial y carga iguales para comparar. Cambiar **una variable**; usar tres repeticiones para comparaciones de recursos y conservar fallos.

| Prueba | Línea base / ejecución propuesta | Criterio propuesto y límites |
|---|---|---|
| O00 Inventario y reposo | **Ejecutada:** tres muestras de RAM y un intervalo CPU; extensión por instalación de Boot separada | Inventario reconciliado, estados y condiciones explícitos. No acredita energía ni disponibilidad prolongada |
| O01 Lote selectivo | Antes/después por paquete, espera 15 min, tres ventanas de muestreo; comprobar Wi-Fi, SSH, UI/teclado, navegador, archivos y ajustes de actualización | Sin regresiones ni nuevos reinicios de procesos críticos; beneficio superior a variación basal antes de atribuir ahorro |
| O02 Pantalla apagada | 1 h USB y después una noche sin USB, con alimentación de batería acordada; dejar intervalos sin SSH/keepalives ni ADB | Conexiones nuevas exitosas tras el reposo; registrar Doze efectivo. La sesión actual solo demuestra respuestas en reposo alimentado |
| O03 Energía y térmica | Medidor USB de energía tras estabilización; ensayo separado de descarga durante 3–6 h, lectura fiable de carga/temperatura | Reportar W medios o mAh/h solo con unidades y condiciones verificadas; no usar corriente neta de batería como consumo USB |
| O04 Recuperación de daemon | En ventana con ADB de respaldo, salida controlada de `sshd`; después comprobar supervisor y reconexión | Recuperación propuesta ≤60 s, sin duplicados, sin bucle de reinicios ni pérdida de logs. **No ejecutada** |
| O05 Reinicio/primer desbloqueo | Reinicio autorizado con acceso físico, apertura/desbloqueo y arranque por Boot; repetir desconexión de red | SSH vuelve sin comandos desde PC después del desbloqueo; disponibilidad antes del PIN se registra separadamente. **No ejecutada** |
| O06 Debian y aplicación | Repetir O00 con Debian mínimo; luego gráfico/app, repositorios sintéticos y concurrencia pequeña | Mantener el margen propuesto en V10: ≥25 % de RAM visible disponible (**≈1,73 GiB**), sin presión sostenida/terminaciones, con límites revisados antes de repetir si falla |
| O07 Piloto prolongado | Escalar a V04 de 72 h y V10; actualizaciones en mantenimiento | Recuperación, temperatura y experiencia S25 aceptables; Device Agent/UI se valida aparte de la disponibilidad SSH |

Las duraciones y umbrales futuros son propuestas, no resultados. Una liberación transitoria de caché no es mejora sostenida; un servicio que vuelve solo porque el PC lo relanza tampoco demuestra autonomía del S23.

## Reproducción y límites de instrumentación

[Recolector de lectura](../tools/audit_s23_readonly.py) y [análisis offline](../tools/summarize_s23_audit.py). Revisar el código antes de repetir; usa únicamente consultas remotas y crea archivos en WSL. No usa `--checkin`, `battery reset/unplug`, `force-idle`, `force-stop`, cambios de configuración ni root.

```bash
# Desde la raíz MESTRY, una nueva captura con los estados entonces vigentes:
python3 tools/audit_s23_readonly.py --sample-count 3 --sample-interval 30
# Sustituir RUTA_EVIDENCIA por el directorio que imprime el recolector:
python3 tools/summarize_s23_audit.py RUTA_EVIDENCIA

# Recalcular los dos momentos conservados de ESTA auditoría, sin tocar Android:
python3 tools/summarize_s23_audit.py docs/validation/mestry-s23-audit-20261020T034416Z
python3 tools/summarize_s23_audit.py docs/validation/mestry-s23-audit-20261020T034416Z --current
```

Las sondas suplementarias también están reproducibles por los comandos de sus manifests. El recolector actual incorpora las principales consultas complementarias y usa metadata activa; `collector_initial.py` se conserva solo como revisión histórica. En la primera extracción de metadata, la sección de APK ocultos de ROM sobrescribía versiones actualizadas. Se corrigió, se repitió la consulta y **las 488/489 versiones activas se cruzaron con `pm list`**. `package_metadata.txt` se conserva marcado como sustituido por `package_metadata_current.txt`; después de Boot se usa `boot_package_metadata.txt`.

Se conservaron denegaciones de `/proc/swaps`, atributos de batería, `swappiness`, `zram/mem_limit`, archivo/tamaño del backing y `/metadata`. Algunas consultas compuestas terminan en 0 aunque un subcomando falle: los stderr forman parte de la evidencia y no se cuentan como éxito total. `dpkg-query` sin estado podía listar nombres no instalados; se comprobó con `${db:Status-Abbrev}` y solo `ii` significa instalado. No se interpretan valores ausentes como cero.

**Resultado para la siguiente decisión:** preparar las excepciones específicas y la recuperación de Termux/Boot, conservar RAM Plus y protecciones, considerar el lote pequeño de siete paquetes y avanzar después a Debian mínimo. **No restablecer de fábrica ni hacer una limpieza amplia antes de disponer de una comparación útil.**
