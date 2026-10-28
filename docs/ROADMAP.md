# Roadmap condicionado por evidencia

**Prioridad vigente — app Android S25:** diagnóstico app-server/Codex 0.163.0/cuenta ChatGPT desde S25 PASS sin inferencia; APK personal preparado, compilado y firma comprobada; 57 pruebas locales correctas. El usuario aprobó los puertos del piloto. Instalación S25, bind real del túnel, tarea desde la app, aprobación/interrupción y reconexión siguen pendientes; se pidió conectar S25 por USB. Después, prueba física con PC apagado y reposo de más de 15 minutos. Primer proyecto/documento real solicitado, todavía sin ampliar el publicador. [Preparación y aceptación](../tools/s25-codex-client/README.md).

**Piloto de publicación y OAuth de producción PASS:** cuenta/scope y renovación nativa S23; cliente Horus y clave limitada; dos versiones Drive, retry sin duplicado, no sobrescritura y lectura S25 verificados. Google Auth Platform está en producción por confirmación del usuario, inicio/privacidad publicados en HTTPS, nuevo consentimiento y refresh real comprobados con copias privadas conservadas. [Uso y límites](HORUS_DRIVE_PUBLISH.md). Continuidad superior a siete días por comprobar desde el 29 de octubre; estar en producción no garantiza tokens permanentes. No repetir OAuth inicial, carpeta o claves ya instaladas. Corpus y comentarios no forman parte de esta aceptación.

**Preparación histórica — publicación desde Horus:** publicador acotado instalado inactivo en Termux separado del UID Horus; 26 tests WSL / 25 S23 correctos, uno solo WSL omitido. [Guía y código](../tools/horus_publish/README.md). El usuario crea su cliente OAuth de escritorio con `drive.file`. Orden pendiente: aprobar callback temporal WSL → autorizar privadamente y comprobar cuenta/scopes → crear carpeta propia y moverla a Review → registrar/verificar clave exclusiva Horus→Termux → subir/readback del fixture y abrirlo en S25 → probar renovación real y uso sin PC. No abrir el callback antes de la aprobación expresa de puertos ni repetir los cuatro uploads del conector. La app Android S25 continúa pendiente y no se sustituye por este publicador.

**Prioridad posterior — Drive y app Android S25, 2026-10-21 UTC:** el usuario adelanta el piloto documental y confirma preferencia por app Android. Conector Drive reautorizado, carpeta privada Review y cuatro Markdown de prueba publicados; permisos y bytes verificados. Una edición del usuario desde S25 se recuperó y preservó; comentarios retirados como requisito por preferencia del usuario; cliente concreto pendiente de identificar. El cliente Android sigue en evaluación, sin bridge instalado ni nuevos puertos. La publicación autónoma S23, PC apagado, Boot y estabilidad prolongada siguen pendientes. [Resultado del piloto](validation/mestry-drive-review-20261021T020632Z/result.json), [contexto de continuación](DRIVE_S25_HANDOFF.md).

**Prioridad vigente — EXP07, 2026-10-20:** controlar Codex desde S25 con PC apagado. **Conexión S25 → Horus por ProxyJump PASS**, con usuario/home/Alpine verificados y autenticación corroborada por servidor. Termux conserva 8023 y ambas claves; Horus está **running** solo en `127.0.0.1:8022`, con clave S25 autorizada. El perfil SSH tiene un home distinto al harness de la app; Codex 0.163.0 quedó instalado y el usuario confirmó el login. Tarea sintética desde S25 y lectura desde otra conexión PASS, con los tres fixtures originales conservados. Recuperación de conversación tras reconectar confirmada por el usuario. El bloqueo de interfaz a los 15 minutos está aclarado; después, ensayo sin PC. Boot tras reinicio sigue sin probarse. [Estado y protocolo](S25_REMOTE_ACCESS.md). No repetir Debian ni EXP06.

**Actualización EXP06 — 2026-10-20:** el usuario priorizó Horus. APK oficial, Alpine y Codex CLI autenticado funcionan en el S23; dos tareas sintéticas y cinco tests independientes pasaron. Esta rama acepta `danger-full-access` expresamente y no valida el sandbox de la app Linux anterior. [Resultado y límites](HORUS_REPORT.md). El siguiente incremento EXP07 ya prepara el acceso desde S25. Las propuestas anteriores se conservan como historia y no sustituyen esta prioridad.

**R2 — 2026-10-19. Sin implementación ni experimentos ejecutados.** [Decisiones P01–P04](DECISIONS.md#aprobaciones-pendientes), [protocolos completos](VALIDATION_PLAN.md).

**Línea base histórica del 20:** S23 dedicado a MESTRY (DEC11) y [auditoría de servidor](S23_SERVER_AUDIT.md) terminada. La limpieza se cerró por decisión DEC12. EXP02 preparó SSH/Boot y Debian; EXP03 verificó X11; EXP06 verificó Horus/Codex. No repetir esas preparaciones como siguiente objetivo. Reinicio y recuperación posterior siguen pendientes de un ensayo específico. El alcance R2 original conservado debajo es histórico.

## Fase actual: revisión crítica y cierre provisional

Esta entrega revisa documentación oficial Linux/app-server, audita las rutas críticas de los tres clientes por commit, mantiene abierta la investigación Windows exacta y rediseña Drive como revisión Markdown. Sustituye la recomendación Cloud no aprobada. Las conclusiones documentales no certifican S23/PRoot.

Hecho: existen app Linux ARM64 y backend oficial; hay reportes adversos PRoot/Termux; los bridges requieren correcciones; el anuncio de Markdown es real. Pendiente: paquete exacto, hardware del usuario, seguridad efectiva, UX S25, comentarios API y continuidad. El registro de arquitectura sigue abierto, sin decisiones aprobadas por inferencia.

## Incremento 0 futuro: validar antes de construir

1. **V00:** inventario autorizado de S23/S25 y condición física/recursos, sin bootloader ni privilegios nuevos.
2. **V01:** inspección del artefacto y prueba reversible de app Linux/PRoot/X11; detener por sandbox o login bloqueantes.
3. Si V01 pasa, **V03/V04** sobre esa configuración. Si falla, diagnosticar y **V02** con app-server/stdio y primer cliente corregido; luego el mismo V03/V04. Si hay fallo de harness común, no repetir tres frontends sin hipótesis nueva.
4. **V11** antes de datos personales; elegir una sola configuración y registrar decisión basada en resultados. No pasar a Cloud automáticamente.

Salida: una ruta **local** demostrada o un informe de bloqueo con evidencia. No se entrega como éxito una app que abre, un app-server que solo negocia protocolo ni un turno sin sandbox. La prueba debe mostrar tres repos y recuperación desde S25 con PC realmente apagado.

La arquitectura se aprueba como dirección antes de estos ensayos; el frontend operativo se confirma después. El PC puede preparar un APK o paquetes una vez, pero no será servidor, túnel ni dependencia del uso diario.

## Primer incremento: entorno remoto multiproyecto en S23

Dependencias: P01/P02 y rama ganadora de V01/V02; V03/V04/V11. Instalar/configurar solo cuando exista autorización futura de implementación.

Alcance: fuente/versiones verificadas, red privada y autenticación, checkouts seleccionados, UI elegida, historial/aprobaciones/cancelación y supervisión/backup consistentes. Conservar bootstrap, actualización y rollback documentados. No desarrollar un frontend completo, mantener tres bridges ni configurar un escritorio si ganó el cliente móvil.

Aceptación: contrato V03, piloto V04 de 72 h, política efectiva y límites del primer desbloqueo explícitos. Cero obligación de mantener PC encendido. Si solo consigue disponibilidad asistida con acceso físico frecuente, registrar incumplimiento y revisar la decisión antes de añadir servicios.

## Segundo incremento: revisión documental y sincronización

**Se adelanta el pequeño flujo de revisión al RAG y al corpus completo** porque permite revisar el propio trabajo Codex desde S25. P03 es condición previa a credenciales/documentos.

- **2A — V12/V13:** publicación de Markdown seleccionado a carpeta privada Review, IDs/hash/base por versión, enlaces desde S25 y comentarios de vuelta. Intercambio entre UIDs sin dar OAuth a Codex. Edición humana conserva propuesta separada; sin overwrite ni resolve automático.
- **2B — V05/V06:** corpus Drive→local, inventario/cambios, exports, integridad, versiones, bajas y OAuth recuperable. Comparar rclone/cliente mantenido con API antes de construir; escoger un solo motor por destino.

Estos adaptadores comparten manifest/colas y app documental, no dos infraestructuras. La prueba básica del editor/SDK se puede estudiar con fixture antes de 2A; el flujo completo requiere el host local validado. No añadir una base vectorial ni Core para publicar un archivo.

Aceptación: revisión cómoda desde S25 y recuperación de comentarios demostradas sobre el tipo real; corpus por ID y errores visibles. Una proyección Google Doc alternativa requiere aceptar el cambio de formato/identidad; no se adopta silenciosamente si Markdown/API falla.

## Tercer incremento: agente Android y modelos opcionales

P04 y V00 antes de habilitar permisos. Primero reglas, API y macro acotada de Configuración: V09. Después V08 compara interpretación española sin ejecutar acciones en cada ensayo. Candidato inicial de runtime: llama.cpp CPU; modelos pequeños solo si mejoran reglas y caben en presupuesto medido. [Investigación conservada](ANDROID_AGENT.md).

Aceptación: lectura verificada contra API y UI, errores/cancelación correctos, ninguna acción fuera de catálogo. V10 mide convivencia con el host Codex y sync; serializar trabajo pesado antes de ampliar hardware/servicios. No usar Computer Use de Linux como equivalente de control Android.

## Incrementos posteriores

1. V07: extracción, FTS y citas; embeddings solo si mejoran recuperación, preservando versión/permisos.
2. Core mínimo cuando dos capacidades verificadas necesiten coordinarse; contratos locales, sin bus externo.
3. Ampliación gradual del catálogo Android y evaluación visual si aporta valor.
4. Otras interfaces personales fuera del alcance actual; Note20 no se investiga.

Windows ARM conserva una **línea documental de reevaluación**, sin incremento de instalación: puerto exacto de variante, firmware, drivers, energía, seguridad y recuperación antes de plantear acciones. No bloquea las pruebas reversibles Android. Si cambia esa evidencia, actualizar decisión/matriz y solicitar únicamente la aprobación de alcance que realmente haga falta.
