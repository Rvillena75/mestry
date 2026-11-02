# MESTRY — H3: clon operativo S23 y entrada desde S25

Fecha: **02/11/2026**, America/Santiago. **EN VALIDACIÓN**; este primer registro
acompaña el código que se probará en el nodo, sin declarar despliegue por tener
los archivos publicados. Continúa H2; no repite H0 ni modifica el ADR congelado.

## Incremento preparado

- Contrato `alpine-aarch64` y ocho suites de aceptación del repositorio.
- `work_session.py lease`: lock local compartido durante operaciones/turnos del
  bridge; release explícito y recuperación pendiente ante EOF ambiguo.
- `project-gate.mjs`: admisión con recepción validada si limpio/libre, preservación
  del trabajo dirty y bloqueo hasta la terminación del turno identificado.
- `horus_keepalive.py`: tarea opcional fetch-only cada 120 segundos dentro del
  supervisor existente, sin otro servicio o puerto.
- `s23_project.py`: validación ARM64, overlay de la release privada ya instalada
  y recibo documental saneado. No copia configuraciones públicas de ejemplo
  sobre el teléfono ni importa credenciales, historiales o dependencias WSL.

Las nuevas pruebas WSL cubren lease/busy/EOF, cambios dirty, candidato válido,
el lock real Python desde Node, notificaciones terminales anticipadas/ajenas,
timeout ambiguo y conservación de la release anterior. La aceptación real del
S23 y el cliente se añadirá después de ejecutar el incremento.

## Preflight y límites iniciales

Ambos teléfonos se identificaron mediante el servidor ADB existente. Termux
aceptó SSH autorizado y Horus respondió en su puerto SSH; el bridge 8787 no
respondía inicialmente. Se abrió Horus normalmente, con las credenciales de
desarrollo ya autorizadas usadas solo en las interfaces normales. El perfil
Bare terminal confirmó `/home/horus`, UID 1000 y `aarch64`.

**Incidencia del operador:** al probar el ejecutable ADB local, su versión 41
reinició el servidor versión 40 del PC. Ambos dispositivos se revalidaron
autorizados después; se volvió al transporte de protocolo sin más arranques.
No se reiniciaron los teléfonos ni se cambiaron claves, VPN o emparejamientos.

La entrada de teclas wake/control en una terminal ya visible produjo caracteres
extra. Los primeros intentos no ejecutaron el preflight esperado. Se corrigió
la detección de pantalla y se comprobó el SHA-256 del payload antes de ejecutarlo.
Un envío largo agotó su timeout en una asignación parcial; se inspeccionó y
completó explícitamente antes de ejecutar, sin repetir escrituras del proyecto.

El repositorio operativo se ubicará fuera de FolderSync y conservará
dependencias propias de ARM64. La recepción automática solo podrá aplicar
cambios desde entradas gestionadas; un escritor que ignore el lock o deje jobs
separados sigue fuera de la garantía cooperativa. H5 validará reposo, reinicio
y PC realmente apagado. Drive y las autorizaciones documentales siguen en H4.
