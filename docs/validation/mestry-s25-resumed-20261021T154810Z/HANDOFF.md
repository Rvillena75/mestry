# Estado actual de MESTRY S25

Continuación del 2026-10-21. **Piloto de app, recuperación y llamada al publicador
PASS.** Este documento reemplaza los pendientes del traspaso de las 08:21 UTC;
los archivos anteriores se conservan como evidencia histórica, sin reescribirlos.

## Uso actual

- S23: Horus y su servicio remoto activos; bridge `127.0.0.1:8787`.
- S25: ConnectBot **Mestry s23 8023** conectado, con reenvío local
  **MESTRY App**, `127.0.0.1:18787 → S23 127.0.0.1:8787`.
- Abrir **MESTRY Piloto**. Reconexión automática activada desde Ajustes.
  Para detener una tarea, **mantener pulsado Enviar**; la insignia no es otro botón.
- Proyecto permitido: `/workspace/projects/mestry-horus-smoke`. El usuario eligió
  pruebas sintéticas; todavía no eligió un proyecto/documento real.
- Publicador existente: `/home/horus/.local/bin/mestry-publish S23_PUBLISH_TEST.md`.
  Solo admite ese Markdown; no ampliar el allowlist ni publicar otros archivos
  del proyecto automáticamente.

## Aplicación instalada y fuentes

- S25 `SM-S938B`, SDK36, arm64-v8a; último transporte ADB `1`, a redescubrir.
- Paquete `com.haochen.codexremote.mestrypilot`, activity
  `com.haochen.codexremote.MainActivity`.
- Versión **0.2.0-mestry-pilot4 / 10004**, debug personal. Firma igual a la
  anterior; se actualizó con `install -r`, sin borrar datos ni repetir pair.
- APK: `C:\Users\developer\Downloads\MESTRY-Piloto-20261021-r4.apk`.
  SHA-256 `99e0f3efb768bc6fdc58fa8fb4d19b90c85b5355d3606c78a9dbdd4bdedc6ac8`.
  Copia Linux y manifest en `apk-result.json`.
- Fuente modificada:
  `/home/developer/.cache/mestry/s25-android-client-20261021T063514Z/source/codex-remote-control-538d65f67e34907789237fc71f56e8ca95d9f3cb`.
- Base GPL3 `chenhaoc/codex-remote-control`, commit
  `538d65f67e34907789237fc71f56e8ca95d9f3cb`.
- Parche acumulado y pins: `tools/s25-codex-client/mestry-pilot1.patch` y
  `source-pins.json`. Parche actual SHA
  `507cf42f3c46381c4a85343ae27821198ce971a32eedf6cf1f4fe21b3242a911`.
  Se reprodujeron 54 archivos desde el tar fijado y wrapper oficial ya verificado,
  sin red; no se modificaron tipos generados.
- Los cambios nuevos son Android: lector de metadatos, traducciones, etiquetas
  para evitar cortes y fechas en la zona del teléfono. Node, transporte, ACL y
  publicador desplegados se conservaron. No reinstalar el bridge ni generar otra
  clave de conexión por este cambio.

## Pruebas completadas

1. Se heredó y revisó la confirmación nativa de interrupción del otro hilo:
   `../mestry-s25-continuation-20261021T153936Z/interruption-result.json`.
   Una lectura stdio nueva al final vuelve a encontrar el turno
   `01a15db6-b876-7c81-a93d-7fe646daee6a` con estado `interrupted`.
2. El error «null» se reprodujo sobre el APK anterior: fallaban cinco de seis
   casos sintéticos. Se corrigió `JSONObject.NULL` sin eliminar un título cuyo
   texto literal sea «null». Seis casos pasan sobre el parser del APK Android;
   `metadata-before.json`, `metadata-after.json`, `metadata-r3.json`.
   En r4 solo cambiaron dos etiquetas de SessionComponents y la versión de build;
   el parser/transportes/caché conservan los bytes fuente de r3.
3. `compileDebugKotlin` y `assembleDebug` pasan; firma, paquete, versión y ausencia
   de permiso para instalar otros APK verificados. Se revisaron menú, ajustes,
   información de conversación, pie de chat y fechas en el S25.
4. Reconexión sin caché: cerrar solo el proceso de la app; apartar privadamente
   el archivo de caché de la conversación, conservando el índice y las claves;
   abrir un proceso nuevo. Se observó pantalla sin mensajes, conexión automática
   y descarga del historial del **mismo ID**. La copia temporal se retiró después
   del éxito. Ver `cache-recovery.json` y las capturas asociadas.
5. Sonda S25 actual: loopback IPv4 ocupado, wildcard IPv6 libre, nueve direcciones
   ajenas a loopback libres, identidad del bridge correcta y HTTP/WS sin clave
   válida rechazados. `loopback-current.json`. La sonda usa bind sin listen;
   el DEX temporal se eliminó. No inferir el bind de `ss`, cuyo netlink se deniega.
6. App → Codex/Horus → cliente SSH limitado → publicador Termux → Drive:
   primer intento detenido por **DRIVE_HTTP_500**. El diagnóstico nativo posterior
   pudo leer cuenta, carpeta, metadata y bytes de la revisión 2 con hash correcto.
   Un reintento idéntico desde la app devolvió **PUBLISHED_VERIFIED**.
7. Comprobación independiente: `thread/read` mediante un proceso stdio distinto
   encontró el recibo en **commandExecution.aggregatedOutput**, no solo en la
   respuesta del modelo. Turno `01a15f49-43a1-7eb2-84ce-f8e083cf1d82`, revisión 2,
   ID `DRIVE_ID_09_EXAMPLE`, hash
   `ada9d1e265088e8fae3dfe57e9a229e8e31ebd75ff480a321e70eaa82d8f20a7`.
   El journal nativo abierto solo en lectura conserva las dos filas anteriores,
   sin versiones nuevas: `publisher-before.json`, `publisher-after.json`.
8. Lectura independiente final del proyecto: PASS, seis archivos previos
   intactos y el archivo de la primera prueba de app como único añadido a aquel
   baseline. No se añadieron archivos en este incremento. Captura
   `horus-final-project-readback.png`.

Sesión de app: **01a15dae-7f34-7a22-926e-594a53f899cd**, `gpt-6.1-sol`, esfuerzo
`low`, cuenta ChatGPT existente, `on-request` y `dangerFullAccess` corroborados.
No se creó una API key. Los diagnósticos no iniciaron inferencia ni imprimieron
credenciales o conversaciones crudas. Dos solicitudes reales desde la app
corresponden al intento de Drive y al reintento; ambas fueron de verificación.

El fixture `S25_APP_TEST_20261021T085207Z.txt` conserva:

```text
MESTRY_S25_APP_OK
estado=creado-desde-app
```

SHA-256 `26a5c89377b286ad37c89ac76b6a9e30ab4b7d319f9fd2d616086e03e8ae30ec`.
No confundir pruebas históricas de PC (51 Node +3 política +3 helpers) con estos
ensayos reales. No se repitieron porque no cambió Node/publicador.

## Continuación y límites

- Siguiente ensayo: [PC_OFF_TEST.md](../../../tools/s25-codex-client/PC_OFF_TEST.md).
  Necesita PC físicamente apagado, un marcador nuevo desde S25 y lectura por
  otra sesión; después 16–20 minutos de reposo S23. **No ejecutado todavía.**
- Boot real, estabilidad 24/7 y reconexión tras muerte del bridge no se validaron.
  No hay autostart nuevo. No desactivar el bloqueo local Horus de 15 minutos.
- No hubo una solicitud real de aprobación en este incremento; no presentar las
  aprobaciones de Android como verificadas por una tarea que no las necesitó.
- El servidor conserva el UID y acceso completo de Horus aceptados; ACL de app
  no equivale a sandbox del SO. OAuth permanece en Termux, otro UID Android.
- Conservar Termux8023, HorusSSH127.0.0.1:8022, bridge8787 y túnel18787. Nuevos
  puertos requieren aprobación. Callback OAuth53682 permanece sin utilizar.
- WSL accede a Termux, **no al home privado de Horus**. Usar ConnectBot del S25
  para diagnósticos Horus, sin añadir la clave WSL ni copiar credenciales.
- ADB Windows:
  `/mnt/c/Users/developer/AppData/Local/Android/Sdk/platform-tools/adb.exe`.
  Identificar modelo/transporte antes de mutar; launcher ConnectBot puede volver
  a la consola actual, no siempre al listado. Imágenes 1440×3120.
- Build: script Windows existente `BUILD_PRIVATE_PILOT.ps1` en
  `C:\Users\developer\AppData\Local\mestry-build\s25-pilot-20261021T063514Z`.
  JBR21, SDK/build tools36.0.0, Gradle8.13. Sin bypass de PowerShell; no reparar
  el SDK35 incompleto. Leer AGENTS.md de upstream antes de editar.
- La prueba de refresh de más de siete días corresponde desde
  **2026-10-29T06:08Z**. No hay una tarea programada ni garantía de tokens perpetuos.
- No publicar repositorios/APK/evidencia, no iniciar nuevos servicios ni cambiar
  scopes/clientes OAuth. Workspace sin Git; no se hicieron commits o pushes.
- `horus_read_thread.py` ahora busca el turno de interrupción por su prompt,
  aunque existan turnos posteriores, y extrae recibos de publicaciones solo de
  salida de herramientas. Es un diagnóstico del fixture fijo, no un lector general.

La app queda conectada a la conversación de prueba. Para otro proyecto real,
pedir la selección del usuario antes de ampliar rutas o documentos publicables.
