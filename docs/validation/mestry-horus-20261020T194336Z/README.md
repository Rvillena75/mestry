# Horus en el Galaxy S23 Ultra — EXP06

**PASS, 2026-10-20 a 20:22 UTC / 17:22 de Santiago.** Horus 1.0.4, Alpine 3.24.0/aarch64 y Codex CLI 0.163.0 autenticado. Dos tareas autorizadas crearon/modificaron un proyecto sintético; cinco tests independientes pasaron en el teléfono, salida 0. [Informe](../../HORUS_REPORT.md), [registro](../../INSTALLATION_LOG.md), [resumen estructurado](summary.json).

| Archivos | Uso |
|---|---|
| [manifest.json](manifest.json), [commands.md](commands.md) | Tiempos, comandos exactos, stdout/stderr, códigos y hashes; errores conservados |
| [apk_verified.json](apk_verified.json), [source_review.json](source_review.json) | APK oficial, firma y copia F-Droid idéntica; fuente fijada al tag y revisión acotada |
| [Primera versión](task01_files_verified.json), [segunda versión](task02_files_verified.json), [cambios](project_changes.json) | Copias reales de los tres archivos mediante Horus/MediaStore; bytes en `task01_files`/`task02_files` y diffs al lado |
| [MESTRY_VALIDATION.txt](phone_validation_final_files/MESTRY_VALIDATION.txt) | Python ejecutado en Bare terminal de Horus: cinco tests, exit 0, Alpine/arquitectura, UID/capacidades y hashes iguales a la segunda copia |
| [Flags](codex_effective_flags.json), [recursos finales](final_resources.json) | PSS por PID, memoria, sensores y proceso/sesión preservados. Sin argumentos completos o credenciales |
| [Postflight Android](h40_android_postflight.stdout.txt) | Remoto apagado, apps previas conservadas y ajustes protegidos consultados sin cambiar políticas |
| [review.json](review.json), [SHA256SUMS](SHA256SUMS) | Revisión local de hashes/documentación y protección del original; huellas finales del anexo |

WSL verificó/instaló el APK, envió interacción UI y recogió datos. Codex y los tests corrieron en el S23 bajo el servicio Android, sin SSH Horus, proxy o ejecutor PC. WSL no ejecutó el proyecto. No se apagó físicamente el computador; S25 y continuidad prolongada siguen pendientes.

El usuario autorizó `danger-full-access` en Horus y las dos tareas sintéticas tras el login manual. Android mantiene su sandbox por UID; los usuarios PRoot son emulados. Las capturas privadas, APK y fuente están fuera del proyecto, en caché del operador. La evidencia no contiene contraseña, código de dispositivo, tokens o URL OAuth de sesión.

Los códigos no cero h05/h10 son guards UI sin input; h33 detuvo una exportación porque faltaba la evidencia. h31/h32 enviaron líneas largas truncadas y h35 heredó una continuación: **rc 0 del emisor no equivale a ejecución válida en el invitado**. h36 confirmó el directorio, h37 ejecutó líneas cortas y h38 exportó la salida válida. No se ocultaron estos intentos ni se atribuyeron a un fallo de los tests del proyecto. También se evitó el formato literal `%s` por la semántica de `input text`.

El cuarto archivo final, `MESTRY_VALIDATION.txt`, fue añadido por el verificador. Las tareas Codex crearon/modificaron los tres acordados. Se conservan proyecto, copias sintéticas y sesión Codex. No se modificaron Debian, Termux/X11, SSH, RAM Plus, particiones o bootloader; sin reinicio, `horus tune`, cambios globales, proyectos personales o fase remota posterior.
