# Traspaso — Drive y app Android del S25

**Cierre verificado el 2026-10-22:** MESTRY activa y asignada; etiqueta, navegador
y control de carpetas comprobados en el S25, con conversaciones conservadas.
[Resultado y límites](validation/mestry-s25-drive-ui-20261021T200418Z/result.json).

**Actualización vigente 2026-10-22 — Drive y controles de conversación.**
MESTRY Piloto **0.2.0-mestry-pilot7 / 10007** actualiza la misma app/firma sin borrar
datos ni emparejar otra vez. Incluye navegación Drive, asignación dentro de cada
proyecto, activación local de carpetas, actividad contraíble bajo cada mensaje y
Ajustes como botón simple con Conexión dentro. El usuario pidió después modo
YOLO: el bridge fija y verifica **never / dangerFullAccess**.

**Raíz elegida: MESTRY**, ID `DRIVE_FOLDER_02_EXAMPLE`.
El usuario completó Google Picker con el cliente existente y solo `drive.file`.
Otra conexión al S23 comprobó renovación HTTPS, cuenta/cliente/scope y carpeta
fuera de la papelera. Token anterior privado, modo 600. MESTRY está activa y
asignada al proyecto sintético; no muestra documentos autorizados todavía. El
usuario organizará el directorio. No se restauró el antiguo Review/Horus ni sus
pruebas, que están en papelera heredada. La asignación nueva permite consulta;
no mueve/sincroniza el proyecto ni redirige el publicador anterior. Desactivar en
la app cambia su lista local, no los permisos OAuth. Abrir la carpeta no concede
automáticamente acceso a todos los archivos existentes.

[Entrega y evidencias vigentes](validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md),
[guía Android](../tools/s25-codex-client/README.md),
[prueba física pendiente](../tools/s25-codex-client/PC_OFF_TEST.md).
Las actualizaciones siguientes conservan la cronología; cuando describan estados
anteriores, prevalece este encabezado y su evidencia.

**OAuth de producción PASS, 2026-10-21:** el usuario confirmó **En producción** y el uso de inicio/privacidad propuestos, sin condiciones. Tras detectar 404 y recibir aprobación expresa, se publicó el sitio GitHub Pages con cuatro archivos estáticos; HTTPS y contenido exacto verificados. Completó el nuevo consentimiento y otra conexión al S23 comprobó refresh token nuevo, renovación real y ambas revisiones privadas intactas. Se conservan copias `600`, cliente, solo `drive.file`, claves SSH y puertos; callback cerrado. [Resultado y límites](validation/mestry-oauth-production-confirmed-20261021T055110Z/result.json), [guía operativa](../tools/s23-publisher-branding/README.md). Continuidad de más de siete días todavía no ensayada.

**Publicación histórica y cierre OAuth de producción PASS.** El cliente del perfil SSH Horus está instalado, la clave exclusiva rechazó comandos/reenvíos ajenos y las dos claves previas permanecen. Se publicaron dos revisiones privadas desde S25/Horus, con reintento sin duplicado, SHA-256 de ambas descargado íntegramente por otra conexión y primera revisión conservada después de la segunda. El conector corroboró metadata y el usuario confirmó lectura de ambas desde S25. En ese ensayo `Horus` estaba dentro de Review; hoy ese destino está en la papelera por decisión del usuario, como se indica arriba. OAuth `drive.file`, cuenta y refresh nativo comprobados otra vez después del consentimiento de producción. [Uso y destino actuales](HORUS_DRIVE_PUBLISH.md), [resultado histórico](validation/mestry-horus-drive-live-20261021T040010Z/result.json). Callback 127.0.0.1:53682 cerrado. PC apagado y continuidad prolongada siguen pendientes.

## Historial de preparación anterior al piloto real

Los párrafos siguientes describen etapas ya superadas; los pendientes operativos vigentes están indicados arriba.

**Consentimiento pendiente por audiencia de prueba:** el primer login devolvió `403 access_denied` con el mensaje de que Mestry solo permite verificadores aprobados. Se leyó únicamente el ID de proyecto del JSON real: `mestry-s23-publisher`. Se pidió añadir `owner@example.invalid` en Google Auth Platform → Público → Usuarios de prueba de ese proyecto, guardar y repetir el helper con esa misma cuenta; cancelar antes el intento anterior si sigue esperando. No recrear cliente ni ampliar scopes. La lista real de testers/cuenta seleccionada no se inspeccionó; el error todavía no está resuelto. Callback ya aprobado para este login. [Diagnóstico y fuente oficial](validation/mestry-horus-oauth-client-20261021T035330Z/testing-audience-error.json).

**Actualización OAuth:** cliente de escritorio real validado e importado en el almacenamiento privado de Termux; ninguna credencial se imprimió. Sin token todavía. El usuario autorizó expresamente el callback WSL temporal 127.0.0.1:53682 por hasta 180 segundos. Se solicitó ejecutar el [comando local preparado](validation/mestry-horus-oauth-client-20261021T035330Z/AUTHORIZE_IN_WSL.sh) en su propia terminal, sin logger, y completar el navegador del PC. Esperar resultado o comprobar que la importación final del token se completó antes de usar Drive. No pedir otra vez aprobar ese mismo callback. [Evidencia y estado](validation/mestry-horus-oauth-client-20261021T035330Z/result.json). Los párrafos de preparación siguientes son anteriores a este avance; siguen pendientes la clave restringida y la publicación desde S23.

**Historial de preparación — publicador autónomo Horus:** [código y guía de configuración OAuth](../tools/horus_publish/README.md), [evidencia de preparación](validation/mestry-horus-publish-20261021T033650Z/manifest.json). El usuario respondió que no tiene cliente OAuth y que hay que prepararlo; se le dieron los pasos Google Cloud, cuenta propia, audiencia externa, cliente de escritorio y solo `drive.file`. Código nativo Termux copiado e inactivo, biblioteca oficial de autorización preparada en un venv WSL; 26 tests WSL / 25 S23 correctos, un test solo WSL omitido en S23. No hay OAuth S23, clave Horus→Termux registrada, carpeta nueva del publicador ni subida real S23. No atribuir esas capacidades a los cuatro uploads anteriores del conector. El callback **temporal WSL 127.0.0.1:53682** aún requiere aprobación por la regla expresa de puertos; no ejecutarlo con el logger ni guardar sus URLs/códigos en evidencia.

El piloto actual guarda OAuth en **Termux UID Android 10348**, mientras Codex se ejecuta en **Horus UID 10350**, corroborados en vivo. La prohibición R2 de OAuth junto a Codex/Termux se formuló cuando Codex residiría en Termux; aquí se mantiene el requisito real de UIDs distintos. PRoot no es la frontera. No ejecutar Codex en Termux ni copiar secretos a Horus. La entrega de bytes se prepara por una clave nueva de comando forzado y loopback al **8023 ya existente**, preservando las dos claves WSL/S25. Se probará esa capacidad antes de declararla funcional.

Con `drive.file`, el nuevo cliente no ve automáticamente Review creada por el conector. Preparará su propia carpeta privada `Horus` con ID reservado y luego se moverá esa carpeta dentro de la Review existente como bootstrap, sin ampliar permisos al Drive completo. El receptor fija cuenta y destino, permite un solo documento sintético de hasta 64 KiB y crea archivos nuevos por revisión; no hace sincronización bidireccional ni comentarios. Las credenciales iniciales se transfieren privadamente por SSH desde un helper que ejecutará el usuario; no guarda el token en WSL. Runtime de publicación/renovación en S23, todavía sin evidencia de uso real o PC apagado.

**Actualización posterior: esta cuenta continúa el trabajo.** El usuario aclaró la cuenta objetivo y reautorizó la conexión. Se confirmó la identidad mediante el perfil del conector, se creó la carpeta privada [MESTRY/Review](https://drive.google.com/drive/folders/DRIVE_FOLDER_03_EXAMPLE) y se subieron cuatro fixtures `.md`, descargados después con bytes/SHA-256 idénticos. La metadata de permisos de carpetas y archivos solo muestra al propietario. El bloqueo de escritura descrito más abajo es histórico; **no recrear carpetas ni repetir publicaciones**. [Resultado, IDs y límites](validation/mestry-drive-review-20261021T020632Z/result.json), [manifest](validation/mestry-drive-review-20261021T020632Z/manifest.json). Lectura/edición desde S25 confirmadas mediante una edición recuperada; app utilizada sin identificar y comentarios retirados como requisito del piloto por preferencia del usuario; no se implementó todavía un publicador autónomo S23 ni el cliente Android. La preferencia por app Android sigue vigente.

Preparado el 2026-10-21 UTC, después de EXP07. Este documento registra el estado del traspaso; los servicios, IP, versiones y permisos deben revalidarse antes de cambiarlos. Continuar en `/home/developer/proyectos/mestry`, sin reiniciar el trabajo desde cero.

## Encargo y decisiones actuales del usuario

El usuario pidió: «por ahora se ve todo ok, me gustaria continuar con la integracion con drive y la interfaz que usaremos en el s25».

Respondió expresamente:

- **Drive:** «Crear MESTRY/Review con documentos de prueba».
- **Interfaz de proyectos y conversaciones Codex en S25:** «App Android».
- Al encontrar el bloqueo OAuth de esta cuenta: «En esta cuenta de codex no, dame un prompt para darselo a otra y que ella continue».

Hay autorización para avanzar con esta preparación e integración acotada. No volver a preguntar por esas dos preferencias ni tratar las restricciones históricas de investigación de R2 como una cancelación de las autorizaciones posteriores. Los documentos personales, un corpus completo, permisos globales, nuevos proveedores o gastos adicionales no están seleccionados por este encargo.

## Base que ya funciona

- S23 Ultra **SM-S918B**, Android OEM, Horus oficial **1.0.4/code 5**, commit `2f8f8a2faebd3d0fbd11dd83340bdcfbac437369`.
- Termux SSH migrado y verificado en **8023**, con sus dos claves WSL/S25 conservadas. Alias WSL `mestry-s23`, usuario `u0_a348`; última IP registrada `192.0.2.15`, dinámica. Termux:Boot y helper actualizados; reversión temporizada cancelada y sin temporizador pendiente.
- Horus remoto fue verificado **enabled/running**, una clave S25, escucha exclusivamente **127.0.0.1:8022**. No aplicar la antigua reversión a 8022 mientras Horus lo usa.
- ConnectBot S25: perfil principal **MESTRY Horus**, destino `horus@127.0.0.1:8022`, clave `mestry-s25`, **ProxyJump = MESTRY S23 8023**. Conservar ese perfil de salto; no hace falta abrir una consola Termux aparte. El perfil Termux 8022 es antiguo; «MESTRY Horus test» fue para comprobaciones.
- Huella Termux: `SHA256:CONFIGURE_LOCAL_FINGERPRINT`. Huella Horus: `SHA256:CONFIGURE_LOCAL_FINGERPRINT`. No desactivar la comprobación de host.
- Perfil SSH Horus: usuario `horus`, `/home/horus`, Alpine **3.24.0**, `aarch64`. Codex CLI **0.163.0** instalado por su launcher oficial y login confirmado por el usuario.
- El S25 hizo crear/modificar `S25_REMOTE_TEST.txt` en `/workspace/projects/mestry-horus-smoke`. Otra conexión S25 leyó el archivo y verificó su hash, conservando los tres fixtures anteriores de EXP06.
- El usuario confirmó que la conversación reaparece después del ensayo solicitado de reconexión y `codex resume --last`. Eso no prueba supervivencia del proceso original ni compartir historial con el harness de la app.
- Los 15 minutos son **bloqueo de la interfaz local tras estar en segundo plano**. El usuario aclaró «Solo vuelve a pedir contraseña en Horus del S23». El código no detiene SSH ni sesiones por ese bloqueo y no ofrece ajuste para desactivarlo. No modificarlo como requisito de Drive o de la app S25.
- **Pendientes reales:** PC físicamente apagado, reinicio/Boot real, reposo prolongado, estabilidad 24/7 y continuidad del proceso ante desconexión. No afirmar que pasaron ni bloquear toda preparación independiente hasta medirlos.

La aceptación de `--sandbox danger-full-access` es específica de Horus, ya concedida por el usuario. La petición posterior de modo YOLO autoriza `never` en este piloto; no extrapolar ambas excepciones a otras rutas. El perfil SSH y `harness_codex` son distintos; no copiar credenciales/historiales para aparentar continuidad.

## Drive: estado exacto del traspaso

Se usó la habilidad Google Drive y el conector disponible en esta cuenta:

1. Búsquedas de carpetas `MESTRY` y `Jarvis`, solo metadatos: sin resultados en esas búsquedas.
2. Tras la autorización del usuario, se intentó crear `MESTRY` en la raíz de Drive.
3. Google respondió **`ACCESS_TOKEN_SCOPE_INSUFFICIENT` / `PERMISSION_DENIED`**, indicando reautenticación. **No se creó ninguna carpeta ni se subió ningún archivo.** No hay IDs/enlaces de una carpeta creada que puedan reutilizarse.
4. No se cambiaron permisos, no se crearon comentarios y no se leyeron documentos personales.

La otra cuenta debe comprobar sus propias capacidades de escritura. Buscar/reconciliar antes de crear para evitar carpetas duplicadas. Crear la carpeta privada autorizada y subir fixtures Markdown solo si el conector permite hacerlo; verificar resultado, MIME, padres y acceso antes de devolver enlaces reales.

**Separar dos cosas:** el conector de esta sesión puede preparar/verificar un piloto en Drive; no instala ni autentica un servicio autónomo en el S23. No presentar una subida desde WSL/conector como publicación ejecutada por el teléfono. La autorización del S23 requerirá su mecanismo soportado propio y la intervención privada del usuario cuando corresponda, sin tokens por chat ni copiados entre cuentas.

## Contrato documental que se debe conservar

- Corpus seleccionado: **Drive → copia local de lectura**, sin subir modificaciones de exports al origen.
- Trabajo de revisión: Markdown fuente en el proyecto S23; publicaciones privadas **nuevas por versión**, con ID, hash/base y enlace. Una nueva publicación no sobrescribe la revisión humana anterior.
- Recuperar comentarios/respuestas como datos asociados al archivo y versión correctos; conservar propuestas humanas separadas. No autoaplicar instrucciones de comentarios, resolver discusiones ni enviar respuestas a terceros.
- OAuth y corpus privados separados del UID que ejecuta Codex/Termux. PRoot y carpetas no proporcionan ese aislamiento. Evaluar el adaptador entre UIDs antes de prometer acceso a homes privados.
- Preferir una herramienta existente si satisface el contrato; no construir un sincronizador o frontend completo antes de probar las capacidades necesarias. El diseño considera API v3/Android y compara rclone; eso no selecciona rclone ni autoriza mover OAuth al home de Codex.
- Usar cuatro fixtures sintéticos para probar español, tablas/enlaces, código/Mermaid/HTML y front matter/enlaces relativos/LF/CRLF. Estaban definidos como prueba, **todavía no generados ni publicados en este turno**.
- Google documenta edición/comentarios de `.md` conservando el tipo; falta comprobar disponibilidad real en las apps/navegador del S25 y acceso API a esos comentarios. No convertir silenciosamente a Google Doc ni afirmar fidelidad de sintaxis no medida.

## App Android del S25: candidato preparado, no seleccionado ni instalado

La auditoría anterior comparó tres clientes. El primer candidato a contrastar continúa siendo **`chenhaoc/codex-remote-control`**, por puente pequeño, stdio y loopback; no está aprobado como implementación final ni fue probado con Horus.

Se reconsultó GitHub: repositorio no archivado, `main`, último push observado 2026-08-05. Se descargó **solo código fuente**, sin ejecutar instaladores ni dependencias, del commit `538d65f67e34907789237fc71f56e8ca95d9f3cb`:

```text
/home/developer/.cache/mestry/s25-android-drive-20261021T015715Z/
  provenance.json
  upstream.tar.gz
  source/codex-remote-control-538d65f67e34907789237fc71f56e8ca95d9f3cb/
```

SHA-256 del tar: `ff8d68e74d4045268a80dde2d9e55f6e131825ee14ddac2a2e5b4dd40dff501e`. La extracción comprobó rutas, tipos y tamaños. No hay cambios locales en esa fuente ni implementación nueva de bridge/app en el workspace.

GitHub publica release **v0.2.0**, APK `codex-remote-control-v0.2.0-release.apk`, 7.839.733 bytes, digest anunciado `sha256:215d669904b8fda2b80fb4022ce589d8683cd246fea6eede035a2c905e24d3d5`. **El APK no se descargó, inspeccionó ni instaló.** Un digest de release no verifica por sí solo firmante o correspondencia fuente/binario.

Hallazgos heredados y reobservados que condicionan el piloto:

- Bridge por defecto `127.0.0.1:8787`, backend mock si no se elige Codex; una UI conectada a mock no demuestra ejecución real.
- Backend Codex arranca `codex app-server --listen stdio://`.
- Token admitido en URL/query y preferencias/historial Android; no tratar ese almacenamiento como Keystore. Revisar también HTTP de archivos/imágenes, no solo WebSocket.
- Endpoints de archivos/directorios pueden salir de la raíz; autenticación no equivale a confinamiento por proyecto.
- Fallback de sandbox demasiado amplio cuando falta metadata; preservar la excepción Horus conscientemente, sin ampliaciones silenciosas ni `approvalPolicy=never` por defecto.
- Verificar idioma y comodidad de la UI, hilos/proyectos, aprobaciones, cancelación y reconexión. No declarar elegida la app solo porque compile.

Debe probarse primero la compatibilidad del app-server de la versión **real del S23**. El `codex --help` de WSL no demuestra esa compatibilidad. WSL no está emparejado con el SSH de Horus; la clave WSL autorizada en Termux no lo autoriza en Horus. El provider Horus permite status/log/pair/start/stop, no un exec remoto arbitrario. No añadir una clave ni capturar la contraseña para evitar esa frontera; preparar un diagnóstico breve que el usuario pueda ejecutar desde la sesión S25 si hace falta.

Entorno observado para una eventual compilación, a revalidar: Node/npm WSL disponibles; java/javac/gradle/sdkmanager no en PATH Linux. Hay Android SDK Windows y JBR de Android Studio bajo `C:\Users\developer\AppData\Local\Android\Sdk` y `C:\Program Files\Android\Android Studio\jbr`. La caché Gradle Linux existe. No se instalaron herramientas de compilación. El Gradle upstream requiere configuración de firma y usa `git rev-parse`; la copia descargada es un archivo de fuentes, no un checkout Git.

La última consulta `adb.exe devices -l` observó un único **S23 SM-S918B**, transporte 1; ningún S25 conectado por USB. El comando reinició automáticamente el servidor ADB del PC por incompatibilidad de versión 40/41, y volvió a listar el S23 autorizado. No fue un reinicio del teléfono ni un cambio de su configuración.

## Límites operativos y forma de continuar

- No repetir instalaciones Debian, X11, Horus, Codex o migración SSH que ya funcionan.
- El usuario pidió aprobar **cualquier cambio de puertos**. Preparar primero la propuesta concreta y comprobable si el cliente necesita un listener/túnel nuevo; no abrirlo ni cambiar 8022/8023 antes de esa aprobación. No se abrió ningún puerto en este incremento.
- Conservar claves, confianza estricta, credenciales, proyectos existentes y protecciones Android. Sin root, flash, reinicio no anunciado, `horus tune`, deshabilitar más apps ni publicar servicios/túneles en Internet.
- No ejecutar tareas pagadas de modelo ni introducir proyectos/documentos personales por inferencia de este piloto. Reutilizar fixtures y autenticación privada del usuario.
- Distinguir permisos del conector, OAuth del S23, compilación, pruebas offline, ejecución en dispositivo, experiencia humana S25 y funcionamiento con PC apagado.
- Avanzar autónomamente en trabajo reversible autorizado. Pedir datos o aprobación solo cuando falten de verdad, con el cambio ya preparado para revisión; no volver a pedir permiso para las preferencias confirmadas arriba.

## Lecturas y evidencia local

Leer primero este traspaso y el estado reciente; las restricciones de R2 anteriores a EXP06/EXP07 son históricas cuando contradicen autorizaciones posteriores.

1. [Acceso S25 y estado vigente](S25_REMOTE_ACCESS.md).
2. [Drive, revisión y comentarios](GOOGLE_DRIVE_RAG.md), [auditoría de clientes](FRONTEND_AUDIT.md).
3. [Contratos de arquitectura](ARCHITECTURE.md), [validación V12/V13](VALIDATION_PLAN.md), [decisiones históricas y posteriores](DECISIONS.md).
4. [Arquitectura documental congelada](../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md); respetar sus principios congelados, sin interpretar propuestas técnicas como código ya construido.
5. [Tarea remota y conversación recuperada](validation/mestry-horus-s25-task-20261020T235104Z/result.json).
6. [Bloqueo local de 15 minutos y estado puntual](validation/mestry-horus-ui-lock-20261021T010002Z/result.json).
7. [Cronología completa](INSTALLATION_LOG.md); `tools/mestry_session.py` permite conservar futuras sondas con comandos, salidas y hashes, sin reutilizar nombres.

Fuentes oficiales verificadas en la preparación: [Markdown de Google](https://support.google.com/docs/answer/18289341), [Drive comments.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/comments/list), [Codex App Server](https://learn.chatgpt.com/docs/app-server). Usar las habilidades disponibles de Drive y OpenAI Docs para las partes correspondientes; revalidar lo que pueda haber cambiado.
