# Marca OAuth de MESTRY S23 Publisher

**Estado del 21-10-2026: producción, web y reautorización completadas; refresh nativo y lectura Drive PASS.** Producción confirmada por el usuario; después ejecutó el asistente privado. Otra conexión SSH al S23 verificó un refresh token distinto del de Pruebas, renovación real con Google y descarga íntegra de ambas revisiones privadas. Con aprobación expresa se creó [Rvillena75/Rvillena75.github.io](https://github.com/Rvillena75/Rvillena75.github.io). [Inicio](https://rvillena75.github.io/) y [privacidad](https://rvillena75.github.io/privacy.html) responden 200 por HTTPS y coinciden byte a byte con el contenido revisado. Se conserva cliente de escritorio, solo `drive.file`, claves y puertos. Callback `127.0.0.1:53682` cerrado y sin cambios. [Resultado y límites](../../docs/validation/mestry-oauth-production-confirmed-20261021T055110Z/result.json).

## Diagnóstico y solución mínima

El mensaje «completar la configuración ... de la marca» indica que la consola no considera completa la marca; no identifica el campo ni demuestra que falte una web. La primera comprobación es guardar nombre, asistencia y contacto del desarrollador. Son los datos básicos de la [configuración de consentimiento](https://developers.google.com/workspace/guides/configure-oauth-consent).

No se puede asegurar que esos tres datos basten para publicar hoy: la ayuda [Manage OAuth App Branding](https://support.google.com/cloud/answer/15549049?hl=en) exige enlaces de la aplicación para aplicaciones externas en producción. La exención de revisión por uso personal no elimina automáticamente la validación de marca. Por eso se prepara una web real como alternativa, pendiente de la comprobación en la consola y de autorización para crear el repositorio público.

| Campo | Valor o decisión |
| --- | --- |
| Nombre | `MESTRY S23 Publisher` |
| Correo de asistencia | `owner@example.invalid`, seleccionado en el desplegable |
| Contacto del desarrollador | `owner@example.invalid` |
| Logotipo | No añadir: no es necesario para el funcionamiento |
| Página principal, si se requiere | `https://rvillena75.github.io/` |
| Política de privacidad, si se requiere | `https://rvillena75.github.io/privacy.html` |
| Dominio autorizado para esos enlaces | `rvillena75.github.io` (sin esquema ni ruta) |
| Condiciones | Omitir inicialmente; usar `https://rvillena75.github.io/terms.html` solo si la consola las exige y se publica la alternativa |

**Condiciones del servicio:** la [guía de verificación de marca](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification) las describe expresamente como opcionales; la nota general de la ayuda de marca agrupa los tres enlaces como obligatorios. No hay base consistente para afirmar que son obligatorias en este caso. `optional/terms.html` es una alternativa local; no forma parte del sitio inicial.

## Qué verificación corresponde

[`drive.file`](https://developers.google.com/workspace/drive/api/guides/api-specific-auth) es un scope recomendado y no sensible. Usar solo permisos no sensibles no exige la revisión OAuth completa, según el [centro de verificación](https://support.google.com/cloud/answer/13463073?hl=en). Google también contempla una [exención para uso personal](https://support.google.com/cloud/answer/13464323?hl=en). No se necesita una evaluación anual de scopes restringidos para este único permiso.

Publicar la aplicación en **Público → En producción**, verificar la marca y pulsar **Publicar marca** son acciones distintas. La revisión de marca permite mostrar nombre/logotipo. No se pedirá verificación adicional si la consola permite publicar sin ella; si aparece como bloqueo, se revisarán sus requisitos concretos, conservando el cliente y el permiso.

## GitHub Pages y propiedad del dominio

El conector GitHub confirmó la cuenta `Rvillena75` y la ausencia inicial del sitio de usuario. Después de recibir autorización expresa del propietario se creó el repositorio público y se publicaron exactamente los cuatro archivos de `site/`. Un segundo acceso por el conector corroboró el árbol público. Commit: `128b2279c92698dc5df100504df8b3674a375ff3`.

[GitHub Pages](https://docs.github.com/en/pages/quickstart) admite el subdominio de la cuenta, sin comprar dominio. Se escoge un sitio de usuario en la raíz para poder publicar un archivo de verificación de propiedad en ella. No se reutiliza ni altera ningún otro proyecto.

Google utiliza el dominio registrable o *top private domain*. La [Public Suffix List](https://publicsuffix.org/list/public_suffix_list.dat) incluye `github.io`; por tanto, se infiere que el dominio apropiado es **`rvillena75.github.io`**, no `github.io`. El usuario confirmó que pudo pasar a producción con inicio/privacidad propuestos y condiciones vacías. La publicación y control del sitio mediante GitHub están comprobados; no se ha acreditado propiedad en Search Console ni se afirma haber completado verificación de marca Google.

Si Google exige acreditar propiedad, usar [Search Console](https://search.google.com/search-console/welcome), con la misma cuenta propietaria/editora del proyecto, y una propiedad **Prefijo de URL** `https://rvillena75.github.io/`. Verificar mediante el archivo HTML proporcionado por Google en la raíz o mediante su etiqueta HTML. No usar una propiedad Dominio que requiera cambiar DNS de `github.io`. Google documenta ambos métodos para [propiedades de prefijo de URL](https://support.google.com/webmasters/answer/9008080?hl=en). Mantener la prueba publicada: Google la vuelve a comprobar. Ese marcador es una prueba pública de propiedad, distinta de las credenciales OAuth; nunca se publicarán estas últimas.

## Contenido publicable y configuración

La carpeta `site/` es el único conjunto inicial publicable:

```text
.nojekyll
index.html
privacy.html
styles.css
```

Páginas estáticas sin dependencias, fuentes remotas, formularios, scripts ni analítica propia. La política describe el acceso real a Drive, la verificación de cuenta/privacidad/integridad, tokens y registro local, el asistente WSL, conservación, revocación y alojamiento en GitHub. No publica correos personales, IDs de archivos, rutas privadas, claves ni credenciales.

Configuración activa comprobada por API: **Deploy from a branch → main → /(root)**, con HTTPS obligatorio. `pages-config.json` es configuración local y no se publicó. Con `.nojekyll` no se necesita generador ni un workflow propio. La petición de creación de Pages devolvió un resultado no exitoso; un GET posterior corroboró que Pages ya existía y estaba construido. La causa exacta de aquella respuesta no se determinó y no se atribuye a permisos.

No subir el directorio del proyecto MESTRY, `docs/validation`, este README, `pages-config.json`, el JSON OAuth, `.ssh`, `.env`, la base de datos ni el estado de Termux. La publicación debe copiar únicamente la lista anterior. Para incluir condiciones, copiar `optional/terms.html` como `terms.html` y enlazarlo desde inicio y privacidad antes de publicar esa revisión.

## Paso posterior en Google Cloud

1. **Completado por el usuario:** [Público](https://console.cloud.google.com/auth/audience?project=mestry-s23-publisher) muestra **En producción**, según su confirmación. No se leyó ese estado mediante una API de Google Cloud. La consola permitió publicar antes de que existieran las páginas; no equivalía a comprobarlas ni prueba que basten tres campos sin URLs.
2. **Completado:** sitio publicado tras autorización, inicio/privacidad/CSS descargados por HTTPS y comparados byte a byte; árbol remoto limitado a cuatro archivos. Las condiciones siguen vacías y no se publicaron.
3. **Completado:** el usuario ejecutó el [comando de reautorización](../../docs/validation/mestry-oauth-production-confirmed-20261021T055110Z/REAUTHORIZE_IN_WSL.sh) en su propia terminal y confirmó «listo». No se registraron el enlace, código ni respuesta OAuth.
4. **Completado por otra conexión SSH:** mismo cliente/scope/cuenta, refresh token distinto de ambas copias anteriores, renovación HTTPS real en Termux y lectura íntegra de ambas revisiones privadas. SHA-256, MIME, ubicación y permisos conservados. Callback cerrado. La verificación de marca/Search Console solo se abordará si Google la requiere; no se afirma haberla completado.

## Token, recuperación y comprobación en el S23

Se conservaron tres copias en el estado privado de Termux, todas `600`: `token.before-production.20261021T043657Z.json`, `token.pre-reauth.20261021T055110Z.json` y `token.production-verified.20261021T061015Z.json`. La última coincide byte a byte con el activo después de su renovación real. Las anteriores permiten reconciliar esta transición; mantienen las limitaciones de su autorización emitida en Pruebas. No se transfirieron valores fuera del teléfono. [Respaldo inicial](../../docs/validation/mestry-oauth-production-20261021T043506Z/r01_private_token_backup.stdout.txt), [comprobación final](../../docs/validation/mestry-oauth-production-confirmed-20261021T055110Z/r05_final_readonly_preservation_check.stdout.txt).

El [comando nuevo](../../docs/validation/mestry-oauth-production-confirmed-20261021T055110Z/REAUTHORIZE_IN_WSL.sh) archiva el activo privadamente bajo el bloqueo del publicador, invoca el [asistente existente](../../docs/validation/mestry-horus-oauth-client-20261021T035330Z/AUTHORIZE_IN_WSL.sh) y verifica desde Termux. Si se cancela o falla antes de completar la importación, intenta recuperar el token archivado **solo si no hay activo**, conservando la copia independiente. Si se pierde también SSH o se interrumpe abruptamente el PC, el [script de recuperación](../../docs/validation/mestry-oauth-production-confirmed-20261021T055110Z/REAUTH_TOKEN_RESTORE_IF_EMPTY.sh) queda disponible para reconciliar el estado sin sobrescribir un activo. Una vez importado un token nuevo, un fallo de lectura posterior no lo sustituye por el anterior.

No ejecutar el asistente en el registrador de comandos ni guardar su enlace, código o respuesta OAuth. El callback se mantiene exactamente como estaba aprobado. Seis fixtures offline comprobaron archivo/recuperación, preservación de un activo nuevo, rechazo de colisiones, scopes distintos y symlinks; no representan una autorización Google real ni acreditan aislamiento Android. El [preflight nativo](../../docs/validation/mestry-oauth-production-confirmed-20261021T055110Z/r01_native_reauth_preflight.stdout.txt) confirmó activo/copia `600`, cliente/scope idénticos y UID real, sin cambiar el token.

Comprobado desde Termux a las **06:07:06 UTC del 21-10-2026**: cliente existente, permiso exacto, cuenta correcta, renovación HTTPS real y lectura/verificación de las dos revisiones publicadas. No se generó ni compartió otro documento de prueba. El wrapper de esta transición es de un uso: no repetirlo con una autorización ya válida, porque conserva y protege su archivo previo.

**Persistencia no significa permanencia.** Google documenta [caducidad de refresh tokens](https://developers.google.com/identity/protocols/oauth2#expiration): siete días en Pruebas con Drive; también revocación, seis meses sin uso, límite de tokens y acceso concedido por tiempo limitado, entre otras causas. La nueva autorización se emitió después de la confirmación de producción y ya renovó correctamente. Ocho días de continuidad todavía no transcurrieron: una comprobación después de **2026-10-29 06:08 UTC** cubriría ese intervalo. No se programó ninguna tarea nueva.

El publicador renueva access tokens antes de expirar y devuelve `OAUTH_REFRESH_FAILED_REAUTHORIZE_PRIVATELY` si falla. Si se pierde el archivo activo sin revocarse el permiso, la copia privada de producción permite recuperación controlada. Si Google invalida el refresh token, una copia del mismo no lo vuelve válido: se prepara otra transición con un nombre nuevo de archivo y se vuelve a autorizar privadamente el mismo cliente. **No revocar la autorización anterior para forzar la rotación:** la revocación puede afectar al permiso del proyecto y a la autorización nueva. Las copias anteriores se conservaron; no se afirmó su validez indefinida.
