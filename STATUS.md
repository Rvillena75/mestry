# Estado para continuar MESTRY

Actualizado: **03/11/2026**. Autoridad de código y documentación técnica: este
repositorio. Originales seleccionados: Google Drive según el ADR congelado.

[Revisión del proyecto y siguientes pasos](docs/PROJECT_REVIEW.md): prototipo
funcional de desarrollo móvil; estabilización y cierre de H3 pendientes. La
revisión documental del 03/11 cotejó la evidencia reciente y el remoto; no repitió
las pruebas físicas ni cerró H4/H5.

- **H0:** cerrada históricamente con límites documentados; no repetir auditoría.
- **H1:** laboratorio privado validado WSL/S23, SHA final común y ocho tests por
  target. Dos contextos Codex independientes, sin inferencia de agentes reales.
- **H2, cerrada en WSL:** flujo local `start/finish/receive/check`, comprobador de entorno y
  política revisada implementados. [Guía operativa](docs/WORK_SESSIONS.md) y
  [evidencia H2](docs/investigaciones/2026-10-26_codex_24x7/14_H2_FLUJO_TRABAJO.md).
- **H3, conversación nueva S25 verificada:** el 03/11 el primer turno de un
  hilo creado con piloto 9 confirmó `4865d2c`, rechazo `BUSY` con salida 3 y
  preview con índice intacto. Terminación y recarga fresca comprobadas.
  [Registro H3](docs/investigaciones/2026-10-26_codex_24x7/15_H3_NODO_S23.md).
- **Selección S25 corregida e instalada:** piloto 9 (`10009`) persiste la
  selección y evita que un índice antiguo sustituya la preferencia reciente.
  Dos cierres/reaperturas conservaron el hilo esperado y recuperaron sus recibos
  mediante contenido fresco. Misma firma, permisos, UID, datos y emparejamiento.
  El envío sin inicio observado por la mañana no se reprodujo antes del cambio;
  su causa sigue desconocida y no se atribuye a esta corrección.
- **Datos móviles:** conexión SSH nueva, túnel/autorización e historial fresco
  aceptados con `CELLULAR` predeterminada y sin agente Wi-Fi. El cambio directo
  desde Wi-Fi no recuperó contenido fresco; reconectar el perfil SSH al cambiar
  de red. Wi-Fi restaurado y recarga fresca posterior verificada.
- **Siguiente acción H3:** publicar un candidato nativo revisado, recibirlo y
  validarlo por `session.start` del bridge y ejecutar la tarea real S25 sobre
  el SHA nuevo. Se mantienen los pins vigentes en S23; Android piloto 9 y sus
  pins nuevos se preservan locales. No reaprobar la política nativa ni aplicar
  primero por CLI. Estabilidad prolongada y H4/H5 se mantienen separadas.
- **SSH S23 recuperado, estabilidad pendiente:** hubo dos ausencias del daemon
  en esta continuación; se arrancó el helper existente sin cambiar configuración.
  No se estableció su causa.
- **Interrupción S25 pendiente:** el turno de espera inició, pero al conciliarlo
  no estaba habilitado el control para detenerlo. No se realizó el gesto ni se
  acredita cancelación. El check nativo posterior confirmó limpio/libre/idle;
  la actividad antigua del cliente se concilió con una recarga fresca.
- **Herramientas S23 implementadas:** comprobador del bridge, observación por el
  ADB existente y lector del fixture Drive. **148 pruebas offline correctas**.
  [Guía y prueba remota S25](docs/S23_CHECKS.md).
- **Reposo 03/11:** PASS; ventana de 20 min, 41/41 muestras saludables y
  41/41 en reposo de pantalla. USB conectado; no acepta PC apagado ni 24/7.
- **Drive 03/11:** autenticación y lectura de 79 bytes verificadas por hash.
  Se restauraron la carpeta y última revisión autorizadas; la revisión antigua
  que heredó la restauración vuelve a su estado previo en papelera. Google
  cambió el padre de la carpeta; el publicador conserva su bloqueo por destino
  diferente de Review. No se alteró su configuración ni se restauró el ancestro.
- **Límite H3:** el checkout ya estaba en `4865d2c` al entrar al bridge; no se
  observó aplicación de un candidato nuevo por esa entrada. El primer turno
  en una conversación nueva y la selección después de reabrir ya tienen
  aceptación física con piloto 9.
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


Continuación 04/11 en curso: `dc3a872…` fue aplicado por `session.start` y
pasó 141 tests ARM64. HEAD, BUSY y preview del turno nativo pasaron, pero el
cierre dejó recuperación pendiente; no acepta H3. Se reprodujo una carrera
de snapshot anterior al lock y se preparó una entrada atómica fetch-only para
el supervisor existente, con cuatro pruebas nuevas. La recuperación se revisará
con escritor terminado, checkout limpio y política sin cambios. S25 sobre el
siguiente candidato y su estado final siguen pendientes. H4/H5 no avanzan.
