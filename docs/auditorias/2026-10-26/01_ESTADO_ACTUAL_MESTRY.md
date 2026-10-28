# MESTRY — Estado actual auditado

Fecha local: **2026-10-26**, America/Santiago (UTC−03:00). Inspección iniciada a las **17:52:30**. Autoridad de este informe: observación local y evidencia histórica identificada; no sustituye decisiones congeladas.

## Resumen ejecutivo

MESTRY dispone de una **infraestructura de desarrollo móvil con un piloto funcional documentado**: Codex en Horus/S23, cliente Android S25, bridge de app-server, acceso privado y capacidades acotadas de consulta/publicación en Drive. Los registros del 20–22 de octubre contienen pruebas reales, verificaciones independientes y límites explícitos. El usuario confirma que Codex funciona satisfactoriamente. **El asistente ambiental MESTRY Core, voz, routers, RAG y conectores generales no quedan acreditados por ese piloto.**

Durante esta auditoría se verificaron directamente los archivos WSL, configuración y registros de sincronización, instalación/configuración persistida de FolderSync Desktop, fuentes reproducidas y pruebas locales. **No hubo acceso actual a S23/S25:** ADB sin dispositivos, SSH LAN sin ruta y TCP a la dirección privada del S23 agotado. Drive no devolvió las carpetas históricas mediante el conector de esta sesión. No se atribuye ese resultado a eliminación ni a una avería del teléfono.

Los hallazgos prioritarios son: sincronización de árboles de desarrollo completos; FolderSync Desktop sin éxito final en sus cuatro registros consultados; falta de Git en el directorio principal; cinco documentos arquitectónicos originales no localizados; y documentación general que conserva estados superados. No se confirmó pérdida documental ni filtración de credenciales.

El siguiente objetivo recomendado es **cerrar el mapa de autoridades y sincronización, preservar una línea base de código y aceptar una lectura documental mínima de extremo a extremo con el broker existente**. No requiere reinstalar Codex, introducir otro servidor ni descargar modelos.

## Contexto y alcance

| Campo | Resultado | Evidencia |
|---|---|---|
| Directorio principal | `/home/developer/proyectos/mestry`, directorio real, sin enlaces simbólicos dentro del árbol | E01 |
| Repositorio / rama / commit principal | **No existe `.git`**; los tres conceptos no son aplicables. `git status` y `git log` fallan por ausencia de repositorio | E01 |
| Base del cliente Android/bridge | Upstream `chenhaoc/codex-remote-control`, commit de procedencia `538d65f67e34907789237fc71f56e8ca95d9f3cb`; parche local y 68 huellas | E04 |
| Entorno actual | Ubuntu 24.04 sobre WSL2, x86_64, kernel `6.18.33.1-microsoft-standard-WSL2`; Windows 11 Home Single Language, build 26300 | E01, E11 |
| Dispositivos de referencia | S23 Ultra SM-S918B / dm3q y S25 Ultra SM-S938B, identificados históricamente; **no conectados durante esta auditoría** | E07, E08, H01–H04 |
| Inventario inicial | 1.803 archivos, 66.129.015 bytes, antes de crear estos cinco informes | E01 |
| Fuente congelada disponible | Un documento de los seis solicitados: arquitectura Drive/sincronización/RAG | E02, E03 |
| Pruebas actuales | **81 casos seleccionados correctos: 78 Python y 3 Node**, sin inferencia ni conexiones reales a teléfonos/Google; 34 fuentes Python analizadas sintácticamente | E06 |

Se inspeccionaron configuración, registros y código accesible. No se ejecutaron sincronizaciones, instalaciones, compilaciones, OAuth, turnos de modelo, publicaciones, pruebas de escritura en Drive ni pruebas de reinicio/fallo. Las consultas remotas de metadata de Drive fueron de lectura. Los registros históricos se conservaron intactos.

## Cómo interpretar los estados

| Estado | Uso en esta auditoría |
|---|---|
| **APROBADO / CONGELADO** | Decisión normativa disponible, no una prueba de implementación |
| **IMPLEMENTADO Y VERIFICADO** | Código/comportamiento con evidencia, indicando lugar, fecha y alcance. Cuando dice «histórico», no certifica disponibilidad actual |
| **CONFIGURADO / NO VERIFICADO** | Configuración encontrada sin aceptación funcional vigente; una ejecución fallida se describe expresamente |
| **REPORTADO POR USUARIO** | Confirmación humana que esta auditoría no repitió independientemente |
| **PROPUESTO** | Recomendación o diseño sin autorización nueva de implementación |
| **PENDIENTE** | Implementación, decisión o criterio de aceptación sin cerrar |
| **BLOQUEADO / SIN ACCESO** | Recursos no accesibles desde esta sesión; no equivale a recurso averiado o inexistente |

Los identificadores E y H remiten al [registro de evidencias](05_EVIDENCIAS_Y_PRUEBAS.md). Para decisiones y componentes véase [trazabilidad](03_TRAZABILIDAD_ARQUITECTONICA.md); para rutas y flujos, [infraestructura](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md).

## Qué existe y hasta dónde funciona

| Capacidad | Estado sustentado | Límite |
|---|---|---|
| Codex CLI en Horus/S23 | **REPORTADO POR USUARIO** actualmente; **IMPLEMENTADO Y VERIFICADO**, histórico 20–21/10: versión 0.163.0, tareas sintéticas y lectura independiente de resultados | No se ejecutó ni reinstaló durante esta auditoría; S23 actual sin acceso. H01, H02 |
| Entornos Android/Linux | **IMPLEMENTADO Y VERIFICADO**, histórico: Termux, Debian 13/PRoot y X11 mínimo; Horus 1.0.4 con Alpine 3.24.0/aarch64 | Debian/X11 son rutas conservadas; Codex validado está en Horus. No fusionar sus homes ni sus credenciales. H01, H05 |
| App Android S25 | **IMPLEMENTADO Y VERIFICADO**, histórico: piloto8 / 10008 instalado conservando firma/datos; código local de 68 archivos coincide hoy con el manifiesto | No es la app final del asistente ambiental ni un cliente multiproyecto general: piloto limitado al proyecto sintético. E04, H02–H04 |
| Bridge e historial | **IMPLEMENTADO Y VERIFICADO**, histórico: app-server real, interrupción comprobada en servidor, recuperación sin caché objetivo y sincronización fresca celular | No se probó hoy el proceso, túnel o historial del teléfono. H02–H04 |
| VPN y supervisión | **IMPLEMENTADO Y VERIFICADO**, histórico: Tailscale, hello real, apagado tras salida, desconexión manual y watchdog saludable | Tarea activa real, muerte del UID, reinicio, cargador de pared/PC apagado y 24 h siguen **PENDIENTES**. H04 |
| Navegador Drive acotado | **IMPLEMENTADO Y VERIFICADO**, código/pruebas actuales; consulta de raíz y controles S25 históricos | Raíz del piloto devolvía cero documentos autorizados; subcarpetas/previews probados con fixtures. No indexa ni sincroniza el workspace. E05, E06, H03 |
| Publicador Drive acotado | **IMPLEMENTADO Y VERIFICADO**, histórico: dos revisiones privadas, hashes y deduplicación | Destino antiguo `Review/Horus` consta en papelera por decisión humana posterior; escritor no redirigido. No usarlo como salida operativa vigente. H03, H06 |
| rclone WSL | **CONFIGURADO / NO VERIFICADO** como operación actual; log del 22/10 registra `Bisync successful` para dos raíces | Último éxito histórico no prueba estado cloud del 26/10. No se encontró programación MESTRY en cron/timers/tareas examinados. E09, E10 |
| FolderSync Windows | **CONFIGURADO / NO VERIFICADO**, instalado 2.13.0.0 y un par habilitado | Filas consultadas: una cancelación y tres fallos; cero finalizaciones exitosas. E11, E12 |
| FolderSync S23 | **REPORTADO POR USUARIO** | Pares, permisos, rutas, horario y políticas **BLOQUEADOS / SIN ACCESO**. No se infieren desde Windows. E07, E08 |
| Google Drive conectado a esta sesión | **BLOQUEADO / SIN ACCESO** a las raíces históricas consultadas | Búsquedas MESTRY/Jarvis vacías y metadata de dos IDs con 404. No determina cuenta efectiva ni estado remoto actual. E13 |
| MESTRY Core / RAG / voz / agentes | **PENDIENTE** en el código inspeccionado | No se encontró implementación integrada. Estado completo de apps/archivos privados del teléfono sin evaluar. E04, E05, E07, E08 |

## Organización actual y control de versiones

El árbol principal contiene el ADR Drive, `README.md`, 22 documentos directos en `docs/`, paquetes de evidencia bajo `docs/validation/` y herramientas bajo `tools/`. No contiene `.gitignore`, manifiesto global de dependencias, CI ni historial Git propios. Por ello no es posible enumerar «cambios sin confirmar» ni establecer un commit de MESTRY: sería inventar una referencia.

Las fuentes completas del cliente/bridge viven fuera del árbol principal, en varias copias de `~/.cache/mestry/`. La copia piloto8 contrastada es `~/.cache/mestry/s25-auto-vpn-20261022T034500Z/reproduced-pilot8`. Tampoco tiene `.git`. El parche acumulado y `source-pins.json` sí están en `tools/s25-codex-client/`: **68/68 huellas coinciden y el SHA-256 del parche coincide**. Es trazabilidad útil de artefactos, pero no un sustituto del historial de desarrollo.

Python sirve para broker, publicación, diagnóstico y supervisión; Node ESM para bridge/políticas; Kotlin/Compose y Java/OkHttp para cliente Android. Hay shell/PowerShell para experimentos y recuperación. Los paquetes de validación son **evidencia y scripts históricos**, no una colección de comandos que deba volver a ejecutarse. Las múltiples copias en caché representan estados de experimentos; no se confirmó que sean servicios duplicados en ejecución. E01, E04–E06.

Los repositorios `.git` vecinos de `app_fotos` y `app_gastos` son proyectos distintos; no se les atribuye la rama o el commit de MESTRY. Sus metadatos aparecen en los listados históricos de sincronización por compartir la raíz `proyectos`. E10.

## Hallazgos y riesgos

No se confirma un incidente de severidad crítica consumado. Los riesgos de pérdida o exposición se clasifican por alcance/evidencia, sin afirmar que ya ocurrieron.

| ID | Severidad | Hallazgo, impacto y evidencia | Tratamiento propuesto, sin aplicar |
|---|---|---|---|
| F01 | Alta | rclone usa `bisync` sobre `IPRE` y **todo `proyectos`**; el listado remoto histórico incluye 5.066 entradas con `/.git/` y 5.655 con `/build/`. Filtros sin exclusión explícita de `.git`, build ni secretos. Un borrado/cambio puede alcanzar copias compartidas; `--max-delete 20` es un límite, no bloqueo total. E09–E10 | Acordar autoridad por árbol, exclusiones y retención; revisar un plan de diferencias antes de aprobar cambios o cualquier `resync` |
| F02 | Alta | FolderSync Desktop: par TwoWay sin filtros, checksums deshabilitados, 143.882 registros de archivos y cuatro ejecuciones sin éxito final; inventario con 97.320 claves que coinciden con `/node_modules/`, 10.482 con `/build/` y 2.637 con `.git/`. No se puede asumir réplica completa ni íntegra. E12 | Diagnóstico de fallos y alcance; decidir qué datos sí pertenecen a Drive; no repetir transferencia masiva automáticamente |
| F03 | Alta | Directorio principal sin Git y fuentes completas en cachés; riesgo de perder autoría, evolución o artefactos al limpiar caché. Las huellas preservan una base parcial. E01, E04 | Aprobar una línea base de código versionada y excluir datos/credenciales antes de crear repositorio o mover fuentes |
| F04 | Alta | Cinco de las seis fuentes arquitectónicas no localizadas; no es posible auditar íntegramente etapas, teclado y broker original. E02 | Recuperar originales por ID/ruta y registrar su autoridad, conservando nombres históricos |
| F05 | Alta | Sin acceso actual al S23/S25 y sin ensayos completos de reinicio, PC apagado o 24 h. Un piloto breve no acredita operación autónoma. E07–E08, H04 | Recuperar acceso de lectura con identidad verificada; ensayos físicos separados y autorizados |
| F06 | Alta | Piloto fija `never / dangerFullAccess`, aceptado previamente por el usuario. ACL del bridge no limita el shell/las herramientas de Codex al proyecto como un sandbox del SO. E05, H03 | Mantener la aceptación acotada al piloto; revisar frontera antes de incorporar repositorios o documentos sensibles. No revertir políticas durante esta auditoría |
| F07 | Media | README indica app pendiente de instalar; evidencias posteriores acreditan piloto8. R2 dice «ninguna arquitectura aprobada» mientras el ADR Drive declara decisiones congeladas. H03–H04, E03 | Usar este informe como índice de estado; futura actualización documental separada, sin alterar congelados |
| F08 | Media | Publicador conserva destino antiguo en papelera y allowlist de un fixture. Asignar otra raíz en el navegador no cambia el escritor. H03, E05 | Aprobar destino y documento concretos antes de reanudar publicaciones; no restaurar ni redirigir automáticamente |
| F09 | Media | rclone declara scope `drive`; piloto Termux declara `drive.file`. Son conexiones distintas sin correspondencia de cuenta verificada. El conector actual no resuelve las raíces históricas. E09, E13, H03 | Identificar conexiones mediante comprobaciones privadas de igualdad; no ampliar scopes ni reautorizar por el solo 404 |
| F10 | Media | Falta evidencia de respaldo independiente, restauración probada y control entre todos los editores/sincronizadores. `flock` solo coordina el script WSL. E09, E12 | Definir retención/restauración y matriz de escritores antes de habilitar más escritura |
| F11 | Baja | SuperDisplay está **Running/Automatic** en Windows; el 22/10 había quedado Stopped/Auto. No se conoce la causa del cambio; su arranque automático ya estaba advertido. E11, H03–H04 | Registrar deriva operacional; no detenerlo ni modificar su recuperación durante esta tarea |
| F12 | Baja | La consulta `adb.exe devices -l` inició automáticamente el daemon ADB Windows, que estaba detenido. Contraviene la restricción de no modificar procesos, aunque no contactó teléfonos. E07 | Declarar la excepción; futuras auditorías deben comprobar el proceso/puerto existente antes de invocar ADB |

## Matriz de avance real

Se distingue progreso de infraestructura de desarrollo de capacidades del producto. **No se asignan porcentajes.**

| Área | Infraestructura / evidencia | Producto y brecha | Estado de cierre |
|---|---|---|---|
| Documentación y arquitectura | Un ADR congelado disponible, informes y handoffs extensos | Faltan cinco fuentes y reconciliar estados generales | **PENDIENTE**; 1/6 fuentes originales localizadas |
| Entorno S23 | Termux/Horus/Alpine y rutas Debian/X11 con evidencia histórica | Salud, recursos y persistencia actuales sin lectura | **BLOQUEADO / SIN ACCESO** hoy |
| Codex | Usuario satisfecho; tareas verificadas históricamente; sin reinstalación necesaria | No demuestra el asistente ambiental ni autonomía 24/7 | **REPORTADO POR USUARIO** hoy; funcionamiento histórico verificado |
| Sincronización documental | Script WSL, par Windows y logs reales | Mapa S23/S25 incompleto; fallos Windows; aceptación cloud pendiente | **CONFIGURADO / NO VERIFICADO** |
| Control de versiones | Upstream, parche y 68 hashes disponibles | Sin repositorio principal ni historial de cambios | **PENDIENTE** |
| MESTRY Core | No localizado en fuentes inspeccionadas | Orquestación, contratos y servicio de producto por implementar | **PENDIENTE** |
| Interfaces | Cliente de desarrollo S25 con evidencia de uso | Voz/teclado/overlay del producto no localizados | Piloto **IMPLEMENTADO Y VERIFICADO**, histórico; producto **PENDIENTE** |
| Modelos e inteligencia | Codex remoto a su proveedor funcionó en tareas sintéticas | Sin Free Model Broker, Reasoning Engine ni inferencia local MESTRY acreditados | **PENDIENTE** para producto |
| Integraciones | Broker Drive de catálogo limitado y publicador de prueba | DriveConnector integral, Calendar/Canvas/Gmail/notas/tareas no localizados | Pilotos verificados; integración general **PENDIENTE** |
| Seguridad | Código con autenticación, validación de rutas y separación de UIDs; pruebas actuales | Política global, auditoría/retención y conflictos entre sincronizadores sin cerrar | **PENDIENTE** aceptación integral |
| Pruebas | 81 casos locales actuales; ensayos sintéticos reales históricos | Sin suite de aceptación del asistente/Core, corpus real, Doze/reinicio/24 h | **IMPLEMENTADO Y VERIFICADO** solo dentro de las suites identificadas |
| Operación autónoma | Procesamiento local S23 probado históricamente; SSH/VPN y watchdog ensayados parcialmente | PC apagado, alimentación estable, recuperación de UID/Boot y larga duración sin aceptar | **PENDIENTE**, no declarado 24/7 |

Los 12 criterios AC-01–AC-12 del ADR no tienen cierre integral actual: **0 cerrados; 12 abiertos**, con subcapacidades documentadas y limitaciones detalladas en [03](03_TRAZABILIDAD_ARQUITECTONICA.md). Esto no borra los avances del piloto ni equivale a cero trabajo realizado.

## Limitaciones y continuidad

No se leyeron configuraciones privadas actuales de Android, pares FolderSync S23, credenciales, historial personal ni documentos del corpus. Las consultas a FolderSync Windows usaron SQLite `mode=ro&immutable=1`, con DB/WAL/SHM existentes y sin checkpoint; no se acredita cobertura de todos los frames WAL pendientes. Se documenta la imagen persistida observada, no el estado en memoria de la aplicación.

La ausencia local de código y los resultados vacíos del conector no prueban ausencia global. Las dependencias se inventariaron por versiones declaradas; no se consultó un registro de vulnerabilidades ni se calificó un paquete como obsoleto por antigüedad. No se verificaron permisos cloud actuales ni se certificó restauración documental.

El [plan de continuidad](04_PLAN_DE_CONTINUIDAD.md) ordena las siguientes tareas, sus dependencias, aprobaciones y evidencia de cierre. Primero asegurar documentos y línea base; después aceptar lectura mínima sobre un archivo autorizado; finalmente ampliar producto sin confundir herramientas de desarrollo con MESTRY Core.

## Integridad de la auditoría

Los únicos archivos añadidos al árbol MESTRY fueron los cinco Markdown solicitados. El [control final](05_EVIDENCIAS_Y_PRUEBAS.md#control-final) registra comparación del árbol original y configuraciones protegidas. No se reconfiguraron Codex, sincronizadores ni teléfonos. **Existe una excepción explícita al requisito de no modificar procesos: el arranque automático del servidor ADB host durante la primera enumeración.** No se lo detuvo ni se realizaron más operaciones de control de procesos para ocultar esa desviación.
