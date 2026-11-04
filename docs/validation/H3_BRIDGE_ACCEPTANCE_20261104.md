# H3: aceptación de una revisión nueva por bridge y tarea S25

Fecha: **04/11/2026**. Criterios obligatorios **PASS**. Evidencia bruta,
identificadores y recibos completos conservados en estado privado, fuera de Git.
Esta aceptación corresponde al candidato `791688abdd59afb33516916c9e031c94553e02c5`.

| Criterio | Recibo observado |
|---|---|
| SHA nativo anterior | `dc3a872a839295e6c4d65ef2b67eab3dcba90f30`, limpio/libre/idle |
| SHA nuevo, distinto | `791688abdd59afb33516916c9e031c94553e02c5` |
| Aplicación | `session.start` del bridge; `applied_new_revision=true`; ninguna entrada CLI lo aplicó antes |
| Validación antes del fast-forward | **155 tests** de las ocho suites en Alpine ARM64; árbol `46026a14ed4088ddf4e663d8926a807202ca986d` |
| Tarea real S25 | Lecturas AGENTS.md/STATUS.md del proyecto real y `git rev-parse HEAD` con el SHA esperado |
| Concurrencia durante ese turno | `receive --fetch-only`: BUSY/salida 3 |
| Preview durante ese turno | `--within-turn finish README.md`: OK, `index_unchanged=true`, publicación no solicitada |
| Recibos adicionales | Cuatro tests Node correctos, ejecutados por la tarea en el target |
| Terminación | Mismo turno `completed`, sin turnos activos; lock liberado |
| Recuperación del hilo | Cierre del proceso y reapertura con el mismo ID; `session.content` fresco y recibos recuperados |
| Estado nativo final | SHA esperado, limpio/libre/idle, validación coincidente, sin recuperación ni candidato fallido |

**159 tests por target**: WSL validó las ocho suites (**54/4/28/13/3/40/9/4**)
y cuatro tests de recibos; ARM64 validó esas ocho suites antes de aplicar y
S25 ejecutó los cuatro de recibos. No se usan los 137/148 resultados históricos
para acreditar el candidato. El límite workflow de 600 s y todos sus casos se
conservaron; no se instalaron paquetes.

## Transición revisada y preservación

El candidato mantiene la huella nativa de dependencias anterior
`ccd7a7f3068531fa87c2bad73c1416a9174d2d2dd3026c395c6edddbacfca080`.
Los pins/parche Android piloto 9 quedan locales; no se migraron dependencias.
Se revisaron explícitamente los únicos dos controles protegidos cambiados:

- `tools/work_session.py`: `da63b8a729a815a3f13073126a29bb765b6593bd3f4df51c3bd45eb91064326f`.
- `tools/test_work_session.py`: `ca7cf14d002cc51f8333b9528fdaa9a81d7f090ce473e37328490e37a2be62db`.

La política futura exacta se preparó antes de recibir, limitada a esos hashes.
Un launcher privado temporal, fijado por hash y limitado a la entrada `lease`
del bridge, permitió validar el candidato conservando la versión operativa.
Solo tras validar y aplicar por el bridge se promovió el blob previamente
revisado. No se ejecutó `configure` automático para quitar un bloqueo ni se
aplicó el candidato por CLI. Se retiró ese PATH temporal antes de la tarea S25;
se conservaron política anterior y rollback. Contrato, identidad, dependencias,
release instalada, índice, claves, pairing e hilos se preservaron.

APK piloto 9 / 10009, release privada del bridge, checkout aceptado y fuentes
locales son referencias distintas. La publicación posterior de este recibo
actualiza GitHub; no acredita otra recepción del checkout S23.

## Intentos previos y correcciones

1. El intento inicial conservó `4865d2c…`. ActivityManager registró recorte de
   procesos a **03:09:55.979 UTC** y terminó SSH/PRoot. Se recuperó el helper
   existente y se reinició el bridge propio tras verificar cero turnos y
   aprobaciones. `max_phantom_processes=32` se mantuvo. Esto no establece la
   causa de las señales del 03/11.
2. El segundo intento aplicó `dc3a872…`, pasó **141 tests ARM64** y completó
   sus recibos, pero dejó recuperación: **INCOMPLETE**, sin aceptación. La
   revisión manual de esa marca comprobó turno terminal, checkout limpio,
   validación coincidente, sin lease y cero turnos/aprobaciones, con backups.
3. La recepción de `197aa5b…` fue rechazada por workflow; no hubo aplicación
   ni turno nuevo. Dos casos temporizados y una repetición completa de **38
   tests nativos en 339,498 s** pasaron. No se capturó el fallo original y no
   se inventa una causa. Su registro solo se limpió por validación completa
   correcta del candidato siguiente.
4. El cuarto intento aceptó `791688abdd59afb33516916c9e031c94553e02c5`. Ni ese turno ni la tarea S25 necesitaron
   reparar después el estado para conseguir el resultado final.

Se reprodujeron dos carreras de snapshot anterior al lock, con regresiones que
fallan antes y pasan después: falsa recuperación al liberar limpiamente y
recuperación real que podía quedar oculta. La CLI carga ahora bajo lock. La
entrada fetch-only del supervisor existente usa también `atomic_project_poll.py`;
conserva BUSY y recuperación real. No se capturó la instrucción exacta que marcó
la incidencia nativa anterior. El validador conserva ahora salida privada y
acotada de la regla fallida, sin volcarla en el estado público.

El worker privado pasó de SHA-256
`1509ce759bc4a53bea58c259a81e3c950221a57d6321177c4915729d055cd63e` a
`230815316be3e556f127eb6aa6a2db251fd09f691f18d230891e5824cccaa9e5`;
el helper coincide con
`f6c4d32ae5872b3446d4ed3b0c4f94c14d182e892af829c93ee5e30df42172c0`.
`updated_keeper_source` reproduce esa sustitución. Se conservan servicio,
intervalo y rollback; no se añadió otro supervisor.

Interrupción complementaria aceptada en otro turno de espera: gesto normal sobre el control dinámico, turno identificado `interrupted`, actividad fresca y cero turnos activos.

## Fuera del cierre obligatorio

El cambio directo Wi-Fi/datos, residencia de procesos y disponibilidad prolongada
siguen separados del recorrido aceptado. La conexión SSH nueva por datos tenía
aceptación previa. Se restauró el tag temporal S25; no se alteraron redes,
protecciones Android, puertos, claves, OAuth, Drive, FolderSync o rclone.
No se reinstalaron APK, Alpine o Codex. **H4/H5 siguen expresamente pendientes**:
no se acreditan PC apagado, reinicio ni una campaña de 24 horas.


## Integridad de los recibos privados

Los nombres y SHA-256 siguientes permiten cotejar la evidencia conservada sin
publicar capturas, conversaciones ni identificadores. El recibo nativo terminó
a 13:39:04.682 UTC; S25 reabrió el mismo hilo a 23:36:08 UTC. La interrupción
corresponde a otro turno de espera y el check final posterior confirmó reposo.

| Evidencia seleccionada | SHA-256 |
|---|---|
| `native-fourth-entry-receipt.png` | `c67bbed7bbb4c9b3b8e7aadbf4d0fbb347c8b033a098b6fc6ee2c2f788c32905` |
| `native-fourth-receipt.png` | `cf6c851e3b41c217155a7e687395d63e2e5840b526e06d464e53cba8adb49dba` |
| `core-receipts.json` | `2863dac22b47a4b96e866ea563aec9f58fa9ef04d46ad8bb12af856d148ac42f` |
| `reopen-result.json` | `e994d57d998472bd423acd2204f137210ef91d44d5902ae0d3a634be3376320a` |
| `interrupt-current.json` | `6fc32ab66fffd0001b0e22abab43eb47e6f712fc3dbaaf6ab8c9d9a8bff869e3` |
| `native-final-after-s25.png` | `9b6cc72f69fc244b71de743ff338e7986d5553fb8fd3a600710158d8e977c48e` |
