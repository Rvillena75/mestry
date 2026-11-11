# Lector Drive de sólo lectura — autorización del 08/11/2026

El usuario **autorizó expresamente** `drive.readonly` para el lector,
con sincronización limitada por código a MESTRY y sus descendientes.
No se autoriza escritura general ni se modifica el ADR congelado.
El consentimiento interactivo de Google es una etapa distinta:
**COMPLETADO y VERIFICADO** en el S23. El lector nuevo está activo.

## Implementación y límites de autoridad

`document_reader.py` conserva el publicador en `publisher.Drive`, su token
`token.json` y scope `drive.file`. El lector usa una capacidad separada
`ReaderDrive`, token `reader/token.json` y activación `reader/selection.json`,
bajo el estado privado Termux existente. No se crea otro cliente OAuth ni se
copian tokens al repositorio, Horus o WSL.

Sólo se admite el scope exacto `drive.readonly`; un token con escritura o
scopes adicionales se rechaza. El transporte lector rechaza POST/PATCH/upload
y asignación de IDs antes de hacer HTTP. La cuenta y el cliente existentes se
validan nativamente. Los tokens permanecen JSON privados 600, no cifrado
aplicativo Keystore.

Google concede lectura de todos los archivos accesibles a esa cuenta.
**El límite MESTRY es de aplicación, no una frontera OAuth por carpeta.**
La selección activa contiene un único ID raíz. El selector sólo presenta esa
raíz; no enumera todas las carpetas del Drive amplio ni permite habilitar otra.
Desactivar y reactivar esa raíz sigue siendo control local.

La API de cambios es de cuenta: el sincronizador descarta cambios de archivos
no relacionados antes de persistirlos. El inventario sólo recorre la raíz
seleccionada. Los archivos antiguos se incluyen mediante reconciliación inicial;
los nuevos se descubren al actualizar. Movimientos fuera de raíz, bajas y
revocación siguen invalidando recuperación normal. No se siguen shortcuts para
ampliar el alcance ni se afirma cobertura de Shared Drives.

La actualización continúa siendo **bajo demanda**, con los límites de tamaño,
formatos y presupuesto de [DOCUMENT_SYNC](DOCUMENT_SYNC.md). Autorizar un
documento no implica que este incremento pueda extraer cualquier formato.
Google puede revocar credenciales o el propietario puede retirar acceso;
“todos” no equivale a un permiso irrevocable.

## Consentimiento y activación

`authorize_reader_wsl.py` se ejecuta sólo en una terminal privada del usuario:

1. Obtiene por SSH estricto el cliente existente y la raíz seleccionada.
   Esos datos quedan en memoria del helper, sin archivos OAuth WSL.
2. Usa biblioteca oficial, PKCE y callback existente
   `127.0.0.1:53682`, máximo 180 segundos, sólo `drive.readonly`,
   `include_granted_scopes=false`. El enlace se muestra únicamente en esa terminal.
3. Transmite el token al S23 por stdin. El S23 verifica scope/cliente/cuenta,
   renovación real del lector y renovación de `drive.file` del publicador
   en memoria. No sustituye el token del publicador.
4. Con locks, valida que la selección no cambió, fuerza reconciliación del
   catálogo y escribe el marcador de activación al final. Cancelación o fallo
   anterior conserva el lector existente. Un lector ya configurado no dispara
   un nuevo consentimiento automáticamente.

Comando privado preparado:

```sh
"$HOME/.local/share/mestry-publish-setup/venv/bin/python" -B \
  tools/horus_publish/authorize_reader_wsl.py \
  --allow-loopback-53682
```

El launcher privado es
`~/.local/state/mestry-reader-setup/run-reader-authorization.sh`.
El recibo WSL `~/.local/state/mestry-reader-setup/result.json` contiene sólo
estado/códigos y verificaciones; no URL OAuth, cliente, código ni token.
No ejecutar el helper mediante herramientas de chat, tee o registradores.

## Pruebas y despliegue del código

**211 tests WSL**, nueve suites, todos correctos, con
`sourceInputsUnchanged=true`. Huella de herramientas:
`d6a48824a39bc1d50387075f4d24aa083b0ec08649b65d770dc0c7587bcee344`.
El grupo documental tiene 106 tests, incluidos los cuatro auxiliares locales previos.

**68 tests de candidata S23 ARM64**, sin fallos: 35 de sync, 20 del navegador y
13 de lector/consentimiento. Casos nuevos: scopes exactos, cliente incorrecto,
operaciones de escritura bloqueadas, raíz no seleccionada, conservación del
token escritor, cancelación/fallo antes de activar, PKCE y descarte de cambios
ajenos al catálogo.

Código preparado en S23 con copia privada `reader-code-backup-*`.
La activación del código preservó publisher, configuración, cliente, token,
selección del navegador, journal y claves. Antes del consentimiento el factory conservó `drive.file`. Después se verificó
`READER_AUTHORIZED`, scope exacto `drive.readonly`, renovación HTTPS nativa de
ambos grants y conservación byte a byte del token del publicador.

Hashes preparados:

| Archivo | SHA-256 |
|---|---|
| document_reader.py | 084f8bfe72e5413450ff45aca8b474786a9d20e326817589424e2dc9d1db40e0 |
| drive_sync.py | e327d352603d0eee42dd6d3a1a25a0f9b5b9a1fd3496d5e53ca8f5ce98ce8550 |
| document_sync.py | 76493ad473850f872561be5b288acdf1a7b86003b73b40f169f2a48e5809a364 |
| navegador privado preservado + integración | cb1f8a02dafbf1c0f4b30c2a5445a99e67be583e997ccf87a01964aded6f9465 |

No se crean o editan archivos de Drive. La primera comprobación real descubrió
99 elementos de MESTRY y verificó texto con versión remota, segunda lectura con
**0 llamadas media/export**, mismo SHA-256 y lectura offline señalizada. El
selector presentó sólo la raíz fijada. Una raíz de prueba ajena se rechazó antes
de consultar Google. No se exportó contenido privado al chat.
El inventario inicial sigue por lotes; su progreso no equivale a caché completo.
La validación visual S25 y cambios humanos reales siguen pendientes.

Durante el consentimiento, un sondeo TCP de diagnóstico consumió la conexión
única del callback y provocó ERR_CONNECTION_REFUSED al llegar el navegador.
Se dejó de sondear ese puerto, se comprobó Windows→WSL con un listener de prueba
separado y el nuevo consentimiento terminó correctamente. No sondear callbacks
OAuth activos; observar sólo el recibo seguro.

El procesamiento por lotes no incrementa intentos/backoff cuando sólo se agotó
su tiempo. La corrección tiene prueba de regresión. Se conservaron copia
consistente de la base derivada y del módulo anterior; 65 jobs no iniciados
quedaron de nuevo disponibles sin alterar documentos ni tokens.

Fuentes oficiales consultadas:
[scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth)
y [OAuth de escritorio y PKCE](https://developers.google.com/identity/protocols/oauth2/native-app).

## Desactivación controlada

Para volver al lector anterior, conservar el token nuevo y mover el marcador
`reader/selection.json` a una copia privada bajo los locks y sin operaciones
en curso. El factory utilizará de nuevo `drive.file`; no se ejecutó ese rollback.
La concesión Google y la activación local son cosas distintas. No revocar
automáticamente el cliente compartido como rollback, pues también sirve al
publicador. No se trasladan credenciales entre cuentas ni se cambia el ID raíz.

## Último checkpoint de carga inicial — 08/11/2026 07:07 UTC

El trabajador acotado terminó con salida 0; no quedó un proceso de carga
separado en segundo plano. Checkpoint persistido:

| Métrica | Valor |
|---|---:|
| Elementos catalogados (archivos y carpetas) | 3.992 |
| Representaciones textuales listas | 7 |
| Aperturas externas clasificadas | 7 |
| Trabajos de recuperación pendientes | 3.216 |
| Errores de jobs registrados | 0 |
| Inventario aún en recorrido | Sí |
| Feed de cambios recibido hasta el final | No |

La autorización recursiva sí está activa. **La carga inicial completa y la copia
offline de todo el corpus no se dan por terminadas.** Nuevas llamadas del
navegador/CLI continúan desde estos checkpoints. No se añadió un scheduler.
Los límites vigentes son 5.000 nodos y 16 MiB de objetos por raíz; si el corpus
los alcanza, debe informarse y revisar tamaño/selección antes de prometer cobertura.
La comprobación de contenido real no reemplaza una edición humana concurrente
o prueba de reinicio Android; esas aceptaciones siguen pendientes.
