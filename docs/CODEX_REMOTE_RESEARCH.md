# Codex en el S23 y acceso visual multiproyecto

**Actualización experimental EXP05, 2026-10-20:** la prueba del sandbox del Codex incluido falló antes de ejecutar un comando; kernel real sin USER_NS/PID_NS/Landlock. **App oficial/PRoot bloqueada en esta configuración**, renderer sin probar. La siguiente investigación recomendada es app-server + UI móvil + ejecutor separado con permisos controlados, sin asumir que el backend supera por ello el fallo común. No se inició app-server ni se instaló un cliente. [Informe y puertas](CODEX_SANDBOX_REPORT.md). La selección principal de la investigación R2 que sigue queda sustituida por este resultado operativo.

**R2 — 2026-10-19. Investigación, sin implementación.** Sustituye la recomendación principal de Cloud de R1, no aprobada por el usuario. [Matriz de entorno](OS_RESEARCH.md), [auditoría del código de clientes](FRONTEND_AUDIT.md), [evidencia](EVIDENCE.md).

## Qué significa cumplir

El S23 debe alojar **el harness Codex, los checkouts y la ejecución de herramientas**. El S25 debe poder seleccionar proyectos, crear y continuar hilos, revisar resultados/diff, responder aprobaciones y cancelar desde una interfaz visual, con el PC apagado. Tener una shell SSH o tmux recuperable no cumple por sí solo.

Esto no implica que el modelo OpenAI se ejecute offline en el Snapdragon. Con la configuración habitual, **la inferencia requiere conexión y envía contexto al proveedor** aunque los comandos corran en el S23. Los modelos pequeños del Device Agent son otro dominio, no sustitutos ya probados del modelo de Codex. No hace falta un servidor cloud de desarrollo para esa inferencia.

Contrato mínimo para evaluar ambas candidatas:

- Catálogo visual de al menos tres repositorios separados; indicar claramente proyecto/rama/ruta en uso.
- Crear un hilo nuevo y continuar uno anterior en cada repo, sin entrar manualmente en una CLI por directorio.
- Leer progreso y cambios, resolver una aprobación real, interrumpir y comprobar estado tras reconexión.
- Recuperar historial después de cerrar la UI y después de reiniciar el proceso del host, sin duplicar comandos de efecto incierto.
- Acceso desde otra red y pantalla S23 apagada. Medir reinicio del teléfono por separado: primer desbloqueo puede requerir presencia física.

Son criterios propuestos, no resultados. [V03](VALIDATION_PLAN.md) fija fixture, denominadores y fricción.

## A. Aplicación oficial Linux ARM64: candidata principal

### Evidencia que cambia la recomendación

OpenAI ofrece la preview Linux para **Debian 13 de escritorio**, otras distribuciones concretas y ARM64. La documentación enlaza `chatgpt_arm64.deb`, login ChatGPT y trabajo con proyectos, archivos locales y Codex. Actualmente la app se presenta bajo la marca ChatGPT; no confundirla con la web ni con una aplicación Android. [Fuente oficial Linux](https://learn.chatgpt.com/docs/linux/linux-app), [N01](EVIDENCE.md#revision-r2-fuentes-nuevas).

**Topología candidata:** Termux → PRoot-Distro → Debian 13 ARM64 → app oficial; display Termux:X11 y escritorio ligero con D-Bus de sesión; S25 ve ese escritorio por canal privado. El S23 ejecuta los comandos. No se presume soporte Linux nativo donde hay PRoot.

### Compatibilidad por comprobar

| Área | Qué sabemos | Qué falta para aceptar |
|---|---|---|
| Paquete y ABI | Hay `.deb` oficial ARM64 | Fijar versión/hash, inspeccionar control/dependencias/scripts y binarios auxiliares; resolverlos sin mezclar bibliotecas Bionic/glibc |
| Arranque gráfico | Termux:X11 documenta PRoot y tmp compartido | Abrir la app, mantener renderer seguro, D-Bus, fuentes/escala, foco, diálogo de archivos y renderizado estable |
| Privilegios | PRoot permite presentar usuario no root | No confundir usuario simulado con aislamiento kernel; no usar root real ni `--no-sandbox` como pase |
| Herramientas | Codex Linux usa shell y herramientas del host | Git, PTY, rg, ediciones, pruebas y rutas de los repos reales en Debian; no solo `--version` |
| Autenticación | Cuenta ChatGPT soportada | Browser/callback en S23 o forwarding autorizado desde S25; keyring/almacén disponible y renovación sin PC |
| Sandbox de comandos | Linux documenta bubblewrap | Prueba determinista de escritura fuera de raíz y red según política; reporte PRoot específico adverso |
| Sesiones y proyectos | App ofrece proyectos/hilos | Qué persiste en ese paquete, reapertura en frío y continuidad después de fallos; no asumir importación de Windows |
| Recursos y mantenimiento | No exige traducir ISA ARM64 | PSS, swap/OOM, I/O PRoot, temperatura, CPU del render/remoto y compatibilidad tras update |

No se descargó ni inspeccionó el `.deb`; las versiones exactas de librerías, su política de actualizaciones y su integración con keyring son **pendientes documentales/estáticas del artefacto**. El funcionamiento PRoot, kernel y One UI es **pendiente experimental**. Distinguir ambas clases evita experimentar para resolver datos que puede dar el manifiesto.

[Sandbox oficial](https://learn.chatgpt.com/docs/sandboxing) y [reporte #47402](https://github.com/openai/codex/issues/47402): hay evidencia concreta de que un userland Debian 13 funcional no garantiza aislamiento. La app podría llevar una versión distinta del harness; registrar por separado versión de app, Codex interno, helper de sandbox y cualquier CLI instalado. Que la CLI externa pase no certifica el ejecutable embebido, ni al revés. [O09, N04](EVIDENCE.md).

### Autenticación sin el PC

Primero probar el login propio de la app con cuenta de prueba autorizada, sin copiar su caché del Windows. Identificar si abre un browser Linux, Android o un callback loopback/custom URI y dónde espera la respuesta. Un callback `localhost` abierto en S25 apunta al S25 salvo forwarding; no publicarlo para corregirlo. No inventar que `codex login --device-auth` inicia también la app: ese flujo beta está documentado para la CLI, y su reutilización por el desktop debe demostrarse. [O10](EVIDENCE.md).

No desactivar keyring silenciosamente. Si la app ofrece un almacén soportado de credenciales, verificar protección y reinicio; si requiere una sesión de escritorio inexistente, es un bloqueo identificable. Los tokens permanecen en S23, sin Drive, Git ni logs. Separar la cuenta/app del bridge y los tokens de Google del servicio documental.

### Remoto gráfico y experiencia

Termux:X11 presenta el escritorio en el S23. Para el S25 hace falta **otra capa**, candidata TigerVNC x0vncserver sobre ese mismo display, solo loopback, con autenticación y túnel SSH sobre VPN privada. Un visor Android con SSH, por ejemplo bVNC, es candidato a validar. No se recomienda x11vnc como dependencia nueva: declara falta de mantenedor. [N02, N08](EVIDENCE.md#revision-r2-fuentes-nuevas).

Este acceso muestra **la app oficial que corre en el S23**; no es una nueva web móvil ni el Remote oficial de OpenAI. Conserva potencialmente el catálogo y los hilos del desktop Linux, pero en una pantalla pequeña: zoom, scroll, selección de proyecto y revisión de diff deben pasar V03. Tampoco conserva automáticamente el mismo estado de la app Windows. No ejecutar dos instancias sobre la misma base viva.

Si el display local no sobrevive al apagado físico, comparar una sesión Xvnc headless en ensayo independiente antes de rechazar toda la app Linux. No atribuir ese resultado al X11 inicial. Aceleración GPU, Turnip/virgl o ajustes gráficos no serán requisitos iniciales sin necesidad medida.

**Criterio para descartarla como principal:** necesitar desactivar una protección esencial, autenticación recurrentemente dependiente del PC, herramientas que no funcionen, UX insuficiente en S25 o fallo de V04. Una ventana de login abierta no equivale a un entorno de desarrollo viable.

## B. App-server y UI móvil: respaldo local

### Qué ofrece oficialmente el backend

[App-server](https://learn.chatgpt.com/docs/app-server) expone el protocolo del harness para integrar autenticación, hilos, turnos, eventos y aprobaciones. No es un catálogo web listo para usar. Transportes actuales: stdio JSONL; socket Unix; TCP WebSocket, señalado experimental. La documentación también califica el comando/transporte remoto como experimental y no soportado para producción: se plantea un piloto personal condicionado, no una plataforma con SLA. [O03/N03](EVIDENCE.md).

Un cliente inicia `initialize`/`initialized`, lista hilos, crea/reanuda uno por ID y envía turnos; recibe eventos y solicitudes de aprobación y puede interrumpir. `thread/resume` continúa historia persistida: **no revive un shell muerto, una tarea en RAM ni un efecto externo que quedó a medias**. El cliente debe reconciliar estado antes de reenviar instrucciones.

El app-server no autenticado es una capacidad administrativa del host. La documentación advierte que listeners WebSocket no loopback pueden aceptar conexiones sin autenticación por defecto durante el rollout. Para esta arquitectura se prefiere **stdio entre bridge y Codex**, con el bridge en loopback detrás de SSH autenticado; nada escucha públicamente. Si se prueba WS oficial, configurar autenticación soportada y TLS/canal SSH antes de hacer alcanzable el listener. Red privada por sí sola no justifica RPC sin autorización.

No reenviar RPC arbitrario desde el cliente. La API incluye operaciones de shell/proceso que pueden ejecutarse fuera del sandbox normal del hilo; una allowlist de métodos y parámetros, más política efectiva de host, debe impedir que una UI cambie el nivel de privilegio. Una política de escritura no implica que toda lectura del mismo UID esté confinada al repo.

### Comparación de los tres proyectos solicitados

| Candidato | Adecuación potencial | Bloqueos encontrados | Prioridad de investigación |
|---|---|---|---|
| friuns2/codex-mobile | Web visual, proyectos y sesiones; declara instrucciones Termux | Acceso completo/sin aprobaciones por defecto, túnel condicional, binding amplio, endpoints de archivos; `node-pty` y binario Codex pendientes | Tercera |
| scouthe/codex-mobile-remote | Mejor orientación móvil, catálogo, APK y caché; servicio Codex compartido | Túnel condicional pese al README, primer setup/skip en red privada, bypass localhost, socket Unix y política del servicio compartido | Segunda |
| chenhaoc/codex-remote-control | Puente Node más pequeño, stdio, loopback, APK con historial y cwd | Fallback `dangerFullAccess`, token amplio/query, lectura de rutas sin confinamiento, credenciales y UX por verificar | **Primer respaldo, solo tras correcciones** |

Detalles y referencias por archivo/commit: [FRONTEND_AUDIT](FRONTEND_AUDIT.md). Son clientes no oficiales sobre un backend oficial; ninguno fue validado en S23 ni ofrece garantía de paridad desktop. Los APK no alojan el harness. Instalar el cliente en S25 deja pendientes Node, Codex, login y supervisión en S23.

### Termux frente a Debian

Termux nativo reduce capas, pero Android/Bionic y las restricciones de rutas no son Linux glibc. La selección de un binario musl ARM64 en el launcher o un README con `npx` no acredita el conjunto. Investigar el conjunto fijado: versión oficial, locks/estado, proceso stdio, shell/tools y sandbox.

Debian/PRoot puede corregir ABI, layout `/tmp` o dependencias del bridge. No concede namespaces, root, KVM ni aislamiento adicional. Hay reportes independientes de locks, Unix sockets y sandbox; **un stdio que negocia JSON-RPC no prueba que las herramientas ejecuten con límites**. [N04](EVIDENCE.md#revision-r2-fuentes-nuevas).

Si ambos frontends usan el mismo backend en ensayos separados, se reutilizan checkouts aprobados y copias consistentes de datos; no sincronizar `.codex` vivo ni abrir dos escritores del mismo hilo. El primer piloto utiliza homes de prueba separados. Una migración posterior requiere formato/versiones, backup consistente y V03, sin reescribir automáticamente bases de Windows mediante importadores del frontend.

## C. Remote oficial, Cloud y Windows ARM

| Modalidad | Dónde corren comandos/archivos | Qué aporta | Por qué no sustituye la candidata local |
|---|---|---|---|
| App Linux en S23, vista por VNC privado | S23 | App oficial y catálogo local potencial | PRoot, seguridad y UX pendientes |
| app-server S23 + UI móvil | S23 | Cliente móvil y herramientas locales | Esquemas y mantenimiento de terceros; menor paridad |
| Remote oficial a Windows/Mac | Host conectado y despierto | Proyectos/chats del host, aprobaciones móviles | Si es el PC actual, deja de funcionar al apagarlo |
| Desktop conectado por SSH a S23 | S23 para el repo, desktop actúa de cliente | Integración SSH oficial | El móvil no adquiere por ello un cliente SSH directo oficial autónomo |
| CLI + tmux/SSH | S23 si arranca allí | Shell y conversación recuperable | No aporta por sí solo catálogo/UX visual multiproyecto |
| Codex Cloud | Entorno del proveedor | Tareas y repositorios sin PC | **No corre en S23 y no está aprobado como principal** |
| Windows oficial ARM64 en host soportado | Ese host | App oficial, proyectos/hilos y sandbox Windows | No demuestra un puerto S23 Ultra funcional |

[Remote connections](https://learn.chatgpt.com/docs/remote-connections) documenta hosts **macOS y Windows** despiertos y conectados, acceso móvil iOS/Android sujeto a rollout y emparejamiento desde el desktop. También describe desktop→SSH. La preview Linux no aparece por ello convertida en host Remote soportado. `remote-control` CLI sigue siendo experimental; no se presupone que un QR Termux sea aceptado por S25 o que otorgue soporte Linux/Android. La app Linux puede ser candidata aunque su acceso móvil deba usar VNC privado. [O01–O02, O13](EVIDENCE.md).

Cloud permanece una opción comparativa, no fallback automático. Sus entornos/tareas, privacidad, cuotas y persistencia difieren de un workspace local. Git no incluye secretos ni todos los hilos locales. No se paga un VPS, se conecta GitHub ni se cambia de ubicación de ejecución para resolver un fallo sin nueva decisión del usuario. [O04–O05, O11](EVIDENCE.md).

OpenAI publica [MSIX Windows ARM64](https://learn.chatgpt.com/docs/enterprise/windows-deployment). A nivel producto hay login, repositorios e hilos, herramientas PowerShell/WSL2 y sandbox; las capacidades dependen del build y modo. El manifiesto exacto del paquete y sus dependencias no se inspeccionaron. A nivel S23 faltan UEFI/controladores/recuperación de la variante, por lo que **no se puede afirmar que esa aplicación funcionaría allí**. Un Windows sin Store podría instalar MSIX por vía oficial y aun así fallar sandbox, red o comandos. [OS_RESEARCH](OS_RESEARCH.md#windows-arm-nativo-investigacion-abierta-instalacion-bloqueada).

## Decisión de evaluación y costos

**Estado tras EXP05:** la app Linux/PRoot está bloqueada en la configuración actual. Investigar app-server/stdio, UI móvil y un ejecutor de acciones separado, con pruebas que impidan eludir sus permisos. La comparación previa de clientes sigue siendo material de auditoría, no selección o autorización para instalar sus defaults. Los dos frontends comparten el posible bloqueo del harness; el respaldo no garantiza superarlo y no se habilitará ejecución irrestricta para intentarlo.

Mantener hardware y cuenta existentes reduce compras, no elimina costos: cuotas/plan Codex, red, electricidad, almacenamiento y mantenimiento del fork o escritorio. No se dispone del plan del usuario; no se dan cifras inventadas ni se autoriza API de pago. Tailscale requiere revisar condiciones del plan y cuenta; ningún túnel público automático forma parte del diseño.

No hay hoy una solución local **verificada** que permita prometer comodidad y disponibilidad prolongada. Sí hay dos hipótesis concretas y reversibles con puertas de descarte. Orden: V00 → V01 app oficial → V02 respaldo si hace falta → V03 multiproyecto S25/PC apagado → V04 disponibilidad → V11 revisión antes de datos personales. En V01 y V02 se verifica seguridad antes de aceptar una tarea real; V11 amplía la frontera completa, no difiere ese control hasta el final.
