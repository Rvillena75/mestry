# Registro de decisiones y propuestas

**Ajuste de alcance posterior — Drive/S25, 2026-10-21:** el usuario indica que no utiliza comentarios en archivos Markdown y no necesita ese circuito. El piloto actual prioriza abrir, editar y conservar versiones de documentos seleccionados; los comentarios y V13 quedan opcionales y dejan de bloquear la integración autónoma del S23 y la app Android del S25. Esto no declara implementadas esas capacidades ni convierte un comentario en autorización. Las referencias históricas a revisión por comentarios siguientes se conservan como diseño anterior.

**R2 — 2026-10-19. Ninguna arquitectura ha sido aprobada.** Autoridad: especificación inicial y aclaración actual del usuario. Las observaciones de documentación/código están en [EVIDENCE](EVIDENCE.md), no son resultados de pruebas.

**Decisión aprobada del proyecto, 2026-10-20 — DEC11:** el Galaxy S23 Ultra queda **dedicado exclusivamente a MESTRY**, sin uso personal cotidiano. Se priorizan recursos, rendimiento, autonomía de servicios, estabilidad y mantenimiento reducido. Esto no autoriza desinstalar/deshabilitar aplicaciones, cambiar ajustes o restablecer: el encargo vigente limita esta fase a una auditoría de lectura y documentación. [Informe y lotes concretos pendientes de aprobación](S23_SERVER_AUDIT.md). Durante la auditoría el usuario instaló Termux:Boot; se verificó, sin configurar scripts ni reiniciar.

**Decisión posterior del 20 — DEC12:** el usuario da por suficiente la optimización inicial. **No se deshabilitarán más aplicaciones ni se hará otro restablecimiento de fábrica.** Los lotes de limpieza de la auditoría quedan como propuestas históricas sin ejecución adicional.

**Autorización experimental posterior del 20 — EXP02:** preparar recuperación ADB/local, SSH exclusivamente por claves cuando sea apropiado, arranque SSH con Boot e instalar una instancia nueva **Debian 13 ARM64 mediante PRoot-Distro**. Autoriza dependencias mínimas de diagnóstico y pruebas, conservando Android, RAM Plus y protecciones. Excluye gráficos/Codex, root y cambios de particiones; no reiniciar sin aviso. [Registro de ejecución](INSTALLATION_LOG.md). No equivale a aprobar P01–P04 ni a declarar viable la aplicación gráfica.

**Resultado de EXP02:** Debian mínimo instalado y criterio WSL verificado, reconfirmado a 04:39 UTC del 20. SSH exclusivamente por claves y Boot solo SSH preparados; recuperación ADB/local asistida documentada, sin reiniciar ni probar arranque tras primer desbloqueo. Se detiene antes de gráficos/Codex. [Informe y límites](DEBIAN13_MINIMAL_REPORT.md).

**Autorización y resultado posteriores — EXP03:** APK oficial normal Termux:X11, acompañante del repositorio y herramientas Debian mínimas autorizados y ejecutados. Ventana y teclado confirmados, con foco explícito corregido; display Unix autenticado y sin TCP. No se reinició ni se instalaron XFCE o ChatGPT/Codex. Se detiene tras la ventana mínima; [informe](TERMUX_X11_REPORT.md) y [plan de la app para revisar, sin ejecución](CHATGPT_LINUX_ARM64_PLAN.md). La prohibición gráfica de EXP02 queda sustituida solo en este alcance.

**Autorización y resultado posteriores — EXP04:** el usuario autorizó obtener/auditar la app oficial Linux ARM64 y, si la auditoría no encontraba bloqueos importantes, instalarla y abrirla sin credenciales. Se verificó **ChatGPT 26.1013.40934**, firmas/hash, scripts/ELF y resolución APT. **La condición de instalación no se cumplió:** kernel real sin USER_NS/PID_NS, syscall nativa `EINVAL` y una transacción amplia de dependencias. Se detuvo antes de instalar o ejecutar el paquete; 139 paquetes existentes sin cambios. No se modifica la arquitectura por defecto ni se inicia sesión. El [informe](CHATGPT_LINUX_ARM64_REPORT.md) propone un diagnóstico separado del helper incluido, sin bypass, **pendiente de autorización**. Boot/reinicio sigue pendiente.

**Autorización experimental posterior, 2026-10-19:** el usuario solicitó iniciar las pruebas desde Ubuntu/WSL2 y autorizó diagnósticos e instalaciones reversibles necesarias, con autorización antes de operaciones sensibles. Limitó la primera fase a ADB y conectividad. La fase inicial está validada y documentada en [INSTALLATION_LOG](INSTALLATION_LOG.md); V00 parcial, sin instalaciones ni configuración SSH. Esta autorización amplía el alcance de investigación de REQ01 y prevalece sobre las frases de esta revisión que limitaban aquella entrega a Markdown. No equivale a aprobar toda la arquitectura ni datos/gasto de P02–P04. No se necesita una nueva aprobación para repetir tareas reversibles ya autorizadas.

**Autorización y resultado posteriores — EXP05:** el usuario autorizó únicamente el diagnóstico del sandbox incluido, con archivos sintéticos y sin instalar la app o dependencias, credenciales, modelos, datos personales o cambios de protecciones. El Codex fijado **0.163.0-alpha.10.2** intenta bubblewrap + seccomp; el comando protegido falla antes del payload. La ausencia real de USER_NS/PID_NS/Landlock y los rechazos nativos confirman el bloqueo de esa ruta en este kernel. Se retiró el fixture, incluido el helper temporal no instalado; 139 paquetes sin cambios. Conforme a la instrucción del usuario, se clasifica **app oficial/PRoot BLOQUEADA en la configuración actual** y se recomienda **investigar app-server + UI móvil + ejecutor de acciones con permisos controlados**. La investigación posterior y nuevas instalaciones **no están ejecutadas**; no se selecciona un frontend con defaults inseguros ni un host externo. [Informe y límites](CODEX_SANDBOX_REPORT.md).

**Autorización posterior — EXP06, Horus, 2026-10-20:** el usuario cambia el objetivo inmediato a **Horus oficial (`scarif-labs/horus`) con Codex CLI ejecutándose en el S23**, sin PC como ejecutor. Autoriza verificar e instalar su APK por ADB, inicializar Alpine y usar su instalador integrado de Codex. **Acepta expresamente `--sandbox danger-full-access` dentro de Horus**; esta excepción es específica de esta rama y no valida el sandbox Linux ni autoriza desactivar protecciones Android. Mantener acceso remoto Horus desactivado; sin `horus tune`, cambios globales, reinicio ni modificaciones/reinstalación de Debian, Termux, X11 o SSH. Detenerse para el login del usuario y realizar las primeras tareas únicamente sobre un proyecto sintético con su autorización. Medir memoria, temperatura y estabilidad inicial; presentar resultados antes de otras instalaciones/fases. No se cambia a otro frontend o a un host externo automáticamente. [Registro](INSTALLATION_LOG.md).

**Resultado EXP06 — PASS, 20:22 UTC:** Horus 1.0.4 firmado por F-Droid, Alpine 3.24.0 ARM64 y Codex CLI 0.163.0 autenticado. El usuario autorizó expresamente dos tareas sintéticas: tres archivos creados y modificados, hashes conservados y cinco tests verificados de nuevo **en el S23**, salida 0. Mismo proceso/sesión Codex recuperado tras navegar por Horus; remoto desactivado. El PC no alojó herramientas del proyecto; apagado físico, S25 y continuidad prolongada siguen sin probar. No se amplía automáticamente la autorización a esa fase ni se declara validado el sandbox Linux. [Informe final](HORUS_REPORT.md).

**Autorización y resultado posteriores — EXP07, 2026-10-20:** el usuario autorizó expresamente **Termux SSH 8022 → 8023**, con respaldo, recuperación ADB, prueba paralela S25/WSL y reversión de cinco minutos. Tras la confirmación de la prueba paralela, se transfirió 8023 al daemon principal y se actualizaron helper, Termux:Boot y alias WSL. El S25 verificó una conexión nueva al daemon principal a las 23:01:37 UTC; guardia cancelada y temporizador terminado. ADB confirma 8022 libre y un único daemon. Dos claves autorizadas intactas; Horus remoto permanece apagado. Esta autorización sustituye la prohibición previa de modificar el puerto solo para esta migración; no activa Horus, no ensaya reinicio ni acredita control de Codex o PC apagado. [Estado, evidencia y recuperación](S25_REMOTE_ACCESS.md).

**Autorización posterior — EXP07, Horus remoto:** después de completar la migración el usuario indicó «dale con eso, deje horus prendido». Esto autoriza continuar el emparejamiento S25 y el acceso remoto oficial de Horus; sustituye la instrucción anterior de mantenerlo apagado para esta fase. El usuario ejecutó el helper preparado e introdujo la contraseña local en su terminal WSL, sin enviarla al chat. El provider confirmó la clave pública S25 y activó el remoto; ADB comprobó `running`, una clave autorizada y `127.0.0.1:8022`. Termux conserva 8023 y ambas claves. Conexión S25 por ProxyJump verificada después: usuario `horus`, Alpine ARM64 y autenticación corroborada por servidor. El perfil SSH inicialmente solo tenía el stub; el usuario completó después su instalador oficial, obtuvo Codex 0.163.0 y `Not logged in`. Autenticación privada por código de dispositivo pendiente. Sin reinicio, `horus tune`, transferencia de claves privadas ni acceso a proyectos personales. [Procedimiento y límites](../tools/HORUS_S25_PAIRING.md).

## Estados

| Estado | Significado |
|---|---|
| Requisito confirmado por el usuario | Restricción explícita del encargo |
| Decisión aprobada | Elección aceptada explícitamente por el usuario; DEC11 se incorpora después de la entrega R2 y no aprueba el resto de la arquitectura |
| Recomendación técnica | Propuesta del investigador, revocable por evidencia/pruebas |
| Hipótesis | Afirmación de integración que todavía no está demostrada |
| Pendiente de prueba | Experimento futuro con criterio de aceptación, no un fallo ni un éxito observado |
| Alternativa no seleccionada/descartada para el piloto | Motivo concreto y puerta de reconsideración; no imposibilidad universal |
| Recomendación sustituida | R1 ya no expresa la dirección propuesta; nunca se convierte retrospectivamente en aprobación |

## Requisitos confirmados

| ID | Requisito | Consecuencia |
|---|---|---|
| REQ01 | Investigación y Markdown exclusivamente | Sin instalaciones, experimentos, cuenta Drive, dispositivos ni funcionalidades nuevas |
| REQ02 | Codex debe ejecutarse realmente en S23, sin PC operativo | Harness, checkouts y comandos locales; Cloud no satisface la prioridad actual |
| REQ03 | UX visual multiproyecto desde S25 | Catálogo, crear/continuar hilos, revisión, aprobaciones/cancelación y recuperación; una CLI única no equivale |
| REQ04 | App oficial Linux ARM64 y app-server deben investigarse primero | Candidatas reversibles antes de Windows/flash; Debian nativo no prueba PRoot |
| REQ05 | Cloud principal no está aprobado | No contratar, adoptar ni activar automáticamente Cloud/host externo si falla una ruta local |
| REQ06 | Windows ARM sigue abierto a investigación específica | Requiere evidencia dm3q/SM-S918/variante y drivers, sin extrapolar otros Snapdragon |
| REQ07 | Drive como fuente del corpus seleccionado | Mantener Drive→local de solo lectura para corpus/RAG |
| REQ08 | Codex escribe Markdown en S23 y el usuario revisa/comenta en Drive desde S25 | Nuevo canal de publicaciones y feedback; no autoriza convertir todo el corpus a bidireccional |
| REQ09 | Acceso cifrado, autenticado y privado | Sin túneles públicos automáticos ni SSH/ADB públicos; mínimos privilegios |
| REQ10 | Modelo propone y otro componente valida/ejecuta | Reglas/API antes que LLM/Accessibility; cancelación, auditoría y límites |
| REQ11 | No inferir hardware/firmware sin comprobación | Android/modelo/recursos, CSC y estados de arranque ya consultados; capacidad comercial de RAM, inventario S25 y ensayos tras reinicio siguen pendientes. Note20 fuera de alcance |
| REQ12 | S23 dedicado exclusivamente a MESTRY | Las funciones personales no son requisito; limpieza/ajustes requieren aprobación sobre la auditoría concreta, preservando Android, conectividad, autenticación, actualización y futuro agente |

## Recomendaciones técnicas

| ID | Propuesta R2 | Evidencia y condición |
|---|---|---|
| DEC01 | Mantener Android OEM y bootloader intacto | Drivers/riesgo: [OS](OS_RESEARCH.md); inventario V00 pendiente |
| DEC02 | **Principal condicionada:** app Linux ARM64 en Debian 13/PRoot y Termux:X11 | Paquete oficial y documentación X11; no soporte PRoot acreditado. V01, V03, V04 y V11 |
| DEC03 | **Respaldo local:** Codex app-server/stdio con cliente móvil, chenhaoc corregido primero | Menos capas gráficas; F07–F09 bloqueantes. V02–V04; comparte posible fallo del sandbox |
| DEC04 | Un único frontend operativo y estado/historial oficial como autoridad | Evitar bases vivas replicadas o escritores simultáneos; pruebas con homes independientes |
| DEC05 | Canal privado Tailscale + OpenSSH; VNC/bridge loopback autenticados | No asumir Serve/SSH server de Tailscale Android; binding y bypass localhost por verificar |
| DEC06 | Document Service Android propio, API v3, WorkManager y SQLite; contrastar rclone antes de construir | Corpus por ID y tareas recuperables; frontend de desarrollo no recibe OAuth. V05/V06/V12 |
| DEC07 | Markdown revisable por **publicaciones nuevas** con base/hash/ID y feedback separado | Anuncio verificado; cuenta/S25/API de comentarios sobre `.md` pendientes V12/V13 |
| DEC08 | Comentarios como datos, sin autoaprobación, auto-resolve ni merge silencioso | APIs oficiales; anclas pueden ser opacas; conservar conflictos y revisión de origen |
| DEC09 | FTS antes de embeddings; índice reconstruible y generaciones coherentes | V07; no base vectorial servidor inicial |
| DEC10 | Device Agent Android separado, determinista primero y modelo pequeño opcional | Se conserva [ANDROID_AGENT](ANDROID_AGENT.md), sin ampliar permisos ni acoplarlo a Codex |

## Qué cambia frente a R1

| Propuesta anterior | Estado R2 | Razón |
|---|---|---|
| DEC02 R1: Cloud principal | **Sustituida y no aprobada** | No ejecuta Codex en S23 |
| DEC03 R1: Termux solo laboratorio/mantenimiento | Sustituida | S23 pasa a ser host objetivo; viabilidad sigue pendiente, no se declara hecho |
| DEC04 R1: Linux externo de respaldo | No seleccionado para este piloto | Incumple ejecución en S23; necesitaría nueva decisión del usuario |
| Drive solamente entrante para todo | Ampliada por requisito REQ08 | Corpus entrante se conserva; revisión saliente es otro conjunto y otra autoridad |
| Windows cerrado para la arquitectura | Investigación abierta, sin instalación propuesta | No aparece evidencia suficiente de puerto específico que permita una prueba prudente |
| Totales R1 que favorecían Cloud | Sustituidos | Nueva puerta obligatoria de ejecución local; no hay total preciso mientras falten pruebas |

## Hipótesis y pendientes de prueba

| ID | Incertidumbre | Prueba / efecto si falla |
|---|---|---|
| HYP01 | App Linux arranca en PRoot con renderer y comandos protegidos | V01; si falla protección, descartar candidata sin `--no-sandbox` ni root |
| HYP02 | App-server funciona en Termux nativo o Debian y el bridge mantiene la política | V02; stdio no cura sandbox; detener si el fallo es común |
| HYP03 | Tres repos/hilos se manejan cómodamente desde S25 | V03; no compensar con una shell o catálogo cacheado |
| HYP04 | Host y display soportan pantalla apagada y 72 h con recuperación | V04; si necesita PC o presencia habitual, no cumple la meta de disponibilidad |
| HYP05 | Nuevo editor Markdown está visible y resulta cómodo en S25 | V12; diferenciar apps, browser y rollout |
| HYP06 | APIs documentadas devuelven comentarios/replies de ese `.md` nativo | V13; si falla, propuesta Google Doc separada requeriría aceptación del cambio |
| HYP07 | Intercambio entre UIDs y OAuth renuevan sin filtrar credenciales | V06/V11/V12; no mover OAuth a Termux para evitar diseñar el contrato |
| HYP08 | Manifest/colas/versiones preservan contenido y feedback ante conflictos | V05/V12/V13; nunca solucionar mediante overwrite o borrados |
| HYP09 | FTS y reglas bastan para los primeros casos | V07/V09; modelos/embeddings solo si aportan mejora medible en V08 |

Estos son problemas técnicos, **no preguntas al usuario sobre detalles que debe resolver la investigación**. No requieren que el usuario adivine compatibilidad, RAM, API o funcionamiento del sandbox.

## Alternativas no seleccionadas y reconsideración

| Alternativa | Motivo actual | Qué permitiría reconsiderarla |
|---|---|---|
| Cloud / Linux o Windows externo como principal o respaldo automático | No cumple REQ02 y no está aprobado | Cambio explícito de la prioridad local y presupuesto/privacidad |
| Windows nativo S23 | No se encontró puerto/driver/recuperación de variante exacta | Evidencia pública mantenida y matriz completa; luego decisión separada, sin flashear para investigar |
| Windows QEMU/TCG | Más guest y capas sin ventaja frente a app Linux disponible | Beneficio demostrado y recursos; no basta arrancar Windows |
| Winlator/KVM stock | App completa o aceleración no acreditadas | Soporte exacto de dependencias/sandbox/host y experiencia útil |
| Bridges auditados sin correcciones | Privilegios, túneles, archivos/auth según F01–F11 | Correcciones verificadas y V02/V11, con versiones fijadas |
| Construir una UI Codex nueva completa | Duplicaría proyectos ya disponibles y aumentaría mantenimiento | Ninguna existente satisface un caso mínimo y esfuerzo aprobado |
| Bidir sync del mismo Markdown mutable | Conflictos y anclas; CAS no demostrado | Protocolo de colaboración validado y necesidad real |
| Modelo grande/residente y base vectorial servidor | Complejidad/consumo no justificados | Benchmarks que demuestren insuficiencia de reglas/FTS/modelos pequeños |

## Aprobaciones pendientes

Solo decisiones de alcance/política que requieren al usuario; no instalación inmediata:

| ID | Decisión para aprobar posteriormente | Propuesta concreta |
|---|---|---|
| **P01** | Dirección arquitectónica y tolerancia a la fase de validación | S23 Android intacto; app Linux oficial como principal condicionada; app-server/stdio con cliente corregido como respaldo local. Aceptar que todavía no existe una ruta verificada y que un fallo común puede bloquear la meta |
| **P02** | Datos y gasto permitidos en las pruebas/uso Codex | Empezar con fixtures, cuenta propia y cap explícito; después repos/feedback seleccionados autorizados para inferencia. Sin API adicional, suscripción o host nuevo por defecto |
| **P03** | Autoridad documental, publicación y acceso OAuth | Corpus de solo lectura separado de Review; archivos `.md` privados por versión, comentarios de vuelta y merge revisado; `drive.file` para revisión. Alcance readonly del corpus, selección y retención a aceptar antes de autorizar acceso |
| **P04** | Alcance posterior del agente y datos sensibles | Solo catálogo determinista inicial, permisos mínimos, exclusión de apps sensibles; modelos/capturas/proveedores externos y ampliaciones requieren aprobación de ese alcance |

No se solicita autorización para flashear o desactivar protecciones. Aprobar P01–P04 fija una dirección; **esta ejecución sigue limitada a investigación y Markdown**. Una futura autorización de V01/V02/V12 tendrá artefactos, fixtures, datos, presupuesto y rollback concretos. No se interpreta tiempo transcurrido ni silencio como aprobación.

## Incremento autorizado posterior: publicador de Horus, 2026-10-21 UTC

El usuario pidió continuar con publicación autónoma desde Horus y confirmó que el cliente OAuth todavía debe prepararse. Se avanza en el piloto privado con documentos sintéticos; no es una autorización para corpus completo, otros proveedores o cambios de puertos. Comentarios siguen fuera del alcance por su preferencia.

El runtime actual permite un adaptador pequeño sin otra app: Codex se ejecuta en Horus UID Android 10350 y el controlador documental se prepara en Termux UID 10348. OAuth privado en el controlador cumple la separación de identidades que R2 exigía, aunque cambia su ubicación propuesta cuando Codex viviría en Termux. No usar PRoot como aislamiento ni ejecutar Codex en el UID documental. Se conserva el principio del [diseño documental](../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md), sin presentarlo como aceptación de todas sus propuestas.

La primera capacidad se limita a `S23_PUBLISH_TEST.md`, hasta 64 KiB, cuenta propia y carpeta fija. Se prepara una clave nueva, restringida a loopback y comando forzado por el SSH **8023 existente**, conservando las dos claves previas. El contenido con hash nuevo crea un archivo nuevo; el mismo contenido reintenta con el ID reservado antes del upload. No actualizar, borrar, compartir ni recuperar comentarios. Un error o bytes remotos alterados detiene la verificación; no sobrescribir para aparentar éxito.

El cliente OAuth nuevo usa solo `drive.file`. Creará una carpeta propia que se moverá una vez bajo Review, en lugar de ampliar a acceso global para localizar la carpeta del otro cliente. La biblioteca oficial de autorización se instala en WSL para el bootstrap interactivo; el token se enviará por stdin SSH a Termux sin persistirlo en WSL. Publicación y refresh serán nativos S23, cuya ejecución real sigue pendiente. El callback WSL temporal **127.0.0.1:53682** no se ha abierto y requerirá aprobación expresa según la regla de puertos del usuario.

Código copiado inactivo, tests offline correctos y dependencias WSL preparadas no equivalen a publicación autónoma validada. OAuth, carpeta/movimiento, clave restringida y subida/readback reales, renovación y PC apagado siguen pendientes. [Guía, código y límites](../tools/horus_publish/README.md), [evidencia de preparación](validation/mestry-horus-publish-20261021T033650Z/manifest.json). La aplicación Android del S25 y el servicio documental completo permanecen en sus incrementos propios.
