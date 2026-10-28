# ChatGPT Linux ARM64 — auditoría EXP04

**2026-10-20. Resultado: BLOQUEADO ANTES DE INSTALAR.** Se obtuvo y verificó el paquete oficial, se inspeccionó sin ejecutar su código y APT resolvió sus dependencias. La configuración real del kernel del S23 carece de **user namespaces y PID namespaces**. Esto impide dar por satisfechos los requisitos del sandbox y activa la condición de parada de la fase 2 solicitada por el usuario.

**ChatGPT no está instalado y no se intentó abrirlo.** No se observó un error de arranque de la aplicación: el bloqueo se detectó antes. No se añadieron ni actualizaron paquetes, repositorios, credenciales o servicios. El criterio inmediato de una interfaz oficial abierta con protecciones conservadas **no se alcanzó**.

## Artefacto y procedencia

La documentación oficial ofrece una preview para Debian 13 y ARM64, con instalación mediante APT. Ese soporte corresponde a Linux desktop y no certifica Android/PRoot. [Documentación oficial](https://learn.chatgpt.com/docs/linux/linux-app).

| Campo | Resultado |
|---|---|
| Paquete y versión **auditados** | `chatgpt` **26.1013.40934** |
| Versión instalada | **Ninguna** |
| Arquitectura declarada y ELF revisados | `arm64`; **AArch64**, sin emulación |
| Formato | Debian `ar`, `debian-binary`, `control.tar.xz`, `data.tar.xz`, `_gpgorigin` |
| Tamaño descargado | **479.841.538 bytes; 457,61 MiB** |
| Installed-Size declarado | **1.599.464 KiB; 1.561,98 MiB**, solo el paquete |
| URL publicada y final | [Instalador ARM64 oficial](https://persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_arm64.deb) |
| SHA-256 | `9ab2cbbaf33cebeaa1e06eb5cab78128936f927a0d97bf00e40694e5f31c629b` |
| Última modificación HTTP | 2026-10-16 22:31:59 UTC |
| Descarga observada | 2026-10-20 07:25 UTC |

Se verificaron **la firma `_gpgorigin` del paquete**, la firma de `InRelease`, el hash del índice ARM64 y la coincidencia de tamaño/SHA-256 del `.deb` con ese índice. Clave pública: **`3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4`**, suministrada en el `postinst` del propio paquete oficial. Esto comprueba consistencia criptográfica; **la confianza inicial procede del enlace oficial y HTTPS**, sin un fingerprint verificado por un canal independiente. No se importó esa clave en Debian.

[Procedencia](validation/mestry-chatgpt-20261020T071932Z/package_provenance.json), [repositorio firmado](validation/mestry-chatgpt-20261020T071932Z/repository_integrity.json), [firma del paquete](validation/mestry-chatgpt-20261020T071932Z/origin_signature_verification.json).

El instalador original se conserva **fuera del proyecto** en `/home/developer/.local/state/mestry/mestry-chatgpt-20261020T071932Z/downloads/chatgpt_arm64.deb`. La URL `latest` es mutable: antes de reutilizarlo hay que comprobar el hash fijado, sin sustituirlo silenciosamente por otra versión.

## Auditoría estática

Se usaron `dpkg-deb`, `ar`, `file`, `readelf`, lectura del encabezado ASAR y búsquedas acotadas de referencias. **No se ejecutaron instaladores, launchers, binarios de OpenAI, código JavaScript ni scripts npm.** La extracción seleccionada quedó en la caché privada de WSL con los archivos sin permiso de ejecución.

El enlace `/usr/bin/chatgpt` apunta a `../lib/chatgpt/codex-launcher`. Ese launcher únicamente resuelve su ruta y ejecuta `/usr/lib/chatgpt/ChatGPT` con los argumentos recibidos. `app.asar` informa versión **26.1013.40934**, metadatos Electron **42.3.0**, build **20770**, y entrada `.vite/build/early-bootstrap.js`; la versión de Electron es un dato del paquete, no una consulta al runtime.

Los seis ejecutables principales revisados son AArch64. `ChatGPT` requiere `/lib/ld-linux-aarch64.so.1`, GTK3, GLib/GIO, NSS/NSPR, ATK, D-Bus, CUPS, ALSA, GBM y X11. Sus símbolos GLIBC llegan a 2.25; el Node incluido, a 2.28. Debian dispone de **glibc 2.41**, por lo que no apareció un bloqueo de versión en esos ELF. `resources/codex` y `codex-code-mode-host` no declaran intérprete ni bibliotecas `NEEDED` en la inspección; eso no verifica sus llamadas al kernel ni su ejecución bajo PRoot. [Inventario ELF y hashes](validation/mestry-chatgpt-20261020T071932Z/static_binary_audit.json).

El archivo del paquete no contiene `chrome-sandbox` ni entradas con setuid/setgid. Se encontraron opciones `sandbox: true`, `contextIsolation: true` y `nodeIntegration: false` en varias ventanas del código principal, así como diagnósticos de Chromium sobre falta de sandbox. Son **referencias estáticas**, no prueba de la configuración de todas las ventanas o de protección efectiva. [Auditoría de referencias](validation/mestry-chatgpt-20261020T071932Z/sandbox_keyring_static_audit.json).

### Scripts de mantenimiento

| Script | Efectos previstos, **no ejecutados** |
|---|---|
| `postinst` | Instala una clave pública en `/usr/share/keyrings/chatgpt-archive-keyring.gpg`; gestiona `/etc/apt/sources.list.d/chatgpt.sources`, `/var/lib/chatgpt/repository.sources` y `/etc/default/chatgpt`; actualiza la base desktop si existe la herramienta; contempla cargar un perfil AppArmor o marcarlo deshabilitado en instalaciones sin ABI 4.0 |
| `prerm` | Retira su enlace AppArmor de deshabilitación y descarga el perfil cuando el entorno correspondiente está activo |
| `postrm purge` | Retira sus fuentes/clave, estado de repositorio y defaults; actualiza la base desktop |
| `preinst` | Ausente |

El perfil AppArmor incluido es `flags=(unconfined)` con permiso `userns`. **No sustituye la función del kernel ni configura SELinux.** En este Debian faltan ABI AppArmor 4.0, `aa-enabled` y `apparmor_parser`; no se ejecutaría la rama de carga en el estado inspeccionado. No se aplicó ninguna rama ni se crearon los archivos del repositorio. [Control completo](validation/mestry-chatgpt-20261020T071932Z/package_control.txt), [postinst](validation/mestry-chatgpt-20261020T071932Z/control_postinst.txt), [prerm](validation/mestry-chatgpt-20261020T071932Z/control_prerm.txt), [postrm](validation/mestry-chatgpt-20261020T071932Z/control_postrm.txt).

## Dependencias, D-Bus y almacenamiento previsto

Se simularon `apt-get --simulate --no-install-recommends install /tmp/mestry-chatgpt-20261020T071932Z/chatgpt_arm64.deb` y una segunda resolución con **`--assume-no`**, que respondió `N` y abortó antes de descargar o instalar. Ambas usaron root **aparente** de PRoot para el gestor de paquetes; ningún proceso de la app se ejecutó como root.

| Transacción propuesta por APT | Resultado |
|---|---|
| Paquetes nuevos | **119**, incluidos ChatGPT y **118 dependencias** |
| Actualizaciones | **1**: `liblzma5`, `5.8.1-1+deb13u1` → `5.8.1-1+deb13u2` |
| Eliminaciones | **0** |
| Descarga adicional | **80,9 MB**; 561 MB contando el `.deb` local |
| Espacio adicional estimado | **2.054 MB decimales, ≈1,91 GiB**, sin contar conservar el instalador |
| Cambios realmente aplicados | **0 paquetes nuevos; 0 actualizados** |

Lista íntegra con versiones: [transacción propuesta](validation/mestry-chatgpt-20261020T071932Z/apt_planned_packages.tsv). Los **139 paquetes instalados** mantuvieron el mismo inventario antes, después de simular y al terminar: [antes](validation/mestry-chatgpt-20261020T071932Z/packages_before.tsv), [después](validation/mestry-chatgpt-20261020T071932Z/packages_after.tsv).

La resolución incorpora GTK, Mesa/LLVM, Vulkan, D-Bus, udev y systemd incluso sin recomendaciones. Una cadena demostrada es **ChatGPT → `libtss2-tcti-device0t64` → `tpm-udev` → `udev` → proveedor de sysusers**; el solver eligió systemd. `dbus-user-session` también arrastra `libpam-systemd` y `systemd-sysv`. Existen alternativas de paquetes en algunas ramas, por lo que esta lista **no se declara el mínimo universal**. No se forzaron dependencias, se construyeron paquetes ficticios ni se instaló un init dentro de PRoot. [Resolución y estimación](validation/mestry-chatgpt-20261020T071932Z/p13_apt_simulation.stdout.txt), [cadenas](validation/mestry-chatgpt-20261020T071932Z/p15_dependency_chain_audit.stdout.txt).

La imagen actual no tiene `dbus-run-session`, `dbus-daemon`, `gnome-keyring-daemon` ni `bwrap`. Una eventual GUI requeriría evaluar un bus de **sesión** con ciclo de vida acotado; instalar bibliotecas D-Bus no acredita que exista un bus funcional. No hay XFCE instalado ni demostrado imprescindible.

El binario Codex contiene referencias a Secret Service/keyring y a **fallback a almacenamiento en archivo** cuando falla el keyring. Esto **no demuestra** qué ruta elegiría la interfaz ni que se cifrarían sus credenciales. El keyring/almacenamiento queda pendiente y bloquea el login hasta una revisión específica.

## Bloqueo del kernel y fronteras de seguridad

El kernel real, leído fuera de PRoot, es **`5.15.DRIVE_ID_04_EXAMPLE`**. El `uname` sintético del invitado no se usa como prueba de capacidades.

| Prueba observada | Resultado e implicación |
|---|---|
| `/proc/config.gz`, lectura ADB sin root | `CONFIG_NAMESPACES=y`; **`# CONFIG_USER_NS is not set` y `# CONFIG_PID_NS is not set`**; NET_NS, SECCOMP, SECCOMP_FILTER y SELINUX habilitados |
| `unshare(CLONE_NEWUSER)` nativo, syscall AArch64 97 en proceso breve de Termux | **−1, errno 22 `EINVAL`**; no crea el namespace |
| `unshare --user --map-root-user true` como `mestry` dentro de PRoot | Devuelve **0**, pero no aparece `/proc/self/ns/user`, el UID real sigue siendo **10348** y el namespace de montaje no cambia |
| Montaje real `/data` y `/data/user/0` | **`nosuid,nodev`**; el root aparente no habilita un helper SUID con root Android |
| Capacidades reales | **`CapEff=0`**; el UID 10349 de `mestry` es aparente |

[Syscall y comparación](validation/mestry-chatgpt-20261020T071932Z/p07_actual_namespace_probe.stdout.txt), [configuración real del kernel](validation/mestry-chatgpt-20261020T071932Z/p18_android_final.stdout.txt), [montajes](validation/mestry-chatgpt-20261020T071932Z/p05_phone_origin_kernel_prereqs.stdout.txt).

**Renderer:** el paquete Chromium/Electron no aporta un helper SUID y el kernel no ofrece las namespaces indicadas. Es un bloqueo de prerrequisitos para aceptar un renderer protegido en esta configuración. **No se ejecutó el renderer** ni se certificó su fallo exacto de arranque. Las cadenas `No usable sandbox` encontradas son parte del binario, no un log generado al abrirlo. No se aplicaron `--no-sandbox`, flags para omitir protecciones, setuid ni permisos privilegiados.

**Comandos Codex:** la documentación Linux utiliza `bwrap` de PATH o un helper incluido que requiere namespaces de usuario no privilegiadas. El Codex incluido contiene referencias a bubblewrap, seccomp y Landlock. La configuración de este kernel incumple el prerrequisito de user namespaces; **no se ejecutó ese helper ni se ensayaron operaciones permitidas/denegadas**. Instalar `bubblewrap` o cambiar solo la interfaz no añade funciones al kernel. [Documentación oficial del sandbox](https://learn.chatgpt.com/docs/sandboxing).

El `Seccomp: 2` observado en Termux/PRoot **no certifica el sandbox de un renderer o de Codex**: ya existía sin la app. PRoot tampoco es una frontera de seguridad entre procesos con el mismo UID Android. No se atribuye este bloqueo a todo Android 16 ni a todos los Samsung: corresponde al kernel/configuración observados en este S23.

## Resultados separados

| Etapa | Estado |
|---|---|
| Suministro y revisión del paquete | **VERIFICADOS**, con límite de anclaje de confianza explícito |
| Resolución APT | **RESUELTA**, transacción no aplicada |
| La aplicación se instala | **NO EJECUTADO**: parada durante auditoría |
| La interfaz abre | **NO INTENTADO**: no hay captura ni ventana oficial |
| Renderer protegido | **NO VALIDADO**, prerrequisitos bloqueados |
| Autenticación | **NO INTENTADA**, por instrucción del usuario |
| Codex abre proyectos | **NO PROBADO**, sin acceso a proyectos personales |
| Codex ejecuta comandos controlados | **NO PROBADO**, helper no ejecutado |

[Dictamen estructurado](validation/mestry-chatgpt-20261020T071932Z/acceptance_review.json).

## Recursos antes y después de la auditoría

Tres muestras por extremo, sin controlar actividad del resto de Android: **07:23:46–50 UTC** y **07:33:52–56 UTC**. No son medidas de rendimiento de ChatGPT, que nunca estuvo ejecutándose. [Datos y límites](validation/mestry-chatgpt-20261020T071932Z/resources_summary.json).

| Métrica | Antes | Después |
|---|---:|---:|
| RAM disponible, mediana | **3,317 GiB** | **3,247 GiB** |
| PREFIX Termux | **428,06 MiB** | **428,09 MiB** |
| Home Termux | **0,91 MiB** | **0,91 MiB** |
| Almacenamiento libre Android | **212,079 GiB** | **212,082 GiB** |
| Temperatura de batería | **24,0 °C** | **24,2 °C** |
| Estado térmico Android | **0** | **0** |
| RAM/PSS de ChatGPT | **No aplicable** | **No medido: no se lanzó** |

La copia temporal para APT ocupó **458,07 MiB asignados** en el teléfono y se retiró tras comprobar su hash. PREFIX terminó con una diferencia observada de **28 KiB**; no se atribuye a una instalación. El rootfs final ocupa **221,87 MiB** y la caché OCI **47,52 MiB**, ambos ya contenidos en PREFIX. La primera consulta `du` deduplicó subdirectorios al incluir también su padre: no produjo una medida independiente inicial del rootfs para EXP04; la lectura final se hizo con invocaciones separadas. No se reutiliza la medida histórica como una nueva observación inicial.

Se conservan el `.deb` y la extracción de análisis **en WSL**, fuera del proyecto; sus tamaños se registran aparte. La temperatura de batería no es temperatura de CPU y no se ensayó carga de la app. SELinux permanece **Enforcing**, Verified Boot **green**, flash bloqueado y RAM Plus **8192**. No se reinició el teléfono.

## Reproducción, recuperación y reversión

El [índice de comandos](validation/mestry-chatgpt-20261020T071932Z/commands.md) y el [manifest](validation/mestry-chatgpt-20261020T071932Z/manifest.json) conservan scripts exactos, stdout/stderr, tiempos, códigos de retorno y hashes. El registro de instalación explica los fallos de descarga y las redacciones de cookies transitorias del CDN.

Comprobación actual desde WSL, sin instalar ni abrir la app:

```bash
ssh mestry-s23 '$HOME/bin/mestry-debian /usr/local/bin/mestry-check'
ssh mestry-s23 '$HOME/bin/mestry-x11 status'
ssh mestry-s23 '$HOME/bin/mestry-debian /usr/bin/test ! -e /usr/bin/chatgpt'
sha256sum /home/developer/.local/state/mestry/mestry-chatgpt-20261020T071932Z/downloads/chatgpt_arm64.deb
```

La comparación nativa/PRoot es reproducible con el [script de diagnóstico p07](validation/mestry-chatgpt-20261020T071932Z/p07_actual_namespace_probe.sh) a través de SSH. La simulación requiere volver a preparar **solo una copia verificada** en tmp compartido; el staging de esta sesión ya no existe. No repetir una instalación ni ejecutar el `postinst` manualmente para reproducir esta auditoría.

**Estado de recuperación:** SSH, wrapper Debian, helper X11 y hook Boot conservaron sus hashes; el display `:1` sigue activo, y TCP 6001 rechaza conexiones por IPv4/IPv6 loopback. No se abrió otro servidor ni se cambió el arranque. La recuperación tras reinicio continúa pendiente.

**Reversión aplicada:** retirada exclusivamente de la copia temporal y su directorio vacío en el teléfono, con guardas de ruta/no-symlink/hash. **No hace falta desinstalar ChatGPT o dependencias**, porque no se instalaron. No retirar Debian, Termux, X11 o Boot para revertir esta auditoría. La caché local WSL puede archivarse o retirarse posteriormente por su ruta de sesión verificada; no contiene credenciales.

Si otra sesión llegara a instalar el paquete, antes de revertir se debe simular `apt-get --simulate purge chatgpt`, comparar con el inventario de esa sesión y revisar sus fuentes/clave/defaults. Revisar `autoremove` aparte: no ejecutar una retirada masiva basándose en esta transacción **no aplicada**.

## Recomendación y siguiente experimento mínimo

**No iniciar sesión ni instalar toda la transacción para intentar sortear este bloqueo.** La aprobación de instalación estaba condicionada a superar la auditoría; esa condición no se cumplió. Este informe no solicita permiso para desactivar protecciones, obtener root o modificar el kernel.

La continuación mínima propuesta, **pendiente de autorización**, es probar exclusivamente el **Codex AArch64 estático incluido en este mismo paquete**, con su hash ya fijado y un fixture desechable, sin GUI, instalación de dependencias, credenciales ni peticiones al modelo:

1. Preparar solo ese binario como archivo de prueba, verificar SHA-256 **`5412ef3ceacc22a058cf19382dbfd85305e405f7275ac36300375998b2ad3fc3`** y consultar su `--help` como `mestry`.
2. Si su ayuda confirma la interfaz, invocar el diagnóstico `sandbox linux` para `/usr/bin/true`, con timeout y sin flags de bypass. Capturar el error real de su helper, no solo un mensaje inferido del kernel.
3. Si devuelve éxito, comprobar namespaces/controles y una escritura denegada sobre un sentinel **sintético** fuera del workspace; un retorno 0 no acredita aislamiento. Si no puede demostrarse la denegación efectiva o propone acceso irrestricto, detener.
4. Si confirma la incompatibilidad, revisar la viabilidad de ejecución local antes de invertir en otro frontend. Cambiar la arquitectura o el host requiere una decisión explícita del usuario.

Esta propuesta **no se ejecutó**. Su resultado no demostraría que la GUI abre, que el renderer está protegido o que el login es seguro. La fase actual termina en la auditoría bloqueada, con el entorno gráfico mínimo previo conservado.
