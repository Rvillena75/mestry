# MESTRY — acceso privado y VPN automática

Estado: **acceso privado, VPN automática y watchdog comprobados en sesión breve**,
2026-10-22. No se declara disponibilidad 24/7, recuperación tras reinicio ni
retención de una tarea real. La continuación está en
[`continuation-20261022/`](continuation-20261022/); las evidencias anteriores se
conservan y sus límites se indican abajo.

Identidades revalidadas: S23 `S23_SERIAL / SM-S918B`; S25
`S25_SERIAL / SM-S938B`. Todas las operaciones de interfaz usan
`tools/s23-remote-access/device_ui.py` con serial y modelo fijados.

## Configuración aplicada

- Tailscale oficial Play Store 1.104.2 instalado y autorizado por el usuario en
  ambos equipos. S23 `192.0.2.11`; S25 `192.0.2.10`. Sin exit node.
- S23: VPN siempre activa en Android, bloqueo sin VPN desactivado, batería
  exenta para Tailscale; Termux/Horus y sus wake locks conservados.
- S25: modo **Including**, dos aplicaciones seleccionadas: MESTRY y ConnectBot.
  La capacidad VPN comprobada solo incluye sus UIDs, el motor Tailscale y sus
  equivalentes SDK sandbox. Sin rango de todas las aplicaciones. VPN siempre
  activa deshabilitada para permitir el apagado solicitado.
- Usuario confirmó guardar grants S25→S23 solo TCP 8023 y desactivar caducidad
  de clave del S23 en su panel. Confirmación humana registrada; estas herramientas
  no inspeccionan el panel. Prueba TCP desde UID MESTRY: 8023 responde como OpenSSH;
  22/8022/8787/18787 no accesibles por la IP privada.
- ConnectBot: perfil `Mestry s23 8023` actualizado a IP privada; copia LAN
  `Mestry s23 8023 (copia)` conserva `192.0.2.15`. Clave existente conservada.
  Huella Ed25519 privada comparada con la conocida y aceptada: coincide.
  La conexión nueva volvió a pedir la contraseña local: el usuario la escribió
  privadamente en ConnectBot. Se comprobó después Termux `u0_a348` y
  `SSH_CONNECTION=192.0.2.10 36312 192.0.2.11 8023`.
  No era la sesión Horus 8022. No se capturaron campos de contraseña.
- APK **0.2.0-mestry-pilot8 / 10008**, mismo certificado y datos. Fuente
  reproducida desde archivo upstream, parche acumulativo y 68 huellas. Compilación
  Kotlin y ensamblado pasan. Copia privada en Downloads `MESTRY-Piloto-20261022-r8.apk`.
  OAuth, scope, emparejamiento, historial y bridge instalado permanecen iguales.

## VPN automática habilitada y observada

Ajustes → Conexión privada permite guardar la IP del S23 y activar VPN automática.
El servicio foreground solicita el cliente oficial Tailscale al abrir MESTRY;
considera la conexión válida tras recibir hello real del bridge. Cierra la VPN
30 segundos después de salir si no hay tareas, conserva tareas por sus IDs y
consulta snapshots autenticados en segundo plano. La acción Desconectar prevalece.
La conexión fallida inicial tiene un límite de 60 s; una pérdida posterior de
90 s. No genera turnos ni lee tokens en diagnósticos. La clave bridge se usa
exclusivamente dentro del UID de MESTRY.

IP `192.0.2.11` guardada e interruptor **habilitado desde Ajustes**.
El APK instalado sigue siendo `0.2.0-mestry-pilot8 / 10008`; no se recompiló ni
reinstaló en esta continuación. Se comprobó el hello real: el estado activo del
servicio lo confirma únicamente desde el manejador del mensaje de protocolo.
La pantalla con historial o una terminal anterior, por sí solas, no se usan
como prueba de conexión.

Con cero tareas activas, volver a los **10,764 s** conservó la VPN. En la salida
posterior seguía presente a los **30,744 s** y ya estaba ausente a los
**31,680 s**, con motivo `background`. El plazo nominal de 30 s se observa con
la granularidad del temporizador y de la muestra; no afirmar apagado exacto a
30,000 s. **Desconectar** dejó servicio y transporte VPN apagados en la primera
muestra, **0,163 s después de retornar la pulsación**, con motivo `manual`.

Los 19 casos puros históricos no sustituyen Doze ni una tarea real. La retención
real y Desconectar con una tarea activa siguen **NO ENSAYADOS**: no se inició
ningún turno para probarlos.

## Supervisión instalada dentro de Horus

`tools/s23-remote-access/horus_keepalive.py` comprueba la salud loopback cada 30 s.
Si el controlador existente confirma que no queda un bridge propio, solicita
su arranque. No mata un proceso vivo que pueda tener una tarea. Retrasa a 5 min
tras fallos repetidos; estado y PID son privados. Cinco casos de recuperación
pasan con funciones simuladas. Antes de instalar se corrigió un caso adicional:
un `status` con salida no cero ahora falla cerrado, sin solicitar arranque.
Cuatro regresiones de ese control pasan.

Instalado mediante comandos de código público en el perfil SSH existente
**Mestry horus**, después de verificar `/home/horus` y `aarch64`. No hubo sesión
SSH desde WSL ni acceso directo suyo al sistema de archivos privado de Horus.
Fuente instalada:
`/home/horus/.local/lib/mestry-keepalive/horus_keepalive.py`, SHA-256
`27ff1f5da79211d36b5c28a8a8acc8186c2bb0e123e4efa6038ff4c4e651247a`.
El instalador vigente es
[`continuation-20261022/INSTALL_KEEPALIVE_IN_HORUS.sh`](continuation-20261022/INSTALL_KEEPALIVE_IN_HORUS.sh);
el preparado anterior se conserva como evidencia y no debe volver a ejecutarse.

Se observaron worker habilitado, salud loopback correcta, estado `healthy` sin
fallos y permisos 0700/0600. Comprobación periódica observada a
`2026-10-22T07:48:30Z`; el registro del proceso del bridge mantuvo su huella
`1f5ef55466f89256`. No se detuvo ni mató el bridge. No se provocó una caída real
ni se ensayó la muerte del UID Android o un reinicio.

## Resultados de esta continuación

| Comprobación | Resultado observado | Evidencia |
| --- | --- | --- |
| SSH privado nuevo por Wi-Fi | Clave autentica en Termux, S25→S23:8023 | [SSH](continuation-20261022/ssh-private-wifi.json) |
| Reenvío existente | Habilitado, 18787→127.0.0.1:8787; solo loopback, health correcto y autenticación negativa correcta | [Túnel](continuation-20261022/loopback-automatic-wifi.json) |
| Hello real con VPN automática | Servicio activo después del protocolo, sin turno nuevo | [Hello](continuation-20261022/hello-before-disconnect.json) |
| Regreso y plazo de salida | PASS con los intervalos indicados arriba, cero tareas | [Regreso](continuation-20261022/vpn-return-measured.json), [salida](continuation-20261022/vpn-background-measured.json) |
| Desconectar | Servicio y VPN apagados, motivo manual | [Desconexión](continuation-20261022/vpn-disconnect-measured.json) |
| Red celular | CELLULAR validada como red predeterminada; Wi-Fi apagada y sin agentes WIFI antes y después | [Celular](continuation-20261022/cellular-ui-validation.json) |
| SSH, túnel y hello por celular | Sesión SSH nueva `192.0.2.10 39410 192.0.2.11 8023`; banner 8023 y health del túnel correctos; 22/8022/8787/18787 privados no respondieron | [Capas de conexión](continuation-20261022/cellular-ui-validation.json) |
| Historial fresco por celular | Cinco respuestas `session.sync` aplicadas dentro de la ventana sin Wi-Fi; 27 elementos y 35 entradas combinadas, no entradas nuevas | [Lectura fresca](continuation-20261022/cellular-fresh-sync-recovered.json) |
| Watchdog vivo | Fuente, worker, salud y permisos verificados; bridge conservado | [Watchdog](continuation-20261022/keepalive-running-verified.json) |
| Estado final | VPN automática habilitada, IP guardada, S25 sin always-on/lockdown, Wi-Fi restaurada, S23 con servicios/wake locks activos | [App](continuation-20261022/final-app-settings.json), [Android](continuation-20261022/final-readiness.json) |

La ventana celular observada fue de `07:40:10.505Z` a `07:41:13.048Z`.
El primer evento de reactivación Wi-Fi fue nuestra restauración en Ajustes.
Se habilitó temporalmente solo la etiqueta de diagnóstico `CodexRemoteSync` para
extraer IDs y conteos de respuestas autenticadas; se restauró a su valor vacío.
No se guardaron mensajes, tokens, credenciales ni logcat bruto.

### Correcciones de instrumentación y ensayos inconclusos

- `private-network-mobile.json` histórico **no acredita ruta celular**: no excluía
  Wi-Fi activa. Se conserva sin editar. El primer ensayo nuevo con `svc wifi`
  también fue inconcluso: Android UID 1000 la reactivó. No se atribuye causa
  concreta a esa reactivación. Apagarla desde Ajustes permitió el ensayo estable.
- El recolector celular inicial solo reconocía `session.content`; por eso
  `cellular-ui-validation.json` conserva `PARTIAL`. El sidecar
  `cellular-fresh-sync-recovered.json` recupera del mismo ensayo las respuestas
  reales `session.sync` dentro de los eventos Wi-Fi de apagado/restauración.
  Los conteos describen historial combinado, no el delta del servidor.
- El primer detector confundió la capacidad `NOT_VPN` de redes físicas con un
  transporte VPN y usó muestreo lento. Su `vpn-background-deadline.json` no sirve
  para juzgar el apagado. Ver [corrección](continuation-20261022/measurement-correction.json)
  y la repetición `vpn-background-measured.json`.
- La primera lectura del watchdog se hizo antes de terminar el comando remoto
  y quedó `NOT_CONFIRMED`. La verificación posterior confirma el estado real.
- [Ocho regresiones](continuation-20261022/regression-tests.log) pasan: cuatro
  del control de propiedad del bridge y cuatro de atribución de red/historial.

## Trabajo pendiente, sin PASS

1. Retención de una tarea real al salir y su finalización; prevalencia de
   Desconectar durante esa tarea. Requiere un ensayo posterior compatible con
   la prohibición actual de iniciar turnos para probar.
2. Cargador de pared y PC físicamente apagado; reposo prolongado y 24 horas.
   Ambos equipos siguen conectados por USB. No extrapolar la sesión breve.
3. Recuperación real después de caída del bridge, muerte del UID o reinicio.
   No se autorizó reiniciar teléfonos ni se provocaron esas caídas.

## Recuperación y límites

La VPN S25 necesita el transporte SSH de ConnectBot. Una clave cifrada puede
solicitar desbloqueo local al arrancar ConnectBot; la app no conoce su contraseña.
No se promete reconexión SSH totalmente silenciosa sin esa sesión disponible.
En los ensayos, apagar la VPN dejó terminales de ConnectBot cerradas. Reabrir
MESTRY enciende la VPN, pero puede requerir reconectar el perfil privado en
ConnectBot. Seleccionar una terminal anterior no demuestra SSH nuevo; usar
«Volver a conectar» o cerrar/confirmar y abrir otra vez el perfil conservado.
No regenerar claves ni crear perfiles alternativos para resolverlo.

Horus 1.0.4 no declara BOOT_COMPLETED. El hook Termux:Boot inicia SSH y wake lock,
pero la recuperación completa tras reinicio Android no está ensayada ni garantizada.
La supervisión dentro de Horus no sustituye a su servicio Android ni sobrevive
por sí sola a una parada total del UID. 24/7 es un objetivo operativo pendiente
con alimentación estable; ahora ambos teléfonos siguen por USB al PC.

Para volver a LAN: apagar VPN automática, desconectar el perfil privado, usar la
copia LAN; solo un reenvío local 18787 a la vez. No borrar perfiles, claves ni datos.
La supervisión se detiene con su acción `stop`, sin parar el bridge. SuperDisplay
se conserva detenido como pidió el usuario; su recuperación original ya fue
restaurada en la entrega anterior. Su estado Windows actual se comprobó sin
mutarlo: [Stopped](continuation-20261022/superdisplay-observed-stopped.json).
Sin router forwarding, root, cliente OAuth nuevo ni scopes adicionales.
Puertos 8022/8023/8787/18787, claves, callback y scope `drive.file` conservados;
cero turnos de Codex y cero publicaciones durante esta continuación.

El preflight de servicios es una fotografía de solo lectura: sus campos de
mutación falsos describen lo que hace ese recolector, no una prueba negativa
de la configuración de red aplicada después del diagnóstico inicial.
