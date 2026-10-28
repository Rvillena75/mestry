# Carpeta de pruebas en la papelera

Una lectura real del S23 informa `trashed=true`, `explicitlyTrashed=false` en
Horus y en sus dos revisiones. Sus IDs y padres siguen siendo los originales.
Esto indica que una carpeta superior está en la papelera. No es un rechazo del
scope ni se arregla ampliándolo. No se han restaurado ni movido archivos.

Para conservar las pruebas existentes:

1. Abrir [Papelera de Google Drive](https://drive.google.com/drive/trash) con la
   cuenta utilizada por MESTRY.
2. Buscar la carpeta superior de `MESTRY/Review/Horus` que se haya eliminado
   (`MESTRY` o `Review`) y usar **Restaurar**, si se desea recuperarla.
3. Comprobar que vuelve a aparecer
   [Horus](https://drive.google.com/drive/folders/DRIVE_FOLDER_01_EXAMPLE)
   dentro de MESTRY/Review. Conservar el ID; no crear una copia ni cambiar permisos.
4. Actualizar las carpetas de MESTRY y repetir el listado nativo.

Si la eliminación fue intencionada, conservarla. Elegir otra carpeta ya
autorizada a la misma app o preparar un consentimiento de Google Picker con el
mismo cliente y `drive.file`. No reautorizar ni sustituir tokens automáticamente.

La activación de carpetas del explorador y su asignación a proyectos son
controles de MESTRY. No cambian las autorizaciones OAuth de Google ni trasladan
el destino del publicador de prueba.
