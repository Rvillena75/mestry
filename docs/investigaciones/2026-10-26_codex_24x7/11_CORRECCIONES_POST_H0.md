# MESTRY — Correcciones posteriores a H0

Fecha: **27/10/2026**, America/Santiago, UTC−03:00. Continuación del [cierre H0](DRIVE_ID_01_EXAMPLE.md), sin modificar ese registro histórico ni el ADR congelado.

## Resultado de la intervención

**Correcciones S23 completadas. GitHub y la autenticación ChatGPT están configurados en la ficha nativa Codex; Horus remoto responde y el bridge MESTRY quedó recuperado con su supervisor. FolderSync pasó una subida, una descarga con SHA-256 idéntico, la prueba de filtros y la sincronización completa del par principal: `SyncOK`, 76.353 archivos comprobados, 0 transferidos y 0 eliminados, duración 34m 35s.**

Se reactivó únicamente el horario del par principal, al **minuto 17 de cada hora**, próxima ejecución mostrada **27/10 19:17**; la propagación de borrados continúa **desactivada**. El par sintético queda pausado y excluido de «Sincronizar todo». La depuración temporal está desactivada y el ajuste USB de pantalla se restauró a su valor original **0**. Se conservan ambas copias de una antigua carpeta PostgreSQL conflictiva, excluida por su ruta exacta; no se afirma que estén reconciliadas ni sean respaldos restaurables. El circuito completo desde el cliente S25 queda fuera de estas pruebas.

El laboratorio H1 puede conservar el perfil `/home/horus` elegido previamente. La ficha `/home/harness_codex` ya dispone además de su propio login GitHub y helper probado para lectura. No se necesita compartir credenciales entre ellos. No se inició H1 ni se probó publicación.

## Alcance y autorizaciones

El usuario pidió corregir las incidencias de FolderSync, Horus remoto y la ficha Codex. Informó que ya había habilitado Horus remoto. Durante la intervención autorizó expresamente:

1. Pausar el par `S23 <> Google Drive`, cancelar su ejecución y desactivar la propagación de borrados.
2. Forzar la detención únicamente de FolderSync y volver a abrirla, conservando datos y configuración.
3. Desvincular y volver a vincular la misma cuenta Drive dentro del registro de cuenta existente. El usuario completó el acceso de Google en el S23 y confirmó su regreso a FolderSync.
4. Iniciar sesión GitHub y configurar su helper Git en la ficha Codex, **sin copiar credenciales entre perfiles**.
5. Después de explicar la consulta rápida, el usuario autorizó **«todos los ajustes y pruebas necesarias en el S23»**. Esta ampliación cubre las correcciones siguientes; no se interpreta como implementar H1, publicar proyectos, alterar la arquitectura congelada o descartar documentos.

Las inspecciones y acciones se dirigieron al **S23 SM-S918B**, serial conocido y modelo revalidado en cada operación ADB. Se reutilizó el servidor ADB Windows existente. El S25 no es necesario para estas correcciones; su prueba como cliente remoto queda separada.

## FolderSync: acciones ejecutadas y evidencia

| Elemento | Resultado observado |
|---|---|
| Programación del par al iniciar el diagnóstico | Pausada. La interfaz cambió de `Desactivar` y próxima ejecución a **`Activar` / `No programado`**; se reactivó al finalizar las pruebas correctas, como se acredita abajo |
| Propagación de borrados | **`Sincronizar eliminaciones` desmarcado**, comprobado visualmente antes y después del reinicio de la app y de la renovación de cuenta |
| Cancelación normal | Solicitada mediante los controles del trabajo y del resumen; no se acreditó su finalización inmediata |
| Detención autorizada | `am force-stop dk.tacit.android.foldersync.lite`; se comprobó ausencia del proceso y se abrió su actividad normal, arranque **COLD** |
| Estado posterior | Sin ejecución activa ni sincronización programada; el historial del par pasó a **`SyncCancelled`**, inicio registrado 27/10 00:43 |
| Cuenta existente | Se conservó el registro `Google Drive` y su asociación a **un par**; no se eliminó ni recreó el par |
| Renovación | `Desvincular cuenta` → `Iniciar sesión con Google` → flujo `accounts.google.com`, completado privadamente por el usuario |
| Prueba de cuenta | Botón `Prueba`: **«Tus credenciales se han probado y todo parece correcto.»** |
| Primer análisis | Se inició **`Analizar archivos`** sobre el par existente; terminó con **«Análisis completo · Error»**, notificación registrada a las **02:00**. El éxito de autenticación no se equipara al éxito del análisis |
| Revisión posterior | Tras retomar la intervención por la tarde se volvió a abrir FolderSync con su proceso reiniciado. El selector de la carpeta remota mostró `/MESTRY/`; se salió con **Atrás**, sin pulsar **Seleccionar** ni guardar otra carpeta |

La prueba de cuenta acredita la recuperación de autenticación que antes fallaba. No acredita por sí sola que cada documento esté actualizado, que se haya ejecutado una transferencia ni que una futura ejecución TwoWay sea aceptable. Se conserva el último error 403 del informe 10 como evidencia histórica; no se borraron registros para aparentar una sincronización correcta.

La elección de reautenticar sigue el procedimiento del proveedor para una cuenta Drive que deja de funcionar. La causa exacta del rechazo anterior —sesión, cliente o autorización usada por la app— no se identifica únicamente porque la renovación haya permitido pasar la prueba. [FolderSync: cuenta existente que no funciona](https://foldersync.io/docs/faq/drive/#existing-account-not-working).

`Analizar archivos` es una comprobación previa: la documentación distingue **Analyze**, que examina los cambios, de **Sync**, que los aplica. En esta primera etapa no se pulsó continuar/sincronizar ni se reactivó el horario; las pruebas reales autorizadas posteriormente se detallan más adelante. Se consultó únicamente la notificación de **FolderSync**, proyectando título y estado; no se volcaron notificaciones de otras aplicaciones. [Acciones del par](https://foldersync.io/docs/help/v2/folderpairs/#folderpair-actions).

Se conservaron dirección TwoWay, raíces, reglas de sobrescritura, checksum, conflictos y configuración de rclone. La ampliación posterior de autorización permitió añadir el filtro de dependencias descrito abajo. La propagación de borrados desactivada no impide reemplazos de archivos: recuperar la cuenta no equivale a aceptar cualquier cambio propuesto por un análisis.

## Horus remoto

Verificación actual mediante el provider oficial, proyección de campos no secretos:

```text
appVersion=1.1.0
configured=true
enabled=true
state=running
port=8022
keys=1
batteryUnrestricted=true
```

Desde el SSH existente de **Termux**, conectar a `127.0.0.1:8022` devolvió **0**. El cambio de habilitación lo hizo el usuario; esta intervención no regeneró claves, emparejó equipos ni modificó puertos.

En esta lectura inicial, el puerto del **bridge MESTRY**, `127.0.0.1:8787`, devolvió conexión rechazada, código **111**. Habilitar Horus remoto no equivale a arrancar ese bridge. Su recuperación posterior mediante los comandos existentes se documenta abajo; no se declaró validado el cliente S25.

Ambos resultados se reconfirmaron por la tarde, después de comprobar que la IP WLAN del S23 identificado por ADB coincidía con el destino del alias SSH existente `mestry-s23`. El proceso de comprobación se ejecutó con UID Termux **10348**. Esta lectura verifica disponibilidad de puertos; no añade una prueba de autenticación al SSH propio de Horus ni una prueba desde el S25.

## Ficha Codex: pantalla recuperada y perfil real

Se retomó **la misma sesión nativa** inspeccionada durante H0; no se inició un turno de modelo. Al volver a ella apareció un aviso de actualización **0.163.0 → 0.164.0**. Se pulsó el control **ESC**, que ofrecía omitirlo. Después se observaron:

```text
OpenAI Codex v0.163.0
/workspace/projects/mestry-horus-smoke
Composer disponible: Ask Codex to do anything
```

Esto acredita que la ficha ya muestra el TUI y admite interacción. No se afirma que el aviso explique retrospectivamente toda la pantalla vacía de H0; la causa de aquella muestra no quedó demostrada. **No se instaló la actualización ni se reinstaló Codex.**

Se ejecutó un comando local con el prefijo `!`, sin inferencia, que comprobó:

| Comprobación dentro de la ficha | Resultado |
|---|---|
| UID guest | **61002** |
| Home | **`/home/harness_codex`** |
| Git | **2.54.0** |
| GitHub antes de autorizar login | `gh api user` devolvió **4** y solicitó iniciar sesión |

Ahora la falta de login en esa ficha tiene una prueba de ejecución, además de los metadatos de H0. `/home/horus` y el harness siguen siendo perfiles distintos por diseño de Horus. Mantenerlos separados evita convertir la corrección de una pantalla en una copia de autenticaciones, configuraciones o conversaciones. [Perfiles oficiales Horus 1.1.0](https://github.com/scarif-labs/horus/blob/76da90789f039fe7ee796ae4ec44c1628fda2031/android/app/src/main/java/com/scariflabs/horus/terminal/TerminalHarnessUsers.kt).

El prefijo `!` permite ejecutar una orden local bajo las aprobaciones y sandbox actuales; no es un prompt de inferencia. No se enviaron tareas al modelo para comprobar Git o autenticación. [Comandos oficiales Codex](https://learn.chatgpt.com/docs/developer-commands).

### GitHub del harness: procedimiento autorizado

Se inició dentro de la propia ficha, con su UID/home efectivo:

```bash
gh auth login --hostname github.com --git-protocol https --web --skip-ssh-key
```

No se usaron `--with-token`, variables con tokens, `--insecure-storage`, copia de `hosts.yml`, SSH keys ni perfiles prestados. La autorización web fue humana, en el S23. No se capturó la pantalla con el código temporal ni se pidió enviarlo por chat. El helper autorizado se configuró para GitHub:

```bash
gh auth setup-git --hostname github.com
```

Después se comprobaron API y lectura de la rama de un repositorio privado ya autorizado, con los resultados de la tabla siguiente. No se creó un remoto, clon, commit o push para probar autenticación. La creación/publicación del laboratorio sigue reservada a H1. [Login gh](https://cli.github.com/manual/gh_auth_login), [helper Git](https://cli.github.com/manual/gh_auth_setup-git).

El primer intento web no dejó una sesión válida (`gh api user` siguió devolviendo 4). A petición del usuario se canceló ese proceso, se limpió la vista de la terminal sin borrar la conversación y se inició una autorización nueva. El usuario confirmó que la completó.

**Resultado verificado en el perfil nativo:**

| Prueba | Evidencia |
|---|---|
| Home de ejecución | `/home/harness_codex` |
| API autenticada | Marcador `NATIVE_GH_OK`, **retorno 0** |
| Helper Git | `gh auth setup-git --hostname github.com` ejecutado tras login; consulta posterior **`GH_HELPER=True`** |
| Lectura Git privada | `git ls-remote` contra el repositorio autorizado `app_gastos`: **retorno 0** |
| Referencia obtenida | `refs/heads/main`, **`4dbaeaeb8ec2b15205b7c34235a87dfde02bdb2c`**, igual a la referencia acreditada en H0 |
| Metadatos del mismo probe | Repositorio **privado**, rama predeterminada **main**, API retorno 0; permisos declarados `pull`, `push`, `admin`, `maintain` y `triage` verdaderos. Salida del probe de **01:31**, observada al retomar la terminal a las **18:00**; no constituye una publicación ni otra llamada API en esa hora |
| Almacenamiento gh | `.config/gh/hosts.yml` presente con modo **0600**; solo se leyó metadata de permisos, nunca su contenido |
| Ejecución | El comando terminó con `NATIVE_GITHUB_VERIFIED_END`, duración visible **6 s**, a las **01:31**; resultado retomado en la sesión de tarde |

Esto corrige el bloqueo de GitHub de la ficha: ya tiene una autorización propia y puede leer un repositorio privado con sus herramientas normales. No depende de copiar el login de Bare. El push efectivo y las modificaciones de working trees siguen pendientes del laboratorio H1 autorizado.

## FolderSync: diagnóstico posterior y pruebas

El error del primer análisis no expuso su causa detallada en las pantallas consultadas: la notificación interna solo muestra **Error**, y el historial de sincronización conserva la ejecución cancelada, sin una entrada de ese análisis. La notificación Android ya no estaba disponible después de volver a abrir la app. No se atribuye este resultado al mismo HTTP 403 de H0 sin disponer de ese detalle.

Se comprobó el acceso efectivo de almacenamiento (`MANAGE_EXTERNAL_STORAGE` permitido para el UID) y la presencia del directorio local. El selector remoto permitió navegar hasta una carpeta denominada `/MESTRY/`; el selector filtra carpetas, de modo que su vista no acredita ausencia de archivos ni revela el ID remoto.

La siguiente prueba propuesta es **desactivar únicamente «Comprobación rápida de cambios remotos» y repetir «Analizar archivos»**, conservando raíces, dirección, pausado y borrados desactivados. Esa opción está actualmente habilitada; la documentación la describe como una optimización que obtiene información de la estructura remota completa. Probar el recorrido normal puede separar un fallo de esa ruta de consulta del acceso ordinario a carpetas, pero **es una hipótesis diagnóstica, no una causa demostrada**. [Opciones oficiales](https://foldersync.io/docs/help/v2/folderpairsettings/#sync-options).

**Autorización recibida posteriormente:** el usuario aprobó los ajustes y pruebas necesarios en S23. Se desactivó esa opción, comprobando el `android.widget.CheckBox` real con `checked=false`, y se ejecutó solo el análisis. La notificación interna registró **«Análisis completo · Error», 27/10 16:00**. No se aplicaron transferencias, no se habilitó el horario y no se alteraron las carpetas. El rollback de la opción es volver a marcarla; el análisis no aplica cambios de archivos.

No hace falta conectar el S25 por USB para esta prueba de FolderSync ni para el perfil GitHub del S23. La recuperación del bridge y su prueba desde el cliente móvil constituyen una intervención posterior con alcance propio.

### Diagnóstico nuevo de FolderSync

Se activó temporalmente **Registro de depuración**, cuyo valor inicial era desactivado. Se consultó por ADB únicamente el logcat del PID FolderSync y se extrajeron categorías de error y campos de cuota. No se imprimió ni exportó el log bruto al workspace, tokens, cabeceras de autorización, URLs con parámetros o contenido de documentos; no se exportó configuración de cuentas. La propia app puede conservar registros privados normales. Al terminar el diagnóstico se volvió a desactivar la depuración y se verificó su casilla real en `false`.

| Evidencia reciente | Resultado saneado |
|---|---|
| Respuestas 16:00:25–16:00:28 | HTTP **403**, `PERMISSION_DENIED`, `RATE_LIMIT_EXCEEDED` / `rateLimitExceeded` |
| Servicio / métrica | `drive.googleapis.com` / `drive.googleapis.com/default` |
| Límite | `defaultPerMinutePerProject`, valor **100000**, unidad **`1/min/{project}`** |
| Mensaje | Cuota excedida para la métrica `Queries`, límite `Previous quota: Requests per minute`; identificador del proyecto consumidor omitido |
| Respuestas posteriores, 16:01:32–16:01:34 | También aparecen **401 / UNAUTHENTICATED** y el rechazo de consumidor no registrado. No se atribuyen todos los errores a una única causa |

La cuota observada es de solicitudes del proyecto API, **no espacio ocupado en Drive**. La FAQ del proveedor confirma que su cuota se comparte entre usuarios y recomienda evitar sincronizaciones en el minuto cero. Es una medida pertinente para el horario futuro; no prueba que cambiarlo resuelva por sí solo los rechazos de autenticación posteriores. No se crea un proyecto Google Cloud, una API key propia ni una autorización alternativa. [FolderSync: cuotas Drive](https://foldersync.io/docs/faq/drive/#quota-exceeded-errors).

Una nueva prueba de la cuenta guardada, después de la reapertura en frío, volvió a mostrar **«Tus credenciales se han probado y todo parece correcto.»**. No fue necesario otro login. Se inició otro análisis a las **16:09:16**; las revisiones de logs posteriores no mostraron nuevos errores de cuota/autenticación en la ventana consultada, pero la comprobación completa seguía sin finalizar. Se interrumpió esa comprobación de lectura deteniendo únicamente FolderSync, para probar un alcance sintético pequeño. No se convierte ausencia de marcadores recientes en éxito del análisis.

El horario existente se preparó con cron **`17 * * * *`** y se guardó. Al reabrirlo, la app lo normalizó como **Minutos → Repetir en → 17 minutos**, con próxima ocurrencia **27/10 17:17**: significa minuto 17 de cada hora, no un intervalo de 17 minutos. El habilitado global del par permaneció desactivado, **No programado**, incluso después de guardar y de reabrir FolderSync. Se activaron las notificaciones de **error**, tanto del horario existente como de ejecución **manual/automatización** en Conexión. Los valores anteriores eran cada hora en punto y ambos avisos de error desmarcados; el rollback es restablecer esos valores conservando el par pausado. Se acreditaron las casillas, no la entrega de una notificación futura con el teléfono en reposo.

### Prueba sintética de transferencia

Se creó un alcance propio, fuera de los documentos reales:

| Elemento | Valor |
|---|---|
| Namespace y par | `MESTRY_SYNC_TEST_20261027T191900Z` |
| Local | `/storage/emulated/0/Download/MESTRY_SYNC_TEST_20261027T191900Z/` |
| Remoto | `/MESTRY_SYNC_TEST_20261027T191900Z/`, creado mediante FolderSync en la misma cuenta Drive |
| Archivo | `probe.txt`, texto sintético público de **58 bytes**, tamaño comprobado con `stat` |
| SHA-256 inicial | `f0512d902527bffe89337a4aed75905eb21ff126968ef72fb683b016e21bb106` |
| Políticas | Bidireccional; programación desactivada; eliminaciones desactivadas; comprobación rápida desactivada; excluido de «Sincronizar todo» |

Se verificaron ambas raíces y **No programado** en el resumen antes de guardar. Tras reiniciar solo FolderSync se acreditaron los dos pares persistidos, ambos sin programación, y se comprobaron las casillas reales del par sintético antes de iniciar su sincronización manual.

| Prueba real | Resultado |
|---|---|
| Crear carpeta remota desde FolderSync | Correcto; carpeta propia localizada y seleccionada en el proveedor |
| Subir `probe.txt`, 16:31 | **SyncOK**, 5 s, **1 comprobado, 1 transferido, 0 eliminados** |
| Preparar recuperación | Se movió solo el archivo sintético local a `/storage/emulated/0/Download/MESTRY_SYNC_TEST_20261027T191900Z_baseline.txt`; hash original conservado |
| Descargar de nuevo desde Drive, 16:33 | **SyncOK**, 3 s, **1 comprobado, 1 transferido, 0 eliminados**. No se restableció la DB del par |
| Integridad de lectura de vuelta | SHA-256 **idéntico** al inicial y al baseline: `f0512d902527bffe89337a4aed75905eb21ff126968ef72fb683b016e21bb106` |
| Analizar el par sintético, 16:35 | **Análisis completo**, 1 archivo, **0 B a transferir**, `probe.txt` con **Ninguna acción** en ambos lados |

La notificación interna de un análisis **correcto** abre su vista de acciones al pulsarla; se verificó ese recorrido. Una notificación **Error** no había ofrecido esa vista. La prueba acredita lectura y escritura efectivas de la cuenta mediante FolderSync, incluida integridad de bytes, y permite distinguirlas de los fallos y el alcance mucho mayor del par principal.

### Alcance local y exclusión de dependencias

Un recorrido de **metadatos** por el SSH existente de Termux confirmó que ya podía leer la ruta compartida sin conceder permisos nuevos. Se limitó a 30 s: alcanzó **37.086 entradas de archivo**, 3.157 directorios y no terminó el árbol completo. Dentro de esa muestra contó 25.579 entradas bajo `node_modules`, 4.178 bajo `venv`, 1.767 bajo `__pycache__` y 7.829 bajo alguna `.codex`; las categorías **pueden solaparse y no se suman**. No se abrieron contenidos.

Otro recorrido limitado, podando dependencias, encontró tres directorios `.codex` de proyecto con `config.toml`; sus marcadores consultados de `auth.json`, `sessions` y `state*.sqlite` no estaban presentes. El recorrido fue parcial: no demuestra ausencia de homes o credenciales en todo el árbol. Tampoco justifica excluir indiscriminadamente la configuración portable de todos los proyectos.

Con la autorización ampliada se añadió al par principal un único filtro **Excluir → Expresión regular del nombre de la carpeta**:

```text
^([.]git|node_modules|[.]venv|venv|__pycache__)$
```

Solo limita transporte/enumeración de esos directorios; no borra los directorios locales ni las copias remotas preexistentes. No excluye por extensión todos los JSON, bases, binarios, APK, Markdown o configuraciones `.codex`. El rollback es eliminar ese filtro manteniendo el par pausado.

El mismo filtro se probó en el par sintético con un archivo público bajo cada uno de los cinco directorios excluidos, más `.codex/config.toml`, `.gitignore` y `.env.example`, que debían conservarse. El análisis correcto de **16:58** contó **4 archivos, 1 carpeta y 86 B a transferir**, con 3 transferencias propuestas. Se comprobó expresamente que `.codex/config.toml` seguía previsto para transferencia, `.gitignore` y `.env.example` permanecían incluidos y `.git` aparecía **Ignorar** en ambos lados. Esto valida el filtro en la instalación, además de su sintaxis documentada. **No se aplicó esa transferencia adicional**. Después se retiraron solo los ocho archivos extra creados para la prueba, verificando antes que sus contenidos seguían siendo los sintéticos esperados; se conservaron `probe.txt` y su baseline.

Se comprobó también la **cola real de FolderSync**: el análisis sintético solicitado a las 16:56 quedó como **Tarea pendiente** detrás del análisis principal iniciado a las **16:52:31**. Este último se canceló desde **Inicio → Notificaciones → Cancelar de su fila**, liberando inmediatamente la prueba pequeña. La app presentó la lectura cancelada como «Análisis completo · Error»; no se interpreta ese evento como otra prueba de fallo de autenticación. En adelante este control oficial evita recurrir a detener toda la app para cancelar una lectura activa.

Identificada la cuota compartida como fallo concreto, se volvió a habilitar en el par principal la **comprobación rápida remota**, para probar la optimización que reduce consultas individuales; desactivarla había sido una prueba diagnóstica y no una reparación demostrada. La casilla real quedó `checked=true`. Con el filtro validado y fuera del minuto cero, se inició el análisis final del par principal a las **17:03:15**.

**El análisis final terminó correctamente.** A las **17:39:43** aún se observaba activo; a las **17:41:57** la notificación de ese mismo par pasó a **«Análisis completo»**, sin sufijo Error. La notificación interna lo fecha a las **17:40**. Durante la espera se observaron consultas API a carpetas distintas y no aparecieron errores nuevos del proveedor en las ventanas examinadas; la observación no se basa solo en el tiempo transcurrido.

Al intentar abrir la vista de revisión, Android mostró Always On Display y el estado de keyguard activo. Se pidió acceso normal al teléfono; el usuario confirmó que había entrado en Horus. Posteriormente se comprobaron su pantalla principal autenticada y el acceso normal a FolderSync. No se recibió PIN o contraseña, no se alteró el bloqueo y no se emplearon métodos privilegiados para sortearlo.

### Revisión del par real y tratamiento del conflicto PostgreSQL

La vista final mostró **78.436 archivos, 7.554 carpetas, 0 B a transferir y 1 conflicto**. Se recorrió únicamente la rama de ese conflicto dentro del análisis, sin abrir contenidos de documentos ni consultar registros de la base:

```text
Villevault/GPTI/Proyecto/.stocksmart-audit/20261012-221102/pgdata/base/16386/1249
```

Se trata de un archivo interno de un directorio PostgreSQL. La fecha y el nombre de auditoría pertenecen a su ruta; **no se acreditó que esa copia fuera una instantánea coherente ni que pudiera restaurarse**. No se eligió una versión de ese archivo para reemplazar la otra ni se marcó «Asumir que los archivos son idénticos». Se confirmó **Omitir archivo**, conservando ambas copias, y se aplicó el plan de 0 B.

La ejecución real del par empezó a las **17:58**, duró **1m 36s** y terminó **`SyncConflict`**, con **78.436 comprobados, 0 transferidos y 0 eliminados**. La notificación Android informó **«S23 <> Google Drive / Fallido, Se ha producido un error»**. Esto acredita que el aviso manual activado se entrega; no se convierte el conflicto en un nuevo fallo de autenticación ni se oculta ese resultado.

Para evitar mezclar parcialmente esa copia física de la base, se añadió un segundo filtro **Excluir → El nombre de la carpeta empieza por**, limitado a esta ruta relativa:

```text
/Villevault/GPTI/Proyecto/.stocksmart-audit/20261012-221102/pgdata/
```

La documentación del proveedor establece que un valor con `/` se compara como ruta relativa y que excluir una carpeta excluye sus descendientes. Se verificó el valor exacto guardado en la interfaz. Las dos copias preexistentes permanecen en S23 y Drive; el filtro no las elimina ni las declara reconciliadas. No se excluyen indiscriminadamente todas las bases o todos los artefactos del proyecto. Su eventual recuperación debe tratar el clúster completo o un respaldo coherente; reemplazar tablas físicas sueltas no es un procedimiento válido de restauración. [Filtros FolderSync](https://foldersync.io/docs/help/v2/filters/), [respaldo físico PostgreSQL](https://www.postgresql.org/docs/current/backup-file.html).

Se inició la sincronización final del alcance documental corregido a las **18:08:08**. La programación se mantuvo pausada durante estas verificaciones. A las **18:25** su pantalla de estado mostraba **3.109/4.561 carpetas**, «Analizando archivos», duración **16m 58s**: progreso real, todavía sin resultado final. Los contadores de archivos/transferencias permanecían en 0 durante esa fase y no se interpretan como inventario vacío. El recorrido avanzó después a **8.221/8.375 carpetas descubiertas**; el denominador variaba al explorar el árbol. Los logs recientes consultados no mostraron categorías nuevas de cuota, autenticación o excepción; esos datos auxiliares no sustituyeron el resultado del historial.

**Resultado final real del par principal:**

| Campo del historial FolderSync | Valor verificado |
|---|---|
| Par | `S23 <> Google Drive` |
| Inicio | **27/10/2026 18:08** |
| Resultado | **`SyncOK`** |
| Duración | **34m 35s** |
| Archivos comprobados | **76.353** |
| Transferidos | **0** |
| Eliminados | **0** |

La pantalla de estado pasó a «No hay sincronización en curso» y se comprobó `SyncOK` tanto en la tarjeta original como en su historial. Se conservaron debajo los registros anteriores `SyncConflict` y `SyncCancelled`. El resultado confirma que el conflicto excluido ya no bloquea el **alcance admitido**, sin reconciliar la copia PostgreSQL excluida ni certificar identidad criptográfica de todos los documentos: el checksum global original sigue desactivado. La prueba sintética sí verificó identidad SHA-256 de sus bytes.

Solo después de ese resultado se pulsó **Activar** en la tarjeta del par original. Quedó **Desactivar / 27/10/2026 19:17**, mientras el par sintético conservó **Activar / No programado**. Se volvió a abrir el original y se verificó en su `android.widget.CheckBox` real **`Sincronizar eliminaciones=false`**; permanece incluido en «Sincronizar todo». La próxima ejecución acredita el horario configurado, **no una ejecución futura ya observada**. No se espera una hora adicional para presentar esa inferencia como prueba.

### Recuperación autorizada del bridge existente

Horus solicitó volver a iniciar sesión al abrirlo. Se comprobó que no existía un alias/key Horus utilizable en Termux ni un alias Horus en WSL; no se intentó sortear ese login. El usuario inició sesión privadamente y confirmó **«listo»**. Se retomó la terminal Bare ya existente, sin lanzar otro aprovisionamiento.

En `/home/horus`, UID guest **1000**, se verificaron las fuentes antes de ejecutar sus acciones:

- Supervisor instalado: SHA-256 **`27ff1f5da79211d36b5c28a8a8acc8186c2bb0e123e4efa6038ff4c4e651247a`**, coincide con la fuente revisada.
- Controlador instalado de la release `2dfb2403c53b973f2973`: SHA-256 **`9ee865fe6b29774808943d11bb4afbe41ee1fe1afc32379ce76841445aaa22ec`**, coincide con la fuente revisada.
- `mestry-bridge status`: retorno 0, `owned_process_running=false`, `pairing_present=true`, puerto 8787.
- Supervisor antes de arrancar: retorno 0, `worker_running=false`, `enabled=true`, salud falsa.

Se ejecutaron las acciones normales existentes, sin reinstalar código ni modificar el emparejamiento:

```bash
/home/horus/.local/bin/mestry-bridge start
/usr/bin/python3 /home/horus/.local/lib/mestry-keepalive/horus_keepalive.py start
```

Resultados visibles: **`MESTRY_HORUS_BRIDGE_READY 127.0.0.1:8787`** y **`MESTRY_KEEPALIVE_RUNNING_NO_NEW_PORTS`**. Una consulta desde Termux al health loopback obtuvo **HTTP 200**, `name=mestry-s25-pilot`, `version=0.1.0`.

La comprobación posterior confirmó `owned_process_running=true`, `pairing_present=true`, supervisor `worker_running=true`, `enabled=true` y salud verdadera. Su `status.json` pasó de **19:09:54Z** a **19:13:54Z**, manteniendo **`healthy` y 0 fallos consecutivos**: hay evidencia de supervisión periódica, no solo del mensaje de arranque. Desde Termux, una petición HTTP sin clave recibió **401** y el upgrade WebSocket sin clave recibió **`HTTP/1.1 401 Unauthorized`**. No se leyó la clave para probarlo.

También se ejecutó dentro de Bare el probe público existente `tools/s25-codex-client/horus_preflight.py`, transmitido como código a la terminal, sin instalarlo ni modificarlo. Resultado **PASS**: Codex **0.163.0**, inicialización app-server correcta, sesión ChatGPT autenticada y consulta de metadatos de hilos admitida; **0 turnos de modelo y ningún puerto abierto por el probe**. No se imprimieron credenciales o conversaciones. Su parser devolvió `unknown` para aprobación y sandbox; no se certifica con él la política efectiva de una futura tarea.

Estas pruebas acreditan el servicio, su supervisor y el backend local. No sustituyen una conexión autenticada desde el cliente S25, una tarea real, un reinicio Android o una prueba de disponibilidad 24/7.

Más tarde la interfaz de Horus requirió acceso de nuevo. Se comprobó inmediatamente que 8022 y 8787 seguían accesibles y que health devolvía HTTP 200 con identidad correcta: el acceso a la interfaz y la disponibilidad de los servicios son capas distintas. El usuario confirmó su entrada y se verificó `HORUS_HOME_READY=true`.

Como comprobación adicional, a las **18:00** se ejecutó dentro de la misma sesión nativa `/home/harness_codex/.local/bin/codex login status`, mediante `!python3`, capturando la salida y proyectando únicamente **`NATIVE_CODEX_LOGIN_RC=0`** y **`NATIVE_CODEX_CHATGPT=True`**. No se imprimió la salida bruta de autenticación y no hubo inferencia. La evidencia del home del harness es propia; no se extrapola el PASS de Bare ni se copian credenciales entre perfiles.

Una lectura independiente posterior desde el SSH habitual de Termux volvió a confirmar TCP 8022 y 8787 accesibles, **HTTP 200** e identidad `mestry-s25-pilot / 0.1.0` en `/healthz`, y **HTTP 401** al consultar `/v1/sessions` sin autenticación. No se alteró la protección del servicio para facilitar las pruebas.

## Límites conocidos y siguiente fase

| Aspecto | Alcance real y siguiente paso |
|---|---|
| Cuota compartida Drive | Causa concreta acreditada. El desplazamiento al minuto 17 reduce coincidencia con el horario en punto, pero no garantiza eliminar futuras cuotas del proveedor. Los avisos de error quedan habilitados |
| Copia física PostgreSQL antigua | Conservada en ambos extremos y excluida por su ruta exacta. Sigue sin reconciliar ni validar como respaldo restaurable; cualquier recuperación requiere un procedimiento de base de datos separado |
| Política TwoWay | Se conservaron sobrescritura y conflictos originales. Desactivar borrados no protege frente a todas las sustituciones; Drive no se convierte en mecanismo seguro para sincronizar un workspace Git activo |
| Autoridades | Drive conserva la documental congelada. Los futuros clones Git independientes deben quedar fuera de este espejo; esta reparación no implementa todavía esa separación |
| Horus | Terminal nativa y Bare autenticadas; servicios disponibles y supervisor observado. No se certifica recuperación después de reinicio, prueba sin PC o disponibilidad 24/7 |
| S25 | No se necesita USB para estas correcciones. La conexión autenticada y navegación desde el cliente deben comprobarse después por la red existente, sin cambiar emparejamientos |
| H1 | Mantener el perfil `/home/horus` elegido. El laboratorio requiere aprobación específica para crear su repositorio privado y sus archivos, commits y publicación sintéticos; no se ejecutaron aquí |

Estas correcciones no sustituyen el cierre H0 histórico ni convierten los límites de disponibilidad H3/H5 en impedimentos nuevos para el laboratorio GitHub. El siguiente paso de desarrollo es el laboratorio H1 del informe 10, con referencias Git comprobadas en ambos entornos y sin transferir dependencias ni homes Codex por FolderSync.

## Preservación y reversibilidad

El par se mantuvo pausado durante la revisión y las pruebas manuales. Los cambios de configuración son identificables: horario antes habilitado, pausado para el diagnóstico y finalmente habilitado al minuto 17 después de `SyncOK`; borrados antes habilitados, ahora deshabilitados. La propagación de borrados no se reactivó al terminar el diagnóstico. Para detener futuras ejecuciones basta pausar el par original; retirar los filtros debe hacerse con él pausado y una revisión previa, porque vuelve a admitir árboles que se aislaron deliberadamente.

Se conservaron los datos de FolderSync al detenerla; no se llamó `pm clear`, reinstalación ni eliminación de la cuenta/par. La cuenta se renovó dentro del mismo registro. La renovación de una autorización no debe describirse como rollback de tokens: no se guardaron copias de credenciales anteriores para restaurarlas.

No se modificaron permisos Android, distro, paquetes, homes entre sí, emparejamientos, VPN, proyectos reales, rclone ni documentos congelados. Las operaciones normales de las apps pueden actualizar su estado privado, historial de pruebas y archivos propios de autenticación; esas escrituras autorizadas son distintas de sincronizar datos de proyectos.

Para evitar que una nueva espera larga interrumpiera las pruebas de interfaz, se leyó `settings get global stay_on_while_plugged_in`: valor original **0**. Se estableció temporalmente **2**, mantener la pantalla despierta con alimentación USB, y se comprobó la lectura posterior. No cambia el PIN ni proporciona acceso a un bloqueo que requiera autenticación. **Al terminar se comprobó que seguía en 2, se restauró a 0 y se verificó la lectura 0.** No queda pendiente ese ajuste temporal. La casilla de depuración FolderSync también quedó verificada desactivada.

**Incidencia de navegación corregida:** al quedar enfocado el campo editable del título del par, unos gestos destinados a desplazar la vista introdujeron caracteres en su nombre. Se restauró exactamente **`S23 <> Google Drive`**, verificando la entrada carácter a carácter y comprobando el nombre final y el cierre del teclado. Se añadió una comprobación que bloquea los desplazamientos automatizados si el teclado está abierto. Las rutas local/remota siguieron siendo las mismas, la dirección continuó TwoWay y en ese momento el par permaneció pausado. No se presenta esta incidencia como una modificación solicitada por el usuario.

La consulta auxiliar del conector Drive no devolvió carpetas en una búsqueda exacta de `MESTRY`, y la lectura de la raíz rclone histórica `proyectos` devolvió 404 **para esa conexión**. No se comprobó equivalencia de identidad/alcance con FolderSync: esos resultados no prueban que su carpeta se haya eliminado ni autorizan reasignar IDs o recuperar elementos de la papelera. No se descargó contenido documental.

Único documento nuevo de esta intervención: este archivo. El cierre H0 conserva SHA-256 **`0468ee85577521e69a460a5d22441e72719339f2626beabaca069915345f4c66`** y el ADR congelado conserva **`02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031`**.

El cotejo confirmó intacta la línea base anterior de **WSL `/home/developer/proyectos/mestry`**: **1.816 archivos, 66.430.452 bytes**, huella agregada **`2296462f68e92cf7906cb478dff9b611abc1befe939a24f52dbffcc779b3ae26`**, excluyendo los informes nuevos 10 y 11. También coincidieron las huellas previas del script rclone, sus filtros y el launcher `codex2`. Este informe pasó la comprobación de enlaces locales, bloques Markdown y ausencia de patrones de tokens o correos. No se escribieron memorias ni se alteraron los informes históricos.
