# Publicación pública inicial de MESTRY

Fecha: 2026-10-27, America/Santiago. El usuario autorizó publicar el proyecto en
su cuenta y después pidió expresamente **repositorio público**, para enlazarlo
en su CV y postulaciones a internships. Destino: `Rvillena75/mestry`, rama `main`.
Esta autorización pública aplica a MESTRY, no a otros proyectos o datos personales.

## Alcance

Se preparó un clon Git fuera de los árboles sincronizados por rclone. El original
completo sigue intacto y no se inicializó Git dentro de su árbol Drive. No se
modificaron rclone, FolderSync, teléfonos, cuentas o servicios para publicarlo.

La selección inicial copió **155 archivos / 1.977.874 bytes** de código, pruebas,
parches y Markdown. Se dejaron locales **1.663 archivos** de evidencia bruta y
cachés: capturas, logs, XML, resultados JSON y snapshots históricos. Ninguno de
los originales se borró. Se incorporaron instrucciones para agentes, exclusiones,
esta documentación, configuración de ejemplo y una presentación pública del proyecto.

Antes de crear commits se saneó la copia pública: identificadores de hardware,
rutas de usuario, direcciones de despliegue, cuentas, IDs de carpetas Drive y
pines públicos del equipo local se sustituyeron por ejemplos. Esto no equivale
a cambiar credenciales ni dispositivos. Los originales de los informes y del
ADR congelado permanecen intactos fuera de Git; sus copias públicas conservan
las decisiones, con los datos de despliegue saneados. Las huellas históricas de
esos documentos se refieren a los originales, no a las copias públicas.

El parche upstream y `source-pins.json` se conservan íntegros. Las direcciones
que aparecen en líneas eliminadas de ese parche son ejemplos públicos del
upstream, no la configuración del despliegue personal. Se aplicó el parche al
archivo upstream fijado y se verificaron los **68 hashes** de texto resultantes,
sin ejecutar código upstream ni instalar dependencias.

Las referencias históricas a evidencia bruta pueden no existir en un clon.
No se crean archivos o resultados ficticios para cubrir esos enlaces. El código
y la documentación técnica se continúan en el clon Git; el original queda como
archivo histórico, sin dos autoridades automáticas para los mismos Markdown.

## Estado y límites

- H0 cerrada con limitaciones no bloqueantes para H1; detalles en el informe 10.
- El informe 11 registra las correcciones: FolderSync `SyncOK`, 76.353 archivos
  comprobados y 0 transferidos/eliminados; borrados desactivados y horario al
  minuto 17; ficha Codex/GitHub y bridge con supervisor recuperados.
- El usuario confirmó posteriormente que el acceso desde S25 funciona. Es una
  confirmación humana, no otra inspección instrumentada de ese cliente.
- Se dieron instrucciones sobre la contraseña de ConnectBot, sin modificar su
  clave ni verificar ese ajuste en el teléfono.
- Esta publicación no crea un clon S23, no instala sincronización Git automática
  y no demuestra que el teléfono haya recibido este repositorio.

## Identidad y comprobaciones

Se usa la cuenta GitHub CLI activa `Rvillena75`, sin copiar tokens. La identidad
Git se configura solo en este clon, con correo noreply de GitHub. No se crean
colaboradores, Pages, despliegues ni workflows automáticos.

Se revisa el contenido que realmente entra en Git para detectar claves privadas,
tokens, OAuth y contraseñas literales. Las coincidencias iniciales corresponden
a fixtures sintéticos. Se revisa además metadata personal en la edición pública.
La revisión tiene límites: no se presenta como garantía universal de ausencia de
secretos. Capturas, logs y estados privados quedan fuera del repositorio.

## Resultados

La selección privada inicial pasó 82 tests antes de solicitarse visibilidad
pública. Tras sanear la edición pública, los cinco grupos vuelven a pasar:
54 tests de publicación/browser/OAuth, 4 helpers, 8 de recuperación/observación,
13 de emparejamiento y 3 de política Node: **82 tests, sin fallos**.

El test del bootstrap dejó de depender de la clave pública personal y ahora
comprueba el pinning con un fixture sintético, sin cambiar las verificaciones SSH
del runtime. El parche upstream se aplicó sobre el tar fijado y sus **68 hashes**
coincidieron. No se compiló Android ni se ejecutaron tareas de modelo en esta fase.
Se cotejaron los **1.818 archivos** del original: siguen íntegros y sin cambios.

Publicación y verificación remota pendientes hasta registrar los resultados.
