# Piloto Android S25 → Codex en Horus

**Incremento VPN del 2026-10-22, en validación:** Android piloto8 instalado, misma
firma y datos. [Estado del acceso privado](../s23-remote-access/README.md) y
[evidencia actual](../../docs/validation/mestry-s23-remote-access-20261022T034500Z/HANDOFF.md).

**Entrega Drive anterior, piloto7:** app y bridge actualizados; MESTRY activa y
asignada, etiqueta y navegador comprobados en el S25. Conversaciones conservadas.
[Resultado y límites](../../docs/validation/mestry-s25-drive-ui-20261021T200418Z/result.json),
[entrega](../../docs/validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md).

Piloto del 2026-10-21. El usuario autorizó continuar con una app Android,
aprobó las escuchas de [PORT_PLAN.md](PORT_PLAN.md) y eligió contenido sintético
para la primera prueba. La tarea, recuperación del historial e invocación del
publicador desde el APK ya pasaron; la disponibilidad con el PC apagado necesita
un ensayo físico separado.

## Estado comprobado

- **APK instalado: 0.2.0-mestry-pilot8 / 10008**, mismo applicationId
  `com.haochen.codexremote.mestrypilot` y firma personal. Actualización sin borrar
  datos ni renovar emparejamiento; `compileDebugKotlin` y `assembleDebug` pasan.
  Fuente reproducible: 68 archivos modificados, huellas en `source-pins.json`.
- **Drive en la app:** selector, asignación por proyecto dentro de su tarjeta,
  navegación de subcarpetas, paginación y vista previa de texto/Markdown/Docs.
  La raíz **MESTRY** quedó autorizada con Google Picker y asignada a
  `/workspace/projects/mestry-horus-smoke`. La lectura real desde el S23 y el
  navegador Android pasan; actualmente no hay documentos autorizados visibles.
  Subcarpetas/vistas previas se comprobaron con fixtures, todavía sin documentos
  reales en la nueva raíz. No se crean ni restauran archivos para rellenarla.
- **Carpetas** permite activar/desactivar las raíces ya autorizadas. Es una lista
  de uso local, separada del permiso OAuth de Google. Pegar un ID no concede
  permisos; desactivar no elimina archivos ni revoca Google. Solo `drive.file`;
  autorizar una carpeta no garantiza acceso a todos sus descendientes.
- La asignación Drive es para consultar documentos: **no mueve ni sincroniza el
  workspace y no cambia el destino del publicador anterior**. Su antigua carpeta
  Horus está en la papelera por decisión del usuario; no se restauró ni se
  redirigió automáticamente el publicador. El usuario preparará su directorio.
- **Actividad desplegable bajo cada mensaje del usuario:** comentarios,
  razonamiento y acciones disponibles en app-server, con comandos/salidas y
  cambios de archivos. La respuesta final queda fuera. No se inventan avisos o
  razonamiento que el servidor no entregue. El historial extendido se solicita
  al iniciar y reanudar; el contenido ya omitido por versiones antiguas no se
  puede reconstruir de forma garantizada.
- **YOLO por petición expresa:** `approvalPolicy=never` y el acceso completo de
  Horus ya autorizado. El servidor comprueba ambas políticas reales antes de
  aceptar turnos; no convierte campos ausentes en éxito. El selector fijo de
  acceso desaparece. Conexión se encuentra dentro de Ajustes; el menú lateral
  conserva un botón simple de Ajustes y Nueva conversación.
- Se corrigió además el envío de `null` en booleanos opcionales al crear o
  reanudar hilos: Codex 0.163 exige omitir los valores ausentes. Se conserva
  un `false` explícito y se verifica el caso contra un servidor de prueba estricto.
- El bridge actualizado preservó emparejamiento/historial y la versión anterior
  para recuperación. OAuth sigue exclusivamente en Termux, separado de Horus.
  El S23 renovó el token por HTTPS con el mismo cliente y solo `drive.file` tras
  elegir MESTRY; la copia anterior está privada, modo 600.
- **Verificación:** 55 tests Node, 3 de política, 4 helpers, 46 del broker
  nativo y 8 del helper Picker pasan sin inferencia. Los 20 casos del navegador
  también pasan sobre el código instalado en S23. En el APK: 8 casos de actividad
  y 6 de metadata; firma/compilación y controles visuales en S25. El túnel solo
  loopback y los rechazos HTTP/WS sin clave válida se comprobaron de nuevo.
- Las tareas, interrupción y recuperación anteriores siguen registradas en su
  evidencia histórica; no se inició ningún turno de modelo en este incremento.
  PC apagado, reposo prolongado, Boot real y renovación tras más de siete días
  conservan sus pruebas físicas pendientes.

[Entrega y evidencia actuales](../../docs/validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md).
[Entrega anterior r4](../../docs/validation/mestry-s25-resumed-20261021T154810Z/HANDOFF.md).
Fuentes aisladas y APK en `~/.cache/mestry/s25-android-client-20261021T063514Z/`.

## Base y cambios acotados

Se adapta [chenhaoc/codex-remote-control](https://github.com/chenhaoc/codex-remote-control)
en el commit `538d65f67e34907789237fc71f56e8ca95d9f3cb`, licencia GPL-3.0-only.
Se conserva Node ESM, Kotlin/Compose y OkHttp. No se crea otra interfaz ni se
modifica el sistema MESTRY fuera del piloto. El parche y las huellas están en
[mestry-pilot1.patch](mestry-pilot1.patch) y [source-pins.json](source-pins.json).

El bridge del teléfono tiene una sola entrada y backend Codex real. El bundle
de instalación excluye el launcher legacy y el backend simulado. Conserva la
cuenta ChatGPT que ya tiene Horus; no necesita una API key nueva ni importa
credenciales de Codex del PC. Se añade `initialized` después de la respuesta a
`initialize`, según el [protocolo oficial](https://learn.chatgpt.com/docs/app-server#initialization).

La clave de conexión es distinta de OAuth y del login de Codex. La app genera
32 bytes aleatorios, los guarda con Android Keystore/AES-GCM y los envía solo por
`X-Bridge-Token`. La URL es `ws://127.0.0.1:18787/`, sin secretos. El bridge exige
clave incluso en loopback y antes del upgrade WebSocket, rechaza el token por
query y el origen de navegadores; limita tamaño, conexiones y tasa de mensajes.
La exportación/importación de respaldos upstream se desactiva porque incluía
credenciales. El manifiesto no permite backups ni instala otros APK.

Se permiten conversaciones del proyecto sintético
`/workspace/projects/mestry-horus-smoke`, listado, historial, texto, aprobaciones
e interrupción. Los endpoints HTTP de imágenes/descarga están desactivados; la
lectura de texto por WS valida rutas reales, hermanos y symlinks. Se rechazan
sesiones ajenas, IDs de aprobación inventados, RPC no catalogado, configuraciones
arbitrarias y objetivos autónomos. El selector muestra únicamente la raíz permitida.

Por petición posterior del usuario se fija `never` y el `danger-full-access` de
**Horus ya aceptado**; se verifica la política devuelta por
`thread/start`/`thread/resume` antes de permitir un turno. Un campo ausente no se
convierte en éxito. El fallback general upstream permanece `readOnly`; el modo
Horus es una excepción explícita, no una configuración trasladable a otros
proyectos. [Contrato oficial](https://learn.chatgpt.com/docs/app-server#approvals).

**La ACL de la app no es un sandbox del SO.** Codex sigue teniendo el UID y el
acceso completo de Horus autorizado previamente. La separación de OAuth se
mantiene entre los UIDs Android de Termux y Horus. Este piloto no valida el sandbox
Linux descartado ni evita que las herramientas de Codex accedan a otros archivos
del mismo UID. Los textos propios de la interfaz se tradujeron y revisaron en el
S25; contenido del modelo y valores técnicos del protocolo se conservan. La
lectura de metadatos ya distingue JSON null de un título escrito como texto.

## Reproducir sin tocar teléfonos

Preparar un directorio nuevo a partir del archivo fijado:

```sh
python3 -B tools/s25-codex-client/prepare_source.py \
  ~/.cache/mestry/s25-android-drive-20261021T015715Z/upstream.tar.gz \
  /ruta/privada/nueva/mestry-pilot-source
```

El script comprueba tar, parche y cada archivo modificado. Rechaza rutas/symlinks
de archivo y no sobrescribe un directorio existente. Sustituye el wrapper Gradle
por el de **8.13 oficial**, verificado por SHA-256, antes de ejecutarlo; el wrapper
del tar upstream no correspondía al checksum 8.13. La distribución también lleva
`distributionSha256Sum`, siguiendo la
[verificación oficial de Gradle](https://docs.gradle.org/8.13/userguide/gradle_wrapper.html#sec:verification).

En las fuentes preparadas:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

En este proyecto MESTRY:

```sh
node --test tools/s25-codex-client/pilot-policy.test.mjs
python3 -B -m unittest discover -s tools/s25-codex-client -p test_helpers.py -v
```

Las pruebas HTTP/WS usan puertos efímeros en `127.0.0.1`, ya autorizados para este
piloto. No enviar tareas a OpenAI para reproducirlas. La compilación usa el JBR
21/SDK Windows existente, Gradle 8.13, AGP 8.13.2 y Build Tools **36.0.0**. La
35.0.0 instalada está incompleta y se conserva sin modificar; la
[documentación AGP](https://developer.android.com/build/releases/agp-8-13-0-release-notes)
describe sus requisitos. `local.properties`, caches, firma y APK quedan fuera del
parche. No se publicaron repositorios ni artefactos externos.

## Uso de Drive y actualización existente

Abrir **Ajustes → Google Drive** o la etiqueta **Drive · MESTRY** dentro del
proyecto. **Cambiar carpeta** asigna otra raíz disponible; **Carpetas** activa o
desactiva raíces ya autorizadas. Los documentos externos se abren en Google Drive
mediante URLs construidas con IDs validados; una URL arbitraria del servidor no
se usa. No se siguen shortcuts para salir de la raíz seleccionada. El broker
nativo comprueba permisos, papelera y ascendencia en cada lectura.

`drive.state`, `drive.folder.enable`, `drive.assign`, `drive.list` y `drive.read`
son capacidades fijas autenticadas, sin inferencia ni comandos de shell
arbitrarios. Horus invoca `mestry-drive-v1` por la clave restringida existente;
las credenciales y el estado de selección viven en Termux. El usuario puede
retirar el permiso global desde las conexiones de su cuenta de Google. Para
conceder acceso a otra carpeta, usar el flujo Picker de
[la guía nativa](../horus_publish/README.md#navegador-drive-y-google-picker), con
el mismo cliente/scope y callback ya aprobado; no lanzar un login nuevo por abrir
la app ni copiar el token al S25/Horus.

El bridge se actualiza con `horus_upgrade.py`, no repitiendo el instalador
inicial. Verifica el manifest instalado y el entrante, rechaza turnos/aprobaciones
pendientes, conserva la versión anterior y revierte si no arranca. El incremento
actual transfirió solo código por la capacidad SSH ya existente, sin nueva
escucha. `pair` y generación de claves **no se repiten** durante una actualización.

## Instalación inicial y recuperación

La app y el bridge ya están instalados. Los pasos siguientes documentan el alta
inicial: **no repetir generación de clave, pair ni bootstrap en esta instalación**.
Para uso diario, conservar el servicio Horus y el perfil Termux 8023 de ConnectBot
con su reenvío; abrir MESTRY Piloto, con reconexión automática ya activada.

1. Identificar el S25 conectado por USB; verificar modelo/transporte antes de
   instalar el APK de huella registrada en `apk-result.json`. Revisar la pantalla
   real de la app. El S23 no es el destino del APK.
2. Ejecutar `stage_horus.py` en WSL con el bundle y un resultado privado para
   servir solo ese código, con timeout y reenvío inverso SSH en el **8787 ya
   aprobado**. Verifica `GatewayPorts no` y el puerto Termux 8023. No modifica SSH.
3. Desde el perfil SSH Horus del S25, descargar el bundle por loopback, verificar
   el SHA-256 esperado antes de extraer y ejecutar `horus_install.py`. El instalador
   verifica su manifest, conserva versiones y no abre puertos. Si encuentra una
   instalación existente, se detiene sin sobrescribir.
4. Cerrar y comprobar el cierre de la transferencia temporal. En la app generar
   una clave nueva. En la terminal Horus ejecutar `~/.local/bin/mestry-bridge pair`
   y pegarla en el ingreso oculto. **No pegarla en comandos, URLs, archivos de
   evidencia ni en el chat.** El portapapeles sensible se limpia si sigue teniendo
   esa clave al cumplirse dos minutos. No volver a generar la clave durante un
   emparejamiento válido; para rotación explícita, detener el bridge y usar
   `mestry-bridge pair --rotate` privadamente.
5. Arrancar con `~/.local/bin/mestry-bridge start`; comprobar `status`. El proceso
   usa una sesión propia para separarse de la terminal SSH. No es autostart y no
   garantiza que Android mantenga vivo el proceso: falta ensayarlo.
6. En el perfil Termux 8023 de ConnectBot añadir reenvío **Local** origen `18787`,
   destino `127.0.0.1:8787`. Verificar en el S25 que su bind es exclusivamente
   loopback antes de aceptarlo. Si no puede garantizarse, detenerse; no exponer LAN.
   Si Android deniega la consulta netlink de `ss`, [LoopbackProbe.java](LoopbackProbe.java)
   permite comprobarlo desde ADB sin root: hace reservas de dirección con `bind`
   **sin `listen`**, las cierra inmediatamente y prueba solo HTTP en loopback.
   Exige que loopback esté ocupado, todas las direcciones de interfaces ajenas a
   loopback estén libres y el wildcard IPv6 esté libre. También comprueba la
   identidad de `/healthz` y el rechazo `401` de HTTP/WS sin clave válida. No lee
   credenciales, no instala una app adicional ni cambia ajustes del teléfono.
7. Conectar la app a `ws://127.0.0.1:18787/`. Primero comprobar autenticación,
   proyecto/historial y políticas reales. Después una tarea sintética iniciada
   por el usuario, política `never` efectiva, interrupción y reconexión.

Para revertir: `~/.local/bin/mestry-bridge stop`, desactivar el reenvío y, si se
desea, desinstalar solo `com.haochen.codexremote.mestrypilot`. El controlador
identifica su proceso por PID, hora de inicio, comando y grupo antes de detenerlo;
no mata procesos ajenos ni toca 8022/8023, claves u OAuth. El token de conexión se
mantiene privado y no se incluye en backups de credenciales Google.

## Aceptaciones que siguen pendientes

La [prueba sin PC y tras reposo](PC_OFF_TEST.md) requiere apagar físicamente el
PC, generar un marcador nuevo desde el S25 y comprobarlo con otra conexión; leer
una caché o recuperar conversación no demuestra proceso vivo. Repetir tras más de
15 minutos con pantalla S23 apagada y registrar hora/duración. Conservar Wi-Fi
independiente del PC; Codex continúa usando Internet para la inferencia.

El usuario eligió el proyecto sintético para este piloto. Un proyecto/documento
real se seleccionará en una etapa posterior; no se amplía el publicador ni su
scope automáticamente. La prueba de
OAuth tras más de siete días queda para **2026-10-29 después de 06:08 UTC** (03:08
Chile); no se programó una tarea automática ni se declara autenticación permanente.
Revocación, límites de tokens y otros mecanismos de Google pueden exigir una
reautorización privada aunque la app esté en producción.
