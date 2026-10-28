# MESTRY — Plan de implementación y aceptación

Fecha: **2026-10-26**. **No ejecutado. Requiere aprobación antes de cualquier escritura, arranque de servicio, credencial, Git init/commit/push, instalación, cambio de filtros o prueba de fallo.** La investigación solo crea estos documentos y realiza lectura/análisis sintáctico.

## 1. Incrementos propuestos

| Etapa | Trabajo y dependencias | Archivos/componentes que se afectarían | Aceptación verificable | Riesgo y rollback |
|---|---|---|---|---|
| I0 — inventario adicional | Obtener pares/logs FolderSync Android por UI/consulta autorizada sin exportar credenciales; recuperar cinco originales. Puede hacerse antes de implementar | Seguimiento nuevo, no originales congelados; ninguna configuración | Tabla por par con rutas/IDs/método/filtros/borrados/conflictos/último resultado; no deducirlos del grant SAF | Bajo; conservar resultados históricos. No iniciar sync para rellenar evidencia |
| I1 — continuidad sobre un S23 | Recuperar **servicios existentes**, verificar home/runtime/historial; después cliente Windows observador del mismo backend por helper SSH acotado. Requiere autorización de arranque/identidad/helper, no reinstalar Codex | Controladores existentes bajo home Horus; candidato nuevo `tools/codex-continuity/remote_gateway.mjs` y cliente `remote_client.py`; claves públicas/catálogo solo tras revisión. Nombres aún no existentes | S25 inicia/observa un hilo sintético y Windows lee el **mismo thread/backend**, estado fresco y archivos por hash. Una tarea activa se observa sin duplicarla ni iniciar otro app-server. Cero exportación de bridge token | Medio. Guardar release/config previas; desactivar solo helper nuevo/revocar su identidad. No borrar sesiones/datos ni reemplazar instalación Codex |
| I2 — PC local→S23→S25→PC | Línea base Git aprobada, propietario/época/receipts, un subproyecto sintético y dependencias stdlib. Depende de I1 y decisión de autoridades/rutas | Nuevo laboratorio, scripts futuros start/end, almacén/control privado del dueño, integración de admisión en bridge; `.gitignore/.gitattributes` solo en nueva base aprobada | Mismo commit/inputs confirmados en ambos targets; pruebas Python reales por plataforma; handoff permite continuar desde S25; vuelta a WSL conserva cambio S23. Entrega tardía/reintento no sobrescribe ni duplica | Medio-alto. Conservar ramas/commits y entorno anterior; no reset/clean automático. Sin snapshot sobre checkout ocupado |
| I3 — recuperación completa y disponibilidad | Cápsulas de dependencias por target, backup remoto S23 autónomo, restore y ensayos físicos. Depende de I2 y permisos de destino/transporte | Capacidad de backup del broker Termux, journal/recibos, política de retención y pruebas; no OAuth en Horus. Automatismo Android solo si se aprueba capacidad soportada | Restore alternativo ejecuta proyecto sin tocar entorno bueno; entrega D4 verificada con PC apagado; reposo/24h y recuperación según alcance aceptados | Alto en pruebas de fallos. Backup/rollback previamente verificados; no destruir original para probar recuperación |

Los primeros tres incrementos de implementación son **I1, I2 e I3**; I0 cierra incertidumbres sin cambiar infraestructura. I1 conserva conversación/proceso en un backend; I2 demuestra continuidad entre dos instalaciones **sin fingir migración de sesión**.

## 2. Preflight y comandos propuestos

### Lecturas posteriores, sin turnos

Inventario dentro de la sesión **Horus** autorizada, no Termux ni WSL fingiendo ser Horus:

```sh
id
pwd
uname -m
cat /etc/alpine-release
command -v codex node npm python3 git rsync tar
codex --version
git --version
```

Resolver HOME/CODEX_HOME por nombre/ruta sin volcar entorno; listar solo metadatos de sesiones/configuración, no auth ni conversaciones completas. Comprobar versión/protocolo instalado antes de elegir flags de documentación actual. Estos comandos no se ejecutaron en Horus durante la investigación porque su sesión remota estaba detenida/inaccesible.

Para controles `mestry-bridge status`/keepalive, leer primero el helper vigente y verificar propietario/hash. Un `start` solo se ejecutaría con autorización de recuperación, después de comprobar ausencia propia y conservar archivos. El arranque del servicio Android Horus se hace por mecanismo existente autorizado; no se genera otra pareja de claves ni se usa un instalador para «recuperar» una app existente.

ADB: utilizar primero el servidor ya activo o solicitar autorización específica si está ausente. No invocar `adb devices` como sonda que pueda arrancarlo. Revalidar serial/modelo antes de cualquier operación. La consulta status del provider puede crear su proceso proveedor aunque sea lectura; no confundir ese PID con servicio remoto saludable.

### Comandos de intercambio, solo en el laboratorio futuro aprobado

Ejemplos conceptuales; los valores son marcadores y **no se deben pegar contra árboles reales**:

```sh
git -C "$MESTRY_LAB_PC" status --porcelain=v1
git -C "$MESTRY_LAB_PC" diff --check
git -C "$MESTRY_LAB_PC" rev-parse HEAD
git -C "$MESTRY_LAB_PC" bundle create "$MESTRY_EXPORT/version.bundle" HEAD
git -C "$MESTRY_LAB_S23" bundle verify "$MESTRY_IMPORT/version.bundle"
sha256sum "$MESTRY_IMPORT/version.bundle"
git -C "$MESTRY_LAB_S23" fetch "$MESTRY_IMPORT/version.bundle" HEAD:refs/mestry/incoming/OPERACION
git -C "$MESTRY_LAB_S23" update-ref refs/mestry/accepted NUEVO_OID BASE_ESPERADA
```

Los tres primeros son comprobaciones; bundle create/fetch/update-ref escriben y requieren aprobación. Crear/reposicionar repositorios y commits requiere aprobación adicional del conjunto exacto de archivos. El flujo real valida propietario/época/manifiesto, completitud de recursos externos y quiescencia **antes** de promover; los comandos Git aislados no implementan esos controles. No usar `--force`, `reset --hard`, `clean`, hooks de apagado como única entrega ni `bisync --resync` en este protocolo.

`npm ci` o instalación Python solo se propondrán para un área nueva cuando el inventario confirme necesidad y se apruebe. No ejecutar sobre dependencias existentes: npm ci borra node_modules de su destino. `rsync --dry-run --itemize-changes` puede ser una prueba futura, pero incluso dry-run requiere que ambos extremos, permisos y fuentes estén identificados; no activarlo sobre pares actuales para experimentar.

## 3. Protocolo sintético detallado de I2

**Ubicaciones propuestas exactas:** WSL `/home/developer/mestry-lab/continuidad-20261026`; S23 `/workspace/projects/mestry-horus-smoke/continuidad-20261026`. Son rutas a crear **después** de aprobación, conservando todos los fixtures previos. Esta prueba no modifica la allowlist para otros proyectos ni declara soporte multiproyecto general.

Fixture: `calc.py` y `input.json` con enteros sintéticos, `test_calc.py` stdlib y `HANDOFF.md` sin secretos. PC y S23 guardan hashes antes/después, commit, versión Python y resultado de tests. Capturar inventario/hash de los fixtures originales del root piloto para comprobar que no cambiaron. Datos y nombres finales se presentan en diff antes de ejecutar.

1. Confirmar que las dos ubicaciones de laboratorio no existen o están vacías según permiso explícito; si contienen datos, detener y revisar. No borrar contenido para preparar el ensayo.
2. Crear base Git solo del laboratorio; ejecutar pruebas en PC y registrar versión. Una edición local cambia un valor y resultado esperado; commit con operación única y hash de inputs.
3. Conceder propiedad y registrar época/base en S23; probar que el flujo gestionado rechaza otra tarea escritora del mismo proyecto. No simular la garantía mediante un lock que nadie consulta.
4. Transferir bundle/inputs a staging con operación estable, verificar hash/objetos; ante diferencia, detener sin promover. Ejecutar tests en S23 con su Python real; conservar ambos resultados separados.
5. Obtener recibo D2/D3, generar handoff y respaldar la entrega en destino sintético aprobado para D4, utilizando en este laboratorio el rclone WSL existente si se aprueba esa escritura. Verificar descarga/hash independiente antes de confirmación final. Ningún original de Drive participa. Esto no valida el uploader autónomo S23 de I3 ni presupone cápsulas nativas completas por superar el fixture stdlib.
6. Desde S25 consultar el mismo proyecto y continuar un cambio dentro del laboratorio; confirmar esa versión y devolverla a WSL. Si se usa el modelo, aprobar previamente **un turno sintético por backend y su presupuesto**; no inferirlo de la autorización para sincronizar. Variante sin inferencia valida transporte/ejecución, no uso real de Codex.
7. Repetir la entrega idéntica y consultar por operation_id: mismo recibo, cero duplicados. Probar de forma sintética token/época obsoletos y base divergente: rechazo con ambas ramas preservadas.
8. Cerrar con manifiesto de archivos, pruebas y estados. Rollback: retirar integración de laboratorio y volver a la versión de servicio conservada si se modificó; dejar commits/export de prueba identificados. Limpieza/eliminación de archivos sintéticos se aprueba aparte, nunca por sincronización propagada.

Para capas de dependencias, ampliar I3 con un proyecto que realmente use un paquete por target y un addon/wheel nativo si forma parte de la carga cotidiana. No declarar el entorno completo recuperable basándose solo en Python stdlib.

## 4. Matriz de fallos y aceptación

Todas las pruebas de fallo siguientes son **PENDIENTES**, sintéticas y sujetas a autorización; la tabla no informa experimentos realizados.

| Caso/prueba | Riesgo | Detección | Comportamiento seguro | Recuperación | Intervención / aceptación |
|---|---|---|---|---|---|
| T01 PC y S23 editan lo mismo | Sobrescritura/merge perdido | Propietario/época/base y dirty/tree hash | Rechazar segunda admisión; si actor externo escribió, no promover sobre divergencia | Ramas separadas/merge revisado | Humana ante divergencia; probar ambos cambios conservados |
| T02 S23 pierde red en transferencia | Conjunto parcial | Estado operación, bytes/hash y recibo ausente | Staging, sin D3/D4 | Reconciliar mismo ID y reanudar solo transporte | Automática si inequívoco; test hash y versión previa intactos |
| T03 PC se apaga antes de publicar | Trabajo solo local; lease huérfano | Sin recibo durable, owner pendiente | S23 sirve última confirmada; no asumir cierre | Reabrir branch/journal PC o recuperar ownership con nueva época | Humana si PC perdido; entrega vieja rechazada, no borrada |
| T04 FolderSync encuentra dos versiones | Elección equivocada por timestamp | Conflicto/estado/log y revisión/hash | Conservar ambas; no auto «idénticos» sin prueba | Reconciliación con original/versión | Humana en originales; probar fuera de datos reales |
| T05 rclone difiere inesperadamente | Borrados/sobrescrituras extensas | Deltas/filtros/raíces/sentinelas/umbral porcentual | Abortar revisión; nunca resync automático | Restaurar/reconciliar con snapshot aprobado | Humana; presentar plan antes de escribir |
| T06 Eliminación accidental | Propagación y pérdida histórica | Git, manifiesto/tombstone/papelera o falta de hash | No limpiar backup por reflejar borrado | Restaurar versión aparte, después promover | Humana para originales; verificar contenido y no borrar otras versiones |
| T07 Dependencia PC llega al S23 | ABI/libc/path incompatibles | Target manifiesto/ELF/wheel/runtime y test | No instalar/promover en activo | Cápsula S23 o reconstrucción aislada | Automática si existe cápsula válida; rechazo de artefacto erróneo |
| T08 DB cambia al copiar | Backup inconsistente | Motor/checkpoint y prueba de restore | Rechazar copia genérica viva | Backup API del dueño/quiescencia aprobada | Humana si no hay export válido; prueba integridad/consistencia, no solo hash |
| T09 Sincronizador falla parcialmente | Éxito aparente | Resultado global y por archivo, pendientes/errores | Sin confirmación final | Reconciliar objetos/operación, no repetir a ciegas | Automática con límites; resultado final sin pendientes falsos |
| T10 Codex ejecuta mientras entra release | Código/deps cambian bajo tarea | Turnos y jobs activos + admisión | Staging; no tocar generación en uso | Esperar fin/reprogramar promoción | No matar tarea por defecto; demostrar hashes de inputs usados estables |
| T11 Drive tarda/limita API | Duplicado o supuesto backup | HTTP/status/reintentos/readback/journal | UNKNOWN/PENDING; no D4 | Backoff acotado y reconciliar ID reservado | Humana en permisos/revocación; cero duplicados tras timeout |
| T12 Dispositivo vuelve tras días | Publicación de base vieja | Época/commit/control + refs actuales | Rechazo de promoción obsoleta | Fetch y branch de rescate/merge | Humana si conflicto; trabajo tardío preservado sin reemplazo silencioso |
| T13 UID/bridge muere | Turno interrumpido/operación incierta | Salud por capas y proceso propietario | No duplicar turno/escritura | Recuperar backend/historial, reconciliar efectos | Ensayo autorizado; guardar evidencia de lo recuperable y lo perdido |
| T14 Reinicio/primer desbloqueo | Nodo inaccesible aunque enabled persista | Boot/CE/servicio/hello y tarea real | Estado no disponible hasta cadena válida | Procedimiento aprobado de desbloqueo/arranque | Humana mientras no exista automatismo soportado; no atribuir PASS a SSH solo |

El control de propiedad solo protege rutas gestionadas: T01 debe incluir el caso fuera de protocolo para demostrar detección/límite, no prometer aislamiento del SO bajo dangerFullAccess.

## 5. Puertas para declarar uso cotidiano 24/7

1. Dos clientes consultan el mismo backend/hilo con contenido fresco y control de un único escritor; no basta listado o hello.
2. Ida/vuelta WSL local↔S23 aceptada por commit/hash y pruebas por target; handoff explícito sin trasladar bases activas.
3. Recepción, ejecución y backup se distinguen; restore alternativo funciona, incluidos recursos únicos y dependencias requeridas.
4. PC físicamente apagado, cargador estable, reposo y carga real prolongada medidos; ensayo24h con hora inicial/final e incidencias. No extrapolar USB o una sesión breve.
5. Fallo/reinicio autorizados y procedimiento de recuperación aceptado; declarar explícitamente la intervención tras primer desbloqueo si sigue necesaria.
6. FolderSync/rclone alineados con autoridad/exclusiones y sin conflictos pendientes; permisos/grants/cuenta verificados por ruta/ID, sin registros de secretos.

No se fijan porcentajes ni SLA sin mediciones. RPO/RTO se aceptan por tipo de datos y nivel D0–D4. La operación no se considera lista si el requisito de recuperación tras reinicio exige cero intervención y esa capacidad sigue sin resolver.

## 6. Aprobaciones necesarias y propuestas concretas

Antes de actuar: aprobar archivos/rutas del laboratorio y alcance Git; recuperación del servicio Horus existente; identidad/capacidad del cliente Windows y acceso privado correspondiente; cambios mínimos de bridge/recibos/admisión; diff de filtros/parámetros por par con backup; destino Drive sintético y capacidad de publicación/backup; instalaciones solo si el inventario demuestra falta; presupuesto de turnos sintéticos; pruebas físicas/de fallos y política de retención.

Decisión separada: aceptar un paso manual tras reinicio/primer desbloqueo o estudiar una capacidad Android soportada para Horus. No se autoriza root, ADB local persistente, cambio de kernel, migrar Codex, desactivar protecciones, restaurar papelera o ampliar OAuth por esta propuesta. La aprobación futura debe referirse a un diff/protocolo concreto; esta investigación no ejecuta ninguna de esas acciones.
