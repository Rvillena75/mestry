# MESTRY — H3: clon operativo S23 y entrada desde S25

Fecha: **02/11/2026**, America/Santiago. **EN VALIDACIÓN**; este primer registro
acompaña el código que se probará en el nodo, sin declarar despliegue por tener
los archivos publicados. Continúa H2; no repite H0 ni modifica el ADR congelado.

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
