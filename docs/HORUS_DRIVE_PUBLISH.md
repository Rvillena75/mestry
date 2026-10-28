# Publicación desde Horus a Drive

**Estado vigente tras el selector Drive, 2026-10-21:** el usuario eligió **MESTRY**
como raíz principal de consulta y completó Picker con el mismo cliente y
`drive.file`. Renovación HTTPS nativa y carpeta no eliminada verificadas. La app
permite activar/desactivar raíces autorizadas, asignarlas por proyecto y consultar
documentos; todavía no hay documentos autorizados visibles en MESTRY. Esto **no
redirige el escritor**: la antigua carpeta Review/Horus y sus pruebas están en la
papelera por decisión del usuario. No se restauraron ni se publicaron documentos
nuevos en este incremento. Los PASS de publicación siguientes son históricos,
anteriores a ese cambio; no presentar el destino antiguo como disponible hoy.
[Entrega actual](validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md).

**Continuación Android, 2026-10-21: PASS.** MESTRY Piloto del S25 invocó este
cliente mediante Codex en Horus. Se confirmó `PUBLISHED_VERIFIED`, revisión 2,
mismo ID y hash, tanto en la salida real de la herramienta leída por otro proceso
app-server como en el journal nativo, que conserva dos filas. El primer intento
recibió HTTP 500; el diagnóstico de lectura y un reintento idéntico pasaron.
[Evidencia actual](validation/mestry-s25-resumed-20261021T154810Z/).

**2026-10-21 UTC: piloto funcional PASS.** El S25 ordenó desde la terminal Horus del S23 una publicación, un reintento idéntico y una segunda revisión. Otra conexión al S23 descargó íntegramente los dos archivos y verificó SHA-256, MIME, ubicación y privacidad. El conector confirmó la metadata por separado y el usuario confirmó lectura de ambos desde S25. La primera revisión conserva sus bytes originales. [Resultado y límites](validation/mestry-horus-drive-live-20261021T040010Z/result.json).

**Cierre OAuth de producción PASS:** el usuario confirmó **En producción** y completó el nuevo consentimiento con el mismo cliente y solo `drive.file`. Otra conexión al S23 verificó refresh token distinto del de Pruebas, renovación HTTPS real, cuenta correcta y lectura íntegra de las dos revisiones privadas, sin publicar archivos nuevos. Copias privadas del token anterior y del de producción `600`; claves originales y restringida intactas; callback `53682` cerrado. [Resultado y límites](validation/mestry-oauth-production-confirmed-20261021T055110Z/result.json). La prueba de más de siete días todavía no transcurrió; Google puede invalidar tokens por otras causas.

**Marca, 2026-10-21:** resuelto el bloqueo por el usuario al completar Google Cloud. Se detectó que las URLs propuestas aún devolvían 404; con aprobación expresa se creó el repositorio y se publicaron [inicio](https://rvillena75.github.io/) y [privacidad](https://rvillena75.github.io/privacy.html). Ambas páginas y CSS coinciden byte a byte con lo revisado y responden 200 por HTTPS. Condiciones vacías, como confirmó el usuario; cuatro archivos públicos, ninguna credencial. [Guía](../tools/s23-publisher-branding/README.md), [prueba HTTPS](validation/mestry-oauth-production-confirmed-20261021T055110Z/website-published-verification.json). El [comando de reautorización](validation/mestry-oauth-production-confirmed-20261021T055110Z/REAUTHORIZE_IN_WSL.sh) se ejecutó correctamente; su verificación nativa se repitió desde otra conexión para el registro independiente.

## Uso instalado

Desde el perfil SSH **horus**, home `/home/horus`, en el S23:

```sh
cd /workspace/projects/mestry-horus-smoke
~/.local/bin/mestry-publish S23_PUBLISH_TEST.md
```

El piloto acepta **solo ese documento**, hasta 64 KiB. El mismo contenido devuelve el mismo archivo; un contenido nuevo crea otra revisión. Si una revisión remota fue editada, no se sobrescribe ni se presenta como una descarga coincidente. Los errores requieren reconciliar el ID existente; no borrar ni cambiar permisos para forzar el resultado.

Destino histórico del escritor, actualmente en papelera: [MESTRY/Review/Horus](https://drive.google.com/drive/folders/DRIVE_FOLDER_01_EXAMPLE), cuenta `owner@example.invalid`.

| Revisión | Enlace | SHA-256 |
|---|---|---|
| 1 | [Primera publicación](https://drive.google.com/file/d/DRIVE_ID_06_EXAMPLE/view?usp=drivesdk) | `0f6b0a0302bac581660a9b059d3773b232ce9c5c2ddf2e6cb86e75b98c0d22c8` |
| 2 | [Segunda publicación](https://drive.google.com/file/d/DRIVE_ID_09_EXAMPLE/view?usp=drivesdk) | `ada9d1e265088e8fae3dfe57e9a229e8e31ebd75ff480a321e70eaa82d8f20a7` |

Ambos archivos son `text/markdown`, 79 bytes. Sus líneas finales son `estado=primera-publicacion` y `estado=segunda-publicacion`. El usuario no identificó la app usada para leerlos; no atribuir el resultado a una interfaz Android Codex nueva ni a un editor concreto.

## Ejecución e identidad

- Horus, UID Android **10350**, conserva el workspace y la clave privada dedicada. El cliente solicita publicar por el SSH Termux existente **8023**, desde loopback.
- Termux, UID **10348**, mantiene OAuth `drive.file`, SQLite y el receptor. No ejecuta Codex. El aislamiento es Android; PRoot no es una frontera de seguridad.
- La clave restringida admite publicación, cliente público y ahora el catálogo fijo
  `mestry-drive-v1` de consulta/selección local. La transferencia temporal de código
  se cierra al retirar el bundle preparado; no admite shell ni forwarding. El S25 verificó rechazo de `whoami` y de un canal SSH de reenvío directo al 8022 existente, sin abrir listeners nuevos. Las claves WSL/S25 anteriores permanecen intactas.
- Cuenta y scope se comprobaron realmente, y el token se renovó por HTTPS **en el S23**. La autorización inicial usó una biblioteca oficial en WSL y el token se transfirió por stdin de SSH; el helper no lo guarda en WSL. El flujo de publicación no usa un proceso del PC.

El cliente se instaló en el perfil SSH Horus, que sigue siendo distinto del
harness integrado de la app Horus. En el piloto inicial no se inició una tarea de
modelo; en la continuación Android se comprobó la invocación desde Codex del
perfil SSH, mediante el bridge privado. No se copiaron historias ni credenciales
entre perfiles para conseguirlo.

## Operación y recuperación

- Código S23: `~/.local/lib/mestry-publish`; estado privado: `~/.local/state/mestry-publish` (directorio 700, credenciales 600). No guardar estas credenciales en Drive, el proyecto o logs.
- Clave exclusiva: `~/.ssh/id_ed25519_mestry_publish` **en Horus**; huella `SHA256:CONFIGURE_LOCAL_FINGERPRINT`. Para revocar, retirar únicamente su línea en `authorized_keys` de Termux, conservando las dos previas y su backup privado.
- Máximo 20 revisiones nuevas por día UTC y 32 totales en este piloto. Ampliar documentos/proyectos requiere seleccionar la política; no convertirlo en acceso libre al workspace o Drive.
- No hay watcher, cron, daemon adicional, sincronización del corpus ni comentarios. Cada petición crea un proceso breve mediante el SSH que ya existe.
- La carpeta nueva se creó en S23. El movimiento inicial a Review falló por error del conector y timeout del PATCH nativo; se verificó el estado antes de pedir al usuario moverla en Drive. El padre final se comprobó por ambos canales. La causa del fallo de movimiento no quedó determinada; no afirmar que fue un rechazo de scopes.
- El antiguo rollback de puertos **no se usa**: Horus ocupa 8022 y Termux 8023. El callback WSL temporal 127.0.0.1:53682 fue aprobado para preparar OAuth; cada intento tiene un máximo de 180 segundos. No pedir otra vez esa misma aprobación al completar este login.

La continuidad con PC físicamente apagado, reposo prolongado, Boot real y
estabilidad 24/7 siguen sin probarse. La app Android S25, recuperación y llamada
al publicador ya pasaron. El corpus, feedback y edición humana automática están
fuera de este piloto.

## Evidencia

[26 tests WSL / 25 S23 y un omitido](validation/mestry-horus-publish-20261021T033650Z/result.json) usaron API simulada; son distintos de estas operaciones reales:

1. [Cuenta, scope, refresh nativo y carpeta propia](validation/mestry-horus-drive-live-20261021T040010Z/r01_native_auth_refresh_and_private_folder.stdout.txt).
2. [Claves previas y restricciones registradas](validation/mestry-horus-drive-live-20261021T040010Z/r04_native_folder_ready_and_key_restrictions.stdout.txt), [salida del bootstrap S25](validation/mestry-horus-drive-live-20261021T040010Z/bootstrap-s25-user-output.json).
3. [Dos revisiones descargadas y verificadas después de la segunda publicación](validation/mestry-horus-drive-live-20261021T040010Z/r06_two_revisions_final_readback.stdout.txt), [metadata del conector](validation/mestry-horus-drive-live-20261021T040010Z/cloud-publication-metadata.json).
4. [Lectura S25 confirmada por el usuario](validation/mestry-horus-drive-live-20261021T040010Z/s25-review-user-confirmation.json).

[Código y configuración de referencia](../tools/horus_publish/README.md). Fuentes oficiales: [Drive scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth), [OAuth/audiencia y caducidad en pruebas](https://support.google.com/cloud/answer/15549945?hl=es), [OAuth escritorio](https://developers.google.com/identity/protocols/oauth2/native-app).
