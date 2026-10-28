# Evidencia de auditoría S23 para servidor dedicado

Fecha: 2026-10-20. [Informe interpretado](../../S23_SERVER_AUDIT.md). Todas las consultas del agente al teléfono fueron de lectura, como shell ADB o UID Termux; los archivos se escribieron en WSL.

| Grupo | Intervalo UTC | Contenido |
|---|---|---|
| `manifest.json` | 03:44:17–03:45:38 | 47 sondas iniciales, inventario y tres muestras de memoria |
| `followup_manifest.json` | 03:46:20–03:51:18 | 22 sondas, metadata activa corregida, CPU, políticas y continuidad |
| `boot_update_manifest.json` | 03:52:32–03:53:07, ver timestamps exactos del manifest | 12 sondas tras la instalación de Boot por el usuario; el agente no lo instaló ni configuró |

Los manifests conservan comandos, tiempos, canal, código de salida y hash de cada salida minimizada. Un código 0 de una consulta compuesta no invalida un stderr de un subcomando. Tres sondas devolvieron no cero: batería sysfs, zRAM con atributos parcialmente denegados y `check-signatures` no soportado. Existen otras denegaciones parciales conservadas en las salidas.

`packages_*`, `package_metadata_current.txt` e inventario/resumen sin sufijo son el momento inicial: **488 APK / 485 sistema / 3 usuario / 23 deshabilitados**. `boot_packages_*`, `boot_package_metadata.txt` y CSV/JSON con sufijo `_current` son posteriores a la instalación de **Termux:Boot por el usuario**: **489 / 485 / 4 / 23**. La diferencia es solo `com.termux.boot`, sin cambios en el conjunto deshabilitado.

`package_metadata.txt` inicial no debe usarse para versiones activas: el primer parser sobrescribía APK actualizados con versiones ocultas de ROM. Se conserva por trazabilidad, marcado como sustituido en el manifest. La extracción corregida se reconcilió contra los versionCode de `pm list` para los 488/489 paquetes.

Los datos de `sample_00`–`sample_02`, procesos PSS/RSS y CPU son anteriores a Boot. El CSV actual conserva esos valores como observación inicial, con `memory_snapshot` explícito; campos de memoria vacíos significan **no observado**, no consumo cero. La muestra `boot_memory.txt` es posterior a la interacción del usuario: no es un ensayo controlado del coste de Boot.

`collector_initial.py` y `collector_metadata_fix.py` son revisiones históricas verificadas contra los hashes del primer y segundo manifest. Para repetir se usa el recolector final, con minimización de batería más estricta, y el analizador final, también disponibles en `tools/` del proyecto. Las consultas suplementarias adicionales se pueden repetir usando los comandos de sus manifests. No existe un ejecutor de desinstalación o cambios de ajustes en este paquete.

`applications_inventory_current.csv` es el inventario clasificado recomendado para revisión; `removal_candidates_current.csv` contiene las 26 candidatas condicionales, 7 del primer lote propuesto. Las clases conservadas como esenciales incluyen conservación preventiva de recursos/OEM y no certifican indispensabilidad individual. Ninguna candidata fue deshabilitada por el agente.

`SHA256SUMS` cubre todos los archivos de este directorio excepto el propio archivo de sumas. `verification.json` recoge las comprobaciones de integridad, reconciliación y documentación realizadas al cerrar la entrega. No contiene secretos; el inventario de aplicaciones sigue siendo información del dispositivo y se mantiene en la documentación local del proyecto.
