# Revisión del estado de MESTRY — 04/11/2026

**Lector Drive activo — 08/11/2026:** consentimiento `drive.readonly` completado,
raíz MESTRY fijada por ID y token separado del publicador. Renovación nativa,
lectura real, cache hit y recuperación offline verificados. 211 tests WSL /
68 de candidata S23 correctos. El inventario/caché aún avanzan por lotes.
[Estado y límites](DOCUMENT_READER_AUTH.md). Los cortes inferiores conservan su fecha.

**Incremento documental — 08/11/2026:** sincronización incremental bajo demanda,
caché SQLite durable, recuperación offline e historial de texto implementados y
activados en Termux/S23. **196 pruebas WSL y 53 de candidata S23 correctas**.
Inventario y changes reales pasaron; la raíz seleccionada devuelve 0 documentos
visibles, por lo que contenido real y UI S25 siguen pendientes de aceptación.
RAG continúa pendiente de revisión. [Operación, evidencia y límites](DOCUMENT_SYNC.md).

**Complemento — 08/11/2026:** la [auditoría de Drive](DRIVE_IMPLEMENTATION_AUDIT.md)
contrasta código, estados históricos y criterios del ADR. Nueve suites locales:
163 tests correctos (cuatro corresponden a auxiliares no versionados). Sin nueva
prueba de teléfonos. Navegador bajo demanda implementado; sincronización
incremental y RAG pendientes; publicación bloqueada en el último registro por
destino fuera de Review. La sección histórica del 03/11 conserva sus pendientes
H3, resueltos según el recibo del 04/11 al inicio de este documento.

**H3 aceptada para el recorrido definido.** Una revisión distinta se validó y
aplicó por el bridge y una tarea real S25 trabajó sobre ella. El
[recibo](validation/H3_BRIDGE_ACCEPTANCE_20261104.md) reúne versiones, suites,
concurrencia, terminación y recuperación fresca del mismo hilo. El estado final
S23 fue limpio/libre/idle, sin recuperación ni candidato fallido. H4/H5 siguen
pendientes. APK piloto 9, release privada, checkout aceptado `791688abdd59afb33516916c9e031c94553e02c5` y fuentes
locales conservan referencias distintas.

La corrección carga estado bajo lock en la CLI y en el poll del supervisor
existente. La transición de los dos controles protegidos fue explícitamente
revisada antes de recibir; la huella nativa de dependencias se conservó. El
PATH temporal se retiró antes de S25. **159 pruebas por target** acreditan ese
candidato. Interrupción complementaria aceptada en otro turno de espera: gesto normal sobre el control dinámico, turno identificado `interrupted`, actividad fresca y cero turnos activos.

El recorte de procesos del 04/11 tiene evidencia actual de ActivityManager;
no explica retrospectivamente las señales del 03/11. No se cambiaron las
protecciones Android. Cambio directo de red y disponibilidad prolongada siguen
siendo mejoras posteriores. El siguiente paso es revisar Android/pins locales,
sin avanzar H4/H5. Las 16 rutas iniciales se preservaron; cinco permanecen locales.

## Revisión histórica del 03/11

El corte siguiente conserva su fecha y describe el estado anterior a la aceptación
del 04/11. Sus pendientes H3 se concilian con el recibo vigente; los límites del
producto completo y de H4/H5 permanecen aplicables.

## Evaluación

MESTRY tiene un **prototipo funcional de desarrollo móvil**: Codex ejecuta en
Horus/Alpine ARM64 del S23, el S25 inicia tareas sobre el proyecto y recupera
contenido del mismo hilo. Hay controles de concurrencia, fuentes reproducibles
y publicación documental acotada. El avance principal ya no depende de instalar
otro entorno o construir otra interfaz.

La brecha inmediata es la **fiabilidad de operación**: Termux terminó con señal
9, el acceso SSH necesitó recuperación, el cambio directo de red no recuperó
historial fresco y la interrupción actual no tiene aceptación. Además, H3 aún
requiere aplicar una revisión Git nueva por la entrada del bridge. El producto
completo de asistente —Core, voz, memoria propia, conectores generales y RAG—
conserva trabajo pendiente. No hay base para asignar un porcentaje global de
avance: estos alcances tienen aceptaciones diferentes.

## Evidencia y madurez por componente

| Componente | Estado sustentado | Límite vigente |
|---|---|---|
| H0/H1: base y laboratorio | Cierre histórico; ida/vuelta Git WSL/S23 y guardas documentadas | No se repitió esa auditoría ni se usa como monitor de disponibilidad |
| H2: sesiones de trabajo WSL | Implementado: start/receive/finish/check, validación de candidato y lock durante descendientes | Bloqueo cooperativo; escritores que lo ignoren quedan fuera de garantía |
| H3: ejecución nativa y cliente | Tarea nueva desde S25 en el proyecto real; HEAD, BUSY y preview verificados | Falta aplicar un candidato Git nuevo desde el bridge |
| Cliente Android | Piloto 9 instalado; selección corregida y dos reaperturas con mismo hilo e historial fresco | Cancelación pendiente; el envío sin inicio de la mañana no se reprodujo ni tiene causa establecida |
| Acceso privado | SSH, túnel loopback, autorización e historial sobre una conexión nueva por datos móviles aceptados | El cambio directo Wi-Fi/datos no pasó; estabilidad de SSH pendiente |
| Fuentes y pruebas | 68 archivos reproducidos; compilación Android offline; 148 pruebas offline actuales correctas en WSL | Las 137 pruebas ARM64 previas corresponden a la revisión anterior; no certifican el candidato local actual |
| H4: documentos | Broker/navegador/publicador acotados; lectura del fixture vigente de 79 bytes verificada por hash | Destino de publicación bloqueado por padre distinto de Review; mapa de autoridades y restore autónomo incompletos |
| H5: disponibilidad | Ventana de pantalla apagada de 20 min, 41/41 muestras saludables | USB y PC presentes; faltan PC apagado, 24 h, reinicio y recuperación aceptados |
| Asistente completo | ADR documental disponible, investigación y componentes parciales | No se acredita Core, RAG integrado, voz, memoria del asistente ni Device Agent por el éxito de Codex |

Detalle técnico y cronología: [informe H3](investigaciones/2026-10-26_codex_24x7/15_H3_NODO_S23.md#continuación-del-0311-por-la-noche--conversación-nueva-y-piloto-9).
El historial de un piloto no sustituye una aceptación del producto completo.

## Versiones y trabajo pendiente de integrar

Al iniciar esta revisión había **13 rutas locales pendientes**: seis modificadas
y siete nuevas, sin staging. Contienen el incremento de herramientas S23, sus
pruebas, el parche piloto 9 y documentación. Se conservan íntegramente. Esta
revisión añade únicamente documentación y actualiza sus puntos de entrada.
El check WSL dio `busy=false`, `phase=idle`, sin recuperación ni candidato
fallido; `dirty=true` corresponde a ese trabajo conservado. No había una
validación candidata almacenada que coincidiera con HEAD en ese estado del
wrapper. Los resultados offline cotejados se informan por separado; la próxima
recepción/publicación debe validar el candidato real.

| Capa | Referencia verificada |
|---|---|
| HEAD WSL y `refs/heads/main` consultado en GitHub | `4865d2c235e3b622cfa5df49b3f41ce1784a287b`; sin commits salientes |
| Checkout/backend S23 | Ese mismo HEAD en el último check nativo del ensayo; no se vuelve a consultar el perfil Horus en esta revisión |
| APK S25 | `0.2.0-mestry-pilot9 / 10009`, actualización del ensayo anterior, con datos y emparejamiento preservados |
| Fuentes piloto 9 | Parche y pins locales; 68 entradas y SHA del parche coherente, revalidados en esta revisión |

Solo cambian respecto de los pins de HEAD dos controladores de selección/caché
y los metadatos de versión Android. El upstream permanece fijado. El APK
instalado y el commit público son referencias distintas: publicar documentación
no despliega el APK ni actualiza el backend.

La huella de fuentes cambió y el wrapper WSL ya tiene su revisión local. **La
política nativa S23 conserva la huella anterior.** Antes de recibir el candidato
completo allí, preparar y revisar su compatibilidad, conservar rollback y
aprobar la huella solo después de verificar el entorno. No reaprobarla de forma
automática para quitar el bloqueo. No se presupone que hagan falta paquetes nuevos.

## Incidencias: qué sabemos y qué falta establecer

| Caso | Observado | Explicación que aún falta |
|---|---|---|
| Termux/SSH | Dos ausencias del daemon en la continuación; terminal terminada con señal 9; recuperación con helper existente, sin cambio de configuración | Emisor y motivo de la señal, momento de caída y relación con pantalla, carga, UID o red. Los exit-info disponibles eran anteriores |
| Interrupción | El turno inició; el monitor no reconoció un comando normalizado y después no encontró habilitado el control; no se hizo el gesto; el turno terminó `completed` | Si falló la instrumentación, el estado de conexión, la representación del turno en UI o una combinación. No está demostrado un defecto de `turn.interrupt` |
| Cambio de red | Sin historial fresco al pasar directamente a datos; una conexión SSH nueva sobre datos sí pasó | Qué capa se perdió y en qué instante. No atribuir el fallo a Tailscale o al cliente sin separar SSH, túnel, hello e historial |
| Publicación Drive | Fixture legible y hash correcto; carpeta restaurada fuera de Review y publicador bloqueado | Destino documental que debe quedar aprobado y accesible; no es evidencia de fallo OAuth |

El código del cliente cambia la descripción accesible del control durante un
turno a **«Enviar instrucción; mantén pulsado para detener»**. El próximo harness
debe reconocer ese estado y el de reposo, comprobar el padre habilitado y
confirmar actividad fresca del servidor; buscar solamente «Enviar» o usar una
caché antigua no basta. Esto orienta el diagnóstico, no demuestra su causa.

## Alcance vigente de cierre H3 — continuación del 03/11

La recepción pendiente tiene prioridad en esta continuación autorizada. Se prepara
un candidato nativo con herramientas, pruebas y documentación concordantes,
manteniendo la huella ya revisada en S23. El parche Android/pins piloto 9 y los
auxiliares Drive se preservan locales. No se reaprobará la política del teléfono
para resolver este ensayo, ni se aplicará el SHA por CLI antes del bridge.

**Aceptar H3:** registrar SHA anterior y nuevo distintos; entrada gestionada
`session.start` con validación candidata ARM64 antes del fast-forward; tarea real
S25 sobre el nuevo SHA con lectura de AGENTS/STATUS, BUSY/salida 3 y preview OK
con índice intacto; terminación identificada, lock liberado, checkout limpio/libre,
sin recuperación pendiente y contenido fresco del mismo hilo tras reabrir.

Termux/SSH se comprueba durante la aceptación y solo se recuperan componentes
existentes cuando hace falta. Una caída reproducida que impida el recorrido exige
una corrección acotada. La señal 9 anterior no establece causa. La cancelación se
repite reconociendo la descripción accesible dinámica y actividad fresca, sin
confundir espera natural con interrupción. La nueva conexión celular ya aceptada
no necesita otra campaña de red para acreditar la aplicación Git.

## Mejoras posteriores de operación — fuera del cierre obligatorio

El diagnóstico causal de Termux y la recuperación automática al cambiar de red
conservan sus incidencias. Una ventana adicional de 60 min es una propuesta de
estabilización posterior, no prerrequisito de H3. No se ejecuta un ensayo de 24 h.

**H4 pendiente y no implementada aquí:** destino documental válido, autoridades/IDs
y recuperación sintética sin PC. No ampliar OAuth ni restaurar ancestros.
**H5 pendiente y no implementada aquí:** disponibilidad prolongada, PC apagado,
reinicio y recuperación, con condiciones y cobertura definidas en su propio ensayo.

## Qué puede hacerse con cada dispositivo

| Disponibilidad | Trabajo útil siguiente |
|---|---|
| Solo S23 | Diagnóstico acotado de Termux/SSH, preparación del observador nativo, revisión de entorno/huella y preparación de recuperación sintética |
| S23 y S25 | Cancelación, reconexión entre redes, recuperación fresca del hilo y recepción real del candidato mediante el bridge |
| Intervención física del usuario | Cambio a cargador de pared/PC apagado y, cuando corresponda, ensayo separado de reinicio/desbloqueo |
| Solo WSL | Revisión del candidato, mejora del harness con fixtures y preparación documental; no sustituye aceptación física S25 ni H5 |

Estas son propuestas de ejecución, no ensayos realizados en esta revisión.

## Después de la continuidad

Definir el siguiente caso útil de producto sobre documentos seleccionados. El
ADR mantiene Drive como autoridad de originales y permite lecturas directas
antes de construir un RAG completo. Corpus incremental, extracción, búsqueda con
citas y evaluación deben aceptarse antes de añadir una base vectorial por defecto.
El flujo de desarrollo Codex no acredita el Core del asistente.

Las cinco fuentes anteriores de voz, secretaría, contexto, teclado y broker de
modelos referidas por el ADR no figuran con esos nombres en este clon; la auditoría
histórica tampoco las localizó en su alcance. Recuperar sus originales antes de
atribuirles requisitos o implementar esas etapas. No se afirma inexistencia global
ni se convierten propuestas antiguas en especificaciones aprobadas.

## Alcance de esta revisión y fuentes

Se verificaron Git local/remoto, política/estado del wrapper, pins/parche y
metadatos seleccionados de los resultados recientes. Una lectura nueva por el
SSH Termux existente obtuvo el health correcto del bridge. Es una muestra puntual:
no revalida autenticación/historial S25, estado privado Horus ni disponibilidad
prolongada. No hubo nuevas tareas de modelo, instalaciones, cambios de teléfono,
Drive/OAuth/sincronizadores, commit o push. Las 148 pruebas y la compilación son
los resultados del incremento anterior cotejados; no se repiten por editar Markdown.

Se actualizaron los puntos de entrada que aún anunciaban S25 pendiente, sin
reescribir la cronología de los informes ni el ADR congelado. Las verificaciones
de esta entrega son diff, enlaces locales, preservación del código previo y
preview de cierre con índice intacto.

- [Estado operativo](../STATUS.md) y [roadmap](ROADMAP.md).
- [Guía de sesiones H2/H3](WORK_SESSIONS.md) y [comprobaciones S23](S23_CHECKS.md).
- [Plan H0–H5](investigaciones/2026-10-26_codex_24x7/09_REORIENTACION_CONTINUIDAD_TRABAJO.md#h-plan-mínimo-de-implementación-y-pruebas).
- [Registro H3 y ensayos del 03/11](investigaciones/2026-10-26_codex_24x7/15_H3_NODO_S23.md).
- [ADR documental congelado](../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md).
- [Trazabilidad histórica del producto](auditorias/2026-10-26/03_TRAZABILIDAD_ARQUITECTONICA.md).
