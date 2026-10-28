# Continuación del piloto MESTRY S25

Estado al entregar el 2026-10-21: **tarea real desde la app PASS**. El usuario pidió
un prompt para continuar en otro hilo. No se iniciaron más operaciones después de
esa solicitud; no asumir que los dispositivos siguen conectados sin comprobarlo.

## Objetivo y alcance elegidos

Continuar la app Android del S25 para controlar Codex en Horus/S23, conservando la
publicación autónoma a Drive ya funcional. Para esta prueba el usuario pidió
«s25 conectado, ponle cualquier cosa para probar la app»: se usa únicamente
`/workspace/projects/mestry-horus-smoke`. No se ha elegido un proyecto real ni
ampliado el publicador a otros archivos. No reiniciar el trabajo desde cero.

Workspace `/home/developer/proyectos/mestry`, sin repositorio Git. Consultar los
AGENTS.md aplicables antes de editar las fuentes upstream. No usar subagentes
sin solicitud explícita. No publicar, hacer push ni crear repositorios.

## Autorizaciones que persisten

- Instalar y probar la app personal en el S25, usar la cuenta ChatGPT existente
  de Codex y tareas sintéticas. No se necesita una API key nueva.
- Puertos: pruebas/compilación temporales solo loopback del PC; bridge Horus
  `127.0.0.1:8787`; reenvío S25 `127.0.0.1:18787 → S23 127.0.0.1:8787`.
  Transferencia bootstrap temporal cerrada; no volver a abrirla sin necesidad.
  Conservar Termux `8023`, Horus SSH `127.0.0.1:8022` y callback OAuth `53682`
  cerrado. Cambios a otros puertos requieren autorización expresa.
- Mantener el `danger-full-access` de Horus previamente aceptado y
  `on-request`; no añadir `never` ni bypasses. La ACL del bridge no es aislamiento
  del sistema operativo. Sin root, reinicios ni cambios de seguridad de Android.
- No copiar claves privadas, OAuth ni login Codex. No imprimir secretos.
  **WSL tiene clave en Termux, no en Horus**: no añadirla ni saltar ese límite.
  Horus se opera mediante la sesión ConnectBot ya autenticada del S25.

## Dispositivos y acceso actual

- S25: `SM-S938B`, SDK 36, arm64-v8a. Usuario aprobó depuración USB; hubo una
  desconexión, reconectó y respondió «conectado». Último transport_id ADB `1`;
  redescubrir y verificar modelo antes de cada mutación, sin imprimir seriales.
- ADB Windows: `/mnt/c/Users/developer/AppData/Local/Android/Sdk/platform-tools/adb.exe`.
  La sonda ADB escribe screenshots de 1440×3120; el visor los reduce.
- ConnectBot `org.connectbot`, versión v1.11.1. Launcher
  `org.connectbot/.ui.MainActivity` puede volver a la consola actual, no siempre
  al listado. Pulsar la flecha superior para volver al listado antes de elegir.
- Perfiles: **Mestry horus** (SSH horus@127.0.0.1:8022 vía ProxyJump Termux8023),
  **Mestry s23 8023** (u0_a348@192.0.2.15:8023), y antiguo 8022 conservado.
  El perfil Termux8023 mantiene el reenvío **MESTRY App**, Local, 18787 a
  127.0.0.1:8787. Mantener esa conexión para la app.
- Horus: Alpine aarch64, home `/home/horus`; Codex privado
  `~/.local/bin/codex`, versión 0.163.0, autenticado ChatGPT. El launcher global
  es un instalador lazy: no usarlo ni reinstalar Codex.
- Controlador instalado: `~/.local/bin/mestry-bridge start|status|stop|pair`.
  Bridge arrancado y separado de la consola SSH. Token privado ya emparejado;
  **no generar otro ni repetir pair**. No es un token Google/OpenAI.
  Estado: `~/.local/state/mestry-s25-client/`. No leer `bridge-token`.
- App instalada: `com.haochen.codexremote.mestrypilot`, activity
  `com.haochen.codexremote.MainActivity`, URL `ws://127.0.0.1:18787/`.
  Clave guardada cifrada con Android Keystore. En el emparejamiento se vio un
  aviso de sincronización del portapapeles de Samsung: no afirmar que el valor
  nunca se sincronizó. El agente no leyó ni registró el valor; campo oculto y
  portapapeles sensible con borrado a los 120 segundos.

## Evidencia real completada

- APK instalado/abierto y bundle Horus instalado desde la consola del S25.
  Transferencia temporal cerrada: `temporary-transfer.json`.
- S23: `s23-bridge-network-probe.json` PASS. Identidad health correcta, HTTP
  sin clave rechazado y bind loopback verificado.
- S25: `s25-loopback-and-auth-probe.json` PASS. Loopback IPv4 ocupado;
  once direcciones no loopback libres; wildcard IPv6 libre; health correcto;
  HTTP sin clave y WS con clave falsa devuelven 401. Android negó netlink a ss;
  no se usó esa ausencia como prueba. `LoopbackProbe.java` usa bind sin listen,
  no instala otra app ni lee secretos; DEX temporal eliminado al terminar.
- Sesión nueva de app: **01a15dae-7f34-7a22-926e-594a53f899cd**,
  modelo `gpt-6.1-sol`, esfuerzo `low`, proyecto smoke. Información de sesión
  real: `on-request` y `dangerFullAccess`. Captura `app-sample-session-info.png`.
- Tarea de app completada: creó solo
  **S25_APP_TEST_20261021T085207Z.txt**, con bytes:

  ```text
  MESTRY_S25_APP_OK
  estado=creado-desde-app
  ```

  Ambas líneas terminadas en salto de línea. SHA-256:
  `26a5c89377b286ad37c89ac76b6a9e30ab4b7d319f9fd2d616086e03e8ae30ec`.
  Baseline de seis archivos tomado antes; verificación independiente en la
  consola SSH Horus: **PASS, CHANGED=0, ADDED=1**. Ver
  `independent-readback.json` y `horus-app-independent-readback.png`.
  El verificador solo leyó el proyecto; no creó el archivo de prueba.
- Baseline privado en Horus:
  `~/.local/state/mestry-s25-client/app-task-baseline-20261021.json`.
  Scripts públicos revisables: `PUBLIC_APP_BASELINE.py`, `PUBLIC_APP_VERIFY.py`
  en este directorio. Contienen hashes/rutas de prueba, sin credenciales.
- La conversación anterior **01a15bb9-aba1-7a82-ae71-6879625e8cae** se conserva;
  el usuario había enviado «hola» y «quien eres?» y recibió respuesta en la app.

## Interrupción y pendientes inmediatos

1. La interrupción se activa **manteniendo pulsado Enviar**, no tocando la
   pequeña insignia cuadrada. El primer ensayo de espera de 30s terminó porque
   se tocó esa insignia; no registrarlo como interrupción PASS.
2. Segundo ensayo: espera de 30s sin cambios de archivos, mantener pulsado Enviar
   a los cuatro segundos. La app mostró solicitud de interrupción y volvió al
   compositor inactivo; capturas `app-interrupt-retry-running.png` y
   `app-interrupt-retry-stopped.png`. **Falta confirmar `interrupted` mediante una
   lectura fresca del hilo en app-server**; no basta el toast. No se han iniciado
   más turnos después. Reutilizar inicialización stdio de `horus_preflight.py`
   y `thread/read` para este ID, sin inferencia ni imprimir conversaciones o
   credenciales; terminar únicamente el proceso de diagnóstico propio.
3. Ensayar cerrar/reabrir o reconectar **la app del piloto**, manteniendo
   ConnectBot/Horus. Verificar el mismo ID e historial con lectura fresca del
   servidor; distinguirlo de caché Android. No apagar ni reiniciar teléfonos.
4. Interfaz: nuevo hilo muestra título literal **null** y quedan controles en
   chino. Revisar el tratamiento de JSON null y completar los textos necesarios
   sin refactor general. Si se cambian fuentes, mantener parche/pins
   reproducibles, compilar, instalar en S25 y revisar pantalla real.
5. Registrar resultados y límites. PC físicamente apagado y reposo prolongado
   siguen sin probarse. El bloqueo de la pantalla Horus a 15min no prueba corte
   SSH y no se debe desactivar como solución. No hay autostart del bridge.

## Fuentes, artefactos y compilación

Guía: `/home/developer/proyectos/mestry/tools/s25-codex-client/README.md`.
Preparación congelada: `docs/validation/mestry-s25-android-client-20261021T063514Z/`;
su estado «no instalado» es histórico: no sobrescribir sus hashes.

Fuente modificada:
`/home/developer/.cache/mestry/s25-android-client-20261021T063514Z/source/codex-remote-control-538d65f67e34907789237fc71f56e8ca95d9f3cb`.
Base GPL3 `chenhaoc/codex-remote-control`, commit
`538d65f67e34907789237fc71f56e8ca95d9f3cb`. Parche y pins en
`tools/s25-codex-client/mestry-pilot1.patch` y `source-pins.json`.
No instalar APK upstream sin los cambios del piloto.

APK actual: `/mnt/c/Users/developer/Downloads/MESTRY-Piloto-20261021.apk`,
SHA `ff6f8e30cd2176b93cbf0427bf39cfb5d18af53865b29f2adc6318cde14411dd`;
debug personal, versionCode10001, versionName0.2.0-mestry-pilot1.
Bundle instalado SHA `ce89f574b85d9be9712d32e38f7d392ace12b745f426ae61f9b76174c0d89a55`,
release Horus `~/.local/lib/mestry-s25-pilot/releases/1c41ac5e55d840561920/`.
Bundle incluye solo backend Codex real; excluye mock y launcher legacy.

Build Windows existente:
`C:\Users\developer\AppData\Local\mestry-build\s25-pilot-20261021T063514Z\BUILD_PRIVATE_PILOT.ps1`.
Usa JBR21 de Android Studio, SDK Windows, build tools36.0.0, Gradle8.13,
compile/target36, min26. SDK35 está incompleto y se conserva; no repararlo.
Usar invocación PowerShell normal, sin bypass de políticas. Sin Java Linux.
Los cambios anteriores pasaron 51 tests Node +3 política +3 helpers Python;
son fixtures de PC, separados de esta prueba real. No repetir toda la batería
sin cambios; aplicar las comprobaciones necesarias si se modifica código.

Punteros temporales disponibles en WSL: `/tmp/mestry-s25-live-current`,
`/tmp/mestry-s25-transport-current`, `/tmp/mestry-s25-android-source-current`.
Pueden faltar en otra sesión; los paths completos anteriores son la referencia.

## Drive preservado

OAuth en producción, mismo cliente de escritorio y solo `drive.file`; refresh y
publicaciones ya verificados. Secretos solo en Termux UID10348, separados de
Codex/Horus UID10350. No reautorizar, ampliar scopes ni mover tokens ahora.
`~/.local/bin/mestry-publish` en Horus usa su clave limitada propia; el piloto
publica únicamente `S23_PUBLISH_TEST.md`, con versiones privadas verificadas.
No ampliar ese allowlist para el archivo nuevo de la app sin elegir el alcance.
Ver `docs/DRIVE_S25_HANDOFF.md` y la evidencia OAuth producción anterior.
Ensayo de renovación después de siete días pendiente desde
2026-10-29T06:08Z; no existe un trabajo programado ni se prometen tokens perpetuos.
