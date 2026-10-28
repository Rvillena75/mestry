# MESTRY — Auditoría del entorno Codex y continuidad

Fecha local: **2026-10-26**, America/Santiago. Investigación iniciada **20:32 −03:00**. Alcance: lectura, fuentes oficiales y diseño; **no implementación**. Los [cinco informes anteriores](../../auditorias/2026-10-26/01_ESTADO_ACTUAL_MESTRY.md) son línea base histórica de las 17:52–18:16, no estado garantizado de esta segunda sesión.

## Diagnóstico principal

El problema tiene dos partes: **mantener vivo y recuperable el nodo Android** y **transferir versiones ejecutables del trabajo entre plataformas**. Se confirmó acceso a ambos teléfonos y SSH a Termux, pero Horus remoto está configurado/habilitado y **detenido**; el bridge no respondió. Disponer de carpetas sincronizadas no mantiene ese backend disponible.

La solución recomendada conserva Codex/Horus: modo remoto sobre el S23 como opción habitual y ejecución WSL local opcional mediante entregas Git verificadas, dependencias por plataforma y handoff explícito. Es una **PROPUESTA**, detallada en [05](05_ARQUITECTURA_RECOMENDADA.md), con pruebas y autorizaciones en [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md).

## Evidencia y estados

Los IDs L01–L12 y S01–S24 remiten a [07](07_EVIDENCIAS_Y_LIMITACIONES.md). Se conservan los estados **APROBADO / CONGELADO**, **IMPLEMENTADO Y VERIFICADO**, **CONFIGURADO / NO VERIFICADO**, **REPORTADO POR USUARIO**, **PROPUESTO**, **PENDIENTE**, **BLOQUEADO / SIN ACCESO**. «Verificado» indica exactamente qué se observó; configuración, proceso existente, prueba funcional y disponibilidad prolongada son evidencias diferentes.

## 1. Cambio respecto de la auditoría anterior

| Punto anterior | Observación nueva | Estado/alcance |
|---|---|---|
| ADB sin dispositivos | Servidor Windows **ya existente**, PID 10168, escuchando en loopback 5037; protocolo ADB enumera S23 y S25 | **IMPLEMENTADO Y VERIFICADO**, acceso de lectura actual. No se invocó el cliente ADB ni su autostart. L02 |
| SSH LAN sin ruta | S23 conserva `192.0.2.15`; alias existente autentica como UID Termux 10348 | **IMPLEMENTADO Y VERIFICADO**, SSH actual. No se cambiaron claves/known_hosts/alias. L03 |
| Horus/bridge saludables el 22/10 | Estado público Horus: configured=true, enabled=true, **state=stopped**; sin servicio terminal/Dropbear/Codex/Node observado; health 8787 sin respuesta | Configuración conservada, servicio **no operativo en la muestra**. No se arrancó. L04 |
| Cliente S25 piloto8 histórico | Instalado `0.2.0-mestry-pilot8 / 10008`; sin procesos cliente/ConnectBot/Tailscale observados en la muestra | Instalación **VERIFICADA**; conexión funcional actual **NO VERIFICADA**. L05 |
| FolderSync Android no inspeccionado | Instalado **4.14.0**, UID 10353, proceso presente, acceso general permitido a nivel UID y grant SAF persistente a `Documents/Mestry` | Permisos/ruta compartida **VERIFICADOS**; pares, Drive IDs, horarios y logs privados **SIN ACCESO**. L06 |
| Acceso de Codex a sincronizados desconocido | Árbol compartido distinto del workspace privado Horus; falta grant/bind compartido y manifiesto Horus no concede acceso general Android 16 | Acceso directo **no demostrado**; no resolver mediante symlink. L06–L07 |
| Posible copia S23 del repo | Existe `Documents/Mestry/Villegol/Proyectos/mestry`; ADR con el mismo SHA-256 de WSL | Copia compartida **VERIFICADA** para el archivo comparado, no réplica completa ni workspace Codex. L07 |
| Fallos Windows | DB persistida sigue mostrando una cancelación y tres fallos, último cierre 23/10; mismo par sin filtros | Hallazgo continúa en imagen consultada, sin afirmar estado en memoria o WAL completo. L08 |
| rclone histórico sin programación | Mismo script/filtros, mismos últimos logs exitosos del 22/10; sin rclone activo ni crontab del usuario en muestras | **CONFIGURADO / NO VERIFICADO** como sincronización actual. L09 |
| MESTRY sin Git | Sigue sin `.git`; fuentes de piloto reproducidas desde caché/pins | **PENDIENTE** línea base propia. L01/L10 |
| 24/7 sin aceptar | Teléfono lleva aproximadamente 84–90 min de uptime en primeras muestras; Termux/SSH activos, Horus detenido | No demuestra causa del estado ni recuperación completa tras ese arranque. Disponibilidad 24/7 **PENDIENTE** |

**Corrección al informe anterior:** la semántica específica de `rclone bisync --max-delete 20` es un umbral porcentual, no un límite de veinte archivos. El código oficial **v1.75.2** calcula `MaxDelete/100`; por tanto el riesgo anterior estaba subestimado. No se modificaron los informes originales ni el script. [Fuente fijada](https://raw.githubusercontent.com/rclone/rclone/v1.75.2/cmd/bisync/deltas.go), L09/S06.

## 2. Windows y WSL2 actuales

| Elemento | Inventario y límite |
|---|---|
| Windows | Windows 11 Home Single Language, versión `10.0.26300`; FolderSync Desktop 2.13.0.0. Google Drive for desktop 132.0.0.0 figuraba instalado en línea base; no se acredita un par suyo activo |
| WSL | Ubuntu 24.04, x86_64, glibc 2.39, kernel WSL2 `6.18.33.1-microsoft-standard-WSL2` |
| Codex WSL | Paquete instalado **0.164.0**, entrada `~/.npm-global/lib/node_modules/@openai/codex/bin/codex.js`. No se ejecutó un turno nuevo para validarlo |
| Estado local Codex | `CODEX_HOME=/home/developer/.codex-account-2`; config existente con modelo `gpt-6.1-sol`, approval `never`, sandbox `danger-full-access`; 40 archivos bajo sessions en la muestra. Solo se contaron/inspeccionaron metadatos, sin leer conversaciones/auth |
| Herramientas | Node 22.23.1, Python 3.12.3, Git 2.43.0, rsync 3.2.7/protocolo 31, OpenSSH/SFTP, tar, rclone 1.75.2. No se instalaron paquetes |
| ABI observada | `/usr/bin/node` es ELF x86-64 con intérprete glibc; no es ejecutable ARM64/Alpine por copiarlo |
| Workspace MESTRY | `/home/developer/proyectos/mestry`; 1.808 archivos y 66.245.027 bytes al inicio, incluidos los cinco informes previos. Sin Git, rama o commit propios |
| Fuentes cliente/bridge | Copia piloto8 en `~/.cache/mestry/s25-auto-vpn-20261022T034500Z/reproduced-pilot8`; upstream `538d65f67e34907789237fc71f56e8ca95d9f3cb`, parche y 68 huellas de línea base. No trasladar su commit upstream como commit de MESTRY |

Un editor Windows puede trabajar sobre WSL, pero un checkout WSL y una carpeta NTFS de Villevault son ubicaciones diferentes. Se recomienda un checkout Linux privado para herramientas Linux; cualquier traslado/creación queda sujeto al plan aprobado.

## 3. S23: separación de entornos

| Dominio | Ubicación/UID | Observación |
|---|---|---|
| Android OEM | SM-S918B/dm3q, Android 16/API36, ABI arm64-v8a; parche 2026-09-05, Verified Boot green | Verificado por propiedades, sin root/cambios. FBE `file`; primer desbloqueo importa |
| Recursos | `/data`: 232.847.308 KiB, 198.926.272 KiB disponibles en primera muestra (≈189,71 GiB); MemTotal7.242.340 KiB, MemAvailable3.988.424 KiB (≈3,80 GiB) | Una muestra de estado, no pico ni garantía. USB=true, AC=false, batería80%, temperatura25,2 °C en muestra actual |
| Termux | UID 10348; `/data/data/com.termux/files/home`; SSH8023 | Acceso actual por clave. Python3, sftp y proot-distro resueltos; **git/node/npm/rsync/rclone no resueltos en PATH Termux**. No indica ausencia en Horus/Debian |
| Debian/PRoot | Instancia histórica mestry-debian13, Debian13/arm64, home/rootfs Termux | No se inició el guest durante esta investigación. No comparte automáticamente home/deps con Horus |
| Horus Android | UID 10350; `/data/user/0/com.scariflabs.horus/files` | APK 1.0.4/versionCode 5 y hash igual al oficial. El shell ADB y Termux no pueden leer su almacenamiento privado |
| Horus invitado | Alpine 3.24.0/aarch64 histórico; perfil SSH `/home/horus`; perfiles de harness separados | Runtime/homes actuales no inventariables con servicio detenido y sin acceso privado. No se asume que home del perfil Codex y SSH sean idénticos |
| Workspace Horus | Guest `/workspace/projects/mestry-horus-smoke`; código APK mapea `/workspace` a `<filesDir>/horus/workspaces/default` | Ruta física deducida del código del APK cuyo hash coincide; contenido privado actual **SIN ACCESO** |
| Documentos compartidos | `/storage/emulated/0/Documents/Mestry`, ramas Villevault y Villegol, esta última con IPRE/Proyectos | No equivale al bind `/workspace`. Nombres/caso deben conservarse. No se demostró autoridad/ID remoto por nombre |

El APK actual tiene SHA-256 `bf67340c4dd8321636c158902d0bf7b5a4684a23eae982d0026d45e348cb3430`, coincidente con [release oficial1.0.4](https://github.com/scarif-labs/horus/releases/tag/v1.0.4). Su fuente fija `filesDir/horus`, `workspaces/default`, `home`, `harness-homes/<harness>` y binds de guest explícitos. No expone DocumentsProvider ni declara BOOT_COMPLETED; no declara acceso general al almacenamiento Android 16. Fuente y contenido instalado deben distinguirse de ejecución actual.

## 4. Persistencia Codex encontrada/documentada

En el piloto, Horus conserva por separado: archivos del proyecto; estado Codex bajo su home efectivo; bridge en `/home/horus/.local/state/mestry-s25-client` con `state.json`, pairing y proceso; watchdog en `.local/state/mestry-keepalive`. Termux conserva OAuth y journal de publicaciones en `.local/state/mestry-publish`, modo 600 para archivos observados. No se copiaron credenciales ni sesiones.

La configuración actual del navegador Termux conserva la raíz `DRIVE_FOLDER_02_EXAMPLE` asignada al proyecto sintético. El journal del escritor conserva `DRIVE_FOLDER_01_EXAMPLE`, destino histórico posterior en papelera según handoff. No se consultó Drive con esos tokens ni se renovaron. No se presupone igualdad de cuenta con FolderSync/rclone.

El historial persistente no conserva procesos ni devuelve automáticamente una tarea que murió. `state.json` del bridge tampoco es toda la conversación: el código limita eventos locales a500 y recupera historial mediante backend. El cliente S25 es una proyección con caché. Para los dos escenarios de continuidad véase [03](03_PORTABILIDAD_Y_PERSISTENCIA.md).

## 5. Límites y siguiente comprobación necesaria

Los pares/IDs/logs de FolderSync Android siguen bloqueados: DB privada denegada, sin exportación existente encontrada en el directorio de backups examinado. No se activó exportación, UI, API o debug. Un permiso SAF prueba capacidad de acceso a un árbol, **no un par de sincronización**. Una búsqueda amplia Android excedió el tiempo de lectura: se conserva como inconclusa, sin declarar ausentes todos los archivos buscados.

Los cinco congelados Jarvis no reaparecieron en las búsquedas locales acotadas ni en el repo compartido examinado; no se puede concluir ausencia global dentro del teléfono. El ADR Drive conserva hash `02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031`. No se renombró ni alteró.

La consulta pública `status` puede despertar el proceso proveedor Horus: apareció su proceso después, **sin servicio remoto ni backend Codex**. Es una lectura con posible efecto de ciclo de vida, no un arranque de su servicio. No se ejecutaron `start`, pair, instaladores, sincronización, permisos o reinicios. Para confirmar funcionamiento se necesita una fase autorizada de recuperación del servicio y observación del mismo hilo; no otra instalación de Codex.
