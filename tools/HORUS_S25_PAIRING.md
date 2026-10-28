# Emparejamiento S25 con Horus

El usuario autorizó continuar con Horus después de completar la migración de Termux a 8023. El acceso remoto se emparejó el 2026-10-20 a las 23:27 UTC mediante el provider oficial de Horus 1.0.4. Se añadió únicamente la clave pública existente `mestry-s25`, huella `SHA256:CONFIGURE_LOCAL_FINGERPRINT`; no se generó ni transfirió una identidad privada. [Evidencia](../docs/validation/mestry-horus-s25-20261020T232332Z/commands.md).

## Comando local

```sh
python3 -B /home/developer/proyectos/mestry/tools/horus_pair_s25.py
```

Ejecutar en una terminal WSL interactiva. El helper identifica un único SM-S918B autorizado por ADB, comprueba Termux 8023 y su confianza estricta, obtiene solo la clave pública S25 ya autorizada y valida su formato y huella. Consulta el provider antes de pedir la contraseña local de Horus. Si la clave ya está autorizada, no vuelve a pedirla ni repite el emparejamiento. `--check` ejecuta únicamente esas lecturas.

La contraseña se introduce con `getpass`, sin eco. Viaja en memoria por stdin de ADB, sin valores en argumentos de WSL, historial, variables de entorno, archivos temporales o registros del helper. El provider oficial exige un argumento base64: el proceso Android `content` lo recibe de forma transitoria; **base64 no cifra la contraseña**. No ejecutar con herramientas externas que registren stdin o memoria. El helper registra solo campos permitidos de las respuestas y omite errores sin filtrar. Un fallo o timeout no provoca reintentos de contraseña; comprobar el estado antes de repetir.

El provider `pair` comprueba la contraseña, añade la clave y activa el remoto. Puede instalar las dependencias SSH mínimas que falten dentro de Alpine. La autorización de una clave no acredita que el servidor ya esté listo ni que el S25 haya conectado: comprobar ambos por separado.

## Estado comprobado

- Emparejamiento: [resultado del helper](../docs/validation/mestry-horus-pair-20261020T232711794480Z/result.json), `PAIRED_VERIFIED`, respuesta `ok` con la huella esperada y autorización posterior `true`.
- Servicio: `s06` confirma `enabled=true`, `state=running`, una clave y `authorized=true` para el S25. ADB muestra Dropbear con UID Android 10350, en `127.0.0.1:8022`; Termux conserva 8023 con sus dos claves.
- Identidad de servidor Horus: `s07` obtuvo la clave pública por loopback dentro de la conexión Termux ya autenticada. Huella **`SHA256:CONFIGURE_LOCAL_FINGERPRINT`**. La huella Termux se conserva por separado.
- Conexión desde el S25: **PASS** con el perfil ProxyJump. La [salida del usuario](../docs/validation/mestry-horus-s25-20261020T232332Z/s25-horus-user-confirmation.json) muestra `horus`, UID 1000, `/home/horus`, Alpine 3.24.0 ARM64 y conexión loopback con puerto origen 50860. El registro del servidor `s08` confirma esa misma conexión con la huella S25 a las 20:29:20 del teléfono. Se distingue esta evidencia del emparejamiento y de las consultas WSL.

## Perfil ConnectBot verificado

Conservar el perfil Termux ya verificado en 8023. Crear otro:

| Campo | Valor |
|---|---|
| Nombre | MESTRY Horus |
| Host | `127.0.0.1` |
| Usuario | `horus` |
| Puerto | `8022` |
| Clave | `mestry-s25` |
| ProxyJump | El perfil Termux que conecta al S23 en 8023 |
| Reenvío de agente | Desactivado |

El código oficial [SSH.kt](https://github.com/connectbot/connectbot/blob/main/app/src/main/java/org/connectbot/transport/SSH.kt), consultado el 2026-10-20, abre `direct-tcpip` desde el salto al hostname/puerto destino y verifica ambos servidores con sus perfiles. La prueba real del S25 pasó por esa ruta. No se creó un puerto local 18022, un `adb forward` ni se importó una clave privada a Termux.

Tras comparar la huella **Horus**, ejecutar desde el S25:

```sh
echo MESTRY_S25_HORUS_OK
whoami
id
echo "$HOME"
echo "$SSH_CONNECTION"
uname -m
cat /etc/alpine-release
```

El diagnóstico inicial del S25 confirmó el stub oficial y ausencia de instalación propia. Después, el usuario ejecutó `cd /workspace/projects/mestry-horus-smoke && codex --version && codex login status`: el [instalador terminó](../docs/validation/mestry-horus-codex-auth-20261020T234450Z/installation-user-output.json) y mostró **codex-cli 0.163.0**, **Not logged in**. Se solicitó `codex login --device-auth` con acceso privado en el navegador del S25 y comprobación posterior de `codex login status`; el usuario confirmó después «ya estoy logged in». La tarea sintética desde el Codex del S25 creó y modificó `S25_REMOTE_TEST.txt`; otra conexión S25 verificó su contenido y SHA-256, además de los hashes intactos de los tres fixtures originales. [Verificación independiente](../docs/validation/mestry-horus-s25-task-20261020T235104Z/independent-s25-verification.json). No se copiaron credenciales ni historial del harness de la app. Reconexión/recuperación de conversación en prueba; persistencia de procesos y PC apagado todavía no acreditados.

## Revocación

En Horus, revocar únicamente la clave con etiqueta `mestry-s25` en Remote Access. Apagar el remoto si se desea detener ese servicio. No restaurar respaldos completos de autorizaciones ni ejecutar la reversión de puertos de Termux mientras Horus ocupa 8022. La revocación en Horus no revoca la clave del perfil Termux.

## Verificaciones del helper

`python3 -B -m unittest discover -s tools -p test_horus_pair_s25.py -v` pasó **13 pruebas offline**: transporte de contraseña por stdin, omisión de errores sin filtrar, rechazo de clave/versión/dispositivo ambiguos, ausencia de prompt en modo lectura y un solo intento fallido. No prueban una contraseña real ni sustituyen la evidencia del emparejamiento. `s03` validó el preflight real sin mutar; `s05` validó el mismo transporte por stdin con una consulta `status`, sin contraseña.
