# MESTRY: Debian 13 ARM64 mínimo en el S23

**Recomprobación del 20 de octubre, 19:37 UTC / 16:37 de Santiago:** el comando WSL volvió a pasar y ADB USB respondió. El informe siguiente conserva la entrega mínima de EXP02; el entorno ya incluye avances posteriores de X11 documentados por separado. Esta continuación no reinstaló paquetes ni cambió ajustes. [Registro actualizado](INSTALLATION_LOG.md), [resultados actuales](validation/mestry-debian13-recheck-20261020T193723Z/README.md).

**Resultado del 20 de octubre de 2026: criterio de aceptación cumplido desde WSL2.** Se retomó la instalación existente sin reinstalar y se confirmó de nuevo a **04:39 UTC / 01:39 de Santiago**. El teléfono conserva Android. Esta entrega cierra las fases de acceso y Debian mínimo; el arranque después de reiniciar todavía no se ha probado.

| Comprobación real | Resultado |
|---|---|
| SSH desde WSL | Ed25519 exclusiva aceptada en conexión nueva; puerto 8022, verificación de host conservada |
| Política de autenticación | Exclusivamente claves; contraseña y autenticación interactiva desactivadas. Prueba sin clave rechazada |
| Distribución | **Debian GNU/Linux 13 (trixie)**; archivo de versión **13.7** |
| Arquitectura | **arm64**, mediante PRoot-Distro **5.10.0** / PRoot **5.1.107.98** |
| APT | **3.0.3**; actualización de índices y transacción mínima correctas; repositorios Debian por HTTPS con `Signed-By` |
| Red | DNS funcional y HTTPS con validación de certificado, **HTTP 200** |
| Archivos y procesos | Lectura/escritura/copia con nombre Unicode y proceso hijo terminado correctamente |
| Sin root Android | Usuario invitado `mestry`; kernel conserva **UID 10348**, capacidades efectivas **0** |

Instancia: **`mestry-debian13`**, en el almacenamiento privado de Termux. Imagen oficial Debian 13 ARM64 fijada a `sha256:b55910b579d6eb05ebd79fbc8468b974fa39bb0610d52e1f1390bb2177ab7614`.

Desde WSL, repetir la comprobación completa:

```bash
ssh -o BatchMode=yes mestry-s23 '$HOME/bin/mestry-debian /usr/local/bin/mestry-check'
```

Terminó con código **0** y `MESTRY_DEBIAN13_CHECK=PASS`. [Salida directa desde WSL](validation/mestry-debian13-20261020T040726Z/s18_wsl_acceptance_command.stdout.txt), [repetición en conexión nueva](validation/mestry-debian13-20261020T040726Z/s20_closure_ssh_debian.stdout.txt).

Para entrar interactivamente y salir:

```bash
ssh -t mestry-s23 '$HOME/bin/mestry-debian'
exit  # vuelve a WSL
```

El wrapper entra con `--isolated --user mestry`; el directorio para futuros proyectos es `/home/mestry/projects`. Las tareas de APT que escriben requieren una entrada de mantenimiento con root **simulado** de PRoot, documentada en el registro. No hay sudo ni SSH adicional dentro de Debian.

## Preparación de continuidad

Termux:Boot **0.8.1** tiene un único hook `~/.termux/boot/10-mestry-sshd`. Su helper valida SSH, evita duplicados mediante bloqueo/PID y mantiene un wakelock. Solo arranca **SSH**; Debian se abre bajo demanda. La doble ejecución del hook no duplicó el daemon.

ADB USB responde con UID shell 2000 y puede llevar Termux al frente. La recuperación preparada es **asistida**: desbloquear el teléfono y ejecutar `"$HOME/bin/mestry-ssh-start"` en Termux si SSH falla. No se concedió ejecución arbitraria de comandos entre apps. El ensayo local con relanzamiento previamente programado recuperó el daemon en **≤2 s**; no demuestra un supervisor permanente ni recuperación ADB completamente automática.

El usuario confirmó ambas apps **Sin restricciones**, con suspensión y notificaciones revisadas. ADB corroboró excepciones Doze y permisos de segundo plano; RAM Plus y protección de carga siguen iguales. No quedan cambios manuales de batería solicitados en esta entrega.

**Reinicio pendiente:** no se reinició el teléfono. El registro contiene el procedimiento para probar Boot sin abrir Termux tras el primer desbloqueo. Se debe prever intervención física: Android mantiene el almacenamiento cifrado por credenciales inaccesible hasta el primer desbloqueo, y el comportamiento de este firmware sigue pendiente de ensayo. [Direct Boot](https://developer.android.com/privacy-and-security/direct-boot?hl=en). La apertura inicial de Boot y sus scripts siguen el [procedimiento oficial](https://github.com/termux/termux-boot#how-to-use).

## Recursos medidos

| Métrica | Resultado |
|---|---:|
| Instancia Debian en disco | **196,21 MiB** |
| Caché OCI conservada | **47,52 MiB** |
| Incremento de PREFIX + home, incluidas dependencias Termux | **303,81 MiB** |
| Datos libres en la comprobación final | **212,08 GiB** |
| RAM visible Android / disponible final | **6,91 / 3,18 GiB** |
| PSS de PRoot + `sleep`, tres muestras | **2,31 MiB** |

El PSS corresponde solo a una sesión mínima inactiva; no representa el coste de una interfaz gráfica. La memoria disponible fluctuó entre estados y no permite atribuir todo el cambio a Debian. La instancia y su caché ya están incluidas en el incremento de Termux. [Muestras originales](validation/mestry-debian13-20261020T040726Z/resources.json).

## Evidencia y límites de la entrega

Se instalaron únicamente `ca-certificates`, `curl`, `procps` y dependencias obligatorias dentro de Debian. En Termux se instalaron PRoot-Distro y sus dependencias, con una sola actualización necesaria de `ncurses`; no hubo upgrade general.

Se conserva un error de instrumentación: después de instalar correctamente los paquetes, `proot-distro --version` devolvió 1 porque ese subcomando no existe en esta versión. Se comprobó el CLI real y el estado instalado sin repetir la instalación. Los demás resultados operativos y stderr están en el [registro completo y procedimientos de recuperación](INSTALLATION_LOG.md), el [anexo de comandos exactos](validation/mestry-debian13-20261020T040726Z/commands.md) y el [manifest con hashes](validation/mestry-debian13-20261020T040726Z/manifest.json).

PRoot conserva el UID Android de Termux: `--isolated` reduce enlaces automáticos de archivos y **no certifica un sandbox de seguridad**. V01.1/V01.2 están verificadas solo en su alcance preparatorio; la app, gráficos y fronteras de procesos siguen pendientes.

No se realizaron nuevas deshabilitaciones, cambios de RAM Plus, root, bootloader, particiones, reinicio, login ni inferencia. No se crearon túneles o reglas públicas; los listeners SSH comodín eran preexistentes y no se verificó alcance WAN. Las claves privadas permanecen fuera del proyecto.

**Detenido al completar Debian mínimo.** La fase posterior será evaluar Termux:X11 y gráficos mínimos, con sus comprobaciones de compatibilidad y seguridad; no se instalaron XFCE, Termux:X11 ni Codex.
