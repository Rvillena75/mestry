# MESTRY — Cierre H0: verificación real de los entornos

Fecha: **26 de octubre de 2026**, America/Santiago, UTC−03:00. Las fechas UTC posteriores a las 00:00 del 27/10 corresponden todavía al 26/10 local durante esta auditoría. **Verificación y preparación documental; ninguna implementación H1.**

## A. Resultado ejecutivo

**H0: CERRADA CON LIMITACIONES NO BLOQUEANTES para el laboratorio H1 definido en §H.**

Se inspeccionó el guest real de Horus desde su **Bare terminal**, con el usuario `horus`, `HOME=/home/horus`, Alpine 3.24.0 ARM64/musl y cwd `/workspace/projects`. En ese mismo perfil se ejecutó el Codex ya instalado, se comprobó su estado de autenticación y se verificaron **GitHub API y lectura de referencias Git de un repositorio privado autorizado**. WSL tiene las herramientas y los dos perfiles necesarios. No se necesita instalar paquetes ni recuperar el bridge S25 para iniciar este laboratorio.

El usuario eligió expresamente **«El perfil /home/horus ya verificado, desde Bare terminal o SSH»**. El camino disponible y probado hoy es **Bare terminal**. El SSH que responde actualmente llega a **Termux**, no al guest Horus; el remoto de Horus está deshabilitado. No se presenta SSH Horus como acceso operativo.

La ficha **Codex** de la interfaz usa otro home, `/home/harness_codex`. Su configuración GitHub no está presente y su terminal quedó sin contenido visible. No se atribuyen a ese perfil las pruebas hechas en `/home/horus`; su recuperación queda fuera del H1 elegido. Si se quisiera imponer la ficha nativa como entrada obligatoria, ese alcance requeriría verificación adicional antes de aceptarlo.

Las limitaciones conocidas son concretas: FolderSync S23 devuelve **403 `PERMISSION_DENIED`**, el acceso remoto Horus está apagado y no se acreditó el circuito S25→Codex actual. Además, en S23 falta configurar el **autor Git** para los futuros commits. Son incidencias documentadas, con tratamiento separado; no impiden probar GitHub y Python estándar desde Bare terminal. **H0 no declara lista la operación 24/7, la sincronización documental ni la publicación Git.**

La lectura de un repositorio y sus permisos no acredita crear uno nuevo ni hacer push. Esas escrituras, la identidad local del laboratorio y las pruebas de continuidad quedan reservadas a H1 y requieren aprobación. No hay un bloqueo de autenticación conocido en el perfil seleccionado ni un entorno de ejecución sin identificar.

### Línea base utilizada

Se continúa la [reorientación 09](09_REORIENTACION_CONTINUIDAD_TRABAJO.md), especialmente C, D, F y H0, sin reescribirla. Se conservaron como antecedentes los informes [01](01_AUDITORIA_ENTORNO_CODEX.md), [02](02_MAPA_SINCRONIZACION_REAL.md), [03](03_PORTABILIDAD_Y_PERSISTENCIA.md), [04](04_COMPARACION_ARQUITECTURAS.md), [05](05_ARQUITECTURA_RECOMENDADA.md), [06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md) y [07](07_EVIDENCIAS_Y_LIMITACIONES.md); las cinco auditorías [estado](../../auditorias/2026-10-26/01_ESTADO_ACTUAL_MESTRY.md), [infraestructura](../../auditorias/2026-10-26/02_INFRAESTRUCTURA_Y_SINCRONIZACION.md), [trazabilidad](../../auditorias/2026-10-26/03_TRAZABILIDAD_ARQUITECTONICA.md), [plan](../../auditorias/2026-10-26/04_PLAN_DE_CONTINUIDAD.md) y [evidencias](../../auditorias/2026-10-26/05_EVIDENCIAS_Y_PRUEBAS.md); el [handoff remoto](../../validation/mestry-s23-remote-access-20261022T034500Z/HANDOFF.md) y el [ADR congelado Drive/RAG](../../../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md).

**Convenciones de evidencia:** «actual» identifica una lectura de esta ejecución; «histórico», un resultado anterior no repetido; «usuario», una decisión o dato comunicado; «propuesto», una acción todavía no ejecutada. No se elevan inferencias a comprobaciones.

## B. Estado real de Horus

### B.1. Dispositivos y accesos

Se reutilizó el servidor ADB Windows existente, **PID 10168, puerto 5037**, mediante su protocolo de cliente. No se ejecutó otro servidor ADB, `adb start-server`, instalación de herramientas, `forward` ni `reverse`. Cada operación Android se dirigió por serial y comprobó el modelo esperado.

| Nodo | Serial y modelo actuales | Estado y mecanismo comprobados |
|---|---|---|
| Galaxy S23 Ultra | `S23_SERIAL`, **SM-S918B**, `dm3q` | ADB `device`, autorizado; Android 16/API 36, ARM64. SSH existente `mestry-s23` autentica en Termux con clave ya configurada |
| Galaxy S25 Ultra | `S25_SERIAL`, **SM-S938B**, `pa3q` | ADB `device`, autorizado; Android 16/API 36, ARM64. Inventario de paquetes por ese transporte |

La lectura `host:devices-l` de las **23:16 locales** mostró ambos dispositivos autorizados, con transportes 3 y 6 respectivamente. El SSH Termux devuelve UID **10348**, `u0_a348`, home `/data/data/com.termux/files/home`, arquitectura aarch64 y Python disponible. Se usó `BatchMode=yes`, comprobación estricta de host y `UpdateHostKeys=no`; no se alteró `known_hosts` ni la configuración SSH.

### B.2. Instalación y perfil elegido

| Comprobación actual | Resultado |
|---|---|
| Paquete | `com.scariflabs.horus`, **1.1.0 / versionCode 6**, UID Android **10350** |
| Instalación y actualización | Primera instalación 20/10/2026 16:47:06; última actualización **26/10/2026 21:10:11** |
| Usuario/distribución en interfaz | **Signed in as horus, Alpine**, reconfirmado al volver a la app |
| Guest real | `/etc/alpine-release`: **3.24.0**; arquitectura **aarch64** |
| libc ejecutada | musl **1.2.6**, mediante `/lib/ld-musl-aarch64.so.1` |
| Identidad guest | `uid=1000(horus) gid=1000(horus)`; grupos suplementarios 3003, 9997, 20350, 50350 |
| Directorio actual | `/workspace/projects` |
| Home efectivo | `/home/horus` |
| `CODEX_HOME` | **No definido** en la terminal; directorio de estado predeterminado `/home/horus/.codex` presente |
| Proyecto existente observado | `/workspace/projects/mestry-horus-smoke`; selector «On device» mostraba un proyecto |
| Directorio propuesto H1 | `/workspace/projects/mestry-continuidad-lab`: **ausente**, no creado |

El UID guest no es root Android ni concede acceso entre aplicaciones. Se abrió la terminal configurada y se arrancó/reanudó su sesión Linux normal. No hubo cambio de distro, aprovisionamiento, actualización ni reinstalación. El arranque de la sesión y los cambios de pantalla son efectos de ciclo de vida permitidos por el encargo, no una prueba de ausencia absoluta de escrituras internas de la app.

### B.3. Rootfs, homes y workspace: evidencia dentro del guest

Un proceso Python del propio usuario recorrió metadatos de sus **ancestros** y proyectó únicamente los argumentos de rootfs y binds PRoot pertinentes. No se volcó la línea de comandos completa de procesos ni variables de entorno generales.

| Vista guest | Almacenamiento privado observado |
|---|---|
| `/` | `/data/data/com.scariflabs.horus/files/horus/distro/versions/alpine-3.24.0-aarch64/rootfs` |
| `/home/horus` | `/data/data/com.scariflabs.horus/files/horus/home` |
| `/workspace` | `/data/data/com.scariflabs.horus/files/horus/workspaces/default` |
| `/home/harness_codex` | `/data/data/com.scariflabs.horus/files/horus/harness-homes/codex` |

Los binds de Claude y OpenCode se observaron como homes distintos; no se inventariaron sus credenciales. Las rutas físicas se conocieron **desde el entorno legítimo Horus**. WSL/Termux no entraron en el almacenamiento privado de otra aplicación; no se usaron root, `run-as`, cambios de UID ni mecanismos para eludir el aislamiento.

### B.4. Herramientas y dependencias

| Herramienta en `/home/horus` | Resultado actual y alcance |
|---|---|
| Codex | **0.163.0**, ejecutado con `/home/horus/.local/bin/codex --version` |
| Estado de login Codex | `Logged in using ChatGPT`, retorno 0; sin inferencia ni hilo nuevo |
| Node / npm | **v24.18.1 / 11.12.1** |
| Python | **3.14.8**; imports `ssl`, `sqlite3`, `venv`, `json`, `unittest` correctos |
| Git | **2.54.0** |
| GitHub CLI | **2.97.0**, compilación indicada 2026-10-14 |
| Otras herramientas resueltas | `bash`, `zsh`, `tar`, `sha256sum`, `flock`, `ssh`, `sftp`, `rsync` |
| No resueltas en ese PATH | `cc`, `gcc`, `make`, `rclone`; no se afirma ausencia en todos los perfiles o el rootfs |
| Autor Git | `user.name` y `user.email` **sin valor efectivo**; consultas individuales retornaron 1 |

Se inspeccionó el launcher ya instalado: ejecuta `/usr/bin/node` con `/home/horus/.local/lib/node_modules/@openai/codex/bin/codex.js`. La función de shell `codex` añade actualmente `--sandbox danger-full-access --no-daemon`; no se cambió. En H1 se documentará el ejecutable concreto y su política de ejecución, sin asumir que otra entrada equivale a él.

**Precaución concreta:** `/usr/local/bin/codex` apunta al stub `horus-agent-stub`, que puede llamar a `install-agent codex`. **Ese stub no se ejecutó.** H1 debe usar el launcher verificado `/home/horus/.local/bin/codex`, no probar un binario ambiguo para averiguar si instala algo.

La importación de biblioteca estándar acredita herramientas suficientes para el fixture Python de H1. No acredita compiladores, todos los paquetes de MESTRY ni todos los proyectos ARM64/musl. En `/home/horus/.venv` y `/home/horus/node_modules` no había directorios; esto no equivale a ausencia de dependencias en otros proyectos. Una comprobación final en `mestry-horus-smoke` encontró ausentes exactamente estas rutas: `.git`, `pyproject.toml`, `requirements.txt`, `package.json`, `package-lock.json`, `uv.lock`, `.venv`, `venv`, `node_modules`. No se inspeccionaron indiscriminadamente otros proyectos ni contenidos de datos. No se ejecutó `pip`, `npm install`, `npm ci`, `apk`, ni un build.

Se conserva **Alpine**: Git/gh/Codex y el Python requerido funcionan en el perfil elegido. H0 no obtuvo una necesidad de Debian para H1. Una dependencia nativa futura deberá evaluarse por proyecto y plataforma, sin mover `.venv`, `node_modules` o binarios x86/glibc entre máquinas.

### B.5. Persistencia y límites funcionales

| Clase | Evidencia actual | Lo que no se presume |
|---|---|---|
| Archivos del proyecto | `mestry-horus-smoke` sigue presente; directorios con metadatos de 20–21/10 | No se ejecutaron otra vez sus tareas históricas ni se atribuye integridad a todos sus bytes |
| Estado Codex | `.codex`, `config.toml`, `auth.json` y `sessions` presentes; config/auth con modo 0600 | Solo metadatos de archivos sensibles; ningún contenido de auth o conversación leído |
| Codex instalado | Launcher y paquete presentes; `--version` y `login status` correctos | No se ejecutó inferencia; no se acredita cada herramienta del agente |
| Configuración MESTRY previa | `.local/state/mestry-s25-client` y `.local/state/mestry-keepalive` presentes, modo 0700 | Presencia no prueba bridge o watchdog saludables |
| Servicio remoto Horus | Interfaz: **Off**, sin escucha; configuración previa conserva un equipo emparejado | No se activó ni se revisaron claves |
| Puertos locales desde Termux | `127.0.0.1:8022` y `127.0.0.1:8787`: conexión rechazada, código 111 | No se confunde SSH Termux operativo con SSH Horus o bridge operativo |

Se acredita conservación observable después de la actualización, por comparación con las rutas históricas y la ejecución actual del CLI. No se provocó reinicio, cierre forzado, cambio de usuario ni actualización adicional para ensayar persistencia.

### B.6. Perfil separado de la ficha Codex

`/home/harness_codex` y su `.codex` existen con modo 0700. Su `auth.json` está presente con modo 0600 y metadatos previos; no se leyó su contenido. El launcher local y el paquete reportan **0.163.0 por metadatos**. La comprobación de preparación se reprodujo en lectura según la implementación oficial: **`NATIVE_READY_STAMP_MATCH=True`**, y `/bin/ps` regular, no symlink. Este marcador solo evitó confundir la apertura con un aprovisionamiento pendiente; no prueba ejecución del agente.

No están presentes `.config/gh` ni `.gitconfig` en ese home. **No se ejecutó allí una llamada GitHub autenticada**: ausencia de esos archivos no demuestra por sí sola denegación, porque podrían existir otros mecanismos. Después de abrir la ficha normalmente, la superficie terminal quedó vacía, sin error ni instalación visibles. No se enviaron prompts, comandos ni autenticaciones a esa superficie.

El código fijado de Horus 1.1.0 distingue homes de harness, home Bare y workspace; la separación observada coincide con él. Esto explica por qué el login GitHub de la interfaz no debe extrapolarse a cualquier ficha. [Fábrica de sesiones oficial, commit fijado](https://github.com/scarif-labs/horus/blob/76da90789f039fe7ee796ae4ec44c1628fda2031/android/app/src/main/java/com/scariflabs/horus/terminal/TerminalSessionSpecFactory.kt).

**Decisión de alcance del usuario:** usar `/home/horus`. No se copiaron credenciales al harness ni se intentó reparar su pantalla. Queda como pendiente de integración de la ficha nativa, si se decide utilizarla más adelante.

## C. GitHub: verificación de autenticación y acceso

### C.1. Perfil S23 admitido para H1

Las siguientes pruebas se ejecutaron **en Bare terminal, `HOME=/home/horus`**, donde el Codex verificado ejecuta comandos. No proceden de Termux ni de WSL.

| Prueba de lectura | Resultado concreto |
|---|---|
| `gh api user` con proyección constante | `H0_GH_LOGIN_OK`; API autenticada responde |
| Metadatos de un repositorio propio autorizado | `app_gastos`, **privado**, rama predeterminada **main** |
| `permissions` del repositorio | `pull=true`, `push=true`, `admin=true`, `maintain=true`, `triage=true` |
| `git ls-remote --heads … refs/heads/main` | Retorno **0**, ref `refs/heads/main` obtenida |
| Commit de esa ref | `4dbaeaeb8ec2b15205b7c34235a87dfde02bdb2c` |
| Helper Git efectivo | Consulta acotada confirma **`gh auth git-credential`**; se imprimió solo `GH_HELPER=yes` |
| Correspondencia cuenta/perfil | La comparación de `gh api user` con la cuenta de la interfaz devolvió **true**, retorno 0, sin imprimir el login |
| Scopes declarados por GitHub | Solo cabecera `X-OAuth-Scopes`: **`gist, read:org, repo, workflow`**, retorno 0; ningún token ni cuerpo de usuario publicado |

Identidad del remoto, saneada: **`https://github.com/<cuenta autorizada>/app_gastos.git`**. No contenía credenciales incrustadas. Se omite el identificador personal de la cuenta en este informe. La UI mostraba la cuenta conectada y un listado de 39 repositorios; no se vuelca ese catálogo ni se usan repos ajenos como fixtures.

**Respuesta a la pregunta principal:** sí, el Codex instalado bajo `/home/horus` dispone de **Git y gh funcionales y acceso Git de lectura a GitHub**, con el helper de ese mismo perfil. Las pruebas reales son API autenticada y lectura de la referencia privada. No se basa en el icono «GitHub conectado».

**Escritura:** `permissions.push=true` es un permiso declarado sobre el repositorio consultado. Los scopes describen la autorización que reportó la API; no prueban publicación efectiva, creación de repositorios bajo cualquier propietario, acceso a toda organización o ausencia de restricciones de ramas. No se cambiaron ni ampliaron. **No hubo clone, fetch, pull, commit ni push.**

No hay repositorio MESTRY según confirmación previa del usuario; H0 no crea ninguno. El repositorio privado consultado conserva sus referencias y contenido; no se utiliza para pruebas futuras de escritura.

### C.2. WSL es otra autenticación

En WSL también respondieron `gh api user`, los metadatos del mismo repositorio permitido y `git ls-remote` con retorno 0 y una ref. El helper específico de GitHub es gh; no hay helper genérico configurado. Una comparación booleana con la identidad mostrada por Horus dio verdadero, sin imprimir nombre o token. Esto no implica que compartan archivos de autenticación ni que un login sane al otro entorno.

La configuración gh de WSL conservó sus bytes antes/después de la lectura comprobada. No se copiaron credenciales, no se llamó `gh auth token`, `git credential fill`, `gh auth login` ni `gh auth setup-git`. Los comandos de API imprimieron campos permitidos, no respuestas completas de usuario/cuenta.

Las cuentas **ChatGPT/Codex** y la identidad **GitHub** cumplen funciones distintas. Dos cuentas Codex pueden usar por turnos el mismo proyecto y el Git autorizado del usuario Unix. La atribución del commit depende de `user.name/email`, sin dar permisos remotos por sí misma.

## D. FolderSync S23: pares, políticas y resultados

### D.1. Método y alcance

FolderSync **4.14.0**, paquete `dk.tacit.android.foldersync.lite`. Se abrió su actividad existente y se recorrieron lista de pares, ajustes del par, programación, opciones, filtros, conexión, historial y detalle de error mediante la interfaz oficial. La lista «Todo» mostró **un par**. No se accedió a su DB privada ni se exportó configuración con posibles secretos.

Los controles personalizados no exponían de forma fiable el valor de checkbox en el árbol de accesibilidad. Los valores indicados abajo se cotejaron **visualmente**, sin pulsar las casillas. Se descartaron lecturas de accesibilidad que por sí solas no acreditaban esos valores. Se cerraron anuncios intersticiales mediante Atrás/cerrar; no se activaron anuncios ni compras.

### D.2. Tabla completa del par observado

| Campo solicitado | `S23 <> Google Drive` | Evidencia o límite |
|---|---|---|
| 1. Nombre | **S23 <> Google Drive** | Lista y detalle |
| 2. Directorio local | **`/storage/emulated/0/Documents/Mestry/`** | General |
| 3. Servicio remoto | **Google Drive** | General/lista; identidad de cuenta no publicada |
| 4. Carpeta remota / ID | Ruta mostrada **`/MESTRY/`**; **ID no verificado** | La vista consultada no expone ID. No se infiere de nombres ni se exportan credenciales para conseguirlo |
| 5. Dirección | **Bidireccional / TwoWay** | Lista y General |
| 6. Frecuencia/disparadores | **Default Schedule**, habilitado, cada **1 hora**; sincronización instantánea desactivada | Programación y Opciones. Automatizaciones adicionales: véase D.3 |
| 7. Exclusiones/filtros | **Sin filtros**: «No se han encontrado filtros»; «No sincronizar carpetas vacías» activado | Filtros y Opciones; no implica que `.git` o secretos estén excluidos |
| 8. Eliminación | **Sincronizar eliminaciones: activado**; «eliminaciones después de transferencias»: desactivado | Opciones. Política separada de papelera/retención no visible en las pantallas inspeccionadas: **no verificada** |
| 9. Conflictos | **Omitir archivo** | Selector visible cuando ambos lados han cambiado |
| 10. Sobrescritura | Etiqueta exacta **«Sobrescribir archivos antiguos» = «Siempre»** | No se convierte esta etiqueta en una promesa de conservar todas las revisiones |
| 11. Red/energía | Valores separados para horario y ejecución manual: D.3 | No se presume una única regla para ambos modos |
| 12. Última ejecución | A las **23:44** seguía «Sincronizando», duración **44m 5s**, siguiente **27/10 00:00** | Ejecución del horario preexistente de las 23:00, no iniciada por esta auditoría |
| 13. Último resultado completado mostrado | **26/10 21:00, SyncFailed**, duración **1h 0m 3s**, disparador **Horario** | Historial y detalle; 0 comprobados, 0 sincronizados, 0 eliminados, 0 B |
| 14. Error pendiente | **403 / PERMISSION_DENIED / forbidden** por identidad de consumidor API no establecida | «Más información», transcripción saneada en D.4; ejecución actual sin resultado final en la muestra |
| 15. Estado | **Habilitado** | Control «Desactivar» y siguiente ejecución visibles |

Otras opciones observadas: verificación de checksum **desactivada**; comprobación de tamaño y de espacio libre **no desactivadas**; comprobación rápida de cambios remotos activada; transferencia con archivos temporales desactivada; excluir el par de «sincronizar todos» desactivado; demora inicial 0; prioridad predeterminada. Las opciones exclusivas de una vía y los backups con timestamp estaban inactivos/no habilitados. No se atribuye a esas opciones un mecanismo de backup aceptado.

### D.3. Red, energía y automatización

| Ajuste | Horario `Default Schedule` | Manual/automatización del par |
|---|---|---|
| Cualquier conexión disponible | **Sí** | No |
| Wi-Fi | **Sí** | **Sí** |
| Datos móviles / Ethernet | No / No | No / No |
| Requiere VPN | No | No |
| Roaming / conexión medida | No / No | No / No |
| Requiere carga | No | No |
| SSID permitidos | Vacío | Vacío |
| SSID no permitidos | Vacío | Vacío, confirmado al recorrer el final de la sección |
| Omitir error de conexión al inicio | No | No se extrapola el ajuste del horario |

La propia pantalla de conexión del par aclara que los trabajos programados usan su horario; las opciones de esa pantalla aplican a ejecución manual/automatizada. Con «cualquier conexión» y Wi-Fi marcados a la vez en el horario, **no se asegura que el horario sea Wi-Fi exclusivo** sin prueba específica.

Al completar la inspección de la sección manual/automatización, las tres casillas de notificación por **éxito, cambios y error** estaban desmarcadas. Es una observación de esa sección, no una prueba de todos los canales de avisos de Android o de cada horario. Se descartó interpretar los checkboxes vacíos del árbol de accesibilidad sin cotejo visual.

Se abrió la pestaña global **Automatización**: mostró **«Esta es una función premium» / «Actualizar a Premium»**. No se cambió licencia ni se accedió a un listado de eventos. Por tanto, **no se certifica ausencia de otros eventos**; el disparador horario sí está acreditado en configuración e historial. La indisponibilidad de esta pantalla no afecta las rutas privadas del laboratorio GitHub.

### D.4. Fallo encontrado y tratamiento

En el último fallo completado, «Más información» mostró código **403**, estado **PERMISSION_DENIED**, razón **forbidden** y este mensaje saneado:

> Method doesn't allow unregistered callers (callers without established identity).

La respuesta también pedía una forma de identidad de consumidor API. **Eso describe el rechazo observado; no acredita que falte una API key personal ni justifica crearla.** No se determinó si la causa interna corresponde a sesión de cuenta, cliente/API de la aplicación u otra condición del proveedor. No se culpa al espacio disponible ni se identifica un fallo de permisos de carpeta sin evidencia.

Otros resultados visibles: **26/10 20:00, SyncFailed**, 26m 39s, 0 comprobados/0 B; **23/10 22:00, SyncOK**, 7m 16s, chequeo rápido sin cambios, 0 B. El éxito antiguo no sanea el fallo actual ni prueba que todos los documentos estén vigentes.

Durante la auditoría se alcanzó el horario ya existente de las **23:00**. A las 23:29 y las **23:44** el par seguía en ejecución con contadores **0/0**. **No se pulsó sincronizar, analizar, cancelar ni desactivar.** No se esperó su final ni se alteró el planificador. La inspección no constituye autorización para reautenticar, detener el trabajo o cambiar políticas de borrado.

Acción posterior mínima: revisar de forma legítima el estado no secreto de esa cuenta en FolderSync y su diagnóstico del proveedor; si se exige reautorizar o modificar algo, solicitar aprobación concreta. Después, validar sobre un par/área sintética aprobada. **No probar la reparación ejecutando primero el TwoWay global sobre documentos reales.**

### D.5. Rutas y solapamientos

| Árbol | Sincronizador/autoridad actual | Relación con H1 |
|---|---|---|
| Horus privado, `/workspace/projects` | Ningún par FolderSync observado apunta aquí | H1 permanece dentro del almacenamiento privado, fuera de `Documents/Mestry` |
| S23 `Documents/Mestry` | Par TwoWay a `/MESTRY/`, sin filtros, propaga borrados | Documentación compartida; no se usará como checkout |
| S23 `Documents/Mestry/Villegol/Proyectos/mestry` | Copia compartida existente, sin `.git` | No es el workspace privado Horus; ADR con hash igual al WSL |
| WSL `/home/developer/proyectos` | Raíz del script rclone bisync existente | Incluye el árbol actual de este informe, por lo que no debe recibir el futuro checkout vivo |
| WSL `/home/developer/IPRE` | Segunda raíz bisync existente | Fuera del laboratorio propuesto |
| Windows `C:\Users\<perfil>\Villevault\` | Par Desktop TwoWay a `/MESTRY/Villevault/` | Ruta NTFS distinta del laboratorio WSL |

Identificadores leídos de configuraciones existentes: raíz rclone `proyectos` **`DRIVE_ID_08_EXAMPLE`**, raíz `IPRE` **`DRIVE_ID_05_EXAMPLE`** y destino FolderSync Desktop **`DRIVE_ID_07_EXAMPLE`**. Son IDs de carpetas, no credenciales. **El ID del par Android no fue expuesto**, de modo que no se declara reconciliada la identidad o jerarquía de todos los destinos Drive únicamente por sus etiquetas.

El hash actual del ADR tanto en la copia compartida S23 como en WSL es **`02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031`**. Acredita igualdad de ese archivo, no una sincronización integral ni el estado actual en Drive.

Existe riesgo documental de solapamiento por las rutas remotas mostradas y el alcance amplio de los pares actuales. Para H1 se elimina la exposición seleccionando **rutas nuevas fuera de todas las raíces locales conocidas**. La conciliación Drive por IDs y la política de única autoridad pertenecen a H4; no se cambió aquí el ADR, filtros ni pares.

## E. Windows, WSL y S25

### E.1. Herramientas y perfiles WSL

| Elemento actual | Resultado |
|---|---|
| Git / GitHub CLI | **2.43.0 / 2.45.0**; API y lectura de ref privada correctas |
| Python / Node / npm | **3.12.3 / 22.23.1 / 10.9.8** |
| Codex instalado | Paquete **0.164.0**; no se lanzó inferencia |
| Herramientas auxiliares | Bash 5.2.21, SSH, `flock`, rclone disponibles |
| Proyecto actual | `/home/developer/proyectos/mestry`, **sin `.git`** |
| Perfil A | `/home/developer/.codex` existente |
| Perfil B | `/home/developer/.codex-account-2` existente; perfil de esta sesión |
| Sesión observada | `CODEX_HOME=/home/developer/.codex-account-2`, cwd `/home/developer/proyectos/mestry` |
| Launcher segundo perfil | `/home/developer/.local/bin/codex2`, selecciona ese `CODEX_HOME` y conserva cwd; leído, no ejecutado |
| Autor Git WSL | `user.name` y `user.email` configurados; valores personales no publicados |

Los dos `auth.json` son archivos regulares **distintos**, sin symlink compartido; sus directorios `sessions` también son distintos. No se leyeron autenticaciones ni conversaciones ni se validó el login de ambas cuentas mediante inferencia. La existencia de dos perfiles no prueba por sí sola dos cuentas vigentes: ese dato proviene del usuario.

`config.toml`, reglas, skills, plugins y paquetes del segundo perfil enlazan al primero mediante symlinks. Es configuración compartida existente, **no una autorización para sincronizar homes**. Se documenta porque separa la autenticación y sesiones observadas de la configuración reutilizada. No se alteraron los enlaces.

Solo se observó una sesión activa de Codex sobre este cwd. El launcher revisado no hace `cd`; ambas cuentas pueden abrir el mismo proyecto por turnos, pero no se simuló su concurrencia ni se afirma que Git evite sobrescrituras entre procesos del mismo workspace. H1 comprobará el uso secuencial y reservará worktrees para concurrencia.

### E.2. rclone y FolderSync Desktop

Se leyó `/home/developer/sincronizar-mestry.sh` y su filtro, sin ejecutarlos. `node_modules`, `.venv`, `venv` y caches están excluidos; no hay una protección general equivalente para `.git`, todos los secretos o todas las compilaciones. El parámetro existente **`--max-delete 20` significa 20%**, no veinte archivos. El modo preview/init contiene caminos `--resync`: **no se invocó ninguno**.

FolderSync Desktop se consultó mediante SQLite **`mode=ro&immutable=1` y `query_only`**, sobre su DB existente bajo el LocalCache de la app Windows. No se exportó/copió la DB ni se ejecutó checkpoint; una vista immutable no acredita incorporar cualquier cambio que estuviera pendiente en WAL.

La vista leída contiene un par habilitado `Local filesystem <> Google Drive`, local `Villevault`, destino Drive ID indicado en D.5, **TwoWay**, último estado **SyncFailed**, última ejecución registrada **23/10 01:03:21** local. Eliminaciones desactivadas, papelera activada, conflicto `Skip`, reemplazo `ReplaceIfNewer`, checksums desactivados, sin filtros. Tres horarios figuran habilitados: uno con cron `0 12 * * *` y dos sin cron; no se inventa una frecuencia para los vacíos. La configuración leída permite Wi-Fi, no móvil, sin exigir VPN ni carga.

Esta consulta aclara el riesgo de rutas y políticas; no acredita salud actual del servicio Desktop ni soluciona Drive. El laboratorio Git no depende de él.

### E.3. S25: disponibilidad, no recuperación del bridge

| Componente actual S25 | Resultado |
|---|---|
| Cliente MESTRY | `com.haochen.codexremote.mestrypilot`, **0.2.0-mestry-pilot8 / versionCode 10008**, instalado; última actualización 22/10 01:23:23 |
| ConnectBot | **v1.11.1 / 11101000**, instalado |
| Tailscale | **1.104.2**, instalado en ambos teléfonos |
| Always-on / lockdown S25 | Ambos **null**, sin modificar |
| S23 VPN previa | Always-on Tailscale, lockdown 0, sin modificar |
| Remoto actual extremo a extremo | **No acreditado**; Horus remoto Off y bridge 8787 no responde |

Las configuraciones de emparejamiento y las pruebas celulares del handoff son **históricas**. Paquetes y metadatos actuales no acreditan vigencia de claves, túnel, hello o historial. No se abrió el cliente MESTRY para evitar su posible automatismo de VPN; no se cambiaron VPN, claves ni emparejamientos. No se ejecutaron tareas Codex desde S25.

Es una condición de disponibilidad para **H3/H5**, no un requisito para el H1 por terminal autorizado. No hace falta añadir otro backend en S25 ni conectar Windows a la misma conversación.

## F. Matriz de aceptación H0

| Criterio | Estado | Evidencia actual y observaciones |
|---|---|---|
| **H0-01** Dispositivos y acceso autorizado | **VERIFICADO** | Dos seriales/modelos `device` por servidor existente; SSH Termux S23 autenticado. Acceso remoto Codex desde S25 se registra aparte, no se presume |
| **H0-02** Versión/distribución Horus | **VERIFICADO** | Paquete 1.1.0/6; UI horus/Alpine y Alpine 3.24.0 dentro del guest |
| **H0-03** Entorno Alpine real | **VERIFICADO** | `pwd`, `id`, HOME, aarch64, release y musl ejecutados dentro de Bare terminal |
| **H0-04** Rutas/home Codex | **VERIFICADO** | `/home/horus`, `.codex`, launcher y binds reales; harness separado identificado; elección explícita del usuario |
| **H0-05** Herramientas | **VERIFICADO** | Versiones ejecutadas, herramientas resueltas y faltantes por PATH; imports Python. No equivale a reproducir todos los proyectos |
| **H0-06** Autenticación GitHub del perfil elegido | **VERIFICADO** | `gh api user` y helper Git en `/home/horus`; no extrapolado al harness |
| **H0-07** Lectura y permisos repo | **VERIFICADO** | Repo privado, main, permissions completos y `ls-remote` retorno 0. Push efectivo explícitamente reservado a H1 |
| **H0-08** FolderSync S23 | **VERIFICADO PARCIALMENTE** | Un par y políticas principales, horario, filtros, conexión completa, historial y 403 leídos. ID no expuesto; política separada de papelera no visible; Automatización bloqueada por pantalla premium. Límites individualizados en D |
| **H0-09** Workspace frente a sincronizadores | **VERIFICADO** | Bind privado Horus distinto de `Documents/Mestry`; raíces rclone/Desktop conocidas; rutas H1 fuera. Identidad global Drive por IDs pendiente H4 |
| **H0-10** WSL preparado documentalmente | **VERIFICADO** | Git/gh/Python, perfiles/metadatos, launcher/cwd, autor y GitHub leídos; rutas nuevas ausentes y propuestas, sin crearlas |
| **H0-11** Riesgos/bloqueos H1 | **VERIFICADO** | Sin bloqueo técnico conocido para H1 seleccionado; autor Git S23 pendiente de configuración aprobada; limitaciones nativa/Drive/remoto separadas |
| **H0-12** Procedimiento H1 actualizado | **VERIFICADO** | §H fija paths, perfil, comandos, archivos, aprobaciones, pruebas negativas, aceptación y rollback sin tocar datos reales |

**Motivo del cierre:** las comprobaciones indispensables de entorno, perfil y acceso GitHub sí tienen evidencia de ejecución. El único criterio parcial trata campos documentales que no gobiernan el laboratorio fuera de los pares. La exclusión de la ficha nativa está respaldada por la elección del usuario, no por atribuirle ficticiamente autenticación o funcionamiento. Ninguna prueba de publicación se marca como realizada.

## G. Bloqueos, riesgos y próximos límites

| Hallazgo | Impacto real | Acción mínima y fase |
|---|---|---|
| Falta autor Git S23 | Precondición conocida para commits H1 | Aprobar nombre/email de autor y configurarlos **solo en el repo laboratorio**. No toca login/credenciales ni necesita instalar |
| No existe remoto laboratorio | Escritura todavía no autorizada | Aprobar propietario y repo privado sintético; crearlo en H1 o que el usuario entregue uno vacío. La capacidad de creación/publicación se prueba entonces |
| Ficha Codex nativa sin GitHub acreditado/pantalla vacía | **No bloquea H1 elegido** | Mantener Bare `/home/horus`; diagnosticar la ficha solo si se quiere adoptar, sin copiar credenciales |
| SSH Horus Off y bridge cerrado | Impide acreditar operación remota S25 actual | H3/H5: autorización específica para recuperar servicios existentes; conservar claves/puertos/emparejamientos |
| FolderSync 403 y sync en curso sin resultado final | No se puede aceptar vigencia documental | H4: diagnóstico de cuenta/proveedor y eventual reautorización aprobada; no ejecutar TwoWay global como primera prueba |
| Borrados Android activados, sin filtros, checksum desactivado | Riesgo para documentos/checkout si se mezclan rutas | H1 fuera de pares; revisión y modificación de políticas solo en H4 con autorización |
| ID Android/jerarquía Drive sin conciliar | No se certifica un único flujo documental | H4: obtener ID legítimo y contrastar padres/destinos; nombres no bastan |
| Dos agentes en mismo checkout | Sobrescritura posible aun con Git | Uso secuencial; para simultaneidad worktrees/rama por agente. No auto-pull durante pruebas o edición |
| Alpine musl/ARM64 frente a WSL x86 | Compatibilidad depende del proyecto | H1 stdlib, sin instalación; proyectos posteriores con receta/locks y pruebas por target |
| Disponibilidad con PC apagado | No probada por estar conectado por USB | H5: alimentación independiente, reposo y observación prolongada aprobados. No reiniciar ni detener ahora |

**Para empezar H1 no hace falta** reparar FolderSync, activar remoto Horus, recuperar S25, migrar distro ni instalar herramientas. Sí hace falta la aprobación limitada de las escrituras de §H y acordar la identidad Git local. Si la autorización para crear el repo resulta insuficiente, detener esa creación y solicitar al usuario un remoto vacío autorizado; no ampliar scopes por cuenta propia.

## H. Preparación concreta de H1

### H.1. Alcance para aprobar

| Elemento | Propuesta concreta, todavía no creada |
|---|---|
| Clon/laboratorio WSL | **`/home/developer/mestry-lab/continuidad-trabajo-v1`**, fuera de `proyectos`, `IPRE` y Villevault |
| Clon S23 | **`/workspace/projects/mestry-continuidad-lab`**, dentro de Horus privado |
| Área auxiliar de concurrencia WSL | **`/home/developer/mestry-lab/continuidad-trabajo-v1-aux`**, solo para los worktrees del caso concurrente; creación también sujeta a aprobación y comprobación previa de ausencia |
| Perfil S23 | **`/home/horus` desde Bare terminal**; launcher Codex absoluto verificado. SSH solo después de recuperación autorizada, no necesario H1 |
| Remoto | Repo privado sintético **`mestry-continuidad-lab`**, propietario por aprobar; no usar `app_gastos` ni el futuro MESTRY real |
| Autor | WSL tiene autor; S23 requiere nombre/email acordados, idealmente noreply del usuario si lo decide; configuración **local del lab** |
| Herramientas | Git/gh y Python ya disponibles; sin gestores de paquetes, sin compiler, sin librerías externas |
| Datos | Enteros ficticios, texto técnico y un falso secreto inocuo; nada de corpus, credenciales reales, históricos Codex o archivos privados |

Archivos propuestos del laboratorio: `calc.py`, `test_calc.py` con `unittest`, `README.md`, `AGENTS.md`, `STATUS.md`, `.gitignore`, `.gitattributes`, `tools/lab-start.sh`, `tools/lab-finish.sh` y `tools/lab-status.sh`. El estado debe registrar implementado, pendiente, pruebas **por target**, problema conocido y siguiente tarea; no transcribir conversaciones. Estos archivos no se han escrito durante H0.

La aprobación H1 debe cubrir creación del remoto privado y directorios de laboratorio, clones, configuración local de autor, ramas/worktrees **de laboratorio**, commits y pushes normales **solo allí**, y scripts con escrituras restringidas a ese alcance. Si se desea comprobar agentes reales con ambas cuentas, debe incluir turnos Codex de alcance sintético; sin ellos se informa validación de Git/runtime, no una ejecución de continuidad entre agentes.

No se requiere aprobar cambios en proyectos reales, rclone/FolderSync, permisos Android, instalaciones, homes, servicios, VPN, credenciales ni arquitectura congelada. Eliminar posteriormente el remoto o directorios tampoco queda implícitamente autorizado por crear el laboratorio.

### H.2. Secuencia y aceptación del laboratorio

1. **Preflight.** Revalidar serial/modelo y perfil; comprobar que las rutas están vacías/ausentes y no son symlinks hacia datos existentes. Si contienen datos, detenerse y proponer otra ruta. Verificar API/helper, identidad Git y remoto. En S23 evitar `/usr/local/bin/codex` installer. No se necesita repetir la auditoría completa.
2. **Base sintética.** Crear solamente lo aprobado, revisar archivos y permisos, ignores y EOL, y ejecutar `python3 -B -m unittest -v` en cada plataforma. Registrar Git/gh/Python, commit y salida por separado. No copiar dependencias.
3. **WSL→GitHub→S23.** Una sesión WSL modifica función/prueba/STATUS. Seleccionar rutas explícitas para staging, revisar diff del índice y posibles secretos, ejecutar pruebas y publicar el conjunto terminado. Comprobar SHA remoto con `git ls-remote`; en S23 recibir solo libre/limpio, ejecutar prueba y confirmar el mismo commit. Un hilo nuevo debe identificar la siguiente tarea leyendo archivos.
4. **S23→GitHub→WSL.** Desde `/home/horus`, completar otra modificación y publicar con el Git configurado de ese perfil. La otra cuenta Codex WSL abre **el mismo cwd por turno**, lee estado/historia, recibe y valida. No compartir auth, sessions, hilos ni credenciales entre cuentas. Para un ensayo con PC realmente apagado, reservar ventana/alcance de H5 o aprobarla por separado.
5. **Cambios pendientes.** Casos separados de tracked modificado, staged y archivo nuevo sin seguimiento: el receptor rechaza aplicar cambios y deja evidencia, sin auto-stash/reset/clean. El cierre no convierte todo cambio en commit. Un temporal y `.env` sintético no deben entrar en el índice; la allowlist/revisión debe impedir su publicación incluso ante un intento de `add -f`.
6. **Concurrencia y divergencia.** Un árbol limpio con una prueba/proceso activo sigue ocupado; solo fetch/aviso, sin alterar su working tree. Simular dos historias en clones del lab: el segundo push normal debe rechazarse y conservar ambos commits. Resolver explícitamente en rama y repetir pruebas. Si hay agentes WSL simultáneos, worktree separado, no dos escritores sobre el mismo directorio.
7. **Conectividad y confirmación.** Usar un remoto/URL de prueba inválido solo dentro del lab para provocar error sin parar red/servicios. Distinguir commit local, publicación, recepción y ejecución. Si el resultado de envío es incierto, consultar ref remota antes de reintentar, sin crear commits duplicados ni force-push.
8. **Dependencias y límites.** El fixture stdlib solo acepta ese contrato. Una ampliación con locks o dependencias necesita receta por target; cualquier candidato se prepara aparte y conserva el entorno operativo. La prueba de instalaciones o un área Drive sintética se autoriza aparte si supera este alcance mínimo; no es prerrequisito de la ida/vuelta Git.

Comandos de lectura que pueden reutilizarse en los clones H1:

```bash
git status --porcelain=v1 --untracked-files=all
git diff --check
git diff --cached --stat
git diff --cached
git rev-parse HEAD
git ls-remote --heads origin refs/heads/main
python3 -B -m unittest -v
```

Estos comandos no forman un publicador automático completo. El preflight también comprueba operaciones Git incompletas, upstream/ramas y uso del proyecto; **un status limpio no equivale a inactividad**. Git 2.43 WSL y 2.54 S23 no necesitan compartir defaults: cualquier integración futura deberá usar explícitamente `--ff-only` cuando corresponda. No se ejecutó pull durante H0.

La automatización H1 empezará por acciones explícitas **iniciar / finalizar y publicar**, con bloqueo local cooperativo y revisión de rutas. No se añadirá cron, servicio ni hook de apagado. La automatización periódica S23 se reserva a H3, inicialmente fetch/aviso hasta cubrir los puntos de entrada que puedan escribir o ejecutar pruebas. Un proceso del mismo UID que ignore el procedimiento no queda aislado por ese bloqueo.

### H.3. Evidencia, aceptación y rollback

**Aceptar H1** únicamente con: commits/ref remota comprobados en ambos sentidos, igualdad de archivos del fixture y pruebas reales en ambos targets; segunda cuenta WSL operando por turno sin compartir conversaciones; rechazo seguro de dirty/untracked/divergencia/uso activo; ausencia del falso secreto y temporales en Git; y estado final que enumere cualquier pendiente. Push declarado por API no sustituye estas pruebas.

Riesgos: publicar un archivo indebido, elegir un remoto erróneo, modificar un checkout ocupado o confundir homes. Controles: nombres/paths aprobados, repo privado dedicado, staging explícito, revisión del índice, validación de remoto/usuario/home, pruebas por target y ausencia de escrituras fuera del lab.

**Rollback:** detener únicamente el uso de los scripts nuevos del laboratorio, conservar clones, ramas, commits y evidencia; mantener operativo el entorno original. Ningún reset destructivo, force-push, borrado de home, migración, eliminación del remoto ni restauración de datos reales. Si alguna limpieza requiere borrar el laboratorio/remoto, presentar lista y pedir autorización específica.

## I. Registro de evidencias y preservación

### I.1. Lecturas ejecutadas y salidas saneadas

Todas las evidencias de dispositivo de esta tabla corresponden al **26/10/2026 local** durante H0. Las últimas lecturas de transporte se hicieron a las 23:16, la lectura final de Bare terminal a las **23:40**, el progreso FolderSync a las 23:44 y el final de su configuración de conexión a las **23:47**. En Bare se reconfirmó `/home/horus`, cwd `/workspace/projects`, coincidencia de cuenta GitHub y scopes. Los comandos siguientes se agrupan por finalidad; las salidas no incluyen tokens, correos, conversaciones o claves.

| ID | Dispositivo / método | Comandos o consulta ejecutada | Resultado utilizado |
|---|---|---|---|
| H0-E01 | Windows ADB existente | Protocolo `host:devices-l`; `getprop ro.product.model`, SDK/ABI | Ambos seriales autorizados y diferenciados; no autostart |
| H0-E02 | S23/S25 ADB | `dumpsys package` con proyección de versión/UID/fechas; ajustes VPN acotados | Versiones de Horus/FolderSync/cliente/ConnectBot/Tailscale y disponibilidad observada |
| H0-E03 | SSH existente S23 Termux | `id`, HOME, `uname -m`, resolución de Python; conexiones loopback con `socket.connect_ex` | SSH Termux válido; puertos Horus/bridge rechazados, sin escaneo ni cambios de servicios |
| H0-E04 | S23 UI oficial Horus | Home, Settings, selector de proyectos; Bare terminal existente | horus/Alpine; remoto Off; proyecto conservado; sesión normal sin instalador |
| H0-E05 | S23 Bare `/home/horus` | `pwd`, `id`, HOME/CODEX_HOME selectivos, `uname -m`, release, loader musl | Alpine/arquitectura/libc y perfil efectivos de B |
| H0-E06 | Mismo perfil | `command -v` acotado; versiones Git/gh/Python/Node/npm; launcher Codex leído; `codex --version`, `codex login status` por ruta verificada | Herramientas y autenticación CLI, sin inferencia |
| H0-E07 | Mismo perfil | `python3 -B` para imports, `stat`/existencia de rutas y ancestros PRoot proyectados | Binds, metadatos de persistencia y herramientas Python; ningún contenido de secretos |
| H0-E08 | Mismo perfil | `gh api user --jq '"H0_GH_LOGIN_OK"'`; API repo con `{private,default_branch,permissions}` | API autenticada y permisos del repo privado |
| H0-E09 | Mismo perfil | `GIT_TERMINAL_PROMPT=0 git ls-remote --heads https://github.com/<cuenta>/app_gastos.git refs/heads/main` | Retorno 0 y SHA; URL real construida con el login de `gh`, sin imprimirlo |
| H0-E10 | Mismo perfil | Consulta de helpers filtrada por presencia de `gh auth git-credential`; `git config --get user.name/email` con stdout a `/dev/null` | Helper gh sí; autor Git sin configurar. No volcado global de config |
| H0-E11 | S23 perfil nativo, metadatos accesibles desde guest | Existencia/permisos de rutas, package version, verificación no modificadora del readiness stamp; apertura normal de ficha | Perfil distinto y terminal sin contenido; no API ni inferencia atribuida a ese perfil |
| H0-E12 | S23 UI FolderSync | General, Programación, Opciones, Filtros, Conexión, Historial, Más información; intento de Automatización | Tabla D, fallo 403 y limitación premium. Ningún sync/análisis/cancelación disparado |
| H0-E13 | WSL | Versiones, metadatos de perfiles/symlinks, cwd y solo `CODEX_HOME` del proceso propio; launcher `codex2` leído | Perfiles/auth/sesiones distintos, configuración enlazada; un cwd activo observado |
| H0-E14 | WSL | API user/repo proyectadas, comparación booleana, `git ls-remote` y presencia de helpers | Autenticación independiente WSL; lectura de repo privado; configuración gh sin cambio de bytes |
| H0-E15 | WSL / Windows | Lectura script/filtros rclone; SQLite Desktop de solo lectura con tablas/columnas no secretas | Raíces y políticas de E.2; sin sync, checkpoint o exportación |
| H0-E16 | S23 compartido y WSL | Metadatos `.git` y SHA-256 de ADR autorizado; existencia de paths propuestos | Copia compartida distinta, un archivo igual; laboratorio aún no creado |
| H0-E17 | Usuario | Elección explícita de `/home/horus` para H1 | Resuelve qué perfil debe satisfacer autenticación/herramientas, sin reparar el otro |
| H0-E18 | S23 Bare, comprobación final | `python3 -B`: HOME/cwd, existencia de nueve rutas del fixture; subprocess de `gh api user` para booleano y `gh api --include user --jq empty` para seleccionar solo `X-OAuth-Scopes` | Terminal reanudable; metadatos de dependencias; cuenta coincide, scopes declarados. Cuerpo y stderr no publicados |

La consulta del repositorio se construyó dentro del guest con el login autorizado, proyectando solo los campos necesarios. Forma equivalente saneada:

```bash
gh api user --jq '"H0_GH_LOGIN_OK"'
gh api repos/<cuenta-autorizada>/app_gastos \
  --jq '{private,default_branch,permissions}'
GIT_TERMINAL_PROMPT=0 git ls-remote --heads \
  https://github.com/<cuenta-autorizada>/app_gastos.git refs/heads/main
```

Los marcadores `<cuenta-autorizada>` son saneamiento del registro, no argumentos literales que se hayan enviado a GitHub. No se imprimieron archivos `hosts.yml`, auth Codex, claves SSH, entorno completo ni URL con token. Inspeccionar metadatos de un auth no equivale a leer su contenido.

### I.2. Efectos permitidos, incidencias y límites

Se navegaron aplicaciones ya instaladas y se abrió/reanudó una terminal existente; eso puede actualizar estado interno de interfaz, sesiones y shell. No se afirma una captura forense sin cambios de atime/estado de app. No hubo instalaciones, gestores de paquetes, modificación de configuraciones, permisos ni datos de proyectos.

Un primer envío largo de comando de inventario a la terminal quedó incompleto por el transporte de entrada de texto. Se canceló esa entrada en la terminal de auditoría y se repitió con bloques cortos; solo la ejecución completada sustenta resultados. No se atribuye el truncamiento a Codex o a corrupción del entorno. No se ejecutaron comandos arbitrarios sobre sesiones ajenas.

Se usaron lecturas de accesibilidad y capturas temporales mínimas para controles que no exponen bien su estado. No se incorporan capturas de cuenta/pantalla terminal al árbol documental. Ante una transición inicial que mostró controles de login, la automatización no introdujo contraseñas ni capturó una imagen; la siguiente lectura estable volvió al home `horus, Alpine` y Bare terminal se pudo reanudar. No se interpreta esa transición como pérdida de autenticación.

No se accedió a documentos personales no autorizados ni se repitió la auditoría completa de Drive/RAG. Se leyó el ADR seleccionado, documentación técnica del proyecto y metadatos de las configuraciones requeridas. Los resultados históricos de Codex/celular/Drive no se presentan como ensayos actuales.

**No ejecutado en H0:** creación de repositorios/directorios laboratorio, clone/fetch/pull/checkout/commit/push, instalaciones, migración de distro, OAuth/login nuevo, `gh auth setup-git`, transferencias rclone, sincronización FolderSync manual, cambios de filtros, arranque/parada/reinicio de servicios o dispositivos, cambio de VPN, credenciales o emparejamientos. La sincronización horaria preexistente de FolderSync se observó, no se provocó ni se intervino.

### I.3. Archivos modificados y control documental

**Único archivo nuevo del workspace:** `docs/investigaciones/2026-10-26_codex_24x7/DRIVE_ID_01_EXAMPLE.md`.

Línea base de H0, antes de este informe: **1.816 archivos regulares, 66.430.452 bytes**, SHA-256 agregado **`2296462f68e92cf7906cb478dff9b611abc1befe939a24f52dbffcc779b3ae26`**. Incluye el informe 09 ya existente. Algoritmo: archivos regulares excluyendo symlinks, ordenar con **`sorted(root.rglob('*'))` (orden de componentes de `pathlib.Path`)**, siendo `root=Path('/home/developer/proyectos/mestry')`; concatenar para cada uno `ruta relativa + NUL + SHA256(bytes).hexdigest() + LF` en UTF-8 y calcular SHA-256 del conjunto. El cierre coteja todo el árbol excluyendo únicamente este nuevo informe. Un primer cotejo ordenó cadenas completas y dio otra huella con igual conteo/tamaño; al usar el orden Path de la línea base coincidió exactamente, sin cambios de contenido.

También se conservan las huellas de los tres archivos externos leídos:

| Archivo | SHA-256 inicial y cotejado en esta ejecución |
|---|---|
| `/home/developer/sincronizar-mestry.sh` | `bbe21150f567fa901b9199a938afc4634fe0eb477c6f547fecd3fa3213ccffe9` |
| `/home/developer/.config/rclone/mestry-bisync.filters` | `13cf61725e39a04bc718db077bdc6c059f2d195ee94e6e16ff6cbdc81d373d2d` |
| `/home/developer/.local/bin/codex2` | `c42c805cece2ac700cbff66e8b39bf0412027c606490d9e5b228140ad4aaf8f7` |

**Control de cierre ejecutado a las 23:49:59 del 26/10/2026 −03:00:** los **1.816 archivos anteriores** conservan conteo, bytes y huella agregada; los tres archivos externos cotejados también conservan sus hashes. Esto incluye los informes históricos, 09 y el ADR congelado. Los **15 enlaces locales** resuelven; están A–I y H0-01 a H0-12, con **11 criterios verificados y uno parcialmente verificado**; cuatro fences equilibrados. Cero coincidencias en los patrones aplicados de claves privadas, tokens GitHub/OpenAI, valores de autenticación y correos. Es un control acotado del entregable, no una certificación de todo archivo o servicio del sistema. Tras añadir este registro se repite solo la validación documental local.
