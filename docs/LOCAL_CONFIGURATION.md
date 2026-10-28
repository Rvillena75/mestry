# Configuración local de la edición pública

Este repositorio presenta el código y el diseño del prototipo, no contiene la
configuración operativa de los teléfonos del autor. Los ejemplos no conceden
acceso a cuentas, dispositivos ni carpetas. No se entregan tokens o claves privadas.

## Antes de ejecutar herramientas de dispositivo

1. Identificar los equipos propios y su autorización normal por ADB/SSH.
2. Configurar las rutas de ADB/DEX, seriales y modelos en las herramientas
   utilizadas. `S23_SERIAL`, `S25_SERIAL`, `/home/developer/` y las rutas Windows
   con usuario `developer` son ejemplos. `192.0.2.0/24` es direccionamiento de
   ejemplo; sustituirlo por el destino propio verificado.
3. Verificar fuera de banda las claves públicas y huellas SSH. Los marcadores
   `CONFIGURE_LOCAL_PUBLIC_KEY` y `CONFIGURE_LOCAL_FINGERPRINT` no son claves
   válidas; nunca desactivar la comprobación de host para sortearlos.
4. Para Drive, configurar la cuenta propia y los IDs de destino autorizados;
   `owner@example.invalid` y `DRIVE_FOLDER_*_EXAMPLE` son valores inertes para
   la publicación pública y las pruebas. Mantener OAuth fuera del repositorio.
5. Revisar los UIDs esperados, perfiles y guardas de scripts históricos. Las
   migraciones acotadas a una instalación anterior no son instaladores genéricos
   ni deben repetirse sobre una instalación actual.

Los parámetros locales siguen siendo constantes de operador en varios scripts,
como en el prototipo. No se afirma haber implementado un nuevo sistema general
de configuración. Conservar las guardas que rechazan identidades o perfiles
inesperados; para desarrollar primero usar únicamente las pruebas offline.

## Reproducir el cliente

`tools/s25-codex-client/prepare_source.py` requiere el tar upstream de la revisión
fijada y un destino nuevo. Verifica el hash del tar, el parche y los archivos
resultantes; también descarga y verifica el wrapper Gradle oficial. Consultar su
README antes de ejecutar. No necesita credenciales de los teléfonos para preparar
fuentes; el build Android y el despliegue son pasos separados.

Los hashes de los pines verifican fuentes reproducidas. Los hashes y PASS de
informes históricos documentan ensayos de otra fecha, no pruebas ya ejecutadas en
la máquina de quien clone el repositorio. En algunas copias públicas se sanearon
metadatos; las huellas históricas corresponden a sus originales privados.
