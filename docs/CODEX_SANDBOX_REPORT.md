# Sandbox del Codex incluido — EXP05

**2026-10-20. Resultado: RUTA BLOQUEADA EN LA CONFIGURACIÓN ACTUAL.** El Codex del paquete oficial intenta usar **bubblewrap para el sistema de archivos/namespaces y una segunda etapa para seccomp**. La preparación falla antes de ejecutar un comando inocuo. El kernel Android real carece de **USER_NS, PID_NS y Landlock**; PRoot no aporta esas funciones.

**Se recomienda detener los intentos de la app oficial en PRoot en este S23 y pasar a investigar app-server + interfaz móvil + un ejecutor de acciones con permisos controlados.** Ese cambio no se declara viable todavía: deberá impedir que las herramientas o RPC eludan al ejecutor. No se inició app-server, se instaló software ni se introdujeron credenciales.

## Alcance y versiones

El usuario autorizó solo esta prueba, con datos sintéticos, sin la aplicación completa, cuentas, modelos, repositorios/documentos personales, privilegios Android o cambios de seguridad/kernel. La [auditoría EXP04](CHATGPT_LINUX_ARM64_REPORT.md) conserva la procedencia y firmas del instalador.

| Componente | Identidad verificada |
|---|---|
| Paquete oficial de origen | ChatGPT **26.1013.40934 ARM64**, no instalado |
| SHA-256 del `.deb` | `9ab2cbbaf33cebeaa1e06eb5cab78128936f927a0d97bf00e40694e5f31c629b` |
| Miembro probado | `usr/lib/chatgpt/resources/codex`, AArch64, sin intérprete ELF declarado |
| Versión que informa el binario | **`codex-cli 0.163.0-alpha.10.2`** |
| SHA-256 de Codex | `5412ef3ceacc22a058cf19382dbfd85305e405f7275ac36300375998b2ad3fc3` |
| Helper temporal | **bubblewrap 0.12.0-1~deb13u1**, ARM64, sin setuid/setgid |
| Kernel real | **5.15.DRIVE_ID_04_EXAMPLE** |
| Credenciales reales | UID **10348**, `CapEff=0`; UID invitado `mestry` **10349** aparente |

El binario original y su paquete se volvieron a comprobar contra los hashes de EXP04. El paquete no ofrece un `bwrap` independiente en su listado y Codex no encontró el recurso adyacente esperado `codex-resources/bwrap`. Por eso la primera consulta del sandbox terminó con un panic **antes** de probar el kernel.

Para probar el mecanismo documentado se preparó **solo una copia temporal** del ejecutable de bubblewrap del [repositorio oficial Debian](https://deb.debian.org/debian/pool/main/b/bubblewrap/bubblewrap_0.12.0-1~deb13u1_arm64.deb), **sin instalar su paquete ni dependencias**. Sus bibliotecas ya estaban presentes. El `.deb` mide **54.820 bytes**, SHA-256 **`d1ac1d0d81c815fc15842b9f04fdf414830ed14a0a602bf6344740f90bb36c00`**; el ejecutable, **`b3b829e18a7d43ee589dc37e351cb9480ff7301b493d8227b8c754294638b976`**. El hash coincide con los metadatos APT existentes de las fuentes firmadas; **EXP05 no revalidó por separado un InRelease nuevo**. [Procedencia Codex](validation/mestry-sandbox-20261020T080841Z/binary_provenance.json), [procedencia del helper](validation/mestry-sandbox-20261020T080841Z/bubblewrap_provenance.json).

## Preparación y límites de la prueba

Todo el estado preparado quedó bajo **`$PREFIX/tmp/mestry-sandbox-20261020T080841Z`**: binarios de prueba, home nuevo, configuración restrictiva, tmp, logs, workspace y sentinel. Los archivos de datos contenían únicamente las cadenas sintéticas fijadas para EXP05. Home, `/tmp` y `/var/tmp` del invitado se enlazaron a esos directorios; no se compartió el home real de Termux ni su tmp/X11.

Las invocaciones de Codex usaron `env -i`, PATH de prueba y una lista explícita de variables de entorno. El valor HOME seguía siendo `/home/mestry`, sobre el directorio sintético. No había `auth.json`, proyectos ni claves SSH en ese home. La configuración fue **`sandbox_mode="read-only"` y `approval_policy="never"`**, sin ampliaciones de permisos. El comando ensamblado por PRoot-Distro muestra su default `MOZ_FAKE_NO_SANDBOX=1`; **Codex no lo heredó**, porque su entorno se reconstruyó con `env -i`.

Un wrapper pequeño registró los argumentos de `bwrap` y realizó obligatoriamente `exec` del helper oficial con esos mismos argumentos. No permitió ejecutar el comando por otra ruta ni reemplazó el sandbox. [Script del wrapper](validation/mestry-sandbox-20261020T080841Z/r08_help_with_temporary_bwrap.sh).

**Estos binds son organización del entorno, no aislamiento del kernel.** No se presenta PRoot como protección de archivos. El payload de prueba no contenía escrituras y nunca llegó a ejecutarse. No se hizo una traza exhaustiva de escrituras de todo el teléfono; no se afirma esa cobertura. El estado de bootstrap registrado y los archivos sintéticos están en el [inventario final](validation/mestry-sandbox-20261020T080841Z/final_fixture_observations.json).

## Mecanismo realmente observado

La documentación oficial señala selección del primer `bwrap` en PATH y una alternativa incluida que necesita namespaces de usuario. La prueba confirma la selección por PATH, pero no demuestra que el recurso alternativo esté disponible en este `.deb`. [Sandbox oficial](https://learn.chatgpt.com/docs/sandboxing).

Los [argumentos efectivos](validation/mestry-sandbox-20261020T080841Z/actual_codex_sandbox_argv.json) incluyen:

- Raíz enlazada **solo para lectura**, `/dev` propio y directorio del daemon oculto mediante tmpfs sin permisos.
- **`--unshare-user`, `--unshare-pid`, `--unshare-ipc`, `--unshare-net`**, un `/proc` propio, nueva sesión y terminación con el padre.
- **`--cap-drop ALL`** y reentrada al mismo binario como `codex-linux-sandbox`.
- Perfil efectivo con sistema de archivos **restricted**, acceso de raíz **read**, red **restricted** y **`--apply-seccomp-then-exec`** antes del comando.

Esto demuestra **qué mecanismo intentó configurar**, no que consiguiera aplicarlo. El filtro seccomp propio de Codex es una segunda etapa; **no se alcanzó ni validó**. `Seccomp: 2` ya existía por Android/PRoot y no certifica protección del motor.

La ayuda del binario fijado usa **`codex sandbox [COMMAND]`**. La sintaxis anticipada `codex sandbox linux ...` del plan anterior trataba `linux` como el ejecutable del payload. Se corrigió antes de la prueba válida; no se ejecutó ese payload inicial, porque bubblewrap falló antes.

## Resultados de ejecución

Con el home sintético y el helper temporal, el comando válido fue:

```text
codex sandbox -- /usr/bin/printf 'MESTRY_CODEX_SANDBOX_PAYLOAD_REACHED\n'
```

No incluye modelo, autenticación, shell genérica o escritura de archivos. Se lanzó como `mestry`, con timeout y el perfil restrictivo anterior. **Salida 1; stdout vacío.** Error conservado:

```text
bwrap: Can't bind mount /dev/null on null: readlink(/proc/self/fd/N) for "/proc/self/fd/5": Invalid argument
```

El fallo ocurre en el montaje/preparación de `/dev` bajo PRoot, **antes de la segunda etapa seccomp y de `printf`**. No se arregló con relajación de `/proc`, flags de omisión, privilegios o ejecución directa del payload. [Prueba válida y ayuda real](validation/mestry-sandbox-20261020T080841Z/r10_readonly_codex_sandbox_probe.stdout.txt).

| Operación | Resultado |
|---|---|
| Versión Codex | **Funciona**: 0.163.0-alpha.10.2 |
| Ayuda del helper interno | **Funciona**; declara bubblewrap + seccomp |
| Versión bubblewrap bajo PRoot | **Funciona**: 0.12.0 |
| Ayuda correcta `codex sandbox --help` | **Funciona** |
| Arranque de comando protegido | **Falla preparando el sandbox**, rc=1; marcador ausente |
| Lectura/escritura por herramientas de Codex | **No ejecutadas** |
| Escritura permitida dentro del workspace | **No probada**: no se estableció aislamiento |
| Escritura denegada sobre sentinel | **No probada**: no se lanzó una escritura |
| Bloqueo de red del payload | **No probado**, aunque el perfil/argv lo solicita |
| Renderer gráfico de ChatGPT | **No ejecutado ni validado** |

El input y el sentinel mantuvieron su contenido. **No se interpreta esto como una denegación efectiva**, porque no se intentó modificarlos. El resultado del sandbox es **fallo de preparación**, no PASS de enforcement.

## Contraste con el kernel Android, fuera de PRoot

La configuración fue leída mediante ADB ya autorizado, sin root. Se observaron también syscalls en procesos breves Bionic/Termux, fuera de PRoot; los hijos terminaron inmediatamente, sin ejecutar comandos ni escribir archivos.

| Evidencia real | Resultado |
|---|---|
| `CONFIG_USER_NS` | **No habilitado** |
| `CONFIG_PID_NS` | **No habilitado** |
| `CONFIG_SECURITY_LANDLOCK` | **No habilitado** |
| Seccomp/filter y SELinux compilados | **Sí** |
| `unshare(CLONE_NEWUSER)`, AArch64 syscall 97 | **−1, errno 22 `EINVAL`** |
| `unshare(CLONE_NEWPID)`, mismo UID sin capacidades | **−1, errno 1 `EPERM`** |
| UID y capacidades reales | **10348, CapEff=0** |
| `/data` real | **nosuid,nodev**, según preflight |

El errno de PID por sí solo no identifica su causa; la ausencia de PID_NS está demostrada por la configuración. La lista genérica `CONFIG_LSM` menciona Landlock, pero **no lo habilita** cuando `CONFIG_SECURITY_LANDLOCK` está desactivado. [Config real](validation/mestry-sandbox-20261020T080841Z/r01_kernel_configuration.stdout.txt), [observaciones nativas](validation/mestry-sandbox-20261020T080841Z/final_fixture_observations.json).

Se intentó además arrancar **solo `bwrap --version` fuera de PRoot**, con el cargador glibc existente, entorno limpio y `NoNewPrivs=1` añadido al hijo. Terminó **−31, SIGSYS**, sin stdout. No se llegó a la prueba de namespaces/payload de ese helper nativo. **No se identificó la syscall causante ni se atribuye el fallo exclusivamente a bubblewrap**; no se desactivó seccomp para investigarlo. [Resultado nativo y límite](validation/mestry-sandbox-20261020T080841Z/native_bwrap_bootstrap_result.json).

**Sí: la ausencia de USER_NS/PID_NS es un bloqueo definitivo para este mecanismo de bubblewrap sin privilegios en el kernel actual.** Los pide explícitamente y un userland no puede añadirlos. El error de fd/montaje bajo PRoot es otro fallo observado; solucionarlo no restauraría las funciones ausentes del kernel. Tampoco se convierte el root aparente en root Android o un helper SUID funcional.

## Alternativas seguras y decisión

No quedó una alternativa funcional demostrada para conservar **este sandbox del motor y comandos generales** sin modificar Android. Instalar dependencias/otro desktop no cambia el kernel; un posible modo Landlock tampoco dispone de soporte en esta configuración. Seccomp por sí solo no demuestra la política de archivos que el perfil requiere. No se probaron flags para eludir o reducir protecciones.

**El sandbox del renderer es otra frontera.** No se ejecutó ChatGPT ni se inspeccionaron procesos renderer en esta sesión; no se declara que la interfaz abra, que el renderer sea seguro o que haya fallado en un punto concreto. Aunque una interfaz llegara a abrir, no resolvería el fallo del motor observado.

**No merece la pena continuar instalando la app oficial en PRoot en esta configuración para usar Codex con controles conservados.** Se clasifica esa ruta como bloqueada y se recomienda la investigación siguiente, sin ejecutarla:

1. Evaluar **app-server por stdio y una interfaz móvil**, con fixture y entorno sin cuenta al comenzar. Su handshake no demostraría ejecución segura.
2. Comprobar si la versión fijada permite impedir todas las rutas de shell, procesos y archivos que evadan un **ejecutor separado**, con acciones tipadas, parámetros validados y límites de workspace/red. Una UI o token de acceso no sustituye esa frontera.
3. Investigar un ejecutor con **UID Android propio y permisos mínimos**, sin ejecución arbitraria dentro del UID de Termux. Es una propuesta distinta, no un sandbox ya validado ni una instalación autorizada.
4. Incluir denegaciones reales y rechazo de RPC no permitidas antes de cuentas/datos reales. La documentación de app-server identifica `thread/shellCommand` y `process/spawn` como rutas fuera del sandbox normal; deben quedar inaccesibles en la propuesta. Si no puede evitarse que el harness use las rutas bloqueadas o irrestrictas, esa variante también se rechaza. [App-server oficial](https://learn.chatgpt.com/docs/app-server).

No se cambió a Cloud, otro host o un ejecutor sin límites. La investigación futura necesita revisar este resultado antes de nuevas instalaciones.

## Cierre, limpieza y evidencia

El [dictamen estructurado](validation/mestry-sandbox-20261020T080841Z/sandbox_test_summary.json) y el [registro de comandos](validation/mestry-sandbox-20261020T080841Z/commands.md) incluyen fallos y correcciones. Se retiró **únicamente el directorio temporal de EXP05**, tras comprobar ruta, hashes, archivos sintéticos y ausencia de procesos Codex de prueba. Se conserva en WSL la evidencia y el paquete original, fuera de Git.

Los **139 paquetes** permanecieron idénticos, con comparación normalizada por nombre/versión/arquitectura/estado. No se instaló bubblewrap, la app, los 119 paquetes ni servicios. SSH, wrapper Debian, helper X11 y Boot conservaron sus hashes; X11 seguía activo. SELinux **Enforcing**, Verified Boot **green**, flash bloqueado, seccomp heredado activo, RAM Plus **8192**; no hubo reinicio.

Las [muestras de recursos](validation/mestry-sandbox-20261020T080841Z/resources_summary.json) son puntuales, sin carga sostenida o PSS de la app; no constituyen un benchmark. La sesión termina aquí: **sin login, modelos, proyectos personales, renderer, app-server o nuevas instalaciones**.
