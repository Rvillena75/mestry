# Document Service: sincronización, revisión Markdown y RAG

**Publicación real validada — 2026-10-21 UTC:** perfil SSH Horus → clave exclusiva limitada → SSH Termux existente 8023 → Drive nativo con `drive.file`. Dos revisiones privadas en Review/Horus, reintento que reutiliza ID, contenido anterior intacto tras la nueva revisión, hashes completos verificados independientemente y lectura S25 confirmada. Cuenta y refresh en S23 reales; pruebas de restricciones SSH según salida del usuario. Se está cerrando el estado OAuth de producción para quitar el límite de siete días de Testing. [Operación y límites](HORUS_DRIVE_PUBLISH.md), [resultado](validation/mestry-horus-drive-live-20261021T040010Z/result.json). El movimiento inicial de carpeta requirió acción manual tras fallos API; el runtime de publicación no usa ese movimiento ni un proceso del PC. Solo un documento sintético autorizado, sin corpus, comentarios, tareas nuevas al modelo o frontend Android instalado. Los estados de preparación siguientes son históricos; el servicio documental completo y el RAG continúan pendientes.

**Preparación del publicador, 2026-10-21 UTC:** [implementación acotada y configuración Google](../tools/horus_publish/README.md) copiada a Termux, inactiva. Horus ejecuta Codex en UID Android 10350 y el publicador vive en Termux UID 10348; esto adapta la ubicación del controlador, conservando la separación de OAuth respecto al agente que exigía R2. Una clave exclusiva de comando forzado utilizará SSH 8023; todavía no se ha registrado ni probado. Runtime sin paquetes nuevos, OAuth inicial con biblioteca oficial en WSL y renovación nativa posterior en S23. 26 tests WSL / 25 S23 correctos y un test solo WSL omitido; APIs simuladas, no publicación real. El usuario prepara el cliente Google de escritorio con solo `drive.file`; callback WSL temporal pendiente de aprobación explícita. Cuenta y selección fijas, ID Drive persistido antes de subir, nuevas revisiones sin overwrite y verificación de metadata/privacidad/bytes. [Evidencia](validation/mestry-horus-publish-20261021T033650Z/manifest.json). OAuth, movimiento de carpeta app-owned a Review, SSH forzado, renovación real y funcionamiento sin PC quedan pendientes. El diseño R2 de servicio Android completo y RAG no se presenta como implementado.

**Actualización del 2026-10-21 UTC — piloto de revisión iniciado:** el usuario autorizó una carpeta privada nueva `MESTRY/Review` con documentos sintéticos y eligió una app Android para el S25. Tras renovar el permiso de la conexión, se crearon las carpetas y se subieron cuatro `.md`; metadata, acceso solo de propietario y descarga inicial exacta por SHA-256 verificados. Se consultó la API de comentarios del primer archivo, inicialmente vacía. [Resultado](validation/mestry-drive-review-20261021T020632Z/result.json). Después se recuperó una edición real del contenido reportada desde S25, sin sobrescribirla; el cliente utilizado no está identificado y la API todavía no devuelve comentarios separados. Esto prueba el conector/WSL y la lectura de esa edición: el usuario retiró los comentarios como requisito del piloto porque no los utiliza en Markdown. Se priorizan lectura, edición y publicaciones por versión. Siguen pendientes el adaptador entre UIDs y OAuth/publicación autónomos en el S23. V12 es parcial; V13 queda opcional, sin declarar soporte de comentarios; el diseño R2 siguiente conserva esas distinciones.

**R2 — 2026-10-19; diseño sin aprobar, sin acceder a cuentas ni descargar documentos.** [Fuentes G01–G16](EVIDENCE.md#documentos-identidad-y-almacenamiento) y [N09–N15](EVIDENCE.md#revision-r2-fuentes-nuevas). Las pruebas son V05–V07 y **V12–V13**, todas futuras.

## Dos flujos con autoridades distintas

La ampliación solicitada no convierte todo Drive en una réplica bidireccional. Se mantienen dos conjuntos seleccionados:

| Flujo | Autoridad | Dirección y permiso | Regla de escritura |
|---|---|---|---|
| **Corpus fuente** | Google Drive | Drive → copia privada S23; lectura | No editar ni subir derivados al origen; sirve al futuro RAG |
| **Documentos de trabajo/revisión** | Git/workspace S23 para el Markdown fuente; Drive para comentarios y ediciones humanas de una revisión | Publicaciones S23 → carpeta Drive; feedback Drive → inbox local | Un publicador crea versiones nuevas; no sincronización automática de dos escritores sobre el mismo archivo |

Codex puede crear/modificar `.md` en un repo del S23 y solicitar publicar una versión autorizada. El servicio documental mantiene OAuth y la relación de IDs; devuelve el enlace privado para abrir desde S25. El usuario revisa/comenta; el servicio recupera feedback y lo entrega como datos asociados a la versión correcta. Codex prepara después una nueva propuesta/diff. **Un comentario no aprueba arquitectura, no concede permisos al agente y no implica autorizar envíos o borrar contenido.**

El flujo de revisión se prioriza tras validar Codex local y antes del RAG. No hay subida, compartición ni comentario real en esta entrega.

## Selección tecnológica

**Recomendación para el servicio mantenible:** app Android pequeña en Kotlin, Drive API v3, WorkManager y almacenamiento privado con SQLite; dos adaptadores de flujo, un único manifest documental. Mantiene identidad por archivo, cursores de cambios y errores explícitos sin depender de PRoot ni de un daemon de desarrollo. No requiere LLM para sincronizar.

| Alternativa | Ventaja | Limitación | Papel recomendado |
|---|---|---|---|
| Drive API v3 + Android | IDs, cambios, permisos y exportación controlados; scheduler Android | Hay que desarrollar y verificar reconciliación | Motor único del Document Service si se aprueba |
| rclone en Termux | Herramienta madura, filtros y exportación; bajo costo de exploración | Mapea a rutas; requiere revisar duplicados/renombrados y trazabilidad por ID; ciclo de vida Termux | Comparador/piloto acotado; alternativa si satisface V05 sin envoltorio complejo |
| Round Sync | UI Android sobre rclone y tareas | Mantenimiento/OAuth actuales y exportación RAG no certificados | Evaluar antes de escribir mucho código; no asumir que sustituye el contrato documental |
| Drive Android “disponible offline” | Experiencia nativa y poca configuración | No contrato de exportación masiva a una carpeta propia ni cursor auditable para RAG | Consulta personal, no motor del índice |

La decisión API propia no busca rehacer Drive: se limita a réplicas seleccionadas y manifest por ID. Antes de construirla, contrastar un corpus pequeño con rclone. **Si un cliente mantenido cumple identidad, exports, eliminaciones y recuperación sin componentes adicionales, adoptarlo y conservar el mismo contrato de salida.** No ejecutar dos motores sobre un mismo destino.

## Autoridad y almacenamiento

Para el **corpus fuente**, Drive es fuente de verdad. La copia local es derivada y no editable. Un usuario que modifique un export local no provoca upload ni obtiene una “nueva versión oficial”. Se registra la alteración; se conserva aparte o se vuelve a descargar según política acordada.

Modelo lógico, no carpetas creadas:

| Entidad | Identidad y campos mínimos |
|---|---|
| Cuenta/corpus | `account_key`, root IDs permitidos, tipos, política de privacidad, versión de selección |
| Documento | `account_key + drive_file_id`; `driveId`, nombre, MIME, parents, enlace, modifiedTime, version remota, permisos/estado observables |
| Representación | ID de documento + formato export + versión del exportador + SHA-256 local + tamaño + fecha de descarga |
| Versión local | Representación inmutable; revisión remota cuando exista y se haya observado; nunca inventarla para Workspace |
| Cola de cambios | Secuencia local, file ID, observación remota, operación, intentos, estado, próximo intento |
| Checkpoint | Cuenta/corpus, token opaco de cambios, página y fecha de reconciliación completa |
| Fragmento | Documento + versión de representación + extractor/chunker + ordinal/locator + hash de contenido |

Guardar bytes por IDs/hashes, no por nombre como clave primaria. Un árbol de nombres puede ser una vista de navegación reconstruible. Dos documentos con igual nombre siguen siendo distintos; un rename mantiene el ID. Los nombres de Drive nunca se convierten en rutas sin saneamiento; impedir traversal y colisiones. Los shortcuts apuntan a un target explícito; no seguirlos fuera de la selección ni crear ciclos.

Bytes, base y temporales viven en el sandbox de **Document Service**, con UID distinto de Termux y del Device Agent. El índice contiene información personal aunque no contenga originales completos: protegerlo igual que los documentos. No usar almacenamiento compartido como ubicación base.

## Sincronización incremental

### Bootstrap sin perder cambios concurrentes

1. Obtener autorización y seleccionar root IDs. Obtener token inicial **antes** del inventario.
2. Enumerar carpetas/archivos con paginación y metadatos mínimos. La consulta de hijos se aplica por parent ID; no existe una consulta que mágicamente garantice todo un subárbol cambiante.
3. Registrar inventario y trabajos durables; descargar/exportar a temporal. Verificar tamaño/tipo y hash disponible. Leer versión/metadatos antes y después si la descarga puede solaparse con edición; si cambian, reencolar en vez de declarar snapshot estable.
4. Renombrar a representación final inmutable y publicar manifest transaccional. Un fallo entre filesystem y SQLite puede dejar un objeto huérfano, nunca un documento listo con bytes inexistentes; recolector/reconciliación recuperan huérfanos.
5. Consumir todos los cambios desde el token inicial y reconciliar movimientos de carpetas y contenido. Con ello se cubren cambios durante el inventario. El bootstrap no es una instantánea global atómica de todo Drive.

### Ciclos posteriores

`changes.list` devuelve cambios de usuario/unidad, no una suscripción recursiva por carpeta. Mantener grafo de parents y pertenencia al corpus. Si se mueve una carpeta, reenumerar su subárbol: no asumir que llegará un cambio individual por cada descendiente. Archivos que entran se incorporan; los que salen se excluyen del índice activo. [G01, G03](EVIDENCE.md#documentos-identidad-y-almacenamiento).

Por cada página, guardar **cola durable y siguiente cursor en una misma transacción SQLite**. Reintentar trabajos de la cola de forma idempotente. Solo publicar la nueva versión activa cuando estén sus bytes íntegros; no esperar a generar embeddings para reconocer un archivo descargado. El cursor significa *cambios recibidos de forma durable*, no *todos los archivos ya indexados*. Exponer ambos contadores por separado.

Consumir `nextPageToken` hasta el final y luego conservar `newStartPageToken`. Los tokens documentados de changes no expiran; no diseñar una supuesta renovación semanal del cursor. Ante cursor corrupto/rechazado, cambio de cuenta o pérdida de estado, hacer inventario completo y reconciliar antes de borrar. Ante revocación de credenciales, detener y pedir nueva autorización; no reiniciar destructivamente el corpus.

Inicialmente My Drive y carpetas accesibles seleccionadas. Si el corpus incluye Shared Drives, habilitar parámetros de soporte, namespaces y cursores por unidad donde correspondan; validarlos antes de anunciar cobertura. La ausencia de permisos nunca se transforma en “no hay documentos”.

### Frecuencia y recuperación

Propuesta de frecuencia: cada **60 minutos** con red disponible, más ejecución solicitada por el usuario y recuperación tras conexión. Es una preferencia de scheduling, no un SLA. WorkManager tiene mínimo periódico de 15 minutos y ejecución inexacta. No iniciar un `dataSync` permanente para simular un servidor: Android moderno limita su tiempo según versión/target. Lotes cortos, checkpoints y backoff. [A01–A02](EVIDENCE.md#android-agentes-e-inferencia).

Los webhooks requieren HTTPS alcanzable, renovación y posterior consulta de cambios. No justifican publicar el S23 ni mantener otro servidor para una copia horaria. Evaluarlos solo si una necesidad de frescura medida lo exige. [G10](EVIDENCE.md#documentos-identidad-y-almacenamiento).

Errores 429/403 de cuota: backoff exponencial con jitter y límite de intentos por ejecución. Distinguir 403 de cuota de 403 de permisos; 401 puede requerir renovación/autorización. Errores de exportación, parsers o espacio quedan visibles por archivo. No reintentar sin límite ni declarar éxito por exit code sin verificar el manifest.

## Exports, integridad y versiones

| Origen | Copia propuesta | Extracción/localizador | Límite |
|---|---|---|---|
| PDF/binarios seleccionados | Bytes originales | PDF: página + rango de texto; imagen: OCR posterior | Cifrado, escaneo o DRM pueden impedir extracción |
| Google Docs | DOCX para estructura; PDF opcional si se necesitan páginas | Encabezado/párrafo/tabla; página solo en PDF real | Export no incluye necesariamente comentarios/historial |
| Google Sheets | XLSX | Libro/hoja/rango A1, valores y fórmulas distinguidos | CSV aislado puede omitir otras hojas; no usarlo como export completo por defecto |
| Google Slides | PPTX; PDF opcional | Diapositiva/caja/notas si presentes | Confirmar notas y contenido excluido por export |
| TXT/MD/HTML/DOCX/XLSX/PPTX cargados | Bytes originales | Extractor acotado por MIME | No ejecutar macros, scripts ni recursos remotos |
| Tipos no soportados o > límite | Manifest con causa | No indexar como vacío | Nunca truncar silenciosamente |

`files.export` documenta máximo **10 MB de contenido exportado**. Archivos que lo superen necesitan otra estrategia documentada por tipo, por ejemplo lectura segmentada de su API específica con permisos adecuados, o quedar fuera de cobertura inicial. Esa excepción no se oculta como éxito. [G02](EVIDENCE.md#documentos-identidad-y-almacenamiento).

Binarios: comparar hashes remotos cuando estén disponibles y calcular siempre SHA-256 local. Workspace: no asumir MD5/SHA remoto de un archivo que no tiene bytes binarios originales. El hash acredita integridad de la representación obtenida, no equivalencia completa con todo el documento Google. Registrar formato y momento de exportación; cambios de empaquetado ZIP pueden alterar bytes sin cambiar texto.

Versionado local: objetos inmutables y puntero a versión activa. Tras extracción, calcular además hash de contenido normalizado para no repetir embeddings por un cambio de empaquetado. Propuesta inicial de retención para versiones reemplazadas/eliminadas: **30 días**, con presupuesto de espacio configurable y borrado físico mediante política aprobada. No es una copia del historial completo de Drive.

## Eliminaciones y pérdida de acceso

- Confirmado `trashed`, eliminación o salida de selección: tombstone y retirada inmediata de búsqueda activa; conservar copia en cuarentena de recuperación según retención.
- `removed` puede significar eliminación **o pérdida de acceso**. Registrar causa desconocida cuando no se puede distinguir. Para pérdida de acceso, retirar de recuperación normal y bloquear exposición del objeto retenido; no tratar el caché como permiso permanente de lectura.
- Una carpeta vacía por error de red no autoriza una eliminación masiva. Reconciliación completa solo genera bajas tras enumeración finalizada y sin errores de alcance.
- Archivo local corrupto: volver a descargar una vez disponible; mantener fallo hasta validar. Offline: últimas versiones válidas disponibles con `last_successful_sync_at` y estado obsoleto; para contenido revocado observado se respeta la exclusión.
- Eliminar un documento debe retirar fragmentos, FTS y vectores correspondientes. Las versiones en cuarentena no participan en consultas ordinarias.

### Si se elige rclone

Usar remote Drive con client ID propio, scope readonly y root IDs/filtros acotados. Su client ID compartido está en retiro durante 2026 según la documentación consultada. Para exploración, **copy** evita borrar extras pero no refleja eliminaciones; no cumple por sí solo una réplica autoritativa. **sync** replica bajas del origen en el destino y debe apuntar a un directorio exclusivo, con dry-run, respaldo de reemplazos/bajas y controles de alcance. [G06–G07](EVIDENCE.md#documentos-identidad-y-almacenamiento).

Ni rclone sync ni backup-dir producen automáticamente el contrato de IDs/citas. **Rclone sí expone IDs y metadatos mediante `lsjson`**: puede alimentar el manifest sin reimplementar todo el inventario. Probar IDs de exports, duplicados, rename, move y baja con V05 antes de decidir que hace falta un motor propio. [G16](EVIDENCE.md#documentos-identidad-y-almacenamiento). Configuración OAuth de rclone contiene credenciales; cifrar su configuración y resolver cómo entregar la clave a un trabajo desatendido. Un secreto junto al archivo cifrado bajo el mismo UID no añade aislamiento frente al agente.

## OAuth y datos personales

**Para el corpus fuente:** acceso readonly a contenido de carpetas escogidas en la lógica del servicio. El scope `drive.readonly` permite leer todo lo accesible por la cuenta; **la selección de carpeta es un filtro de aplicación, no una barrera OAuth**. `drive.file` ofrece acceso por archivos autorizados, pero admite escritura y no debe suponerse que una carpeta elegida autorice todos sus descendientes existentes/futuros. La elección requiere [P03](DECISIONS.md#aprobaciones-pendientes).

Para la app Android, evaluar `AuthorizationClient` de Google Play services: devuelve tokens cuando la cuenta y scopes ya están autorizados, o una resolución que requiere al usuario. No diseñar la app alrededor de APIs de GoogleAuthUtil obsoletas ni copiar un refresh token de una CLI a Android. Para una herramienta instalada como rclone, el flujo OAuth de cliente instalado y su refresh token son un caso distinto. [G05, G15](EVIDENCE.md#documentos-identidad-y-almacenamiento).

Cuando el componente mantenga refresh tokens u otros secretos, cifrarlos mediante claves Android Keystore y almacenamiento privado; evitar logs/backup de tokens. Conservar acceso protegido después del primer desbloqueo, sin exigir biometría por cada tarea si eso impide el uso autorizado en segundo plano. Validar renovación, revocación y reautorización de forma explícita. Las apps OAuth externas en Testing pueden recibir refresh tokens de 7 días para estos scopes; no confundirlo con expiración de cursores Drive. No crear backend solo para renovar tokens si el cliente Android soportado basta.

No enviar documentos ni embeddings externos inicialmente. Si se activa un proveedor externo, consentimiento por corpus y campos, minimización, destino y retención conocidos. La autorización de inferencia Codex para un repositorio no autoriza transmitir el corpus personal, comentarios o capturas al modelo. La revisión en Drive autoriza solo los documentos seleccionados para ese destino. Uso estándar de Drive API figura sin cargo adicional; existen nuevas cuotas 2026 y anuncios de cargos sobre umbrales. No prometer gratuidad ilimitada. [G09](EVIDENCE.md#documentos-identidad-y-almacenamiento).

## Markdown nativo en Drive y Docs: evidencia y límites

El [anuncio oficial del 5 de octubre de 2026](https://workspaceupdates.googleblog.com/2026/10/preview-edit-and-collaborate-on-Markdown-files-natively-across-Drive-and-Docs.html) confirma vista renderizada en Drive y edición/comentarios colaborativos en Docs **sin convertir `.md`/`.markdown` a otro tipo de archivo**. Indica despliegue gradual de hasta quince días y disponibilidad para Workspace y cuentas personales. El 19 de octubre no se presupone que la cuenta del usuario tenga ya la función. [N09](EVIDENCE.md#revision-r2-fuentes-nuevas).

La [ayuda del editor](https://support.google.com/docs/answer/18289341) confirma permanencia del tipo Markdown e historial; también documenta pérdidas/cambios de formatos de Docs incompatibles con Markdown. No garantiza que un viaje de edición conserve bytes, enlaces relativos, Mermaid, HTML, YAML front matter o toda extensión GitHub. No afirma soporte equivalente en las apps Android. **Probar Drive/Docs nativos del S25 y navegador móvil por separado**; el modo escritorio del navegador es un posible fallback a medir, no éxito supuesto. [N10](EVIDENCE.md#revision-r2-fuentes-nuevas).

Un `.md` sigue siendo archivo con contenido descargable; no necesita `files.export` como un Google Doc nativo. Comprobar `mimeType`, capacidades, ID y descarga después de abrir/editar. La nueva UI no demuestra que `documents.get` de Docs API acepte ese ID binario, ni que todos sus comentarios sean accesibles de la misma forma. Es la hipótesis principal de V12/V13, no una integración ya disponible.

## Publicación y revisión desde S25

Propuesta mínima: carpeta privada `MESTRY/Review`, creada/autorizada para esta función; nombres con secuencia y hash breve, por ejemplo `ARCHITECTURE.r0007.a1b2c3d4.md`. El nombre es legible; las identidades reales son IDs, no nombres de archivo. **Cada publicación crea un archivo nuevo**; el publicador no reemplaza el contenido de una revisión abierta. No se publican archivos mediante `revisions.published` ni permisos `anyone`: aquí publicar significa subir privadamente para revisar.

1. Codex trabaja en el checkout S23. Seleccionar explícitamente archivos de documentación y revisar diff; excluir `.codex`, `.git`, tokens, bases, capturas y archivos no autorizados.
2. El adaptador de intercambio entrega bytes y metadatos, nunca un path arbitrario que Document Service deba leer. Mantener UID/OAuth separados; V12 valida URI grants o capacidad loopback sin inventar acceso entre sandboxes. [Contrato](ARCHITECTURE.md#contratos-minimos).
3. Guardar una copia consistente del Markdown y su SHA-256, logical document ID, repo/commit y secuencia. Registrar solicitud durable con idempotency key y destino permitido antes de la subida.
4. Crear archivo Drive con extensión/MIME adecuado, sin conversión; guardar `fileId`, `version`, revisión remota si es observable y `webViewLink`. Descargar una muestra o el fixture completo para verificar bytes; no marcar publicado solo por iniciar upload.
5. S25 abre ese enlace y comprueba versión/título antes de comentar. El catálogo inicial puede ser la propia carpeta ordenada por versiones y los enlaces devueltos; no hace falta una nueva aplicación web.
6. Recuperar comentarios y, si hay ediciones humanas, bytes remotos como propuesta separada. Entregar un `FeedbackBatch` al checkout autorizado. El usuario decide el trabajo derivado; no autoaplicar texto como instrucciones de sistema.
7. Codex prepara nueva versión local. Tras revisión/autorización dentro del alcance, crear r0008 y mantener r0007 con su discusión. No mover comentarios a otra versión como si fueran anclas equivalentes.

Un solo publicador serializa por logical document ID. Si se pierde la respuesta a una creación, reconciliar mediante manifest e identificador de publicación guardado en metadatos privados de app antes de reintentar; si no se puede determinar si se creó, registrar **resultado incierto** y detener ese trabajo. Puede evaluarse reserva de IDs si la API/tipo la permite. No declarar entrega exactamente una vez basándose solo en reintentos o nombres únicos: Drive admite nombres duplicados.

El alcance de sincronización saliente son **estos artefactos aprobados**, no todos los proyectos ni el corpus personal. Rclone `copy` puede servir para un piloto de subida a nombres de versión únicos y `lsjson` para reconciliar IDs; no recupera por sí solo el ciclo completo de comentarios. `bisync` o `sync` bidireccional no son la recomendación: pueden borrar/reemplazar trabajo o confundir archivos por nombre. La API v3 encaja mejor con la identidad, feedback y cola de publicación; contrastar costo de construir este adaptador pequeño frente a un cliente mantenido.

## Recuperación autorizada de comentarios

**Fuera del piloto actual por preferencia del usuario (2026-10-21):** el usuario no comenta archivos Markdown. El diseño siguiente se conserva como una opción futura; no implementar ni exigir este circuito para continuar con lectura, edición, versiones y la app Android. La edición remota ya observada se conserva separada de su base.

**Ruta principal propuesta: Drive API v3**, para cada `fileId` de revisión conocido. [Gestión de comentarios](https://developers.google.com/workspace/drive/api/guides/manage-comments), [comments.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/comments/list), [replies.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/replies/list), [recurso Comment](https://developers.google.com/workspace/drive/api/reference/rest/v3/comments). [N11–N12](EVIDENCE.md#revision-r2-fuentes-nuevas).

- Solicitar `fields` explícitos, obligatorio en comments salvo delete: `nextPageToken` y, por comentario, ID, content, fechas, resolved, deleted, autor mínimo, quote, anchor y respuestas necesarias. No pedir correo si no es necesario; la API no rellena todos los identificadores del autor.
- Primera carga paginada completa; después `startModifiedTime` con solapamiento y deduplicación por `fileId + commentId + modifiedTime`. **Ese es el nombre del parámetro v3**, no `minModifiedTime`. `Comment.modifiedTime` incluye modificaciones de sus respuestas. Agotar `nextPageToken`; si se invalida, volver a enumerar y deduplicar, no saltar páginas.
- `includeDeleted=true` y reconciliación periódica completa. Conservar tombstones/estado, no inventar el texto de comentarios eliminados. `resolved` no significa eliminado. Reenumerar respuestas para las discusiones cambiadas usando IDs y estado; la respuesta embebida puede aprovecharse si se comprueba completa. No suponer filtros temporales en replies que su referencia no ofrezca.
- Guardar lote y watermark en una transacción **tras** recibir todas las páginas correspondientes; usar un límite temporal seguro registrado al comenzar y un solapamiento para no perder cambios concurrentes. Los page tokens no son el cursor `changes` del corpus.
- Hacer polling explícito de comentarios de revisiones abiertas, además de la detección de cambios de contenido. No se encontró una garantía suficiente de que `changes.list` notifique todo cambio de comentario sin modificar bytes: no depender solo de ese feed.

Un `anchor` puede contener datos opacos del editor; una cita puede faltar o repetirse. Guardar texto citado, sección/localizador conocido, hash de base y ancla original; solo resolver automáticamente si hay coincidencia inequívoca contra la versión capturada. Si hay ambigüedad, presentar comentario sin ubicación exacta. La guía advierte que la posición puede no conservarse entre revisiones y las anclas creadas por API no equivalen a anclas nativas del editor.

**No se afirma que Docs API carezca de comentarios.** Su documentación actual expone `commentsViewMode`, hilos y anclas; podría ofrecer ubicación estructural cuando el tipo de archivo lo permita. Sin embargo, la guía y partes de la referencia muestran condiciones inconsistentes sobre el modo de sugerencias, y no se verificó soporte de archivos Markdown. [Docs: comentarios/sugerencias](https://developers.google.com/workspace/docs/api/how-tos/suggestions), [referencia Document](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents). V13 probará capacidades/tipos de respuesta autorizados antes de depender de esa ruta. No se da por hecho que sea preview ni que esté habilitada para esta cuenta. [N14](EVIDENCE.md#revision-r2-fuentes-nuevas).

Si la API no devuelve los comentarios nativos del `.md`, registrar fallo de integración. Fallback documental posible: **proyección separada a Google Doc** para comentarios, con su propio ID, versión de Markdown base y advertencia de formato; no afirmar que conserva el archivo ni el mismo historial. Solo adoptarla si el usuario acepta la pérdida de equivalencia. No scraping, automatización de cookies, endpoints privados ni tokens de terceros.

El primer incremento de revisión solo **lee** comentarios/respuestas. Responder o resolver desde el agente sería una capacidad de escritura adicional, con autorización explícita por acción. No resolver automáticamente un comentario porque Codex crea haberlo atendido. Autores/quotes/HTML son datos no confiables; escapar su renderizado, no ejecutar HTML ni cargar recursos remotos.

## Versiones, conflictos y retención de revisiones

Manifest adicional en SQLite:

| Entidad | Clave y contenido |
|---|---|
| Documento lógico | ID propio estable, repo/ruta autorizada, origen/autoridad y política |
| Publicación | Logical ID + secuencia + idempotency key, hash/commit/base, estado queued/uploading/uncertain/published/failed |
| Revisión revisable | File ID Drive independiente por publicación, revisión/version remota observadas, MIME, URL y hash publicado |
| Feedback | File ID + comment/reply ID, timestamps, deleted/resolved, texto/quote y ancla opaca; hash de base |
| Propuesta remota | File ID/revisión observada, bytes/hash, base usada y estado pendiente/merge/conflict |

En Markdown, `version` Drive es un contador de cambios del archivo, **no** un SHA, número de revisión editorial ni sustituto de un ID de revisión. El formato/hashes de metadatos pueden variar por tipo; verificar tras el editor nativo. Git conserva historia de contenido local; los comentarios no viven dentro de los bytes Markdown, por lo que necesitan captura separada.

La [política de revisiones Drive](https://developers.google.com/workspace/drive/api/guides/manage-revisions) permite conservar revisiones blob con `keepForever` hasta un máximo documentado de 200 por archivo, contando almacenamiento; otras pueden purgarse. El historial visible de Docs y lo enumerado por API no necesariamente tienen la misma cobertura. Por ello los artefactos de revisión y los snapshots locales son el registro de esta aplicación, **no se promete recuperar cualquier revisión histórica desde Drive**. [N13](EVIDENCE.md#revision-r2-fuentes-nuevas).

Conflictos previstos:

- **Codex avanza mientras se comenta r0007:** la base de feedback sigue siendo r0007. Generar diff contra esa base; no desplazar una cita a la última versión por coincidencia aproximada.
- **El usuario edita r0007 en Docs:** se detecta divergencia de bytes/hash/revisión. Guardar remoto por separado y proponer merge de tres versiones: base publicada, local actual y remoto observado. El publicador no sobrescribe r0007 ni reemplaza automáticamente el archivo Git.
- **Edición durante descarga:** comparar metadatos/hash antes/después y reintentar si cambian. Eso detecta inestabilidad, no una instantánea global atómica.
- **Dos peticiones de publicación:** serialización durable por documento e idempotencia; una sola instancia escritora. No confundir bloqueo local con exclusión de editores humanos en Drive.
- **Archivo mutable permanente solicitado más adelante:** hará falta un protocolo de edición/lease o escritura condicional **documentado y validado**. La referencia `files.update` consultada no basta para prometer CAS por `version`; leer metadatos y luego subir deja una carrera. No afirmar que `If-Match`/412 está garantizado sin evidencia específica del endpoint/tipo. [files.update](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update).

Existe una alternativa condicional **documentada para Google Docs**: `documents.batchUpdate` con `writeControl.requiredRevisionId` rechaza la escritura si el documento cambió desde la lectura; `targetRevisionId` tiene otra semántica de integración con cambios concurrentes. [Prácticas oficiales de Docs](https://developers.google.com/workspace/docs/api/how-tos/best-practices). No son el `version` ni el revision ID de Drive y no se trasladan a `files.update`. Si V13 confirma que Docs API admite estos Markdown, podría reevaluarse un documento mutable con esa protección; no se presupone esa compatibilidad ni se autoacepta un merge del servidor. [N15](EVIDENCE.md#revision-r2-fuentes-nuevas).

En la primera versión se evita esa carrera **creando nuevos archivos de revisión**, no sobrescribiendo un archivo que un humano edita. La política de “inmutable” restringe al publicador; el propietario de Drive puede editar, y esa divergencia se conserva. La carpeta puede crecer: acordar presupuesto y retención antes de borrar versiones. No eliminar automáticamente revisiones con discusiones pendientes. Ni una baja remota ni una limpieza de caché borran el original Git.

## OAuth del flujo de revisión

Usar `drive.file` para archivos creados/autorizados por esta aplicación: su referencia permite `comments.list`. Preferir carpeta de revisión y artefactos creados por el publicador. No asumir autorización recursiva de todo el Drive por elegir una carpeta. Para el corpus ya existente se conserva la evaluación de `drive.readonly` de la sección OAuth anterior.

Separar perfiles/capacidades de lectura del corpus y publicación/revisión; comprobar scopes efectivos y grants acumulados, no suponer que dos variables de token bajo el mismo cliente crean aislamiento OAuth. **El agente de desarrollo no recibe ninguno de esos tokens**: obtiene una capacidad local limitada al documento/proyecto y destino aprobados. No ampliar a `drive` global para simplificar permisos. [G04–G05, N12](EVIDENCE.md).

La cuenta y el método OAuth son pendientes de V06/V12. El diseño no usa service accounts con acceso implícito al Drive personal ni una cuenta conectada en Codex como si proporcionara automáticamente credenciales a otra app. Capturas de revisión y comentarios pueden ser personales: exportar al contexto de Codex solo el feedback explícitamente seleccionado para esa tarea.

## Preparación para RAG

Excluir inicialmente la carpeta de Review y su feedback del corpus RAG para evitar duplicados, versiones no aprobadas y un bucle de reingesta. Solo una decisión editorial explícita puede promover una revisión a corpus fuente.

Pipeline propuesto: **representación validada → extractor → texto con estructura → normalización → fragmentos → FTS → embeddings opcionales → recuperación con citas**. El original queda intacto. El estado de cada paso es separado: descargado, extraído, indexado y error.

Normalizar Unicode y espacios sin borrar números, unidades, encabezados o coordenadas de tabla. Mantener texto original para cita y texto normalizado para búsqueda. OCR solo cuando falte texto útil; registrar motor, versión, idioma y confianza. Un documento no extraíble es una brecha de cobertura, no un documento sin información.

Chunking inicial propuesto: 300–500 tokens respetando estructura, solapamiento aproximado de 50, ajustado al tokenizador/límite del embedding. No cortar filas/tablas arbitrariamente; encabezados acompañan celdas. Un fragmento largo se subdivide con localizadores estables. El tamaño se valida con corpus español, no se toma como universal.

**Índice inicial:** SQLite con FTS5 y `unicode61` sobre driver SQLite empaquetado y versión fijada, o FTS4 si la combinación Android elegida lo requiere. La documentación Room actual incluye FTS5; no se asume que SQLite de sistema lo incluya. Probar acentos, ñ, números y consultas por frases en V07. FTS no requiere un LLM.

**Vectorial:** primero comparación exacta en memoria sobre candidatos o corpus pequeño; luego `sqlite-vec` si mejora calidad/latencia con costo aceptable. Android puede requerir enlace nativo, no carga dinámica de una extensión de escritorio. No desplegar un servidor vectorial ni Qdrant/Milvus/Elasticsearch sin límites medidos que lo justifiquen.

Embeddings candidatos: `multilingual-e5-small` (384 dimensiones, prefijos `query:`/`passage:`, máximo 512 tokens) y EmbeddingGemma 300M como comparación. Fijar revisión, normalización, dimensión y cuantización. Vectores de modelos distintos no se mezclan. Ejemplo de dimensionamiento **aritmético, no benchmark**: 10.000 × 384 × 4 bytes = 15,36 MB de vectores float32, sin contar índice, metadatos ni runtime. [G11–G14](EVIDENCE.md#documentos-identidad-y-almacenamiento).

Incrementalidad: hash semántico y versiones de extractor/chunker/embedding deciden qué se reconstruye. Publicar una generación coherente por documento mediante transacción; si falla, conservar estado anterior marcado desactualizado o excluirlo si perdió acceso. Un embedding nuevo no obliga a reexportar Drive; una eliminación sí invalida todas las generaciones activas.

Recuperación: FTS primero; comparar híbrido léxico/vectorial en V07 antes de añadirlo. Respuesta incluye `document_id`, título, enlace Drive, versión/hash local, fecha de sincronización, localizador y extracto exacto. El modelo no inventa números de página ni referencias a una versión remota histórica no capturada. Filtrar permisos y vigencia **antes** de devolver texto.

MESTRY Core consumirá `search` y `get_fragment`; no leerá tokens, base o disco directamente. Contenido recuperado se considera dato no confiable y no puede conceder permisos al Device Agent. La generación de respuestas y el control de aplicaciones quedan desacoplados de la sincronización.
