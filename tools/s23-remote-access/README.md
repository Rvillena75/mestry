# Acceso privado al S23 desde fuera de la Wi-Fi

Preparación del 2026-10-22. El usuario pidió disponibilidad 24/7 y acceso desde
cualquier conexión a Internet. La propuesta usa Tailscale Android con el SSH
existente, conserva el túnel de MESTRY y elimina la dependencia de la IP LAN.

**Autorizado, implementación en curso.** Leer el [plan de puertos, cambios y pruebas](PORT_PLAN.md).
El usuario aprobó Tailscale y añadió VPN automática en el S25, limitada a MESTRY
y ConnectBot como transporte. Apagado 30 segundos después de salir, retenido si
hay una tarea activa; desconexión explícita inmediata. Sin VPN siempre activa en
el S25. El plan incluye sockets VPN administrados por la app y TCP 8023 privado.

El diagnóstico de solo lectura, ejecutado con ambos teléfonos ya autorizados por
USB, no instala, modifica ajustes, inicia servicios ni abre listeners:

```sh
python3 -B tools/s23-remote-access/preflight.py --output /ruta/nueva/preflight.json
```

Los IDs están fijados al S23 SM-S918B y S25 SM-S938B conocidos; rechaza un modelo
distinto y nunca utiliza transport ID. Solo registra metadatos seleccionados,
hashes y estado; no lee contenido de claves, tokens, credenciales ni chats.

La disponibilidad continua, acceso entre redes y recuperación tras reiniciar
son pruebas distintas. Termux tiene hook de arranque; Horus instalado no tiene
receptor BOOT_COMPLETED. No confundir mantener el servicio activo con prometer
arranque autónomo tras un reinicio. Se conservará la frontera entre los UIDs.

Continuación comprobada y límites en el
[handoff](../../docs/validation/mestry-s23-remote-access-20261022T034500Z/HANDOFF.md).
La VPN automática ya está habilitada en el S25. Se observaron SSH privado nuevo,
túnel, hello e historial fresco por datos móviles, regreso dentro del margen,
apagado entre 30,7 y 31,7 s sin tareas y Desconectar inmediato. Watchdog instalado
en Horus y saludable. Retención de una tarea real, reposo prolongado, cargador de
pared, PC apagado, 24 h y recuperación tras reinicio siguen sin ensayar.

Herramientas de continuación:

- `device_ui.py`: interfaz con serial/modelo fijos; bloquea inspección/captura
  de pantallas con contraseñas. `tap-connection` localiza exclusivamente el botón
  público Conectar/Desconectar sin devolver campos de entrada.
- `vpn_observe.py`: flags de ciclo de vida y transporte VPN exacto; no confundir
  la capacidad `NOT_VPN` con un transporte VPN. No lee el almacén de claves.
- `reconnect_private_ui.py`: cierra la terminal Termux anterior, abre el perfil
  privado conservado y espera la confirmación del servicio. Rechaza tareas
  activas y se detiene ante un ingreso privado; no intenta contraseñas.
- `mobile_validate.py`: ensayo autorizado con interrupción breve de Wi-Fi desde
  Ajustes, red predeterminada CELLULAR validada sin agentes WIFI, SSH nuevo,
  túnel, hello y metadatos `session.content`/`session.sync`. Restaura Wi-Fi y la
  etiqueta temporal de diagnóstico en `finally`; no guarda mensajes ni logcat
  bruto. No usar `svc wifi` como garantía de que permanezca apagada.
- `horus_keepalive.py`: solo dentro de `/home/horus`, usa el controlador existente.
  Un fallo de `status` impide solicitar arranque. No mata procesos vivos ni abre
  listeners. No demuestra recuperación Android tras reinicio.

Regresiones sin teléfonos, cuentas ni llamadas al modelo:

```sh
python3 -B -m unittest discover -s tools/s23-remote-access -p 'test_*.py' -v
```
