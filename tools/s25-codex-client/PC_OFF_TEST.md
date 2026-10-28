# Ensayo físico de autonomía

Preparado; **todavía no ejecutado**. La app, interrupción, recuperación sin caché
y acceso al publicador ya pasaron con el PC encendido. No se necesita cambiar
puertos, claves ni permisos para este ensayo.

1. En S23 conservar Horus y el servicio remoto activos. En S25 dejar conectado
   **Mestry s23 8023** en ConnectBot, con el reenvío **MESTRY App**. Abrir MESTRY
   Piloto y comprobar el indicador verde. La red Wi-Fi debe funcionar sin el PC.
2. Apagar físicamente el PC mediante su menú normal. No reiniciar ni apagar el
   S23, ni cerrar su servicio para hacer la prueba.
3. Desde MESTRY Piloto del S25 enviar:

   > Trabaja solo en /workspace/projects/mestry-horus-smoke. Obtén la hora UTC
   > real y usa un sufijo aleatorio para crear un archivo nuevo
   > PC_OFF_CHECK_<horaUTC>_<sufijo>.txt. Si existe, detente. Escribe dos líneas
   > terminadas en salto de línea: MESTRY_PC_OFF_OK y utc=<hora real>.
   > Ejecuta pwd, uname -m, cat del archivo y sha256sum. Muestra el nombre exacto
   > y las salidas reales. Conserva los demás archivos y no publiques en Drive.

4. Abrir la consola **Mestry horus** del S25 y verificar el nombre exacto devuelto:

   ```sh
   cd /workspace/projects/mestry-horus-smoke
   date -u
   cat NOMBRE_EXACTO_DEL_ARCHIVO
   sha256sum NOMBRE_EXACTO_DEL_ARCHIVO
   ```

   Comparar contenido y hash con la respuesta de la app. Un marcador nuevo con
   lectura por otra sesión distingue esta prueba de una conversación en caché.
5. Para el ensayo de reposo, dejar la pantalla S23 apagada durante **16–20
   minutos**, conservando Wi-Fi y los servicios. Sin desbloquear primero el S23,
   repetir desde el S25 con otro nombre y marcador `MESTRY_IDLE_OK`. Registrar la
   hora de inicio/fin y la lectura independiente.

Conservar resultados o el error exacto. Si falla, diagnosticar el servicio/túnel
antes de cambiar ajustes. El bloqueo de la interfaz Horus tras 15 minutos no se
debe confundir con terminar SSH. No desactivarlo como arreglo automático.

Este ensayo no valida reinicio/Boot ni disponibilidad 24/7. No hay autostart nuevo
del bridge ni una tarea programada de OAuth. La renovación de más de siete días
se comprueba por separado a partir del 2026-10-29T06:08Z.
