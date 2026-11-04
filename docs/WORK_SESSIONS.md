# Sesiones de trabajo H2/H3

Este flujo trabaja sobre el clon Git fuera de Drive. Cada cuenta conserva su
propio home Codex; comparte únicamente el checkout por turnos. No necesita
conversaciones anteriores ni un hook de apagado. [Estado vigente](../STATUS.md).

## Preparación local revisada

Desde el clon, leer `.mestry-workflow.json` y los scripts antes de ejecutar:

```sh
sh tools/check-env.sh
sh tools/work-session.sh configure --review-policy
sh tools/work-session.sh check --remote
```

`configure` aprueba explícitamente remoto, rama, correo Git, contrato, archivos
de control y huella de dependencias actuales. Guarda política y estado con
permisos 600 en un directorio 700 fuera del repositorio:
`~/.local/state/mestry-workflow/<hash-del-checkout>/`. No inicia autenticación,
instala paquetes ni cambia configuración Git. Repetirlo exige revisar primero
los cambios de política/entorno; no usarlo automáticamente para quitar un error.

El contrato admite **WSL x86-64 y Alpine ARM64**, Python ≥3.12, Git ≥2.43 y
Node ≥22. Las dependencias instaladas permanecen locales. El clon S23 pasó las
ocho suites en H3; su admisión concreta y el cliente S25 se registran en el informe 15.

## Inicio y continuación

```sh
sh tools/work-session.sh start -- env CODEX_HOME="$HOME/.codex" codex
# Otro turno, con el launcher existente de la segunda cuenta:
sh tools/work-session.sh start -- codex2
```

`start` exige árbol limpio, obtiene referencias y solo aplica fast-forward tras
validar una copia candidata aislada. Si fallan tests, cambia una dependencia,
hay divergencia o trabajo pendiente, conserva la versión anterior. Después
mantiene un bloqueo local durante el comando y sus descendientes. Las dos
cuentas heredan sus launchers y entornos independientes; no se copian homes.

Para continuar trabajo local incompleto sin aplicarle una versión remota:

```sh
sh tools/work-session.sh start --resume -- codex2
# Sin conectividad, aceptando expresamente que el remoto no está actualizado:
sh tools/work-session.sh start --resume --offline -- codex
```

`--resume` obtiene referencias para inspección, sin modificar los archivos.
`--offline` no contacta GitHub. Una sesión offline no puede confirmar recepción
o publicación. No ejecutar escritores/pruebas paralelos fuera del wrapper.

El bloqueo es cooperativo, no un aislamiento frente a procesos del mismo UID.
El supervisor Linux espera incluso a hijos que se separan de la sesión; señales
TERM/HUP/INT se reenvían al grupo principal sin liberar antes el bloqueo.
Un cierre forzado del supervisor puede dejar descendientes: se conserva fase
`running` y las próximas operaciones gestionadas requieren revisión. Comprobar
procesos y archivos, esperar a los escritores y revisar antes de volver a
`configure --review-policy`. No cerrar una sesión gestionada dejando un servidor
indefinido: el bloqueo seguirá retenido mientras viva su descendiente.

## Revisar y publicar al terminar

Actualizar la documentación existente y `STATUS.md` con resultado, pruebas,
limitaciones y siguiente tarea. No transcribir conversaciones. Revisar:

```sh
git status --short
git diff -- README.md STATUS.md tools/example.py
sh tools/work-session.sh finish README.md STATUS.md tools/example.py
```

El último comando es una **previsualización**, sin commit/push ni cambios en el
índice real. Construye objetos Git temporales y registra el intento local. Las
rutas del ejemplo deben sustituirse por archivos concretos revisados que existan
o eliminaciones explícitas. No usar `git add .` como cierre automático.

Tras revisar el conjunto y disponer de autorización para publicarlo:

```sh
sh tools/work-session.sh finish --publish --message "Describe reviewed change" README.md STATUS.md tools/example.py
sh tools/work-session.sh check --remote
```

El cierre selecciona solo esas rutas en un índice temporal, examina todo el
candidato y todos los commits salientes, ejecuta las seis suites en una copia
aislada y vuelve a comprobar HEAD, índice, política, archivos y remoto. Solo
después modifica el índice real, crea un commit normal y hace push sin force.
Un staging previo no seleccionado o parcial se rechaza y conserva. Los cambios
no seleccionados permanecen locales y no contaminan los tests del candidato.

La verificación posterior consulta la referencia remota: puede confirmar el
commit exacto o que el remoto avanzó conservándolo como ancestro. Un fallo de
push conserva el commit; el reintento reconcilia la referencia sin inventar un
segundo commit. `remote_contains_commit=true` acredita GitHub, **no recepción
S23** ni sincronización Drive. Esas salidas permanecen explícitamente separadas.

La política bloquea rutas privadas, dependencias instaladas, binarios/evidencia
bruta, symlinks, submódulos y patrones conocidos de secretos/metadatos. Es una
defensa acotada más revisión humana, no garantía universal de ausencia de
secretos ni sandbox frente a tests maliciosos. Los tests candidatos ejecutan
código del repositorio admitido con permisos del usuario. No ejecutar este flujo
con código no confiable. Los hooks locales personalizados exigen revisión.

Cambiar validadores o archivos protegidos requiere revisar y aprobar otra vez la
política antes de publicar. Cambiar entradas de dependencias bloquea recepción
y publicación: preparar/validar el entorno por separado, conservar el operativo
y aprobar la nueva huella solo cuando las dependencias estén verificadas.
H2 detecta cambios; no implementa migraciones de venv, bases o paquetes nativos.

## Consultar, recibir y diagnosticar

```sh
sh tools/work-session.sh check
sh tools/work-session.sh check --remote
sh tools/work-session.sh receive --fetch-only
sh tools/work-session.sh receive
sh tools/check-env.sh
```

`check` muestra dirty, busy, ahead/behind de la referencia **en caché**, última
observación, recuperación pendiente y errores de entorno. `--remote` consulta
la ref actual sin aplicar cambios; un error no sustituye el último éxito.
`receive --fetch-only` permite observar sin cambiar el árbol. `receive` solo
aplica si libre, limpio, compatible y con tests correctos. Los bloqueos devuelven
código **3** y un motivo estable; errores externos no imprimen credenciales.
No hay stash/reset/clean, resolución automática de conflictos ni borrado local.

`validation` y `validation_matches_head` indican qué árbol se probó.
`failed_candidate` conserva el hash/regla del candidato rechazado incluso tras
un fetch exitoso; solo una validación completa correcta limpia ese error.

Desde PowerShell, el wrapper opcional conserva argumentos y código de salida:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\WorkSession.ps1 -Repo '<ruta absoluta Linux del clon>' -Action check
```

Windows puede bloquear el archivo sin firma en una ruta UNC WSL. El ejemplo
permite ejecutar únicamente ese proceso revisado; no cambia la política
persistente de Windows ni requiere `Set-ExecutionPolicy`. Bash sigue siendo
la entrada principal.

Para iniciar Codex o pasar opciones avanzadas, preferir una terminal WSL y los
comandos Bash anteriores. El wrapper no transforma rutas Windows ni configura
la distribución; `-Distribution` selecciona una distribución WSL existente.

## Recuperación y alcance

Ante divergencia: conservar ambos historiales, inspeccionar y resolver en una
acción explícita. Ante desconexión: continuar con `--resume --offline`, guardar
el trabajo y reintentar al recuperar red. Ante fallo de tests: revisar el
candidato sin reemplazar el árbol operativo. El estado local conserva el último
éxito y el intento posterior fallido, sin contenidos de comandos o secretos.

Rollback de H2: dejar de usar los wrappers y conservar commits/archivos locales;
no borrar dependencias, ramas, credenciales o trabajo pendiente. Cualquier
reversión de código publicado será otro commit revisado, nunca force push.
No se añade un coordinador, servicio, cron ni sincronización al apagar Windows.
La implementación y aceptación H3 se registran por separado en el informe 15.

## Entrada gestionada desde S25 — H3

`project-gate.mjs` integra el bridge existente con el mismo lock local mediante
`work_session.py lease`. La operación de metadatos de un hilo mantiene el lock
hasta su respuesta; un turno lo mantiene hasta su notificación terminal con
thread/turn IDs coincidentes. Un timeout ambiguo o pérdida del proceso padre
deja recuperación pendiente. No es un coordinador ni mantiene conversaciones
entre cuentas. Los escritores externos siguen sujetos al procedimiento.

El supervisor existente puede leer una configuración privada `projects.json`
en su directorio de estado y ejecutar **solo fetch** cada 120 segundos. No aplica
archivos en segundo plano. Al entrar desde el bridge, un checkout limpio y
libre recibe el candidato validado; el trabajo dirty continúa sin sobrescribirlo.
El modo inicial de la clase de guardia es observación; la admisión revisada
activa recepción únicamente en esas entradas gestionadas.

Dentro de un turno protegido o del escritor lanzado por `start`, las pruebas
directas ya quedan bajo el lock.
Para un cierre autorizado se usa `sh tools/work-session.sh --within-turn finish
<rutas>` y, tras revisar, la misma orden con `--publish`. Se comprueban PID,
inicio del proceso y ascendencia del backend registrado: otro terminal no puede
tomar prestado el lock con esa opción. El cierre conserva la fase `running`;
solo el final real del turno libera la propiedad. No se copian credenciales ni
se incorpora otro servicio. La validación usa exclusivamente metadatos `/proc`.

`s23_project.py verify` valida el clon ARM64 configurado. `activate --head <SHA>
--review` exige ese HEAD limpio y validado, conserva backups y genera un overlay
de código sobre la release **existente en el teléfono**, manteniendo cuentas,
emparejamiento y dependencias locales. No es un instalador genérico: exige el
perfil y ruta admitidos, y rechaza un bridge activo o configuración previa de
polling que requiera revisión. No ejecutar por simple prueba local en WSL.

La ruta S25 apunta al proyecto real tras admitirlo. Su asignación documental
Drive no se amplía automáticamente; H4 conserva ese control por separado.
La prueba de independencia prolongada del PC permanece en H5.

Desde Bare terminal/SSH del perfil admitido, usar el binario nativo existente:

```sh
cd /workspace/projects/mestry
sh tools/work-session.sh start -- /home/horus/.local/bin/codex \
  -c 'approval_policy="never"' -c 'sandbox_mode="danger-full-access"'
```

Estos argumentos reproducen la excepción de Horus ya aprobada para el bridge;
no escriben configuración ni trasladan credenciales. No representan un sandbox
del sistema operativo ni una política general para WSL u otros proyectos.
La aceptación real utilizó `codex exec` con esos mismos argumentos, una tarea
de lectura, rechazo `BUSY` y preview `--within-turn finish` correcto. Ver informe 15.

Para consultar pendientes desde una terminal remota del S25, `check --remote`
muestra estado local, referencia observada, validación y candidato rechazado.
El estado del polling se conserva en el `status.json` privado del supervisor;
ninguno de esos estados operativos se sincroniza por Drive o Git.


## Transición acotada de controles para H3

La entrada nueva carga política/estado **después de adquirir el lock**, también
cuando verifica un préstamo `--within-turn`. Dos regresiones cubren la liberación
limpia y una recuperación aparecida entre el snapshot antiguo y la adquisición.
Un fallo de suite conserva únicamente la salida de esa regla, acotada a 2 MB y
modo 600 fuera de Git; `check` informa la referencia privada y no su contenido.

`reviewed_workflow_handoff.py` consume un plan privado, revisado y fijado por
SHA-256, para una pareja exacta de commits. Solo admite cambios de pins en
`work_session.py` y `test_work_session.py`; contrato, entorno/dependencias,
remoto, identidad y resto de controles deben seguir iguales. No crea una
aprobación ni invoca `configure`.

El plan contiene la política futura ya revisada. El bridge valida la copia
candidata con esos hashes mientras conserva checkout/política anteriores.
Solo tras el fast-forward gestionado promueve ese mismo blob aprobado, verifica
el nuevo checkout y guarda un recibo privado. Un fallo previo conserva la
versión anterior; una promoción incompleta conserva recuperación, sin reset.
El código de compatibilidad se usa mediante un launcher privado solo durante
la entrada del bridge y se retira de PATH antes del ensayo S25. El launcher
y el plan no se copian entre cuentas ni incluyen credenciales.

Esta transición es una operación revisada del despliegue existente, no un
instalador genérico ni un modo de aceptar dependencias nuevas automáticamente.
Conservar backups y probar el SHA exacto; no usarla para silenciar un bloqueo
que aún no fue conciliado.


La preparación de esa transición se hace con `prepare_workflow_handoff.py`,
solo en el perfil/ruta admitidos y con `--review`, SHA anterior/nuevo y los
dos hashes de fuente esperados. Conserva backup, no escribe política ni HEAD
y activa un launcher privado únicamente en el PATH del bridge existente.
El launcher fija por hash el adaptador y su plan y deja intactos los demás
comandos Python. Tras verificar la recepción y terminar el turno,
`--restore-launcher <directorio de revisión> --review` reinicia el bridge
propio sin ese PATH temporal; no revierte la política ya promovida ni Git.
Cada reinicio exige cero turnos/aprobaciones y comprueba preservación de
release, pairing, índice e hilos. Los recibos/planes quedan privados.
