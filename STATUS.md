# Estado para continuar MESTRY

Actualizado: **02/11/2026**. Autoridad de código y documentación técnica: este
repositorio. Originales seleccionados: Google Drive según el ADR congelado.

- **H0:** cerrada históricamente con límites documentados; no repetir auditoría.
- **H1:** laboratorio privado validado WSL/S23, SHA final común y ocho tests por
  target. Dos contextos Codex independientes, sin inferencia de agentes reales.
- **H2, cerrada en WSL:** flujo local `start/finish/receive/check`, comprobador de entorno y
  política revisada implementados. [Guía operativa](docs/WORK_SESSIONS.md) y
  [evidencia H2](docs/investigaciones/2026-10-26_codex_24x7/14_H2_FLUJO_TRABAJO.md).
- **H3, activada en S23; S25 en validación:** clon ARM64 con 137 tests,
  bridge integrado y polling existente observados. Push real S23 `f0df88d`
  recibido/validado en WSL. Falta completar la entrada del cliente S25 por su
  túnel guardado. [Registro H3](docs/investigaciones/2026-10-26_codex_24x7/15_H3_NODO_S23.md).
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
