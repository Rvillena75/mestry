# MESTRY S25 — Drive, actividad y controles

**Cierre verificado el 2026-10-22**, con S23 y S25 identificados por su serial y
modelo. El [checkpoint anterior](CHECKPOINT.md) conserva la pausa; el usuario
autorizó después continuar. La etiqueta, la raíz abierta y su interruptor activo
se comprobaron en el S25. [Resultado final](result.json), [manifest](manifest.json).

Continuación del 2026-10-21. Se conservan instalación, credenciales y conversaciones
anteriores. Esta entrega sustituye el estado operativo r4; su evidencia histórica
permanece intacta.

## Cambios entregados

- Android **0.2.0-mestry-pilot7 / 10007**, mismo paquete y certificado, instalado
  mediante actualización sin borrar datos ni emparejar otra vez. APK privado:
  `C:\Users\developer\Downloads\MESTRY-Piloto-20261021-r7.apk`.
  [Huella y resultado](apk-result.json),
  [APK extraído del S25 y cotejado de nuevo](resume-installed-apk.json),
  [firma/manifiesto](apk-inspection-pilot7.log),
  [compilación](android-build-pilot7.log).
- Etiqueta pequeña **Drive · MESTRY** dentro de la tarjeta del proyecto; selector,
  subcarpetas, paginación y vista previa de texto/Markdown/Google Docs. Otros
  formatos se abren en Drive con URLs construidas con IDs validados.
- **Ajustes → Google Drive → Carpetas** permite activar/desactivar raíces ya
  autorizadas. Desactivar solo modifica la lista local, no borra archivos ni
  revoca OAuth. Pegar una URL no concede permisos de Google.
- Actividad contraíble debajo de cada mensaje del usuario: comentarios,
  razonamiento y herramientas que app-server entregue, conservando comandos y
  salidas. Respuestas finales fuera del desplegable. No se reconstruye contenido
  que una versión anterior del servidor no haya guardado. El historial extendido
  se solicita al iniciar y reanudar hilos; avisos se muestran cuando existen en
  la fuente, sin fabricar avisos propios del CLI.
- Botón simple de Ajustes; Conexión dentro. Retirado el selector fijo de acceso.
  Nuevos chats en **never / dangerFullAccess**, por petición expresa del usuario.
  La respuesta real de inicio/reanudación debe confirmar ambas políticas para
  aceptar un turno. La ACL del bridge sigue sin ser un sandbox del SO.
- Corregido un fallo real al crear/reanudar chats: Codex 0.163 rechazaba `null`
  en booleanos opcionales. Se omiten parámetros ausentes, conservando `false`
  explícito. [Fallo capturado](runtime-policy-before.json),
  [55 tests finales](node-tests-final.log).

## Drive real y decisiones conservadas

Raíz elegida por el usuario: [MESTRY](https://drive.google.com/drive/folders/DRIVE_FOLDER_02_EXAMPLE).
Cuenta objetivo: la cuenta Gmail ya configurada, sin cambiar cliente ni ampliar
`https://www.googleapis.com/auth/drive.file`.

El usuario completó Picker desde su terminal privada, con el cliente Desktop
existente y callback ya aprobado `127.0.0.1:53682`, máximo 180 segundos. El token
activo se conservó durante el consentimiento y se guardó antes una copia privada
`token.pre-picker.*.json`, modo 600, en Termux. No se copiaron credenciales a WSL,
Horus, S25, el repositorio ni la evidencia. No repetir OAuth para esta carpeta.

Otra conexión estricta al S23 verificó renovación HTTPS nativa, cuenta, cliente,
scope, carpeta fuera de la papelera, activación y asignación al proyecto
`/workspace/projects/mestry-horus-smoke`. [Verificación OAuth](mestry-native-verified.json),
[lectura nativa de esta continuación](resume-drive-native.json).
La lista real no contiene todavía documentos autorizados. El usuario armará su
árbol; no se crearon fixtures nuevos para rellenarlo.

La [tarjeta real](resume-app-stable.png) muestra **Drive · MESTRY**;
el [navegador real](resume-drive-root-ready.png) abre la raíz sin errores y
el [control de carpetas](resume-drive-enabled.png) confirma MESTRY activa.
La desactivación anterior y la reactivación final quedan reunidas en
[la comprobación de controles](drive-control-live-ui.json).

**El permiso Google y la lista local son distintos.** Con `drive.file`, elegir
una carpeta no garantiza acceso automático a todos sus archivos existentes o
descendientes. Una nueva carpeta/documento puede necesitar concesión mediante
Picker; desactivar en MESTRY no revoca el permiso global de la cuenta. La app
incluye un acceso a las conexiones de Google para gestionarlo.

La carpeta antigua `Review/Horus` y sus pruebas están en papelera heredada. El
usuario decidió conservar esa eliminación; no se restauraron, movieron ni
compartieron archivos. La carpeta MESTRY nueva para consulta **no cambia el
destino fijo del publicador anterior** ni sincroniza el workspace. El escritor
sigue limitado a `S23_PUBLISH_TEST.md` y su destino antiguo; no se declara una
publicación actual ni se redirige el escritor sin una decisión posterior.

El broker `mestry-drive-v1` ejecuta un catálogo fijo. La API Drive se usa solo
para lectura; activación y asignación se guardan en el estado privado Termux.
Cada lectura valida raíz activa, permisos, papelera y ascendencia. No se siguen
shortcuts para salir de la raíz. OAuth permanece en UID Termux 10348; Codex y el
cliente restringido usan UID Horus 10350. No se añade una clave WSL a Horus.

## Verificación y límites de la evidencia

| Comprobación | Resultado / evidencia |
| --- | --- |
| Node, sin modelos | 55/55, [log final](node-tests-final.log) |
| Política fija del piloto | 3/3, [log](policy-tests.log) |
| Helpers, incluida actualización con reversión | 4/4, [log](helper-tests.log) |
| Publicador + navegador con API simulada | 46/46, [log](native-tests-final.log) |
| Navegador sobre código instalado en S23, API simulada | 20/20, [log](native-browser-s23-final.log) |
| Picker, errores/cancelación/cuenta/scope/backup | 8/8, [log](picker-setup-tests.log) |
| Renderer del APK instalado | 8/8, [resultado](activity-rendering-pilot7.json) |
| Parser de metadata del APK instalado | 6/6, [resultado](metadata-parser-pilot7.json) |
| APK, misma firma y fuente Android de compilación | PASS, [fuente](android-staged-source.json) |
| Reanudación real en Horus, sin turno | never / dangerFullAccess, [resultado](runtime-policy-final.json) |
| OAuth + raíz real desde S23 | PASS, [resultado](mestry-native-verified.json) |
| Túnel S25 y autenticación negativa, continuación | PASS, diez direcciones no loopback y wildcard IPv6 libres, [resultado](resume-loopback-initial.json) |
| Drive real en S25: etiqueta, navegador, control local | PASS, [resultado](drive-control-live-ui.json) |
| Fuente y APK conservados después de la pausa | PASS, [fuente](resume-source-integrity.json), [APK](resume-installed-apk.json) |
| Fuente completa, parche y wrapper oficial | 64 archivos verificados, [reproducción](source-reproduction-final-pilot7.json) |

Las pruebas de subcarpetas y vistas previas usan fixtures. La nueva raíz real
está vacía para este cliente; esa funcionalidad todavía necesita documentos
reales autorizados para una aceptación humana completa. No se envió ningún
turno de modelo en este incremento ni se modificaron archivos del proyecto para
probar la interfaz.

La recuperación anterior, publicación histórica y uso real del modelo conservan
sus registros en la [entrega r4](../mestry-s25-resumed-20261021T154810Z/HANDOFF.md).
PC físicamente apagado, reposo prolongado, Boot y estabilidad 24/7 siguen
pendientes. [Protocolo físico](../../../tools/s25-codex-client/PC_OFF_TEST.md).
La renovación después de más de siete días debe observarse después del
2026-10-29 06:08 UTC; producción no garantiza tokens permanentes ni elimina la
posibilidad de revocación.

## Código, transporte y recuperación

Base upstream `538d65f67e34907789237fc71f56e8ca95d9f3cb`, GPL-3.0-only. No hay
commit/push ni repositorio nuevo en este incremento. Fuente reproducible en
[source-pins.json](source-pins.json); el parche acumulado conserva su nombre
[mestry-pilot1.patch](../../../tools/s25-codex-client/mestry-pilot1.patch).

El bridge final incluye la corrección de parámetros opcionales y conserva su
versión previa para reversión. [Bundle y manifest](bridge-bundle-final.json),
[actualización real](bridge-upgrade-final.json). `horus_upgrade.py` verifica
ambos manifests, rechaza turnos/aprobaciones pendientes y restaura la versión
anterior si falla el arranque. No ejecutar `pair`, el instalador inicial ni
generar otra clave para actualizar.

Puertos existentes conservados: Termux 8023, Horus SSH 127.0.0.1:8022, bridge
127.0.0.1:8787 y reenvío S25 127.0.0.1:18787. Ningún servicio nuevo ni exposición
LAN. Los artefactos de actualización son solo código y se transfieren por la
clave restringida ya existente. El staging público se retira al verificar el
despliegue. Callback y transferencia deben quedar cerrados al finalizar.

Al retomar, Horus seguía enabled/running y conservaba una clave S25 autorizada.
Se reconectó únicamente el perfil existente Termux de ConnectBot para recuperar
el reenvío. [Estado del provider](resume-horus-provider-status.json),
[conexión recuperada](resume-termux-reconnect.png).

SuperDisplay se dejó **detenido por petición expresa del usuario**; no se cambió
su tipo de inicio Auto. Su regla de recuperación causó reinicios después del
primer cierre forzado. La restitución de esa regla falló en un helper y se
corrigió antes de cerrar; la consulta independiente confirma que se conservó
exactamente la configuración original. [Estado final](superdisplay-service-final.json),
[recuperación restaurada](superdisplay-recovery-restored.json).
Auto sigue vigente: la detención no es una desactivación permanente después de
reiniciar Windows. El antiguo helper de arranque quedó bloqueado para evitar
reinicios involuntarios. Los helpers USB usan serial/modelo, no transport IDs.

[Limpieza de diagnósticos temporales](cleanup-final.json). El callback está
cerrado, OAuth sigue privado y la transferencia pública de código fue retirada:
[verificación de esta continuación](resume-native-integrity.json).

Guías operativas: [Android](../../../tools/s25-codex-client/README.md),
[broker/Picker](../../../tools/horus_publish/README.md),
[publicación y destino histórico](../../HORUS_DRIVE_PUBLISH.md).
