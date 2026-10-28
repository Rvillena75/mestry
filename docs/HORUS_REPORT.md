# Horus y Codex local en el S23 — EXP06

**20 de octubre de 2026, 20:22 UTC / 17:22 de Santiago. PASS: Horus ejecuta Codex CLI en el S23 y el proyecto sintético fue creado, modificado y probado en el teléfono.** El PC se usó para instalación, interacción UI y observación; no alojó Codex, sus herramientas ni las pruebas del proyecto. [Registro de comandos, resultados y errores](INSTALLATION_LOG.md), [aceptación estructurada](validation/mestry-horus-20261020T194336Z/summary.json).

**Actualización posterior EXP07:** **S25 → Horus por ProxyJump PASS**, usando Termux 8023 como salto. Horus está **running** solo en `127.0.0.1:8022`, con una clave S25 autorizada; usuario `horus`, `/home/horus` y Alpine ARM64 comprobados. El instalador del perfil SSH mostró Codex 0.163.0 y `Not logged in`; el usuario confirmó después el login. Tarea sintética S25 y lectura desde otra conexión PASS, con los tres fixtures originales conservados; recuperación de conversación tras reconexión confirmada por el usuario. El aviso de 15 minutos corresponde al bloqueo de interfaz local, sin detener SSH en el código instalado. Las menciones a remoto apagado del informe EXP06 siguiente describen el cierre de aquella fase. [Estado actual](S25_REMOTE_ACCESS.md).

| Paso | Evidencia real |
|---|---|
| Release estable | **Horus 1.0.4/code 5**, publicada 2026-10-13; no se confunde con main 1.1.0 pendiente de publicación |
| Integridad y procedencia | SHA-256 **`bf67340c4dd8321636c158902d0bf7b5a4684a23eae982d0026d45e348cb3430`**, coincide con el asset oficial y con la descarga independiente de F-Droid |
| Firma APK | Verificación `apksigner` correcta; certificado **`311e3d58a6f92b2704aff6fabb5ad2f1ceddfe8b4bda2ed4dafeb72819b7112c`**, coincide con la release oficial |
| Compatibilidad comprobada | APK ARM64, minSdk 24/targetSdk 36; S23 Android 16/API 36. Instalación **Success** y actividad abierta **ok** |
| Separación Android | UID propio **10350**, sin sharedUserId ni APK debug; Termux conserva su instalación |
| Acceso remoto | **Apagado**, `enabled=false/state=stopped/keys=0`; no pairing ni servidor Horus iniciado |
| Asistente | **Completado**, confirmado por el usuario. `configured=true`, notificaciones y excepción de batería para Horus; remoto apagado |
| Alpine | **3.24.0, aarch64**, leídos desde una terminal Horus; Python **3.14.8** |
| Codex | **0.163.0**, instalado mediante Horus y autenticado por el usuario. PID **31853**, Node padre **31846**, UID Android **10350**; ambos siguen presentes al cierre |
| Proyecto sintético | **`/workspace/projects/mestry-horus-smoke`**: `saludo.py`, `test_saludo.py`, `README.md`, creados y después modificados por dos tareas de Codex autorizadas |
| Prueba independiente | **5 tests / OK / salida 0** desde Bare terminal de Horus, hashes iguales a los archivos exportados; UID real **10350**, CapEff **0** |
| Autonomía | PRoot, Codex y sus hijos ejecutándose bajo el servicio Android de Horus; sin bridge o SSH Horus. No se apagó físicamente el PC ni se hizo un ensayo prolongado |

Se eligió el APK de la [release oficial v1.0.4](https://github.com/scarif-labs/horus/releases/tag/v1.0.4), idéntico al distribuido por [F-Droid](https://f-droid.org/packages/com.scariflabs.horus/). [Verificación guardada](validation/mestry-horus-20261020T194336Z/apk_verified.json), [manifest de ejecución](validation/mestry-horus-20261020T194336Z/manifest.json), [comandos exactos](validation/mestry-horus-20261020T194336Z/commands.md).

La fuente revisada es el commit **2f8f8a2faebd3d0fbd11dd83340bdcfbac437369** del tag, no la rama main. Su [launcher](https://github.com/scarif-labs/horus/blob/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369/android/app/src/main/java/com/scariflabs/horus/terminal/ProotSessionLauncher.kt) instala `@openai/codex` al primer uso y lo envuelve con `--sandbox danger-full-access --no-daemon`. El usuario aceptó expresamente ese modo **dentro de Horus**. No demuestra aislamiento del sandbox Linux: la frontera real es el UID de la aplicación Android; los usuarios invitados PRoot son emulados. No se ampliaron permisos hacia Termux o sus claves.

La UI inicial sin sesión usó PSS **53,15–54,26 MiB**. Tras las dos tareas, tres muestras completas de los **10 procesos observados de Horus** sumaron **628,41 / 601,29 / 599,37 MiB**: UI, servicio, PRoot, zsh, Codex, hijos Node y Code Mode host. Mediana **601,29 MiB**; RAM global disponible **2,867–2,880 GiB**. Son lecturas posteriores al trabajo, **no el pico de inferencia**. [Datos por PID](validation/mestry-horus-20261020T194336Z/final_resources.json). Las primeras sumas del arranque eran incompletas por procesos transitorios y se conservan con esa limitación.

Al cierre: estado térmico **0**, AP **24,5–25,1 °C**, batería **22,9 °C**, piel **25,9 °C**; USB conectado y batería protegida al 80 %. Datos libres **210,99 GiB**; el cambio de `df` es global y no mide por sí solo el footprint de Horus. No se midió potencia eléctrica. El proceso Codex permaneció **23 min 28 s** y la misma sesión se reanudó tras usar el explorador y la terminal de comprobación. `exit-info` no mostró crash o ANR; solo la salida inicial Samsung SPEG `EXIT_SELF/status 0`. Este alcance no valida pantalla apagada, reinicio o disponibilidad 24/7.

El usuario creó privadamente el perfil, realizó el login y confirmó **«listo, sesion iniciada en codex»**; después autorizó expresamente **«Sí, autorizo las dos tareas sintéticas»**. El enlace automático mostró `link_unavailable`; se facilitó la copia con `c` y la alternativa de [código de dispositivo](https://auth.openai.com/codex/device), según la [documentación oficial](https://learn.chatgpt.com/docs/app-server). No se afirma qué alternativa eligió: se observó después la CLI autenticada. Contraseña, URL OAuth de sesión, código y tokens no se copiaron al proyecto. Las capturas de inspección están en caché privada fuera de él; no se copiaron credenciales de WSL/Termux.

La primera tarea creó una función de saludo y dos tests; la segunda añadió `strip()`, rechazo de nombres vacíos mediante `ValueError`, tres tests y documentación. Se conservaron [archivos iniciales](validation/mestry-horus-20261020T194336Z/task01_files/saludo.py), [archivos finales](validation/mestry-horus-20261020T194336Z/task02_files/saludo.py) y [hashes antes/después](validation/mestry-horus-20261020T194336Z/project_changes.json). La biblioteca estándar de Python bastó; no se instalaron paquetes para las tareas.

La [salida independiente producida en el S23](validation/mestry-horus-20261020T194336Z/phone_validation_final_files/MESTRY_VALIDATION.txt) contiene los cinco tests, `MESTRY_PHONE_TEST_EXIT=0`, Alpine/arquitectura, UID/capacidades y hashes. Horus exportó solo el proyecto sintético mediante MediaStore; WSL copió y comprobó bytes, sin ejecutar las pruebas. `MESTRY_VALIDATION.txt` es un cuarto archivo añadido por el verificador, no por la tarea del agente.

Se resolvió una incidencia del operador: una línea larga enviada por ADB quedó truncada y dejó la shell en continuación. Los primeros intentos no generaron evidencia válida; se comprobó el directorio y se repitió con líneas cortas. Los errores y guards se conservan en el registro; no se cuentan como PASS por devolver 0 el emisor ADB. No se corrigió mediante cambios de Horus, Android o paquetes.

No se modificaron Debian, Termux, X11 ni SSH; el `sshd` conserva PID **2975**. Horus sigue con remoto **false/stopped/0 claves**. RAM Plus **8192**, protección **80 %**, Verified Boot **green**, flash **locked**, ADB inalámbrico **0**. Sin reinicio, `horus tune`, proyectos personales o nuevas fases. Queda Codex abierto en el proyecto probado. El control desde S25 y la disponibilidad prolongada se investigarán después de presentar este resultado.

Para continuar directamente en el S23: abrir **Horus → sesión activa Codex**. Si no hay sesión, **Codex → On device → mestry-horus-smoke** abre el proyecto con la instalación y autenticación ya preparadas. No hace falta WSL para ese recorrido.
