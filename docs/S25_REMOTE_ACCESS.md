# EXP07 — Control S25 → S23 sin PC

Fecha: 2026-10-20 (Chile). **S25 → Codex en Horus PASS: tarea de archivos y comprobación desde otra conexión verificadas; recuperación de conversación confirmada por el usuario.** Codex CLI 0.163.0 creó y modificó `S25_REMOTE_TEST.txt` en el proyecto sintético; el S25 leyó el resultado desde otra sesión y los tres fixtures originales conservan sus hashes EXP06. ADB observó Codex como hijo de la sesión SSH bajo el UID Android de Horus. Horus usa solo `127.0.0.1:8022`; Termux conserva 8023 y sus dos claves. El aviso de 15 minutos corresponde al bloqueo de la interfaz local, según aclaración del usuario y código de Horus 1.0.4. Proceso tras desconexión, Boot tras reinicio y PC apagado aún no probados. EXP06 no se repitió.

## Estado observado

| Comprobación | Resultado real |
|---|---|
| Dirección del S23 por ADB | **Última: `192.0.2.15/22`** a las 23:27:35 UTC. Durante la preparación también estuvo en `10.211.130.70/24` |
| WSL → Termux | Conexión nueva por clave en **8023: PASS**, usuario `u0_a348`, daemon principal 2975 comprobado por ascendencia |
| Confianza del servidor | La nueva IP presentó exactamente la clave Ed25519 previamente conocida |
| SSH de Termux | **Solo 8023**, IPv4/IPv6 y por clave, daemon principal PID 2975. Listener temporal 13734 retirado; 8022 está reservado al loopback de Horus |
| Helper / Termux:Boot | Actualizados a 8023; ejecución manual del hook: `ready pid=2975 port=8023`. No se reinició el teléfono |
| Reenvío TCP | `AllowTcpForwarding yes`, `DisableForwarding no`, `PermitOpen any`; **tráfico real S25 → Termux → Horus PASS mediante ProxyJump** |
| Claves autorizadas | WSL conservada y nueva Ed25519 `mestry-s25` añadida de forma atómica; no se copiaron claves privadas |
| Recuperación ADB | Shell UID 2000 y actividad local Termux disponibles; no permite escribir directamente en el home privado de Termux |
| Horus remoto | **`enabled=true`, `state=running`, 1 clave, `authorized=true` para el S25**; Dropbear UID Android 10350, escucha real `127.0.0.1:8022` |
| Huella de servidor Horus | **`SHA256:CONFIGURE_LOCAL_FINGERPRINT`**, obtenida por loopback desde Termux autenticado; distinta de la de Termux |
| S25 → Horus | **PASS**, perfil ProxyJump por Termux; usuario `horus`, `/home/horus`, Alpine 3.24.0 aarch64 y conexión `127.0.0.1 50860 127.0.0.1 8022`; clave S25 confirmada por servidor |
| Codex en perfil SSH | **0.163.0 instalado**, login confirmado por el usuario y **tarea sintética PASS**, comprobada desde otra conexión S25; Codex observado bajo el UID Android Horus |
| Archivo sintético remoto | `S25_REMOTE_TEST.txt` contiene `MESTRY_S25_REMOTE_OK` y `estado=modificado`; SHA-256 **`b630aca886c0e78dd680d18838cf9393ebb9be57890a6b1e18a3fb0e6f4f8fcc`** |
| Fixtures anteriores | `saludo.py`, `test_saludo.py` y `README.md` conservan exactamente los hashes verificados en EXP06, según lectura S25 de 23:54:20 UTC |
| Recuperación de conversación | **Confirmada por el usuario** tras solicitar reconexión y `codex resume --last`: «funciona, reaparece la conversacion». No prueba que sobreviva el proceso original |
| Bloqueo de 15 minutos | El usuario aclara: **solo vuelve a pedir contraseña en Horus del S23**. Horus 1.0.4 bloquea la interfaz tras 15 minutos en segundo plano; no ofrece ajuste para desactivarlo ni llama a detener SSH desde ese bloqueo |
| S25 → Termux | **8023 PASS final** a las 23:01:37 UTC: origen `192.0.2.13`, destino `192.0.2.15 8023`, usuario `u0_a348`, ancestro canónico 2975 y `MESTRY_S25_CANONICAL_8023=PASS` |
| Protección de reversión | `wsl-final-confirmed`, `s25-final-confirmed` y `confirmed` verificados en el teléfono; temporizador terminado sin ejecutar reversión |

Durante el alta inicial se actualizó la dirección DHCP del alias WSL `mestry-s23` y se añadió a `known_hosts` la clave pública de servidor ya autenticada, conservando las entradas anteriores. Tras el segundo cambio de red se devolvió el alias a **`192.0.2.15`**. En aquella etapa se mantuvo 8022 y solo se añadió la clave pública del S25; la migración posterior autorizada se detalla debajo. Respaldo local privado inicial: `~/.cache/mestry/s25-ssh-address-20261020T220207Z/{config,known_hosts}`; el segundo respaldo figura en `p11`. No contienen copias de claves privadas. Actualmente el alias usa **8023**, con identidad y verificación estricta conservadas; el respaldo previo al cambio de puerto está en `~/.cache/mestry/s23-port-migration-20261020T224339Z/{config,known_hosts}`.

La sonda inicial al alias antiguo acabó en timeout/255. Después se verificó la nueva IP con `HostKeyAlias=[192.0.2.15]:8022`, antes de actualizar WSL. Una conexión nueva al alias actualizado volvió a pasar. No se interpretó el timeout como fallo de autenticación ni como parada de Termux.

Al intentar el alta, `10.211.130.70` ya no respondió: ADB confirmó que el teléfono había vuelto a `192.0.2.15` y que `sshd` conservaba PID 2975. El intento falló antes de ejecutar comandos remotos; se preservó como `p08`. El alta posterior `p10`, en la dirección actual y comprobando la clave de servidor conocida, terminó en 0:

- S25: **`SHA256:CONFIGURE_LOCAL_FINGERPRINT`**.
- WSL conservada: `SHA256:CONFIGURE_LOCAL_FINGERPRINT`.
- `authorized_keys` final SHA-256: `31d62780157ee7714a7cc1f145d1825ccda9ab761eda38bf92fb492a8f1c7e59`; directorio 700, archivo 600.
- Respaldo privado en Termux: `~/.local/state/mestry/s25-key-20261020T221228Z/authorized_keys.before`. Para revocar, retirar únicamente la línea con esa clave/huella; restaurar el respaldo completo solo si no hubo otras altas posteriores.

## Fase 1 — Alta inicial completada en el S25

Los pasos siguientes conservan el alta original en 8022. **Para uso actual, abrir el perfil 8023 ya verificado**; el perfil original 8022 solo se conserva como recuperación manual.

Cliente recomendado: **ConnectBot**, paquete `org.connectbot`, desde los enlaces de [su sitio oficial](https://connectbot.org/download/). Permite generar Ed25519 localmente y configurar reenvíos SSH. No requiere instalar un servidor ni un escritorio en el S25. Las guías consultadas describen v1.11.1; confirmar la versión y los nombres de menú de la instalación real.

1. Conectar S25 y S23 a la misma Wi-Fi local. Mantener el puerto actual **8022** durante toda esta fase.
2. En ConnectBot, abrir **Manage pubkeys / Administrar claves públicas** y **+ / Generate**. Elegir **Ed25519** y nombre `mestry-s25`. Proteger la clave con una frase de paso introducida solo en el S25. Ed25519 usa almacenamiento de software en ConnectBot; su opción biométrica de Keystore está documentada para RSA/EC.
3. En la clave nueva, elegir **Copy public key / Copiar clave pública**. Compartir únicamente la línea `ssh-ed25519 AAAA… comentario`. La clave privada y la frase de paso permanecen en el S25. No importar la identidad de WSL.
4. **Completado:** formato y huella validados, clave pública añadida sin reemplazar la de WSL, respaldo privado y permisos 700/600 conservados. Añadir una clave no requiere reiniciar `sshd`.
5. Añadir en ConnectBot un host de tipo **SSH**, nombre `MESTRY — Termux`. Si el editor presenta campos separados: **Servidor/Hostname = `192.0.2.15`**, **Usuario/Username = `u0_a348`**, **Puerto/Port = `8022`**. Seleccionar expresamente la clave `mestry-s25` y conservar el reenvío de agente desactivado. No pegar la cadena compacta con usuario y puerto dentro del campo Servidor: la captura aportada por el usuario muestra que se guardó como hostname literal, mantuvo el puerto 22 y produjo `Unable to resolve host`, antes de alcanzar el servidor. La IP es dinámica: reconfirmarla si cambia de red.
6. Al conectar por primera vez al destino correcto, ConnectBot muestra un aviso para aceptar la clave del **servidor Termux**. Allí aparece su huella; compararla antes de aceptar:

   ```text
   SHA256:CONFIGURE_LOCAL_FINGERPRINT
   ```

7. **Prueba básica completada:** el usuario ejecutó `whoami` desde el S25 y confirmó la respuesta esperada. Para ampliar la evidencia de la conexión en otro ensayo puede ejecutarse:

   ```sh
   echo MESTRY_S25_TERMUX_OK; whoami; id; echo "$SSH_CONNECTION"
   ```

   Debe mostrar el marcador, `u0_a348`, UID 10348 y la conexión cuyo destino es `192.0.2.15 8022`. Registrar salida y hora; distinguir la dirección de origen del S25 de la conexión WSL de esa misma red. Una prueba desde WSL no sustituye este paso.

**Fase 1 y migración completadas.** La confirmación original se conserva como [evidencia humana](validation/mestry-s25-port-plan-20261020T222743Z/phase1_user_confirmation.json). El usuario también confirmó «funciona en el 8023» durante la prueba paralela; `r07` identifica su clave en el registro del servidor. Tras el cambio permanente abrió una conexión nueva y ejecutó `~/bin/mestry-ssh-check`: [salida aportada por el S25](validation/mestry-s25-port-migration-20261020T224339Z/s25-final-user-confirmation.json). El verificador rechazaba sesiones de la etapa temporal, exigía la comprobación WSL y escribió la confirmación bajo bloqueo. La conexión principal, sus marcadores y la salida del temporizador se comprobaron después desde WSL. El emparejamiento y la conexión S25 a Horus se verificaron posteriormente.

## Fase 2 — Emparejamiento y conexión S25 a Horus PASS

Se revisó el código correspondiente a **Horus 1.0.4**, commit instalado `2f8f8a2faebd3d0fbd11dd83340bdcfbac437369`, sin actualizar la app ni instalar su CLI de escritorio.

| Implementación oficial | Consecuencia |
|---|---|
| `RemoteAccess.PORT = 8022`; Dropbear `-p 127.0.0.1:8022` | Horus queda en loopback; no tiene selector de puerto en la interfaz revisada |
| Antes de la migración, Termux escuchaba `0.0.0.0:8022` y `[::]:8022` | El solapamiento se resolvió trasladando Termux a 8023; Horus usa ahora su loopback 8022 |
| Dropbear `-s -w` y perfil no root | Acceso por clave; no habilitar contraseñas SSH ni root |
| Provider limitado al UID shell ADB; `pair` verifica contraseña local de Horus | El SSH ordinario de Termux no puede emparejar por sí solo mediante ese provider |
| `pair` añade la clave y llama a `enable()` | **Emparejar también enciende el servidor**: hacerlo solo después de resolver el conflicto |
| Arranque remoto instala sus dependencias mínimas si faltan | La primera activación puede descargar Dropbear, clientes SSH/SFTP, rsync y zsh dentro de Alpine; no es una reinstalación de Debian |

El conflicto está fundamentado en las escuchas reales de Termux y el bind del código de Horus. **No se activó Horus para provocar un error de bind.** No asumir que UIDs Android distintos les asignan puertos independientes.

Solución **autorizada por el usuario, aplicada y verificada**: **Termux 8022 → 8023**, dejando libre el `127.0.0.1:8022` oficial de Horus. Evita modificar/recompilar Horus y no depende de una IP Wi-Fi fija para reservar la dirección de escucha. [Autorización](validation/mestry-s25-port-migration-20261020T224339Z/authorization.json).

Procedimiento y archivos en [tools/s23-ssh-port-plan](../tools/s23-ssh-port-plan/README.md). Respaldo y scripts en Termux: `~/.local/state/mestry/ssh-port-8023-20261020T222743Z`. Después de autorizar se revalidaron hashes y archivos activos. Se abrió el listener temporal **13734**, inicio `/proc` **8265778**, en 8023; WSL y S25 lo probaron antes del corte. `r08` instaló el drop-in y reemplazó helper/Boot, retiró solo ese listener y recargó el principal **2975**. `r09` actualizó únicamente el puerto del alias WSL y añadió la misma clave pública de servidor ya confiable para 8023; se conserva la entrada anterior de 8022. Origen WSL: `192.0.2.14`; origen S25: `192.0.2.13`. `r12` verificó que no cambió otra opción del cliente y mantuvo `StrictHostKeyChecking`, `IdentitiesOnly` y agente desactivado. **No repetir el corte ni reutilizar esta carpeta para otra migración.** Secuencia ejecutada:

1. **Completado:** conexión real S25 → Termux en 8022 y `whoami`, confirmados por el usuario.
2. **Completado:** ADB y actividad local Termux disponibles; respaldos privados de config, drop-ins, helper/Boot y WSL verificados. La recuperación ADB puede requerir desbloquear físicamente el S23.
3. **Completado:** WSL probó ambos puertos y el S25 confirmó 8023; el registro temporal autenticó su propia clave Ed25519.
4. **Completado:** `Port 8023` instalado mediante el include existente; `sshd -t/-T` correctos y autenticación solo por clave. Guardia iniciada a las 22:59:36 UTC antes del corte.
5. **Completado:** helper, hook, alias y perfil S25 usan 8023. El hook ejecutado manualmente respondió `ready pid=2975 port=8023`; las conexiones nuevas S25/WSL tienen al daemon principal como ancestro.
6. **Completado en el corte:** ADB confirmó un único daemon y 8022 libre, con Horus todavía apagado. S25 canceló la reversión a las 23:01:37 UTC bajo bloqueo; `r13` confirmó que el temporizador terminó. Horus se emparejó después y ocupa solo `127.0.0.1:8022`. **Boot tras reinicio pendiente**, sin reiniciar el teléfono.

Recuperación asistida disponible, sin root:

```sh
# Desde WSL; seleccionar el transporte USB autorizado del SM-S918B.
adb.exe -t TRANSPORTE shell id
adb.exe -t TRANSPORTE shell am start -W --user 0 \
  -a android.intent.action.MAIN -c android.intent.category.LAUNCHER \
  -n com.termux/.app.TermuxActivity
```

Desbloquear físicamente el S23 si procede y ejecutar en Termux el comando de reversión preparado antes del cambio; después, `~/bin/mestry-ssh-start`. ADB abre la terminal, pero no da acceso directo a los archivos privados de Termux. El helper comprueba puerto e identidad del servidor; la recarga durante la migración se realizó expresamente sobre el daemon validado.

Orden de reversión manual conservada para esa migración; **no ejecutarla durante el uso normal en 8023**:

```sh
sh "$HOME/.local/state/mestry/ssh-port-8023-20261020T222743Z/rollback.sh" \
   "$HOME/.local/state/mestry/ssh-port-8023-20261020T222743Z"
```

Restaura el helper/hook originales y el puerto 8022 sin reemplazar `authorized_keys`. La protección temporizada ya fue **cancelada** y su proceso terminó; no se ejecutó una reversión real. Una reversión manual posterior exige apagar primero Horus si estuviera activo para liberar 8022. Tras revertir, usar el perfil S25 original y `ssh -p 8022 mestry-s23` desde WSL; el script del teléfono no modifica esos clientes. El respaldo WSL permite recuperar la configuración anterior tras comprobar que no haya cambios posteriores que conservar.

### Emparejamiento y ProxyJump verificados

El usuario autorizó «dale con eso, deje horus prendido». El preflight `s01` encontró `enabled=false`, `stopped`, cero claves y `authorized=false` para el S25; tener la app abierta no acreditaba un servidor SSH activo. `s02` accedió correctamente a Termux 8023 y terminó en 1 únicamente porque todavía no había una clave de servidor Horus en loopback; no fue un fallo de autenticación Termux.

Se preparó [horus_pair_s25.py](../tools/horus_pair_s25.py), comprobado con 13 pruebas offline y consultas reales sin mutación. El usuario lo ejecutó en su terminal WSL e introdujo allí la contraseña local mediante `getpass`; confirmó «listo». El [resultado](validation/mestry-horus-pair-20261020T232711794480Z/result.json) registra `ok`, la huella S25 esperada y autorización posterior `true`. Solo se añadió `mestry-s25`, sin generar identidad WSL ni transferir claves privadas. El provider activó el remoto e inició sus dependencias mínimas; `s06` lo comprobó después en **running**, con una clave y escucha exclusiva `127.0.0.1:8022` bajo UID Android 10350. `s07` confirmó Termux 8023 y sus dos claves conservadas.

La huella del servidor **Horus** obtenida por loopback dentro de Termux autenticado es:

```text
SHA256:CONFIGURE_LOCAL_FINGERPRINT
```

Ruta verificada, usando el campo ProxyJump de la instalación real del S25:

```text
ConnectBot S25 → perfil Termux S23:8023
  canal SSH direct-tcpip → horus@127.0.0.1:8022 (Alpine de Horus)
```

Perfil verificado `MESTRY Horus`: Host **`127.0.0.1`**, usuario **`horus`**, puerto **`8022`**, clave **`mestry-s25`**, ProxyJump **perfil Termux 8023**. Mantener reenvío de agente apagado y comparar la huella Horus anterior al conectar. La clave privada firma localmente ambas autenticaciones en ConnectBot. El código oficial abre el destino desde el salto, sin listener local adicional; **la prueba real del S25 pasó**. [Instrucciones, límites y revocación](../tools/HORUS_S25_PAIRING.md).

Prueba completada desde el nuevo perfil, sin ejecutar `codex` en ese diagnóstico:

```sh
echo MESTRY_S25_HORUS_OK; whoami; id; echo "$HOME"; echo "$SSH_CONNECTION"; uname -m; cat /etc/alpine-release
```

La [salida aportada por el usuario](validation/mestry-horus-s25-20261020T232332Z/s25-horus-user-confirmation.json) muestra el marcador, usuario `horus`, UID 1000, home `/home/horus`, Alpine 3.24.0 y `aarch64`. La conexión termina en `127.0.0.1 8022`; su origen loopback es normal tras el salto. `s08` corrobora la autenticación S25 y el puerto origen 50860 a las 20:29:20 del teléfono. Esta prueba se distingue de las consultas WSL y del emparejamiento. Evidencia: [sondas](validation/mestry-horus-s25-20261020T232332Z/commands.md).

### Referencia del mecanismo oficial y alternativa de túnel

El mecanismo oficial `horus pair` genera una identidad **del computador** en `~/.horus`, pide la contraseña de Horus y envía su clave pública por ADB. Para esta fase se usó directamente el mismo provider con `keyType`, `keyData` y `label` de la identidad exclusiva S25; no se instaló `horus-cli`. La contraseña viajó por stdin de ADB, sin eco, archivos, historial ni argumentos WSL. Android `content` recibe transitoriamente el argumento base64 requerido por el provider; base64 no es cifrado. Los registros del helper conservan solo campos permitidos de las respuestas. La interfaz de Horus permite encender/apagar y revocar claves, pero no ofrece un formulario para añadirlas.

Este emparejamiento inicial necesita ADB autorizado una vez; el transporte ordinario posterior será SSH por Wi-Fi. El método `start` no activa un remoto deshabilitado y el método `pair` sí lo activa. Antes de emparejar deben estar verificados 8023 y la liberación de 8022. Obtener y comparar separadamente la huella del servidor **Horus**: la de Termux no es intercambiable con ella.

Alternativa documental de túnel, **no aplicada**; ProxyJump ya pasó sin añadir otro puerto de escucha:

```text
ConnectBot S25 → SSH Termux S23:8023
  túnel Local: S25:18022 → S23:127.0.0.1:8022
  segunda conexión S25: horus@127.0.0.1:18022 → Alpine de Horus
```

En el host Termux de ConnectBot: **Edit port forwards → Local**, puerto origen **18022**, destino **127.0.0.1:8022**. Mantener abierta esa conexión; abrir un segundo host SSH `horus@127.0.0.1:18022` usando la clave del S25 emparejada. No usar Mosh, reenvío remoto ni de agente. No crear ningún `adb forward` como dependencia diaria.

ConnectBot documenta que sus listeners locales usan `InetAddress.getLocalHost()` y no ofrece dirección de bind configurable. **Verificar en el S25 que 18022 queda limitado a loopback antes de aceptar el túnel como privado**; durante la preparación puede usarse ADB del S25 solo para observar ese bind. Si la versión instalada no permite garantizarlo, detenerse y evaluar OpenSSH en Termux del S25 con `-L 127.0.0.1:18022:127.0.0.1:8022`, sin instalarlo automáticamente. Tener el túnel habilitado en un menú no demuestra que su tráfico llegue a Horus.

El perfil Termux conserva ProxyJump **Ninguno**. El perfil nuevo Horus selecciona ese Termux como salto; no modificar el perfil Termux para que salte hacia sí mismo. El código [SSH.kt oficial](https://github.com/connectbot/connectbot/blob/main/app/src/main/java/org/connectbot/transport/SSH.kt), consultado el 2026-10-20, usa `openDirectTcpipTransport(destination.hostname, destination.port)` y verifica la clave del salto con su propio perfil. Esa revisión no acredita la prueba real del cliente instalado.

## Fase 3 — Tarea sintética y lectura independiente PASS; conversación recuperada

El [diagnóstico de lectura desde S25](validation/mestry-horus-s25-20261020T232332Z/s25-codex-preflight-user-output.json) encontró la función de shell `codex`, el stub `/usr/local/bin/codex` con `# horus-agent-stub`, ausencia de `$HOME/.local/lib/node_modules/@openai/codex/bin/codex.js` y el directorio sintético `/workspace/projects/mestry-horus-smoke`. No ejecutó Codex ni leyó credenciales.

El usuario ejecutó `cd /workspace/projects/mestry-horus-smoke && codex --version && codex login status` y aportó la [salida del instalador](validation/mestry-horus-codex-auth-20261020T234450Z/installation-user-output.json): `added 2 packages in 48s`, `Codex is installed.`, **`codex-cli 0.163.0`** y **`Not logged in`**. Se registra instalación reportada desde S25; no se atribuye al perfil remoto el login previo del harness. El tiempo de npm no es un benchmark controlado.

Se solicitó en la misma terminal S25 `codex login --device-auth`, abrir el enlace mostrado en el navegador del S25 e introducir allí el código de un solo uso, manteniendo SSH abierto. Según [OpenAI Docs](https://learn.chatgpt.com/docs/auth#login-on-headless-devices), esta es la ruta indicada para CLI remota; el acceso por código debe estar permitido en la configuración de seguridad de la cuenta o del workspace. El usuario confirmó **«ya estoy logged in»**: [confirmación conservada](validation/mestry-horus-codex-auth-20261020T234450Z/login-user-confirmation.json). Se registra login confirmado por el usuario, sin transcripción íntegra del estado. No se capturan enlaces de login, códigos, tokens ni archivos de credenciales, ni se transfieren tokens o historiales del harness para simular continuidad.

El usuario abrió Codex desde S25 en `/workspace/projects/mestry-horus-smoke` y aportó su [respuesta de la tarea](validation/mestry-horus-s25-task-20261020T235104Z/codex-user-reported-result.json): creación del archivo con `estado=creado`, modificación a `estado=modificado`, ruta correcta, `aarch64`, contenido y SHA-256 esperados. El prompt exacto y su regla de detenerse si el destino ya existía se conservaron en el [plan](validation/mestry-horus-s25-task-20261020T235104Z/plan.json). La función oficial Horus aplica los flags ya aceptados `--sandbox danger-full-access --no-daemon`; no se añadieron flags para omitir aprobaciones. WSL no envió una tarea al modelo.

La [lectura independiente desde otra conexión S25](validation/mestry-horus-s25-task-20261020T235104Z/independent-s25-verification.json), a las **23:54:20 UTC**, mostró usuario `horus` y conexión `127.0.0.1 39052 127.0.0.1 8022`, distinta de la que mantiene Codex. El contenido y SHA-256 del archivo nuevo coincidieron exactamente con el plan; los hashes de `saludo.py`, `test_saludo.py` y `README.md` coincidieron con EXP06. Esta lectura no usa el modelo. `t01` observó el proceso **Codex 21261** como hijo de Node/zsh/Dropbear bajo UID Android **10350**; distingue ejecución en el S23 de la inferencia del modelo por el servicio de OpenAI.

Se solicitó después desconectar únicamente la conexión original en ConnectBot, reconectarla y ejecutar desde el mismo proyecto `codex resume --last`, precedido de lectura/hash del fixture. Según [OpenAI Docs](https://learn.chatgpt.com/docs/developer-commands#codex-resume), ese comando retoma la conversación guardada más reciente del directorio. El usuario confirmó **«funciona, reaparece la conversacion»**: [confirmación conservada](validation/mestry-horus-s25-task-20261020T235104Z/reconnect-user-confirmation.json). Se registra recuperación confirmada por el usuario, sin transcripción de la TUI ni identidad del hilo. Esta prueba se refiere a la conversación nueva del perfil SSH, no al historial del harness de la app; no demuestra por sí sola que sobreviva el proceso original.

El servidor entra como perfil **`horus`**, con `paths.home`. La app usa una identidad diferente para el harness Codex: **`harness_codex`**, UID invitado **61002**, `paths.harnessHome("codex")`. Ambos pueden compartir `/workspace`, pero eso no demuestra compartir credenciales, historial o terminal. El remoto incluye un launcher que instala Codex en el home del usuario SSH al primer uso si no está instalado allí. Comprobar primero el launcher sin ejecutarlo; no convertir una comprobación en una instalación inadvertida.

| Prueba posterior | Evidencia necesaria |
|---|---|
| Identidad y autenticación | Usuario/home/CODEX_HOME efectivos y `codex login status`, sin leer tokens. Si requiere login, intervención privada del usuario |
| Proyectos existentes | Listado acotado de `/workspace/projects/mestry-horus-smoke`; no acceder a proyectos personales |
| Historial | Comprobar si `codex resume` ofrece el hilo sintético de la app. Si no aparece, registrar la separación de perfiles; no copiar credenciales ni historiales para simular continuidad |
| Terminal de la app | Una conexión SSH abre otra PTY. La implementación revisada no ofrece un attach a la PTY nativa; `resume` recupera una conversación guardada y no equivale a adjuntarse a ese proceso vivo |
| Trabajo sintético | Desde S25, iniciar Codex con el `--sandbox danger-full-access` ya autorizado, crear un nuevo `S25_REMOTE_TEST.txt` en el proyecto sintético y modificar su contenido; no sobrescribir los tres archivos validados en EXP06 |
| Comprobación independiente | Desde otra sesión del S25, leer el archivo y calcular su SHA-256; registrar hora, comando y resultado |
| Desconexión | Registrar PID/hilo, desconectar S25 y reconectar: evaluar por separado archivos persistentes, conversación recuperable y proceso todavía vivo |

No prometer supervivencia de una TUI ligada a SSH. Si hace falta conservar una terminal interactiva independiente de la conexión, evaluar un único multiplexor dentro de Alpine después de medir el comportamiento básico; no instalarlo en este incremento. Apagar el remoto Horus termina su árbol de sesiones según el código; no usar ese interruptor como ensayo de simple desconexión del cliente. No ejecutar `horus tune`.

### Bloqueo de la interfaz a los 15 minutos

El usuario aclaró que el síntoma es **«Solo vuelve a pedir contraseña en Horus del S23»**, sin reportar un corte de ConnectBot. En el código del commit instalado, `sessionTimeout.ts` fija 15 minutos **en segundo plano**, no de inactividad del teclado. `App.tsx` muestra el login y revoca únicamente el permiso de desbloqueo; `SessionUnlockGrant.kt` replica el plazo en el servicio, sin terminar procesos. El controlador remoto mantiene su propio estado. Los ajustes de esta versión no exponen un selector para cambiar o desactivar ese plazo.

Ese bloqueo local no requiere mantener la pantalla encendida ni renovar la contraseña cada 15 minutos para trabajar por SSH desde el S25. Se conserva el comportamiento oficial. La revisión del código y el estado puntual del servicio no sustituyen una prueba medida de reposo prolongado o con el PC apagado. [Diagnóstico, fuentes y consulta de lectura](validation/mestry-horus-ui-lock-20261021T010002Z/result.json).

## Fase 4 — Protocolo con el PC físicamente apagado

1. Haber pasado fases 1–3, guardar instrucciones/huellas y tener el proyecto sintético disponible en el S25. Asegurar que la Wi-Fi y su acceso a Internet no los proporciona el PC. El modelo de Codex sigue usando el servicio de OpenAI; independencia del PC no significa ejecución del modelo sin Internet.
2. Desconectar USB/ADB de los teléfonos y cualquier sesión WSL. Mantener S23 alimentado por una fuente independiente si se necesita. El usuario apaga físicamente el PC; el agente no ejecuta esa acción.
3. **Con el PC apagado**, desde el S25 iniciar una conexión SSH nueva a Horus usando el ProxyJump verificado, abrir una sesión Codex nueva en el S23 y pedir otra modificación sintética con un marcador elegido en ese momento.
4. Abrir otra sesión desde el S25, leer el resultado y obtener SHA-256. Guardar hora y salida en el S25; después desconectar y reconectar para comprobar recuperación. Repetir tras apagar la pantalla del S23, anotando la duración real, sin reiniciarlo.
5. Solo declarar éxito si el usuario confirma el apagado físico y aporta los resultados obtenidos desde el S25 durante ese intervalo. Capturar nueva evidencia al volver a documentar; no atribuir una orden ejecutada desde WSL al S25.

## Evidencia y fuentes

Aplicación autorizada: [sondas de migración](validation/mestry-s25-port-migration-20261020T224339Z/commands.md). `r01/r02` preflight SSH/ADB; `r03` respaldo privado WSL; `r04` arranque temporal 8023; `r05` conexiones nuevas WSL por clave en ambos puertos; `r06` escuchas por ADB; `r07` clave S25 autenticada en el temporal. `r08a/r08b` revalidaron el estado al retomar; `r08` aplicó el corte y probó manualmente el hook; `r09` actualizó WSL y reconectó; `r10` comprobó 8022 libre. `r11` observó los marcadores finales del S25, `r12` verificó el cambio mínimo WSL, `r13` confirmó conexión nueva al principal, archivos, claves y temporizador terminado; `r14` reconfirmó por ADB un único daemon, 8022 libre y Horus apagado. [Resultado y límites](validation/mestry-s25-port-migration-20261020T224339Z/result.json).

La [salida aportada por el usuario](validation/mestry-s25-port-migration-20261020T224339Z/s25-final-user-confirmation.json) es la prueba desde el S25; no se atribuyen al teléfono comandos ejecutados desde WSL. El stderr de `r08` conserva una carrera al leer `/proc/13734/stat` cuando el listener temporal ya había terminado; el corte y el hook terminaron en 0 y las comprobaciones independientes posteriores verificaron el resultado. La advertencia parcial de netlink de ADB también se conserva. No se convierten esas observaciones en pruebas de reinicio, reversión real ni acceso a Horus.

Continuación tras el éxito manual de fase 1: [sondas y preparación de recuperación](validation/mestry-s25-port-plan-20261020T222743Z/commands.md). `q01/q02` revalidan SSH/ADB, claves y estado remoto apagado; `q03` comprueba parámetros sin escuchar; `q04` guarda respaldos y plantillas inactivos y confirma los hashes de los archivos activos. Las verificaciones de preparación no acreditan una migración de puerto ni acceso remoto Horus.

Comandos, tiempos, salidas y errores de este incremento: [registro de sondas](validation/mestry-s25-remote-20261020T215417Z/commands.md). `p01` conserva el timeout inicial; `p04` la verificación con la confianza anterior; `p05` el cambio de dirección WSL; `p06` la reconexión y política efectiva; `p07` los fragmentos y hashes de código revisados. La primera lectura filtrada de `sshd -T` en `p04` quedó vacía por las mayúsculas de OpenSSH; `p06` corrige el filtro y captura los campos. `ss` bajo Termux no pudo enumerar sockets; ADB sí mostró las escuchas, con una advertencia parcial de netlink. No se ocultaron estos límites.

`p08` conserva el segundo timeout de red; `p09` confirma por ADB el regreso a la dirección inicial; `p10` registra el alta de la clave pública; `p11` devuelve el alias a la red actual y prueba nuevamente la clave de WSL. La primera respuesta del usuario contenía una clave truncada: se solicitó la línea completa antes de cualquier alta.

- [Claves Ed25519 en ConnectBot](https://connectbot.org/guides/ssh-keys/), [alta del host](https://connectbot.org/guides/add-host/) y [reenvíos y límites de bind](https://connectbot.org/guides/port-forwarding/), consultados el 2026-10-20.
- [Horus CLI del commit instalado](https://github.com/scarif-labs/horus/blob/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369/cli/README.md), [provider de emparejamiento](https://github.com/scarif-labs/horus/blob/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369/android/app/src/main/java/com/scariflabs/horus/terminal/RemoteAccessProvider.kt) y [launcher SSH](https://github.com/scarif-labs/horus/blob/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369/android/app/src/main/java/com/scariflabs/horus/terminal/ProotSessionLauncher.kt).
- [Identidades separadas de los agentes](https://github.com/scarif-labs/horus/blob/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369/android/app/src/main/java/com/scariflabs/horus/terminal/TerminalHarnessUsers.kt) y [selección del home de SSH](https://github.com/scarif-labs/horus/blob/2f8f8a2faebd3d0fbd11dd83340bdcfbac437369/android/app/src/main/java/com/scariflabs/horus/terminal/TerminalSessionSpecFactory.kt).
- [Referencia oficial de `codex resume`](https://learn.chatgpt.com/docs/cli/reference#codex-resume), consultada el 2026-10-20. Sus funciones documentadas no acreditan por sí solas que el perfil SSH vea el historial del harness de la app; falta la prueba real.
