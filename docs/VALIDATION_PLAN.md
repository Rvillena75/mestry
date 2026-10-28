# Plan de validación reproducible

**Actualización Drive posterior — 2026-10-21 UTC:** V12 **PARCIAL**: carpeta privada y cuatro fixtures `.md` subidos por el conector/WSL, permisos solo de propietario, MIME conservado y descarga exacta por SHA-256, incluidos CRLF. La prueba humana del S25 produjo una edición del cuerpo recuperada sin sobrescritura; la API de comentarios sigue vacía. El usuario no utiliza comentarios en Markdown y los retira de los requisitos actuales. Pendientes cliente concreto S25 y adaptador/OAuth/publicación del S23. **V13 opcional, fuera del piloto actual y sin aceptación técnica.** El usuario eligió app Android para el control Codex del S25; sigue en evaluación, sin instalar bridge ni abrir puertos. [Evidencia](validation/mestry-drive-review-20261021T020632Z/result.json). Los estados R2 históricos siguientes no sustituyen esta actualización.

**EXP07 — S25 → S23:** **Termux 8023, emparejamiento y conexión S25 → Horus PASS.** El S25 entra por ProxyJump como `horus`, UID 1000, home `/home/horus`, Alpine 3.24.0 ARM64; el servidor confirma su clave y el mismo puerto de conexión 50860. Horus está **running** en `127.0.0.1:8022`; Termux conserva 8023, dos claves, Boot/alias y guardia cancelada. Tras el diagnóstico inicial del stub, el instalador oficial mostró Codex 0.163.0 y `Not logged in` en la salida aportada por el S25. El usuario confirmó después el login. Tarea Codex sintética desde S25 y verificación desde otra conexión PASS: SHA-256 nuevo exacto y tres fixtures originales intactos. ADB observó Codex como hijo de la sesión SSH en el S23. Recuperación de conversación tras reconectar confirmada por el usuario; bloqueo local de 15 minutos identificado en el código y por aclaración humana; persistencia de procesos y PC apagado pendientes. La ejecución manual del hook no prueba un reinicio. [Protocolo por fases](S25_REMOTE_ACCESS.md).

**R2 — Protocolos definidos el 2026-10-19. Estado actual, 2026-10-20: V00 PARCIAL; V01 PARCIAL (Debian/X11 verificados; auditoría de ChatGPT bloqueada antes de instalar); V02–V13 NO EJECUTADOS.** La entrega de investigación original solo permitía investigación y Markdown. Ni publicar estos protocolos ni aprobar arquitectura autoriza por sí mismo instalar herramientas, descargar modelos, activar permisos, acceder a cuentas o pagar solicitudes.

**Actualización operativa posterior del 2026-10-19:** el usuario autorizó diagnósticos e instalaciones reversibles desde Ubuntu/WSL2, con avance incremental y autorización previa a operaciones sensibles. Pidió comenzar solamente por ADB/conectividad. Esa fase está completada: ADB Windows 37.0.0 detecta por USB el S23 SM-S918B autorizado, responde la shell y se confirma Termux instalado. No se configuró SSH ni se instalaron componentes. [Registro y evidencia](INSTALLATION_LOG.md). Las menciones «futuro» y «No ejecutar ahora» conservadas abajo describen el alcance de la entrega R2 original; no requieren volver a pedir autorización para operaciones reversibles ya autorizadas. Cada fase debe verificar sus dependencias antes de avanzar.

## Reglas comunes y evidencia

**Actualización del 2026-10-20:** SSH con clave exclusiva y alias `mestry-s23` verificado desde WSL (3/3 pruebas); recursos, batería y candidatos PRoot/Debian/X11 consultados. El usuario limitó esta etapa a configurar SSH y diagnosticar: **todavía no instalar Debian ni software gráfico**. [Resultados y procedimiento recomendado](INSTALLATION_LOG.md). V00 sigue parcial; V01–V13 no ejecutados.

**Actualización posterior del 20: servidor dedicado.** Se ejecutó la [auditoría de recursos y aplicaciones del S23](S23_SERVER_AUDIT.md), con tres muestras de memoria, intervalo CPU y lectura de servicios/energía/particiones. V00 avanza en inventario; no se convierte en validación de Debian, autonomía prolongada o Device Agent. El usuario añadió Termux:Boot durante la auditoría; falta preparar scripts y probar reinicio. Los protocolos **O00–O07** del informe distinguen esa línea base de los ensayos futuros y se anteponen a V01 cuando corresponda. No se deshabilitó nada ni se modificaron ajustes; toda optimización requiere la aprobación explícita exigida por el encargo vigente.

**Actualización vigente posterior — EXP02, Debian mínimo:** el usuario cerró la optimización sin más deshabilitaciones/reset y autorizó recuperación local/ADB, SSH por claves, Boot y una instancia nueva Debian 13 ARM64. **Ejecutado:** SSH Ed25519 exclusivamente por claves, hook Boot solo SSH, ajustes de batería confirmados manualmente y Debian mínimo `mestry-debian13` con APT/HTTPS/archivos/procesos, usuario invitado no root y mediciones. Comando de aceptación desde WSL correcto, reconfirmado a 04:39 UTC. **Pendiente:** reinicio/primer desbloqueo, disponibilidad prolongada, X11, app oficial y fronteras de procesos. [Informe](DEBIAN13_MINIMAL_REPORT.md), [registro reproducible](INSTALLATION_LOG.md). Las actualizaciones anteriores conservan sus estados históricos; la prohibición previa de instalar Debian quedó sustituida solo para este alcance.

**Actualización vigente posterior — EXP03, gráficos mínimos:** APK oficial normal Termux:X11 y acompañante del repositorio instalados; socket Unix local autenticado con TCP deshabilitado; Debian conectado mediante tmp compartido optativo. **Ventana y teclado PASS**: se corrigió el foco PointerRoot y el usuario confirmó letras y `MESTRY_GUI_INPUT=PASS`, marcador a **06:58:56 UTC**. Se conservaron métricas, errores y reversión. [Informe gráfico](TERMUX_X11_REPORT.md), [aceptación y límites](validation/mestry-x11-20261020T052004Z/acceptance_review.json). **No se instalaron ChatGPT/Codex, XFCE ni un gestor de ventanas, y no se reinició.** La app oficial, sus dependencias y seguridad requieren un incremento posterior; [plan para revisar](CHATGPT_LINUX_ARM64_PLAN.md). Las menciones X11 pendiente de EXP02 describen el estado anterior.

Antes de cada ensayo futuro: fijar autorización y presupuesto, activo exacto, datos permitidos, versiones/commits, condiciones iniciales, operaciones y restauración. Usar repositorios y documentos sintéticos salvo autorización de otros. Registrar fallos y ensayos interrumpidos; no convertir ausencia de métricas en cero o éxito.

Registro mínimo por ensayo: `run_id`, protocolo/revisión, hora UTC, modelo de dispositivo sin identificadores personales, firmware, componente/commit, cuenta anonimizada, configuración, hashes del fixture, perfil de permisos, condición de red/pantalla/carga, inicio/fin, métricas, evidencia y resultado. Los secretos y códigos de pairing no son evidencia publicable.

Publicar después manifest, configuración sin secretos, resultados por caso y resumen. Fijar denominadores, seeds y orden antes de ejecutar. Separar **hecho observado, explicación inferida y decisión humana**. Guardar logs sensibles localmente y extraer solo evidencia minimizada.

Los umbrales siguientes son **propuestos para aceptar un prototipo útil**, no benchmarks existentes ni límites certificados por Samsung. Pueden revisarse antes del ensayo; no cambiarse retroactivamente para aprobar un resultado. Los documentos de tecnología enlazan sus fuentes en [EVIDENCE](EVIDENCE.md).

**Actualización vigente — EXP04, app oficial:** autorizado el instalador y la instalación condicionada a una auditoría favorable, sin login. Paquete **26.1013.40934 ARM64**, SHA-256 y firmas de paquete/repositorio verificados; scripts, ELF y resolución APT revisados. **Parada antes de instalar:** kernel real con `CONFIG_USER_NS` y `CONFIG_PID_NS` deshabilitados; syscall nativa devuelve `EINVAL`, pese al retorno 0 de `unshare` en PRoot. APT propone 119 paquetes nuevos y una actualización; ninguno aplicado. No se lanzó la app ni su helper; no hay resultado de GUI, renderer, autenticación o enforcement de comandos. [Informe EXP04](CHATGPT_LINUX_ARM64_REPORT.md). Las menciones de la app sin descargar/revisar en EXP03 describen el estado anterior.

**Actualización vigente — EXP05, diagnóstico autorizado del sandbox:** Codex incluido **0.163.0-alpha.10.2**, sin aplicación instalada. Helper bubblewrap oficial preparado solo en fixture temporal, sin instalar paquetes. El comando de impresión protegido falla preparando `/dev`, **rc=1, sin ejecutar payload**; se capturó perfil read-only, red restringida y namespaces/seccomp previstos. Config real sin USER_NS/PID_NS/Landlock; observación nativa USER EINVAL/PID EPERM. Arranque glibc nativo del helper termina SIGSYS, syscall no identificada; no se cambian protecciones. **Ruta app oficial/PRoot bloqueada en la configuración actual.** Renderer, escrituras permitidas/denegadas, autenticación y app-server no probados. Se recomienda investigar UI móvil y ejecutor controlado por separado. [Informe EXP05](CODEX_SANDBOX_REPORT.md), [dictamen](validation/mestry-sandbox-20261020T080841Z/sandbox_test_summary.json).

## Orden y puertas de la revisión R2

Los IDs V01–V03 se **redefinen**: en R1 V01 evaluaba Cloud; en R2 evalúa la aplicación Linux y Cloud deja de ser una puerta de entrada. No comparar resultados futuros sin anotar revisión de protocolo. No hay resultados previos que migrar.

Orden: **V00 → V01 app oficial → V03/V04 si pasa; V02 respaldo si falla o si se justifica comparación acotada → V03/V04**. En cada rama hay revisión de renderer/suministro antes del login y enforcement de comandos antes de usar datos reales. V11 amplía controles antes de operar habitualmente con datos reales en el S23 dedicado. V12–V13 pueden prepararse con fixtures tras aprobar la dirección documental; necesitan Codex local validado para probar el flujo completo, pero no para investigar el editor de Drive. V05–V10 siguen separados.

**Abortar una rama** si solo progresa con root, `--no-sandbox`, acceso completo sin límites, exposición pública o intervención rutinaria del PC. Conservar el error original, versiones y evidencia; no cambiar la configuración insegura y llamar éxito al resultado. Si el fallo es del harness/sandbox común a GUI y app-server, no suponer que cambiar de UI lo arreglará.

## V00: Inventario sin modificar el dispositivo

**Objetivo:** identificar qué equipo/firmware se evaluará y qué mediciones son posibles. Riesgo bajo si se limita a consulta; sin permisos de depuración nuevos durante una inspección no autorizada.

1. Consultar Ajustes de S23/S25 o canal diagnóstico **ya autorizado**. Si no existe acceso, registrar pendiente; no habilitar ADB, instalar apps o reiniciar para completar el inventario.
2. Modelo exacto, CSC/región, Android/API, One UI, build y parche; RAM física documentada y memoria disponible observada, distinguiendo RAM Plus/swap; capacidad nominal y espacio libre real; batería/carga/temperatura disponibles.
3. Registrar estados de bootloader/OEM/Verified Boot solo si son legibles sin modificaciones. Un campo ausente no implica desbloqueado. No entrar en un flujo de desbloqueo ni aceptar borrados.
4. Mapear red Wi-Fi, VPN existente, acceso del S25 desde otra red y espacio para herramientas. No registrar IMEI, número telefónico ni serial de usuario.

En una conexión ADB ya aprobada, ejemplos de consultas futuras: propiedades `ro.product.model`, `ro.build.version.release`, `ro.build.version.sdk`, `ro.build.display.id`; memoria vía `dumpsys meminfo`, disco de datos y `dumpsys battery`. Las propiedades exactas de lock/CSC varían: validarlas antes de interpretar. MemTotal Linux excluye reservas; no llamarlo RAM comercial exacta.

**Aceptación:** inventario con fuente por campo y desconocidos explícitos. No requiere que el bootloader sea desbloqueable. **Salida:** capacidades y presupuesto de recursos inicial, no una modificación del teléfono.

## V01: App oficial Linux ARM64 en Debian 13/PRoot/X11

**Objetivo:** validar primero la candidata con mayor paridad desktop. Dependencias: V00, autorización específica para paquetes/rootfs de prueba y, para autenticación/inferencia, una cuenta de prueba y límite de consumo. La auditoría y apertura sin credenciales no requieren cuenta. **EXP02/EXP03 completan Debian y una ventana X11; EXP04 verifica suministro y simulación de ChatGPT, pero bloquea su instalación por prerrequisitos del kernel. App/login y enforcement siguen pendientes.** Riesgos: almacenamiento, cambios reversibles de apps, credenciales, fallos gráficos/OOM y temperatura. No modificar kernel, bootloader ni particiones.

| Etapa | Protocolo reproducible | Criterio/resultado posible |
|---|---|---|
| V01.1 Artefacto, antes de instalar | Fijar origen/versión/hash del `.deb` ARM64, Termux, PRoot-Distro, rootfs Debian 13 y X11 APK/componente. Inspeccionar control/dependencias/scripts, ejecutables y firma/repositorio de actualización; registrar cadena de suministro | Lista de dependencias y scripts completa; ninguna arquitectura distinta ni instalador ajeno sin revisar. Si falta integridad/procedencia, detener |
| V01.2 Userland aislado de pruebas | Rootfs nuevo, datos sintéticos, usuario no root aparente para la app. Registrar ABI real del binario y kernel/Android fuera de la vista sintética de PRoot; espacio/memoria antes/después | No confundir `uname` simulado, UID virtual o glibc disponible con kernel/privilegios nuevos |
| V01.3 Gráficos mínimos | X11 local con tmp compartido según documentación, DISPLAY y D-Bus de sesión. Abrir una aplicación gráfica inocua y luego el paquete oficial sin credenciales; registrar render, foco, fuentes/escala y selección de carpetas | UI estable durante 30 min. Sin `--no-sandbox`, root real o overrides de seguridad. Flags de dibujo/software solo como configuración distinta documentada |
| V01.4 Fronteras de proceso | Inspeccionar argumentos/helpers/logs oficiales disponibles de renderer y harness. Verificar enforcement real con el ejecutable que usa esta app, no solo una CLI externa. Registrar permisos efectivos | Protección del renderer conservada y sandbox de ejecución funcional. `doctor`/`unshare` favorable no basta; no obtener root para inspeccionar |
| V01.5 Autenticación | Tras verificar renderer/suministro y el helper cuando sea invocable sin cuenta, login oficial propio del host. Probar apertura del browser/callback o forwarding autorizado S25↔S23; keyring/almacén soportado. Cerrar/reabrir app y sesión gráfica | Login/renovación y reapertura sin copiar `auth.json` del PC, callback público ni logs con tokens. Si requiere PC cada vez, falla |
| V01.6 Herramientas y persistencia | Un repo fixture: lectura, cambio permitido, `git diff`, búsqueda y test corto determinista. Cerrar app, abrir mismo proyecto/hilo; después reiniciar proceso en tarea sintética y verificar estado | Los cambios están realmente en S23; historial recuperado. Proceso muerto no se reporta como tarea terminada ni se repite ciegamente |
| V01.7 Display remoto | TigerVNC x0vncserver comparte el **mismo** display, en loopback con auth; visor S25 con forwarding SSH sobre VPN privada. Desconectar visor, apagar pantalla S23, reconectar desde otra red | Mantener UI/proyectos/hilos y aislamiento. Termux:X11 local no se cuenta como prueba remota |

### V01.1b: auditoría del instalador y prerrequisitos, EXP04

1. Descargar únicamente el `.deb` publicado oficialmente; fijar versión/arquitectura/tamaño/hash y verificar firma del paquete, `InRelease` e índice. Declarar el origen de la clave y el límite del anclaje inicial HTTPS.
2. Leer scripts, conffiles, permisos, launcher, ASAR y ELF sin ejecutarlos. Separar configuración estática de renderer/credenciales de su comportamiento real.
3. Simular APT sin recomendaciones; registrar paquetes, actualizaciones, espacio y cadenas que incorporan init/udev. No aplicar una resolución inesperada ni resolverla con dependencias ficticias.
4. Leer el kernel/configuración/montajes reales fuera de PRoot. Contrastar el resultado de una syscall nativa con las namespaces y UIDs observados dentro del invitado. **El retorno 0 de `unshare`, `Seccomp: 2` heredado o root aparente no acreditan sandbox.**
5. Ante bloqueo de seguridad, detener instalación/apertura, conservar errores y pedir revisión de un experimento mínimo concreto. No invocar helpers del paquete ni introducir credenciales durante esa parada.

**Resultado EXP04:** suministro y auditoría estática completados; APT resuelve, **no aplicado**. El kernel declara **USER_NS y PID_NS deshabilitados**; creación nativa de user namespace falla con `EINVAL`. `/data` es `nosuid`; el paquete no contiene `chrome-sandbox`. **V01.3 para ChatGPT no intentado; V01.4 sin validación de renderer/harness.** Se propone por separado un diagnóstico del Codex estático incluido, con fixture sintético y sin cuenta, instalación o bypass; **pendiente de autorización, no ejecutado**. [Dictamen](validation/mestry-chatgpt-20261020T071932Z/acceptance_review.json), [recursos](validation/mestry-chatgpt-20261020T071932Z/resources_summary.json), [informe](CHATGPT_LINUX_ARM64_REPORT.md).

### V01.3a: ventana mínima local, alcance EXP03 completado

Subprueba previa a la aplicación oficial; no sustituye V01.3 completo ni V01.4. Cuenta/inferencia no necesarias.

1. Revalidar SSH/Debian y medir recursos. Fijar release, digest y firma APK **normal**, arquitectura y acompañante del repositorio; registrar cualquier diferencia de loader sin inferir automáticamente incompatibilidad.
2. Iniciar un único display Unix, cookie privada y `-nolisten tcp`. Verificar socket host/invitado con `--isolated --shared-tmp`, denegación sin cookie, cliente autorizado y ausencia de alcance TCP por loopback IPv4/IPv6 y LAN.
3. Abrir solo `xterm` como `mestry`. Verificar visualmente el contenido sintético; probar escritura/Enter mediante interacción real. Si no recibe teclado, observar foco antes de modificarlo y enfocar solo la ventana objetivo, sin desproteger Android.
4. Registrar antes/después, PSS disponible, footprint de directorios sin doble conteo, datos no legibles y estado de primer plano. Dejar procedimientos de operación, parada y reversión. No atribuir a la app toda variación de Android.

**Resultado EXP03: PASS mínimo.** APK 1.03.01-fa3a8b4-06.10.26 y paquete 1.03.01-6 funcionan juntos; ventana inspeccionada, usuario y marcador confirman entrada. Fallo inicial de foco resuelto sin cambiar teclado/seguridad. El síntoma de ausencia de socket del issue Samsung #1115 no apareció; la prueba tras reinicio no se ejecutó.

**Cobertura pendiente:** 30 minutos de estabilidad, ciclo de suspensión y nuevas notificaciones/batería del APK X11, app oficial y sus dos puertas de seguridad. Las notificaciones X11 no estaban concedidas en la lectura final; no se forzaron. [Reproducción, fallos y métricas](INSTALLATION_LOG.md).

Antes del login, probar renderer y helper interno determinista sin cuenta cuando el paquete lo permita. Si el harness solo puede ejercitarse después del login, registrar esa dependencia: únicamente una cuenta/entorno de prueba expresamente autorizados, tras verificar renderer y sin datos personales, puede habilitar esa etapa. El control de comandos sigue siendo bloqueante antes de aceptar uso real; nunca afirmar que la CLI externa certifica el helper embebido.

**Fixture de sandbox común a V01/V02:** directorio de workspace con archivo editable, sentinel sintético fuera de writable roots, repositorio vecino y destino de red de prueba autorizado. Una operación permitida debe escribir dentro; una escritura al sentinel debe ser denegada sin modificarlo; red prohibida por el perfil debe bloquearse. Leer fuera de workspace puede estar permitido por un perfil normal: no usarlo como falso negativo universal; verificar por separado exclusiones sensibles y UIDs documentales. No introducir secretos reales para comprobar bloqueo. Ejercitar la ruta real de tools, no solo mostrar flags.

El arranque que necesita full access falla la puerta de comandos. Aprobar manualmente salir del sandbox no demuestra aislamiento. Verificar que el renderer no fue desprotegido y que el harness no fue sustituido por otro binario para la medición. Si no hay visibilidad suficiente para demostrarlo, resultado **inconcluso**, no aprobado.

**Aceptación de V01:** etapas relevantes verificadas, cero fallos de frontera y una tarea fixture recuperada. Todavía no demuestra experiencia multiproyecto ni 72 h: necesita V03/V04. Si falla solo el display al apagar pantalla, se puede plantear V01.7b con Xvnc headless como configuración distinta, manteniendo las mismas puertas; no repetir con más capas sin explicar la hipótesis.

**Rollback:** cerrar procesos nuevos, retirar el rootfs/artefactos de prueba con ruta verificada y revocar solo credenciales/grants de prueba. Preservar datos Termux preexistentes; no desinstalar toda la familia de apps para resolver firmas. Registrar ajustes Android y devolver únicamente los cambiados en el alcance autorizado.

## V02: App-server local y clientes visuales

**Objetivo:** validar el respaldo, no asumir que una GUI elimina los fallos Termux. Dependencias: V00, autorización futura y fixtures. Se fijan frontend por commit y versión oficial de Codex **juntos**. No se elige una versión histórica solo porque un reporte dice que arrancaba.

1. **Suministro/seguridad antes de ejecutar el bridge:** revisar lockfile, scripts/postinstall, soporte de Node mantenido y artefacto Android. Convertir F01–F11 de [FRONTEND_AUDIT](FRONTEND_AUDIT.md) en lista de cambios/controles verificables. Para chenhaoc, bloquear fallback de acceso completo, cambios remotos de política, rutas fuera de raíces y token en URL/historial. Un prototipo corregido sería implementación futura autorizada, no parte de esta investigación.
2. **Backend sin UI:** en Termux nativo, home de prueba vacío y transporte stdio; handshake `initialize`/`initialized`, listado de capacidades/hilos y sandbox determinista sin petición al modelo cuando sea posible. Probar locks, almacenamiento de estado y subprocesses. Registrar binario/ABI y errores, incluido el startup del daemon interno aunque se use stdio.
3. Si hay incompatibilidad identificada de ABI/layout, repetir en Debian 13/PRoot con versiones comparables y registrar qué cambió. No parchear controles de seguridad ni crear un `/tmp` privilegiado. Probar socket Unix solo si se evalúa scouthe; un handshake stdio no lo acredita.
4. Tras pasar enforcement, login oficial del host; device auth beta solo si disponible para la cuenta, o callback forwarding privado. Verificar expiración/reapertura sin PC y sin copiar credenciales de otro equipo. La UI móvil no debe recibir tokens OpenAI.
5. Un bridge por vez: primero chenhaoc corregido; scouthe si el primero no cumple UX y justifica resolver socket/superficie mayor. Friuns2 solo si aporta una mejora concreta. Nunca `npx` ambiguo como prueba de haber instalado el fork auditado. Ningún túnel automático, binario descargado al vuelo ni instalador remoto sin revisión.
6. Transporte externo: loopback, autenticación de aplicación también a través de SSH y ACL privada; o terminación TLS privada si el cliente no soporta el forwarding elegido. Probar token ausente/erróneo/revocado, primer setup y skip, peer/Host localhost, HTTP y upgrade WS, origen ajeno y acceso LAN directo. Verificar listeners IPv4/IPv6 y ausencia de procesos cloudflared/FRPC y relays no autorizados.
7. Política efectiva: inicio, resume, actualización de sesión y turno no pueden elevar privilegios ni salir de raíces aprobadas por petición del cliente. Intentar traversal, ruta absoluta y symlink con fixtures; todos los endpoints de archivo deben aplicar alcance. Bloquear RPC fuera de allowlist y operaciones de proceso/shell fuera del modelo de permisos.
8. Comprobar caducidad/límites, protección de token/estado en S23 y Keystore/almacén S25; URLs/logs/portapapeles sin secretos. Cliente cerrado no debe matar por diseño al host, y el APK no se declara host por mostrar un servicio foreground.

**Aceptación:** todos los controles negativos pasan y una conversación fixture puede usar tools con límites. Un README o ARM64 reconocido por el instalador no cuentan como ejecución en Android. Si falta una corrección bloqueante, **no apto para piloto con credenciales personales**, aunque la UI abra. V03 mide el catálogo/continuidad; V04, disponibilidad.

**Rollback:** detener bridge/harness de prueba, retirar tokens y pairing/keys de prueba, listeners y ajustes nuevos; conservar estado minimizado y hashes. No publicar servicios para simplificar el acceso ni contratar otro host como continuación automática.

## V03: Contrato visual multiproyecto desde S25, con PC apagado

**Objetivo:** comparar la app oficial y cada respaldo que haya pasado su seguridad con **el mismo fixture**. No evaluar solo terminales. Dependencias: V01 o V02; cuenta/cuota autorizadas; tres repos sintéticos A/B/C, un hilo previo por repo y otro que se creará durante el ensayo (seis hilos al terminar), con permisos fijados. Preparar una tabla previa con raíz, rama, archivos/sentinel único y respuestas esperadas.

1. Apagar el PC realmente antes de la sesión evaluada. No usarlo como bastión SSH, servidor VNC, DNS privado, relay, observador ni ejecutor. Registrar hora y topología; el S25 se conecta desde otra red, el S23 queda en Wi-Fi. El setup previo o compilación de APK puede haber usado PC: documentarlo, sin confundir dependencia de preparación con dependencia operativa.
2. Desde S25 abrir la UI y **listar/seleccionar A/B/C** sin shell por directorio. Crear un hilo nuevo en cada uno; ordenar una lectura del sentinel y modificación inocua exclusiva del repo. Verificar ruta/branch y diff en el almacenamiento S23, con ID de hilo/host. El sentinel solo existente allí y los cambios locales aportan evidencia de ejecución en S23; el nombre mostrado por la UI por sí solo no basta.
3. Alternar A→B→C→A; continuar al menos un hilo previo de cada repo. Repetir seis cambios de proyecto con orden fijado. Comprobar que no cruza cwd, historial o writable roots. Probar repos con nombres parecidos para detectar ambigüedad visual.
4. En una tarea sintética provocar solicitud de aprobación, denegarla y verificar que no ejecutó; repetir con una autorización puntual permitida y comprobar que no se vuelve aprobación general. Interrumpir un turno y confirmar estado en UI/harness.
5. Cerrar visor/app del S25 y abrir de nuevo. Cortar red dos veces durante una tarea controlada; después reiniciar bridge o app/harness según la rama, en ensayo separado. El historial debe recuperarse; reconciliar efectos y no reenviar automáticamente prompts. Mostrar interrupted/unknown si el proceso murió, sin afirmar que la tarea continuó.
6. Comprobar diferencia entre estado del host y caché móvil: leer historia offline puede ser válido, enviar un nuevo turno debe indicar falta de host/red. No presentar una pantalla cacheada como prueba de servicio disponible.
7. Mantener una jornada de **24 h sin PC**, varias visitas desde S25 y pantalla S23 apagada la mayor parte; V04 amplía a 72 h. Revisar diff/documento en S25 sin depender de que el PC muestre una ventana.

**Aceptación funcional:** 3/3 repos seleccionables y 6/6 hilos identificables; crear y continuar en todos; cero escrituras cruzadas, replays o pérdida de cambios publicados como correctos; aprobación, denegación e interrupción verificables. Si chenhaoc solo ofrece cwd sin una navegación móvil utilizable, falla esta prueba aunque soporte el protocolo.

**Fricción propuesta:** tras bootstrap/login inicial, abrir el entorno ya autorizado desde otra red ≤60 s y cambiar/retomar proyecto ≤20 s en al menos 5/6 cambios, sin comandos SSH manuales. Registrar conexión, carga de UI y cómputo del modelo por separado; no contar espera del modelo como tiempo de selección. Medir lectura de diff, scroll y acceso a aprobar/cancelar en pantalla S25. El usuario valora comodidad en la aceptación final; una media rápida no compensa controles inaccesibles.

**Recuperación:** ninguna autorización de reset/reinstalación; rollback del entorno fixture. Si falla una rama, clasificar UI, host, auth, sandbox, red o lifecycle y conservar evidencia. No atribuir a One UI un fallo del frontend sin diagnóstico.

## V04: Disponibilidad del S23 y red privada

**Objetivo:** evaluar pantalla apagada y recuperación sin afirmar disponibilidad de servidor por intuición. Dependencias: V00, red/instalaciones autorizadas y equipo en condición física segura. No forzar descarga profunda ni temperatura.

1. Estado inicial documentado: primer desbloqueo realizado, Wi-Fi estable, VPN y OpenSSH autenticados; ninguna regla de router expone puertos. Usar claves y verificación de host.
2. Desde otra red, verificar alcance S25→S23 y denegación a cliente no autorizado. Confirmar puerto SSH real y que Tailscale SSH integrado no es el servidor Android. Probar alcance LAN y no solo tailnet.
3. Ensayo de **72 h** con PC apagado, pantalla S23 apagada durante la mayor parte, alimentación normal y carga ligera. Medir el canal privado cada minuto desde observador independiente del PC; usar S25 u observador de prueba autorizado, sin convertirlo en ejecutor/bastión. El método debe sobrevivir su propio reposo o declarar huecos. Separar **SSH/VPN disponible**, **VNC/bridge autenticado disponible** y **Codex realmente utilizable**: un puerto abierto no prueba los tres. Para bridge, usar listado autenticado por su protocolo; para app oficial, observar el display y realizar al menos seis reconexiones visuales distribuidas y tres tareas de lectura fixture espaciadas durante las 72 h. No inventar un endpoint privado de salud de la app ni atribuir el porcentaje SSH a la disponibilidad Codex.
4. Provocar dos pérdidas controladas de Wi-Fi y un reinicio de proceso. Ensayar reinicio del teléfono solo con autorización específica y acceso físico de recuperación. Distinguir antes/después del primer desbloqueo; no intentar eludir PIN.
5. Registrar Android/One UI, restricciones de batería aceptadas, wake locks, muertes de procesos, VPN expirada y necesidad de intervención. Cambiar una variable por vez y preservar cómo revertirla.

**Aceptación propuesta del canal tras primer desbloqueo:** ≥99% muestras válidas accesibles, ninguna caída inexplicada >5 min y recuperación de las dos pérdidas de red ≤5 min. Conservar el total bruto de muestras y muestras faltantes; no atribuir un fallo del monitor al S23 sin evidencia. Un periodo de 72 h solo acepta piloto, no acredita meses de disponibilidad. Las seis reconexiones y tres tareas deben funcionar o recuperar estado en ≤5 min, sin shell por repo ni PC; publicar cobertura/denominador de cada capa. No afirmar 99% de disponibilidad de Codex si solo se midió red.

Si requiere desbloqueo físico tras reinicio, documentar **recuperación asistida**, no disponibilidad desatendida completa. En la arquitectura local, **el desarrollo queda indisponible mientras el S23 no recupere sus servicios**; el límite afecta al objetivo central. No hay continuidad Cloud automática. Recuperación: retirar ajustes experimentales/llaves y restaurar políticas previas registradas cuando se cierre el piloto.

## V05: Sincronización e integridad Drive

**Objetivo:** validar algoritmo/cliente antes de datos personales. Crear fixture **solo en fase futura autorizada**: al menos 24 objetos con subcarpetas, PDFs, texto, Docs, Sheets de varias hojas, Slides, dos nombres iguales, un shortcut y un tipo no soportado. Guardar inventario esperado por ID y hashes de binarios conocidos.

Ensayos mínimos, con expectativas anotadas antes:

1. Bootstrap y cambios durante el inventario; paginación con tamaño pequeño para recorrer varias páginas.
2. Alta, modificación, rename con mismo ID, move entre carpetas y traslado de una carpeta con descendientes.
3. Papelera, borrado, salida/entrada de selección y revocación de acceso en un archivo compartido de prueba.
4. Mismo nombre/diferente ID y shortcut a target fuera de alcance/ciclo. No colisionar ni filtrar datos no escogidos.
5. Interrumpir durante descarga y entre archivo final/commit; repetir la misma página y reiniciar proceso. Probar disco insuficiente en almacenamiento de prueba acotado, no llenando el teléfono.
6. Inyectar respuestas 429, 403 de cuota, 403 de permisos, 401, timeout y export imposible mediante dobles controlados; no generar tráfico real para provocar rate limit.
7. Export >10 MB o respuesta simulada equivalente; Workspace sin checksum remoto; modificaciones antes/después de export. Revisión manual de contenido exportado por tipo.
8. Comparar candidato rclone/cliente y API con la misma tabla de resultados, sin escribir ambos a un destino.

**Aceptación:** 100% objetos soportados reconciliados por ID, 100% bajas/revocaciones excluidas de búsqueda activa, cero colisiones, cero contenido fuera de selección, todos los errores visibles y ninguna corrupción publicada como válida. Binarios con hash esperado coinciden. Workspace se valida por representación/contenido esperado, sin inventar hash remoto. Repetir ciclo sin cambios no descarga nuevamente binarios intactos; exports no deben repetirse sin cambio observado o causa registrada.

La prueba no exige capturar toda revisión intermedia de Drive: la réplica sigue el estado observable con versiones locales trazables. Recuperación: restaurar grants/fixtures de prueba según alcance autorizado; no borrar documentos reales.

## V06: Credenciales y segundo plano documental

**Evidencia posterior real:** cliente propio con `drive.file` autorizado privadamente y cuenta comprobada; S23 renovó el token sin WSL y publicó dos archivos privados. La clave de Horus rechazó otros comandos y reenvío SSH según salida del usuario. Se termina el paso a producción/reautorización para quitar el límite de Testing. Revocación, reposo, horizonte ≥8 días cuando corresponda y operación 24/7 siguen pendientes; **V06 completo no es PASS**. [Resultado acotado](validation/mestry-horus-drive-live-20261021T040010Z/result.json).

**Preparación actual, no aceptación V06:** runtime Python estándar en Termux separado de Horus; autorización inicial oficial en WSL y transferencia por stdin SSH, sin token persistido en WSL. Callback WSL 127.0.0.1:53682 pendiente de aprobación de puertos. La renovación nativa pasó pruebas simuladas, no Google real; faltan autorización, refresh real, revocación y autonomía. [Preparación y límites](../tools/horus_publish/README.md).

**Objetivo:** autorización renovable y jobs recuperables en Android real. Dependencias: P03, V05 y OAuth de prueba. Usar cliente soportado por plataforma; distinguir Android AuthorizationClient de refresh token de rclone.

Probar autorización inicial, token caducado, autorización previa sin UI, revocación, cuenta retirada, error recuperable que exige consentimiento y corte de red. Para app externa OAuth en Testing con scopes Drive, comprobar el límite de 7 días cuando aplique; usar reloj/token simulado para regresión y un periodo real **≥8 días** si esa modalidad es candidata de operación. No declarar “permanente” desde una hora de funcionamiento.

Ejecutar trabajos acotados con pantalla apagada, cargando y durante un periodo autorizado sin carga. Medir demora real del scheduler y reanudación. No usar un FGS dataSync infinito para evitar WorkManager; verificar restricciones API/target del artefacto exacto.

**Aceptación:** renovar sin reconsentimiento mientras grants válidos lo permitan; revocación detiene acceso y produce estado claro; no bucles de login ni secretos en logs. En condición normal cargando/red disponible, objetivo de frescura p95 ≤2 h con scheduling de 60 min, medido sobre cambios programados. Offline y antes del primer desbloqueo se reportan aparte, sin prometer SLA imposible. Las interrupciones no pierden cola/cursor.

Recuperación: revocar grant de prueba, retirar secretos del dispositivo/entorno y conservar manifest sin tokens.

## V07: Extracción, búsqueda y citas

**Objetivo:** decidir si FTS basta. Corpus español de prueba aprobado y hash de cada representación. Preparar **40 preguntas contestables y 10 sin respuesta**, con documento/localizador relevante marcado por revisión humana antes del benchmark. Dividir 20 para desarrollo y 30 para evaluación cerrada, conservando tipos de pregunta.

1. Medir cobertura de extracción por MIME, texto/hojas/diapositivas y errores. No evaluar solo documentos que el parser pudo abrir sin publicar cobertura total.
2. FTS con driver SQLite/Room fijados: verificar FTS5 real o FTS4 seleccionado, acentos, ñ, frases, identificadores, unidades y tablas.
3. Medir top-5 con FTS; después e5-small u otro embedding local si se autorizó descarga, y finalmente híbrido si se justifica. Misma partición de evaluación, sin retocar parámetros tras ver respuestas.
4. Cambiar un documento, quitar acceso y repetir: generaciones/citas antiguas no deben aparecer como actuales. Fallo de embedding no debe corromper texto ni publicar mezcla de versiones.

**Aceptación propuesta:** cobertura de tipos declarados documentada; 100% citas de muestra apuntan a fragmento/version exactos; cero fragmentos revocados activos; Recall@5 ≥0,85 sobre preguntas contestables de evaluación. Para seleccionar estrategia de abstención, revisar las preguntas sin respuesta con error explícito: no generar una respuesta por mera similitud. Objetivo latencia búsqueda caliente p95 ≤1 s para el corpus piloto, sin contar generación de respuesta.

Añadir vectorial solo si mejora Recall@5 al menos 5 puntos porcentuales o resuelve una clase importante predefinida, sin sobrepasar recursos/latencia. Las muestras pequeñas no prueban superioridad estadística; reportar intervalos y casos, no decimales de falsa precisión. Core/generación no son necesarios para validar recuperación.

## V08: Modelos, español y tool calling sin actuar

**Objetivo:** medir interpretación y costo sin ejecutar acciones UI. Dependencias: V00, artefactos/versiones autorizados; límite de almacenamiento y descarga acordado. Sin llamadas API salvo autorización y cap explícitos.

Dataset propuesto: **120 instrucciones en español**, incluyendo paráfrasis, negación, ambigüedad, fuera de catálogo y texto malicioso presentado como contenido de pantalla. 40 desarrollo, 80 evaluación cerrada. Etiquetas: intención/acción/argumentos o abstención. Al menos dos revisiones de casos ambiguos; preservar desacuerdos.

Comparar reglas/clasificador, Qwen3-1.7B no thinking y un especialista si se justifica. Qwen3.5-2B/visión se incorpora después, con dataset visual propio. No afinar FunctionGemma y evaluarlo con sus propios ejemplos de entrenamiento.

Fijar runtime/commit, checkpoint/revisión/hash, cuantización, template, parser/gramática, herramientas, idioma, contexto inicial 2.048 tokens y prueba de 4.096 solo si hay margen, límite de salida, muestreo efectivo, seed cuando exista, threads y backend. No comparar “thinking” contra “no thinking” llamándolo únicamente efecto de temperatura.

Cada configuración: tres cargas frías y tres pasadas de evaluación con orden fijo aleatorizado; contabilizar tokens y timeouts. Reportar esquema válido, función correcta, argumentos exactos, abstención y tool call no permitido **por separado**. Medir TTFT y latencia total p50/p95, PSS pico, memoria disponible mínima, errores y consumo de inferencia. Todo output pasa por validador sin tocar Android.

**Aceptación propuesta:** ≥99% sintaxis válida, ≥95% función+argumentos/abstención correctos en evaluación, cero acciones no permitidas aceptadas por el validador, latencia caliente p95 ≤5 s por propuesta en el catálogo mínimo, sin OOM. Un modelo que no supera reglas en casos importantes no se incorpora. El validador debe rechazar siempre propuestas inválidas incluso si el modelo se equivoca; cero aceptación insegura no significa cero errores del modelo.

Memoria: demostrar margen de al menos 25% de memoria física utilizable del dispositivo bajo carga piloto, o un presupuesto menor revisado antes de repetir. Distinguir memoria sistema disponible y PSS; no sumar RSS de procesos compartidos como RAM física consumida.

## V09: Demostración Configuración y recuperación UI

**Objetivo:** cumplir la instrucción completa definida en [ANDROID_AGENT](ANDROID_AGENT.md#demostración-inicial). Sin modelo al principio. Fixture: estado visible e idioma registrados, referencia `Build.VERSION` leída por API y recorrido por nodos determinado para One UI real.

1. Ejecutar diez veces desde estado inicial restaurado: abrir Configuración, localizar información de software/versión, leer y cotejar con API. Máximo 10 acciones/60 s por ensayo.
2. Cinco ensayos de error: pantalla bloqueada, permiso revocado, nodo obsoleto, transición lenta y captura protegida/no disponible. Esperar bloqueo, reobservación o fallo correcto, nunca éxito inventado.
3. Cinco cancelaciones en fases diferentes: antes de inferencia, antes de gesto, gesto emitido, verificación y espera/reintento. Registrar último action ID despachado y tiempo de cancelación efectiva.
4. Si hay LLM seleccionado después de V08, comparar el mismo protocolo sin cambiar oráculo ni presupuestos. No hacerle evaluar su propio éxito.

**Aceptación:** 10/10 lecturas normales concordantes con evidencia de UI y API; 5/5 errores identificados sin falsa finalización; ninguna acción nueva tras confirmarse cancelación, objetivo de reconocimiento ≤1 s sin contar fin de gesto ya emitido. Cambios de ajustes prohibidos: cero. Un ensayo bloqueado correcto valida el control de seguridad, pero no cuenta como éxito de navegación normal.

Recuperación: volver al estado anterior solo mediante acciones seguras autorizadas; no restablecer ajustes generales del teléfono ni revocar permisos de otras apps.

## V10: Energía, temperatura y convivencia

**Objetivo:** decidir límites de ejecución sostenida. No se califica seguridad física del hardware dañado por software; verificar condición material antes de iniciar. Detener ante avisos del fabricante, comportamiento anormal o estado térmico Android **SEVERE o superior**; conservar límites de protección existentes.

Comparar sesiones con mismas condiciones ambientales registradas, cargador, nivel aproximado de batería, red, brillo/estado de pantalla y configuración: reposo, **Codex con app/PRoot/X11**, acceso VNC activo/inactivo, **Codex con bridge/cliente**, sync, extracción/embedding, modelo, control UI y combinación permitida. Para comparar las ramas Codex usar el mismo repo, cambio/test corto y fixture, con versión de modelo/configuración y red anotadas; separar latencia del proveedor de tiempo de herramientas y renderizado. Tres repeticiones por carga representativa; duración propuesta 20 min tras estabilización. Alternar orden y esperar recuperación al baseline entre repeticiones, sin enfriamiento que cambie solo una configuración.

Medir potencia/Wh preferentemente con medidor USB externo; sirve para consumo de entrada incluyendo carga/pérdidas. Si no se dispone, usar contadores disponibles y declarar precisión/limitación; no interpretar corriente de batería cargando como potencia total del sistema. Medir batería en °C y estado térmico del sistema; no etiquetar batería como CPU.

Registrar latencia y throughput a lo largo del tiempo, PSS/available RAM, trabajos retrasados, fallos y temperatura. Publicar energía incremental respecto del baseline comparable. No fijar un número de W o tokens/s sin haber medido el equipo.

**Aceptación propuesta:** sin OOM ni estado térmico de parada; límites de interacción V03 y latencia V08/V09 mantenidos y degradación entre primeros/últimos bloques ≤20% en tarea comparable. Si hay contención, serializar o reducir modelo y repetir solo la configuración cambiada. La coexistencia no es requisito para cumplir los dominios: un planificador simple puede impedir cargas simultáneas.

## V11: Seguridad, límites y recuperación integral

**Objetivo:** verificar fronteras antes de datos personales o ampliación de permisos.

Casos: cliente no autorizado; token expirado/revocado; endpoint local accidentalmente en LAN; rutas fuera del corpus/workspace; APK/artefacto con hash inválido; intento de Termux de leer almacén privado documental; Device Agent intentando observar paquete excluido; texto Drive/pantalla que ordena cambiar permisos; repetición de action ID, aprobación vencida y cancelación persistida; backup/restauración de manifest y reconstrucción de índice.

**Aceptación:** todos los intentos fuera de política rechazados y auditados, cero secretos en logs/artefactos, recuperación de un fixture sin corrupción y sin ejecutar dos veces un efecto. Verificar separación de UIDs y, aparte, filtros Accessibility: una no sustituye a los otros. No copiar SQLite abierto mediante Drive para simular un backup.

No se hacen pruebas destructivas sobre cuentas o documentos reales. Una fuga o acción aceptada fuera de política detiene la rama y se corrige antes de seguir; nunca se compensa con una alta tasa de éxito funcional.

## V12: Publicar Markdown desde S23 y revisarlo en S25

**Aceptación del piloto acotado: PASS.** Terminal Horus S25 publicó `S23_PUBLISH_TEST.md`, repitió idéntico contenido con el mismo ID y publicó una segunda revisión con otro ID. Una conexión independiente descargó ambos archivos completos y verificó SHA-256, metadata, carpeta y privacidad; la primera sigue idéntica después de la segunda. El conector corroboró metadata y el usuario confirmó lectura de ambas desde S25, sin exigir edición/comentarios. Esto no valida todos los fixtures sintácticos de R2, el editor concreto, invocación por un modelo, corpus o frontend Android nuevo. OAuth de producción se está terminando. [Resultado y fuente de cada observación](validation/mestry-horus-drive-live-20261021T040010Z/result.json), [uso](HORUS_DRIVE_PUBLISH.md).

**Publicador preparado, no PASS autónomo:** 26 tests WSL y 25 S23 correctos, uno de instalador WSL omitido en S23; código copiado inactivo. Cuenta/carpeta y documento sintético fijos, revisión nueva, idempotencia por ID reservado, verificación de bytes y no overwrite probados con API falsa. No hay todavía token, clave Horus→Termux, carpeta del nuevo cliente ni upload del teléfono. [Guía](../tools/horus_publish/README.md), [evidencia](validation/mestry-horus-publish-20261021T033650Z/manifest.json).

**Ajuste vigente del piloto:** la prueba de comentarios se retiró por preferencia del usuario. Los pasos sobre comentarios y la dependencia V13 del protocolo R2 siguiente son opcionales para este incremento; no bloquean el flujo de lectura/edición/versiones. Se mantienen las verificaciones de publicación, identidad, permisos y no sobrescritura. La subida mediante conector sigue sin demostrar publicación autónoma S23.

**Objetivo:** validar el editor nuevo y el intercambio entre UIDs antes de crear un sincronizador. Dependencias: aprobación de dirección documental, cuenta/carpeta de prueba y OAuth limitado; V01/V02/V03 para el flujo completo Codex→S23. Sin archivos personales. [Diseño](GOOGLE_DRIVE_RAG.md).

1. Registrar cuenta anonimizada, rollout visible, apps Drive/Docs y navegador de S25. Probar enlaces con apps nativas y web móvil **por separado**; si solo sirve modo escritorio web, registrar fricción y pedir evaluación de UX, no declarar paridad móvil nativa.
2. Fixture de cuatro Markdown UTF-8 con hashes: español/ñ y encabezados; tablas/enlaces; código/Mermaid/HTML; enlaces relativos/imágenes/front matter. Incluir LF/CRLF y tamaños pequeños. Anotar qué formato debe preservarse y qué renderizado es opcional antes del ensayo.
3. Codex crea/modifica esos archivos en S23. Selección explícita de salientes; probar adaptador URI/document provider o capacidad loopback limitada. Verificar que Document Service **no** puede leer todo Termux ni Termux sus tokens; método de arranque autorizado y lifecycle Android. Elegir un solo adaptador, sin copiar datos privados al almacenamiento compartido como atajo.
4. Publicar r0001 como archivo `.md`, con idempotency key, metadatos y enlace; no conversión Docs ni permisos públicos. Comparar `fileId`, MIME, capabilities, versión y descarga bytes antes/después de abrirlo **sin editar**. Abrir la revisión desde S25 y añadir un comentario de prueba manual autorizado.
5. Editar deliberadamente una copia en Docs desde S25; descargar y comparar diff semántico/bytes, versión y tipo. No exigir hash idéntico después de una edición; exigir que las transformaciones estén visibles y se conserve la propuesta humana.
6. Codex avanza localmente y publica r0002. Verificar archivo nuevo, IDs distintos, r0001 conservado con su discusión y ninguna escritura al corpus fuente. Cortar red después de crear pero antes de confirmar y reconciliar por idempotencia/metadata; si no se conoce el resultado, pausar en uncertain antes de duplicar.
7. Scope `drive.file`: comentarios accesibles sobre el artefacto autorizado y escritura denegada a un archivo ajeno no autorizado de prueba. No ampliar scope global para pasar. Registrar grants acumulados. Revocación detiene publicación sin borrados.

**Aceptación:** artefactos trazables por ID/hash/base, sin conversión inesperada ni sobrescritura; revisión/comentario legibles en al menos un canal S25 que el usuario considere cómodo; salidas fuera de selección y acceso a credenciales rechazados. Registrar cobertura de sintaxis, no afirmar renderizado Mermaid/enlaces relativos si fallan. La revisión en Drive puede funcionar sin que Codex esté online después de publicar; no equivale a control del desarrollo.

**Rollback:** revocar grant y retirar únicamente fixture/carpeta autorizados, preservando evidencia mínima; no tocar documentos reales ni permisos generales de la cuenta. Si Markdown nativo no está visible, registrar rollout pendiente y volver a comprobar documentación/cuenta sin simular compatibilidad mediante conversión silenciosa.

## V13: Comentarios, versiones y conflictos sin pérdida

**Opcional y diferido:** fuera del piloto actual porque el usuario no utiliza comentarios en Markdown. No se registra PASS ni se solicita al usuario completar estos pasos. El procedimiento se conserva como referencia para una ampliación futura. La preservación de versiones y de ediciones humanas continúa siendo obligatoria en el flujo actual.

**Objetivo:** validar la API autorizada sobre el tipo Markdown real y el ciclo de feedback; no scraping. Dependencias: V12 y fixture con al menos 25 comentarios para forzar páginas pequeñas, respuestas, comentario resuelto, reabierto y eliminado. Creación de fixtures y edición humana solo en ensayo futuro autorizado.

1. Leer con `comments.list`, `fields` explícitos, `includeDeleted=true` y pageSize 10; registrar todas las páginas. Recuperar respuestas por ID/estado con la API documentada y comparar con inventario humano de la UI, incluidos comentarios hechos en Docs sobre el `.md`.
2. Modificar una respuesta sin tocar bytes del archivo; comprobar `Comment.modifiedTime`, detección por `startModifiedTime` y recuperación aunque no llegue un cambio de contenido. Añadir comentarios durante paginación; usar solapamiento, deduplicación y barrido completo. Simular página/token rechazado y repetir sin pérdidas.
3. Resolver, reabrir, editar y eliminar discusiones de prueba; comprobar tombstones, estado y ausencia de texto inventado del comentario eliminado. Registrar que resolver no equivale a borrar. No ejecutar respuestas/resolve automáticos del agente.
4. Verificar quotes/anclas contra base publicada con citas únicas y duplicadas, párrafos movidos y caracteres Unicode. Los ambiguos deben permanecer sin ubicación exacta, nunca apuntar por aproximación a otra versión. Si se explora Docs API, registrar compatibilidad de file ID/MIME y parámetros efectivos; no asumir que un `.md` es un Document API nativo. Si se plantea mantener un documento mutable, probar además rechazo de una escritura de fixture con `writeControl.requiredRevisionId` obsoleto, sin extrapolarlo a Drive files.update; no es requisito para las publicaciones nuevas.
5. Editar remotamente r0001 mientras Codex modifica la copia local y publica r0002. Conservar base, local y remoto; generar propuesta de merge, detectar conflicto real y no sobreescribir ninguno. Insertar cambios entre lectura de metadata y subida para demostrar que preflight **no** es CAS; la solución inicial debe seguir creando nueva revisión, sin intentar sobreescribir el archivo humano.
6. Interrumpir después de leer una página y antes del commit de watermark; reanudar idempotentemente. Enviar un comentario con texto que pide revelar tokens/cambiar permisos: debe llegar como dato y no causar ninguna acción. Probar revocación/permisos y no confundir 403 con lista vacía.
7. Reconciliación manual final: inventario por file/comment/reply ID y contenido/estado esperado frente al capturado, hashes/commits de bases y enlaces de versión. Verificar que r0001 no se borra ni sus comentarios se trasladan a r0002.

**Aceptación:** 100% comentarios/respuestas soportados del fixture capturados con versión y estado correctos, cero pérdidas/duplicados de efecto, cero sobrescrituras y ningún comentario ambiguo con localización fabricada. Solicitar feedback debe recuperar cambios en el siguiente ciclo autorizado; objetivo de refresco manual ≤60 s para este fixture pequeño, con tiempos de API separados. Polling periódico sujeto a V06; no prometer inmediatez de WorkManager.

**Descarte/fallback:** si comentarios nativos Markdown no son accesibles por APIs documentadas, el flujo `.md` no pasa. Evaluar proyección Google Doc separada solo tras aceptación del usuario; conservar identidades distintas. Un `If-Match` hipotético o un borrado de comentarios no es una corrección. Rollback limitado a fixtures/grants de prueba; conservar registro de conflictos sin datos personales.

## Registro de resultados

**EXP06 — Horus, validación funcional separada: PASS el 2026-10-20 a 20:22 UTC.** No sustituye el bloqueo de la app Linux en V01 ni acredita sandbox Linux: el usuario aceptó expresamente `--sandbox danger-full-access` para Horus. APK 1.0.4 verificado por SHA-256, firma y copia F-Droid; Alpine 3.24.0/aarch64 y Codex CLI 0.163.0 ejecutados en S23. Login manual del usuario y autorización explícita de dos tareas sintéticas. Tres archivos creados, modificados y conservados antes/después; cinco tests independientes desde Horus con salida 0, UID real Android no root y hashes concordantes. PSS y térmico posteriores medidos. [Informe](HORUS_REPORT.md), [prueba producida en el teléfono](validation/mestry-horus-20261020T194336Z/phone_validation_final_files/MESTRY_VALIDATION.txt), [aceptación estructurada](validation/mestry-horus-20261020T194336Z/summary.json).

El PC fue instalador/interfaz de entrada/observador, sin ejecutar el proyecto ni alojar el agente. Remoto Horus apagado, SSH/Termux/Debian/X11 conservados. **No ejecutado:** control S25, apagado físico del PC, reinicio, pantalla apagada prolongada o 24/7. Antes de ampliar la fase, presentar el resultado; esta entrega se detiene aquí. La rama no convierte V02–V13 en pruebas ejecutadas.

| Protocolos | Estado y momento | Evidencia experimental |
|---|---|---|
| V00–V13, entrega de investigación R2 original | **NO EJECUTADO** al cerrar aquella entrega | Ninguna en aquella entrega; solo se leyó el workspace y documentación pública |
| V00, primera comprobación autorizada del 2026-10-19 | **PARCIAL**; ADB USB validado | Sesión `mestry-adb-wsl-20261020T024456Z`: WSL2, ADB Windows, shell S23 y presencia de Termux. SSH pendiente; inventario de recursos incompleto |
| V00, SSH y diagnóstico del 2026-10-20 | **PARCIAL**; SSH por clave y recursos verificados | Sesión `mestry-ssh-preflight-20261020T031017Z`: 3/3 pruebas SSH, RAM/espacio/batería, versiones y disponibilidad. CSC, One UI, arranque y S25 pendientes |
| V01–V13, estado posterior al diagnóstico SSH | **NO EJECUTADO** | Sin instalaciones, login, inferencia ni pruebas gráficas |
| V00, auditoría S23 y actualización EXP02 del 20 | **PARCIAL** | Inventario S23, estados de arranque y batería consultados; ADB/SSH actualizados. S25 y recuperación tras reinicio pendientes |
| V01.1, alcance preparatorio EXP02 | **PARCIAL** | PRoot-Distro 5.10.0, PRoot y rootfs Debian 13 ARM64 fijado por digest instalados; inspección y paquetes registrados. Artefactos de X11/app sin instalar ni validar |
| V01.2, base Debian mínimo | **FUNCIONAMIENTO BASE VERIFICADO; V01 GLOBAL PARCIAL** | Debian 13/arm64, APT, DNS/HTTPS, archivos/procesos, UID Android no root y recursos. `--isolated` no acredita frontera de seguridad; V01.3–V01.7 pendientes |
| O04/O05, continuidad en EXP02 | **O04 PARCIAL; O05 NO EJECUTADO** | Hook SSH idempotente y relanzamiento local preparado en ≤2 s; sin supervisor permanente ni rescate ADB automático demostrado. No se reinició |
| O06, recursos con Debian mínimo | **PARCIAL** | Tres muestras de RAM antes/durante/después y PSS de PRoot inactivo, más espacio. No valida carga gráfica ni V10 |
| V02–V13, estado vigente tras EXP02 | **NO EJECUTADO** | Sin gráficos, app Codex, cuentas, inferencia, pruebas de enforcement o disponibilidad prolongada |
| V01.1/V01.2, actualización EXP03 | **PARCIAL GLOBAL; ARTEFACTOS X11 Y BIND VERIFICADOS** | APK normal oficial, digest/firma, paquete del repo, wrapper optativo compartiendo tmp. Artefacto de ChatGPT aún sin descargar ni revisar |
| V01.3a, EXP03 a 06:58:56 UTC | **PASS, VENTANA MÍNIMA** | xterm visible y teclado confirmado, foco corregido, cookie exigida y TCP rechazado. Sin ensayo de 30 minutos ni app oficial |
| O06/V10, actualización EXP03 | **MEDICIÓN PRELIMINAR; V10 NO EJECUTADO** | RAM y footprint registrados; PSS de procesos activos y visor medidos en condiciones explícitas. Sin energía/carga sostenida |
| O05/V01.4–V01.7/V02–V13, estado tras EXP03 | **NO EJECUTADO** | Sin reinicio, app/renderer/harness, login, inferencia, remoto S25 o piloto prolongado |
| V01.1/V01.1b, EXP04 | **ARTEFACTO Y AUDITORÍA COMPLETADOS; INSTALACIÓN BLOQUEADA** | ChatGPT 26.1013.40934 ARM64, firmas/hash, scripts/ELF y APT resueltos; 119 paquetes nuevos y 1 actualización propuestos, ninguno aplicado |
| V01.2/V01.4, prerrequisitos EXP04 | **BLOQUEO DE NAMESPACES; SANDBOX REAL NO VALIDADO** | Kernel USER_NS/PID_NS deshabilitados y syscall nativa EINVAL; retorno guest 0 sin namespace nuevo. No se ejecutó renderer ni helper |
| V01.3 app/V01.5–V01.7/V02–V13, tras EXP04 | **NO EJECUTADO** | Sin instalación/apertura, login, proyectos personales, comandos del helper, inferencia o reinicio. Diagnóstico mínimo propuesto requiere revisión |
| V01.4, EXP05 — motor | **PREPARACIÓN FALLIDA; RUTA BLOQUEADA ACTUALMENTE** | Mecanismo bubblewrap + segunda etapa seccomp observado; rc=1 antes de payload. USER_NS/PID_NS/Landlock ausentes; Bionic USER EINVAL/PID EPERM; no bypass |
| V01.4, EXP05 — renderer/enforcement | **NO VALIDADOS** | Renderer no ejecutado; escrituras y red de payload no probadas porque no llegó a arrancar. Sentinel íntegro no cuenta como denegación |
| V02, siguiente rama tras EXP05 | **INVESTIGACIÓN RECOMENDADA; NO EJECUTADO** | App-server/UI móvil/ejecutor separado deben impedir rutas shell/proceso/archivos no mediadas. No nuevas instalaciones, servidor, cuenta o inferencia en EXP05 |

Windows nativo, desbloqueos y flasheos **no tienen protocolo operativo autorizado**. La única puerta de reconsideración es documental: soporte exacto de placa/variante, drivers, recuperación y beneficio probado. No se ensaya irreversibilidad para resolver un vacío de documentación.
