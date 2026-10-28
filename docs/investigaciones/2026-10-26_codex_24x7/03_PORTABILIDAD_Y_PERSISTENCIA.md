# MESTRY — Portabilidad, persistencia y sesiones

Fecha: **2026-10-26**. Clasificación y diseño **PROPUESTOS** sobre inventario [01](01_AUDITORIA_ENTORNO_CODEX.md). No se excluyen dependencias para ahorrar espacio: se evita intercambiar instalaciones incompatibles y se preservan por plataforma para ejecución/recuperación.

## 1. Consistencia que realmente se necesita

Una versión ejecutable queda identificada por **commit/árbol fuente + archivos únicos externos por hash + configuración portable + identidad del entorno/dependencias + resultado de aceptación de esa plataforma**. No implica directorios internos idénticos ni resultados numéricos bit a bit entre arquitecturas.

Hay tres persistencias distintas: archivos durables, historial durable y procesos vivos. Una copia de archivos no transfiere RAM, descriptores, sockets, terminales, tareas activas ni identidad de un proceso. La persistencia del mismo hilo se mantiene en su backend; entre instalaciones se entrega estado de proyecto y contexto explícito sin prometer la misma conversación.

## 2. Matriz A: conservación, identidad, reconstrucción y ABI

«Único» indica contenido que puede perderse si se descarta sin otro registro. «Reconstruible» es condicional a conservar **todas** las entradas; un lockfile aislado no garantiza disponibilidad futura de registries ni compilaciones idénticas.

| ID / categoría | ¿Conservar? ¿Datos únicos? | ¿Mismos bytes Windows/WSL y S23? | Reconstrucción y determinismo | Compatibilidad |
|---|---|---|---|---|
| K01 Código fuente | Obligatorio; cambios propios únicos | Sí para la misma versión confirmada, con política EOL explícita | Git recupera commits; cambios sin guardar/confirmar no aparecen mágicamente | Texto portable; comportamiento depende de APIs/entorno |
| K02 Documentos originales | Obligatorio según selección; ediciones humanas únicas | Original por ID/revisión; una exportación nativa puede diferir | No reconstruibles desde índice/resumen | Formato/editor y fidelidad por validar; Drive autoridad |
| K03 Configuración del proyecto | Obligatorio; separar opciones propias de secretos | La parte portable sí; rutas/toolchains no | Versionar manifest/locks, scripts y versiones de herramienta | Rutas absolutas, intérpretes y SO requieren perfiles |
| K04 node_modules | Necesario para ejecutar si el proyecto los usa; puede contener parches únicos | **No exigir identidad** | Reinstalable si locks, paquetes, flags y scripts están disponibles; rescatar parches/vendor antes de excluir | JS puro puede ser portable; `.node`, binarios opcionales y postinstall no se asumen portables |
| K05 Entornos Python | Necesarios para ejecutar; no guardar fuente propia dentro | No | Recrear con intérprete/locks/wheels/toolchain; preservar paquetes privados/parches | Python3.12 WSL frente a3.14 histórico Horus, arquitectura/libc y shebangs absolutos difieren |
| K06 Bibliotecas/binarios nativos | Obligatorios si ejecutados; binarios sin fuente pueden ser únicos | No entre ARM64/musl, x86-64/glibc o Windows/PE | Guardar fuente/licencia/toolchain y/o artefacto exacto por plataforma | ISA, linker, libc, ABI y kernel importan; extensión de archivo no basta |
| K07 Metadatos Git | Historia/refs obligatorias; reflog/stash/untracked pueden ser únicos | Objetos/commits compartidos; index/config/locks/reflog no deben espejarse vivos | Clonar/fetch de objetos/refs, bundles consistentes; registrar stashes/trabajo no confirmado aparte | Git es protocolo de objetos, no sincronización física del directorio `.git` |
| K08 Cachés de compilación | Preservar si reducen RTO medido; normalmente regenerables | No | Dependen de paths, toolchain y flags; reconstrucción válida no siempre bit reproducible | Cache compartida sin clave de plataforma puede contaminar builds |
| K09 APK y artefactos finales | Conservar releases/entregables y hashes; firma o build puede ser único | El artefacto distribuido sí; binario de host no | Rebuild solo si fuentes, herramientas, inputs y firma existen | APK puede tener ABI/SDK específicos; build host es otro problema |
| K10 Generados no reproducibles/resultados | Obligatorio cuando representan trabajo/experimento único | Por hash si se replica ese resultado | No asumir regeneración sin seed, datos, versión, servicios y parámetros | Resultados pueden depender de arquitectura/BLAS/tiempo/red |
| K11 Generados reproducibles | Conservar selectivamente según RTO | Solo si su contrato exige igualdad | Fuentes+generador+config+versión/hash; demostrar repetibilidad | Mantener separados de código manual y resultados únicos |
| K12 Bases de datos | Datos únicos obligatorios | Snapshot lógico compatible, no DB viva idéntica | Backup/restore del motor; migraciones/versión necesarias | Formato/codec/extensiones/versiones; no copiar entre motores por extensión |
| K13 Índices/catálogos | Estado incremental/cursor puede ser importante; índice derivado regenerable | No necesariamente | Rebuild desde corpus autorizado, extractor/modelo/versión; conservar checkpoint si seguro | Extensiones nativas y validez de permisos/cursor dependen del entorno |
| K14 Temporales/locks/sockets | No como estado transferible; rescatar temporales con trabajo único | No | Se regeneran; un temporal puede contener una operación incierta que debe reconciliarse | PID/lock de otra máquina no acredita proceso vivo |
| K15 Historial/sesiones Codex | Conversaciones persistidas pueden ser únicas y sensibles | No sincronizar internals activos entre instalaciones | Resume en backend original; backup coherente para recuperación del mismo entorno; handoff para otro | Rutas, versión/protocolo, auth y herramientas locales no son portables automáticamente |
| K16 Credenciales | Disponibilidad necesaria, conservación privada separada | No, salvo provisión específica autorizada | Reautorización/rotación o recuperación segura según mecanismo; Keystore puede ser no exportable | Credencial de una app/UID/equipo no concede acceso a otro |
| K17 Configuración del sistema | Conservar manifiesto/red/servicios y cambios propios | No | Procedimiento documentado y backups de configuración seguros | PRoot no es sistema con systemd/root Android; UID/SELinux deben respetarse |
| K18 Estado durable de servicios | Journal/colas/recibos/enabled importantes; PID/estado de RAM no portable | Datos lógicos según contrato, no PID/puertos activos | Arranque idempotente, propietario verificado, reconciliación de UNKNOWN | Persistir enabled no mantiene servicio ni lo inicia tras Boot |
| K19 Datos de proyecto/modelos/recursos | Obligatorios si son entradas únicas o difíciles de obtener | Por hash si son el mismo input autorizado | Recuperar fuente por revisión/licencia o guardar copia; no descargar modelos en esta investigación | Pesos/datos pueden portarse, runtime/aceleración y tamaño no se asumen |
| K20 Configuración personal del cliente | Preferencias y mapas de hilos pueden ser únicos; caché derivada | No copiar Android prefs/Keystore a WSL | Provisión por cliente, estado mínimo recuperable del servidor | Cliente S25 no sustituye backend ni guarda toda la autoridad |

Referencias: [venv no portable](https://docs.python.org/3/library/venv.html), [tags Python por ABI/plataforma](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/), [addons Node](https://nodejs.org/api/addons.html). Inferencia aplicada al inventario: un ejecutable ELF x86-64/glibc observado en WSL no se convierte en ARM64/Alpine al sincronizarlo.

## 3. Matriz B: archivos abiertos, daños y mecanismo seguro

| ID | ¿Copiar en uso? | Copia desde otra plataforma | Si lo sobrescribe un sincronizador | Versionado/respaldo y mecanismo de persistencia |
|---|---|---|---|---|
| K01 | Solo snapshot de versión estable; buffers abiertos no incluidos | Conservar EOL/mode/symlinks del contrato | Pierde cambios no publicados o mezcla releases | Git por objetos; branch de rescate para trabajo pendiente |
| K02 | API/revisión o snapshot del formato; revalidar cambios | Conversión puede perder estructura/comentarios | Pérdida de edición humana | Drive por ID/version; controlador de edición y recuperación separada |
| K03 | Congelar configuración usada por cada tarea | Adaptar perfil sin modificar el original portable | Ejecuta con endpoints/rutas/versiones incorrectos | Git para parte portable; perfil local y secretos privados |
| K04 | No instalar ni reemplazar mientras una tarea los usa | Puede fallar carga de módulos/binarios o seleccionar paquetes erróneos | Instalación parcial, crashes o ejecución distinta | Mantener instalación local existente; reconstruir **en nueva área**; cache/archivo de recuperación etiquetado por plataforma |
| K05 | No reemplazar venv activo | Shebangs/path/interpreter/ABI pueden quedar inválidos | Rompe intérprete/paquetes durante tareas | Venv local; wheelhouse y snapshot por plataforma/version/ruta prevista |
| K06 | No sustituir librerías cargadas o binarios de tarea viva | Exec format error, loader ausente, símbolos o comportamiento incorrecto | Rompe capacidad de ejecución y recuperación | Artefactos versionados por target+hash, instalados solo en área validada |
| K07 | Nunca espejar `.git` activo | Puede copiar index/config de otro host aunque objetos sean legibles | Refs/index/locks incoherentes, historial aparente incorrecto | fetch/push/bundle, fsck; backup consistente de refs/objetos y trabajo fuera de commits |
| K08 | Solo si la herramienta proporciona cache segura o export cerrado | Invalidez por ABI/paths/flags | Resultados obsoletos o build errático | Cache local con clave; backup opcional medido, regeneración como fallback |
| K09 | Solo artefacto cerrado, hash verificado | Distribuir a targets compatibles; no al PATH arbitrariamente | Reemplaza release confirmada sin trazabilidad | Nombre/ID de versión único, manifiesto y readback; firmas privadas aparte |
| K10 | Capturar después de cierre/checkpoint de aplicación | Preservar formato y procedencia | Destruye resultado irrecuperable | Export inmutable por política y hash; backup separado, sin deduplicar por parecido |
| K11 | Solo generación terminada | Recalcular si cambió generador/target | Puede mezclar etapas incompatibles | Versionar inputs/generador y publicar lote consistente |
| K12 | **No con copia genérica**; usar API de backup o quiescencia | Validar motor/schema/codec antes de restore | Corrupción/pérdida transaccional | Snapshot coherente; test restore e integridad; conservar journals necesarios según motor |
| K13 | Solo export/generación coherente | Validar modelo/extensión/permisos | Respuestas obsoletas o cursor perdido | Rebuild y generación; backup de cursor/cola solo con consistencia y alcance |
| K14 | No replicar archivos especiales ni locks | PIDs/paths no corresponden al receptor | Falso proceso activo, trabajo bloqueado o repetido | Reconciliar operación; limpiar solo con criterio aprobado, nunca por sync ciego |
| K15 | No copiar DB/JSONL/client-state activos como migración de sesión | No crea proceso, contexto operativo ni acceso válido | Pérdida de historial o sesiones divergentes | API oficial para leer/resumir; backup frío/coherente del dueño para recuperación; export de handoff revisado |
| K16 | No copiar por sincronizador | Puede exponer secretos o inutilizar cifrado/Keystore | Revoca/rompe auth o comparte privilegios | Almacén privado por UID/cliente; backup cifrado separado solo autorizado o reauth |
| K17 | No trasplantar configuración de otro SO | Rutas/UID/init/network distintos | Servicio deja de arrancar o expone permisos | Inventario+procedimiento+backup del mismo target, sin root ficticio |
| K18 | Journal mediante transacción; no copiar PID vivo | IDs/procesos no trasladables | Reintentos duplicados o falsa salud | Journal propio del S23 y receipts; control de propiedad por PID+start-time local |
| K19 | Solo snapshot estable y autorizado | Datos sí, engines no necesariamente | Cambia input de una tarea a mitad de ejecución | IDs/revisiones/hash/licencia y snapshots por experimento |
| K20 | Preferencias exportables según app, no storage interno activo | No porta Keystore ni permisos Android | Pérdida de pairing o caché obsoleta | Backend como autoridad; preferencias/identidades propias de cada cliente |

Para SQLite, [Backup API](https://sqlite.org/backup.html) y [WAL](https://sqlite.org/wal.html) explican la necesidad de una captura coherente. La lectura `immutable=1` usada para auditar metadata **no constituye un backup transaccional** ni justifica copiar una DB de Codex activa.

## 4. Dependencias: preservar ejecución, no solo lockfiles

No se borra una dependencia existente al excluirla del intercambio entre plataformas. El procedimiento futuro conserva el entorno operativo actual hasta que **otro entorno, en otra ruta, supera la prueba del proyecto**. Fallar instalación o no disponer de un wheel ARM/musl bloquea la declaración «listo en S23», aunque el código fuente ya haya llegado.

Se propone conservar por target una cápsula identificada por `SO + CPU + libc + runtime/ABI + hash de locks + toolchain + variables no secretas`. Incluye paquetes descargados, wheels/tarballs privados autorizados, fuentes/parches, inventario de librerías y, si aporta recuperación más rápida, snapshot completo de dependencias/rootfs del mismo target. El gasto adicional de almacenamiento se justifica por **RTO medido** y capacidad offline, no por una obligación de copiar todo entre máquinas.

`npm ci` exige lock coherente y elimina node_modules existente: por eso solo se propone en una **copia de preparación**, nunca sobre el runtime activo. [npm](https://docs.npmjs.com/cli/v11/commands/npm-ci/). Python necesita intérprete y wheels compatibles; un lock sin hashes, binarios disponibles y toolchain no demuestra determinismo. Dependencias modificadas a mano se rescatan como patch/vendor antes de considerarlas regenerables.

Android Studio no soporta actualmente hosts Linux ARM; esto no demuestra que cada compilador individual sea imposible, pero sí impide prometer el build Android existente sobre Horus. [Requisitos oficiales](https://developer.android.com/studio/install#linux). Recomendación: editar/pruebas compatibles en S23; build APK/SDK/NDK en PC cuando se requiera, con artefactos finales verificables disponibles después desde S23/Drive. No migrar a Debian ni cambiar Codex para resolverlo sin otra evaluación/aprobación.

## 5. Dos escenarios de sesiones Codex

### Escenario 1: S25 y Windows sobre el mismo S23

| Estado | Qué puede conservarse | Condición real |
|---|---|---|
| Archivos/cambios | Mismo filesystem/proyecto del S23; no hay que copiarlos para cambiar de pantalla | Acceso al **mismo workspace**, no Documents/Mestry por coincidencia de nombre |
| Conversación/historial | Hilo persistido del mismo backend/home | Cliente usa ID original y recupera estado del servidor |
| Contexto cargado y tarea activa | Continúan en el proceso dueño mientras siga vivo | Windows debe observar/conectar al mismo backend; otro app-server/TUI no equivale a adjuntarse al proceso original |
| Herramientas/procesos | Siguen ejecutándose en S23 si el ciclo de vida los conserva | Desconexión de transporte no prueba persistencia; comprobar turno real |
| Caché/preferencias | Cada cliente tiene su propia proyección | No importar pairing/Keystore de S25 a Windows |

La [documentación app-server](https://learn.chatgpt.com/docs/app-server) distingue lectura, reanudación y estado cargado. El bridge MESTRY usa un protocolo propio sobre app-server **stdio**; no es el endpoint nativo WS de Codex. `codex --remote` no puede apuntarse sin más a 8787/18787. Existe documentación actual de ese modo remoto, pero compatibilidad con S23 0.163 y el bridge no está probada: **no requiere ni autoriza actualizar Codex ahora**.

Falta un cliente Windows validado del protocolo MESTRY y una credencial propia. La opción inicial de terminal SSH sirve para archivos y sesiones inactivas bajo autorización, pero no se presenta como la UX completa ni como garantía de observar el mismo turno activo. Abrir `codex resume` en otro proceso exige quiescencia y validar home/hilo; nunca es recuperación transparente de una tarea viva.

### Escenario 2: Codex local WSL y luego Codex del S23

Se preservan la **versión confirmada del proyecto**, adjuntos seleccionados, resultados y un handoff revisado. La conversación WSL permanece en su backend/home. En S23 se continúa el hilo propio adecuado o se crea uno nuevo con ese handoff. No se promete transferir conversación completa, memoria cargada, tarea activa, procesos, shell ni herramientas del PC.

Contenido mínimo de handoff: proyecto, base y commit nuevo, hashes de datos/artefactos, cambios realizados, pruebas realmente ejecutadas por plataforma, pendientes/errores, dependencias/capacidades requeridas y tarea siguiente. IDs de hilo opcionales se acompañan de **backend/home/plataforma**; no se convierten en IDs globales por copiarlos. Excluir secretos, prompts completos y contexto personal innecesario.

El home WSL observado es `.codex-account-2`, no el default genérico `.codex`; el home efectivo de cada perfil Horus debe inventariarse en su propia sesión autorizada. [Variables oficiales de estado](https://learn.chatgpt.com/docs/config-file/environment-variables). **No fusionar esos homes ni sus bases activas mediante FolderSync/rclone.**

## 6. Backups y puntos de recuperación

Tres capas propuestas: (1) objetos Git/inputs/artefactos con recibos; (2) cápsula de ejecución del mismo target para restaurar dependencias sin red; (3) backup coherente del estado único de servicio/sesiones, con privacidad y procedimiento del dueño. Credenciales tienen política separada; un backup de Keystore o UID no se asume restaurable en otro dispositivo.

Git bundle no incluye automáticamente archivos sin seguimiento, índice, stash no referenciado, LFS externo o submódulos completos. El manifiesto debe identificarlos/respaldarlos expresamente. La restauración es en ubicación alternativa y sin reemplazar el entorno bueno; solo se promueve al superar pruebas. Copiar un tar de Linux a Drive preserva sus bytes internos, pero extraerlo necesita validar permisos, enlaces, propietarios, rutas y versión del entorno. Ningún backup transfiere una ejecución viva.
