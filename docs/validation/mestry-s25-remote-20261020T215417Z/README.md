# EXP07 — Evidencia de preparación S25 → S23

Registro del 2026-10-20. [Informe](../../S25_REMOTE_ACCESS.md), [comandos](commands.md), [manifest](manifest.json).

Clave pública exclusiva del S25 autorizada; identidad WSL conservada y reconexión independiente comprobada. Primera ejecución desde S25 **pendiente**. Puertos sin cambios y Horus remoto apagado. Dos timeouts por cambios de red conservados; no son fallos de credenciales ni ejecución de mutaciones.

- `p01`: timeout en IP anterior.
- `p02/p03`: ADB de recuperación, estado remoto apagado, escuchas e IP.
- `p04/p05/p06`: nueva IP con confianza previa, actualización WSL y reconexión.
- `p07`: revisión de código oficial fijado al commit instalado.
- `p08/p09`: segundo timeout y confirmación ADB del cambio de red.
- `p10`: alta atómica de la clave pública del S25, manteniendo WSL.
- `p11`: alias devuelto a la red actual y autenticación WSL comprobada.

No contiene contraseñas, claves privadas ni tokens. Las claves públicas y sus huellas sirven para identificar la autorización y verificar su conservación. La política de autenticación se observó sin modificarla. El texto de solicitudes de autenticación de cuentas no forma parte de estas sondas.
