# MESTRY — H3: clon operativo S23 y entrada desde S25

Fecha inicial: **02/11/2026**, America/Santiago. Seguimiento al **04/11/2026**.
**H3 aceptada para el recorrido definido el 04/11:** revisión nueva aplicada
por bridge, validación ARM64, tarea real S25 sobre ese SHA, BUSY/preview,
terminación y reapertura fresca, con estado final limpio/libre/idle.
[Recibo vigente](../../validation/H3_BRIDGE_ACCEPTANCE_20261104.md).
Las secciones anteriores a este cierre conservan sus resultados, incluidos
intentos incompletos. **H4/H5 pendientes**, sin implementación aquí.
[Evaluación y siguientes pasos](../../PROJECT_REVIEW.md).

**Estado al inicio del informe, 02/11:** nodo S23 verificado y cliente S25
pendiente. Las secciones siguientes conservan la secuencia de pruebas; las
continuaciones del 03/11 actualizan ese estado. Continúa H2, sin repetir H0 ni
modificar el ADR congelado.

## Incremento preparado

- Contrato `alpine-aarch64` y ocho suites de aceptación del repositorio.
- `work_session.py lease`: lock local compartido durante operaciones/turnos del
  bridge; release explícito y recuperación pendiente ante EOF ambiguo.
- `project-gate.mjs`: admisión con recepción validada si limpio/libre, preservación
  del trabajo dirty y bloqueo hasta la terminación del turno identificado.
- `horus_keepalive.py`: tarea opcional fetch-only cada 120 segundos dentro del
  supervisor existente, sin otro servicio o puerto.
- `s23_project.py`: validación ARM64, overlay de la release privada ya instalada
  y recibo documental saneado. No copia configuraciones públicas de ejemplo
  sobre el teléfono ni importa credenciales, historiales o dependencias WSL.

Las nuevas pruebas WSL cubren lease/busy/EOF, cambios dirty, candidato válido,
el lock real Python desde Node, notificaciones terminales anticipadas/ajenas,
timeout ambiguo y conservación de la release anterior. La aceptación real del
S23 y el cliente se añadirá después de ejecutar el incremento.

## Preflight y límites iniciales

Ambos teléfonos se identificaron mediante el servidor ADB existente. Termux
aceptó SSH autorizado y Horus respondió en su puerto SSH; el bridge 8787 no
respondía inicialmente. Se abrió Horus normalmente, con las credenciales de
desarrollo ya autorizadas usadas solo en las interfaces normales. El perfil
Bare terminal confirmó `/home/horus`, UID 1000 y `aarch64`.

**Incidencia del operador:** al probar el ejecutable ADB local, su versión 41
reinició el servidor versión 40 del PC. Ambos dispositivos se revalidaron
autorizados después; se volvió al transporte de protocolo sin más arranques.
No se reiniciaron los teléfonos ni se cambiaron claves, VPN o emparejamientos.

La entrada de teclas wake/control en una terminal ya visible produjo caracteres
extra. Los primeros intentos no ejecutaron el preflight esperado. Se corrigió
la detección de pantalla y se comprobó el SHA-256 del payload antes de ejecutarlo.
Un envío largo agotó su timeout en una asignación parcial; se inspeccionó y
completó explícitamente antes de ejecutar, sin repetir escrituras del proyecto.

El repositorio operativo se ubicará fuera de FolderSync y conservará
dependencias propias de ARM64. La recepción automática solo podrá aplicar
cambios desde entradas gestionadas; un escritor que ignore el lock o deje jobs
separados sigue fuera de la garantía cooperativa. H5 validará reposo, reinicio
y PC realmente apagado. Drive y las autorizaciones documentales siguen en H4.

## Entorno y primer clon verificados

Horus **1.1.0 / 6**, Alpine **3.24.0**, Python **3.14.8**, Node **24.18.1**,
npm **11.12.1**, Git **2.54.0**, GitHub CLI **2.97.0**. Codex nativo **0.163.0**
con `login status=0`. Se confirmó la cuenta GitHub esperada; la API del
repositorio público declaró lectura/escritura/admin y rama `main`. Esos permisos
declarados no sustituyen una prueba de push desde el nuevo clon.

La ruta `/workspace/projects/mestry` no existía. Se clonó directamente desde
GitHub y se comprobó el SHA **`15fa53df2e49b87e83cb1d5481c540038afdef44`**.
El laboratorio H1 permanece presente. El bridge propio no estaba en ejecución,
su emparejamiento sí existía y el supervisor conservaba su flag habilitado.
La identidad Git se configura solo en este clon, con el correo público noreply.

El primer incremento de código pasó **133 tests WSL** y un clon público anónimo
cotejó **179 archivos**, incluidos sus objetos normalizados, con árbol limpio.
La siguiente corrección añade cierre desde el propio escritor protegido:
`--within-turn finish` exige ascendencia y PID/inicio del escritor registrado,
mantiene la fase exterior running y conserva la nueva evidencia de validación.
Otro terminal no puede usar esa opción para saltarse el lock. También funciona
desde el escritor de `start`, sin anidar otro supervisor. La suite vigente
consta de **136 tests** (54/4/12/13/3/37/9/4); la aceptación ARM64 sigue separada.

La primera validación real ARM64 rechazó `helpers`: dos tests negativos usaban
el home/arquitectura del host como supuesto de perfil incorrecto. En Horus ese
supuesto deja de cumplirse. Se cambió la prueba para simular explícitamente un
home externo con `unittest.mock`, antes de llamar a los guards de instalación y
upgrade. Los fixtures no deben inspeccionar la instalación real para probar un
rechazo. No se desactivó ni saltó ninguna prueba; se conservan cuatro helpers y
las ocho suites. El rechazo ocurrió antes de activar el nuevo bridge.

Una comprobación repetida del cierre desde el propio escritor detectó un falso
"sin cambios" al copiar el índice a un archivo con mtime nuevo. Se reprodujo
determinísticamente con un cambio del mismo tamaño y timestamps iguales. Git
usa el mtime del índice para decidir cuándo debe releer contenido potencialmente
ambiguo ([documentación oficial sobre racy Git](https://git-scm.com/docs/racy-git)).
Se conserva ahora el timestamp del índice copiado y se verifica, por contenido
normalizado con Git, cada ruta seleccionada antes de aceptar el candidato.
Los cambios del ensayo anterior quedaron locales; no se descartaron ni se
reescribieron commits remotos. La suite incorpora ese caso sin relajar los
guards: **137 tests** (54/4/12/13/3/38/9/4).

El siguiente ensayo ARM64 pasó los guards corregidos y encontró otro supuesto
del harness: esperaba la salida del stager en 5 s, mientras ese helper permite
5 s de terminación más 2 s de cierre forzado del hijo y limpieza HTTP. En
PRoot se observó ese recorrido. El test espera ahora hasta 15 s y mantiene las
comprobaciones de salida 0, túnel hijo cerrado, una descarga y puerto cerrado.
No se cambió el comportamiento ni el límite productivo del helper.

La suite Git real en Alpine pasó sus **38 pruebas en 305,861 s**. El límite
general de 120 s rechazaba un candidato correcto. El contrato revisado asigna
600 s a esa suite; las otras conservan 120 s. La preparación del bridge admite
hasta 900 s para la validación completa, antes de iniciar el escritor. Se
mantienen todos los tests, el bloqueo y el rechazo de candidatos fallidos; no
se omiten pruebas ni se aplica una actualización antes de validarla.

La validación completa de `5d377574f8b09915b64f52d76fe530fd0c450436` pasó
**137 tests en Alpine**. La primera activación se detuvo antes de reemplazar
el bridge: el helper suponía un wrapper `mestry-keepalive` que no existe en
esta instalación. El supervisor histórico se invoca mediante Python y su
archivo ya instalado, como registra el informe 11. Se corrigió esa invocación;
no se crea otro supervisor ni se cambia su identidad. El bridge anterior y su
emparejamiento seguían presentes, sin proceso activo tras el rechazo.

## Aceptación real del nodo y de Git

- `4c0ff9fb3070af8460c771211c93b13e54c5a8c7` pasó las ocho suites en
  Alpine: **137 tests**, con herramientas locales y sin instalar paquetes.
- `activate --head <ese SHA> --review` devolvió `H3_ADMITTED` y
  `MESTRY_BRIDGE_UPGRADED/PASS`. Conservó emparejamiento, estado de sesiones,
  release anterior y puertos; no cambió credenciales ni añadió servicios.
- La release seleccionada es `22f817f13591e1d6dbd9`. La recuperación conserva
  el puntero, wrapper y código anterior del supervisor en backups privados.
- El supervisor existente observó `healthy`, cero fallos consecutivos y
  `project_poll.state=checked`, proyecto `mestry`, estado `fetched`, SHA local
  y remoto `4c0ff9f…`, `update_pending=false`, el **02/11 a las 15:12:34 UTC**.
  Es evidencia del polling real, no una garantía de disponibilidad continua.
- Un escritor `start` generó únicamente el [recibo saneado del S23](../../validation/H3_S23_RECEIPT.md).
  El preview seleccionó solo ese documento y conservó el índice. `finish
  --publish` validó el candidato y publicó **`f0df88defede9c43ea09e788a45065e0c7448320`**.
- WSL recibió ese commit mediante `receive`, volvió a pasar **137 tests** y
  quedó limpio, con `validation_matches_head=true` y sin candidato fallido.
  La autenticación Git efectiva del nuevo clon S23 queda probada por ese push.

La edición pública anónima en `5d37757…` cotejó **179 archivos**, bytes y
objetos Git normalizados, con árbol limpio. El recibo posterior añade un
documento técnico; no contiene identidades de hardware, tokens ni historial.

## Prueba del cliente y condiciones de operación

El S25 conserva **0.2.0-mestry-pilot8**. La app estaba desconectada: el texto de
"Nueva conversación" estaba habilitado en accesibilidad, pero su botón padre
estaba deshabilitado. Se corrigió la lectura de ese estado antes de crear un
hilo. Un intento de conexión conservó los campos guardados. El puerto loopback
18787 devolvió `Connection refused`; esto no contradice el health correcto de
8787 en el S23 y sitúa la comprobación siguiente en el transporte del cliente.
ConnectBot está instalado/habilitado y conserva los perfiles MESTRY; no se han
modificado sus reenvíos, claves, VPN ni emparejamientos.

Durante la reanudación, el servidor ADB del PC cambió repetidamente de PID y
cortó consultas; también mostró autorización intermitente. Había otro hilo de
Codex activo, pero no se inspeccionaron sus comandos ni se atribuye causalidad
sin prueba. Se reutiliza el protocolo del servidor existente. Solo se reintentan
lecturas; una entrada potencialmente ejecutada se concilia mirando su resultado
antes de volver a escribir. Ambos agentes pueden trabajar en paralelo con
servidor compatible; la interfaz de un mismo teléfono requiere turnos.

La pantalla del S23 se mantuvo temporalmente encendida por USB para evitar
interrumpir la validación con bloqueos. Se restauró y releyó su valor original
`stay_on_while_plugged_in=0`. No se llegó a modificar ese ajuste en el S25.
Este ensayo no prueba reposo ni funcionamiento con el PC apagado: corresponden a H5.

## Alcance pendiente para cerrar H3

**H3 no se declara cerrada.** El nodo y Git están validados, pero todavía no
se ejecutó una tarea de Codex desde un hilo nuevo del S25 en este clon.
La aplicación automática mediante `start` del CLI sí está acreditada por la
continuación S23 de abajo. La entrada del bridge sigue pendiente de prueba
física; el bootstrap inicial y las suites no se presentan como esa aceptación.

| Comprobación | Estado / evidencia |
|---|---|
| Clon real ARM64 y entorno compatible | Verificado: contrato y 137 tests en el S23 |
| Despliegue sobre release privada anterior | Verificado: `H3_ADMITTED`, pairing y estado conservados |
| Fetch desde supervisor existente | Verificado: estado real del polling, sin aplicación de archivos |
| Push S23 y recepción WSL | Verificado: `f0df88d…`, documento recibido y 137 tests WSL |
| Aplicación automática desde entrada gestionada | Verificada en CLI `start` hasta `bdf3e4c…`; bridge pendiente |
| Hilo nuevo Codex CLI en S23 | Verificado: lectura de estado, entorno, HEAD y guardas reales |
| Hilo nuevo S25 que lea estado y continúe | Pendiente de transporte disponible y operación de interfaz coordinada |
| Lock durante una sesión Codex CLI real | Verificado: `receive` rechazado y preview autorizado desde el escritor |
| Lock durante un turno del bridge/cliente S25 | Cubierto en fixtures; pendiente de la prueba física S25 |
| PC apagado, reposo y reinicio | H5; no probado aquí |

Como alternativa no destructiva al ADB intermitente se intentó SSH al guest
mediante el salto Termux existente. La identidad WSL actual fue rechazada por
SSH; no se obtuvo sesión ni se registraron claves, habilitaron métodos o
modificaron permisos. No afecta al acceso legítimo Bare terminal ya utilizado.
El pin temporal del host se mantuvo separado del `known_hosts` normal. No se
copiaron contraseñas, tokens ni hogares Codex.

Las publicaciones documentales `c4b3cb2…` y `67b16fd…` llegaron al S23 como
antecesores de `bdf3e4c…` mediante el fast-forward validado de `start`.
El commit originado allí y recibido en WSL es `f0df88d…`; su recibo documenta
la admisión inicial, mientras STATUS y esta sección contienen la aceptación posterior.

Para reanudar sin repetir H0/H1/H2:

1. Coordinar una ventana sin reinicios de ADB ni manejo concurrente de las
   pantallas S23/S25. El otro hilo puede continuar con código u otro dispositivo.
   Reutilizar servidor/versión compatibles; el lock Git no controla el daemon ADB.
2. En MESTRY del S25, usar la conexión SSH guardada y comprobar `/healthz` por
   su loopback 18787. Mantener la app en primer plano durante el ensayo: la
   política del cliente permite cerrar su VPN al salir sin tarea activa. No
   cambiar claves, scopes ni reenvíos como respuesta automática a un rechazo.
3. Abrir una conversación nueva sobre `/workspace/projects/mestry`. Comprobar
   la recepción validada del HEAD publicado, leer AGENTS/STATUS/recibo y ejecutar
   una tarea acotada. Probar `--within-turn finish` primero como preview y
   verificar que otro escritor obtiene `BUSY` durante ese turno. Registrar
   después el resultado, el HEAD y la liberación del lock.

El siguiente incremento sigue siendo esta aceptación S25. No avanzar H4 como
si H3 estuviera cerrada, ni reinstalar Horus/Codex para resolver esta coordinación.

## Continuación exclusiva en S23 — cancelación del helper

Esta continuación utiliza exclusivamente la interfaz del S23; la aceptación
del S25 permanece separada. Se conservan bridge, SSH, VPN y emparejamientos existentes.
El supervisor observó `healthy`, cero fallos y `update_pending=true`: HEAD local
`f0df88d…`, remoto `67b16fd…`, el **02/11 a las 21:35:55 UTC**. El fetch real
detectó correctamente la actualización sin aplicarla en segundo plano.

El primer `start` gestionado rechazó el candidato por `VALIDATION_FAILED_HELPERS`,
antes de iniciar Codex. Una ejecución offline protegida reprodujo el fallo:
el stager sintético no terminó en los **15 s** posteriores a SIGTERM; cuatro
tests, un error, 17,778 s. Se conservó el checkout anterior.

Se reforzó el mismo test con una espera cuyo despertar se difiere y una señal
enviada después de entrar en ella. Es una reproducción controlada del problema
de cierre, no una prueba de su mecanismo interno exacto en PRoot. En WSL falló
con el código previo (cuatro tests, un error, 16,176 s). El helper vuelve ahora
a Python al menos cada 250 ms, manteniendo su deadline monotónico original;
con la corrección pasaron los cuatro tests en **1,675 s**. Se conservan las
comprobaciones de artefacto único, HTTP 404, descarga única, hijo cerrado y
puerto cerrado. No se amplió el timeout de 15 s ni se omitió ningún caso.

La corrección quedó publicada en **`bdf3e4c12ef7a97da79ca93416150b9c67aa704d`**.
Un clon público anónimo cotejó sus **180 archivos**, bytes y objetos Git
normalizados, sin diferencias y con árbol limpio. El fixture SSH es sintético
y no modifica túneles ni servicios reales.

## Aceptación real posterior — sesión nativa S23

Un intento obtuvo `BUSY`; el chequeo posterior mostró `busy=false`, `phase=idle`,
`dirty=false` y ninguna recuperación pendiente. Se reintentó por el flujo normal,
sin quitar locks, reaprobar políticas ni forzar Git. `start` recibió y validó
`bdf3e4c…` antes de lanzar el escritor; no se ejecutó un merge manual para este
incremento. Las ocho suites pasaron en Alpine: **54/4/12/13/3/38/9/4 = 137 tests**.

Se inició una tarea **nueva** con el Codex nativo mediante `codex exec`. Leyó
AGENTS, STATUS y el recibo, ejecutó `check-env.sh` y `git rev-parse HEAD`, y
terminó con `H3_S23_READY`. No requirió conversaciones anteriores, no editó
archivos y no instaló dependencias. Se usaron por invocación `approval_policy=never`
y `sandbox_mode=danger-full-access`, iguales a la excepción ya aprobada para
Horus; no se escribió configuración. La restricción de lectura de esta tarea
procede de su instrucción y no demuestra un sandbox del SO.

La salida de ejecución observada confirma:

- `check-env.sh`: target `alpine-aarch64`, aprobación coincidente, sin errores
  ni instalaciones; Git 2.54.0, Node 24.18.1 y Python 3.14.8.
- `git rev-parse HEAD`: `bdf3e4c12ef7a97da79ca93416150b9c67aa704d`.
- `receive` dentro del escritor: salida **3**, `BLOCKED/BUSY`, trabajo preservado.
- `--within-turn finish README.md`: salida **0**, `OK`, `index_unchanged=true`,
  `changed=[]`, cero commits salientes y publicación no solicitada. Esto prueba
  la autorización real por ascendencia del escritor en el guest.
- Al finalizar: `start` devolvió `OK`, `phase=idle`, `dirty=false`. Una consulta
  posterior independiente confirmó `busy=false`, `failed_candidate=null`,
  `validation_matches_head=true` y los **137 tests** persistidos.
- La consulta seleccionada de entorno confirmó `HOME=/home/horus` y
  `CODEX_HOME` no definido. No se imprimieron el entorno completo ni archivos de auth.
- El supervisor existente confirmó `worker_running=true`, `enabled=true` y
  health coincidente. Su actualización natural de **22:09:51 UTC** mostró
  `healthy`, cero fallos consecutivos, proyecto `fetched`, HEAD y remoto
  `bdf3e4c…`, `update_pending=false`. No se reinició para obtener ese resultado;
  la recuperación tras reinicio continúa sin acreditar y pertenece a H5.

El último mensaje de esta prueba permanece en el estado privado del S23; no
se publica una transcripción. La aceptación de código corresponde a `bdf3e4c…`;
las actualizaciones documentales siguientes usan el mismo flujo de recepción.
Permanece pendiente la prueba del cliente S25/bridge, que no se operó durante
esta continuación. Tampoco se probaron PC apagado, reposo o reinicio de H5.


## Revisión del 03/11/2026 — estado actual y trabajo posible con solo S23

Revisión de código, historial y evidencia, con consultas de lectura al S23.
La documentación se actualiza localmente bajo el wrapper; no se publica como
parte de esta revisión. Solo estaba conectado el S23 esperado.

### Estado observado

- WSL y `refs/heads/main` de GitHub coinciden en **`4865d2c235e3b622cfa5df49b3f41ce1784a287b`**.
  El checkout estaba limpio, libre, `idle`, sin recuperación pendiente ni
  candidato fallido. El contrato de entorno WSL no mostró errores.
- Se ejecutaron de nuevo las ocho suites offline bajo `start --resume --offline`:
  **54/4/12/13/3/38/9/4 = 137 tests**, todos correctos. No hubo inferencia,
  dependencias nuevas ni ejecución de estas suites en el teléfono hoy.
- Una sesión SSH nueva autenticó en Termux. Horus declaró **1.1.0**, configurado,
  habilitado y `running`. El bridge respondió HTTP **200** en `/healthz` con
  nombre/versión esperados; la ruta consultada sin autenticación devolvió **401**.
- Android llevaba unas **83,3 h** encendido; los procesos principales de Horus,
  unas **34,6 h**. Son edades de procesos observados, no registros continuos de
  disponibilidad del bridge ni prueba de recuperación tras reinicio.
- Android declaró `Dozing`, con wake locks de Termux/Horus y sus exenciones de
  batería presentes. `stay_on_while_plugged_in=0`. No se despertó la pantalla
  ni se forzó reposo. El estado térmico del sistema fue **0**.
- Tres muestras entre **10:28:28 y 10:29:32 UTC** mantuvieron health correcto,
  `Dozing`, batería **79 %**, temperatura de batería **21 °C** y memoria
  disponible alrededor de **3,67 GiB**. Alimentación **USB=true / AC=false**.
  La observación cubre aproximadamente un minuto con el PC conectado.

Al enumerar dispositivos, el cliente ADB local detectó servidor versión 40 y
lo reinició con versión 41. El S23 siguió autorizado y se revalidó su modelo;
no se reinició el teléfono. Se registra esta incidencia del host explícitamente.
No se cambiaron paquetes, ajustes Android, SSH, VPN, OAuth, emparejamientos,
sincronizadores ni servicios del teléfono.

### Qué queda acreditado y qué sigue pendiente

La base H1/H2 y la aceptación CLI de H3 mantienen su evidencia anterior. La
inspección actual acredita acceso Termux y salud del bridge en las muestras.
No se accedió desde WSL al perfil privado de Horus ni se usó la salud HTTP como
prueba de su checkout: **HEAD actual del S23, estado de polling/lock del guest,
lectura Drive vigente y recorrido autenticado del bridge no se revalidaron hoy**.
El último HEAD aceptado del S23 con tarea nativa sigue siendo `bdf3e4c`.

El repo integra cliente, bridge, publicación documental y continuidad Git.
El servicio documental completo, índice/RAG y disponibilidad 24/7 siguen sin
aceptación integral; los planes históricos no convierten esos componentes en
funcionalidad terminada. STATUS y el seguimiento vigente del roadmap prevalecen
sobre los siguientes pasos antiguos de los informes 09–14.

### Prioridades cuando solo está disponible el S23

| Trabajo | Alcance y aceptación propuesta | Dependencia que conserva |
|---|---|---|
| Bridge real desde el propio S23 | Usar Bare terminal del perfil existente; comprobar `check --remote`, polling y un cliente autenticado local. Para una tarea acotada posterior, comprobar HEAD recibido, lectura del estado, rechazo `BUSY` durante el turno y liberación final. Reutilizar credenciales en su UID; no repetir la aceptación CLI como sustituto del bridge | Complementa H3 del servidor; no acepta UI, VPN ni túnel de la app S25 |
| Observación prolongada de reposo | Preparar ventana de 20–30 min con muestras de salud, estado Android, memoria y térmico, sin forzar Doze ni cambiar ajustes | Evidencia preliminar; H5 sigue dependiendo de H3 y de ensayos físicos separados |
| Vigencia del acceso Drive | Preparar lectura de un fixture ya autorizado, con renovación ordinaria del runtime y verificación de bytes; han pasado más de siete días desde el piloto. No repetir consentimiento ni ampliar scopes/raíces por defecto | Diagnóstico del componente existente; no iniciar H4 ni crear publicaciones de prueba como parte de esta revisión |

La prioridad es comprobar el recorrido del bridge desde S23 y registrar por
separado su alcance. Para cerrar H3 sigue haciendo falta el cliente S25.
Cargador de pared, PC realmente apagado, 24 h observadas, recuperación de fallos
y reinicio siguen pendientes; USB conectado y procesos antiguos no los prueban.


## Implementación autorizada del 03/11 — comprobaciones con solo S23

Continúa la revisión anterior con autorización de implementación y restauración
limitada a la carpeta piloto y su última revisión sintética. Código y
documentación se mantienen en el clon de desarrollo; no se publica este
incremento ni se modifica la release del servidor como parte del ensayo.

### Herramientas y validación local

- `tools/s23-remote-access/observe_s23.py`: observación finita mediante protocolo
  del servidor ADB existente y SSH Termux. Verifica modelo y exporta únicamente
  batería, memoria, pantalla, térmico y health. Los errores permanecen separados;
  JSON privado/atómico con archivo nuevo y directorio del operador modo 700.
- `tools/s23-remote-access/accept_s23.mjs`: usa dentro de Horus la clave existente,
  crea un hilo/turno acotado, comprueba concurrencia y recibos reales de comandos,
  reconecta y solicita contenido/sync del mismo hilo. No exporta clave ni chat.
- `tools/horus_publish/read_existing_fixture.py`: reutiliza el runtime Termux,
  journal en lectura y mismos IDs ya verificados; comprueba privacidad, bytes y
  hash. La opción de ubicación restaurada es solo diagnóstica y no habilita al
  publicador a escribir en otro destino.
- **148 pruebas offline correctas en WSL**: 58 publicación/browser/OAuth/lectura,
  4 helpers, 16 recuperación/polling/observación, 13 pairing, 3 política,
  38 workflow, 9 guardas de turno, 4 overlay y 3 recibos de aceptación.
  Se verificó el nuevo caso de carpeta restaurada fuera de Review con rechazo
  predeterminado y lectura por ID solo mediante opción explícita.

[Procedimiento reproducible y prueba S25](../../S23_CHECKS.md).

### Bridge real en el S23 — PASS

El código se transfirió como datos públicos acotados a una ruta privada del
perfil, verificando SHA-256 antes de ejecutarlo. Hash del helper ensayado:
`4990ad94a8ac5fe0278307140ed7fbf8b59d29e0df40c138746993550646d8ed`. Una entrada de terminal larga quedó truncada;
se concilió su estado y se usaron órdenes cortas y fragmentos comprimidos.
La tecla normal de encendido permitió despertar la pantalla; no se reconfiguró
su timeout, servicios, permisos o acceso remoto para resolver la interfaz.

Un único turno nativo a través del WebSocket existente se ejecutó entre
**2026-11-03T11:17:31.830Z y 2026-11-03T11:19:04.653Z**:

| Comprobación | Resultado observado |
|---|---|
| Hello autenticado loopback | Correcto; clave conservada en el perfil Horus |
| HEAD antes/después y remoto | `4865d2c235e3b622cfa5df49b3f41ce1784a287b`; validación coincidente |
| Otro escritor durante el turno | `receive --fetch-only`: salida 3 / `BUSY` |
| Comando real de lectura de HEAD | Recibo de `commandExecution` verificado |
| Preview desde el turno | `--within-turn finish README.md`, OK e índice intacto |
| Terminación del turno | `completed` |
| Otra conexión, mismo hilo | `session.content` y `session.sync`, 10 entradas cada uno |
| Estado final | `busy=false`, `dirty=false`, `phase=idle`, sin candidato fallido ni recuperación pendiente |

La evidencia se leyó en la interfaz normal de Bare terminal y se registró como
metadatos seleccionados de capturas revisadas, sin hacer pasar una transcripción
por descarga automática del estado privado. El resultado completo permanece en
`~/.local/state/mestry-s23-checks/result.json`. En este perfil no se obtuvo una
exportación mediante `/system/bin/log` ni `/sdcard`; no se ampliaron permisos
para conseguirla. El supervisor previo mostró healthy, cero fallos y polling
fetched con ese mismo HEAD; no se confunde con un log continuo de disponibilidad.

**Alcance:** el clon ya tenía ese HEAD antes de entrar. Esta prueba acepta el
recorrido local del bridge y sus guardas; no prueba un fast-forward nuevo desde
esa entrada, la app S25 ni su transporte VPN/SSH.

### Ventana medida de pantalla apagada — PASS

Se separó la preparación interactiva de una ventana nueva. Se volvió al inicio
y se apagó la pantalla con la tecla normal; no se usó `force-idle` ni se cambió
ningún ajuste. El observador corrió protegido por el wrapper WSL.

- Intervalo de muestras: **2026-11-03T11:29:34.884933+00:00 → 2026-11-03T11:49:34.901244+00:00**, 20 minutos,
  cada 30 segundos; **41/41** health correctos y **41/41**
  con pantalla en reposo. Consultas válidas: 41/41.
- Batería observada: **79–79 %**; temperatura:
  **23.2–23.7 °C**.
- Memoria disponible: **3.20–3.37 GiB**. Estado térmico:
  **[0]**, cobertura 41/41 muestras.
- Alimentación USB; el PC permaneció conectado. Las consultas pueden despertar
  CPU. `Dozing` aquí es estado de pantalla, no prueba de Doze profundo.

La observación inicial de preparación también guardó 61/61 health correctos
durante 30 min, con pantalla interactiva parte del tiempo. No se usa para
reemplazar esta ventana ni se declara 24/7, recuperación tras reinicio o PC apagado.

### Drive: restauración acotada y lectura verificada

La cuenta esperada funcionó; carpeta y fixture inicialmente tenían `trashed=true`
y `explicitlyTrashed=false`. El padre conocido devolvió 404 al cliente actual:
no se afirma por ello que esté borrado permanentemente. Según la
[referencia de Drive](https://developers.google.com/workspace/drive/api/reference/rest/v3/files),
el estado de papelera puede heredarse de un ancestro.

Tras autorización expresa se enviaron solo dos peticiones de restauración,
por los IDs del journal. Google devolvió ambos elementos fuera de la papelera
y cambió el padre de la carpeta, sin una petición nuestra de cambiar padres.
Se confirma que quedó fuera de Review; la ubicación exacta no pudo resolverse
con el cliente `drive.file`. Otra revisión antigua heredó el estado activo;
para respetar el alcance de solo dos elementos se devolvió esa revisión
identificada al estado previo de papelera, con snapshot privado y una operación
compensatoria. No se tocó contenido ni se restauraron otros ancestros.

La lectura final del mismo fixture devolvió **79 bytes**, metadatos estables y
SHA-256 **`ada9d1e265088e8fae3dfe57e9a229e8e31ebd75ff480a321e70eaa82d8f20a7`**, coincidente con el registro de la publicación
original. Autenticación y privacidad verificadas; contenido y OAuth permanecen
en el runtime nativo. El publicador conserva **`publication_destination_ready=false`**
por el padre distinto de Review; este resultado no acepta el circuito H4 completo.

### Siguiente aceptación: S25 desde fuera de casa

El S23 queda con el bridge existente operativo y sin escritor del ensayo.
Usar la conexión privada guardada, mantener MESTRY en primer plano y abrir un
hilo nuevo del proyecto real. La guía contiene una tarea de lectura con rechazo
BUSY esperado y preview del cierre. Solo esa prueba puede aceptar el cliente;
el nuevo candidato por bridge y H4/H5 completos siguen separados.


El preflight posterior observó un agente de red activo `WIFI|VPN`, conectado y
validado, filtrando exclusivamente `NetworkAgentInfo` y los tokens de transporte
exactos. No se confundieron capacidades `NOT_VPN` o solicitudes de red con una
VPN activa. Esto prepara la prueba externa; no sustituye el acceso real del S25.


## Continuación física del 03/11 — S25 conectado

Se reutilizaron el APK piloto 8, los perfiles y el emparejamiento existentes.
Se revalidaron los modelos exactos antes de las operaciones ADB. La observación
utilizó el daemon existente, sin reiniciarlo; hubo fallos intermitentes de su
transporte, conservados como errores y conciliados antes de nuevas acciones.
Las evidencias completas permanecen privadas fuera de Git.

### Transporte y recuperación del acceso

El S23 respondió al health del bridge mediante el acceso LAN existente. En el
S25 se distinguieron VPN local, SSH, túnel y hello. Al inicio hubo timeouts SSH
y ausencia del puerto local; una terminal conservaba avisos de una conexión
anterior. También se observaron cierres por la política automática sin tareas.
La preparación con la VPN local activa y la reapertura del cliente SSH permitió
recuperar el reenvío. No se cambiaron los plazos, perfiles, claves ni puertos.

| Capa comprobada | Resultado actual |
|---|---|
| Red privada desde el UID del cliente | PASS; banner OpenSSH en 8023 y rechazo de 22, 8022, 8787 y 18787 del peer |
| SSH del perfil guardado | Autenticación y activación del reenvío observadas en una terminal nueva |
| Loopback S25, puerto 18787 | PASS; salud e identidad correctas, IPv4 loopback ocupado y direcciones no loopback libres en la prueba bind-only |
| Autorización del bridge | Sesiones sin token y WebSocket con token inválido rechazados con 401 |
| Cliente Android | Hello autenticado y respuestas frescas del historial observados |

La red subyacente de este ensayo fue Wi-Fi. Esta evidencia no renueva la
aceptación celular histórica ni acredita acceso desde otra red actual.

### Turno enviado desde S25 — PASS en el hilo piloto existente

Después de un diagnóstico corto sin herramientas, se envió una tarea nueva desde
la app entre **2026-11-03T15:19:47.507Z y 2026-11-03T15:20:33.219Z**. Se usó el
hilo sintético existente; los turnos anteriores quedaron excluidos al extraer
los recibos. Se verificaron cuatro elementos `commandExecution`, incluidos:

| Recibo del turno nuevo | Resultado |
|---|---|
| `git rev-parse HEAD` | Salida 0; `4865d2c235e3b622cfa5df49b3f41ce1784a287b` |
| `receive --fetch-only` | Salida 3, razón `BUSY`, durante el turno protegido |
| `--within-turn finish README.md` | Salida 0, `OK`, `index_unchanged=true`, publicación no solicitada |
| Terminación | Evento `turn/completed` del mismo ID, estado `completed`; cero turnos activos |
| Recarga completa | Respuesta nueva `session.content` después de la acción normal Recargar historial |
| Reapertura del proceso Android | Mismo ID del hilo ensayado y callbacks nuevos `session.sync`; 18 elementos y 21 entradas combinadas |
| Estado nativo final S23 | HEAD conservado; `busy=false`, `dirty=false`, `phase=idle`, `recovery_required=false`, sin candidato fallido |

Los conteos combinados del historial no son un delta de mensajes nuevos. La
frescura se acredita por el callback del servidor posterior a cada acción;
la pantalla y el archivo de caché por sí solos no bastaron. La terminación se
comprobó también en los eventos del servidor: antes de recargar, el snapshot
incremental no contenía el último elemento `turn_status` aunque sí el evento
terminal y todos los recibos. La recarga completa devolvió las 21 entradas.
El check final se leyó mediante Bare terminal y se registró como transcripción
seleccionada de metadatos de una captura revisada, no como exportación JSON del
perfil privado de Horus.

### Caso pendiente: primer turno y selección de un hilo nuevo

Antes de ese recorrido se creó desde la app un hilo nuevo en la ruta real del
proyecto. Su ID y ruta se comprobaron en Información de la conversación. El
mensaje de prueba quedó almacenado y hubo respuestas frescas de contenido/sync,
pero no se observó inicio de turno ni recibos de comandos para ese hilo. Una
reapertura posterior seleccionó el hilo sintético anterior. El diagnóstico y
la tarea que sí completaron se atribuyen explícitamente a ese otro ID.

La causa precisa del primer envío sigue sin capturarse. No se acredita el caso
nuevo a partir del éxito del hilo existente ni se modifica la política para
resolverlo. El siguiente ensayo debe conservar el ID nuevo, capturar la
respuesta de `turn.send` y comprobar su selección después de reabrir.

### Cierre y límites

El cliente quedó conectado al hilo ensayado, sin tareas activas. Se restauró el
valor anterior del tag temporal de diagnóstico; Wi-Fi, APK, OAuth y políticas
conservaron su configuración. Los cierres de clientes se hicieron sin tareas
activas y no detuvieron el servicio del S23. No se publicó código ni se aplicó
un candidato Git nuevo en el teléfono durante esta continuación.

H3 conserva dos pendientes: aceptar el primer turno/selección del hilo nuevo y
observar la aplicación de una revisión nueva por la entrada del bridge. H4/H5,
celular actual, reinicio, PC apagado y duración 24/7 mantienen sus límites previos.
Las 148 pruebas offline del incremento anterior no se repitieron por estos
cambios documentales; esta sección registra comprobaciones físicas adicionales.


## Continuación del 03/11 por la noche — conversación nueva y piloto 9

Esta sección actualiza los pendientes del ensayo de las 15 h sin borrar su
resultado. Se reutilizaron el daemon ADB existente, perfiles, claves y servicios.
La evidencia bruta, IDs de hilos/turnos, capturas y respaldos quedan privados.

### Recuperación inicial y reproducción

En el preflight de esta continuación el SSH existente de Termux no aceptaba
conexiones en 8023. Desde la interfaz normal de Termux se ejecutó su helper ya
instalado `bin/mestry-ssh-start 8023`; terminó con salida 0 y recuperó SSH y health.
En el cierre volvió a observarse rechazo de conexión tanto por LAN como desde
el S25, y se repitió ese mismo arranque existente. No se modificó su configuración.
La terminal normal mostraba `Process completed (signal 9)`: se cerró esa sesión
y se abrió otra desde la interfaz normal antes del arranque. La señal no
identifica al emisor ni establece una causa. Los registros de salida de la app
Termux disponibles tenían fechas anteriores al ensayo y no explican la caída
actual. La causa de la ausencia del daemon no quedó establecida; no se atribuye a Android, memoria o batería sin evidencia.

Con piloto 8 se creó otro hilo del proyecto real. El primer turno corto pasó
sin error visible; después, un turno de lectura entre **22:09:06.410Z y
22:09:36.869Z** confirmó HEAD, BUSY y preview. Por tanto, el envío sin inicio
observado por la mañana no se reprodujo y su causa permanece desconocida.
Al cerrar y reabrir el proceso, ese hilo exitoso fue sustituido por el piloto
antiguo: la pérdida de selección sí quedó reproducida con recibos previos.

### Corrección acotada, compilación y actualización

`selectSession` guardaba `KEY_SESSION` pero no actualizaba el índice de lista;
la restauración daba prioridad al `selectedSessionId` antiguo de ese índice.
Se persiste la lista al seleccionar y se prefiere el ID activo reciente solo
si pertenece a los hilos de la conexión restaurada. El cambio entre conexiones
sigue reiniciando el ID activo. No se cambia el esquema de caché ni la política
del bridge. Solo difieren dos controladores Kotlin y la versión Android.

- Piloto **9**, versión **0.2.0-mestry-pilot9 / 10009**; actualización `-r`,
  mismo paquete, certificado, permisos y UID, sin borrar datos ni emparejar otra vez.
- SHA-256 del APK: `542abbdf0f4021fb9fc0d95d7926f8aae7bbd7675df79513d13b8b7ce91b09a8`.
- SHA-256 del parche: `5c62a6190092e48da4858d6923ca0f8d9d3b41e958f4ab0810d0c6b04290eb39`.
- Archivo upstream y versiones de dependencias conservados. Reaplicación desde
  el archivo fijado: **68/68 hashes** correctos. Árbol Android de compilación cotejado.
- `assembleDebug` offline correcto con el entorno Windows existente. Se recuperó
  el APK piloto 8 instalado para conservar rollback y se compararon firmas antes
  de instalar. Gradle había eliminado la salida anterior; el respaldo recuperado
  coincide con el hash instalado anterior y permanece privado.
- **148/148 pruebas offline actuales**: 58 publicación, 4 helpers, 16 acceso,
  13 emparejamiento, 3 política, 38 workflow, 9 guardas, 4 overlay y 3 recibos.

La huella de fuentes del wrapper WSL se actualizó tras revisar contrato,
controles, archivo upstream y los tres archivos cambiados. Se conservó respaldo
privado de su configuración. No se reaprobaron políticas en el S23: su backend
y checkout siguen en `4865d2c`. Antes de recibir esta revisión allí hace falta
un handoff revisado de esa huella; publicar los archivos no equivale a desplegarlos.

### Aceptación del primer turno y reaperturas — PASS

| Prueba física con piloto 9 | Evidencia |
|---|---|
| Reabrir el hilo que piloto 8 perdía | Mismo ID, contenido nuevo del servidor y los cuatro recibos originales recuperados |
| Crear otro hilo y enviar su primera tarea | **22:36:06.555Z → 22:37:11.306Z**, ocho elementos `commandExecution`, estado `completed` |
| HEAD de esa tarea nueva | Salida 0, `4865d2c235e3b622cfa5df49b3f41ce1784a287b` |
| Exclusión del segundo escritor | `receive --fetch-only`: salida 3 y `BUSY` |
| Preview dentro del turno | Salida 0, `OK`, `index_unchanged=true`, publicación no solicitada |
| Cierre y reapertura del hilo recién creado | Mismo ID; `session.content` fresco, 12 entradas/11 elementos y los ocho recibos recuperados |

Se excluyeron turnos anteriores al extraer recibos. Las dos pruebas de reinicio
compararon el ID en la interfaz normal; callbacks posteriores acreditaron
servidor fresco. Un toast, texto del asistente o caché por sí solos no aceptan
las guardas ni la recuperación. Esta evidencia acepta el recorrido nuevo y la
selección corregida; no explica retroactivamente el envío fallido de la mañana.

### Datos móviles, cambio de red y retorno

El primer ensayo de cambio directo Wi-Fi → datos no recibió `session.content`
fresco. Había `CELLULAR` validada como predeterminada y ningún agente Wi-Fi;
la prueba quedó **no aceptada**, con cero tareas nuevas. Su causa precisa no se
capturó. Se restauró Wi-Fi sin cambiar políticas y se conservó esa evidencia.

Una segunda entrada, con MESTRY cerrado y conexión SSH nueva mediante el perfil
guardado, sí pasó por datos móviles. Antes y después del historial se verificó
`CELLULAR` predeterminada/validada, Wi-Fi desactivado y ausencia de agente Wi-Fi.
Desde el UID del cliente se comprobó banner SSH 8023 y rechazo de los demás
puertos ensayados; el túnel devolvió health correcto, 401 sin autorización y
escucha restringida a loopback. La app recuperó `session.content` fresco del
mismo hilo, con 12 entradas/11 elementos, sin otro turno de modelo por esta lectura.

La preparación de cancelación en esa ventana se abortó antes del envío por una
precondición del helper temporal de entrada; no se acredita cancelación celular.
El ensayo de interrupción posterior se hizo en Wi-Fi. Wi-Fi quedó restaurado
con red predeterminada validada; la recarga posterior del mismo hilo
volvió a recibir contenido fresco. No se tocaron datos móviles, roaming, VPN,
plazos, perfiles, reenvíos ni claves. Cambiar de red requiere por ahora renovar
la conexión SSH, con cero tareas activas y sin reenviar una tarea ambigua.

### Interrupción desde la app — no aceptada

El ensayo Wi-Fi conservó el ID del turno y su evidencia privada. La actividad
identificó el comando, pero el monitor no encontró un elemento normalizado
`commandExecution`. Al conciliar el mismo turno, el control Enviar no estaba
habilitado: no se realizó el gesto de interrupción. No se acredita cancelación.
La terminación y el estado final nativo se comprobaron por separado, sin reenviar
la tarea ni detener servicios. Este caso requiere diagnóstico adicional.

La recarga fresca final confirmó estado `completed` del mismo turno y cero
turnos activos.

### Estado final y pendiente H3

El check nativo posterior se leyó por Bare terminal del perfil existente y se
registró como transcripción seleccionada de una captura revisada: HEAD conservado,
`busy=false`, `dirty=false`, `phase=idle`, `recovery_required=false` y sin candidato
fallido. Se restauró el valor previo vacío del tag temporal de diagnóstico.
El cliente conserva el hilo ensayado, sin tareas activas, y su conexión volvió
a recibir contenido fresco después del retorno a Wi-Fi.

Los cambios de código/documentación quedan locales, con preview de cierre;
no se publicó ni se recibió un candidato Git nuevo en el S23. El primer turno
nuevo y la selección al reabrir quedan aceptados. H3 sigue pendiente de aplicar
una revisión nueva por el bridge con revisión de entorno previa; H4/H5, PC apagado,
reinicio y 24/7 conservan sus pruebas separadas.


## Continuación de cierre H3 — candidato nativo separado

Se revalidó `4865d2c235e3b622cfa5df49b3f41ce1784a287b` en WSL y remoto,
las 16 rutas pendientes sin staging y el transporte SSH/health existente. Se
conservó respaldo privado de las 16 rutas antes de editar. No se reinició ADB,
reinstaló APK/Alpine/Codex ni se modificó SSH, VPN, OAuth o sincronizadores.

Para evitar una transición de dependencias innecesaria en el teléfono se separa
el candidato nativo H3 del parche Android/pins piloto 9 y de los auxiliares Drive.
Se conserva la huella operativa ya revisada en S23 y su release instalada. WSL
revisa expresamente esa misma huella para publicar este conjunto; la política
y los bytes locales piloto 9 quedan respaldados para restaurarlos después.
No es una aprobación automática de una huella nueva para quitar un bloqueo.

El comprobador nativo registra SHA anterior/posterior a `session.start` y la
validación del target; rechaza recibos de comandos fallidos o no terminados.
La ejecución no se envuelve en `start`: debe adquirir el lock mediante el bridge.
Hasta registrar el resultado físico, esta preparación no acredita recepción.

El cierre obligatorio se limita a la aplicación nueva por bridge, tarea S25
sobre ese SHA, BUSY/preview, terminación, liberación del lock, limpieza y
reapertura fresca del mismo hilo. La interrupción se repite con descripción
accesible dinámica. El diagnóstico causal de señal 9, handover automático y
ventanas de disponibilidad prolongada no se convierten en ensayo de 24 h;
H4/H5 quedan expresamente pendientes.


## Continuación del 04/11 — recepción del candidato nativo

Se publicó `dc3a872a839295e6c4d65ef2b67eab3dcba90f30` mediante preview
con índice intacto y `finish --publish` con once rutas explícitas. El candidato
pasó las ocho suites WSL: **141 tests** (54/4/16/13/3/38/9/4), más
**4 tests** del comprobador de recibos. Mantiene el contrato, controles y
pins anteriores: **68/68 fuentes reproducidas**, huella
`ccd7a7f3068531fa87c2bad73c1416a9174d2d2dd3026c395c6edddbacfca080`.
Los cinco archivos Android/Drive no seleccionados siguen respaldados y locales.

### Primer intento conservado y conciliado

El check nativo anterior confirmó `4865d2c…`, limpio/libre/idle, validación
coincidente y sin recuperación. El fetch vio `dc3a872…` con `applied=false`.
Se extrajo únicamente el comprobador a estado privado, se verificó su SHA-256
`9376efc3a13c58b1163f8a0a0f06ec0b76eab2cfa70c20881d86ba2288e8e4c1`
y se invocó sin un `start` exterior. El recibo a **03:06:19.310 UTC** confirma
hello autenticado y fase `preparing_thread`, con **cero turnos de modelo iniciados**.

A **03:09:55.979 UTC**, ActivityManager registró `Trimming phantom processes`
y terminó el sshd de Termux y procesos de Horus. La terminal mostró `sigkill`;
el comprobador terminó con hangup/salida 129. Este intento **no aplica ni acepta
el candidato**: el check posterior conserva el SHA anterior, limpio/libre/idle,
sin recuperación ni candidato fallido. Los exit-info de la app solo contienen
registros antiguos; la atribución de esta caída se apoya en el registro actual
de ActivityManager. No se adjudican retrospectivamente las señales del 03/11.

### Recuperación acotada y repetición

Se reabrió la shell normal de Horus y se recuperó SSH con el helper existente.
Antes de reiniciar el bridge, su controlador verificó propiedad y salud, y el
contador de metadatos registró **cero turnos/aprobaciones activos**. Se conservaron
el recibo y la salida del primer intento en el perfil privado. Se detuvo el
keepalive existente, se reinició únicamente el bridge propio y se restauró el
keepalive. El controlador confirmó `MESTRY_OWNED_BRIDGE_STOPPED`, bridge listo
y keepalive activo, sin cambiar release, pairing, estado, puertos ni política.
Los hijos residentes de ese bridge dejaron de figurar tras el reinicio.

`max_phantom_processes=32` se conserva: no se desactiva ni amplía esa protección.
S25 abrió otra conexión por el perfil SSH guardado; el probe existente aceptó
loopback, health y rechazos de autorización. No se cambió Wi-Fi ni se reinstaló
ningún componente. El segundo intento se inicia después de conciliar el primero,
con el mismo candidato y sin una aplicación CLI previa. Su resultado final se
registra a continuación, separado del primer rechazo.


### Segundo intento: aplicación nueva verificada; cierre incompleto

La entrada `session.start` aplicó **`4865d2c…` → `dc3a872…`**, después de
las ocho suites ARM64: **141 tests**, árbol candidato
`0d0c8641a2ebfcb4a5ad6921ec38c408c95f5424`, validado a **03:34:16 UTC**.
El turno propio terminó `completed`; los recibos de comandos acreditan HEAD,
BUSY/salida 3 y preview con índice intacto. Una conexión nueva recibió
`session.content` y `session.sync`. Esos recibos no sustituyen todavía S25.

El comprobador devolvió **INCOMPLETE/salida 1** porque el estado final fue
`recovery_required`, libre y limpio. Se conserva ese resultado; no se declara
H3 cerrada. Los cinco comandos propios inspeccionados fueron lecturas del
proyecto, HEAD/espera y preview. No hay nuevas órdenes de terminación por recorte
de procesos en el registro seleccionado de este segundo intento.

### Carrera reproducida y corrección de la entrada del supervisor

La CLI histórica carga estado antes de intentar el lock. Se reprodujo con un
fixture Git y una liberación limpia controlada entre esos pasos: el snapshot
antiguo `running` produce un falso `UNCLEAN_SESSION_REVIEW_REQUIRED`. HEAD,
índice y política permanecen iguales. Esta condición es compatible con la
incidencia nativa; no se capturó una traza de la instrucción exacta que la marcó.

`atomic_project_poll.py` toma primero el lock, carga después el estado y sigue
siendo fetch-only. BUSY no carga ni sobrescribe al escritor; una recuperación
real no se limpia. Cuatro tests cubren snapshot anterior, BUSY, recuperación
real y sustitución revisada de la llamada antigua. La reproducción nueva
devuelve salida 0/fetch-only sin aplicar. Se revisará e instalará únicamente
esta llamada en el worker ya existente, conservando respaldo y rollback.
La corrección no reaprobará ni cambiará la política nativa. La carrera general
de la CLI histórica queda identificada para una transición de controles
separada; esta entrega corrige la entrada background que opera en H3.


### Tercer intento rechazado por validación, sin aplicación

`197aa5b99106db661395dc84cda9c093a5e0a3f1` pasó las suites previas,
pero `workflow` devolvió `tests_failed_or_missing` a **04:19:17 UTC**.
El bridge rechazó `session.start`, con cero turnos nuevos y sin fast-forward.
Se conservan `dc3a872…`, limpio/libre/idle, sin recuperación y con candidato
fallido registrado para el árbol `71a3047f…`. No se borró esa evidencia.
Dos casos temporizados pasaron en **15,824 s**, y la suite completa nativa
repetida con salida privada pasó **38 tests en 339,498 s**. No se capturó el
fallo original ni se atribuye una causa a partir de la repetición correcta.

### Corrección general del snapshot y transición revisada

Dos regresiones WSL fallan con la entrada anterior: una liberación limpia
parece recuperación, y una recuperación posterior al snapshot puede quedar
oculta. Moviendo la carga de política/estado dentro del lock, ambas pasan y
se preservan HEAD/índice/política del fixture. La suite WSL conserva los 38
casos y añade esos dos: **40 correctos**. No se omitieron pruebas ni se amplió
el presupuesto del validador. Se guarda ahora salida privada y acotada de
la regla que falle, sin imprimirla en el estado público.

Los dos archivos son controles protegidos. Se prepara un handoff acotado a
esos hashes, con política futura revisada antes de entrar. Cinco tests
comprueban rechazo de cambios no revisados/ajenos, preservación al fallar y
una recepción real contra Git local que valida, aplica y solo después
promueve el blob aprobado. No modifica huella de dependencias ni contrato.
La versión anterior permanece operativa hasta completar la validación del
candidato; no se aplica el SHA nuevo por CLI antes del bridge.


La preparación añade tres pruebas del plan sin mutaciones, del launcher
acotado y del rechazo fuera del perfil. El launcher y el plan se fijan por
hash; los cambios de política se limitan a los dos controles revisados,
sin cambiar contrato, identidad o huella de dependencias. La promoción
consume el blob revisado; no crea otra aprobación durante la recepción.
Se retirará ese PATH temporal antes del recorrido real S25.


### Recibo nativo del cuarto intento — 04/11, 13:39 UTC

El comprobador inició a **13:31:20.908 UTC** y terminó a **13:39:04.682 UTC**,
**PASS/salida 0**. `session.start` aplicó
`dc3a872a839295e6c4d65ef2b67eab3dcba90f30` →
`791688abdd59afb33516916c9e031c94553e02c5`, con
`applied_new_revision=true`. La validación ARM64 del árbol
`46026a14ed4088ddf4e663d8926a807202ca986d` pasó las ocho suites:
**54/4/28/13/3/40/9/4 = 155 tests**.

El turno nativo terminó `completed`; HEAD, BUSY, preview e historial fresco
pasaron. Final limpio/libre/idle, validación coincidente, sin recuperación ni
candidato fallido. La transición exacta de los dos controles se revisó antes
de entrar; el blob futuro se promovió tras validar/aplicar por el bridge.
Se mantuvo la huella anterior de dependencias. El launcher temporal se retiró
antes de S25: recibo con cero turnos, PATH normal e índice, release, pairing e
hilos preservados. No se reparó el estado después de este turno.

**La tarea real S25 sobre este SHA y su reapertura siguen pendientes** en este
punto cronológico. El S25 se bloqueó durante la preparación y requiere
intervención física para desbloquearlo; no se lee ni adivina su PIN.


El poll posterior a la retirada del launcher devolvió fetch-only OK,
`applied=false`, con HEAD/remoto en `791688a…`. El check nativo fresco de
13:53 UTC confirmó limpio/libre/idle, validación coincidente, sin recuperación
y `failed_candidate=null`. Se restaura el tag temporal de diagnóstico S25 y
los pins/parche piloto 9 locales; esa restauración WSL conserva los dos controles
nuevos y exige su revisión explícita. No se publica el cierre H3 sin la tarea
S25 faltante. Los probes S25 previos no alcanzaron SSH privado/túnel; WSL→Termux
SSH sí pasó. Se mantienen las capas separadas, sin atribuir causa por inferencia.


### Cuarto intento: transición revisada y recepción nueva — PASS

Se verificó de nuevo `dc3a872a839295e6c4d65ef2b67eab3dcba90f30`, limpio/libre/idle, sin recuperación.
El fetch-only observó `791688abdd59afb33516916c9e031c94553e02c5` sin aplicarlo. Los auxiliares privados coincidieron
con sus hashes publicados. La primera preparación devolvió BUSY antes del lock,
sin mutaciones; se concilió y repitió esa operación. Se revisaron los hashes
exactos del controlador y sus tests; contrato y huella de dependencias no cambiaron.

La política futura se preparó antes de entrar, limitada a esos dos controles.
El launcher privado quedó fijado por hash y limitado al lease del bridge.
`session.start` validó **155 tests ARM64**, árbol `46026a14ed4088ddf4e663d8926a807202ca986d`, aplicó
**`dc3a872a839295e6c4d65ef2b67eab3dcba90f30` → `791688abdd59afb33516916c9e031c94553e02c5`** y promovió solo entonces el blob previamente revisado.
No hubo aplicación CLI previa ni aprobación automática durante la recepción.
El turno nativo completó HEAD/BUSY/preview e historial fresco; terminó
limpio/libre/idle, sin recuperación ni candidato fallido. Se retiró el PATH
temporal antes de usar el S25. Se preservaron configuración ajena, release,
claves, pairing, índice e hilos, con backups y rollback.

### Tarea S25 y cierre obligatorio — PASS

La tarea del proyecto real leyó AGENTS.md/STATUS.md y ejecutó HEAD nuevo,
`receive --fetch-only` BUSY/salida 3 y `--within-turn finish README.md` con
índice intacto y publicación no solicitada. Ejecutó además cuatro tests de
recibos: **159 por target**. Los recibos pertenecen al mismo turno, terminal
`completed`, con lock liberado. Cierre del proceso y reapertura conservaron el
hilo y recuperaron recibos mediante `session.content` fresco.

El check nativo final confirmó `791688abdd59afb33516916c9e031c94553e02c5`, limpio/libre/idle, validación coincidente,
sin recuperación ni candidato fallido. No se reparó el estado después del
cuarto intento o la tarea S25 para conseguir esos valores. Interrupción complementaria aceptada en otro turno de espera: gesto normal sobre el control dinámico, turno identificado `interrupted`, actividad fresca y cero turnos activos.

La carga general de estado ya ocurre bajo lock; la identificación anterior de
esa carrera queda corregida por la transición de controles, además del poll
atómico instalado en el supervisor existente. No se capturó la instrucción
exacta de la marca nativa anterior. El rechazo original de workflow conserva
causa desconocida; la salida de futuros fallos queda ahora privada y acotada.

Se restauró el tag temporal S25. No hubo reinstalación ni cambios de protecciones,
red, OAuth, Drive o sincronizadores. README/parche/pins Android y dos auxiliares
Drive permanecen locales. La publicación posterior de este informe no acredita
otra recepción del checkout S23. Disponibilidad y cambio directo de red conservan
sus pruebas separadas; **H4/H5 pendientes**. [Recibo](../../validation/H3_BRIDGE_ACCEPTANCE_20261104.md).


### Conciliación de instrumentación S25

La captura inicial de ID al crear el hilo apuntó al hilo anterior del comprobador
nativo. Se conservó ese resultado, se identificó el hilo real por el mensaje
único enviado desde S25 y se verificaron sus recibos, sin reenviar la tarea. La
recarga fresca recuperó los cinco comandos completos; el snapshot parcial no
se tomó como ausencia de ejecución. La reapertura posterior conservó ese mismo
ID y recibió `session.content` nuevo. No se demuestra por esa captura prematura
un defecto adicional de selección de piloto 9.

La espera complementaria se envió una sola vez. Con actividad fresca del comando
y la descripción dinámica exacta, se verificó el padre habilitado y se realizó
una pulsación prolongada normal. El servidor confirmó ese turno `interrupted`,
cero actividad y contenido fresco. El turno principal de aceptación permanece
`completed`; no se mezclan ambas terminaciones. Se restauró el tag de diagnóstico
y se retiraron únicamente los archivos temporales propios del harness.
