# Estado para continuar MESTRY

**Lector activo — 08/11/2026:** consentimiento Google completado con scope exacto
`drive.readonly`, raíz MESTRY fijada por ID y token separado del publicador.
Renovación nativa de ambos grants comprobada; token escritor preservado.
**211 pruebas WSL** con fuentes intactas y **68 de candidata S23** correctas.
Primer lote real: 99 elementos descubiertos, texto leído, segunda lectura sin
descarga y copia offline con hash coincidente. Último checkpoint: 3.992 elementos,
7 textos listos y 3.216 trabajos pendientes sin errores. El inventario/caché
siguen incompletos por lotes; trabajador acotado cerrado, sin daemon nuevo. UI S25 pendiente. [Detalle](docs/DOCUMENT_READER_AUTH.md).

**Desarrollo documental — 08/11/2026:** sincronización incremental bajo demanda,
caché durable y recuperación de texto/historial implementados y activados en S23.
196 tests WSL con fuentes intactas y 53 de candidata S23 correctos. Drive real:
inventario/cursor verificados; raíz seleccionada sin documentos visibles. Contenido
real y UI S25 pendientes. H4 avanza parcialmente; H5 no cambia.
[Operación, evidencia y límites](docs/DOCUMENT_SYNC.md).

**Prioridad revisada — 08/11/2026:** RAG queda **PENDIENTE DE REVISIÓN**.
El usuario anticipa poco uso en el producto final; su implementación no se
considera un siguiente paso comprometido. Antes de retomarla, revisar casos de
uso reales y si la lectura/búsqueda directa de archivos ya los resuelve. Esto no
elimina ni modifica el ADR congelado: una eventual exclusión definitiva de RAG
requiere registrar la decisión arquitectónica correspondiente.

**Corte anterior al desarrollo — auditoría del 08/11/2026:** código y nueve suites offline revisados:
163 tests correctos, incluidos cuatro tests de auxiliares locales no versionados.
No es una nueva aceptación de dispositivos. Drive ofrece lectura bajo demanda
y publicación Markdown acotada; **sin sincronización incremental, caché
documental ni RAG**. Último registro de publicación: bloqueada por destino fuera
de Review (03/11), con fixture legible; estado remoto actual no verificado.
[Informe, matriz D/AC e incremento propuesto](docs/DRIVE_IMPLEMENTATION_AUDIT.md).
No se implementó H4/H5 ni se alteraron los cinco cambios locales previos.

## Corte histórico H3 — 04/11/2026

Actualizado: **04/11/2026**. Código/documentación técnica: este repositorio.
Originales seleccionados: Drive según el ADR congelado.

**H3 aceptada para el recorrido solicitado:** revisión Git nueva aplicada por
el bridge y tarea real S25 sobre ese SHA, con concurrencia, terminación y
recuperación fresca del hilo. [Recibo](docs/validation/H3_BRIDGE_ACCEPTANCE_20261104.md) y
[cronología](docs/investigaciones/2026-10-26_codex_24x7/15_H3_NODO_S23.md).

- **Recepción:** `dc3a872a839295e6c4d65ef2b67eab3dcba90f30` → `791688abdd59afb33516916c9e031c94553e02c5` por `session.start`, sin aplicación CLI previa.
- **Validación:** **159 tests por target**; 155 del contrato antes de aplicar
  en ARM64 y cuatro de recibos ejecutados desde S25. Las pruebas históricas
  no sustituyen este candidato.
- **S25:** leyó AGENTS/STATUS reales y HEAD nuevo; BUSY/salida 3 y preview OK
  con índice intacto y sin publicación. Mismo turno `completed`, lock libre,
  reapertura del mismo hilo con `session.content` fresco y recibos recuperados.
- **Final S23:** SHA de aceptación `791688abdd59afb33516916c9e031c94553e02c5`, limpio/libre/idle, validación
  coincidente, sin recuperación ni candidato fallido. La publicación posterior
  del informe y la release instalada son referencias distintas.
- **Correcciones H3:** carga de estado bajo lock en CLI y entrada fetch-only
  del supervisor existente; dos regresiones antes/después. Salida fallida del
  validador conservada privada. Transición explícita de dos controles protegidos,
  con política futura revisada antes de entrar y promoción tras validar/aplicar;
  dependencia nativa anterior conservada y launcher temporal retirado.
- **Cliente:** piloto 9 / 10009 conservado, sin reinstalación. Interrupción complementaria aceptada en otro turno de espera: gesto normal sobre el control dinámico, turno identificado `interrupted`, actividad fresca y cero turnos activos.
- **Incidencias operativas:** recorte de procesos observado el 04/11; se recuperó
  con componentes existentes sin cambiar el límite Android. Las señales del
  03/11 mantienen causa desconocida. Cambio directo de red y disponibilidad
  prolongada conservan sus aceptaciones separadas.
- **Trabajo local preservado:** README/parche/pins Android piloto 9 y dos
  auxiliares Drive. No se incluyeron en los candidatos nativos. Publicarlos
  requiere revisar la transición de fuentes, preservando operativo y rollback.
- **H0/H1/H2:** cierres históricos con límites; flujo y bloqueo cooperativo
  conservados. No se repitió instalación/auditoría.
- **H4/H5:** pendientes, sin implementación aquí. Destino documental,
  autoridades/restore, PC apagado, reinicio y 24/7 no se aceptan por esta prueba.

Siguiente paso: revisar el conjunto Android/pins local y su compatibilidad
nativa antes de integrarlo. Mantener las mejoras de disponibilidad separadas;
no comenzar H4/H5 sin indicación. [Revisión](docs/PROJECT_REVIEW.md),
[roadmap](docs/ROADMAP.md), [sesiones](docs/WORK_SESSIONS.md).
