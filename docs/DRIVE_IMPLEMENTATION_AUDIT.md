# Auditoría del repositorio y estado de Google Drive

**Línea base histórica anterior al desarrollo del 08/11:** este informe conserva
el diagnóstico que motivó el incremento. El estado posterior está en
[Sincronización documental](DOCUMENT_SYNC.md): motor y caché implementados y
activados en S23, con aceptación del contenido real y S25 todavía pendiente.

**Prioridad revisada — 08/11/2026:** RAG queda **PENDIENTE DE REVISIÓN**.
El usuario anticipa poco uso en el producto final; su implementación no se
considera un siguiente paso comprometido. Antes de retomarla, revisar casos de
uso reales y si la lectura/búsqueda directa de archivos ya los resuelve. Esto no
elimina ni modifica el ADR congelado: una eventual exclusión definitiva de RAG
requiere registrar la decisión arquitectónica correspondiente.

Fecha: **08/11/2026**, America/Santiago. Corte local: HEAD `359162c`.
Auditoría de código, pruebas offline y documentación; sin consultas a cuentas,
teléfonos, servicios, Git remoto ni escrituras Drive. No es una aceptación H4/H5.
El [ADR congelado](../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md)
conserva íntegros D-01–D-15 y AC-01–AC-12.

## Estados y autoridad de la evidencia

**APROBADO** describe una decisión, **PROPUESTO** una alternativa futura,
**IMPLEMENTADO** código inspeccionado, **PROBADO** una ejecución con alcance y
fecha, **PENDIENTE** una capacidad faltante, **NO VERIFICADO** una condición sin
comprobación suficiente. Pueden coexistir: pruebas simuladas no prueban Google.

Se inspeccionó el clon de desarrollo fuera de Drive. Se preservaron tres cambios
previos (`tools/s25-codex-client/README.md`, parche y pins) y dos archivos no
versionados (`read_existing_fixture.py`, `test_read_existing_fixture.py`).
Estos auxiliares son código local inspeccionado, no una entrega integrada.
No se ejecutaron instaladores, OAuth, migraciones, sincronizadores ni despliegues.
Los ejemplos públicos no son configuración desplegable.

Precedencia temporal: los PASS de publicación del 21/10 preceden al cambio de
raíz del navegador del 22/10. La revisión del 03/11, conservada en
[PROJECT_REVIEW](PROJECT_REVIEW.md#incidencias-qué-sabemos-y-qué-falta-establecer),
registra lectura de un fixture restaurado de 79 bytes y bloqueo del publicador
por padre distinto de Review. Por ello, ni “sigue en papelera” ni “publicación
disponible hoy” son estados actuales demostrados. El 08/11 no se consultó Drive.

## Inventario y madurez general

| Componente real | Tecnología / evidencia | Estado y límite |
|---|---|---|
| Cliente S25 y bridge S23 | Kotlin/Compose/Java y Node; parche en `tools/s25-codex-client/`, `source-pins.json` | IMPLEMENTADO; aceptación histórica H3 del 04/11. Upstream fijado a `538d65f67e34907789237fc71f56e8ca95d9f3cb`; 68 entradas de texto en pins. No es una app escrita desde cero |
| Continuidad Git | Python, shell, PowerShell; `work_session.py`, `project-gate.mjs`, `.mestry-workflow.json` | IMPLEMENTADO / PROBADO offline y H3 histórico. Lock cooperativo, validación y recepción; no sincroniza documentos Drive |
| Nodo y acceso privado | Horus/Alpine ARM64, Termux, SSH, túnel y VPN; `tools/s23-remote-access/` | Herramientas IMPLEMENTADAS; disponibilidad actual NO VERIFICADA. Handover, reinicio y 24/7 pendientes |
| Herramientas documentales | Python estándar, urllib, SQLite; `tools/horus_publish/` | Publicador y navegador IMPLEMENTADOS / PROBADOS con simulaciones y pilotos históricos acotados |
| Preparación OAuth | `oauth_setup.py`, `authorize_wsl.py`, `authorize_picker_wsl.py` | Flujo implementado. `requirements.txt`: google-auth 2.62.0 y google-auth-oauthlib 1.5.0 para preparación WSL; runtime S23 sin esos paquetes |
| Documentación y evidencia | `docs/`, informes fechados, recibos H3, ADR público saneado | Decisiones, propuestas y resultados históricos separados; varios enlaces a evidencia privada ausente |
| Core completo, voz, teclado, Device Agent, memoria, RAG y Free Model Broker | Diseño en ADR y documentos de referencia | PENDIENTE como producto integrado; no localizados en el código inspeccionado |

El contrato local exige Python ≥3.12, Git ≥2.43 y Node ≥22 para WSL x86-64 y
Alpine ARM64. Android/Gradle y dependencias upstream están representados por
parche/pins; no se reconstruyó ni compiló ese árbol. La copia pública no contiene
los cinco documentos congelados previos citados por el ADR (§0.3); tampoco se
localizaron por esos nombres en el árbol histórico consultado. Su contenido y
compatibilidad completa son **NO VERIFICADOS**; no se inventan decisiones.

## Recorrido real desde la solicitud

### Consulta de documentos

1. La tarjeta Drive del cliente S25 abre selector, carpetas y vista previa:
   `MainActivityDriveController.kt` y UI incluidos en
   [el parche](../tools/s25-codex-client/mestry-pilot1.patch).
2. Envía `drive.state`, `drive.folder.enable`, `drive.assign`,
   `drive.list` o `drive.read` por el bridge autenticado. Su
   `BridgeServer` requiere política piloto y `driveClient`; asignar proyecto
   además pasa la política de proyecto.
3. `src/mestry-drive.mjs::DriveClient.request` valida campos y tamaño,
   lanza Python aislado con ejecutable fijo y sin shell. La consulta no crea
   un turno Codex ni llama a un modelo.
4. [drive_client.py](../tools/horus_publish/drive_client.py) transporta JSON por
   SSH loopback 8023, identidad y host fijados, sin forwardings, con timeout.
   El comando forzado `mestry-drive-v1` entra al receptor Termux.
5. [drive_browser.py](../tools/horus_publish/drive_browser.py) valida esquema,
   cuenta, raíces habilitadas, papelera y ascendencia; usa `Drive.call` contra
   Drive API v3 oficial por HTTPS con OAuth.
6. Devuelve metadatos, enlace y texto; el cliente lo muestra. No hay inserción
   automática en contexto RAG ni cita generativa verificada.

`state_response` enumera hasta cinco páginas de 100 carpetas visibles al
cliente y señala si quedan más. `list` pagina hijos directos de una carpeta.
No es un inventario recursivo del corpus. Hasta 32 raíces locales; ascendencia
limitada a 33 iteraciones y un padre por nodo; no se siguen shortcuts.

`read` descarga texto/JSON/XML vía `alt=media`; Google Docs se exporta a
texto plano. PDF, DOCX, Sheets, Slides y demás binarios devuelven
`OPEN_IN_DRIVE`; no hay extractor de esos tipos. Texto inválido o mayor de
64 KiB también deriva a Drive. Abrir externamente no acredita extracción ni
edición mediante MESTRY.

### Publicación

[client.py](../tools/horus_publish/client.py) lee únicamente
`S23_PUBLISH_TEST.md` del proyecto sintético permitido, valida UTF-8 y 64 KiB,
calcula hash e ID determinista y solicita `mestry-publish-v1` por SSH.
[publisher.py](../tools/horus_publish/publisher.py) valida cuenta fija, destino,
propietario único y privacidad, reserva ID en SQLite antes del upload, crea un
archivo Markdown nuevo y verifica metadatos y SHA-256 de los bytes descargados.
Solo entonces marca `verified=1` y devuelve `PUBLISHED_VERIFIED`.

No modifica un documento existente. La “revision” devuelta es una secuencia
local, no un revisionId remoto. El mismo contenido reutiliza reserva/ID;
otra versión crea otro archivo. Si una revisión ya publicada cambió o fue
eliminada, el retry falla sin recrearla ni sobrescribirla. Límites: 20 reservas
nuevas/día UTC y 32 totales. No hay API de edición Docs/Sheets/Slides,
precondición de revisión para actualizar un original, diff/confirmación general
ni merge concurrente. La autorización es la capacidad acotada del piloto;
no equivale al controlador general de D-07.

## Autenticación, selección y almacenamiento

Existe un conector acotado real, no una clase vacía: `publisher.Drive` hace
HTTP oficial, OAuth instalado y refresh grant; no scraping. Preparación
interactiva/Pickers usa WSL y biblioteca oficial con PKCE y callback temporal.
El runtime refresca por HTTPS en S23 cuando el token está próximo a caducar.
Un error 401 posterior no dispara automáticamente otro refresh en `Drive.call`.

Solo se admite `drive.file`; selección local y concesión Google son distintas.
Una carpeta habilitada no concede OAuth a todos sus descendientes. El navegador
está limitado al proyecto sintético por `drive_browser.PROJECT`; H3 sobre el
repo real no amplía automáticamente esa asignación. No se presume acceso a
todo Drive ni equivalencia con la cuenta/conexión de FolderSync o rclone.

Rutas del runtime documentado, **no creadas ni consultadas en esta auditoría**:

| Datos | Ubicación / protección implementada |
|---|---|
| OAuth, cliente y configuración | Termux `~/.local/state/mestry-publish/`; JSON privados |
| Reservas de publicación | `journal.sqlite3`, tablas `folder` y `publication`; no catálogo del corpus |
| Selección navegador | `drive-browser.json`, raíces y asignaciones; lock propio |
| Código receptor | Termux `~/.local/lib/mestry-publish/` |
| Capacidad Horus | `~/.ssh/id_ed25519_mestry_publish` y known_hosts; sin OAuth |
| Texto de lectura | Respuesta en memoria/vista previa; sin caché documental durable ni índice local |

`private_path/read_private/write_private` comprueban dueño, symlinks y modos
700/600; escritura temporal, fsync y replace. El aislamiento OAuth depende de
UID Android Termux separado de Horus. **No se implementa cifrado aplicativo con
Keystore**: los JSON no están cifrados por este código. El estado de cifrado del
dispositivo, backups, revocación y retención actuales no se verificó.
Los errores se reducen a códigos; ello no es una prueba exhaustiva de ausencia
de filtraciones en todo el sistema. No se leyeron secretos.

## Sincronización, frescura y recuperación

**No existe sincronización incremental documental funcional en el código
inspeccionado.** No se localizaron consumidor `changes.list`,
`getStartPageToken`, `newStartPageToken`, bootstrap de corpus, checkpoint de
cambios, cola durable de ingesta, tombstones, FTS, chunks, vectores ni scheduler
Drive. El `page_token` del navegador es paginación de listado, no cursor durable
de cambios. El polling H3 de Git no es polling Drive.

- **Bajo demanda:** cada listado/lectura vuelve a consultar Google. La segunda
  lectura vuelve a descargar/exportar bytes aun sin cambios; no hay cache hit.
- **Cambios remotos:** una lectura posterior ve el contenido que la API entregue;
  no hay notificación ni invalidación de un índice. Metadatos de lectura incluyen
  modifiedTime pero no version/revisionId, ni comparación antes/después del texto:
  una edición concurrente puede dejar metadatos y bytes de momentos distintos.
- **Altas/movimientos/bajas/permisos:** se observan al volver a listar o validar
  raíz/ancestros. 403/404 de metadata se informan como no concedido/no disponible,
  sin inventar si fue borrado o revocado. No hay bitácora ni reconciliación global.
- **Offline:** error explícito y sin respuesta desde caché documental; no hay
  recuperación automática al volver la red ni estado de antigüedad por documento.
- **Retries:** HTTP con timeout y sin redirección de Bearer; no hay backoff/jitter
  de cuota, clasificación completa de 403 ni cola persistente. El publicador sí
  soporta reintento idéntico y reserva durable ante respuesta perdida/409.
- **Recursos:** lectura acotada, sin embeddings ni proceso documental permanente.
  La revalidación de ancestros y las descargas repetidas consumen red. Locks
  serializan operaciones, pero los locks de browser/publicador son distintos;
  no hay coordinación global de refresh entre ambos.
- **RAG/Broker:** solo diseño; no extracción general, fragmentos por versión,
  comprobación de vigencia del contexto, búsqueda semántica o integración con
  Free Model Broker. Enlaces/IDs del navegador dan procedencia básica, no
  trazabilidad de fragmentos.

FolderSync sí tiene transferencia real documentada: el
[informe 11](investigaciones/2026-10-26_codex_24x7/11_CORRECCIONES_POST_H0.md)
registra upload/download con hash y SyncOK; horario al minuto 17 de cada hora,
borrados desactivados. rclone bisync figura como circuito WSL histórico en
[la auditoría de infraestructura](auditorias/2026-10-26/02_INFRAESTRUCTURA_Y_SINCRONIZACION.md).
Son sincronizadores externos de árboles, no el Sync Engine del ADR, ni prueban
un manifest por fileId/version, recuperación RAG o acceso al sandbox Horus.
Su ejecución actual y configuración privada no se inspeccionaron. No se tocaron.

Windows/WSL ejecuta desarrollo, tests y preparación interactiva OAuth.
La lectura/publicación acotada y refresh están diseñados y probados históricamente
en S23 sin proceso PC en su camino de ejecución. El cliente S25 depende de
túnel/SSH/bridge y ambos nodos de red, procesos Android y Google disponible.
Inferencia Codex depende de su servicio externo. PC físicamente apagado,
reinicio, Doze, batería y recuperación prolongada siguen **NO VERIFICADOS** para
este flujo. Recortes de procesos observados en H3 no se resuelven con un test WSL.

## Comparación con D-01–D-15

Todas las decisiones de esta tabla están **APROBADAS** en el ADR; la columna
estado describe cumplimiento técnico, no modifica su autoridad.

| Decisión / capacidad | Estado y evidencia | Brecha / acción pendiente |
|---|---|---|
| D-01 Nombre | IMPLEMENTADO en puntos de entrada MESTRY | Preservar nombres históricos |
| D-02 Autoridad Drive | Parcial: lectura API y nuevas publicaciones | Falta catálogo de originales seleccionados y restore aceptado |
| D-03 Separación | IMPLEMENTADO parcial: UI → bridge → broker Termux | Core, Tool Manager general y RAG PENDIENTES |
| D-04 Selectiva/incremental | Lectura selectiva IMPLEMENTADA; `handle` | Changes, caché y no redescarga PENDIENTES |
| D-05 Directo/RAG | Directo IMPLEMENTADO; `list/read` | RAG PENDIENTE DE REVISIÓN por utilidad prevista |
| D-06 Formatos | Docs export/texto y publicación MD IMPLEMENTADOS | Edición nativa y archivos convencionales PENDIENTE |
| D-07 Controlador | Validación acotada PROBADA en tests publisher | Operaciones generales, permisos/confirmación por acción PENDIENTES |
| D-08 No overwrite | PROBADO offline en nuevas versiones/retry | Edición in situ con revisión y conflictos PENDIENTE |
| D-09 Privacidad | Scope fijo, modos y UID IMPLEMENTADOS | Keystore/cifrado aplicativo, retención y política de contexto PENDIENTES |
| D-10 Sin PC permanente | Piloto S23 PROBADO históricamente | Setup WSL; disponibilidad y reinicio NO VERIFICADOS |
| D-11 Eficiencia | Límites IMPLEMENTADOS | Caché, deduplicar lecturas y medidas de energía PENDIENTES |
| D-12 Fallback | Errores IMPLEMENTADOS | Caché offline con antigüedad PENDIENTE |
| D-13 Gradualidad | Piloto acotado IMPLEMENTADO | MVP documental completo aún PENDIENTE |
| D-14 Free Model Broker | Solo arquitectura | Integración/contexto sin privilegios PENDIENTES |
| D-15 Herramientas comunes | Broker compartido IMPLEMENTADO parcialmente | Voz/teclado/Core reutilizando herramientas PENDIENTES |

## Matriz AC-01–AC-12 del MVP

No se declara aprobado el MVP completo. “PROBADO histórico” se refiere a
registros fechados, no a una nueva consulta a Google.

| Criterio exacto (resumido) | Estado | Evidencia y brecha |
|---|---|---|
| AC-01 Autorizar ≥1 archivo | PROBADO histórico, acotado | OAuth/publicación del 21/10 y Picker 22/10; grants actuales NO VERIFICADOS |
| AC-02 Hallar y mostrar metadata | IMPLEMENTADO / PROBADO parcial | `metadata/list_page`, tests navegador; fixture leído 03/11, no búsqueda general por nombre |
| AC-03 Leer y citar origen | IMPLEMENTADO / PROBADO parcial | `handle(read)` devuelve ID/URL/texto; piloto y fixture histórico. No prueba citas RAG |
| AC-04 No redescargar sin cambios | PENDIENTE | Cada `read` hace media/export; sin cache/revisión |
| AC-05 Cambio invalida índice | PENDIENTE | Sin change tracker ni índice; lectura directa no cumple invalidación |
| AC-06 Edición reversible autorizada | PENDIENTE; publicación alternativa probada | Nueva revisión preserva anterior, no edita original ni ofrece edición general |
| AC-07 Verificar versión modificada | PROBADO parcial | `publish` verifica hash/metadata de archivo nuevo; edición de original PENDIENTE |
| AC-08 Conflicto sin overwrite | PROBADO parcial | Tests human edit/retry; evita mutación. Falta concurrencia de edición in situ |
| AC-09 Offline explícito | IMPLEMENTADO parcial / NO VERIFICADO extremo a extremo | Códigos de error, sin caché; falta ensayo desconexión y mensaje final en UI |
| AC-10 Reinicio sin cursor corrupto/duplicados | PENDIENTE | Test reopen de reserva demuestra retry de publicación; no hay cursor changes ni prueba reboot |
| AC-11 Logs sin secretos innecesarios | PROBADO parcial | Tests OAuth fallos saneados, stderr oculto; auditoría completa de logs/UI PENDIENTE |
| AC-12 Android o límites PC explícitos | PROBADO histórico acotado | S23 publicador/refresh y S25 piloto; setup WSL documentado, autonomía prolongada NO VERIFICADA |

## Discrepancias documentales y fuentes limitantes

Los encabezados operativos de ARCHITECTURE/GOOGLE_DRIVE_RAG todavía mezclaban
preparación inactiva con PASS posterior. HORUS_DRIVE_PUBLISH conservaba como
“vigente” la papelera del 22/10. Se añade precedencia fechada sin reescribir
informes históricos. La tabla histórica del 03/11 en PROJECT_REVIEW precede a
H3 aceptada el 04/11 y no debe interpretarse como un nuevo bloqueo H3.

Muchos result.json, logs y capturas citados por pilotos no están en el clon
público: no se afirman releídos ni se reparan con archivos ficticios. Los relatos
de validación sí están disponibles. No se accedió a cuentas para resolver esas
limitaciones ni se verificó documentación actual de proveedores; esta auditoría
evalúa el repositorio y el contrato congelado, no certifica políticas externas.

## Siguiente incremento funcional mínimo — PROPUESTO

Un **catálogo/cache durable de texto seleccionado, actualizado incrementalmente
bajo demanda**, reutilizando `Drive` y el receptor Termux existente. Sin servicio
nuevo, embeddings, scheduler permanente, nuevas interfaces o edición multiformato.
No es una decisión definitiva ni está implementado por esta auditoría.

Dependencias: selección explícita de un pequeño conjunto de IDs realmente
concedidos por el cliente actual; resolver el mapeo proyecto/raíz y el destino
del publicador como decisiones separadas. No ampliar scopes por conveniencia.
Mantener OAuth en Termux y separar el nuevo catálogo del journal de publicación.

Propuesta de secuencia y aceptación:

1. Leer metadata con versión observada; persistir fileId, pertenencia, hash,
   estado de frescura y bytes inmutables. Segunda lectura estable: **cero media/
   export**, con validación remota y procedencia. No asumir snapshot estable si
   cambian metadatos durante descarga; reencolar y no publicar bytes como vigentes.
2. Bootstrap con token de cambios anterior al inventario y replay posterior.
   Guardar página/trabajos y siguiente cursor juntos en transacción. Tras caída
   en cada frontera, reanudar sin perder cambios ni duplicar versiones.
3. Consumir changes al pedir “actualizar”: descargar solo cambiados, invalidar
   bajas, salida de raíz y permisos; reenumerar subárbol ante movimiento de
   carpeta. No mostrar retenidos revocados. Un listado fallido no autoriza bajas.
4. Offline: conservar último éxito y antigüedad explícita, sin declarar actualidad.
   429/errores transitorios con backoff acotado; cursor rechazado produce
   reconciliación no destructiva, revocación exige acción privada.
5. Pruebas simuladas obligatorias: doble lectura, edición durante descarga,
   paginación, alta/rename/move/delete/revocación, cursor rechazado, red caída,
   replay tras interrupción y límites de bytes. Después, piloto S23 pequeño
   expresamente autorizado, con mediciones de llamadas/bytes/tiempo; sin inferir
   autonomía de 24 h del éxito de una consulta.

Esto aporta AC-04 y una base verificable para AC-05/AC-10 sin construir RAG
prematuramente. Un índice textual por versión queda sujeto a necesidad demostrada; RAG permanece
pendiente de revisión y no es la continuación comprometida de este incremento. No se
dará AC-05 por cumplido hasta comprobar que la recuperación excluye texto obsoleto.

## Verificaciones ejecutadas el 08/11

Bajo `sh tools/work-session.sh start --resume --offline -- bash --noprofile --norc`,
sin fetch ni aplicación remota. Las nueve suites siguientes terminaron con
salida 0, **163 tests, cero fallos y cero omitidos**:

| Comando | Tests |
|---|---:|
| `python3 -B -m unittest discover -s tools/horus_publish -p 'test_*.py'` | 58 |
| `python3 -B -m unittest discover -s tools/s25-codex-client -p test_helpers.py` | 4 |
| `python3 -B -m unittest discover -s tools/s23-remote-access -p 'test_*.py'` | 28 |
| `python3 -B -m unittest discover -s tools -p test_horus_pair_s25.py` | 13 |
| `python3 -B -m unittest discover -s tools -p test_work_session.py` | 40 |
| `python3 -B -m unittest discover -s tools -p test_s23_project.py` | 4 |
| `node --test tools/s25-codex-client/pilot-policy.test.mjs` | 3 |
| `node --test tools/project-gate.test.mjs` | 9 |
| `node --test tools/s23-remote-access/accept_s23.test.mjs` | 4 |

Los 58 incluyen cuatro tests locales no versionados; por ello 163 no reemplaza
la aceptación histórica de 159 por target. Las pruebas usan fixtures/temporales;
ninguna acredita OAuth vivo, publicación disponible ni batería del teléfono.
No se ejecutaron tests Node que requieren upstream reconstruido, compilación
Android ni `prepare_source.py` (también descarga wrapper). Sin dependencias nuevas.

Revisión documental: `git diff --check`, enlaces locales nuevos, cercas Markdown,
huellas de las cinco rutas previas y ADR; diff limitado a documentación.
