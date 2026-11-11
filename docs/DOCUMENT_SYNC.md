# Sincronización incremental y recuperación documental

**Ampliación autorizada por el usuario — 08/11:** lector separado con
`drive.readonly` activo; consentimiento Google y renovación nativa verificados.
El publicador conserva `drive.file`. [Estado de autorización](DOCUMENT_READER_AUTH.md).
Los resultados y hashes siguientes corresponden al incremento previo.

Estado del **08/11/2026**: backend implementado y activado en Termux/S23.
Aceptación del contenido real y de la UI S25 **PENDIENTE**. RAG continúa
**PENDIENTE DE REVISIÓN** y no participa en este incremento.

La autorización de desarrollo de sincronización posterior a la auditoría permite
este incremento H4. No cambia D-01–D-15, no cierra H4 completo ni H5, no redirige
el publicador y no añade permisos, servicios o dependencias.

## Recorrido y piezas implementadas

- `tools/horus_publish/drive_sync.py`: adaptador GET de Drive, catálogo SQLite,
  objetos por SHA-256, versiones, jobs, inventario y cursor de cambios.
- `drive_browser.py::cached_handle`: conserva el contrato del bridge. Listar
  online actualiza el corpus seleccionado en lotes; leer verifica metadatos,
  pertenencia y versión antes de reutilizar bytes. No necesita turno de modelo.
- `document_sync.py`: CLI privada para sync/status/list/read/history/clear y
  reconciliación explícita. La selección existente del navegador sigue vigente.
- `install.py`: incluye los dos módulos nuevos en una instalación inicialmente
  inactiva; conserva el rechazo a restage automático de una instalación activa.

La actualización es **bajo demanda**, al listar desde el navegador o ejecutar
sync. No se añadió cron, WorkManager, webhook ni sincronización periódica.
Una lectura focalizada comprueba el archivo solicitado sin inventariar todo Drive.

## Persistencia, consistencia y recuperación

Cada cuenta/raíz tiene una base independiente en Termux:
`~/.local/state/mestry-publish/documents/<hash-cuenta-raíz>/documents.sqlite3`.
El hash del namespace no cifra el contenido. Directorios 700 y archivos 600,
validación de dueño y symlinks; OAuth sigue en el runtime existente de Termux.

Tablas: `config` (identidad, cursor, generación y estado), `nodes` (metadatos,
firma remota, disponibilidad y digest activo), `objects` (bytes), `versions`
(archivo/versión/hash), `jobs` (intentos, error y próximo reintento) y `scans`
(carpeta, página y estado). No se modifica el journal del publicador.

SQLite usa transacciones, synchronous FULL y journal DELETE. Bytes, versión y
puntero activo se publican juntos en la misma base: no queda un puntero a un
objeto todavía no escrito. Esto evita el problema de coordinar SQLite con un
segundo almacén de archivos. El lock documental serializa los procesos que usan
la misma raíz; no se sincroniza la base activa por Drive/FolderSync.

Bootstrap: obtener startPageToken **antes** del inventario; persistirlo con
trabajos de exploración; recorrer hijos con paginación durable; consumir después
los cambios concurrentes. Cada página de changes avanza su cursor junto con la
cola e invalidaciones en una misma transacción. Se distingue recepción de cambios,
inventario pendiente, descargas pendientes y último éxito completo.

Una interrupción reanuda las páginas/jobs persistidos. Un token changes rechazado
con 410 inicia reconciliación conservando objetos. Un cursor de inventario
rechazado con 400 reinicia esa carpeta sin autorizar bajas por el fallo.
Inventario incompleto o fallido no produce bajas masivas.

Cambios de archivo revalidan pertenencia y descargan sólo cuando cambia la firma
remota o faltan/corrompieron los bytes. Movimientos de carpetas provocan un nuevo
inventario de **metadatos de la raíz seleccionada**, porque no se presume recibir
eventos de todos sus descendientes. Esto conserva corrección, con más coste que
un futuro grafo optimizado. No se re-descargan los documentos estables.

Bajas, papelera, salida de selección y pérdida de acceso observada retiran el
contenido de consulta normal. Una raíz revocada bloquea todo su caché, incluso
offline. La revocación de un ancestro invalida conservadoramente las copias
afectadas; la reconciliación determina de nuevo la pertenencia.

## Lectura, caché e historial

Se recupera texto UTF-8, Markdown, JSON/XML y exportación textual de Google Docs.
La segunda lectura con versión estable no repite media/export. Metadatos y
ascendencia se consultan de nuevo; bytes y metadatos se contrastan después de una
descarga para detectar edición concurrente. Sin versión remota no se habilita
la reutilización estable de bytes.

Una lectura online devuelve versión, hash y fecha de comprobación.
Una caída transitoria permite la última copia válida con
`offline=true`, `freshness=cached_unverified` y un aviso dentro del texto,
visible también para clientes que ignoren los campos nuevos. No hay fallback
automático ante rechazo de permisos. No se considera el caché una autorización
permanente.

Las versiones conservadas pueden listarse y recuperarse como
`historical_snapshot`; no sustituyen el archivo actual ni se suben a Drive.
Las versiones de un documento revocado/dejado fuera de selección tampoco quedan
disponibles por el historial normal. Si se detectan bytes corruptos, una lectura
online vuelve a descargarlos; no fabrica contenido vacío.

Límites del incremento: 64 KiB por representación textual, 16 MiB de objetos por
raíz y 5.000 nodos. Un documento demasiado grande, inválido como UTF-8 o de otro
formato queda como apertura externa. El presupuesto agotado queda como error/job
pendiente; no se borran automáticamente versiones para hacer sitio.
`clear` vacía únicamente derivados locales de esa raíz, sin tocar Drive.

## Operación privada

En Termux, con el código y OAuth existentes, usando IDs ya autorizados.
Estos comandos pueden mostrar texto privado: ejecutarlos en terminal propia,
sin redirigir contenido a registros públicos.

```sh
python -B ~/.local/lib/mestry-publish/document_sync.py status --root-id ID_RAIZ
python -B ~/.local/lib/mestry-publish/document_sync.py sync --root-id ID_RAIZ
python -B ~/.local/lib/mestry-publish/document_sync.py read --root-id ID_RAIZ --file-id ID_ARCHIVO
python -B ~/.local/lib/mestry-publish/document_sync.py read --root-id ID_RAIZ --file-id ID_ARCHIVO --offline
python -B ~/.local/lib/mestry-publish/document_sync.py history --root-id ID_RAIZ --file-id ID_ARCHIVO
python -B ~/.local/lib/mestry-publish/document_sync.py read --root-id ID_RAIZ --file-id ID_ARCHIVO --version VERSION
python -B ~/.local/lib/mestry-publish/document_sync.py sync --root-id ID_RAIZ --reconcile
```

El vaciado local explícito utiliza la acción `clear`; no se ejecutó contra los
datos del usuario. Los lotes tienen presupuesto de páginas/jobs y tiempo de
llamadas; repetir sync permite avanzar. HTTP transitorio/429 tiene reintentos
acotados con jitter; los jobs fallidos conservan backoff durable.
Un 401/403 no se reintenta ciegamente ni amplía scopes.

## Evidencia del 08/11

- **WSL: 196 tests**, nueve suites, salida 0. Incluyen 33 casos nuevos del motor
  y su integración, además de los cuatro auxiliares locales previos.
  `sourceInputsUnchanged=true`; huella de entradas de herramientas:
  `824f5efc1dbf1196e86bdaab640a82b3048b54ef8a5b224eb36e7600e2f7b5be`.
- **S23 ARM64: 53 tests de candidata**, salida 0, sin ResourceWarning:
  33 del incremento y 20 del navegador. Pruebas sintéticas en directorio privado
  aislado, sin escrituras Google.
- Casos cubiertos: bootstrap con cambio concurrente, paginación, replay tras
  reapertura, transacción de página interrumpida, edición durante descarga,
  altas/bajas/movimientos, revocación de raíz/ancestro, caché corrupto, historial,
  límites, backoff y aviso offline usando el contrato existente.
- **Drive real/S23:** cuenta verificada con configuración existente; inventario,
  startPageToken, changes y cursor durable completados. Dos entradas al navegador
  en procesos nuevos pasaron y el listado CLI offline pasó. Después de la
  actualización final se volvió a completar sync con el motor instalado.
- La raíz habilitada devuelve **0 documentos visibles**: no se acredita descarga
  real, cache hit real ni detección de una edición humana. No se crearon archivos
  remotos para rellenar la prueba. Scope/concesiones individuales siguen siendo
  `drive.file`.
- Activación reversible bajo locks del navegador/publicador, módulos nuevos
  primero y navegador al final; sin reinicio de servicios. Se preservaron
  publisher, configuración, cliente OAuth, token, selección, journal y claves
  durante la activación. El refresh ordinario puede actualizar el token después.
  No se copiaron credenciales a WSL.

Hash del motor final instalado y del archivo local:
`a2fc0b6ff2ec4dc1092594c0960b607e32dc221b03be6ac1b73f95871a2cd678`.

El navegador instalado conserva su base privada y añade la integración revisada;
no se reemplazaron sus constantes con ejemplos públicos. Hash de ese overlay:
`ff7a37992656bf80fce39775ceed5641ed5cf9cb04736b3cf28c15ba83c23023`.

Rollback: conservar la base derivada y, con el broker sin operaciones y sus locks
adquiridos, restaurar la copia privada original de `drive_browser.py` del
directorio `document-sync-backup-*` en el estado Termux. Los módulos nuevos
quedan sin invocación por el navegador original. Para revertir sólo el último
ajuste de motor existe `document-sync-engine-backup-*`. No reautorizar OAuth,
borrar originales, reinstalar ni reutilizar el instalador histórico como rollback.

## Alcance pendiente y criterios AC

AC-04 (no redescarga), AC-09 (caché offline) y recuperación del estado de AC-10
tienen **IMPLEMENTACIÓN + PRUEBAS SINTÉTICAS**, no aceptación completa con Drive
real y reinicio Android. AC-05 tiene invalidación de catálogo/caché probada;
no se afirma invalidación de un índice RAG inexistente.
AC-06–AC-08 de edición de originales no cambian por este lector.

“Recuperación completa” aquí cubre el recorrido del texto soportado: descubrir,
sincronizar, conservar, reabrir, verificar, recuperar offline y consultar versiones.
**No significa cobertura universal de formatos ni cierre extremo a extremo.**
PDF/Office/Sheets/Slides no tienen extracción/caché binaria en este incremento.
Tampoco se aceptan Shared Drives, reboot/corte eléctrico, autonomía 24/7,
cifrado aplicativo Keystore, retención automática o backend restaurado desde una
base físicamente ilegible. SQLite corrupto exige preservar la evidencia y una
reconstrucción controlada desde Drive; no se borra automáticamente.

La UI S25 y su reconexión offline necesitan prueba con el teléfono. El selector
de raíces todavía consulta Google y no ofrece descubrimiento offline completo;
la CLI sí permite recuperar directamente un ID previamente cacheado. La
indisponibilidad de OAuth durante un refresh se trata de forma conservadora.
Se necesita al menos un documento de prueba realmente concedido a este cliente
para aceptar el flujo de contenido real. No se modifica la selección ni OAuth
sin esa información.

## Solicitud inicial de acceso recursivo — antecedente previo a la autorización

Este apartado conserva la propuesta previa al consentimiento. La autorización
posterior y su implementación vigente constan en [DOCUMENT_READER_AUTH](DOCUMENT_READER_AUTH.md).

Google documenta `drive.file` como acceso por archivo elegido/abierto con la app;
no es una concesión recursiva para todos los descendientes de una carpeta.
`drive.readonly` permite ver y descargar todos los archivos de Drive accesibles
a la cuenta. No existe en esa lista de scopes un permiso limitado a una carpeta.
[Scopes oficiales, consultados el 08/11/2026](https://developers.google.com/workspace/drive/api/guides/api-specific-auth).

Propuesta concreta pendiente de consentimiento: añadir autorización **sólo de
lectura** para el lector documental, con token privado separado del publicador.
El sincronizador seguiría limitado por ID a la raíz MESTRY y descendientes,
incluidos los que se incorporen después. El publicador conservaría su token,
scope y destino; no se amplía su capacidad de escritura.

La selección por raíz es una restricción de la aplicación: Google sí concedería
lectura más amplia. Antes de activar el lector habría que comprobar cuenta,
scope efectivo, conservación del publicador y exclusión de archivos externos.
No se promete acceso si el propietario revoca permisos o la autorización caduca.
La ampliación no está implementada ni autorizada por inferencia; se solicita
confirmación explícita de ese alcance.
