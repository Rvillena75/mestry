# MESTRY — Comparación de arquitecturas

Fecha: **2026-10-26**. Evaluación de diseño, **no benchmark ni autorización de implementación**. Evidencia actual en [01](01_AUDITORIA_ENTORNO_CODEX.md), herramientas en [02](02_MAPA_SINCRONIZACION_REAL.md), semántica de archivos/sesiones en [03](03_PORTABILIDAD_Y_PERSISTENCIA.md).

## 1. Obligaciones y preferencias

Obligatorio: S23 como nodo principal sin PC permanente; cliente S25 conservado; PC capaz de ejecutar localmente cuando se elija; versiones confirmadas trazables y recuperables; dependencias funcionales según plataforma; seguridad/arquitectura Drive respetadas; ningún reemplazo de Codex sin justificación/aprobación. No se exige migrar un proceso ni tener todas las carpetas idénticas.

Preferencias: mínimo trabajo manual, actualización WSL al inicio/cierre, respuesta remota práctica, reutilización de herramientas y recuperación rápida. Almacenamiento adicional es aceptable si reduce RTO o conserva capacidad de ejecutar; no es el eje de puntuación.

**Puerta actual para todas las alternativas:** Horus/bridge no están operativos en la muestra; 24/7, acceso Windows al mismo backend y recuperación completa no están aceptados. Las puntuaciones siguientes corresponden a diseños una vez implementados y probados, no al sistema instalado.

## 2. Alternativas

**A — Workspace único S23.** Clientes remotos comparten filesystem/backend y no replican entorno de desarrollo. Máxima continuidad del mismo hilo cuando el proceso vive y mínima divergencia; requiere conectividad y herramientas ARM/Alpine. **No satisface por sí sola la ejecución local opcional del PC**, requisito obligatorio. Sigue siendo el modo preferido cuando se quiere conservar una tarea/conversación viva.

**B — Dos entornos coordinados simétricos.** WSL y S23 trabajan localmente con sus propios homes Codex/dependencias y entregan commits o paquetes al iniciar/cerrar. Puede usar Git correctamente; no se evalúa como copia ciega. Permite potencia PC/offline, pero exige resolver quién publica, qué base usa cada uno y qué contexto se traslada. No transfiere tareas o conversación viva entre instalaciones.

**C — S23 principal con réplica local opcional.** S23 conserva versión principal disponible; WSL obtiene una base, prepara cambio y lo devuelve validado. Mejora autoridad y recuperación frente a simetría ambigua. Es una base viable, pero una réplica por sí sola no define control de turnos, aceptación por plataforma ni recibos de publicación. Con procedimientos manuales puede ser suficiente para un usuario disciplinado.

**D — C con modo remoto habitual y entregas administradas.** Mantiene A para conservar el backend vivo; usa C cuando se pide ejecución WSL. Añade propietario/época por proyecto, bloqueo de admisión de tareas sobre el proyecto cedido, commit/base y recibos de recepción/ejecutabilidad, handoff de contexto y cápsulas de recuperación por plataforma. Reutiliza SSH/bridge/broker, sin nuevo servidor permanente. Tiene más código de control y un cliente Windows pendiente, pero automatiza las decisiones que C dejaría al usuario.

**Recomendación: D, condicionada a las pruebas y límites de [05](05_ARQUITECTURA_RECOMENDADA.md).** Si no se acepta desarrollar/probar ese control, escoger C con handoff manual explícito, sin prometer automatización ni continuidad de sesión entre instalaciones.

## 3. Puntuación justificada

Escala1–5: 1=desfavorable, 3=viable con restricciones, 5=muy favorable para este caso. En complejidad/mantenimiento/consumo, mayor puntuación significa menor coste operativo. Son juicios comparativos de diseño; no porcentajes ni disponibilidad medida. No se suma un total con pesos inventados que oculte requisitos excluyentes.

| Criterio | A | B | C | D | Justificación comparativa |
|---|---:|---:|---:|---:|---|
| Continuidad del trabajo | 5 | 3 | 4 | 5 | A conserva backend; B cambia de host; D evita cambio cuando no se necesita y formaliza el handoff cuando sí |
| Integridad/consistencia | 4 | 3 | 4 | 5 | D exige base, propietario, CAS y recibo; no se confunde con protección ante procesos no cooperantes del mismo UID |
| Facilidad de uso | 4 | 3 | 3 | 4 | D busca dos acciones explícitas inicio/cierre; su facilidad aún necesita UI/ensayos, no está entregada |
| Autonomía S23 | 5 | 4 | 5 | 5 | C/D no requieren PC para servir versión confirmada; B necesita disciplinar intercambio/autoridad |
| Ejecución correcta | 3 | 4 | 4 | 4 | S23 tiene límites ARM/Alpine; tener dos runtimes no garantiza compatibilidad, se acepta por target |
| Multiplataforma | 2 | 5 | 5 | 5 | A limita herramientas al host S23; B/C/D permiten builds PC y ejecución S23 donde se valida |
| Sesiones Codex | 5 | 2 | 3 | 4 | A mantiene una sesión; D ofrece A o un handoff explícito. Ninguna opción transfiere RAM/tarea viva entre instalaciones |
| Recuperación | 3 | 4 | 4 | 5 | D añade cápsulas, recibos y restauración ensayada; la puntuación es objetivo condicionado, no garantía actual |
| Complejidad operativa | 4 | 3 | 3 | 2 | D añade coordinador lógico/protocolos y cliente Windows; se justifica por prevenir errores repetidos de handoff |
| Mantenimiento | 4 | 3 | 3 | 3 | Dos plataformas requieren locks/toolchains; D añade tests de control, evita nuevos daemons |
| Seguridad | 4 | 3 | 4 | 4 | Credenciales por UID/cliente y exposición privada; no se elimina el riesgo del full-access actual |
| Velocidad de actualización | 5 | 3 | 4 | 4 | A no copia; D tampoco en remoto y transfiere deltas/artefactos confirmados en local; sin latencias medidas |
| Consumo/uso de recursos | 3 | 4 | 4 | 4 | D permite PC para builds pesados y conserva caches útiles; no optimiza a costa de perder dependencias |
| Infraestructura existente | 5 | 4 | 4 | 4 | D reutiliza transporte/runtime, requiere lógica/cliente pendiente; no exige NAS/cloud compute ni Syncthing nuevo |

## 4. Comparación específica de herramientas

| Herramienta | Capacidad real/documentada | Papel recomendado y límites |
|---|---|---|
| FolderSync Android/Desktop | Pares, filtros, conflictos y scheduling/automatización; Drive/SFTP soportados; Android sujeto a permisos | Conservar documental una vez corregido/inventariado. No arbitra Git ni preserva una ejecución viva. UI/configuración de Android aún incompleta |
| rclone copy | Copia y omite iguales; no elimina extras, **puede reemplazar destinos cambiados** | Artefactos/backup con nombres/IDs únicos y verificación; copy solo no es versionado ni append-only. [Manual](https://rclone.org/commands/rclone_copy/) |
| rclone sync | Hace coincidir destino, con borrados si corresponde | Solo espejo reconstruible con autoridad definida; no checkout activo ni backup único. [Manual](https://rclone.org/commands/rclone_sync/) |
| rclone bisync | Dos vías, listados previos/conflictos/recuperación; resync tiene otra semántica | Revisar árboles actuales; no usar para sincronizar homes Codex/DB/Git vivos. Umbral borrado porcentual en1.75.2. [Manual](https://rclone.org/bisync/) |
| rclone mount | Vista VFS/FUSE con caché y traducción de permisos/enlaces | No elegir como disco principal de Git, DB o deps activas; Android/PRoot no acredita FUSE, locks remotos ni POSIX. [Manual](https://rclone.org/commands/rclone_mount/) |
| Git local/remoto | Objetos, refs, historial, branches, merge y rechazo/CAS | Autoridad propuesta del fuente; repositorios independientes, fetch/push/bundles. No copiar `.git` vivo ni asumir que incluye datos externos. [Bundle](https://git-scm.com/docs/git-bundle), [update-ref](https://git-scm.com/docs/git-update-ref) |
| rsync sobre SSH | Transferencia incremental, preservación de atributos según opciones/capacidades; ambos extremos necesitan herramienta | Útil para staging de datos/exports coherentes, después de inventario. No consistencia multarchivo, no controlador de dos escritores. [Manual](https://download.samba.org/pub/rsync/rsync.1) |
| SSH/SFTP | Ejecución/acceso privado ya parcialmente disponible | Transporte preferido; no obliga daemon nuevo. Acceso Horus desde Windows requiere identidad/autorización pendiente; no confundir SSH Termux con permiso privado Horus |
| Syncthing | Replicación P2P y conflictos; motor distinto de wrapper Android | No seleccionado: añade servicio/estado continuo, no acceso mágico a UID Horus ni sesiones/procesos. Wrapper Android oficial retirado; evaluar cualquier fork por separado. [Anuncio del mantenedor](https://forum.syncthing.net/t/discontinuing-syncthing-android/23002), [FAQ](https://docs.syncthing.net/users/faq.html) |
| Archivos/snapshots consistentes | Guardan bytes/metadata de una generación cerrada | Backup por target y restauración; no Docker/VM/FS snapshot disponible presumidos en PRoot. Para DB usar mecanismo del motor. [SQLite](https://sqlite.org/backup.html) |

Mantenimiento consultado: rclone 1.75.2 aparece en changelog oficial del 09/10/2026 y coincide con lo instalado; Horus 1.0.4 aparece como release de app disponible, con fuente/APK comprobados. Los manuales vigentes de Git/rsync/npm/Python describen capacidades, no certifican soporte Android de toda su cadena. La CLI FolderSync está documentada como componente distribuido aparte; no se acreditó su disponibilidad ni se lanzó para descubrir configuración. **No recomendar instalación/actualización basándose solo en que exista una versión/documentación nueva.**

## 5. Alternativas descartadas y reconsideración

A sola se descarta por impedir usar potencia local PC; se conserva como modo. B se descarta como política principal porque dos centros simétricos complican autoridad y contexto sin beneficio frente a D para un S23 permanente. C es fallback viable si se acepta handoff manual. D se elige por combinar acceso al mismo backend con publicación por sesión y recuperación, no por tener más sincronizadores.

Se descartan por ahora espejos completos de homes, dependencias x86 sobre ARM, Drive mount como disco operativo, multi-master de `.git`/DB y un nuevo host permanente. No se selecciona VS Code Remote-SSH como interfaz garantizada del Horus actual: [Microsoft excluye hosts Alpine/non-glibc de ese modo](https://code.visualstudio.com/docs/remote/ssh). SFTP/terminal o cliente MESTRY compatible son alternativas a validar; cambiar a Debian solo por el editor necesitaría otra decisión.
