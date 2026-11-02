# MESTRY — H3: clon operativo S23 y entrada desde S25

Fecha: **02/11/2026**, America/Santiago. **ACTIVADA EN S23; ACEPTACIÓN S25 EN
VALIDACIÓN**. El clon ARM64 y la ida/vuelta Git ya tienen evidencia real; falta
terminar la entrada del cliente móvil. Continúa H2, sin repetir H0 ni modificar
el ADR congelado.

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
Tampoco se acredita aún una aplicación automática real de un candidato por
la entrada del bridge: los primeros incrementos se incorporaron mediante
bootstrap explícitamente revisado. Las suites cubren ese mecanismo; la
aceptación física sigue separada de los tests.

| Comprobación | Estado / evidencia |
|---|---|
| Clon real ARM64 y entorno compatible | Verificado: contrato y 137 tests en el S23 |
| Despliegue sobre release privada anterior | Verificado: `H3_ADMITTED`, pairing y estado conservados |
| Fetch desde supervisor existente | Verificado: estado real del polling, sin aplicación de archivos |
| Push S23 y recepción WSL | Verificado: `f0df88d…`, documento recibido y 137 tests WSL |
| Aplicación automática desde entrada gestionada | Pendiente de prueba física; no confundir con el bootstrap |
| Hilo nuevo S25 que lea estado y continúe | Pendiente de transporte disponible y operación de interfaz coordinada |
| Lock durante un turno real del cliente | Cubierto en fixtures; pendiente de la misma prueba física S25 |
| PC apagado, reposo y reinicio | H5; no probado aquí |

Como alternativa no destructiva al ADB intermitente se intentó SSH al guest
mediante el salto Termux existente. La identidad WSL actual fue rechazada por
SSH; no se obtuvo sesión ni se registraron claves, habilitaron métodos o
modificaron permisos. No afecta al acceso legítimo Bare terminal ya utilizado.
El pin temporal del host se mantuvo separado del `known_hosts` normal. No se
copiaron contraseñas, tokens ni hogares Codex.

La documentación técnica de esta aceptación se publicó en WSL como
`c4b3cb21b12b47d916a1c9b196ae56f6271485cc`. Su recepción en el S23 todavía
no se confirma. El último commit originado allí y recibido en WSL es `f0df88d…`;
no se presenta un fetch supuesto como prueba de aplicación.

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

El usuario asignó el S25 al otro hilo. Esta continuación utiliza exclusivamente
la interfaz del S23 y conserva bridge, SSH, VPN y emparejamientos existentes.
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

La validación ARM64 de esta corrección y la tarea nueva de Codex se registrarán
después de ejecutarlas. El total sigue siendo 137 tests; el fixture de SSH es
sintético y no modifica túneles ni servicios reales.
