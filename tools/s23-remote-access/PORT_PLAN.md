# S23 disponible por Internet — propuesta concreta

Estado: **autorizado por el usuario el 2026-10-22**, con condiciones adicionales
para el S25. No sustituye las autorizaciones existentes de 8022/8023/8787/18787.

El usuario confirmó conservar ConnectBot como transporte y el apagado automático
30 segundos después de salir de MESTRY. Si hay una tarea activa, mantener la VPN
hasta que termine; Desconectar la cierra expresamente. En el S25 incluir solo
MESTRY y ConnectBot mediante la lista de aplicaciones de Tailscale; resto fuera.
La VPN del S25 no será «siempre activa». Se usará la confirmación/estado real del
bridge, no la presencia de historial en caché, para acreditar la conexión.

## Recorrido propuesto

```text
S25 (Wi-Fi distinta o datos móviles)
  → Tailscale privado
  → IP Tailscale del S23 :8023, SSH Termux con la clave S25 existente
  → reenvío SSH existente a 127.0.0.1:8787 en Horus
  → MESTRY Piloto por 127.0.0.1:18787 en el S25
```

La consola Horus conserva su destino `127.0.0.1:8022` y ProxyJump por Termux.
El PC no forma parte del recorrido. La IP Tailscale se obtiene después del login;
no se inventa ni se utiliza una IP de ejemplo como si fuera real.

## Puertos y alcance de la aprobación

| Elemento | Cambio propuesto |
| --- | --- |
| Tailscale Android en S23 y S25 | Instalar cliente oficial y activar VPN privada con la misma cuenta. Su transporte UDP usa el puerto que elija el cliente Android; no se fija a ciegas 41641. Comunicaciones salientes con coordinación/relays por HTTPS y STUN. |
| Termux TCP 8023 existente | También accesible desde la red privada Tailscale, restringida al S25. Se conservan número, clave Ed25519, confianza estricta y acceso LAN actual. |
| Horus SSH TCP 8022 | Conserva exclusivamente loopback del S23. |
| Bridge TCP 8787 | Conserva exclusivamente loopback del S23 y su autenticación. |
| Reenvío TCP 18787 | Conserva exclusivamente loopback del S25, sobre SSH 8023. |
| Router/Internet público | Sin redirecciones de puertos, DMZ, UPnP configurado manualmente, Funnel, Serve ni publicación HTTP/SSH. |

La app VPN puede crear sockets propios para su transporte y servicios auxiliares;
no equivale a afirmar que no habrá sockets nuevos. Se acepta su gestión de
puertos de transporte al aprobar este plan. Se verificará su configuración real,
sin ampliar a servicios de aplicación adicionales. No activar exit nodes,
subnet routes, Taildrop ni opciones de compartir servicios como parte del piloto.

La regla de acceso objetivo es **IP del S25 → IP del S23, solo TCP 8023**.
Antes de guardar una política se revisará si la cuenta ya tiene una red privada
con otros dispositivos. Una regla estrecha añadida a una regla global permisiva
no restringe el acceso; no reemplazar a ciegas la política de una red existente.
No activar el producto «Tailscale SSH» ni cambiar al puerto 22: aquí se conserva
OpenSSH de Termux con su autenticación actual.

## Configuración Android y disponibilidad

En S23: cargador de pared, protección de carga existente, pantalla apagable,
Termux/Horus/Tailscale sin restricción de batería y Tailscale como VPN siempre
activa. En S25: conservar ConnectBot y su reenvío; permitir actividad de fondo de
ConnectBot/Tailscale para que el túnel no dependa de mantenerlos visibles. Usar
IP Tailscale en el perfil de salto; la URL de MESTRY no cambia. Conservar el
perfil LAN hasta verificar el nuevo. No activar bloqueo de conexiones sin VPN.

Se propone desactivar la caducidad del dispositivo servidor S23 en Tailscale
para evitar una desconexión por reautenticación programada; sigue revocable
desde la consola. El login de Tailscale es independiente de Google Drive/Codex.
El usuario inicia sesión privadamente; no se solicitan contraseñas, auth keys ni
tokens por chat. No cambiar OAuth de Drive, scopes, certificados ni claves SSH.

El hook Termux:Boot actual ya inicia SSH 8023 y solicita wake lock. Horus 1.0.4
tiene servicio foreground/START_STICKY y wake lock, pero **no declara receptor
de arranque**. El bridge actual se inicia manualmente y no tiene supervisor de
reinicio. No se promete recuperación autónoma completa tras un reinicio Android.
Preparar la recuperación y, si hace falta, supervisión dentro del UID Horus sin
copiar secretos a Termux ni saltar el provider privado. Con la instalación actual
puede hacer falta desbloquear/abrir Horus y arrancar el bridge después de reiniciar.
No root, cambios de bootloader ni reinicio del S23 en esta fase.

## Aceptación y reversión

1. Autorizar este plan; instalar por Play Store o distribución oficial verificada.
   Login y consentimiento VPN en cada equipo por el usuario. Confirmar que no se
   sustituye una VPN que esté usando y que ambos pertenecen a su misma red privada.
2. Restringir TCP 8023 a S25; verificar ambos equipos y excluir configuraciones
   de exposición pública o de acceso a toda la LAN. Guardar la política anterior
   privadamente antes de modificarla. Conservar huellas SSH conocidas.
3. Probar otra conexión al S23 por su IP Tailscale, reenvío y MESTRY con historial
   real. Comprobar autenticación negativa y bind loopback del bridge/reenvío.
4. En S25, con autorización para interrumpir esa Wi-Fi, usar datos móviles; S23
   queda en Wi-Fi. Confirmar nueva conexión y lectura real, no solo pantalla en
   caché. Si no tiene SIM/datos, usar otra Wi-Fi realmente ajena.
5. Ensayo con PC físicamente apagado, S23 en cargador y pantalla apagada. Después,
   observación de reposo y 24 horas. No declarar PASS antes de medir esos períodos.
   No iniciar tareas al modelo ni publicar documentos solo para probar red.
6. Reversión: reconectar el perfil LAN conservado, desconectar VPN y restaurar
   únicamente la política/ajustes modificados. No borrar datos, claves ni apps
   existentes. Un ensayo de reinicio/Boot posterior requiere su autorización.

## Fuentes oficiales consultadas

- [Instalación Android](https://tailscale.com/docs/install/android).
- [SSH habitual sobre Tailscale](https://tailscale.com/docs/reference/ssh-over-tailscale).
- [Conectividad y puertos de transporte](https://tailscale.com/docs/reference/faq/firewall-ports).
- [Grants: permisos acumulativos y sintaxis](https://tailscale.com/docs/reference/syntax/grants).
- [Caducidad por dispositivo](https://tailscale.com/docs/features/access-control/key-expiry).
- [VPN siempre activa en Android](https://developer.android.com/develop/connectivity/vpn#always-on).

Horus: fuente local del tag instalado 1.0.4, commit
`2f8f8a2faebd3d0fbd11dd83340bdcfbac437369`, manifest y TerminalSessionService.
