# Puertos del piloto Android MESTRY

Estado: **autorizado por el usuario el 2026-10-21**, sin nuevos puertos en el
incremento de Drive/interfaz. Bridge `127.0.0.1:8787` y reenvío
`127.0.0.1:18787` conservados. La sonda S25 del 2026-10-22 encontró diez direcciones ajenas
a loopback libres, wildcard IPv6 libre y rechazo HTTP/WS con clave ausente o
inválida. No se utiliza la denegación Android de `ss` como prueba de bind.
[Sonda real de la continuación](../../docs/validation/mestry-s25-drive-ui-20261021T200418Z/resume-loopback-initial.json).
[Entrega y evidencias actuales](../../docs/validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md).

| Equipo | Escucha propuesta | Uso y duración |
| --- | --- | --- |
| PC, WSL/Windows | Loopback, puertos efímeros | Pruebas HTTP/WebSocket con fixtures y comunicación local de Gradle/Kotlin durante la compilación; cerrar al terminar. Sin modelos ni credenciales reales en tests. |
| S23, perfil privado Horus | `127.0.0.1:8787` | Bridge Node → Codex app-server por stdio. Solo el proyecto `/workspace/projects/mestry-horus-smoke`; token propio, autenticación por cabecera incluso en loopback. Detener el proceso cierra la escucha. |
| S25, cliente SSH | `127.0.0.1:18787` → S23 `127.0.0.1:8787` | Reenvío local sobre la conexión Termux `8023` ya emparejada; la app conecta a `ws://127.0.0.1:18787/`. Verificar el bind real antes de aceptar el túnel. |

Se conservan Termux `8023`, Horus `127.0.0.1:8022`, sus claves y el publicador de
Drive. Sin túneles públicos, exposición LAN, clientes OAuth nuevos ni más scopes.
El callback OAuth `127.0.0.1:53682` se reutilizó con aprobación previa para
Picker, máximo 180 segundos; debe quedar cerrado tras cada intento.

Antes de instalar el bridge, el mismo `8787` del S23 puede usarse durante un
máximo de diez minutos como reenvío SSH inverso hacia un servidor de artefactos
en loopback del PC. Sirve únicamente el bundle de código sin credenciales; el
comando en Horus verifica su SHA-256 antes de extraerlo. Este reenvío usa la clave
WSL ya autorizada en Termux y se cierra antes de emparejar/arrancar el bridge de
Horus. Es una dependencia de instalación, no de funcionamiento diario. No se
añade una clave WSL al home privado de Horus ni se amplía el broker de Drive.

La versión personal tiene applicationId `com.haochen.codexremote.mestrypilot`;
no sustituye otras apps. El token de emparejamiento se genera en la app, se guarda
con Android Keystore/AES-GCM y se introduce privadamente con `getpass` en Horus.
No se imprime ni se transporta en una URL; no es un token OAuth de Google/Codex.
Los respaldos de configuración que exportaba upstream están desactivados.

El modo de Horus `danger-full-access` ya aceptado sigue siendo explícito; se fija
`never` por petición expresa posterior del usuario. Se verifica la política
real antes de aceptar un turno. La ACL de rutas del bridge **no es un sandbox
del sistema operativo**: las herramientas de Codex conservan el UID de Horus.
El piloto no habilita cargas de imágenes ni descargas HTTP. La lectura de texto
por la app se limita al proyecto, con verificación de ruta real y symlinks.

## Comprobación y reversión

1. Tras aprobación, ejecutar pruebas de regresión con backends sintéticos en PC;
   compilar y verificar APK/manifiesto/firmante, sin instalar en ningún teléfono.
2. Instalar el APK solo en el S25 identificado y preparar el bridge en Horus.
   WSL no recibe una clave SSH de Horus ni copia su login de Codex.
3. Comprobar en ambos teléfonos que los nuevos puertos son exclusivamente
   loopback. Si ConnectBot no puede garantizarlo, detener el intento y no sustituir
   el transporte por una escucha LAN. Evaluar otra implementación SSH local.
4. Probar primero autenticación negativa y lectura de proyectos/historial sin
   inferencia. Luego una tarea sintética, interrupción y reconexión.
5. Para revertir, detener el bridge y quitar/desactivar el reenvío local. La app se
   puede desinstalar por su ID independiente; `8022/8023` y Drive siguen disponibles.
   No habilitar arranque automático antes de verificar el ciclo de vida.

Los ensayos de PC apagado y reposo necesitan confirmación física del usuario;
la aceptación no se obtiene dejando de usar WSL mientras el PC sigue encendido.
