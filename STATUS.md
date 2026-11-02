# Estado para continuar MESTRY

Actualizado: **02/11/2026**. Autoridad de código y documentación técnica: este
repositorio. Originales seleccionados: Google Drive según el ADR congelado.

- **H0:** cerrada históricamente con límites documentados; no repetir auditoría.
- **H1:** laboratorio privado validado WSL/S23, SHA final común y ocho tests por
  target. Dos contextos Codex independientes, sin inferencia de agentes reales.
- **H2, cerrada en WSL:** flujo local `start/finish/receive/check`, comprobador de entorno y
  política revisada implementados. [Guía operativa](docs/WORK_SESSIONS.md) y
  [evidencia H2](docs/investigaciones/2026-10-26_codex_24x7/14_H2_FLUJO_TRABAJO.md).
- **H3, nodo S23 verificado; cliente S25 pendiente:** recepción automática real
  mediante `start`, 137 tests ARM64 y tarea nueva de Codex sobre `bdf3e4c`.
  La recepción concurrente devolvió `BUSY`; el preview `--within-turn finish`
  funcionó con índice intacto. Al terminar: `idle`, limpio, libre y sin candidato
  fallido. Push S23 `f0df88d` y recepción WSL ya comprobados.
  [Registro H3](docs/investigaciones/2026-10-26_codex_24x7/15_H3_NODO_S23.md).
- **Siguiente acción H3:** verificar una conversación nueva, recepción y lock
  a través del bridge/cliente S25. La aceptación CLI del S23 no sustituye esa
  prueba física. No repetir H0/H1/H2 ni reinstalar el entorno.
- **Corrección S23:** el helper atiende cancelación con esperas acotadas;
  reproducción antes/después y aceptación ARM64 completadas, con el mismo plazo
  de cierre de 15 s y todos los tests conservados.
- **H4/H5:** autoridad/recuperación documental y ensayos prolongados pendientes;
  GitHub disponible no demuestra recepción S23 ni disponibilidad 24/7.

La validación H2 pasó **111 tests** y reprodujo los **68 hashes** del parche.
Usa fixtures Git locales y las suites offline existentes. No
instala paquetes ni ejecuta inferencia, servicios o sincronizadores. El wrapper
mantiene bloqueo durante los descendientes del comando; escritores que ignoren
el procedimiento siguen siendo un riesgo cooperativo explícito.

Al finalizar cada tarea: actualizar este estado con cambios, pruebas y próximo
paso, revisar rutas y usar `finish` primero como previsualización. Publicar solo
el conjunto autorizado. Mantener credenciales y conversaciones fuera de Git.
