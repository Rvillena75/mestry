# Registro de instalación experimental

Este registro recoge ejecución real y complementa la investigación R2. Una comprobación de conectividad no valida Codex, PRoot ni sus mecanismos de aislamiento.

## Alcance autorizado el 19 de octubre de 2026

El usuario autorizó administrar desde Ubuntu/WSL2 los diagnósticos y las instalaciones reversibles necesarias para probar el S23, avanzar por fases y pedir autorización antes de operaciones sensibles. Indicó expresamente: **«Comienza solamente comprobando ADB y la conectividad con el S23»**. Esta primera sesión se limita a esa fase y a consultar la presencia de Termux. Las restricciones históricas de investigación de R2 no anulan esta autorización posterior.

Se mantienen las restricciones del usuario: sin root, cambios de particiones, instalación de Windows ni desactivación de mecanismos de seguridad. La autorización experimental no aprueba toda la arquitectura, acceso a cuentas, envío de datos personales ni consumo de inferencia. No se requiere repetir la autorización de diagnósticos e instalaciones reversibles ya incluidos en el encargo.

## Sesión `mestry-adb-wsl-20261020T024456Z`

**Resultado: conexión ADB USB validada; fase inicial terminada. V00 parcial.** V01–V13 no ejecutados. SSH todavía no configurado ni probado.

- Inicio observado: **2026-10-19 23:44:56 −03:00**, equivalente a **2026-10-20 02:44:56 UTC**.
- Fin de las consultas: **2026-10-19 23:46:41 −03:00**, equivalente a **2026-10-20 02:46:41 UTC**.
- Estación: `/home/developer/proyectos/mestry`, Ubuntu en WSL2 sobre el Windows del usuario.
- Protocolo: precomprobación de transporte y subconjunto de V00 de [VALIDATION_PLAN](VALIDATION_PLAN.md), revisión R2, bajo la autorización experimental posterior.
- Evidencia estructurada y minimizada: [JSON de la sesión](validation/mestry-adb-wsl-20261020T024456Z.json). Serial del teléfono omitido. Sin credenciales, pairing, SSID, MAC, IMEI ni número telefónico.
- SHA-256 del JSON: `901860c5896c9014ced41738b766b56e3da4bcb4d6d07d04a1d3bc8d790e1a27`.
- Cuenta de prueba y fixture: no utilizados; no se hizo login ni inferencia. RAM, disco, firmware completo, One UI y estados de arranque siguen pendientes.

### Hechos observados

| Comprobación y fuente | Resultado observado | Alcance |
|---|---|---|
| `/etc/os-release`, `uname -a` | Ubuntu **24.04.4 LTS**, x86_64, kernel `6.18.33.1-microsoft-standard-WSL2` | Entorno anfitrión; no describe el kernel del S23 |
| `wsl.exe --version` | WSL **2.7.8.0**; kernel **6.18.33.1-1**; WSLg **1.0.73.2**; Windows **10.0.26300.9711** según la salida | Windows 11 es la identificación declarada por el usuario; se conserva la numeración exacta que imprimió WSL |
| `wsl.exe --list --verbose` | `Ubuntu-24.04`, `Running`, versión **2** | WSL2 confirmado; interop de ejecutables Windows funcional |
| `wslinfo --networking-mode` | **`nat`** | Un futuro listener en Windows requerirá comprobar cómo alcanzarlo desde WSL |
| `command -v adb.exe` | ADB existente en el SDK de Android de Windows: `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe` | No se descargó ni instaló ADB |
| `adb.exe version` | Android Debug Bridge **1.0.41**, platform-tools **37.0.0-14910828**; se ejecuta en Windows | Cliente Windows invocado directamente desde WSL |
| `adb.exe devices -l` | **Un dispositivo**, estado **`device`**, `model:SM_S918B`, `product:dm3qxxx`, `device:dm3q`, `transport_id:1` | Autorizado y alcanzable por USB en esta sesión |
| `adb.exe -t 1 shell id` | `uid=2000(shell)`, contexto SELinux `u:r:shell:s0` | Shell ADB ordinaria; sin solicitar root |
| `shell getprop ro.product.model` y `ro.product.device` | **SM-S918B**, **dm3q** | Identificación del S23 Ultra conectado |
| `shell getprop ro.build.version.release` y `ro.build.version.sdk` | **Android 16**, **API 36** | Versión informada por el dispositivo |
| `shell getprop ro.product.cpu.abi` | **`arm64-v8a`** | ABI principal Android; no certifica el funcionamiento de un paquete Linux |
| `shell cmd package list packages --show-versioncode com.termux` | **`package:com.termux versionCode:1002`** | Termux instalado; versión comercial, origen y firma pendientes. No apareció `com.termux.x11` en esta consulta |
| `shell pm path com.termux` | Devuelve una ruta al `base.apk` de Termux | Confirma APK instalado; ruta aleatoria omitida del registro |
| Herramientas en PATH de WSL | `ssh`, `ssh-keygen`, `python3`, `timeout`, `wslpath`, `wsl.exe`, `powershell.exe`, `cmd.exe`, `pwsh.exe`, `adb.exe` | Disponibilidad de ruta; no implica que todas se hayan ejecutado |
| `ssh -V` | **OpenSSH_9.6p1 Ubuntu-3ubuntu13.20**, OpenSSL **3.0.13** | Cliente SSH disponible para la fase posterior |
| `command -v adb`, `usbipd.exe`, `lsusb` | Sin resultado en PATH | No demuestra ausencia de instalaciones fuera del PATH; no son necesarios para el transporte verificado |
| `git status --short --branch` | La carpeta no es un repositorio Git | No se creó repositorio, commit ni push |

Todos los comandos ADB de la tabla terminaron con código **0** y sin stderr. La salida de dispositivos, con el identificador minimizado, fue:

```text
List of devices attached
[device-id-redacted] device product:dm3qxxx model:SM_S918B device:dm3q transport_id:1
```

### Interpretación y decisiones de esta fase

La combinación de enumeración USB, estado `device` y respuestas de shell demuestra que **el ADB de Windows sirve para administrar el S23 desde esta sesión WSL**. No hace falta transferir USB a Linux: **no instalar ni configurar `usbipd-win` para esta ruta**. No se observó un fallo que justifique instalar ADB Linux o cambiar drivers.

El cliente `adb.exe` se ejecuta en Windows y usa su servidor ADB. Este éxito **no demuestra** que un puerto TCP vinculado a `127.0.0.1` de Windows sea alcanzable como `127.0.0.1` desde WSL. No se crearon forwards ni se probaron puertos SSH. Antes de usar un túnel USB futuro, comprobar sus bindings y el acceso WSL↔Windows; no publicar el listener ni cambiar firewall para eludir un fallo de localhost.

No fue necesaria ninguna interacción manual con el teléfono. No se instalaron paquetes, abrieron aplicaciones, habilitaron permisos nuevos, generaron claves, configuraron SSH ni cambiaron ajustes del dispositivo. Tampoco se descargó Debian o la app oficial.

### Próxima fase delimitada

Comprobar primero la versión, procedencia y estado de Termux, y después preparar SSH con clave desde WSL, preferentemente por Wi-Fi local. Si el bootstrap necesita ejecutar un comando dentro de Termux, dar instrucciones precisas y esperar al usuario; no habilitar silenciosamente permisos entre apps. Antes de cualquier instalación, preservar los datos Termux existentes. Debian 13/PRoot/X11 y el paquete oficial siguen sujetos a las puertas de V01, incluyendo integridad y protección efectiva antes del login.

Para repetir solo la comprobación inicial desde WSL:

```bash
command -v adb.exe
adb.exe version
adb.exe devices -l
# Usar el transport_id del S23 observado en la consulta anterior.
# El valor 1 corresponde solo a la sesión registrada:
adb.exe -t 1 shell getprop ro.product.model
adb.exe -t 1 shell id
adb.exe -t 1 shell cmd package list packages --show-versioncode com.termux
```

`transport_id` puede cambiar al reconectar. Seleccionar el S23 por su modelo antes de consultar la shell. Omitir el serial de cualquier evidencia que se comparta. No hay cambios del teléfono que revertir en esta fase.

Verificación de la entrega: JSON válido, diez consultas ADB registradas y 29 enlaces locales de los documentos modificados con destino existente. Se comprobó que el documento previo de arquitectura conserva el SHA-256 `02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031` registrado en R2. Estas comprobaciones documentales no amplían el resultado de conectividad.

## Sesión `mestry-ssh-preflight-20261020T031017Z`

**Resultado: acceso por clave y alias `mestry-s23` verificados, 3/3 pruebas funcionales correctas; diagnóstico previo terminado. No se instaló Debian, PRoot ni software gráfico. V00 continúa parcial; V01–V13 no ejecutados.**

El encargo del **2026-10-20** autoriza configurar SSH y consultar los recursos previos a Debian. El límite vigente es explícito: **«Todavía no instales Debian ni la aplicación gráfica»**. Esta sesión sustituye el estado SSH pendiente de la sesión anterior; no amplía la autorización a instalaciones.

- Inicio: **2026-10-20 00:10:17 −03:00 / 03:10:17 UTC**.
- Pruebas de acceso: **03:13:32–03:13:34 UTC**; consultas remotas y simulación hasta **03:18:34 UTC**.
- Evidencia minimizada cerrada a **03:19:44 UTC**: [JSON de SSH y diagnóstico](validation/mestry-ssh-preflight-20261020T031017Z.json).
- SHA-256 del JSON: `b0ec0adfd8fdc0246a30e8f5519f756739b62b3502521f42dff4571a2f89162c`.
- Administración desde WSL con OpenSSH nativo. ADB Windows se usó únicamente para consultar batería y presencia de paquetes, por restricciones del UID Termux; **sin PowerShell**, root, cambios de particiones ni ajustes de seguridad.

### Clave exclusiva, alias y autenticación

Se crearon fuera del proyecto `~/.ssh/id_ed25519_mestry_s23` y su archivo público `.pub`, sin sobrescribir `id_ed25519` ni ninguna clave anterior. Directorio `~/.ssh`: **700**; clave privada y `~/.ssh/config`: **600**; clave pública: **644**. La configuración real y todas las claves permanecen en el home de WSL, fuera del workspace; no se copiaron al registro ni a Git.

La clave se generó **sin passphrase** para el acceso automatizado solicitado; no se usa ni necesita `ssh-agent` en esta configuración. No se almacenó una contraseña o passphrase. La huella de la clave pública exclusiva es `SHA256:CONFIGURE_LOCAL_FINGERPRINT`.

El alias local **`mestry-s23`** apunta al destino LAN facilitado por el usuario, puerto **8022**, usuario **`u0_a348`**, y selecciona exclusivamente la identidad MESTRY mediante `IdentitiesOnly yes`. Conserva verificación estricta de host; el servidor coincide con la entrada que ya existía en `known_hosts`. Se deshabilita el reenvío del agente y de X11 en este cliente; se configuraron keepalives de 30 s y tres faltas antes de cerrar una conexión caída. No se exporta aquí una copia del archivo de configuración local.

La prueba inicial con la identidad anterior y la prueba de la clave nueva antes de instalarla terminaron con **255 / Permission denied** en modo no interactivo: el servidor respondía, pero esas identidades no permitían entrar sin contraseña. Se solicitó una única intervención en una terminal WSL:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_mestry_s23.pub mestry-s23
```

El usuario completó el paso y respondió **«listo»**. La contraseña se introdujo exclusivamente en su terminal; el agente no la recibió. Después se verificaron:

| Prueba real desde WSL | Resultado | Evidencia y límite |
|---|---|---|
| Autenticación con clave exclusiva y `BatchMode=yes` | **PASS**, código 0 | Log OpenSSH: `using "publickey"`; sin fallback a contraseña, autenticación interactiva, otra identidad de agente o conexión multiplexada previa |
| Comando remoto mediante el alias | **PASS**, código 0 | `MESTRY_REMOTE_COMMAND_OK`, UID **10348**, arquitectura **aarch64** |
| Sesión con terminal mediante el alias | **PASS**, código 0 | `ssh -tt` y comprobación de TTY: `MESTRY_PTY_OK` |
| Permisos remotos de `.ssh` / `authorized_keys` | **700 / 600** | Consulta `stat`; no se volcaron claves autorizadas al registro |
| Contraseña del servidor conservada | **Confirmado** | `sshd -T`: `PasswordAuthentication yes`, `PubkeyAuthentication yes`; el servidor sigue anunciando ambos métodos |

Los parámetros que impiden recurrir a la contraseña se usaron **solo en los comandos de prueba del cliente**; no deshabilitan la contraseña en Termux. No se modificó ni reinició `sshd`.

Uso cotidiano, ya comprobado:

```bash
ssh mestry-s23
ssh mestry-s23 'uname -m'
```

Si después se decide proteger la clave con passphrase, se puede añadir interactivamente desde WSL y cargarla durante ocho horas en un agente. Estos comandos son una **opción documentada, no ejecutada**:

```bash
ssh-keygen -p -f ~/.ssh/id_ed25519_mestry_s23
eval "$(ssh-agent -s)"
ssh-add -t 8h ~/.ssh/id_ed25519_mestry_s23
```

La passphrase se escribe en el terminal, no en argumentos, archivos o documentación. El agente evita repetirla mientras la identidad esté cargada; una terminal nueva debe heredar el entorno de ese agente o cargarla de nuevo.

### Red local e IP dinámica

La sesión usa la IP privada facilitada, **192.0.2.15**, por Wi-Fi/LAN. No se crearon listeners, forwards USB, túneles públicos, reglas de firewall ni cambios del router. La configuración preexistente de `sshd` informa listeners comodín IPv4/IPv6; las herramientas de Termux no permitieron enumerar sockets TCP efectivos. **No se probó alcance desde Internet ni se certifica el aislamiento WAN del router.**

La IP es **dinámica**. Antes de depender de ella habitualmente, preparar una **reserva DHCP**, una red privada con nombre/dirección estable o un mecanismo equivalente. Si cambia, actualizar únicamente el destino del alias en WSL y comprobar la identidad del S23; no desactivar la verificación de host ni borrar entradas de confianza a ciegas. No abrir el puerto 8022 en el router para resolver cambios de dirección.

### Recursos y componentes observados

| Campo | Observación | Fuente y límites |
|---|---|---|
| Hardware / sistema | **SM-S918B**, **aarch64**, Android **16**, API **36** | SSH: `id`, `uname -m`, propiedades Android seleccionadas |
| Kernel Android real | `5.15.DRIVE_ID_04_EXAMPLE` | `uname -r` fuera de PRoot; no es el kernel WSL |
| Build / parche | `BP4A.251205.006.S918BXXSAFZI1` / **2026-09-05** | `getprop`; One UI, CSC y estados de arranque no comprobados |
| Termux | **0.118.3**, origen declarado **F_DROID** | Variables del entorno Termux; paquete Android `versionCode:1002`. No se verificó criptográficamente la firma del APK |
| OpenSSH Termux | **10.6p1-2**; binario **10.6p1** | `dpkg-query`, `sshd -V` |
| RAM total visible al kernel | **7.242.340 KiB ≈ 6,907 GiB** | `/proc/meminfo`; excluye reservas y no demuestra la capacidad comercial exacta |
| RAM disponible | **3.290.092 KiB ≈ 3,138 GiB** | `MemAvailable`, instantánea a las 03:14:40 UTC; `MemFree` era 290.748 KiB y no es la misma métrica |
| Swap | Total **12.582.908 KiB ≈ 12 GiB**, libre **10.744.828 KiB** | No sumarlo a la RAM física; tipo/origen no determinados |
| Datos del teléfono | Total **222,060 GiB**, disponibles **212,151 GiB** | `df -Pk` sobre home y PREFIX; ambos pertenecen al mismo volumen, no se suman. Filesystem observado: **f2fs** |
| Batería | **80 %**, **25,0 °C**, USB conectado, **4,063 V** | `adb.exe … shell dumpsys battery`; valores actuales seleccionados, sin identificadores del fabricante ni historial |
| Estado de batería | `status:4` / **NOT_CHARGING**, `health:2` / **GOOD**; umbral de protección observado **80 %** | Constantes de [BatteryManager](https://developer.android.com/reference/android/os/BatteryManager). Compatible con pausa al límite observado; no se cambió la protección ni se midió capacidad/degradación física |
| PRoot-Distro instalado | **No instalado** | `command -v`, `dpkg-query`; no hay una versión instalada que reportar |
| Candidato PRoot-Distro | **5.10.0** | `apt-cache policy/show`, índices ya existentes; dependencias `proot`, `python`, `python-pip` |
| PRoot instalado / candidato | **No instalado** / **5.1.107.98** | Caché APT existente; no se actualizó ni instaló |
| Python Termux | **No instalado** | `command -v python3`; distinto del Python de WSL usado para administrar |
| X11 | No se detectaron APK `com.termux.x11`, `termux-x11-nightly` ni `x11-repo` | ADB y `dpkg-query`; no hay candidato X11 en los índices actuales, sin el repositorio gráfico habilitado |
| Directorios estándar de rootfs consultados | Ausentes | Rutas estándar de PRoot-Distro antiguas y nuevas; no se realizó una búsqueda exhaustiva de todos los archivos del usuario |

La simulación **`apt-get --simulate --no-install-recommends install proot-distro=5.10.0`** terminó con código 0: **13 paquetes nuevos, 1 actualización (`ncurses`), 0 eliminaciones**. Incluye Python **3.14.8**, pip **26.2.1** y PRoot. **No se aplicó ninguna de esas operaciones.** El mensaje genérico de APT sobre root en modo simulación no es una autorización ni un requisito de root Android para Termux.

Los índices locales anuncian para `proot-distro_5.10.0_all.deb` SHA-256 `6172cc54808fcd0084604a7a7d75e9be22c949f281e3f1dc35cd03dcf364e092`, tamaño 288.548 bytes. Es **metadata del candidato**, no una descarga validada. Se corroboró que la [receta oficial de Termux](https://github.com/termux/termux-packages/blob/master/packages/proot-distro/build.sh) declara 5.10.0; antes de instalar hay que resolver de nuevo el paquete concreto y sus dependencias.

### Debian 13 ARM64 y requisitos X11

Debian **13/trixie** publica soporte **ARM64/AArch64**. Se comprobó además metadata de la imagen oficial `library/debian:13`, variante `linux/arm64/v8`, activa, con digest `sha256:b55910b579d6eb05ebd79fbc8468b974fa39bb0610d52e1f1390bb2177ab7614`. El registro informa 49.761.105 bytes para esa imagen; **no se descargaron capas y ese número no estima el espacio del escritorio/app ni el total instalado**. [Debian](https://www.debian.org/releases/trixie/), [metadata oficial de la imagen](https://hub.docker.com/v2/repositories/library/debian/tags/13).

La versión **5.10.0** de PRoot-Distro usa imágenes **OCI**, no el catálogo antiguo de plugins. Se fijó el tag `v5.10.0` al commit `5a427a1f924550c176ab34197e9fcf5d010fdbd9` y se leyó su README mediante GitHub API. Admite nombre propio, arquitectura y referencia fijada por digest; no se ejecutó el instalador. [Manual de esa revisión](https://github.com/termux/proot-distro/blob/5a427a1f924550c176ab34197e9fcf5d010fdbd9/README.md).

Termux:X11 exige **Android 8 o posterior**, un **APK Android** y el **paquete acompañante** de Termux; el S23 cumple el mínimo de Android. Para este origen F-Droid se recomienda el APK ordinario `termux-x11-universal-debug.apk`, **sin cambiar de fuente ni desinstalar Termux**. La variante `sharedUid` exige la firma de Termux GitHub. Para PRoot, compartir tmp con `--shared-tmp`, configurar `DISPLAY` y D-Bus de sesión. Revisar coherencia de versiones/origen de APK y paquete antes de instalarlos. Se fijó el README al commit `fa3a8b430e2896a19f44c99a9cb056254615ae06`. [Requisitos oficiales](https://github.com/termux/termux-x11/blob/fa3a8b430e2896a19f44c99a9cb056254615ae06/README.md).

### Procedimiento recomendado para la fase siguiente, no ejecutado

1. **Preparar solo el userland base.** Preservar Termux existente, fijar las versiones/hashes reales y revisar dependencias/scripts de los paquetes. Refrescar índices y repetir la simulación antes de aplicar cambios; no hacer un upgrade general para instalar un único componente. PRoot-Distro 5.10.0 y sus dependencias son la candidata observada. El espacio disponible es holgado, pero los 3,138 GiB de RAM disponible no certifican el margen de una app gráfica completa.
2. **Crear un rootfs de prueba nuevo**, con nombre propio y referencia Debian 13 ARM64 fijada por digest. No usar `reset`, `remove` ni reutilizar un rootfs desconocido. Tras entrar, comprobar `/etc/os-release` y `dpkg --print-architecture`; Debian debe informar 13/trixie y `arm64`. El UID 0 simulado de PRoot no es root Android; preparar después un usuario aparente no root para las aplicaciones.
3. **Validar shell, almacenamiento y recursos antes de gráficos.** Usar fixtures sintéticos y medir RAM/espacio/temperatura de nuevo. No presentar compatibilidad ABI o arranque de shell como prueba de sandbox.
4. **Añadir X11 en otra etapa**, tras revisar los artefactos ordinarios y su procedencia: repositorio gráfico y componente Termux, APK oficial, tmp compartido, D-Bus y una aplicación mínima como `xterm`. Empezar sin escritorio completo ni paquetes GPU adicionales. La app oficial y sus puertas de protección/login quedan para una fase posterior del plan V01; sin `--no-sandbox` ni cambios SELinux.

La forma de instalación OCI candidata, **solo documentada y pendiente de verificar en el PRoot-Distro que finalmente se instale**, es:

```bash
# En Termux, en una futura fase de instalación autorizada:
proot-distro install --name mestry-debian13 --architecture aarch64 \
  'debian:13@sha256:b55910b579d6eb05ebd79fbc8468b974fa39bb0610d52e1f1390bb2177ab7614'
proot-distro login mestry-debian13 -- /bin/sh -lc \
  'cat /etc/os-release; dpkg --print-architecture'
```

No se acepta automáticamente el mismo digest si deja de resolverse o si cambia el artefacto seleccionado: registrar el fallo y revisar procedencia antes de sustituirlo. Las versiones, los hashes y los recursos de esta sesión son una base de preparación, no una instalación ya demostrada.

### Fallos de instrumentación y límites conservados

Las 23 consultas remotas se conservan con sus resultados, incluidos `dpkg-query` no cero por paquetes ausentes, `ss` no instalado y `netstat` sin acceso a TCP bajo Android. Una consulta inicial de `sshd -T` usó un filtro de minúsculas y no capturó la salida con mayúsculas de OpenSSH 10.6; se corrigió consultando directamente y publicando solo los campos pertinentes. El código 0 de una tubería no se contó como prueba de que su comando anterior funcionó. La sonda que anuncia métodos de contraseña terminó intencionalmente en 255 sin introducir contraseña: es una observación del protocolo, no un fallo del acceso por clave.

La batería no era legible desde sysfs con el UID Termux y no había Termux:API; se resolvió mediante el canal ADB ya autorizado, sin instalar complementos ni conceder permisos. El dump Samsung completo incluye historial e identificadores: se conserva únicamente en el estado privado de WSL, fuera del proyecto, y la evidencia publicable contiene solo métricas seleccionadas.

No se accedió a cuentas de modelo/Drive ni se pagaron solicitudes. No se probó todavía el runtime Debian, el renderer, el sandbox de herramientas, la estabilidad gráfica o disponibilidad con pantalla apagada. CSC, One UI, inventario S25 y estado de arranque siguen pendientes; no se marca V00 completo.

## Sesión `mestry-s23-audit-20261020T034416Z`: servidor dedicado

**Resultado: auditoría de lectura terminada; optimizaciones pendientes de aprobación.** El usuario confirmó que el S23 será exclusivo para MESTRY. Prohibió desinstalar/deshabilitar aplicaciones, restablecer y modificar ajustes sin aprobación. No se instaló Debian ni la aplicación gráfica, no se reinició y no se alteraron parámetros del dispositivo por el agente.

Informe completo: [S23_SERVER_AUDIT](S23_SERVER_AUDIT.md). Evidencia: [directorio de captura](validation/mestry-s23-audit-20261020T034416Z/), [manifest inicial](validation/mestry-s23-audit-20261020T034416Z/manifest.json), [complementario](validation/mestry-s23-audit-20261020T034416Z/followup_manifest.json), [actualización Boot](validation/mestry-s23-audit-20261020T034416Z/boot_update_manifest.json), [SHA-256 por archivo](validation/mestry-s23-audit-20261020T034416Z/SHA256SUMS).

La captura inicial comenzó **2026-10-20 03:44:17 UTC / 00:44:17 −03:00**. Se usaron ADB Windows, transporte del único SM-S918B autorizado, y SSH por el alias existente. Las sondas y stderr se conservaron con minimización de datos; no se volcaron cuentas, claves o credenciales de red al proyecto. El recolector y analizador se guardan en `tools/`, con copias y hashes en la evidencia. La carpeta sigue sin ser repositorio Git: no hay commit ni push de esta entrega.

Hechos principales:

- RAM visible **6,9068 GiB**, disponible **3,2814–3,3143 GiB** en tres muestras; caché **≈2,61 GiB**, swap usado **≈1,23 GiB** y zRAM física **≈0,414 GiB**. Presión PSI baja. No sumar swap lógico y RAM física.
- RAM Plus configurado en **8192 / equivalente a 8 GB**; zRAM lógica **12 GiB**, **lzo-rle** y respaldo **loop52**. No se modificó y no hay evidencia comparativa para apagarlo.
- CPU agregada **0,896 %** en una ventana de **47,95 s**; consumo eléctrico basal **no determinado de forma fiable** con USB y atributos sysfs bloqueados.
- Batería **80 % / 26,2 °C**, AP **26,8 °C**, estado térmico **0**. Protección al **80 %** conservada. Aviso histórico OEM de deterioro registrado sin inferir degradación ni una avería actual.
- Datos libres **≈212,435 GiB**, CSC **CHO**, propiedad One UI **80500**, Verified Boot **green**, bootloader **locked**. S25 y la recuperación tras reinicio siguen pendientes de V00.
- **416 servicios Binder registrados**, **126 ServiceRecord únicos**, **15 procesos PERS**; no son cantidades equivalentes de tareas activas. LMKD/freezer conservados; límite efectivo de procesos secundarios **32**.
- Termux en primer plano, notificaciones concedidas, bucket activo; fuera de whitelist Doze y sin wakelock parcial observado. SSH respondió tras unos **10 min de pantalla en reposo con USB**, con el mismo daemon; no equivale a prueba sin alimentación o Doze profundo. `termux-services` no instalado, sin runit observado.

Durante la auditoría el usuario informó **«acabo de instalar termux boot»**. Se verificó después **Termux:Boot 0.8.1**, instalado por F-Droid, UID compartido 10348, `notLaunched=false`, habilitado y con notificaciones. **No existe `~/.termux/boot`**, por lo que falta preparar el script y verificar el reinicio. El agente no instaló ni abrió esa aplicación. No se trató la instalación como permiso para cambiar ajustes o crear scripts.

Se preservan dos inventarios: inicial **488 paquetes / 485 sistema / 3 usuario** y posterior **489 / 485 / 4**; el único APK añadido es `com.termux.boot`. Los **23 deshabilitados son los mismos**. El [CSV actual](validation/mestry-s23-audit-20261020T034416Z/applications_inventory_current.csv) clasifica 230 conservados como esenciales operativos, 3 para MESTRY, 99 por compatibilidad, 26 prescindibles condicionales y 131 inciertos. Los 26 incluyen 8 ya deshabilitados; el primer lote propuesto contiene solo 7 habilitados. La memoria corresponde al snapshot previo a Boot, explicitado en el CSV.

Correcciones de instrumentación: se repitió la metadata de paquetes después de detectar que el parser inicial mezclaba APK activos con versiones ocultas de ROM; se verificaron versiones contra PackageManager. `check-signatures` no es un comando soportado; no se afirma verificación criptográfica independiente. Estado `un` de dpkg no significa instalado. Denegaciones parciales se conservaron aunque una shell compuesta devolviera 0.

Recomendación previa a Debian: **optimización selectiva, excepciones específicas y recuperación Termux/Boot; conservar RAM Plus/protecciones y no restablecer de fábrica**. Procedimientos reversibles, riesgos y pruebas O00–O07 están en el informe. V01–V13 no ejecutados; V00 sigue parcial. Esta entrega documenta las propuestas y no las aplica.

## Sesión `mestry-debian13-20261020T040726Z`: SSH, Boot y Debian mínimo

**Estado final: COMPLETADA la instalación mínima y su criterio de aceptación desde WSL; recuperación tras reinicio PENDIENTE, sin reiniciar el teléfono.** Autorización explícita posterior del usuario: dar por suficiente la optimización, no deshabilitar más aplicaciones ni restablecer, preparar recuperación/SSH por claves/Boot e **instalar Debian 13 ARM64 mínimo con PRoot-Distro**. El límite vigente excluye XFCE, Termux:X11 y la aplicación Codex. No se autoriza root, cambios de bootloader/particiones, RAM Plus, exposición pública ni desactivar protecciones.

Esta autorización sustituye la prohibición histórica de instalar Debian en las sesiones anteriores y el «No ejecutar ahora» de la entrega R2 para este subconjunto de V01.1/V01.2. No aprueba las fases gráficas, sandbox, cuentas ni inferencia. La limpieza propuesta en la auditoría queda cerrada sin nuevas actuaciones.

Todos los comandos operativos, resultados y errores de esta sesión se registran en el [anexo de comandos](validation/mestry-debian13-20261020T040726Z/commands.md), con scripts exactos, stdout/stderr y tiempos UTC. [Manifest](validation/mestry-debian13-20261020T040726Z/manifest.json). Las inspecciones de archivos de documentación se realizaron en WSL. El bootstrap a las **04:05 UTC** comprobó el alias SSH y enumeró un único SM-S918B autorizado por ADB USB; el serial se omitió de la evidencia guardada.

El usuario confirmó durante la ejecución: **«Ambas están sin restricciones; revisé suspensión y notificaciones»**, sobre Termux y Termux:Boot. Se registra como intervención manual del usuario, contrastada después con whitelist Doze de ambos paquetes y appops de segundo plano permitidas. No se cambió la política global de batería mediante ADB.

### Resultado y cierre del hilo recuperado

El hilo anterior dejó ejecutadas las sondas **s01–s19** entre **04:07:56 y 04:23:30 UTC**. Al retomar se leyeron los tres documentos solicitados, las decisiones y todos los scripts/resultados pertinentes; **no se reinstaló el entorno**. Las sondas nuevas **s20/s21**, entre **04:39:30 y 04:39:38 UTC / 01:39:30–01:39:38 de Santiago**, confirmaron el estado mediante conexiones independientes SSH/ADB. **s22** verificó offline 63 hashes de los 21 comandos anteriores, las métricas y los invariantes. [Informe de entrega](DEBIAN13_MINIMAL_REPORT.md), [revisión estructurada](validation/mestry-debian13-20261020T040726Z/closure_review.json).

El comando solicitado desde WSL pasó en **s18** y se repitió dentro de una conexión SSH nueva en **s20**, ambos con código **0**:

```bash
ssh -o BatchMode=yes mestry-s23 '$HOME/bin/mestry-debian /usr/local/bin/mestry-check'
```

Salida principal observada:

```text
distribution=Debian GNU/Linux 13 (trixie)
debian_full=13.7
architecture=arm64
apt_version=3.0.3
network_https_status=200
filesystem=PASS
processes=PASS
MESTRY_DEBIAN13_CHECK=PASS
```

La identidad invitada fue **mestry, UID aparente 10349**; `/proc/self/status` conservó **UID/GID Android 10348**, con **CapEff=0000000000000000**. El usuario no tiene contraseña configurada ni servidor SSH dentro de Debian. El login remoto termina en el `sshd` de Termux y desde allí entra en PRoot. La cuenta `root` usada durante APT fue **simulada por PRoot**, sin root Android.

### Cambios realmente aplicados

| Capa | Cambio y evidencia |
|---|---|
| SSH Termux | Drop-in `$PREFIX/etc/ssh/sshd_config.d/00-mestry-key-only.conf`, modo 600: `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AuthenticationMethods publickey`. `sshd -t` pasó. Configuración principal y `authorized_keys` conservan sus bytes originales; respaldo privado en `$HOME/.local/state/mestry/20261020T040726Z/` |
| Recarga SSH | s06 preparó reversión local a los 40 s si faltaba confirmación; s07 reconectó por clave y confirmó a tiempo. No fue necesario revertir. s11 rechazó una conexión sin clave con 255 esperado; s20 volvió a aceptar la Ed25519 exclusiva, sin agente, contraseña ni multiplexación |
| Boot | Único hook `$HOME/.termux/boot/10-mestry-sshd`, modo 700; ejecuta `$HOME/bin/mestry-ssh-start`, también 700. Valida configuración, toma un bloqueo `flock`, solicita wakelock y comprueba el PID para no duplicar `sshd`. No instala supervisor ni inicia Debian u otros servicios |
| Termux | APT actualizado y transacción revisada: **13 paquetes nuevos y actualización de `ncurses`**, sin eliminaciones ni upgrade general. PRoot-Distro **5.10.0**, PRoot **5.1.107.98**, Python **3.14.8**; dependencias obligatorias incluidas en s08 |
| Debian | Instancia nueva **`mestry-debian13`**, ARM64 nativa, desde `library/debian:13` fijada por digest; no reemplaza Android. Rootfs dentro de `$PREFIX/var/lib/proot-distro/containers/mestry-debian13` |
| APT Debian | `apt-get update` correcto en s14 y s15, incluidos índices `trixie`, `trixie-updates`, `trixie-security` con `Signed-By` conservado. Tras instalar certificados y comprobar TLS se cambiaron las URLs a HTTPS; copia previa en `/var/local/mestry/bootstrap/debian.sources.before-https` |
| Diagnóstico mínimo | Solo solicitudes explícitas **`ca-certificates` 20250419**, **`curl` 8.14.1-2+deb13u7**, **`procps` 2:4.0.4-9**, con dependencias obligatorias: 28 paquetes nuevos en total, 0 actualizados/eliminados. Sin recomendados. Se preservó el `policy-rc.d` existente de la imagen para impedir arranques de servicios por los paquetes |
| Acceso cotidiano | Wrapper `$HOME/bin/mestry-debian`, modo 700, entra con `--isolated --user mestry`; home invitado `/home/mestry`, directorio `/home/mestry/projects`. Comprobación repetible `/usr/local/bin/mestry-check` |

Instalación exacta realizada después de consultar el CLI instalado, **no repetir sobre la instancia existente**:

```bash
# Dentro de Termux; comandos ya ejecutados, conservados aquí como registro.
apt-get update
apt-get -y --no-install-recommends install proot-distro=5.10.0
proot-distro install --name mestry-debian13 --architecture aarch64 \
  'debian:13@sha256:b55910b579d6eb05ebd79fbc8468b974fa39bb0610d52e1f1390bb2177ab7614'
# Dentro del rootfs, mediante el root aparente de PRoot:
apt-get update
apt-get -y --no-install-recommends install ca-certificates curl procps
```

Los scripts s08/s13/s14/s15 conservan además inspecciones, simulaciones, creación de usuario y cambio de URLs en su orden real. La metadata seleccionada está en [debian13_image_selected.json](validation/mestry-debian13-20261020T040726Z/debian13_image_selected.json). El digest identifica el artefacto descargado; la versión observada la confirman los archivos de Debian y dpkg, sin inferirla solo del tag.

**Límite de PRoot:** `--isolated` evita los bind mounts automáticos del home de Termux y de almacenamiento compartido; el check no vio el `.ssh` de Termux por su ruta habitual. **No demuestra una frontera de seguridad**: los procesos conservan el mismo UID Android y PRoot no aporta una VM, otro kernel ni aislamiento de privilegios. `uname -r` dentro informa `6.17.0-PRoot-Distro`, un valor sintético. V01.4/V11 siguen sin probar.

### Batería y configuración manual de One UI

Confirmación del usuario conservada arriba. ADB observó después a **Termux y Termux:Boot en la whitelist Doze**, `RUN_ANY_IN_BACKGROUND: allow`, notificaciones concedidas y `stopped=false/notLaunched=false`. s21 volvió a confirmar esos estados con pantalla `Dozing` y USB conectado; no fue un ensayo de Doze profundo.

Los ajustes manuales pertinentes son **Información de la aplicación → Batería → Sin restricciones** para ambas, y **Batería → Límites de uso en segundo plano**: fuera de suspensión/suspensión profunda y, si la UI lo permite, en Nunca en suspensión. Si una aplicación sin restricciones no aparece en esa lista, no forzar cambios. Mantener notificaciones. Estas pantallas OEM no se sustituyeron por comandos ADB que alteren políticas globales.

El helper mantiene `termux:service-wakelock`; s10/s21 lo observaron. Su coste energético **no se midió**. Para una parada de mantenimiento futura puede liberarse desde Termux con `termux-wake-unlock`; Boot/helper volverá a solicitarlo al arrancar. RAM Plus continúa en **8192**, ahorro de energía en **0**, protección de carga en **80 %**, Verified Boot **green**, flash **locked**. Los conjuntos de **23 APK deshabilitados son idénticos** antes/después; no hubo nuevas deshabilitaciones. No se habilitó ADB inalámbrico.

### Entrar y salir de Debian desde WSL

Acceso directo interactivo (un `exit` vuelve a WSL):

```bash
ssh -t mestry-s23 '$HOME/bin/mestry-debian'
# Ya dentro: usuario mestry, home /home/mestry.
exit
```

Acceso por etapas:

```bash
ssh mestry-s23
"$HOME/bin/mestry-debian"
exit  # Debian -> Termux
exit  # Termux -> WSL
```

APT se puede consultar como `mestry`; actualizar índices/instalar exige el root **aparente** del invitado. Entrada de mantenimiento, sin sudo ni root Android:

```bash
ssh -t mestry-s23 'proot-distro login --isolated mestry-debian13'
# apt-get update  # solo cuando se quiera refrescar índices; no hace upgrade
exit
```

Debian se inicia bajo demanda. Salir termina la shell; cerrar SSH no equivale a terminar todos los procesos si se dejan trabajos de fondo. En esta fase no se configuraron daemons Debian; `proot-distro ps` no mostró sesiones persistentes al cierre de s20 antes del nuevo check.

### Recuperación cuando falla SSH

**Canal ADB USB verificado, recuperación local asistida preparada; no se afirma rescate desatendido por ADB.** ADB ejecuta como UID 2000 y Termux como UID 10348. No se habilitaron `RUN_COMMAND`, permisos entre apps ni acceso a su almacén privado. s03 comprobó que ADB lleva Termux al frente; el keyguard seguía bloqueado, por lo que hacía falta intervención física.

Desde WSL, seleccionar el transporte actual del único **SM_S918B** autorizado (el `1` de esta sesión puede cambiar):

```bash
adb.exe devices -l
adb.exe -t TRANSPORT_ID shell getprop ro.product.model
adb.exe -t TRANSPORT_ID shell id
adb.exe -t TRANSPORT_ID shell am start -W --user 0 \
  -a android.intent.action.MAIN -c android.intent.category.LAUNCHER \
  -n com.termux/.app.TermuxActivity
```

En el teléfono, **desbloquear normalmente**, abrir una consola de Termux y ejecutar:

```bash
"$HOME/bin/mestry-ssh-start"
```

Después repetir el comando de aceptación desde WSL. Si hay error de sintaxis, revisar `sshd -t` en esa consola y el drop-in, con el respaldo privado disponible. Si falta la clave autorizada, incorporar únicamente la **clave pública** desde la consola local y conservar modos `.ssh=700/authorized_keys=600`. No copiar claves privadas ni deshabilitar verificación de host. Un cambio de IP requiere revisar la dirección del alias, no abrir puertos del router. Si ADB aparece `unauthorized`, aceptar el PC físicamente; no eludir el bloqueo.

En **s17** se detuvo solo el daemon listener, con un helper local previamente programado: pasó de PID **18143** a **2975** en **≤2 s** y luego s18 reconectó. Se conserva como **ensayo de recuperación del proceso con relanzamiento preparado**, no como supervisor automático ni como prueba completa de recuperación ADB con SSH caído. Boot tampoco supervisa una caída posterior de `sshd` o del UID Termux.

### Comprobación tras un futuro reinicio — procedimiento, NO ejecutado

1. Acordar previamente la ventana de reinicio, tener acceso físico/USB y conservar la configuración WSL. No se ha enviado ningún comando de reinicio en esta sesión.
2. Tras el reinicio autorizado, registrar si SSH está disponible **antes** del primer desbloqueo, sin abrir apps ni ejecutar el helper. Su ausencia no prueba una avería de Boot. Android separa el almacenamiento cifrado por credenciales, accesible después del primer desbloqueo; por ello se debe prever recuperación asistida. [Direct Boot, documentación Android](https://developer.android.com/privacy-and-security/direct-boot?hl=en).
3. Desbloquear una vez con la credencial normal y esperar hasta **60 s como ventana propuesta de observación**, con Wi-Fi disponible, **sin abrir Termux**. Probar una conexión nueva `ssh -o BatchMode=yes mestry-s23 true` y después el comando Debian de aceptación.
4. Consultar por SSH `cat "$HOME/.local/state/mestry/ssh-start.status"`, el PID de `$PREFIX/var/run/sshd.pid` y `sshd -t`; registrar tiempo hasta volver, pantalla/red, política de claves y número de listeners. El éxito debe llegar sin lanzar comandos de rescate desde el PC/teléfono para contarlo como arranque por Boot.
5. Si falla, usar la recuperación asistida anterior y conservar el fallo como tal. Revisar apertura inicial de Termux:Boot, restricciones OEM y notificaciones. No marcar el ensayo de Boot como PASS si SSH vuelve solo después de abrir Termux o ejecutar el helper manualmente.

[Termux:Boot](https://github.com/termux/termux-boot#how-to-use) requiere abrir la app una vez y ejecutar scripts desde `~/.termux/boot`; PackageManager ya informa que fue abierta. En este firmware queda **pendiente comprobar** el comportamiento tras primer desbloqueo y eventuales retrasos OEM. No se retira PIN/cifrado ni se trasladan claves fuera del almacén privado. La revisión de reinicios automáticos de One UI y una eventual reserva DHCP siguen siendo tareas manuales de mantenimiento, sin cambios automáticos ahora.

### Mediciones y límites

[Datos originales s19](validation/mestry-debian13-20261020T040726Z/resources.json): tres muestras por estado a **04:23 UTC**, con una sesión PRoot que solo ejecutó `sleep`, más el coste de SSH/Python de diagnóstico.

| Métrica | Resultado |
|---|---:|
| RAM visible Android | **6,907 GiB** |
| RAM disponible antes / con PRoot inactivo en espera / después, medianas | **3,277 / 3,274 / 3,270 GiB** |
| PSS de la familia PRoot + sleep, tres muestras | **2.370 KiB = 2,31 MiB** en cada muestra |
| Rootfs y metadata de la instancia, `du` | **200.921 KiB = 196,21 MiB** |
| Caché OCI conservada | **48.663 KiB = 47,52 MiB** |
| PREFIX Termux final, incluyendo instancia/caché | **406.956 KiB = 397,42 MiB** |
| Crecimiento PREFIX + home desde s01 | **311.101 KiB = 303,81 MiB** |
| Datos disponibles s19 / s20 | **212,089 / 212,082 GiB** |
| RAM disponible en la conexión final s20 | **3,181 GiB**, instantánea distinta |

La diferencia de RAM total disponible fluctúa también después de salir: **no se atribuye íntegramente a Debian** ni se presenta el PSS de `sleep` como coste de una aplicación. Rootfs y caché ya están incluidos en PREFIX: no sumarlos dos veces. El crecimiento de `du` es de los directorios medidos, no una estimación de todo el volumen; no se borró caché para mejorar la cifra. El margen actual no valida gráficos, carga sostenida ni V10.

### Comandos, resultados y errores conservados

El [anexo](validation/mestry-debian13-20261020T040726Z/commands.md) contiene un enlace al script **exacto** de cada sonda, stdout, stderr, tiempos y código; el manifest conserva argv, timeout y SHA-256. Se ejecutaron mediante `python3 tools/mestry_session.py --directory docs/validation/mestry-debian13-20261020T040726Z --name NOMBRE --channel ssh|adb|host --script ARCHIVO --timeout SEGUNDOS`; las sondas Ed25519 incluyen `--ssh-debug`. Los ejemplos de recuperación y mantenimiento de arriba son instrucciones futuras, no ejecuciones adicionales.

| Sondas | Resultado y lectura correcta |
|---|---|
| s01–s04 | Preflight Termux, ADB, apertura de actividad local y refresco de metadata Termux: código 0. La apertura llevó una tarea existente al frente; no desbloqueó el teléfono |
| s05–s07 | Preparación y recarga protegida SSH, reconexión independiente y doble invocación idempotente de Boot: código 0, sin duplicar daemon |
| **s08** | **Código 1 conservado:** APT terminó de instalar, pero la consulta posterior `proot-distro --version` no existe en 5.10.0. No fue un fallo de instalación; s12 confirmó `ii`, versiones y ayuda real, sin reinstalar |
| s09–s11 | Metadata de imagen fijada, verificación tras ajustes manuales y test negativo de auth: código 0. El SSH interno de s11 devuelve **255 esperado** sin clave; no se introdujo contraseña |
| s12–s16 | CLI instalado, instalación del rootfs, APT, diagnóstico mínimo, usuario y wrappers: código 0. Las ayudas extensas de PRoot-Distro se imprimen en stderr, sin que ello indique fallo |
| s17–s19 | Recuperación controlada del daemon, comando directo WSL y mediciones: código 0 |
| s20–s22 | Reconexión Ed25519 + Debian, ADB actual y revisión offline: código 0. Se conservaron salidas previas sin sobrescribir |

Exploración local al retomar: `pwd`, `rg --files`, lecturas `cat`/`sed`/`tail`, búsquedas `rg`, `ls`, `wc`, `date` y revisión Python de JSON/hashes. No apareció `AGENTS.md` en el proyecto ni en sus padres comprobados; la búsqueda de memoria `mestry|s23|termux|proot` no tuvo coincidencias (rg=1). **`git status --short` devolvió 128: no es un repositorio Git**, como ya constaba. No se creó repositorio ni se hicieron commits/push. Los archivos temporales de sondas se crearon en `/tmp` y se guardaron por el logger antes de ejecutarse.

Consulta documental final, fuera del teléfono: apertura web del README oficial de Termux:Boot y de Direct Boot. La primera apertura de la página Android falló por **timeout de lectura**; se recuperó su contenido mediante búsqueda de la misma fuente oficial con `?hl=en`. No hubo reintento de ninguna operación del teléfono por este fallo. No se siguieron las instrucciones de conversión de cifrado que aparecen en esa página; solo se consultó el comportamiento tras desbloqueo.

**Límite final:** userland Debian mínimo verificado y documentación de operación/recuperación preparada. Sin reinicio, root, cambios de bootloader/particiones/RAM Plus, nuevas deshabilitaciones, XFCE, X11, app Codex, cuentas o inferencia. No se crearon forwards, túneles ni reglas públicas. SSH mantiene los listeners comodín IPv4/IPv6 preexistentes en 8022; el acceso probado fue LAN y **no se certifica aislamiento WAN/IPv6 del router**. No se copiaron contraseñas ni claves privadas al proyecto; el respaldo SSH permanece en el almacén privado de Termux. **Trabajo detenido aquí; fase gráfica pendiente.**

## Sesión `mestry-x11-20261020T052004Z`: Termux:X11 y ventana Linux mínima

**EXP03, autorización posterior: PRUEBA GRÁFICA MÍNIMA COMPLETADA.** El usuario autoriza instalar el APK oficial **normal**, el acompañante del repositorio X11 y solo herramientas gráficas mínimas en Debian, con display local, mediciones y reversión. Se mantienen prohibidos reinicio, root, cambios privilegiados/SELinux/sandbox, escritorio XFCE completo y aplicación ChatGPT/Codex. La prueba de Boot continúa separada y pendiente. No hay autorización de cuentas ni inferencia.

Evidencia: [manifest y tiempos UTC](validation/mestry-x11-20261020T052004Z/manifest.json), [comandos exactos y stdout/stderr](validation/mestry-x11-20261020T052004Z/commands.md). Se reutiliza `tools/mestry_session.py` con un manifest nuevo de alcance EXP03, sin modificar la evidencia de Debian mínimo.

Se leyeron `DEBIAN13_MINIMAL_REPORT.md`, `INSTALLATION_LOG.md` y `VALIDATION_PLAN.md`; no se encontró AGENTS aplicable ni memoria específica. Se comprobó SSH Ed25519 en conexión nueva, `MESTRY_DEBIAN13_CHECK=PASS`, ADB USB y se tomaron tres muestras de RAM y almacenamiento **antes** de instalar. La consulta inicial de herramientas no encontró Java/aapt/apksigner Linux y `ls /usr/lib/jvm` devolvió 2; se usaron Android SDK build-tools **37.0.0** y Java de Android Studio ya existentes en Windows, sin instalar herramientas de host.

El APK oficial normal `termux-x11-universal-debug.apk` procede de la release `nightly`, commit **fa3a8b430e2896a19f44c99a9cb056254615ae06**, publicada **2026-10-06**. SHA-256 comprobado contra el digest del asset GitHub: **64995746d1887a0e70bc8977d4a9c5ea56e3e00eadd4a6eeab32ae6048ba733a**. `apksigner verify --verbose --print-certs` pasó; `aapt` confirmó ARM64, paquete `com.termux.x11`, versión **1.03.01-fa3a8b4-06.10.26** y ausencia de `sharedUserId`. [Selección](validation/mestry-x11-20261020T052004Z/artifact_selection.json), [verificación](validation/mestry-x11-20261020T052004Z/apk_verified.json). La firma se verificó criptográficamente; la procedencia se apoya en release HTTPS/digest oficial, sin una raíz de confianza independiente para el certificado debug.

ADB instaló el APK con `install --no-incremental`, **Success**, sin flags de concesión masiva o evasión de restricciones. Se habilitó `x11-repo=8.4-1`, y se instaló `termux-x11-nightly=1.03.01-6` con su dependencia `xkeyboard-config=2.48-1` desde índices firmados; no se instaló XFCE sugerido. Se inspeccionaron control/payload/postinst: solo hace no escribible `loader.apk`. Las definiciones de servicios `tx11`/`tx11-xfce4` quedan con `down`; Boot no se alteró.

**Errores y decisiones durante la preparación:** q09 devolvió 1 porque una comprobación adicional exigía identidad de bytes/DEX entre el loader del repositorio y el de la misma release nightly del APK. Son diferentes; no se interpretó como fallo del S23 ni se sustituyó el paquete del repositorio. Se conserva el fallo y se exige comprobar el arranque/protocolo real antes de declarar compatibilidad. La simulación con `x11-utils` proponía **66 paquetes**, incluyendo Mesa/LLVM: **no se aplicó**. Se preparó una simulación reducida con `xterm`, `xauth` y `fonts-dejavu-mono`.

La apertura del APK mediante ADB llegó al diálogo Android de notificaciones con el keyguard bloqueado. Se solicitó al usuario desbloquear normalmente y permitir las notificaciones; no se eludió el bloqueo ni se concedió ese permiso mediante ADB.

### Resultado observado y alcance

**Ventana Linux visible y entrada de teclado verificadas.** El usuario primero informó que veía la ventana pero no aparecían letras. Tras corregir el foco respondió **«Sí, aparecen las letras y PASS»**. El script dentro de `xterm` escribió el marcador **2026-10-20 06:58:56 UTC / 03:58:56 de Santiago**; q23 lo leyó desde WSL en una conexión SSH nueva y volvió a confirmar `MESTRY_DEBIAN13_CHECK=PASS`.

[Informe gráfico mínimo](TERMUX_X11_REPORT.md), [captura inspeccionada](validation/mestry-x11-20261020T052004Z/xterm_focus_corrected.png), [aceptación estructurada](validation/mestry-x11-20261020T052004Z/acceptance_review.json). La captura muestra la ventana **antes** de escribir; la respuesta de teclado se acredita por la confirmación humana y el marcador invitado, no por un PASS añadido a la imagen.

| Criterio | Resultado real |
|---|---|
| APK normal instalado | **PASS**, versión 1.03.01-fa3a8b4-06.10.26, ARM64; firma v2 válida y digest oficial coincidente |
| Acompañante | **PASS**, termux-x11-nightly 1.03.01-6 del repositorio firmado; cargador funcional con ese APK |
| Servidor local | **PASS**, display `:1`, PID 11339, socket `$PREFIX/tmp/.X11-unix/X1` |
| Debian conectado | **PASS**, `--isolated --shared-tmp --user mestry`, mismo socket visible como `/tmp/.X11-unix/X1`; `xterm` abrió el display |
| Autenticación X11 | **PASS**, MIT-MAGIC-COOKIE-1 en archivo privado modo 600; cliente sin cookie rechazado con rc=1, autenticado aceptado. Sin `-ac` ni `xhost +` |
| Acceso por red | TCP deshabilitado mediante `-nolisten tcp`; puerto 6001 rechazó conexión por loopback IPv4/IPv6 y desde la LAN WSL. No se publicaron listeners ni forwards X11 |
| Ventana y respuesta | **PASS**, ventana MESTRY visible; foco corregido y `MESTRY_GUI_INPUT=PASS` tras escritura real del usuario |
| Privilegios/protecciones | UID real Termux **10348**, capacidades efectivas **0**; SELinux **Enforcing**, Verified Boot **green**, flash **locked** y RAM Plus **8192** |

No se ensayaron 30 minutos de estabilidad, suspensión prolongada, Boot/reinicio, escritorio, app oficial, renderer o sandbox del harness. **V01 global continúa parcial.**

### Herramientas mínimas y corrección del foco

La transacción aplicada en Debian fue `apt-get -y --no-install-recommends install xterm=398-1 xauth fonts-dejavu-mono`: **28 paquetes nuevos, 0 actualizados/eliminados**, descarga 6.062 kB, estimación APT de 16,4 MB instalados. `fonts-dejavu-core` llegó como dependencia, sin Mesa/LLVM. Para diagnosticar el teclado se añadió **xdotool** y cuatro dependencias: otros **5 paquetes nuevos**, sin upgrade general. Versiones finales: xterm **398-1**, xauth **1:1.1.2-1.1**, fuentes **2.37-8**, xdotool **1:3.20160805.1-5.1**.

El display no tiene gestor de ventanas. `xdotool` observó foco **PointerRoot, valor 1**; intentar consultar propiedades de ese valor generó `BadWindow`, conservado en q21. Se usó `windowfocus --sync` sobre la única ventana titulada **MESTRY - Debian 13 ARM64**, ID **2097164**. Después el foco coincidió y el teclado funcionó. No se cambió el teclado Samsung ni preferencias de entrada Android, y no se inyectó texto mediante ADB/xdotool para fabricar la confirmación.

Se adaptó `$HOME/bin/mestry-debian` con **opt-in `MESTRY_SHARED_TMP=1`**; sin esa variable conserva el comportamiento aislado original. Respaldo exacto privado: `$HOME/.local/state/mestry/mestry-x11-20261020T052004Z/mestry-debian.before`. El helper nuevo `$HOME/bin/mestry-x11` implementa `start|status|demo|focus|stop`, evita colisiones de display y PID, genera una cookie nueva al arrancar y enfoca automáticamente la demo. `/usr/local/bin/mestry-gui-demo` solo muestra identidad/versión y espera la cadena de prueba.

Copias públicas de revisión de los scripts desplegados, sin cookies ni claves: [wrapper Debian](validation/mestry-x11-20261020T052004Z/deployed_mestry-debian.sh), [helper X11](validation/mestry-x11-20261020T052004Z/deployed_mestry-x11.sh), [demo invitada](validation/mestry-x11-20261020T052004Z/deployed_mestry-gui-demo.sh). Los hashes están en el [anexo](validation/mestry-x11-20261020T052004Z/deployed_scripts_sha256.json).

### Operación reproducible desde WSL

Para arrancar una sesión de prueba cuando no exista una demo previa:

```bash
ssh mestry-s23 '$HOME/bin/mestry-x11 demo'
```

En el S23 abrir **Termux:X11** y desbloquear normalmente si corresponde. Debe aparecer `MESTRY - VENTANA LINUX`, Debian 13, `arm64`, usuario `mestry`, display `:1`. Mostrar el teclado con Atrás o su botón; escribir `MESTRY_OK` y Enter. Aparece `MESTRY_GUI_INPUT=PASS`. La ventana se mantiene abierta con `xterm -hold` después de que termina el pequeño script.

Si ya hay una demo abierta, no duplicarla; consultar estado y recuperar el foco:

```bash
ssh mestry-s23 '$HOME/bin/mestry-x11 status'
ssh mestry-s23 '$HOME/bin/mestry-x11 focus'
ssh mestry-s23 '$HOME/bin/mestry-debian /usr/bin/test -f /home/mestry/.local/state/mestry/x11/input-confirmed' && echo MESTRY_GUI_INPUT=PASS
```

Para otra aplicación de prueba ya instalada, compartir tmp explícitamente y pasar el display y la cookie dentro del invitado:

```bash
ssh mestry-s23 'MESTRY_SHARED_TMP=1 "$HOME/bin/mestry-debian" /usr/bin/env DISPLAY=:1 XAUTHORITY=/tmp/mestry-x11-auth/Xauthority /usr/bin/xterm -fa "DejaVu Sans Mono"'
```

Ese último ejemplo es una instrucción futura y crea otro cliente; la aceptación registrada usó el helper de demo. La cookie real está en `$PREFIX/tmp/mestry-x11-auth/Xauthority`, directorio 700 y archivo 600, y **no se copió al proyecto**. `--shared-tmp` abre el tmp de Termux al invitado; no habilita el bind habitual del home SSH ni demuestra aislamiento de seguridad entre procesos del mismo UID Android.

Para cerrar solo el servidor experimental y sus clientes, sin tocar SSH:

```bash
ssh mestry-s23 '$HOME/bin/mestry-x11 stop'
```

`stop` valida el PID y su cmdline antes de enviar TERM. La actividad Android puede permanecer abierta sin conexión; se cierra normalmente desde el teléfono. No se ejecutó `stop` al entregar: el servidor y el `xterm` de prueba quedaron abiertos, sin arranque automático añadido.

### Memoria y almacenamiento antes/después

[Datos, unidades y límites](validation/mestry-x11-20261020T052004Z/resources_summary.json). Tres muestras de RAM antes a **05:21 UTC**, final a **07:02 UTC**, con intervalo de reanudación de la sesión y acciones del usuario entre ambas; no es un experimento controlado de rendimiento.

| Métrica | Antes | Después |
|---|---:|---:|
| RAM disponible Android, mediana | **3,234 GiB** | **2,880 GiB** |
| Instancia Debian, incluida dentro de PREFIX | **196,21 MiB** | **221,87 MiB** |
| PREFIX Termux | **397,40 MiB** | **428,05 MiB** |
| Home Termux | **0,38 MiB** | **0,91 MiB** |
| Caché OCI | **47,52 MiB** | **47,52 MiB** |
| Código instalado del APK X11 | Ausente | **14,04 MiB** |

Crecimiento de PREFIX + home: **31,18 MiB**; el rootfs aporta **25,65 MiB** de ese crecimiento, no se suma otra vez. El directorio de código APK se mide aparte; **sus datos privados internos no fueron medidos**. Quedan **212,09 GiB** disponibles. `df` refleja cambios de todo Android y no se usa para atribuir ahorro/coste causal a esta instalación.

PSS medido de los procesos activos seleccionados del servidor + PRoot + xterm: mediana **92,75 MiB** en q27. El visor Android mostró **51,78 MiB** en otra lectura, cuando ya no estaba al frente. No se presentan como consumo físico total sincronizado ni se suma RSS de páginas compartidas. Tampoco son una estimación del futuro coste de ChatGPT/Codex.

La captura con `TERMUX_X11_DEBUG=1` lanzaba un `logcat` de diagnóstico. q25 detuvo **solo ese hijo** del servidor para evitar recolección continua, y dejó desactivado el debug por defecto en próximos arranques; se puede solicitar con `MESTRY_X11_DEBUG=1`. La primera suma PSS posterior incluyó un proceso logcat zombi y quedó marcada **incompleta**, con `ProcessLookupError`, sin sustituirlo por cero. q27 verificó su estado `Z` y midió por separado los procesos activos, conservando ambos resultados.

### Fallos y límites conservados

- **q09, rc=1:** diferencia real de bytes/DEX entre loader del repositorio y nightly. Ambos comparten base 1.03.01; su compatibilidad **para esta configuración** se confirmó con ayuda del servidor, socket, cliente autenticado, ventana y teclado, sin afirmar identidad binaria.
- **q14:** un cliente sin cookie devolvió 1 y `Can't open display`, como test negativo previsto. Se conservan stderr y los mensajes de autorización del log; no se transformaron en fallo del cliente autenticado, cuya ejecución tiene evidencia independiente.
- **q21:** fallo inicial de consulta del foco PointerRoot; corregido enfocando la ventana real. La confirmación final vino del usuario y del marcador dentro de Debian.
- **q24, rc=1:** se canceló una captura porque Termux:X11 ya no estaba al frente. No se capturó otra aplicación. q26 recogió métricas sin forzar foco Android y conservó la captura anterior y la confirmación humana.
- **q25/q27:** suma PSS incompleta y lectura posterior específica de procesos activos, según lo explicado arriba.
- **Lectura web:** el lector no admitió `text/markdown` de dos páginas OpenAI; se obtuvieron por HTTPS con urllib solo para preparar el plan, sin descargar la app. Fuentes/hashes en [next_phase_official_sources.json](validation/mestry-x11-20261020T052004Z/next_phase_official_sources.json).

El [issue oficial #1115](https://github.com/termux/termux-x11/issues/1115) describe ausencia de socket tras reiniciar un **SM-F936U1** con Android 16; fue cerrado por falta de actividad, sin resolución verificada. **No se reprodujo ese síntoma en esta sesión del S23**: se creó el socket y se completó la interacción. No se reinició para intentar reproducirlo, ni se aplicaron parches, root o relajación de protecciones. Los avisos de acceso denegado a una propiedad OEM de refresco de pantalla se conservaron; no motivaron cambios privilegiados.

El APK tiene un UID Android **10349**, distinto del UID Termux **10348**. El UID 10349 de `mestry` dentro de PRoot es aparente y no debe confundirse con los permisos reales del APK. La lectura final mantiene notificaciones de Termux:X11 **no concedidas**; no se forzó el permiso. Para disponibilidad prolongada, revisar manualmente sus notificaciones y restricciones de batería; el éxito actual es una prueba con interacción en primer plano, no certificación de segundo plano.

La línea base de esta sesión tenía **28 APK deshabilitados**, distinta de los 23 de la sesión anterior. No se atribuye ese cambio a este trabajo: ya estaba presente en q02 y q26 confirmó el conjunto idéntico. No se deshabilitó ni habilitó ninguna app existente durante EXP03.

### Recuperación y reversión — instrucciones, no ejecutadas

Si se pierde la ventana, comprobar `status`, abrir Termux:X11 y usar `focus` si la demo sigue abierta. Leer los logs privados `$HOME/.local/state/mestry/x11/server.log` y `demo.log` sin copiarlos indiscriminadamente; no publicar cookies. Si falta un socket, verificar el proceso real antes de retirar un lock propio: no borrar todo `.X11-unix` ni iniciar servidores duplicados. SSH/ADB conservan el procedimiento de recuperación de la sesión Debian mínima.

Para revertir todo el incremento, después de cerrar el servidor:

1. Retirar **solo** `com.termux.x11` mediante Ajustes o `adb.exe -t TRANSPORT_ID uninstall com.termux.x11`. Eso borra preferencias/datos del nuevo APK; conservarlos primero si interesan. No desinstalar Termux, Boot o F-Droid.
2. En Debian, simular `apt-get --simulate purge xterm xauth fonts-dejavu-mono xdotool` con el root aparente. Revisar la lista contra el inventario previo `/var/local/mestry/bootstrap/packages.before-x11.tsv` antes de aplicar. Revisar aparte `apt-get --simulate autoremove`; no retirar dependencias que use otro software añadido después.
3. En Termux, simular `apt-get --simulate remove termux-x11-nightly xkeyboard-config x11-repo` y aplicar únicamente si siguen siendo exclusivos de esta prueba. El paquete `x11-repo` gestiona su archivo de repositorio; comprobar qué archivo retira, sin borrar otras fuentes.
4. Restaurar el wrapper exacto desde `$HOME/.local/state/mestry/mestry-x11-20261020T052004Z/mestry-debian.before`. Archivar `$HOME/bin/mestry-x11` y retirar la demo invitada `/usr/local/bin/mestry-gui-demo`. Tras confirmar que no hay servidor activo, retirar **solo** el directorio de cookie `mestry-x11-auth` y el estado de esta demo si no se necesitan sus diagnósticos.
5. Repetir `ssh mestry-s23 '$HOME/bin/mestry-debian /usr/local/bin/mestry-check'`. El rootfs, `/home/mestry/projects`, claves SSH, Boot y Android se conservan. No usar `proot-distro reset/remove` como desinstalación de gráficos.

Todos los comandos ejecutados están en el anexo q01–q28 y las verificaciones documentales posteriores. Las operaciones de reversión anteriores **no se ejecutaron**. La sesión termina en la ventana mínima validada. [Plan de ChatGPT Linux ARM64 para revisar, sin instalación](CHATGPT_LINUX_ARM64_PLAN.md).

## Sesión `mestry-chatgpt-20261020T071932Z` — EXP04, auditoría de la app oficial

**2026-10-20. Estado final: BLOQUEADO ANTES DE INSTALAR.** El usuario autorizó obtener y auditar el `.deb` oficial ARM64 y, únicamente si no había bloqueos importantes, instalarlo y abrirlo como `mestry` sin iniciar sesión. La auditoría encontró un bloqueo real de prerrequisitos del sandbox: **USER_NS y PID_NS deshabilitados en el kernel del S23**. Se activó la parada de la fase 2; no se instaló ni ejecutó ChatGPT, Codex o sus dependencias. El criterio de apertura gráfica segura **no se alcanzó**; tampoco se observó un crash de arranque, porque no se intentó ese paso.

[Informe específico](CHATGPT_LINUX_ARM64_REPORT.md), [dictamen estructurado](validation/mestry-chatgpt-20261020T071932Z/acceptance_review.json), [índice íntegro de comandos](validation/mestry-chatgpt-20261020T071932Z/commands.md), [manifest con hashes, tiempos y retornos](validation/mestry-chatgpt-20261020T071932Z/manifest.json).

### Preparación y artefacto fijado

Se leyeron `CHATGPT_LINUX_ARM64_PLAN.md`, `TERMUX_X11_REPORT.md`, este registro y el plan de validación. Se consultaron las páginas oficiales [Linux](https://learn.chatgpt.com/docs/linux/linux-app) y [sandbox](https://learn.chatgpt.com/docs/sandboxing); copias de referencia fuera del proyecto, URLs/hashes en [procedencia](validation/mestry-chatgpt-20261020T071932Z/package_provenance.json). SSH por clave respondió, `mestry-check` volvió a dar **PASS**, Debian informó **13.7/arm64**, glibc **2.41** y el servidor X11 previo seguía activo.

Paquete descargado desde el enlace ARM64 publicado, sin repositorios de terceros:

```text
https://persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_arm64.deb
Package: chatgpt
Version: 26.1013.40934
Architecture: arm64
Bytes: 479841538 (457,61 MiB)
SHA256: 9ab2cbbaf33cebeaa1e06eb5cab78128936f927a0d97bf00e40694e5f31c629b
```

El instalador se conserva en `/home/developer/.local/state/mestry/mestry-chatgpt-20261020T071932Z/downloads/chatgpt_arm64.deb`, **fuera del proyecto**. Tiene formato Debian `ar` y firma `_gpgorigin`. Se verificaron esta firma, `InRelease`, el hash del índice ARM64 y la coincidencia del paquete con ese índice, usando la clave pública incluida **`3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4`**. El anclaje inicial sigue siendo HTTPS y el enlace oficial: no se afirmó disponer de un fingerprint autenticado por otro canal. [Verificación del repositorio](validation/mestry-chatgpt-20261020T071932Z/repository_integrity.json), [firma del paquete](validation/mestry-chatgpt-20261020T071932Z/origin_signature_verification.json).

### Comandos, resultados y errores conservados

Cada fila enlaza el script exacto; su stdout/stderr y retorno están en el índice y manifest anteriores. Los archivos de evidencia no son un instalador para ejecutar en bloque.

| Probe | Operación | Resultado |
|---|---|---|
| [p01](validation/mestry-chatgpt-20261020T071932Z/p01_phone_preflight.sh) | SSH, UID/kernel reales, recursos, helpers, X11, check Debian e inventario | **0**; `MESTRY_DEBIAN13_CHECK=PASS`; 139 paquetes instalados |
| [p02](validation/mestry-chatgpt-20261020T071932Z/p02_android_preflight.sh) | ADB: batería/temperatura, térmico, protecciones, X11 y RAM Plus | **0**; Enforcing/green/locked, RAM Plus 8192 |
| [p03](validation/mestry-chatgpt-20261020T071932Z/p03_official_download.sh) | Referencias HTTPS e intento inicial de descargar el `.deb` con urllib | **1**; HTTP **403**, Cloudflare código **1010**, con user-agent Python predeterminado |
| [p04](validation/mestry-chatgpt-20261020T071932Z/p04_download_diagnostics.sh) | Diagnóstico del mismo enlace con urllib/curl y HEAD | **0**; con user-agent de navegador o curl devuelve **200**, MIME Debian y tamaño esperado |
| [p05](validation/mestry-chatgpt-20261020T071932Z/p05_phone_origin_kernel_prereqs.sh) | HEAD desde Termux, montajes, sysctls legibles y `unshare` invitado | **2**; HEAD 200; montaje `nosuid`; el último `ls` no encuentra namespaces user/pid. `unshare` había devuelto 0; no se aceptó como protección |
| [p06](validation/mestry-chatgpt-20261020T071932Z/p06_download_official_deb.sh) | Descarga HTTPS oficial con user-agent de navegador, sin cookies/login | **0**; artefacto completo, formato/control, tamaño/hash fijados |
| [p07](validation/mestry-chatgpt-20261020T071932Z/p07_actual_namespace_probe.sh) | Syscall nativa AArch64 97 y comparación dentro de PRoot | **0** del diagnóstico; syscall **−1/EINVAL**, guest unshare 0 sin namespace nuevo |
| [p08](validation/mestry-chatgpt-20261020T071932Z/p08_redact_transient_cdn_cookies.sh) | Minimizar cookies transitorias del CDN en evidencia pública | **0**; redacción declarada y hashes publicados actualizados |
| [p09](validation/mestry-chatgpt-20261020T071932Z/p09_static_control_audit.sh) | `dpkg-deb --control/--contents`, `ar`, `file`; leer scripts | **0**; sin ejecutar instaladores; scripts y listado archivados |
| [p10](validation/mestry-chatgpt-20261020T071932Z/p10_signed_repository_integrity.sh) | `gpgv` de InRelease e índice ARM64 | **0**; firma válida y paquete coincidente |
| [p11](validation/mestry-chatgpt-20261020T071932Z/p11_static_binary_audit.sh) | Extraer selección en WSL sin ejecución; `readelf`, ASAR | **0**; ELF AArch64 y glibc compatibles en lo inspeccionado; sin `chrome-sandbox` |
| [p12](validation/mestry-chatgpt-20261020T071932Z/p12_stage_for_apt_simulation.sh) | Copiar paquete a un directorio nuevo privado en tmp Termux | **0**; SHA-256 remoto idéntico; solo staging para solver |
| [p13](validation/mestry-chatgpt-20261020T071932Z/p13_apt_simulation.sh) | APT simulado y resolución `--assume-no`, inventario posterior | **0** del probe; `--assume-no` **1 esperado**, responde N y aborta; ningún paquete cambiado |
| [p14](validation/mestry-chatgpt-20261020T071932Z/p14_verify_package_origin_signature.sh) | `gpgv` de `_gpgorigin` sobre los tres miembros Debian concatenados | **0**; firma válida |
| [p15](validation/mestry-chatgpt-20261020T071932Z/p15_dependency_chain_audit.sh) | `apt-cache depends`, AppArmor y lectura de config disponible a Termux | **0**; cadenas udev/systemd explicadas; config no legible por Termux |
| [p16](validation/mestry-chatgpt-20261020T071932Z/p16_sandbox_keyring_static_audit.sh) | Referencias estáticas de renderer, bubblewrap y keyring | **0**; no acredita rutas ejecutadas ni enforcement |
| [p17](validation/mestry-chatgpt-20261020T071932Z/p17_cleanup_staging_final_resources.sh) | Retirar solo staging, revalidar helpers/display/TCP y recursos/inventario | **0**; staging retirado, TCP X11 rechazado, paquete y repo ausentes |
| [p18](validation/mestry-chatgpt-20261020T071932Z/p18_android_final.sh) | ADB: batería/protecciones y config.gz ya legible sin root | **0**; **USER_NS/PID_NS no habilitados**; seccomp/SELinux sí |
| [p19](validation/mestry-chatgpt-20261020T071932Z/p19_offline_audit_summary.sh) | Comparar inventarios y derivar transacción, métricas y dictamen | **0**; inventarios idénticos; bloqueo previo a instalar |

El lector web identificó el enlace oficial, pero no pudo representar el contenido binario Debian; la descarga efectiva y su hash proceden de p06. El 403 inicial no se confundió con una necesidad de autenticar: p04 comprobó el mismo enlace público y p06 descargó sin cuenta ni cookies.

Las cabeceras HEAD incluyeron cookies **transitorias de CDN, sin sesión de usuario**. Se retiraron sus valores de tres salidas públicas; el [registro de redacción](validation/mestry-chatgpt-20261020T071932Z/public_output_redactions.json) conserva hashes originales/publicados y razón, y los hashes del manifest reflejan los archivos publicados. No se guardaron claves privadas, contraseñas ni tokens de cuenta.

### Auditoría del paquete y APT

`postinst` instalaría su clave y fuente APT oficial con `Signed-By`, defaults y estado del repositorio; también contempla carga de un perfil AppArmor. `prerm` y `postrm` gestionan retirada de perfil/repositorio. Se leyeron completos; **no se ejecutaron**. En el invitado faltan las herramientas/ABI AppArmor de la rama de carga. [Scripts y permisos](validation/mestry-chatgpt-20261020T071932Z/static_control_audit.json).

Launcher: `/usr/bin/chatgpt` → `/usr/lib/chatgpt/codex-launcher` → `ChatGPT`. ASAR declara versión 26.1013.40934 y Electron 42.3.0 en metadatos. Seis ELF relevantes AArch64 revisados, sin ejecutar `ldd` sobre ellos. Los requisitos GLIBC inspeccionados no exceden la 2.41 disponible. [Binarios](validation/mestry-chatgpt-20261020T071932Z/static_binary_audit.json).

APT resolvió **119 paquetes nuevos** —ChatGPT + 118 dependencias—, **1 actualización** de `liblzma5` a `5.8.1-1+deb13u2`, **0 eliminaciones**, descarga adicional **80,9 MB** y espacio adicional **2.054 MB**, sin contar mantener el instalador. La propuesta incluye GTK, D-Bus, Mesa/LLVM, Vulkan, udev y systemd; no XFCE. Cadena comprobada de TPM: `libtss2-tcti-device0t64` → `tpm-udev` → `udev` → proveedor de sysusers, para el que APT selecciona systemd. Hay alternativas en algunas dependencias; no se afirma que esta sea la única resolución mínima. [Lista completa propuesta](validation/mestry-chatgpt-20261020T071932Z/apt_planned_packages.tsv).

**Aplicado: cero paquetes nuevos/actualizados.** Las 139 entradas instaladas conservan idéntico nombre, versión, arquitectura y estado. No se añadió el repo OpenAI. No hay bus D-Bus de sesión o keyring funcional demostrado; las referencias del Codex a fallback de keyring hacia archivos requieren revisión antes de credenciales.

### Bloqueo, seguridad y límites

Kernel real **`5.15.DRIVE_ID_04_EXAMPLE`**. El acceso ADB sin root permitió leer `/proc/config.gz`: `CONFIG_NAMESPACES=y`, **`# CONFIG_USER_NS is not set`**, **`# CONFIG_PID_NS is not set`**, `CONFIG_NET_NS=y`, seccomp/filter y SELinux habilitados. La syscall nativa `unshare(CLONE_NEWUSER)` falla **EINVAL**; el retorno 0 de la utilidad bajo PRoot no crea el namespace ni cambia el UID Android **10348**, con capacidades efectivas **0**.

El paquete no contiene helper `chrome-sandbox` SUID; `/data` es `nosuid`. Instalar un userland, `bubblewrap` o un desktop no añade esas funciones al kernel. Se considera bloqueo de prerrequisitos y **no** un resultado de apertura o de fallo de la app ejecutada. Los strings estáticos de Chromium no son stderr de arranque. `Seccomp: 2` heredado de Android/PRoot no se presenta como protección del renderer.

**Renderer no validado; helper de comandos no ejecutado; autenticación/proyectos/comandos controlados no probados.** No se empleó `--no-sandbox`, se omitieron protecciones ni se tocaron SELinux, permisos privilegiados, bootloader o particiones. No se reinició ni se habilitó acceso público. La fase 3 no se ejecuta por la condición explícita de parada de la fase 2.

### Recursos, recuperación y siguiente propuesta

[Métricas completas](validation/mestry-chatgpt-20261020T071932Z/resources_summary.json): mediana RAM disponible **3,317 → 3,247 GiB**, almacenamiento libre **212,079 → 212,082 GiB**, batería **24,0 → 24,2 °C** y estado térmico **0 → 0**. No se atribuye la variación de Android a ChatGPT, que no se lanzó; **PSS/RAM de la app no medido**. Rootfs final **221,87 MiB**, contenido dentro de PREFIX; PREFIX **428,06 → 428,09 MiB**, home sin cambios. La invocación inicial de `du` deduplicó subdirectorios dentro de su padre y no produjo una medida inicial independiente del rootfs; se corrigió en la medición final con invocaciones separadas.

El staging ocupó **458,07 MiB asignados** y se retiró con guardas de ruta/no-symlink/hash, conservando el original en WSL. **No hace falta desinstalar paquetes.** No usar `autoremove` sobre la transacción propuesta ni borrar Debian/Termux para revertir. SSH/X11/Boot conservan sus scripts y hashes; display :1 activo, TCP 6001 rechazado por loopback IPv4/IPv6. Boot tras reinicio continúa pendiente.

El [informe](CHATGPT_LINUX_ARM64_REPORT.md) deja una propuesta concreta **sin ejecutar y pendiente de autorización**: extraer únicamente el Codex estático incluido, verificar su hash y ejecutar su diagnóstico de sandbox como `mestry` con un fixture desechable, sin credenciales, modelo, dependencias o bypass. Un retorno 0 requeriría demostrar denegación efectiva sobre un sentinel sintético; no se aceptaría por sí solo. Se detiene el trabajo operativo antes de ese experimento y de cualquier login.

La [comprobación local final](validation/mestry-chatgpt-20261020T071932Z/final_validation.json), p20, revisa hashes de evidencia, inventarios, sintaxis de los scripts y enlaces documentales; no instala paquetes, se conecta al teléfono ni ejecuta el código auditado.

## Sesión `mestry-sandbox-20261020T080841Z` — EXP05, sandbox del Codex incluido

**2026-10-20. Resultado: BLOQUEADO EN LA CONFIGURACIÓN ACTUAL.** El usuario autorizó únicamente un diagnóstico controlado del Codex incluido, con datos sintéticos, sin instalar la aplicación/dependencias, usar cuentas/modelos/repositorios personales, desactivar protecciones, obtener privilegios Android o modificar el kernel. Se completó esa prueba y se detuvo antes de nuevas instalaciones. [Informe específico](CODEX_SANDBOX_REPORT.md), [dictamen](validation/mestry-sandbox-20261020T080841Z/sandbox_test_summary.json), [comandos exactos y retornos](validation/mestry-sandbox-20261020T080841Z/commands.md), [manifest](validation/mestry-sandbox-20261020T080841Z/manifest.json).

### Identidad y preparación

Se reutilizó el `.deb` oficial **26.1013.40934 ARM64**, SHA-256 `9ab2cbbaf33cebeaa1e06eb5cab78128936f927a0d97bf00e40694e5f31c629b`, comprobándolo de nuevo. Su miembro `resources/codex` conserva SHA-256 **`5412ef3ceacc22a058cf19382dbfd85305e405f7275ac36300375998b2ad3fc3`** e informa **`codex-cli 0.163.0-alpha.10.2`**. No se reemplazó por una CLI de npm, otro build o un paquete comunitario. [Procedencia](validation/mestry-sandbox-20261020T080841Z/binary_provenance.json).

El caso temporal `$PREFIX/tmp/mestry-sandbox-20261020T080841Z` tuvo binarios propios, home nuevo, configuración `read-only`, tmp/var-tmp, workspace y sentinel sintéticos. Los binds de home/tmp no expusieron home SSH, proyectos o cookies X11. Cada Codex usó `env -i` con una lista explícita; el default `MOZ_FAKE_NO_SANDBOX=1` mostrado por el ensamblador PRoot-Distro **no fue heredado por Codex**. No había `auth.json` en ese home. **Los binds no se trataron como aislamiento de seguridad.**

La primera consulta del sandbox falló por falta de `bwrap` del sistema y de `codex-resources/bwrap` adyacente. Se preparó **solo un ejecutable temporal** de **bubblewrap 0.12.0-1~deb13u1**, ARM64, desde el repositorio oficial Debian y contra el SHA-256 de los metadatos APT existentes; **no se instaló ningún paquete ni dependencia**, ni se ejecutaron scripts de instalación. Paquete 54.820 bytes, SHA-256 **`d1ac1d0d81c815fc15842b9f04fdf414830ed14a0a602bf6344740f90bb36c00`**; ejecutable **`b3b829e18a7d43ee589dc37e351cb9480ff7301b493d8227b8c754294638b976`**, modo de prueba 0500, sin SUID. Sus bibliotecas ya estaban instaladas. El anclaje es el índice APT existente de fuentes firmadas; no se verificó un InRelease nuevo en EXP05. [Control, origen y límite](validation/mestry-sandbox-20261020T080841Z/bubblewrap_provenance.json).

Un wrapper registró argumentos con separador NUL y ejecutó obligatoriamente ese `bwrap` con los mismos argumentos; no añadió una ruta sin sandbox. La captura mostró raíz de solo lectura, red restringida, `--unshare-user/pid/ipc/net`, `/proc` propio, `--cap-drop ALL` y reentrada a `codex-linux-sandbox` con **`--apply-seccomp-then-exec`**. Esa segunda etapa **no se alcanzó**. [Argumentos reales y perfil](validation/mestry-sandbox-20261020T080841Z/actual_codex_sandbox_argv.json).

### Registro de comandos y errores

| Probe | Operación / resultado |
|---|---|
| r01 | ADB/config real: USER_NS, PID_NS y SECURITY_LANDLOCK **no habilitados**; seccomp/filter y SELinux sí. Sin root |
| r02 | SSH/UID/capacidades/montajes, ayuda de PRoot y recursos; scripts operativos sin cambios |
| r03 | Hashes del paquete/binario, fuentes oficiales y referencias estáticas del helper; **sin ejecución** |
| r04 | Copia únicamente a fixture temporal, home/config/input/sentinel sintéticos y symlink del helper interno |
| r05 | **rc=101**: versión Codex funciona; consulta posterior hace panic porque no hay `bwrap` ni recurso adyacente |
| r06 | Ayuda del helper interno **rc=0**, metadatos de bubblewrap y bibliotecas existentes; sin descargar/instalar en el teléfono |
| r07 | Descarga/verificación/extracción en WSL y copia solo del helper a fixture; no `dpkg -i` ni APT install |
| r08 | Versión bubblewrap funciona; **rc=1**, falla la preparación de `/dev`. La sintaxis anticipada `sandbox linux --help` pasó `linux` como payload; no llegó a ejecutarlo |
| r09 | **rc=1**, guarda previa detectó ruta incompleta del rootfs antes de ejecutar el helper nativo; se corrigió al path ya inspeccionado con `/rootfs` |
| r10 | Ayuda correcta `codex sandbox --help` y payload válido de impresión: **rc=1 del sandbox**, stdout vacío y error `/dev/null`/fd. **No marcador, no prueba de escritura** |
| r11 | Arranque nativo, fuera de PRoot, de `bwrap --version` mediante glibc existente y NoNewPrivs=1: **−31/SIGSYS**, antes del payload; probe termina 1 por su guarda. No se alteró seccomp para continuar |
| r12 | **rc=1** de colección: asumía errno EINVAL para ambas namespaces; PID devolvió un rechazo distinto. No fue un éxito del kernel ni una razón para continuar ejecutando payloads |
| r13 | Observaciones Bionic nativas: USER **EINVAL**, PID **EPERM**; input/sentinel íntegros, `auth.json` ausente, inventario y archivos temporales; sin nuevos tests Codex/bwrap |
| r14 | **rc=1**, derivación local comparaba el orden textual de dos inventarios equivalentes; corregido en r17, sin cambios remotos |
| r17 | Comparación canónica: **139 paquetes idénticos**; dictamen y argumentos efectivos archivados. Se ejecutó antes de la limpieza r15, según timestamps |
| r15 | Retirada guardada exclusivamente del fixture temporal; versiones originales conservadas en WSL; SSH/X11/Boot sin cambios |
| r16 | ADB final: SELinux Enforcing, Verified Boot green, flash bloqueado, RAM Plus 8192, estado térmico 0 |
| r18 | Consulta documental oficial de app-server y resumen local de recursos; no se inició servidor, login o modelo |

Scripts, stdout/stderr, tiempos y hashes de **todas** estas operaciones están en el índice/manifest. No se ocultaron los probes fallidos ni se cambiaron sus retornos para declarar éxito.

### Resultado técnico y límites

En este binario, la interfaz correcta es **`codex sandbox [COMMAND]`**. Prueba válida, con timeout, `mestry`, home sintético y perfil read-only:

```text
codex sandbox -- /usr/bin/printf 'MESTRY_CODEX_SANDBOX_PAYLOAD_REACHED\n'
# Sandbox rc=1, stdout vacío:
bwrap: Can't bind mount /dev/null on null: readlink(/proc/self/fd/N) for "/proc/self/fd/5": Invalid argument
```

El payload solo habría impreso después de preparar el sandbox. **No se ejecutó.** No se intentaron escrituras permitidas o denegadas; el sentinel íntegro **no se cuenta como denegación efectiva**. El filtro seccomp de Codex tampoco quedó validado; el filtro Android heredado no lo sustituye.

Fuera de PRoot, procesos breves Bionic/Termux con UID real **10348** observaron `unshare(CLONE_NEWUSER)` → **−1/EINVAL** y `unshare(CLONE_NEWPID)` → **−1/EPERM**. La configuración real confirma ausencia de ambos y de Landlock; el errno PID por sí solo no identifica su causa. El intento nativo glibc recibió SIGSYS antes de emitir versión; **no se identificó su syscall causante** ni se atribuye exclusivamente a bubblewrap. No se usó un bypass para obtener más información.

**Bloqueo definitivo para esta ruta bubblewrap sin privilegios en el kernel actual.** Corregir el error de fd/montaje de PRoot no añadiría USER_NS/PID_NS. El renderer gráfico es independiente y **no se ejecutó ni validó**. La GUI oficial sigue sin instalar y no se introdujeron credenciales. No se usaron flags/modos para omitir sandboxes, root Android, modificaciones de kernel/bootloader, desactivación de SELinux/seccomp, reinicios o listeners nuevos.

Todo estado de bootstrap preparado se dirigió al fixture mediante home/tmp y entorno controlados. PRoot no ofrece una barrera que certifique confinamiento; **no se realizó una traza exhaustiva de escrituras de todo Android**. El payload no tuvo escrituras ni llegó a ejecutarse. Se conservan [archivos/observaciones](validation/mestry-sandbox-20261020T080841Z/final_fixture_observations.json) y [paquetes antes](validation/mestry-sandbox-20261020T080841Z/packages_before.tsv)/[después](validation/mestry-sandbox-20261020T080841Z/packages_after.tsv).

### Cierre y recomendación

Fixture de prueba retirado, sin procesos Codex de prueba pendientes. **0 paquetes instalados/actualizados**, 139 existentes idénticos; no se instalaron app, bubblewrap o las 119 dependencias. SSH, helper Debian, X11 y Boot mantienen hashes; X11 continúa activo. Reinicio/Boot sigue pendiente.

[Recursos](validation/mestry-sandbox-20261020T080841Z/resources_summary.json): muestras puntuales de RAM disponible **3,194 → 3,139 GiB**, libre **212,066 → 212,078 GiB**, batería **23,8 → 23,9 °C**, térmico **0 → 0**. Sin benchmark, carga sostenida, renderer o PSS representativo de la app; no se atribuye a Codex la variación de Android.

Se cierra la ruta **app oficial/PRoot en esta configuración**. La siguiente recomendación es **investigar app-server + UI móvil + ejecutor separado con permisos controlados**, sin asumir que un cambio de frontend cura el sandbox. Hay que demostrar que shell/procesos/archivos no puedan evadir ese ejecutor; la documentación oficial identifica RPC de ejecución fuera del sandbox. Esa investigación, instalaciones, servidor, login y modelo **no se ejecutaron** en EXP05. [Informe y puertas concretas](CODEX_SANDBOX_REPORT.md).

La [comprobación final local de EXP05](validation/mestry-sandbox-20261020T080841Z/final_validation.json), r19, revisa hashes, scripts, enlaces, inventarios y límites del dictamen. No vuelve a ejecutar Codex/bubblewrap ni contacta con el teléfono.

## Continuación del 20 de octubre, 19:33–19:37 UTC — recomprobación de acceso y Debian

**Resultado: criterio Debian mínimo confirmado de nuevo; SSH y ADB USB disponibles.** Se contrastó el hilo recuperado con el workspace: EXP02 ya tenía cierre a las 04:45 UTC y existen las entregas posteriores EXP03–EXP05. Se preservaron esos avances y no se repitieron instalaciones ni diagnósticos del sandbox. El alcance de esta continuación fue comprobar acceso, Debian y estados Android de lectura, y registrar el resultado. No se reinició el teléfono, recargó SSH, lanzó o detuvo X11 ni se cambiaron paquetes, aplicaciones, permisos o ajustes.

Evidencia de esta recomprobación: [índice y alcance](validation/mestry-debian13-recheck-20261020T193723Z/README.md), [comandos exactos, resultados y errores](validation/mestry-debian13-recheck-20261020T193723Z/commands.md), [manifest](validation/mestry-debian13-recheck-20261020T193723Z/manifest.json), [resumen estructurado](validation/mestry-debian13-recheck-20261020T193723Z/summary.json). La consulta SSH previa a las 19:33 UTC se añadió al anexo anterior con nombre propio, [s21_final_ssh_and_inventory](validation/mestry-debian13-20261020T040726Z/s21_final_ssh_and_inventory.record.json); sus salidas no sustituyen los cierres históricos s20/s21 de las 04:39 UTC.

| Comprobación | Resultado actual y límite |
|---|---|
| SSH | Conexión nueva por clave con `BatchMode=yes`, sin contraseña, agente ni multiplexación. `sshd -T` mantiene `AuthenticationMethods publickey`, contraseña y teclado interactivo desactivados; daemon PID 2975. Configuración principal y `authorized_keys` conservados |
| Comando WSL → Debian | **Código 0**, `MESTRY_DEBIAN13_CHECK=PASS`, a las **19:37:35 UTC**. Debian **13.7/trixie**, **arm64**, usuario invitado `mestry` 10349, UID real Android **10348**, capacidades efectivas **0** |
| APT y red | APT **3.0.3** ejecutable y metadata HTTPS legible; DNS y HTTPS con certificado verificado, **200**. No se refrescaron índices ni se instalaron paquetes en esta continuación; los `apt-get update` reales están registrados en EXP02 |
| Archivos y procesos | Round trip UTF-8 y creación/espera de proceso hijo correctos; archivos temporales del check eliminados |
| ADB USB | Enumeración de un SM-S918B autorizado y shell **UID 2000**. El fallo previo de selección se resolvió al volver a consultar, sin modificar configuración; causa no determinada |
| Batería y seguridad | Termux/Boot en excepciones Doze, segundo plano permitido y notificaciones concedidas. Wakelock Termux presente. RAM Plus **8192**, protección **80 %**, Verified Boot **green**, flash **locked**, ADB inalámbrico **0** |
| Aplicaciones | **28 deshabilitadas**, conjunto idéntico al que ya existía al iniciar EXP03. La diferencia frente a las 23 de EXP02 es histórica y no se atribuye a esta continuación. No se deshabilitó ninguna app |
| Recursos globales a 19:33 UTC | **3,016 GiB de RAM disponible**, **212,031 GiB libres**. Había procesos preexistentes Termux:X11 y xterm; no es una nueva medición del coste incremental de Debian mínimo |

Comando ejecutado por c01 desde WSL, con identidad pública exclusiva y comprobación de host conservada:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 \
  -o ControlMaster=no -o ControlPath=none \
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no \
  -o KbdInteractiveAuthentication=no -o IdentityAgent=none \
  mestry-s23 '$HOME/bin/mestry-debian /usr/local/bin/mestry-check'
```

**Error conservado:** el intento `s20_final_android_guards` terminó localmente con código 1 y `Expected exactly one authorized SM-S918B.` antes de ejecutar su script en Android. El logger guarda el script antes de seleccionar el dispositivo y, en ese caso, no genera registro de ejecución. Se conserva el [script preparado, no ejecutado](validation/mestry-debian13-20261020T040726Z/s20_final_android_guards.sh) y la observación en `summary.json`; no se inventaron stdout Android ni hora exacta del fallo. c02 y c03 posteriores terminaron con código 0 y demostraron de nuevo el canal USB. No se confundió el fallo de enumeración con un fallo de Debian o de autenticación SSH.

La batería ya fue revisada manualmente por el usuario; no se piden nuevos cambios One UI. Boot mantiene su único hook SSH. El ensayo de reinicio/primer desbloqueo y la recuperación totalmente automática siguen pendientes; las instrucciones y sus límites están en la entrega EXP02 anterior. Esta continuación no ejecutó la siguiente rama propuesta en EXP05. Se detiene tras la comprobación y la documentación.

## Sesión `mestry-horus-20261020T194336Z` — EXP06, Horus y Codex local

**COMPLETADA — PASS a 20:22 UTC: Horus/Alpine y Codex CLI autenticado, dos tareas sintéticas y cinco tests independientes en el S23.** El usuario aclara que Debian/X11 ya están verificados y solicita avanzar con Horus oficial. Autoriza instalar el APK verificado desde WSL, inicializar Alpine y usar la instalación integrada de Codex. Acepta expresamente **`--sandbox danger-full-access` dentro de Horus**. Se pausó ante el login y el usuario lo completó; autorizó después las dos tareas concretas. Las secciones intermedias conservan los estados pendientes de su momento. No repetir pruebas Debian/X11 ni modificar sus instalaciones, Termux o SSH; acceso remoto Horus desactivado, sin `horus tune`, cambios globales o reinicio. [Informe final](HORUS_REPORT.md).

Repositorio indicado: [scarif-labs/horus](https://github.com/scarif-labs/horus). Evidencia de ejecución: [manifest](validation/mestry-horus-20261020T194336Z/manifest.json), [comandos exactos y stdout/stderr](validation/mestry-horus-20261020T194336Z/commands.md). Los APK y el código fuente descargado se conservan en caché de WSL fuera del proyecto; no se copian credenciales de otras instalaciones.

### Estado previo

h01 consultó metadata oficial GitHub: última release estable **v1.0.4**, publicada **2026-10-13T04:59:53Z**, no prerelease. El README de main anuncia 1.1.0 pendiente de la cola F-Droid; no se elige main ni la prerelease de rootfs Debian. El APK estable es `horus-1.0.4.apk`, 8.562.827 bytes, SHA-256 anunciado `bf67340c4dd8321636c158902d0bf7b5a4684a23eae982d0026d45e348cb3430`, certificado F-Droid anunciado `311e3d58a6f92b2704aff6fabb5ad2f1ceddfe8b4bda2ed4dafeb72819b7112c`. La publicación de esos valores no sustituye su verificación real, registrada por separado antes de instalar. [Release estable](https://github.com/scarif-labs/horus/releases/tag/v1.0.4).

h02 confirmó ADB USB ordinario UID 2000, SM-S918B, Android 16/API 36, ARM64; Horus aún no instalado. Termux, Boot y X11 presentes. Línea base a **19:44:28 UTC**, USB conectado, batería 80 %: `MemAvailable=3165852 KiB` (**3,019 GiB**), datos libres `222323388 KiB` (**212,024 GiB**), estado térmico **0**, sensor AP **22,4 °C**, batería **21,2 °C**, piel **24,6 °C**. Temperatura de batería corroborada en `dumpsys battery`; no se equipara a temperatura CPU. El teléfono estaba desbloqueado y con F-Droid en primer plano. No se abrió Debian ni se repitió su check.

### APK verificado e instalado

h03 descargó el APK oficial y comprobó **tamaño y SHA-256 contra el digest del asset GitHub**. Descargó además la copia de **F-Droid `com.scariflabs.horus_5.apk`**: su SHA-256 es idéntico. `apksigner verify --verbose --print-certs` pasó y el certificado SHA-256 coincide con el publicado en la release. `aapt` confirmó paquete **`com.scariflabs.horus`**, versión **1.0.4/code 5**, ARM64, minSdk 24/targetSdk 36; sin `sharedUserId` ni `debuggable`. Fuente fijada al commit de v1.0.4 **`2f8f8a2faebd3d0fbd11dd83340bdcfbac437369`**. [Verificación y comandos](validation/mestry-horus-20261020T194336Z/apk_verified.json). La firma y la identidad entre ambos distribuidores están verificadas; no se realizó una compilación reproducible propia ni se verificó la firma PGP opcional.

h04 ejecutó `adb.exe -t ID install --no-incremental APK_VERIFICADO`: **Success**. Instalación nueva, sin reemplazo, `-g`, flags de evasión ni cambio de políticas. Android no pidió confirmación adicional para este ADB ya autorizado. `am start -W ... com.scariflabs.horus/.MainActivity` informó **Status ok/COLD** y mostró la bienvenida. PackageManager confirma UID Android propio **10350**, distinto de Termux; el APK no es debuggable. La captura de bienvenida y los binarios permanecen en caché fuera del proyecto; [jerarquía inicial de UI](validation/mestry-horus-20261020T194336Z/welcome_ui.xml).

La consulta de lectura `content call --uri content://com.scariflabs.horus.remote --method status` devolvió **`enabled=false`, `state=stopped`, `keys=0`, `configured=false`**. No se llamó a `pair`, `start`, `stop`, al CLI de Horus ni a `horus tune`. El puerto 8022 es solo el configurado para un eventual servidor, **no evidencia un listener Horus activo**. El SSH de Termux no se tocó.

### Intervención local y estado pendiente

h05 preparó pulsar `welcome-continue` usando la UI observada de nuevo, pero el guard no encontró ese botón en la pantalla actual y terminó con **1 / `Do not tap an unobserved screen`**. **No envió el tap** ni cambió el asistente. No se atribuye este resultado a fallo de Alpine. Se solicitó al usuario completar el asistente real: crear su contraseña local privadamente, confirmar notificaciones y batería sin restricciones solo para Horus y llegar a la pantalla principal, manteniendo remoto apagado. La contraseña no se pidió en el chat, no se inyectó y no se capturará la pantalla mientras la escribe. A las 19:48:53 UTC, `configured=false`: finalización del asistente aún no confirmada.

h07 revisó únicamente el código fijado de la release, sin ejecutarlo: rootfs Alpine **3.24.0/aarch64**, SHA-256 fijado `4b8cd66a6688b2a87276c39843ed89c3a06d9534fc6a5823c586aff2696c1f2a`; botón Codex instala **`@openai/codex` desde npm** y prepara su home. El wrapper añade `--sandbox danger-full-access --no-daemon`, sin cambiar automáticamente la política de prompts. Remoto requiere una marca de habilitación ausente en instalaciones nuevas. [Revisión estática](validation/mestry-horus-20261020T194336Z/source_review.json). El campo `local_password` de ese resumen describe el procedimiento previsto, **no acredita que la contraseña ya se haya creado**; la evidencia del estado real es la consulta `configured` y la confirmación del usuario.

### Medición inicial, todavía sin Codex

h06 tomó tres muestras **19:48:53–19:49:04 UTC**. Solo aparecía el proceso UI Horus PID 28780; no había proceso `:terminal` ni Codex en esa lectura. PSS UI **55.560 / 54.492 / 54.423 KiB** (**54,26 / 53,21 / 53,15 MiB**); esta cifra no incluye un entorno Alpine/Codex en ejecución. RAM global disponible **2,970 / 2,965 / 2,970 GiB**. Estado térmico **0**, AP **22,5–23,2 °C**, batería **21,4 °C**, piel **24,7 °C**. USB conectado y batería al 80 %; no es una medida de consumo eléctrico.

`exit-info` registra únicamente una salida **EXIT_SELF/status 0** del arranque optimizado Samsung SPEG a las 19:47:08 UTC; no se interpreta como crash o prueba de estabilidad de Codex. El PID UI posterior permaneció en las tres muestras. No se valida aún persistencia con pantalla apagada, trabajo de proyecto ni funcionamiento con el PC apagado. El criterio de éxito completo sigue **PENDIENTE**.

### Asistente terminado y arranque real de Codex

h08 consultó únicamente el estado y los IDs de controles: Linux **done**, herramientas **working**, perfil **waiting**, a las **19:51:21 UTC**. No exportó texto de campos, terminal o contraseñas al proyecto. Después h09 confirmó **`configured=true`, `batteryUnrestricted=true`, remoto apagado** y el proceso `:terminal` de Horus. El usuario respondió **«Asistente terminado; estoy en la pantalla principal»**; se registra como confirmación de la intervención local. Durante h09 apareció también un proceso `gh`; el agente no inició login GitHub ni leyó sus credenciales, y la pantalla posterior seguía mostrando «Login to GitHub».

h10 buscó el botón Codex y terminó con **10**, `CODEX_TILE_NOT_VISIBLE`, sin enviar taps. h11 confirmó Horus en primer plano. La inspección visual local posterior mostró instalación integrada Codex al 30 %; no se atribuye ese primer intento a h10. h12 observó de nuevo la pantalla principal. Las capturas se guardaron en caché fuera del proyecto, sin incorporarlas a Git.

Tras la confirmación del usuario, h13 sí encontró **`metro-harness-codex`** y pulsó su centro observado. El resultado fue el **selector de proyecto**, no un arranque de CLI todavía. La frase de éxito del script h13 describe la solicitud de apertura del botón; la observación h15 delimita el resultado real. No había proyectos locales. h16 eligió la pestaña nueva, campo de carpeta vacía y nombre **`mestry-horus-smoke`**, y envió Enter. No escribió archivos de código, clonó repositorios ni hizo una petición al modelo. El flujo de Horus prepara el directorio antes de invocar Codex; su contenido y pruebas se comprobarán después del login autorizado.

h17 observó el instalador integrado: workspace y paquetes del sistema listos, Codex instalándose. h18 registró el relevo a procesos persistentes **PRoot 31611 → zsh 31626 → node 31846 → codex 31853**, todos con **UID Android 10350**. El servicio terminal es **30564** y su padre Android **1706**; no descienden de una shell ADB/SSH de WSL. No se instaló Codex con un comando npm manual del operador: lo ejecutó el mecanismo de Horus. La versión exacta de Codex aún no se consultó y no se infiere de npm latest.

h19 ocultó únicamente el teclado visible, condicionado por `mInputShown=true`, para inspeccionar los controles. No encontró overlay de instalación que abrir: la **CLI ya había arrancado** y mostraba bienvenida y **Finish signing in via your browser**, junto a **`link_unavailable`** en Horus. Se **detuvo inmediatamente el envío de acciones** al llegar a este paso. La imagen de inspección permanece en caché fuera del proyecto porque incluye una URL OAuth de sesión; no se copió esa URL, código o token a la evidencia. No se eligió una cuenta ni se introdujeron credenciales.

Se pidió al usuario completar el login y confirmar la autorización de **dos tareas concretas**: crear `saludo.py`, `test_saludo.py`, `README.md` y después modificar la función y ejecutar pruebas, siempre en el proyecto sintético y sin instalar paquetes nuevos. Ante su consulta sobre evitar escribir la URL, se indicó la tecla **c** del flujo de navegador para copiar y se proporcionó el [enlace corto de código de dispositivo](https://auth.openai.com/codex/device), verificado en la [documentación oficial](https://learn.chatgpt.com/docs/app-server). Se explicó ESC → Sign in with Device Code si `link_unavailable` impide abrir navegador. El login y la autorización del trabajo siguen pendientes de confirmación. No se inspecciona la pantalla mientras el usuario introduce sus credenciales.

### Recursos al arrancar Codex y límites actuales

h14 midió UI + servicio **sin sesión invitada activa** a las 19:56 UTC: PSS agregado completo de esos dos PIDs **122,62–130,56 MiB**. No se atribuye ese número a Codex. h18 midió la transición instalación → CLI a **19:58:41–19:58:56 UTC**: PSS de procesos medidos **152,25 / 249,38 / 277,25 MiB**, con `tail`, `sleep` o `git` que terminaron entre enumerar y consultar. El resumen marca explícitamente **`pss_sum_complete_for_selected_pids=false`**; son sumas parciales de muestras, **no consumo total ni pico máximo**. [Datos por PID](validation/mestry-horus-20261020T194336Z/codex_install_resources.json).

Memoria global disponible **2,780 / 2,985 / 2,939 GiB**; térmico **0**, AP **26,9–28,3 °C**, batería **22,3 °C**, piel **26,0–26,1 °C**. `exit-info` no añadió crashes o ANR en la lectura de cierre h18, aparte del EXIT_SELF SPEG ya explicado. Esto acredita un arranque inicial, no estabilidad bajo inferencia, pantalla apagada, 24/7 o PC apagado.

El `sshd` existente sigue en **PID 2975**, UID Termux 10348. Horus permanece con remoto **false/stopped/0 claves**; no se crearon forwards ADB, listener Horus o puente PC. El PC descarga/instala el APK, envía interacción UI y observa recursos; los procesos Alpine/Codex se ejecutan en el teléfono. **Todavía falta demostrar una tarea completa de archivos y comandos**, tras el login y su autorización. Debian, Termux/X11 y SSH no se modificaron; no hubo `horus tune`, reinicio, root, cambios globales o ampliación a otra fase.

### Cierre: autenticación, dos tareas y verificación independiente

El usuario confirmó **«listo, sesion iniciada en codex»** y después **«Sí, autorizo las dos tareas sintéticas»**. h20 observó el prompt autenticado **OpenAI Codex v0.163.0**, proyecto `/workspace/projects/mestry-horus-smoke` y modelo **GPT-6.1-Sol default**; no se cambió modelo. h26 clasificó los argumentos del PID **31853** sin conservar la línea completa: **`--sandbox danger-full-access` y `--no-daemon` presentes**, sin flag `--ask-for-approval never` añadido. No se afirma la política efectiva de todas las capas de configuración a partir de esa ausencia.

| Ejecución | Evidencia real |
|---|---|
| h22 / h24 | Primera instrucción en el Codex del teléfono: crear `saludo.py`, `test_saludo.py`, `README.md`; el agente informó dos pruebas correctas, trabajo de 18 s según TUI. [Prompt exacto](validation/mestry-horus-20261020T194336Z/task01_create_prompt.txt) |
| h25 | Explorador nativo Horus: exactamente tres archivos; exportación por MediaStore a `Download/Horus`, lectura ADB de esas copias y hashes. [Primera versión](validation/mestry-horus-20261020T194336Z/task01_files_verified.json). WSL no ejecutó el código |
| h27 / h29 | Segunda instrucción: aplicar `strip()`, rechazar vacío/solo espacios con `ValueError`, conservar dos tests y añadir tres; actualizar README. El agente informó cinco tests correctos, 19 s según TUI. [Prompt exacto](validation/mestry-horus-20261020T194336Z/task02_modify_prompt.txt) |
| h30 | Segunda exportación de exactamente esos tres archivos. Todos cambiaron; [hashes antes/después](validation/mestry-horus-20261020T194336Z/project_changes.json), [segunda versión](validation/mestry-horus-20261020T194336Z/task02_files_verified.json). Los tiempos de TUI no constituyen un benchmark controlado |
| h37 / h38 | Comprobación desde **Bare terminal de Horus**, sin modelo: `python3 -B -m unittest -v`, **Ran 5 tests / OK / salida 0**; versión Alpine **3.24.0**, arquitectura **aarch64**, Python **3.14.8**, UID invitado **1000**, UID real **10350**, CapEff **0**. Hashes iguales a la segunda exportación. [Salida producida en el S23](validation/mestry-horus-20261020T194336Z/phone_validation_final_files/MESTRY_VALIDATION.txt) |
| h38 / h39 | Salida de la shell temporal y reanudación de **la misma sesión Codex `s-1792526266502-3`**, con PID **31853** conservado. No se reinició la CLI para pasar esta comprobación; tampoco el teléfono |

El cuarto archivo `MESTRY_VALIDATION.txt` lo creó el verificador dentro del proyecto, después de las dos tareas. h38 exportó solo los cuatro archivos sintéticos y conservó sus bytes en `phone_validation_final_files`. No se leyó/exportó un home de credenciales. Las pruebas se ejecutaron en Alpine en el S23; el Python de WSL solo manejó metadata, hashes, diffs y documentación. La inferencia de Codex utiliza la cuenta/servicio del proveedor; no se descargó un modelo local ni se desplegó un ejecutor en PC.

**Incidencias de instrumentación conservadas:** h31/h32 devolvieron 0 al enviar una línea larga a la terminal, pero la entrada quedó truncada y dejó una continuación de shell; eso **no acredita ejecución del comando**. Además se eliminó el formato literal `%s` de la línea porque `input text` lo transforma en espacio. h33 terminó con **1** al no encontrar el cuarto archivo esperado; su guard impidió exportar un resultado inexistente. h34 observó la continuación. El acorde Ctrl+C de h35 no produjo el estado limpio esperado: los primeros comandos continuaron en el buffer y apareció `zsh: no such event: 0`; las órdenes posteriores se ejecutaron en el directorio padre, con errores de archivos ausentes. No se contó como fallo de los tests del proyecto ni como PASS. h36 confirmó explícitamente `pwd`; h37 repitió con líneas cortas en el directorio correcto, eliminó solo el archivo de verificación mal ubicado que había creado el operador y produjo el resultado válido. No se modificó Horus o Android para resolverlo. Los scripts completos y stderr están conservados, incluidos los intentos fallidos.

### Recursos finales, preservación y alcance logrado

h39, **20:21:54–20:22:11 UTC**, tres muestras completas de los diez PIDs observados de Horus: PSS **628,41 / 601,29 / 599,37 MiB**, mediana **601,29 MiB**. Incluye UI, servicio, PRoot, zsh, Node, Codex, tres hijos Node y Code Mode host. RAM disponible global **2,867 / 2,880 / 2,878 GiB**. Son lecturas **posteriores** a las tareas y no un pico de inferencia. [Datos originales](validation/mestry-horus-20261020T194336Z/final_resources.json).

Térmico **0**, AP **24,5–25,1 °C**, batería **22,9 °C**, piel **25,9 °C**. USB conectado, batería al 80 %. Datos libres **210,99 GiB**; la variación global de `df` no es un `du` exclusivo de Horus. Codex PID **31853** conservó **23 min 28 s**; UI **28780** y servicio **30564** también persistieron. `exit-info` no registró crash/ANR, solo el EXIT_SELF SPEG inicial. Esto es estabilidad inicial, sin prueba de reposo prolongado, reinicio o disponibilidad 24/7.

h40 confirma Termux/Boot/X11 conservados, Horus **1.0.4/code 5**, remoto **false/stopped/0 claves**, notificaciones y batería sin restricciones confirmadas después de la intervención del usuario. RAM Plus **8192**, protección de carga **80 %**, Verified Boot **green**, flash **locked**, ADB inalámbrico **0**. `sshd` permanece en **2975**. Sin root, `horus tune`, cambios globales, otras instalaciones/fases, datos personales o acceso remoto S25.

**Criterio mínimo cumplido:** Codex CLI, cambios de archivos y herramientas ejecutados en el S23, sin PC como host de ejecución. ADB sirvió para instalar, introducir instrucciones y observar/copiar evidencia. Entre el final de h22 y la siguiente consulta del teléfono transcurrieron unos 38 s; la primera tarea completó su trabajo sin más entrada del operador. No se apagó físicamente el PC ni se valida aún un observador/controlador S25. Horus queda con el proyecto probado y la sesión Codex abierta; los archivos/copies sintéticos se conservan para revisión. Las capturas sensibles permanecen en caché local privada fuera del proyecto, sin passwords, URL OAuth de sesión, códigos o tokens en la evidencia. [Resumen de aceptación](validation/mestry-horus-20261020T194336Z/summary.json). **Se detiene esta fase.**

Revisión documental final, solo WSL: h42 verificó los hashes/sintaxis/enlaces, pero devolvió 1 porque el patrón de secretos detectó su propia cadena literal `code_challenge=` en el script del escáner. No era una credencial. h43 corrigió el patrón para exigir un valor con longitud compatible, conservando h42 y su stdout; repitió la revisión de los archivos modificados. [Revisión final](validation/mestry-horus-20261020T194336Z/review.json), [huellas del anexo](validation/mestry-horus-20261020T194336Z/SHA256SUMS). No se contactó con el teléfono ni con la cuenta durante esa revisión.


## Sesión `mestry-s25-remote-20261020T215417Z` — EXP07, primer acceso desde S25

**Alcance autorizado:** preparar SSH S25 → Termux mediante Ed25519 exclusiva del S25, conservar WSL y revisar el remoto oficial Horus sin cambiar puertos antes de autorización. No se repitieron instalación, Debian, X11 ni el experimento Codex local. [Procedimiento completo y fases pendientes](S25_REMOTE_ACCESS.md); [comandos exactos, resultados y errores](validation/mestry-s25-remote-20261020T215417Z/commands.md).

**Resultado de este incremento:** clave pública `mestry-s25` recibida del usuario, validada como Ed25519 y añadida atómicamente a `authorized_keys`, preservando la clave WSL. Directorio 700, archivo 600. Huella S25 `SHA256:CONFIGURE_LOCAL_FINGERPRINT`; WSL `SHA256:CONFIGURE_LOCAL_FINGERPRINT`. Hash final `authorized_keys`: `31d62780157ee7714a7cc1f145d1825ccda9ab761eda38bf92fb492a8f1c7e59`. Respaldo privado Termux `~/.local/state/mestry/s25-key-20261020T221228Z/authorized_keys.before`. No se transfirió ni leyó ninguna clave privada. La primera respuesta contenía una clave truncada: no se usó; se pidió y verificó la línea completa.

**Red y errores reales:** `p01` agotó la conexión a la dirección anterior. ADB confirmó `10.211.130.70`; `p04` verificó su clave contra la ya conocida y autenticó con la identidad WSL, antes de actualizar el alias en `p05`. `p06` confirmó acceso nuevo por el alias. Al iniciar el alta, `p08` agotó conexión antes de ejecutar comandos; ADB `p09` confirmó el retorno del S23 a `192.0.2.15`, con el mismo daemon PID 2975. `p10` completó el alta en esa dirección. `p11` devolvió el alias WSL a **192.0.2.15:8022** y confirmó una conexión independiente con la clave WSL. Origen WSL observado en esa red: `192.0.2.13`. La confianza estricta del servidor se mantuvo; respaldos privados de configuración WSL en las rutas registradas en `p05/p11`. No se cambió la configuración de red del teléfono.

**Preservación:** sin cambios en puerto 8022, configuración de `sshd`, helper de arranque o Termux:Boot; sus hashes coinciden con la línea base. Sin reinicios, root, paquetes nuevos, RAM Plus, `horus tune`, puertos públicos ni proyectos personales. ADB de recuperación funciona como shell normal y resuelve la actividad local de Termux; no da acceso directo al home privado. Horus remoto se consultó en modo lectura: apagado, detenido, cero claves.

**Revisión `p07`:** Horus 1.0.4 del commit instalado fija Dropbear en `127.0.0.1:8022`; se solapa con el bind comodín real de Termux. Propuesta pendiente: migrar Termux a 8023 con recuperación ADB, escucha temporal paralela, rollback y actualización de Boot/WSL/S25, previa autorización. Emparejar por el provider oficial verifica la contraseña de Horus y también enciende el remoto: no se ejecutó. El usuario SSH `horus` y el harness `harness_codex` tienen homes distintos; compartir autenticación/historial o adjuntar la PTY de la app siguen sin verificar. No se instaló el CLI de escritorio Horus.

**Instrumentación:** `sshd -T` imprime mayúsculas; el primer filtro de `p04` no capturó sus campos y `p06` lo corrigió. `ss` de Termux no pudo enumerar sockets por restricciones de Android; ADB mostró las escuchas con advertencia parcial de netlink. Los intentos y errores se conservan.

**Punto de parada:** falta que el usuario conecte desde ConnectBot en el S25 a `u0_a348@192.0.2.15:8022`, seleccione `mestry-s25`, compare la huella del servidor y envíe la salida de `echo MESTRY_S25_TERMUX_OK; whoami; id; echo "$SSH_CONNECTION"`. No se acredita aún S25 → Termux ni fases 2–4. No solicitar/aplicar el cambio de puertos hasta completar esa primera prueba y preparar su reversión concreta. Se dejó el protocolo de apagado físico manual del PC en el informe; no se apagó ningún equipo.


### EXP07 — Corrección manual del perfil ConnectBot

Registro UTC: 2026-10-20T22:19:30.485372+00:00. El usuario aportó una captura del S25 con `Unable to resolve host "u0_a348@192.0.2.15:8022"` y destino mostrado con puerto adicional `:22`. Evidencia de que la cadena completa quedó guardada como hostname y el puerto conservó 22; no se alcanzó la autenticación SSH ni apareció todavía la confirmación de huella del servidor. Se corrigieron las instrucciones: servidor `192.0.2.15`, usuario `u0_a348`, puerto `8022`, clave `mestry-s25`, en campos separados. Se explicó que la huella del S23 aparece en el aviso de primera conexión válida, antes de aceptarla. Sin cambios de dispositivo, claves, puertos o servicios; sigue pendiente la prueba originada en S25. No se copió la captura personal al repositorio.


### EXP07 — Tres capturas del editor del host en el S25

Registro UTC: 2026-10-20T22:23:38.636929+00:00. Se revisaron las tres imágenes locales aportadas por el usuario, sin copiarlas ni modificarlas. El usuario ya tiene `Nombre de usuario = u0_a348`, `Puerto = 8022` y clave `mestry-s25`, pero el campo Host todavía contiene `192.0.2.15:8022`. Corrección indicada: Host debe contener únicamente `192.0.2.15`. Se detallaron los restantes campos: SSH, IP automático, contraseña vacía, perfil Default, ProxyJump Ninguno, agente y compresión apagados, shell y mantenerse conectado encendidos, cerrar al desconectar apagado y automatización sin acciones. La interfaz instalada sí muestra ProxyJump; solo se observa su disponibilidad, sin probarlo ni habilitarlo en fase 1. Primera conexión y huella de servidor siguen pendientes; sin operaciones sobre el teléfono ni cambios de puerto.


### EXP07 — Fase 1 confirmada y migración de puerto preparada

Registro UTC: 2026-10-20T22:39:41.420584+00:00. El usuario confirmó «funciono, me respondio bien a whoami» después de corregir el perfil ConnectBot. Se registra **PASS básico de S25 → Termux por confirmación del usuario**; no se inventa transcripción de `id`, IP de origen ni prueba con PC apagado. [Confirmación](validation/mestry-s25-port-plan-20261020T222743Z/phase1_user_confirmation.json).

Se preparó el siguiente incremento, sin cambiar puertos: [comandos y resultados](validation/mestry-s25-port-plan-20261020T222743Z/commands.md). `q01/q02` terminaron en 0 y revalidaron SSH por clave, ADB shell normal, actividad local Termux y escuchas. Dirección S23 `192.0.2.15`, daemon PID 2975, dos claves autorizadas y autenticación exclusivamente pública; Horus remoto `false/stopped/0 keys`. No apareció listener en 8023 en la observación ADB, con la advertencia de netlink ya conocida.

`q03` comprobó `sshd -t/-T -p 8023` sin crear sockets: la política prospectiva conserva clave pública y desactiva contraseña/teclado interactivo. La configuración real siguió mostrando Port 8022. Se verificó además el chequeo de huella por loopback 8022 y que no existe todavía el drop-in destino. **No equivale a haber probado SSH en 8023.**

`q04` preparó en Termux `~/.local/state/mestry/ssh-port-8023-20261020T222743Z`, carpeta 700, respaldos/configs 600 y scripts 700. Contiene configuración principal/drop-ins anteriores, helper/hook originales y propuestas de puerto/helper/Boot, reversión y temporizador inactivos. No se copiaron claves privadas ni se respaldó/restauró `authorized_keys`: solo se guardó su hash para conservar las dos autorizaciones. La sintaxis pasó localmente y con `sh -n` en Termux. Los hashes de configuración activa, helper, Boot y autorizaciones permanecen idénticos a `q01`. Sin recarga, puerto adicional, temporizador iniciado, emparejamiento Horus, instalaciones o reinicios.

Procedimiento concreto y código revisable: [tools/s23-ssh-port-plan](../tools/s23-ssh-port-plan/README.md). Tras autorización se abrirá primero un daemon temporal en 8023 con PID propio, manteniendo 8022. Se pedirán pruebas desde WSL/S25 antes de transferir la escucha al principal, actualizar Boot/WSL y cerrar 8022. Reversión local preparada y guardia de cinco minutos durante el corte; confirmación bajo bloqueo antes de encender Horus. Recuperación ADB abre Termux para ejecutar la orden del informe con desbloqueo físico si hace falta. No se probó una reversión real porque supondría recargar el servicio antes de autorización.

La interfaz real del S25 muestra ProxyJump, dejado en Ninguno durante fase 1; se evaluará antes de añadir un listener local. **Punto de parada: autorización explícita del usuario para migrar 8022 → 8023**, solicitada conforme a su instrucción original. Fases Horus/Codex y apagado físico siguen pendientes.

### EXP07 — Migración Termux 8022 → 8023 completada

**Resultado: PASS**, 2026-10-20, comprobaciones finales hasta 23:03 UTC. El usuario autorizó «si, dale con eso», confirmó la prueba paralela con «funciona en el 8023» y pidió continuar. Se preserva la autorización y la ejecución en [sondas de migración](validation/mestry-s25-port-migration-20261020T224339Z/commands.md); [resultado estructurado](validation/mestry-s25-port-migration-20261020T224339Z/result.json).

`r01/r02` revalidaron SSH/ADB, configuración y estado Horus; `r03` respaldó WSL fuera del proyecto en `~/.cache/mestry/s23-port-migration-20261020T224339Z/{config,known_hosts}`, ambos 600. Los respaldos privados de Termux ya estaban en `~/.local/state/mestry/ssh-port-8023-20261020T222743Z`; no se sobrescribieron ni se copiaron claves privadas. `r04` abrió el temporal 8023, PID 13734, manteniendo el principal 2975 en 8022. `r05/r06` comprobaron ambas escuchas y conexiones nuevas WSL. `r07` encontró autenticación de la clave S25 `SHA256:CONFIGURE_LOCAL_FINGERPRINT` desde `192.0.2.13` en el registro temporal.

Al retomar, `r08a/r08b` confirmaron que el corte todavía no había ocurrido y que respaldos, procesos y Horus seguían en el estado esperado. `r08` inició la guardia de cinco minutos a las **22:59:36 UTC**, instaló `10-mestry-port.conf`, actualizó helper/Boot, retiró únicamente el listener temporal identificado y envió HUP al principal 2975. `sshd -t/-T` verificaron solo 8023 y autenticación pública; el hook ejecutado manualmente devolvió **`ready pid=2975 port=8023`**. La configuración principal y el drop-in de autenticación permanecen idénticos a sus respaldos. El stderr conserva una carrera al leer el `/proc` del temporal ya terminado; la sonda terminó en 0 y las comprobaciones independientes verificaron el estado final.

`r09` comprobó una conexión nueva a 8023 con la confianza previa, cambió **solo Port 8022 → 8023 del alias `mestry-s23`** y añadió para 8023 la clave pública de servidor ya autenticada, conservando la entrada 8022. Después reconectó por el alias actualizado; `r12` verificó ese cambio mínimo, permisos 600, identidad, `IdentitiesOnly`, verificación estricta y agente desactivado. `r10` confirmó 8022 libre mediante ADB, con la advertencia parcial de netlink conservada.

El usuario abrió una conexión nueva desde el S25 y ejecutó el verificador instalado como `~/bin/mestry-ssh-check`. Su [salida completa](validation/mestry-s25-port-migration-20261020T224339Z/s25-final-user-confirmation.json) muestra **23:01:37 UTC**, usuario `u0_a348`, `SSH_CONNECTION=192.0.2.13 56756 192.0.2.15 8023`, ancestro canónico **2975**, **`MESTRY_S25_CANONICAL_8023=PASS`** y guardia confirmada. El verificador exigía puerto, origen, ascendencia del daemon principal, comprobación WSL y hash intacto de autorizaciones; escribió los marcadores bajo bloqueo. `r11` los observó desde el teléfono y `r13` confirmó una nueva conexión WSL al principal, los archivos instalados, ambas claves y el proceso del temporizador ya terminado sin reversión.

`r14` confirmó independientemente por ADB **un único daemon sshd**, escuchas IPv4/IPv6 en **8023**, ninguna en **8022**, IP `192.0.2.15/22` y Horus remoto **false/stopped/0 claves**. `authorized_keys` conserva SHA-256 **`31d62780157ee7714a7cc1f145d1825ccda9ab761eda38bf92fb492a8f1c7e59`**; huella de servidor **`SHA256:CONFIGURE_LOCAL_FINGERPRINT`**. Scripts 700, autorizaciones/configuración de puerto 600. No se mataron las sesiones autenticadas antiguas durante el corte.

**Estado de uso:** ConnectBot S25 → `u0_a348@192.0.2.15:8023`; WSL → `ssh mestry-s23`. El perfil original 8022 y los respaldos se conservan como recuperación. No hay reversión automática pendiente. La orden manual y recuperación ADB están en [S25_REMOTE_ACCESS.md](S25_REMOTE_ACCESS.md). No hubo reinicio, reversión real, paquetes nuevos, cambios de Debian/X11, emparejamiento o activación Horus. **Siguiente incremento pendiente:** emparejar Horus y comprobar el acceso S25 a Codex; después persistencia y PC físicamente apagado. La prueba manual del hook no acredita Boot tras reinicio.

### EXP07 — Clave S25 emparejada y acceso Horus por ProxyJump PASS

El usuario autorizó continuar con «dale con eso, deje horus prendido». [Autorización y sondas](validation/mestry-horus-s25-20261020T232332Z/commands.md). `s01` encontró inicialmente Horus remoto **disabled/stopped/0 claves**, `configured=true` y la clave S25 todavía sin autorizar; Termux seguía correctamente en 8023. `s02` terminó en 1 al no encontrar servidor Horus en loopback, después de verificar SSH Termux y ambas claves. No se interpretó como fallo del acceso Termux.

Se preparó [horus_pair_s25.py](../tools/horus_pair_s25.py), que valida un único SM-S918B autorizado, Termux 8023 con confianza estricta y la clave pública S25 ya verificada. Pide la contraseña local mediante `getpass` en el terminal del usuario y la transmite por stdin de ADB; no la registra ni la pone en argumentos WSL. Android `content` recibe transitoriamente el argumento base64 requerido por el provider oficial. Registra solo campos permitidos de las respuestas; errores sin filtrar y solicitudes se omiten. No copia claves privadas ni usa variables de entorno para contraseñas. `s03` pasó el preflight real de lectura; `s04` conserva **13 pruebas offline** de límites de credenciales/autorización; `s05` comprobó ese transporte por stdin con una consulta `status`, sin contraseña ni mutación.

El usuario ejecutó el helper y confirmó «listo». El [resultado real](validation/mestry-horus-pair-20261020T232711794480Z/result.json) confirma solicitud a las **23:27:18 UTC**, respuesta `ok`, huella **`SHA256:CONFIGURE_LOCAL_FINGERPRINT`**, `started=true` y autorización posterior `true`. Solo se añadió `mestry-s25`. El provider inició la preparación mínima SSH y reportó `installing`; `s06` comprobó después **enabled/running/1 clave**, S25 autorizado y Dropbear UID Android **10350**, PID **18968**, escuchando exclusivamente en **`127.0.0.1:8022`**. Termux conserva su daemon 2975 en 8023. `s07` obtuvo la clave pública de Horus por loopback desde la conexión Termux autenticada: **`SHA256:CONFIGURE_LOCAL_FINGERPRINT`**.

El S25 creó el perfil `MESTRY Horus`, destino `horus@127.0.0.1:8022`, clave S25 y **ProxyJump = perfil Termux 8023**. Su [salida real](validation/mestry-horus-s25-20261020T232332Z/s25-horus-user-confirmation.json) muestra `MESTRY_S25_HORUS_OK`, usuario **horus**, UID 1000, home **`/home/horus`**, Alpine **3.24.0**, **aarch64** y `SSH_CONNECTION=127.0.0.1 50860 127.0.0.1 8022`. El log filtrado `s08` corrobora el puerto origen 50860 y la autenticación de la huella S25 a las **20:29:20 del teléfono**. El origen loopback corresponde al tramo final del salto; la atribución al S25 proviene de su salida y su clave, no de confundir ese origen con una dirección Wi-Fi.

No se creó listener 18022, `adb forward` ni puente diario por WSL. Se usa la capacidad `direct-tcpip` de ConnectBot, revisada en [su fuente oficial](https://github.com/connectbot/connectbot/blob/main/app/src/main/java/org/connectbot/transport/SSH.kt) y probada en el cliente real. ADB se utilizó para el emparejamiento y la observación inicial; el login S25 usa Wi-Fi. Esto no prueba todavía el PC físicamente apagado, un reinicio o la supervivencia tras desconexión.

El [diagnóstico Codex posterior desde S25](validation/mestry-horus-s25-20261020T232332Z/s25-codex-preflight-user-output.json) encontró solo el stub oficial en el perfil `/home/horus`, `CODEX_PROFILE_INSTALL=absent` y el proyecto sintético compartido. Se solicitó su preparación mediante `codex --version && codex login status` en ese proyecto, avisando de la descarga inicial; resultado pendiente. La instalación/autenticación e historial del harness de la app no se atribuyen automáticamente al usuario SSH. [Estado actual y revocación](S25_REMOTE_ACCESS.md), [helper y límites](../tools/HORUS_S25_PAIRING.md).


### EXP07 — Codex 0.163.0 instalado en perfil SSH; login pendiente

El usuario aportó la salida de `cd /workspace/projects/mestry-horus-smoke && codex --version && codex login status` ejecutado desde el S25: `added 2 packages in 48s`, `Codex is installed.`, **`codex-cli 0.163.0`**, **`Not logged in`**. [Evidencia humana conservada](validation/mestry-horus-codex-auth-20261020T234450Z/installation-user-output.json). La preparación se hizo mediante el instalador oficial ya existente en Horus, en el perfil SSH `/home/horus`; no se repitieron Debian, X11 ni la instalación APK. No se ejecutó una tarea al modelo. Los 48 s corresponden a la salida npm aportada, sin medición controlada de duración total.

Se consultó y leyó [OpenAI Docs sobre CLI remota](https://learn.chatgpt.com/docs/auth#login-on-headless-devices). Se solicitó `codex login --device-auth` en esa misma terminal, completar el acceso en el navegador del S25 y comunicar solo `codex login status`. Puede requerir que la cuenta o el workspace permita el acceso por código. El enlace y código de acceso, tokens y archivos de credenciales permanecen fuera del chat y de la evidencia. **Autenticación pendiente**, sin atribuir el login/historial del harness de la app a este perfil, ni iniciar tareas Codex, probar persistencia, reiniciar o apagar el PC. [Alcance y fuente](validation/mestry-horus-codex-auth-20261020T234450Z/source-review.json).


### EXP07 — Login confirmado; primera tarea Codex desde S25 solicitada

El usuario confirmó **«ya estoy logged in»** después del paso de autenticación privado. Se conserva la [confirmación humana](validation/mestry-horus-codex-auth-20261020T234450Z/login-user-confirmation.json), sin inventar una transcripción de `codex login status` ni leer credenciales. La instalación 0.163.0 y el acceso S25 → Horus ya estaban registrados.

Se solicitó abrir Codex desde el S25 en `/workspace/projects/mestry-horus-smoke` y crear/modificar únicamente `S25_REMOTE_TEST.txt`: marcador `MESTRY_S25_REMOTE_OK`, estado inicial `creado` y final `modificado`. El encargo exige parar si el destino ya existe, conservar todos los demás archivos y no instalar paquetes; pide comandos y salidas de `pwd`, `uname -m`, contenido y SHA-256. [Plan y prompt exacto](validation/mestry-horus-s25-task-20261020T235104Z/plan.json). Se usará la función oficial Horus que ya agrega `--sandbox danger-full-access --no-daemon`, aceptados para esta rama; no se agregaron flags para omitir aprobaciones. **Ejecución todavía pendiente de resultado del usuario**; WSL no envió una tarea al modelo. Después se comprobarán contenido y hashes desde una conexión nueva del S25, distinguiendo esa prueba de persistencia de procesos o PC apagado.


### EXP07 — Tarea Codex desde S25 y verificación independiente PASS

El usuario ejecutó la tarea en el Codex del perfil SSH. Su [respuesta de la tarea](validation/mestry-horus-s25-task-20261020T235104Z/codex-user-reported-result.json) describe creación con `set -C`, contenido inicial `estado=creado`, modificación a `estado=modificado`, ruta `/workspace/projects/mestry-horus-smoke`, arquitectura `aarch64` y SHA-256. El hash partido por el ancho del S25 se normalizó uniendo sus dos líneas hexadecimales y se conserva también la respuesta original. Esa respuesta se distingue de la verificación posterior sin modelo.

El usuario abrió **otra conexión S25** y aportó una [lectura independiente](validation/mestry-horus-s25-task-20261020T235104Z/independent-s25-verification.json) a las **23:54:20 UTC**, usuario `horus`, conexión `127.0.0.1 39052 127.0.0.1 8022`. Contenido exacto `MESTRY_S25_REMOTE_OK\nestado=modificado\n`; SHA-256 **`b630aca886c0e78dd680d18838cf9393ebb9be57890a6b1e18a3fb0e6f4f8fcc`**. `saludo.py`, `test_saludo.py` y `README.md` coinciden con los tres hashes verificados en EXP06. `t02` corrobora en el log de Horus la autenticación de la clave S25 desde ese mismo puerto origen. No se volvieron a ejecutar las pruebas Python de EXP06; la comprobación actual preserva bytes y verifica el archivo remoto.

`t01` observó **Codex PID 21261** bajo UID Android **10350**, como hijo de Node/zsh/Dropbear de la sesión SSH original, a las **23:51:54 UTC**. El CLI y sus herramientas están en el S23; la inferencia sigue usando el servicio de OpenAI. WSL solo conservó evidencia y observó procesos; no alojó el proyecto ni envió la tarea al modelo. [Resultado y límites](validation/mestry-horus-s25-task-20261020T235104Z/result.json).

**Reconexión en comprobación:** se solicitó desconectar solo el perfil original en ConnectBot, reconectarlo y abrir `codex resume --last` desde el mismo proyecto, con lectura/hash antes de la TUI. `t03` todavía observaba el PID y la sesión originales mientras faltaba el resultado del usuario; no se cuenta como prueba de supervivencia tras desconexión. No se afirma todavía recuperación de conversación, mismo proceso vivo, PC físicamente apagado, Boot o resistencia prolongada. No hubo reinicio, nuevos puertos, cambios Android globales ni transferencia de credenciales en este incremento.


### EXP07 — Conversación recuperada y bloqueo local de 15 minutos aclarado

Registro del 2026-10-21 UTC, todavía 20 de octubre en Chile. El usuario confirmó **«funciona, reaparece la conversacion»** después del ensayo solicitado de reconexión y `codex resume --last`. Se conserva como [confirmación humana](validation/mestry-horus-s25-task-20261020T235104Z/reconnect-user-confirmation.json); no se obtuvo transcripción de la TUI ni ID de hilo. El [resultado de la tarea](validation/mestry-horus-s25-task-20261020T235104Z/result.json) distingue recuperación de conversación de supervivencia del proceso original, que sigue sin demostrarse.

Ante el supuesto corte de 15 minutos, el usuario precisó **«Solo vuelve a pedir contraseña en Horus del S23»**. Se revisó el commit instalado de Horus **1.0.4**, `2f8f8a2faebd3d0fbd11dd83340bdcfbac437369`: `sessionTimeout.ts` y `SessionUnlockGrant.kt` fijan 15 minutos en segundo plano; el bloqueo de `App.tsx` muestra el login y revoca el permiso de desbloqueo, sin detener sesiones ni el servidor remoto. Los ajustes revisados no permiten desactivar o cambiar el plazo. Tres archivos de la caché coinciden exactamente con la fuente oficial obtenida por el conector GitHub. [Fuentes y comparación](validation/mestry-horus-ui-lock-20261021T010002Z/source-review.json).

Una consulta ADB de lectura a las **01:00:12 UTC** confirmó versión **1.0.4/code 5**, remoto **enabled/running**, puerto **8022**, una clave y `batteryUnrestricted=true`. Se observan Dropbear **18968** y otro proceso Codex **30133** bajo UID Android **10350**; no se atribuye al PID original 21261 supervivencia ni continuidad sin interrupción. [Sonda](validation/mestry-horus-ui-lock-20261021T010002Z/commands.md), [diagnóstico y límites](validation/mestry-horus-ui-lock-20261021T010002Z/result.json).

Se conserva el bloqueo oficial: no hace falta mantener Horus desbloqueado en el S23 para usar SSH desde el S25. No hubo cambios de app, contraseña, puertos, ajustes Android, paquetes ni sesiones, ni se envió otra tarea al modelo. El estado puntual no sustituye medir reposo prolongado, PC físicamente apagado o Boot tras reinicio.


### Drive y app Android S25 — conexión reautorizada, piloto privado y edición recuperada

El usuario eligió explícitamente crear una carpeta privada nueva `MESTRY/Review` con documentos sintéticos y una **app Android** para controlar proyectos/conversaciones Codex desde el S25. Se preparó [un traspaso](DRIVE_S25_HANDOFF.md) al faltar scope de escritura del conector. El usuario aclaró después la cuenta objetivo; el perfil del conector confirmó la identidad solicitada y las consultas de metadata funcionaron, pero el intento de crear la carpeta todavía devolvió `ACCESS_TOKEN_SCOPE_INSUFFICIENT`. No se interpretó ese error como ausencia de acceso de lectura ni como fallo de cuenta.

Tras «actualize la conexion, prueba de nuevo», se revalidó el perfil y se buscó MESTRY antes de crear. El conector creó `MESTRY` y su subcarpeta [Review](https://drive.google.com/drive/folders/DRIVE_FOLDER_03_EXAMPLE). Se subieron cuatro fixtures `.md` por primera vez, sin conversión: español, tablas/enlaces, código/Mermaid/HTML y front matter/relativos/CRLF. Metadata posterior confirmó IDs, padre, MIME y permisos solo de propietario; no se añadieron otros usuarios ni permisos públicos. Los cuatro archivos descargados como bytes completos coincidieron con sus SHA-256 locales, incluidos CRLF. Se preservan bases y lecturas originales en [manifest](validation/mestry-drive-review-20261021T020632Z/manifest.json). Las URLs temporales de descarga no se guardaron en la evidencia.

La API de comentarios del primer fixture respondió inicialmente vacía. Se solicitó al usuario abrirlo desde el S25 y añadir un comentario separado con `MESTRY_S25_DRIVE_REVIEW_OK`. Respondió «listo». Una nueva descarga mostró una edición real del cuerpo: la línea `si si puede`; el tamaño pasó de 583 a 594 bytes y el SHA-256 observado a `e32370214b44ca900e24f481ff446c11af8eb5f17439297f15fe93e40014efe1`. La API de comentarios seguía vacía. Se conserva el [diff de la edición humana](validation/mestry-drive-review-20261021T020632Z/post-s25-byte-comparison.json), sin deshacer ni sobrescribir el archivo remoto. Se pidió aclarar la app utilizada y usar «Añadir comentario» para distinguir edición del contenido y feedback separado; **comentarios todavía pendientes de verificación**.

Este resultado prueba creación/subida/descarga mediante conector/WSL y una edición reportada desde S25, recuperada independientemente. No prueba publicación autónoma por el S23, OAuth separado entre UIDs ni toda la fidelidad Markdown. No se instalaron bridge o cliente Android, no se abrieron puertos, no se cambiaron claves/credenciales del teléfono y no hubo nuevas solicitudes al modelo. [Resultado y límites](validation/mestry-drive-review-20261021T020632Z/result.json). El bloqueo OAuth anterior queda histórico; continuar con los IDs existentes.


### Drive/S25 — comentarios retirados de los requisitos del piloto

El usuario aclaró que no utiliza comentarios en Markdown y no ve utilidad en añadirlos a este flujo. Se [conservó su aclaración](validation/mestry-drive-review-20261021T020632Z/comment-scope-user-clarification.json) y se cerró la solicitud de comentario como **no requerida**, sin marcar la API de comentarios como validada ni seguir consultándola. El archivo de prueba está en Google Drive; la mención del usuario a OneDrive no se interpretó como una autorización para migrar de proveedor.

El flujo actual conserva lectura/edición de documentos seleccionados, publicaciones por versión y preservación de cambios humanos. La creación, subida y descarga íntegra por conector, así como la edición humana recuperada, siguen siendo los resultados verificados. La publicación autónoma S23 y la interfaz Android de Codex siguen pendientes. Se actualizaron el estado del piloto, el traspaso y los criterios V12/V13 para que los comentarios no bloqueen el avance. No hubo escrituras adicionales en Drive, comentarios enviados, nuevas consultas de comentarios ni cambios de dispositivos/puertos/credenciales.

### Publicador Horus → Drive — preparación inactiva, 2026-10-21 UTC

El usuario pidió «sigamos con la la publicación autónoma desde Horus» y respondió «No, hay que prepararlo» al preguntar por el cliente OAuth propio. Se preparó [la guía Google Cloud](../tools/horus_publish/README.md): cuenta `owner@example.invalid`, audiencia externa, prueba inicial, cliente de escritorio y solo `drive.file`. Ante una captura de la lista de scopes se indicó seleccionar únicamente ese scope y dejar las opciones ajenas desmarcadas. No se accedió a una contraseña, JSON real ni token del usuario.

Las comprobaciones reales SSH/ADB distinguen **Termux UID 10348** y **Horus UID 10350**, Horus remoto running/enabled en 8022 con una clave S25; el SSH Termux existente sigue en 8023. Se copió código nativo Python a `~/.local/lib/mestry-publish`, con estado `~/.local/state/mestry-publish` (700, archivos 600). Sigue inactivo, sin cliente OAuth, token, journal de publicaciones o clave nueva. SHA-256 de `authorized_keys` idéntico al baseline de dos claves WSL/S25. [Prueba de estado nativo](validation/mestry-horus-publish-20261021T033650Z/r05_native_stdlib_tests_and_private_stage.stdout.txt).

La capacidad preparada usa clave exclusiva de comando forzado/loopback en 8023; acepta solo un Markdown sintético de hasta 64 KiB, cuenta/destino fijos y crea otro archivo por revisión. Reserva el ID Drive antes de subir, reconcilia ese ID tras respuesta perdida y exige privacidad, metadata y bytes íntegros antes de confirmar. No ejecuta comandos proporcionados por el agente, sobrescribe archivos ni cambia permisos Drive. La allowlist cliente no demuestra criptográficamente procedencia del contenido ante un agente con control de su workspace.

La primera preparación de Google Auth en Termux falló por CFFI sin compilador. Se conservaron salidas/código de fallo y se retiraron **solo** el paquete `python-cryptography` recién instalado y el venv incompleto de este intento. El diseño final mantiene el runtime S23 en Python estándar; el refresh usa el endpoint oficial fijo por HTTPS. Se instaló la biblioteca oficial actual **google-auth 2.62.0 / google-auth-oauthlib 1.5.0** en venv privado WSL para la autorización inicial que ejecutará el usuario. El helper transferirá el token por stdin SSH y no lo persistirá en WSL. No se inició OAuth, abrió callback ni guardó URL/código/token.

**26 tests WSL correctos; 25 S23 correctos y uno exclusivo WSL omitido.** Se probaron con API falsa respuesta perdida/reintento, ediciones humanas preservadas, hash/privacidad, cuenta/carpeta incorrectas, límites de entrada/cuota y renovación simulada que rechaza ampliación de scopes. El preflight de la biblioteca oficial construye PKCE S256 y scope único con sockets bloqueados; no demuestra consentimiento real. El callback temporal **127.0.0.1:53682 en WSL** queda pendiente de aprobación expresa por la regla de puertos. No hubo escrituras nuevas en Drive ni tareas al modelo, cambios de claves/puertos/Boot o de la interfaz S25. Publicación real, renovación real y PC apagado siguen pendientes. [Registro de preparación](validation/mestry-horus-publish-20261021T033650Z/manifest.json).

### Cliente OAuth real importado y callback aprobado

El usuario facilitó la ruta local Windows del JSON descargado. Se validó el tipo de escritorio y los endpoints fijos de Google sin mostrar valores y se transmitió por stdin del SSH existente a Termux. Una conexión nueva comprobó UID 10348, estado privado 700, archivo `client.json` 600, ausencia de token/journal y el SHA-256 intacto de las dos claves anteriores. No se guardó una copia del JSON en el proyecto ni se interpretaron los scopes solicitados por el helper como permisos ya concedidos. [Importación y readback](validation/mestry-horus-oauth-client-20261021T035330Z/manifest.json).

Con el comando concreto preparado, se solicitó el callback temporal WSL 127.0.0.1:53682 por hasta 180 segundos, explicando la regla previa de aprobación de puertos. El usuario respondió **«Sí, autorizo el callback temporal»**. Se conserva [la aprobación](validation/mestry-horus-oauth-client-20261021T035330Z/callback-approval.json). No pedirla otra vez para este paso. Se le entregó `AUTHORIZE_IN_WSL.sh` para ejecutar privadamente, abrir el enlace solo en el navegador del PC y responder con el resultado final. No se ejecutó el login bajo herramientas/logger del agente ni se guardaron URL, códigos o tokens. Consentimiento, cuenta/scopes reales y publicación siguen pendientes de resultado; SSH 8022/8023, claves y Horus sin cambios.

El usuario reportó después **403 access_denied**, «la app se está probando y solo los verificadores aprobados por los desarrolladores pueden acceder». Una consulta SSH confirmó cliente presente y token ausente. Se extrajo solo el ID público de proyecto del JSON, `mestry-s23-publisher`, y se contrastó [la documentación oficial de audiencia](https://support.google.com/cloud/answer/15549945?hl=es). Se pidió añadir la cuenta objetivo a Usuarios de prueba de ese proyecto y guardar, luego cancelar el intento anterior si seguía esperando y repetir el helper seleccionando exactamente esa cuenta. No se accedió a la lista Google Cloud ni se afirmó que ya estuviera corregida. Se conserva [el diagnóstico](validation/mestry-horus-oauth-client-20261021T035330Z/testing-audience-error.json), sin nuevos tokens, cambios de scopes o subida Drive.

### Publicación nativa Horus/Drive — piloto PASS

Después de «listo», se confirmó el token en Termux y se verificaron realmente cuenta `owner@example.invalid`, scope único `drive.file`, archivo privado 600 y refresh nativo sobre HTTPS. El S23 creó una carpeta propia `Horus` con ID reservado, [DRIVE_FOLDER_01_EXAMPLE](https://drive.google.com/drive/folders/DRIVE_FOLDER_01_EXAMPLE). El traslado mediante conector devolvió error interno y el PATCH nativo venció sin respuesta; metadata se reconcilió después de ambos intentos y seguía en la raíz. Se pidió al usuario moverla a Review y el padre final/privacidad se comprobaron por conector y S23. No se atribuyó el error a un scope rechazado ni se concedió uno mayor.

El usuario generó una clave dedicada dentro de Horus y entregó solo su parte pública. Se registró con `restrict`, loopback y Python aislado/comando fijo, con backup privado y conservación byte a byte de las dos claves anteriores. Huella nueva `SHA256:CONFIGURE_LOCAL_FINGERPRINT`. El bootstrap S25 confirmó **MESTRY_PUBLISH_COMMAND_AND_FORWARDING_DENIED=PASS** y **MESTRY_PUBLISH_CLIENT_READY**; las pruebas no abrieron nuevos listeners.

El S25 ejecutó el cliente en el perfil SSH Horus del S23: r0001 `DRIVE_ID_06_EXAMPLE`, SHA-256 `0f6b0a0302bac581660a9b059d3773b232ce9c5c2ddf2e6cb86e75b98c0d22c8`. El reintento idéntico devolvió el mismo ID/revisión. Tras comprobar el hash local y cambiar solo `estado`, r0002 `DRIVE_ID_09_EXAMPLE`, SHA-256 `ada9d1e265088e8fae3dfe57e9a229e8e31ebd75ff480a321e70eaa82d8f20a7`. Ambas son Markdown de 79 bytes. Otra conexión descargó ambas íntegramente, verificó sus hashes y mostró primera/segunda publicación sin sobrescritura; journal con exactamente dos filas. El conector confirmó MIME/padre/permisos solo de propietario. El usuario respondió «listo» tras abrir ambas desde S25 y comprobar sus estados. App lectora sin identificar, sin pedir edición ni comentarios.

**Piloto funcional PASS**, con alcance a un documento sintético y sin tarea nueva al modelo, app/bridge S25, corpus, root, reboot o cambios de puertos permanentes. PC físicamente apagado, continuidad y Boot real siguen sin medir. Se solicitó completar Google Auth Platform **En producción** y un nuevo consentimiento para evitar el vencimiento fijo de siete días de Testing; archivado/recuperación privados del token preparados, todavía sin ejecutar. [Uso actual](HORUS_DRIVE_PUBLISH.md), [resultado y evidencia](validation/mestry-horus-drive-live-20261021T040010Z/result.json).

## Preparación OAuth de producción `mestry-oauth-production-20261021T043506Z`

El usuario solicitó investigar el bloqueo de «Publicar app», conservar cliente de escritorio, `drive.file`, callback y puertos, respaldar el token antes de reautorizar y preparar GitHub Pages solo si fuera necesario, con autorización antes de crear un repositorio público.

- Consulta de documentación oficial actual: permisos no sensibles y uso personal eximen de revisión OAuth completa, pero la ayuda de marca exige enlaces para producción externa. La documentación difiere sobre condiciones del servicio. Se solicita primero comprobar nombre, asistencia y contacto ya guardados; todavía no se observó la consola del usuario ni un cambio a producción.
- Cuenta GitHub y CLI verificadas como `Rvillena75`. No se encontró sitio de usuario en los repositorios accesibles. No se creó ni publicó ningún repositorio.
- [Sitio local y guía](../tools/s23-publisher-branding/README.md): inicio, política de privacidad, CSS y `.nojekyll`; condiciones separadas como alternativa solo si Google las exige. Payload limitado a cuatro archivos estáticos, sin correos personales ni credenciales. Chromium local por pipe, sin puerto de red: inicio/privacidad a 320, 390 y 1280 px, sin desbordamiento; revisión visual móvil y escritorio. La librería de audio necesaria para renderizar se extrajo únicamente en `/tmp` de WSL; no se instaló en el sistema ni en el teléfono. La primera captura CLI tuvo una ventana recortada; se conserva, sustituida para aceptación por las capturas con viewport medido.
- SSH al Termux real UID 10348 confirmó cliente/token existentes. Se copió y verificó el token en el almacenamiento privado del S23 como `token.before-production.20261021T043657Z.json`, permisos `600`; el activo quedó byte a byte intacto. No se exportaron credenciales ni se abrió el callback.
- Se preparó, sin ejecutar, una comprobación de mismo cliente/scope, refresh nativo y lectura de las dos revisiones existentes para después de producción y reconsentimiento. Ningún cambio al runtime del publicador ni nuevas publicaciones.
- Se pidió autorización condicionada para crear/publicar `Rvillena75/Rvillena75.github.io` si los campos básicos no resuelven el bloqueo. La aprobación y la comprobación de Google Cloud están pendientes.

[Evidencia y estado](validation/mestry-oauth-production-20261021T043506Z/state.json), [fuentes](validation/mestry-oauth-production-20261021T043506Z/research.json), [respaldo](validation/mestry-oauth-production-20261021T043506Z/r01_private_token_backup.stdout.txt), [verificación local](validation/mestry-oauth-production-20261021T043506Z/local-preparation-check.json), [render](validation/mestry-oauth-production-20261021T043506Z/render-check.json).

## Cierre OAuth de producción `mestry-oauth-production-confirmed-20261021T055110Z`

**Resultado: OAuth de producción reautorizado, refresh nativo y lectura Drive PASS.** El estado de producción procede de confirmación explícita del usuario en Google Cloud; las comprobaciones de credenciales/Drive proceden de otra conexión SSH al S23.

- El usuario confirmó «En producción», pero no sabía si existían las URLs. Inicio, privacidad y condiciones propuestas devolvían 404. Se corroboró ausencia del repositorio de usuario en GitHub. El usuario autorizó expresamente crear/publicar el repositorio y aclaró que guardó inicio/privacidad, dejando condiciones vacías.
- Creado `Rvillena75/Rvillena75.github.io`, commit `128b2279c92698dc5df100504df8b3674a375ff3`, exactamente `.nojekyll`, `index.html`, `privacy.html`, `styles.css`. Checkout Git aislado en `/tmp`; autor con correo GitHub noreply. Ninguna credencial, archivo OAuth, documento Drive ni evidencia interna publicada.
- La petición de creación de Pages devolvió resultado no exitoso; GET posterior confirmó Pages `built`, `main`/raíz y HTTPS obligatorio. No se determinó la causa exacta del primer resultado. Inicio/privacidad/CSS descargados con HTTP 200, idénticos byte a byte a los archivos revisados. Conector GitHub independiente corroboró árbol de cuatro archivos. No se afirma verificación Search Console/marca Google.
- Preflight nativo: UID 10348, cliente y scope únicos iguales a los existentes, token/copia `600`, activo sin cambios. Helper WSL único preparado sobre el flujo oficial existente; archivado y recuperación bajo bloqueo del publicador, conservación de un activo nuevo, seis fixtures offline correctos. No se modificó el código del runtime.
- El usuario ejecutó el helper en su propia terminal y respondió «listo». El agente no ejecutó ni registró el flujo interactivo, su enlace, código ni respuesta OAuth. Se mantuvo el callback ya autorizado `127.0.0.1:53682`, máximo 180 segundos por intento.
- A las 06:07:06 UTC se verificó desde otra conexión al S23: refresh token distinto de los anteriores, mismo cliente/cuenta/scope, renovación real HTTPS, descargas de ambas revisiones de 79 bytes con SHA-256 esperado y permisos privados. Cero publicaciones nuevas. Callback WSL cerrado.
- Copias privadas anteriores conservadas y copia del token de producción `token.production-verified.20261021T061015Z.json`, todas `600`. Copia de producción idéntica al activo. Un primer chequeo adicional de SSH (`r03`) falló por asumir dos líneas para dos claves cuando el original incluye una línea vacía; el respaldo ya se había creado. `r04` reconcilió el archivo completo y la copia sin modificarlos; `r05` confirmó las dos claves previas byte a byte, clave restringida exacta, tres claves totales, conexión efectiva 8023 y hashes del runtime idénticos a las fuentes WSL. No se borró ni ocultó el fallo del chequeo.
- Estado final registrado; no nuevos scopes/clientes, puertos ni cambios de otras funcionalidades. Los tokens siguen sujetos a revocación y otras causas de caducidad. La observación de más de siete días todavía no transcurrió; una comprobación después del 29-10-2026 06:08 UTC la cubriría. No se programaron tareas. Backups emitidos en Pruebas no constituyen una autorización perpetua.

[Resultado y límites](validation/mestry-oauth-production-confirmed-20261021T055110Z/result.json), [refresh/Drive real](validation/mestry-oauth-production-confirmed-20261021T055110Z/r02_post_production_reconsent_verify.stdout.txt), [copias/claves/código](validation/mestry-oauth-production-confirmed-20261021T055110Z/r05_final_readonly_preservation_check.stdout.txt), [HTTPS](validation/mestry-oauth-production-confirmed-20261021T055110Z/website-published-verification.json), [callback cerrado](validation/mestry-oauth-production-confirmed-20261021T055110Z/callback-closed-check.json).
