# Sesiones de trabajo H2

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

El contrato inicial admite **WSL x86-64**, Python ≥3.12, Git ≥2.43 y Node ≥22.
Las dependencias instaladas permanecen locales. Alpine ARM64 se admitirá con
su contrato y validación en H3; estos wrappers no se han instalado en el S23.

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
H3 implementará recepción/admisión del proyecto real en el S23 por separado.
