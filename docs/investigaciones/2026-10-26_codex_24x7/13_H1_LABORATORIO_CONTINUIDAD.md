# MESTRY — H1: laboratorio de continuidad ejecutado

Fecha: **01/11/2026**, America/Santiago. Continuación autorizada por el usuario
después de guardar las credenciales locales del S23. Se mantuvo separado del
repositorio MESTRY público y de los proyectos/documentos reales.

## Resultado y alcance de aceptación

**H1 técnica validada: ida/vuelta GitHub, ejecución WSL/Alpine ARM64, perfiles
independientes, integridad y rechazos seguros.** Ambos clones aceptaron finalmente
`34004dd48ce7b6403112b6db4e366c556bdf55f8`, con **8 pruebas unitarias** por target,
**14 escenarios WSL** y **2 comprobaciones de protección en el S23**.

Esta aceptación corresponde a **Git y runtime**, el alcance sin inferencia
previsto en el informe 10. No se iniciaron turnos de modelos: se comprobaron los
dos perfiles Codex WSL y se ejecutaron comandos bajo sus contextos por turnos,
pero **no se afirma que dos agentes Codex reales desarrollaran la funcionalidad**.
El ensayo de agentes mediante inferencia no se ejecutó. Tampoco se aceptan con
este laboratorio dependencias nativas arbitrarias, operación sin PC o 24/7.

## Recursos creados y límites preservados

| Recurso | Alcance |
|---|---|
| Remoto | [Rvillena75/mestry-continuidad-lab](https://github.com/Rvillena75/mestry-continuidad-lab), **privado**, rama de trabajo `main` |
| Laboratorio WSL | `~/mestry-lab/continuidad-trabajo-v1`, fuera de rclone |
| Auxiliares WSL | `~/mestry-lab/continuidad-trabajo-v1-aux`, clones/worktrees/casos conservados |
| Laboratorio Horus | `/workspace/projects/mestry-continuidad-lab`, perfil `/home/horus` |
| Fixture | `calc.py`, `test_calc.py`, README, AGENTS, STATUS, ignores/attributes, `NOTES.md` y `EVIDENCE.json` |
| Prototipos de sesión | `tools/lab_session.py`, `lab-start.sh`, `lab-finish.sh`, `lab-status.sh`, dentro del laboratorio |
| Autor Git | Configuración **local de cada clon**, cuenta GitHub existente y correo noreply; sin copiar autenticaciones |

No se clonó el MESTRY real en el teléfono ni se instaló polling, cron, hook de
apagado, servicio adicional o coordinador. No se modificaron FolderSync, rclone,
permisos Android, claves SSH, emparejamientos ni arquitectura congelada. Los
ejemplos saneados del repositorio público no se desplegaron en los teléfonos.

## Recuperación del acceso y preflight real

Se reutilizó el servidor ADB existente y se revalidó el S23 **SM-S918B** autorizado.
El PIN y la contraseña guardados se usaron únicamente en las interfaces normales
de bloqueo Android e inicio Horus. No se imprimieron, copiaron al laboratorio,
incluyeron en argumentos Windows ni incorporaron a informes/Git/memorias.
El archivo local conservó modo **600**, directorio **700**.

Horus **1.1.0** se abrió normalmente y se seleccionó el perfil Alpine y Bare
terminal. Esto inició el guest existente y volvió a disponer su SSH loopback
8022; no hubo aprovisionamiento, cambio de distribución ni instalación. El bridge
8787 no se recuperó como parte de H1: la terminal bastó para el laboratorio.

| Comprobación dentro del perfil que ejecutó Git | Resultado |
|---|---|
| Home / UID guest | `/home/horus`, UID **1000**, comprobados antes de operar |
| Sistema | `/etc/os-release`: **alpine / 3.24.0** |
| Arquitectura | **aarch64** |
| Python | **3.14.8** |
| Git | **2.54.0** |
| GitHub | Cuenta esperada, API del repo privado, clone/fetch y **push reales** desde el perfil propio |
| Codex | `login status` retorno **0**, ChatGPT; solo booleans proyectados, sin salida bruta |
| WSL | **x86_64**, Python **3.12.3**; ambos perfiles Codex con `login status=0`, homes de autenticación separados y sin symlink del archivo de auth |

La disponibilidad de auth no se usó para leer conversaciones ni consumir
inferencia. Los comandos del guest se introdujeron por la terminal legítima;
los archivos se recibieron/publicaron directamente con GitHub desde el S23.

## Recorrido realizado y commits

| Commit | Actor/contexto y resultado |
|---|---|
| `3ce5677d57fe` | Base WSL: suma entera tipada, **2 tests**, documentación y prototipos con controles |
| `630d6bfa871b` | S23: clonó la base, pasó **2 tests**, publicó evidencia propia y confirmó la ref remota |
| `ed9faf3f7a06` | WSL, contexto perfil A: recibió evidencia S23, añadió `total`, tests y un `NOTES.md` nuevo legítimo; **4 tests**, cierre revisado y push |
| `860cd2598d3f` | S23: recibió el commit WSL, validó el candidato, añadió media exacta con `fractions.Fraction`; **8 tests** y push confirmado |
| `d35972777c5a` | S23: publicó pruebas reales de rechazo por dirty y busy, conservando HEAD y cambios |
| `34004dd48ce7` | WSL, contexto perfil B: recibió la continuación, cotejó SHA-256 y tests; cerró STATUS/EVIDENCE con resultados y límites |

El perfil B utilizó **el mismo checkout WSL** por turno y obtuvo los avances
desde Git/documentación, sin compartir homes, credenciales ni conversaciones.
La ejecución fue del harness técnico, no de un nuevo hilo de modelo. `STATUS.md`
explica lo implementado, validación, límites y siguiente incremento.

Después el S23 recibió también el último commit: su terminal mostró
`state=RECEIVED`, `candidate_tests=8`, `updated=true`, el SHA completo y después
`git rev-parse --short=12 HEAD` → **`34004dd48ce7`**. Se observaron la salida y el
SHA en una captura local del terminal sintético, sin secretos o conversaciones.

Los hashes de `calc.py`, `test_calc.py`, `STATUS.md` y `NOTES.md` se conservan en
`EVIDENCE.json`; la recepción WSL comprobó bytes contra los generados por S23.
Una descarga independiente verificó también la versión final y sus hashes.

## Casos de seguridad y recuperación ejecutados

Todos los fallos se introdujeron en clones/worktrees **nuevos del laboratorio**.
No se alteraron servicios reales para simular red o fallos del código.

| Caso | Resultado verificado |
|---|---|
| Archivo tracked sin confirmar | `DIRTY_OR_UNTRACKED`, código 3; HEAD y bytes intactos |
| Índice staged | Rechazo; índice, archivos y HEAD conservados |
| Archivo nuevo sin seguimiento | Rechazo; archivo nuevo conservado |
| `.env` sintético forzado con `git add -f` | Git permitió el staging forzado; el cierre **rechazó su publicación**, sin borrar el índice para ocultarlo |
| Índice ajeno al conjunto seleccionado | `PREEXISTING_INDEX_NOT_SELECTED`; sin reescribir trabajo previo |
| Marcador prohibido dentro de un archivo admitido | Rechazo antes de commit/push; candidato conservado |
| Falso secreto en commit local intermedio y retirado después | Revisión de todo el historial saliente lo rechazó; ambos commits locales se conservaron, **sin subirlos** |
| Remoto no disponible | Proxy inválido solo en configuración local de un clon de prueba; rechazo sin modificar HEAD/árbol; configuración retirada y reintento correcto |
| Checkout limpio pero con una tarea gestionada activa | `BUSY`; no se aplicó una actualización durante la tarea |
| Candidato remoto con tests fallidos | `TESTS_FAILED` antes del fast-forward; versión anterior y su ejecutabilidad preservadas |
| Historias divergentes | Segundo push normal rechazado; `receive` devolvió `DIVERGED`; ambos commits sobrevivieron |
| Integración del caso divergente | Conflicto real, resolución explícita conservando ambas contribuciones, merge y push normal; ambos commits siguen como ancestros |
| Dos worktrees | Archivos y locks locales distintos, retenidos simultáneamente; no se simularon dos agentes reales |
| Reconciliación de publicación | Un cierre posterior sin cambios comprobó ref remota y devolvió `new_commit=false`; sin commit duplicado |
| Dirty/busy en el kernel real del S23 | Dos rechazos con código 3, HEAD conservado; el archivo dirty mantuvo sus bytes |

Los resultados automatizados WSL contabilizan **14 escenarios**, incluyendo
subcasos de índice, red y divergencia. Se añaden las dos comprobaciones S23.
La prueba de candidato preserva código **stdlib**; no se presenta como prueba
de reconstrucción de venv, paquetes nativos o rollback de una migración de datos.

Los prototipos usan Git, Python stdlib y un lock local cooperativo durante el
comando escritor/prueba. Validan una copia candidata dentro de `.git` antes de
aplicar fast-forward; el cierre selecciona rutas explícitas, prueba, revisa
commits salientes y reconcilia la ref. No equivalen a aislamiento frente a otros
procesos del mismo UID que ignoren el procedimiento, ni a un validador general
de seguridad para cualquier repositorio. H2 debe adaptar su contrato al proyecto.

## Evidencia conservada y estado final

- `main`: **14 archivos** del fixture; limpio en WSL, ref publicada y recepción
  S23 final comprobadas. Los temporales y el `.env` sintético se conservan solo
  localmente como datos de prueba, fuera del conjunto publicado.
- Rama privada **`h1-validation-evidence`**: script operador y resultados WSL
  archivados. Repetir exige nombres/rutas nuevos y revisión; no ejecutar sobre
  los casos existentes como si fueran un instalador genérico.
- Rama **`h1-divergence`**: integración que conserva ambas historias del caso.
- Rama **`h1-invalid-candidate`**: candidato deliberadamente fallido, conservado
  como evidencia. No es una release funcional ni debe integrarse en `main`.
- Clones auxiliares locales: conservan estados dirty/staged/untracked y commits
  rechazados; no se hizo reset, clean, force-push ni borrado de esas historias.
- Auditoría de una descarga completa del remoto: **11 commits / 31 blobs** de
  todas sus ramas; ningún `.env`, temporal o marcador completo del falso secreto
  en la historia publicada. No aparecieron patrones de credenciales reales.
  Es una comprobación acotada, no garantía universal de ausencia de secretos.

El repositorio **MESTRY público** no recibió commits/push de este incremento.
La revisión documental local previa se preservó. Los originales y ADR privados
no fueron sustituidos por copias saneadas ni modificados.

### Incidencias resueltas durante el ensayo

La entrada inicial de una orden larga se truncó en la terminal. Se canceló solo
esa orden incompleta de la nueva shell y se enviaron fragmentos cortos. Otro
envío agrupado agotó el timeout del cliente; antes de repetir se comprobó que
había quedado en asignaciones parciales, sin ejecutar la modificación. Se
retransmitió de forma serial y se verificaron commits/estado. No se interpretó
el timeout como prueba de publicación ni se duplicó el cambio.

### Siguiente paso

**H2:** convertir lo validado en acciones de trabajo del proyecto real
`start/finish/receive/check`, comprobador de entorno y estado mantenido, con una
política explícita de publicación y capacidades por target. Reutilizar los
prototipos del lab; no repetir H0 ni desarrollar un coordinador. **H3** admitirá
después el clon MESTRY en S23/S25 y su actualización, inicialmente fetch/aviso.
El ensayo con agentes reales, dependencias nativas y disponibilidad H5 conserva
sus criterios separados; no se deducen del éxito de Git.
