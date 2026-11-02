# MESTRY — H2: flujo de trabajo local y publicación revisada

Ejecución: **01–02/11/2026**, America/Santiago. Continúa H1 y la autorización de H2,
sin repetir la auditoría de teléfonos ni anticipar H3. El destino vigente es
el repositorio **público** `Rvillena75/mestry`, por la autorización posterior al
plan 09. No se crea otro repositorio ni coordinador.

## Resultado y alcance

Flujo H2 implementado y validado localmente: `start`, `finish`, `receive`,
`check`, comprobación de entorno, política portable versionada y estado privado
por checkout. Las dos cuentas conservan credenciales/historiales independientes
y comparten archivos por turnos. `finish` previsualiza; publicar requiere rutas
explícitas revisadas y `--publish` dentro del alcance autorizado.

**110 tests correctos**: 82 existentes y 28 pruebas de integración H2. El archivo
upstream fijado y el parche íntegro reproducen los **68 hashes de texto**. No se
ejecutó upstream ni se descargó/verificó otra vez el wrapper binario de Gradle.
La admisión automática del MESTRY real en S23/S25, paquetes ARM64 y operación
sin PC continúan en H3/H5; no se deducen del éxito de pruebas WSL.

La configuración y la publicación reales de este incremento se registran al
final de este documento tras completar su validación. La guía de uso es
[`docs/WORK_SESSIONS.md`](../../WORK_SESSIONS.md); el contexto de continuación
es [`STATUS.md`](../../../STATUS.md).

## Archivos y decisiones

| Archivo | Responsabilidad |
|---|---|
| `.mestry-workflow.json` | Remoto/rama/target, entradas de dependencias, archivos protegidos, selección admitida y seis validadores |
| `tools/work_session.py` | Operaciones Git explícitas, estado, lock, validación candidata, reconciliación de publicación |
| `tools/work-session.sh` | Entrada Bash/POSIX, mismo cwd y código de salida |
| `tools/check_env.py`, `tools/check-env.sh` | Versiones, target, huella de dependencias y pin del parche; nunca instala |
| `tools/WorkSession.ps1` | Acceso opcional desde Windows a WSL mediante argumentos separados |
| `tools/test_work_session.py` | 28 ensayos con clones y remotos bare temporales locales |
| `STATUS.md`, `docs/WORK_SESSIONS.md` | Estado verificable y operación por otros agentes |
| `README.md`, `AGENTS.md`, `docs/ROADMAP.md` | Entrada y continuidad del proyecto |

También se incorporan los informes locales previos 12/13 revisados. En las
copias públicas 10/11 solo se repara una referencia de nombre de archivo
deformada por el saneamiento inicial. Los originales históricos y el ADR
congelado no se reescriben ni sincronizan con las copias públicas.

La política se aprueba una vez por clon con `configure --review-policy` y se
conserva en `~/.local/state/mestry-workflow/<hash-del-checkout>/`: configuración
y estado 600, directorio 700. Ambas cuentas WSL pertenecen al mismo usuario
local y comparten este estado operativo; no comparten sus homes Codex. No se
configura autenticación nueva ni se leen archivos de credenciales para H2.

## Comportamiento verificado en laboratorio local

| Escenarios | Evidencia |
|---|---|
| Dirty, staged y untracked | Recepción rechazada; se conservan HEAD, bytes e índice |
| Fast-forward válido | Candidato probado antes de actualizar el checkout |
| Candidato con tests fallidos | La versión buena y el índice permanecen íntegros |
| Entrada de dependencias modificada | Rechazo antes de aplicar; sin instalar o borrar dependencias |
| Previsualización | Índice real idéntico byte a byte; ningún commit/push |
| Publicación seleccionada | Solo el candidato seleccionado; `.env` ignorado y otro documento dirty permanecen locales |
| Tests fallidos al cerrar | No se altera el índice real ni se crea commit |
| Índice previo ajeno o staging parcial | Rechazo y conservación de lo preparado previamente |
| `.env` forzado y marcador sintético | Rechazo antes de publicación |
| Marcador retirado de un commit posterior | Todos los commits salientes se inspeccionan; historial inseguro no publicado |
| Symlink y recorrido fuera del checkout | Selección rechazada |
| Remoto de lectura/push, rama o política diferentes | Requieren revisión; no se publica por otra ruta |
| Divergencia | Conservación de los dos historiales; sin rebase/reset automático |
| Offline y reanudación | Mantiene archivos locales y declara remoto no actualizado |
| Reintento sin cambios | Confirma referencia sin otro commit |
| Escritor hijo separado | Aunque salga el launcher, otro comando recibe `BUSY` hasta terminar el hijo |
| Señal TERM al supervisor | Reenvía al comando; retiene lock hasta finalizar el hijo separado |
| Sesión con fase running y sin lock | Bloqueo de recuperación explícita, sin robar el workspace |
| Hooks personalizados | Exigen revisión, sin desactivarlos silenciosamente |
| Remoto no disponible y recuperación | Conserva HEAD/índice y último éxito; reintento correcto |
| Dos contextos de cuenta | Mismo checkout, distintos `CODEX_HOME`, operaciones sucesivas correctas |

La suite usa solo Git local, Python stdlib y remotos desechables. Esas pruebas
de push no acceden al GitHub real. La publicación real se valida separadamente.
No son sesiones de inferencia de dos agentes ni una prueba de reconstrucción
de entornos nativos o de recuperación tras migraciones de bases de datos.

## Comprobaciones de plataforma y reproducibilidad

WSL **x86_64**, Python **3.12.3**, Git **2.43.0**, Node **22.23.1**. La huella
aprobable de entradas de dependencias inicial es
`ccd7a7f3068531fa87c2bad73c1416a9174d2d2dd3026c395c6edddbacfca080`.
El target admitido inicialmente es `wsl-x86_64`; no se afirma soporte H2 en
Alpine ARM64 por haber funcionado el fixture H1.

Comandos ejecutados desde el clon de desarrollo:

```sh
python3 -B -m unittest discover -s tools/horus_publish -p 'test_*.py'
python3 -B -m unittest discover -s tools/s25-codex-client -p test_helpers.py
python3 -B -m unittest discover -s tools/s23-remote-access -p 'test_*.py'
python3 -B -m unittest discover -s tools -p test_horus_pair_s25.py
node --test tools/s25-codex-client/pilot-policy.test.mjs
python3 -B -m unittest discover -s tools -p test_work_session.py
sh -n tools/work-session.sh tools/check-env.sh
python3 -B tools/check_env.py
```

Resultados por suite: **54 / 4 / 8 / 13 / 3 / 28**, todos correctos. La
reproducción adicional verificó el SHA del archivo cacheado, el SHA del parche,
extracción segura, aplicación en un temporal nuevo y los 68 hashes; cero
descargas/instalaciones/ejecución upstream. El pin del parche permanece
`342b44089b8ce39876b4b4f723fb480bbaf4c93825da8bf5995d84facff8401b`.
El parser oficial de PowerShell de Windows aceptó el wrapper sin errores.

## Operación comprobada en el clon real

- `configure --review-policy`: `OK`, sin auto-commit; política privada creada
  fuera del checkout. `check-env` confirmó `approval_status=matches`, sin errores.
- `check --remote`: HEAD y referencia GitHub inicial iguales a
  `0499557b70eef14a3fce993ee6a8935fe2a0f053`; estado dirty declarado por el
  incremento aún no publicado, no confundido con un árbol limpio.
- `start --resume --offline` ejecutó sucesivamente una comprobación de cwd y
  `codex --version` bajo cada home existente. Ambos devolvieron **0** y
  **codex-cli 0.166.0** en el mismo proyecto. No se lanzó inferencia ni login.
- `finish` sobre **17 archivos concretos** revisados devolvió el plan y
  `index_unchanged=true`, sin commit/push. Incluye documentación previa 12/13,
  reparaciones de referencias públicas 10/11 y el incremento H2.
- PowerShell bloqueó inicialmente el archivo UNC sin firma. La ejecución con
  `-ExecutionPolicy Bypass` limitada a ese proceso devolvió **0** y el estado
  correcto del clon. No se modificó la política permanente de Windows.
- Revisión acotada de patrones/rutas sobre todos los archivos públicos
  seleccionados: sin incidencias pendientes. Dos falsos positivos de rutas
  genéricas se corrigieron en el detector, sin cambiar los documentos históricos.
- Los hashes del original H0 y del ADR original coinciden con la línea base;
  el árbol histórico continúa sin `.git`. El parche conserva su SHA fijado.

## Integridad, límites y recuperación

El lock es **local y cooperativo** durante comando, pruebas y descendientes;
no reemplaza procedimientos para escritores externos que lo ignoren. Linux
subreaper permite esperar a hijos separados. Un SIGKILL, fallo del supervisor
o cierre abrupto exige revisar procesos y archivos antes de reaprobar el estado;
no hay recuperación automática que mate procesos ajenos o descarte trabajo.

La validación usa índice temporal y archivo Git aislado antes de modificar el
índice/árbol real. El cierre no descarta archivos sin confirmar. Cambiar archivos
protegidos o dependencias exige revisión explícita; no copiar `node_modules`,
venv o binarios entre arquitecturas. Los tests admitidos ejecutan código con
permisos del usuario: el mecanismo no es un sandbox para código no confiable.

Los patrones de secretos y metadata reducen riesgos conocidos, con revisión
de contenido adicional. No constituyen garantía universal. Estado, claves,
capturas y evidencia bruta quedan fuera de Git. No se leyó la carpeta privada
de credenciales S23 ni se usó ADB/SSH, ni se cambiaron servicios, cuentas,
FolderSync, rclone, permisos o distribuciones durante H2.

Rollback: dejar de invocar los wrappers, conservar commits/archivos y revisar
el estado; si se necesita revertir código, hacerlo por commit normal. No borrar
trabajo, instalaciones ni historiales. Ningún hook de apagado, cron, servidor
o mensajería nueva. La confirmación remota acredita GitHub; mantiene
`s23_received=not_checked` y `document_sync=external_not_run`.

## Siguiente incremento

H3 debe revisar en el S23 el entorno existente y el contrato de ejecución real,
preparar un clon fuera de sincronizadores y configurar su política propia.
Probar primero fetch/aviso, después recepción libre/limpia y actualización
candidata. La admisión desde S25 y cualquier programación requieren validación
específica. No migrar distribuciones ni desplegar ejemplos saneados por inercia.
