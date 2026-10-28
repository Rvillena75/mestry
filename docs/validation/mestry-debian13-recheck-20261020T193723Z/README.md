# Recomprobación de Debian y acceso desde WSL

**2026-10-20, 19:37 UTC / 16:37 de Santiago. Resultado: PASS.** El entorno ya estaba instalado y documentado; no se reinstaló ni se avanzó de fase. Esta evidencia complementa EXP02 y conserva los avances posteriores EXP03–EXP05.

| Sonda | Resultado |
|---|---|
| c01 | WSL → SSH por clave → `mestry-debian` → `mestry-check`: Debian 13.7 ARM64, APT 3.0.3, DNS/HTTPS 200, archivos y procesos correctos, UID real Android 10348 y capacidades 0 |
| c02 | ADB Windows enumera un SM-S918B autorizado; shell UID 2000 y modelo comprobados. Serial omitido |
| c03 | Estados de batería/Boot, Doze, notificaciones, RAM Plus, protección de carga y arranque consultados; 28 APK deshabilitados, iguales al conjunto preexistente de EXP03 |

[Comandos exactos y salidas](commands.md), [manifest con hashes de cada ejecución](manifest.json), [resumen estructurado](summary.json), [verificación local](review.json), [huellas del anexo](SHA256SUMS).

La [consulta SSH de las 19:33 UTC](../mestry-debian13-20261020T040726Z/s21_final_ssh_and_inventory.record.json) quedó anexada al registro original con nombre propio. Confirma autenticación exclusivamente por claves, archivos SSH/Boot conservados, inventario y recursos: **3,016 GiB de RAM disponible y 212,031 GiB de datos libres**. Tenía Termux:X11 y xterm preexistentes activos; estas cifras describen el teléfono completo y no el coste incremental de Debian mínimo.

Antes de esa consulta, `s20_final_android_guards` devolvió **1** durante la selección local ADB: `Expected exactly one authorized SM-S918B.` Su [script preparado](../mestry-debian13-20261020T040726Z/s20_final_android_guards.sh) **no se ejecutó en el teléfono**; el logger no produjo stdout, stderr ni registro por salir en ese preflight. El error y el mtime de preparación se recogen como observación en `summary.json`, sin atribuirles una hora de ejecución remota. c02/c03 demostraron después que ADB respondía; la causa transitoria no se determinó.

No hubo reinicio, recarga de SSH, arranque/parada de X11, instalación/desinstalación, cambios de permisos, parámetros Android o APK. El check crea y elimina su fixture temporal de archivos y espera un proceso hijo. No se reiniciaron las pruebas del sandbox ni se instalaron gráficos o Codex en esta continuación. Boot tras primer desbloqueo y recuperación totalmente automática siguen pendientes.

Los cierres históricos y sus hashes se conservan como resultados de su fecha; no representan el inventario posterior de X11. `review.json` vuelve a comprobar los hashes de los scripts/salidas del manifest original, además de este anexo, sin reinterpretar los SHA de documentos que cambiaron en fases posteriores. El informe de operación y recuperación completo está en [INSTALLATION_LOG](../../INSTALLATION_LOG.md).
