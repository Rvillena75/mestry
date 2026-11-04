# Comprobaciones con solo el S23

Estas herramientas verifican componentes existentes. No instalan paquetes,
abren servidores, cambian SSH/VPN/OAuth ni aceptan el cliente S25. Las evidencias
JSON se conservan privadas fuera de Git; los informes públicos solo contienen
resultados revisados.

## Bridge desde Horus

Ejecutar **desde Bare terminal del perfil existente `/home/horus`**, después de
revisar `STATUS.md`. El bridge debe estar saludable y el checkout libre/limpio.
No envolver este cliente con `work-session.sh start`: el turno del bridge
adquiere ese mismo lock y una envoltura exterior lo bloquearía. La tarea de
Codex solicita solo lecturas y el preview de cierre; no modifica el checkout.

```sh
cd /workspace/projects/mestry
node tools/s23-remote-access/accept_s23.mjs
```

El comprobador utiliza la clave de emparejamiento **dentro de su UID**, mediante
cabecera y un WebSocket loopback. No muestra la clave ni usa tokens en URLs.
Inicia **un turno real del modelo**: lee AGENTS/STATUS, registra el HEAD mediante
un comando, espera diez segundos y prueba `--within-turn finish README.md`.
Durante el turno verifica `receive --fetch-only -> BUSY`; después abre otra
conexión y solicita `session.content`/`session.sync` del mismo hilo. Solo acepta
comprobantes de comandos terminados con salida 0, sin usar afirmaciones del asistente como prueba.

El recibo distingue el SHA anterior/posterior a `session.start` y conserva la
validación del target. `entry_application.applied_new_revision=true` exige
SHAs diferentes; un diagnóstico sobre un checkout ya actual no acredita recepción nueva.

El informe privado queda en
`~/.local/state/mestry-s23-checks/result.json`. Un timeout ambiguo no autoriza
reintentar un turno, quitar locks, reaprobar políticas ni reiniciar servicios.
Revisar el resultado y la sesión existente antes de otra ejecución. El helper
solo puede interrumpir el turno propio que llegó a identificar.

Si el script aún no está recibido por Git, se puede transferir únicamente este
archivo de código al estado privado del perfil mediante la terminal normal,
comparando SHA-256 antes de ejecutarlo. No copiar homes ni claves y no sustituir
la release instalada por la configuración pública de ejemplo.

## Observación de pantalla apagada

Desde WSL, usar una terminal separada. La herramienta consulta el **servidor ADB
existente por su protocolo**; no lanza `adb.exe`, no inicia ni reinicia el daemon.
Debe estar autorizada la conexión y responder el alias SSH existente de Termux.
Los datos se filtran antes de guardarse: batería, memoria, estado de pantalla,
térmico y salud del bridge. No almacena registros de batería ni pantallas.

```sh
mkdir -p -m 700 /ruta/privada/nueva-evidencia
python3 -B tools/s23-remote-access/observe_s23.py \
  --serial S23_SERIAL \
  --powershell /ruta/al/WindowsPowerShell/v1.0/powershell.exe \
  --duration 1200 --interval 30 \
  --output /ruta/privada/nueva-evidencia/observacion.json
```

En un host que llegue directamente al servidor ADB local, omitir `--powershell`. Para un
ensayo desde una terminal independiente, anteponer `sh tools/work-session.sh
start --resume --offline --` al comando Python; mantiene el lock WSL durante
la medición. Dentro de un escritor ya protegido, ejecutar Python directamente
sin anidar `start`.
`S23_SERIAL` y las rutas son ejemplos; no escribir la identidad real en Git.
El directorio de salida debe pertenecer al usuario, con modo 700, y el archivo
debe ser nuevo. Se guarda atómicamente con modo 600 después de cada muestra.

Separar la preparación interactiva de la ventana medida. Volver al inicio y
apagar la pantalla normalmente, sin cambiar ajustes ni usar `force-idle`.
Las consultas pueden despertar CPU; `Dozing` es un estado de pantalla y **no
prueba Doze profundo**, independencia del PC ni disponibilidad 24/7. Una consulta
fallida queda como error; nunca se convierte en batería/RAM cero ni en éxito.

## Límite documental

La lectura Drive ya registrada en el informe 15 conserva su evidencia histórica.
Sus auxiliares continúan locales y no forman parte del candidato nativo H3.
Esta aceptación no ejecuta OAuth, publicaciones ni restauraciones documentales.

## Pruebas offline

```sh
python3 -B -m unittest discover -s tools/s23-remote-access -p 'test_*.py'
python3 -B -m unittest discover -s tools/horus_publish -p 'test_*.py'
node --test tools/s23-remote-access/accept_s23.test.mjs
```

Ejecutarlas desde un escritor protegido por `work-session.sh start`, conforme a
AGENTS. Las fixtures no usan teléfonos, OAuth ni inferencia. La aceptación real
se documenta por separado en el informe 15.


## Prueba S25 desde otra red

El ensayo físico del 03/11 aceptó el primer turno de una conversación nueva
con piloto 9: HEAD, BUSY, preview, terminación y contenido fresco. Se corrigió
la selección al reabrir; dos reinicios del proceso conservaron el hilo esperado.
También se aceptaron SSH, túnel, autorización e historial fresco sobre datos
móviles, con red predeterminada `CELLULAR` y sin agente Wi-Fi. El informe 15
conserva la evidencia anterior y los límites de cada ensayo.

El cambio directo de Wi-Fi a datos no recuperó contenido fresco. Con cero tareas
activas, establecer de nuevo el perfil SSH guardado después de cambiar de red;
no reenviar una tarea ambigua para comprobar conectividad. Wi-Fi quedó restaurado
y la recarga posterior volvió a recibir contenido fresco.

Antes de enviar una tarea, comprobar la VPN local desde la pantalla principal
de Tailscale y abrir el perfil SSH existente en ConnectBot. El estado de un
**dispositivo remoto** dentro de Tailscale no confirma la VPN local. Un aviso
antiguo de autenticación en una terminal tampoco acredita una conexión nueva.
Durante este ensayo fue necesario cerrar el cliente SSH desconectado y abrirlo
con la VPN ya activa; se conservaron perfil, claves y reenvío.

La política existente conserva 30 s para volver desde otra app y 60 s para la
conexión inicial. Si hace falta preparar el túnel más despacio, hacerlo sin
tareas activas, con MESTRY cerrado y la VPN conectada normalmente desde
Tailscale; después volver a MESTRY y mantenerlo en primer plano. No cambiar los
plazos ni reconfigurar los destinos para superar una desconexión.

1. Abrir MESTRY y conectar usando el perfil privado guardado. Mantener la app en
   primer plano durante la prueba; no sustituir el destino por la IP LAN al estar
   fuera de casa ni reconfigurar claves o reenvíos ante un rechazo.
2. Elegir el proyecto `mestry` y abrir **una conversación nueva**. Enviar:

   ```text
   Prueba S25 remota, solo lectura. No edites ni publiques.
   En /workspace/projects/mestry lee AGENTS.md y STATUS.md y ejecuta git rev-parse HEAD.
   Ejecuta sh tools/work-session.sh receive --fetch-only: el rechazo BUSY es esperado.
   Ejecuta sh tools/work-session.sh --within-turn finish README.md solo como preview.
   Responde S25_REMOTE_OK solo si el HEAD es el esperado, receive devolvió BUSY
   y el preview fue OK con index_unchanged=true.
   ```

3. Guardar el resultado de los comandos y el ID mostrado por Información de la
   conversación. Después cerrar y volver a abrir la app y comparar ese ID.
   **Recargar historial** en esa pantalla solicita contenido completo al servidor.
   Conservar para diagnóstico un hilo cuyo mensaje no produce un turno; evitar
   reenviarlo por una respuesta ambigua. La vista guardada por sí sola no acredita
   historial fresco: la aceptación instrumentada debe distinguir respuesta del servidor y
   caché del cliente. SSH, túnel, hello, turno e historial son capas separadas.

Este incremento deja código/documentación locales revisados; no publica commits
por el hecho de ejecutar las comprobaciones. Hasta una recepción explícita, el
HEAD esperado del teléfono es el registrado en el informe 15, no el working tree WSL.


## Entrada atómica del polling H3

`atomic_project_poll.py --repo <checkout>` adquiere el lock antes de leer la
política y el estado. Solo obtiene referencias; no aplica, repara recuperación
ni aprueba políticas. BUSY no lee ni sobrescribe al escritor. Una recuperación
real sigue bloqueada y requiere revisión explícita.

El incremento evita que el supervisor clasifique como abandonado un snapshot
`running` del escritor que acaba de terminar. La reproducción en un fixture Git
conservó HEAD/índice/política: la entrada anterior devolvió
`UNCLEAN_SESSION_REVIEW_REQUIRED`; la nueva devolvió fetch-only correcto.
`updated_keeper_source` prepara únicamente la sustitución de esa llamada en el
worker existente y rechaza código desconocido. No instala ni inicia nada.

La instalación revisada conserva respaldo del worker, coloca el helper a su
lado y verifica hashes. No cambia intervalo, servicio, puertos ni protecciones
Android. La entrada del supervisor se conserva. El siguiente incremento corrige también
la CLI general, con dos regresiones y una transición revisada de sus controles.
No se reaprobará una política para limpiar la incidencia.
