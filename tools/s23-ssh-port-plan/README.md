# EXP07: Termux 8022 → 8023

**Completada y verificada el 2026-10-20: Termux en 8023; reversión cancelada.** El usuario autorizó «si, dale con eso» y confirmó «funciona en el 8023» durante la prueba paralela. El daemon principal, helper, Boot y alias WSL usan 8023. Conexiones nuevas S25/WSL verificadas; ADB confirma un único daemon, 8022 libre y Horus apagado. Ambas claves intactas. No volver a ejecutar la etapa paralela ni el corte sobre este estado. [Evidencia](../../docs/validation/mestry-s25-port-migration-20261020T224339Z/commands.md).

El temporizador empezó a las **22:59:36 UTC (19:59:36 Chile)**. Desde una conexión nueva, el S25 ejecutó `~/bin/mestry-ssh-check` y obtuvo **`MESTRY_S25_CANONICAL_8023=PASS` a las 23:01:37 UTC**. El verificador comprobó origen S25, descendencia del daemon principal, política, claves y comprobación WSL; escribió los marcadores bajo bloqueo. `r11/r13` comprobaron esos marcadores y la salida del temporizador. **No hay una reversión automática pendiente.** El comando es específico de esta migración y no debe reutilizarse para otra. [Salida del usuario](../../docs/validation/mestry-s25-port-migration-20261020T224339Z/s25-final-user-confirmation.json).

Respaldo privado WSL: `~/.cache/mestry/s23-port-migration-20261020T224339Z/{config,known_hosts}`. Recuperación puntual WSL tras reversión: `ssh -p 8022 mestry-s23`. Las entradas de confianza anteriores se conservan. La ejecución manual del hook pasó; el arranque tras reinicio no se ensayó.

Los siguientes apartados conservan el procedimiento preparado y aplicado para revisión y recuperación. Estos archivos no son un instalador automático ni archivos de inicio de WSL.

**Preparación realizada:** `q04` ya guardó el respaldo y las propuestas inactivas en `~/.local/state/mestry/ssh-port-8023-20261020T222743Z`. No recrear esa carpeta ni sobrescribir sus respaldos. Antes de aplicar, comprobar su integridad y revalidar el estado activo; el procedimiento de abajo conserva también los pasos previos para revisión.

Resultado buscado: un único SSH Termux en 8023, Horus oficial en loopback 8022 cuando se empareje después, claves existentes conservadas. No se copian claves privadas ni se alteran Debian/X11/Android.

## Antes del cambio autorizado

1. Revalidar IP, SSH actual, ADB, huellas, hashes de archivos y ausencia del destino `10-mestry-port.conf`. Mantener la conexión actual del S25 y otra WSL en 8022. ADB permite abrir Termux, pero la recuperación local puede requerir desbloquear físicamente el S23.
2. Copiar las plantillas a una carpeta privada de Termux con nombre único `~/.local/state/mestry/ssh-port-8023-20261020T222743Z`. Usar permisos 700 para carpeta/scripts, 600 para configuraciones y respaldos. Guardar en ella:
   - Copia de la configuración principal `sshd_config.before` y de los drop-ins existentes, sin claves privadas.
   - El helper actual como `ssh-start.before` y el hook actual como `boot.before`.
   - La propuesta de puerto como `10-mestry-port.conf.proposed`, más `rollback.sh` y `rollback-timer.sh`.
   - Hash de `authorized_keys`, sin reemplazar ese archivo durante migración o reversión.
3. Guardar fuera de Git el respaldo de `~/.ssh/config` y `known_hosts` de WSL. Dejar al usuario la ruta concreta del respaldo y la orden local de reversión **antes de recargar el daemon**.

## Prueba paralela en 8023

Los siguientes son comandos **futuros**, en Termux, tras autorización. `mestry_migration` debe contener la carpeta privada real creada en el paso anterior; no ejecutar con una ruta de ejemplo.

```sh
# La opción de puerto afecta únicamente a este segundo daemon temporal.
sshd -t -p 8023 -o "PidFile=$mestry_migration/stage.pid"
sshd -p 8023 -o "PidFile=$mestry_migration/stage.pid"
mestry_stage_pid=$(cat "$mestry_migration/stage.pid")
awk '{print $22}' "/proc/$mestry_stage_pid/stat" > "$mestry_migration/stage.starttime"
```

Comprobar una conexión WSL nueva a 8023 usando la identidad existente y la confianza del servidor ya verificada (`HostKeyAlias=[IP_ACTUAL]:8022` para esta prueba puntual). En el S25, duplicar el perfil Termux, conservar el perfil 8022 y poner **solo Puerto = 8023** en el duplicado; volver a comprobar la misma huella Ed25519 y ejecutar `whoami`. No cerrar 8022 hasta que ambas pruebas pasen.

## Persistencia y transferencia al daemon principal

1. Instalar la propuesta como `$PREFIX/etc/ssh/sshd_config.d/10-mestry-port.conf`; reemplazar helper y hook con sus plantillas mediante archivos temporales y `mv`, con permiso 700. La configuración principal y la autenticación permanecen intactas. `sshd -t` debe pasar y `sshd -T` debe mostrar **solo Port 8023**, sin contraseña ni teclado interactivo.
2. Antes de retirar el listener temporal o recargar el principal, iniciar la protección en el teléfono:

   ```sh
   nohup sh "$mestry_migration/rollback-timer.sh" "$mestry_migration" \
     </dev/null >"$mestry_migration/rollback-timer.log" 2>&1 &
   ```

   El temporizador dura cinco minutos y deja de actuar al aparecer `confirmed`. Su reversión toma `migration.lock` y vuelve a comprobar ese marcador para evitar la carrera con la confirmación. No depende de WSL; no certifica supervivencia ante una terminación de la app por Android.
3. Verificar PID, nombre y tiempo de inicio del listener temporal antes de terminar **solo ese listener**; no usar `pkill`, no matar sesiones ni otros servicios. Enviar `HUP` únicamente al daemon principal validado en `$PREFIX/var/run/sshd.pid` para que relea la configuración y tome 8023. Si falla, ejecutar la reversión mediante la sesión anterior o recuperación local; el temporizador es respaldo adicional.
4. En WSL, actualizar **solo el puerto del alias `mestry-s23` a 8023**. Añadir a `known_hosts` el mismo material de clave pública de servidor ya autenticado para `[IP_ACTUAL]:8023`, conservando la confianza anterior y `StrictHostKeyChecking yes`. No aceptar ciegamente una clave obtenida de la red.
5. Abrir conexiones independientes desde WSL y S25, sin reutilizar sesiones antiguas. Verificar el puerto real, usuario, claves autorizadas y helper/Boot; ADB debe mostrar Termux en 8023 y ausencia de escucha 8022 mientras Horus siga apagado.
6. Solo tras esas verificaciones, confirmar desde una conexión nueva a 8023:

   ```sh
   # Comprobar primero que SSH_CONNECTION termina en 8023.
   (
     flock -x 8
     : > "$mestry_migration/confirmed"
   ) 8>"$mestry_migration/migration.lock"
   ```

   No emparejar ni activar Horus hasta cancelar la reversión. No reiniciar para probar Boot sin aviso y autorización del ensayo.

## Recuperación

Antes del cambio se anotará la orden con la ruta real:

```sh
sh "$HOME/.local/state/mestry/ssh-port-8023-20261020T222743Z/rollback.sh" \
   "$HOME/.local/state/mestry/ssh-port-8023-20261020T222743Z"
```

Si falla SSH, en WSL seleccionar por modelo el transporte ADB autorizado del SM-S918B y ejecutar `adb.exe -t TRANSPORTE shell am start -W --user 0 -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.termux/.app.TermuxActivity`. Desbloquear el S23, introducir allí la orden anterior y reconectar por 8022. En WSL puede usarse temporalmente `ssh -p 8022 mestry-s23`, con la confianza previa conservada; en S25 se mantiene el perfil original 8022.

La reversión elimina únicamente el drop-in esperado, restaura el helper/hook y recarga el daemon. No restaura `authorized_keys`, por lo que conserva la autorización del S25. Si posteriormente Horus ya ocupa 8022, apagar primero su acceso remoto mediante la app antes de una reversión manual; el script rechaza una clave de servidor distinta en ese puerto.

Referencia para los flags de prueba y recarga: [manual oficial `sshd`](https://man.openbsd.org/sshd.8). `-t`/`-T` verifican sin escuchar; `-p` prevalece sobre `Port` del archivo y `HUP` relee mediante reejecución. La aplicación autorizada y sus salidas reales figuran en la evidencia enlazada al inicio; no se ha probado Boot tras reinicio.
