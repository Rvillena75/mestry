# Trabajo en MESTRY

La continuidad se basa en archivos y versiones Git, con conversaciones y
credenciales independientes por cuenta y entorno. Este repositorio es público
por autorización expresa del usuario del 27/10/2026. GitHub conserva el código
y la documentación técnica del repositorio. Google Drive mantiene la autoridad
documental de los originales seleccionados según el ADR congelado.

## Antes de trabajar

1. Leer el estado actual al principio de `README.md`,
   `docs/GITHUB_PUBLICATION.md` y los informes 09, 10 y 11 de
   `docs/investigaciones/2026-10-26_codex_24x7/`.
2. Revisar `git status` y los commits recientes; conservar cambios locales.
   No ejecutar reset, clean, stash, pull, checkout ni rebase automáticamente
   sobre trabajo ajeno o sin confirmar.
3. Leer el ADR `MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md`
   antes de proponer cambios documentales. Los informes históricos conservan
   su fecha y no certifican por sí solos el estado actual de los teléfonos.

## Límites

- No versionar credenciales, homes Codex, conversaciones, bases activas,
  dependencias instaladas, APK firmados ni capturas/registros brutos.
- No modificar teléfonos, permisos, SSH, VPN, OAuth, FolderSync o rclone por
  ejecutar una prueba local. Esas operaciones requieren alcance autorizado.
- No ejecutar los scripts históricos de instalación o migración como si
  fueran pruebas. No reinstalar ni cambiar Alpine/Horus por defecto.
- Usar clones fuera de los árboles sincronizados por Drive. El original
  histórico y las evidencias completas permanecen fuera de este repositorio.
- Esta es una edición pública: identificadores de hardware, cuentas, rutas
  locales y claves públicas del despliegue se sustituyeron por ejemplos.
  Consultar `docs/LOCAL_CONFIGURATION.md` antes de usar herramientas de dispositivo.
  No desplegar esta copia sobre la instalación existente como parte de un test.
- Revisar archivos y pruebas antes de confirmar/publicar. No convertir todo
  cambio detectado en un commit automático. No usar force push.

## Pruebas locales sin teléfonos ni inferencia

```sh
python3 -B -m unittest discover -s tools/horus_publish -p 'test_*.py'
python3 -B -m unittest discover -s tools/s25-codex-client -p test_helpers.py
python3 -B -m unittest discover -s tools/s23-remote-access -p 'test_*.py'
python3 -B -m unittest discover -s tools -p test_horus_pair_s25.py
node --test tools/s25-codex-client/pilot-policy.test.mjs
```

Las pruebas de integración Node que importan `../src/` se ejecutan dentro del
árbol upstream reconstruido con `prepare_source.py`, no directamente desde
`tools/s25-codex-client`. No instalar dependencias ni abrir conexiones reales
solo para resolver un import fuera de ese árbol.

Al finalizar una tarea, documentar cambios, pruebas, problemas y siguiente paso
en la documentación existente, sin transcribir conversaciones. La publicación
inicial no instala sincronización automática Windows/S23.
