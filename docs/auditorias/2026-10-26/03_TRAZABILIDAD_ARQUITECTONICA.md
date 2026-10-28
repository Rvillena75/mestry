# MESTRY — Trazabilidad arquitectónica

Fecha: **2026-10-26**. No se alteraron fuentes originales. La evidencia técnica se identifica en [05](05_EVIDENCIAS_Y_PRUEBAS.md); el diagnóstico y riesgos están en [01](01_ESTADO_ACTUAL_MESTRY.md).

## 1. Autoridad y disponibilidad de las seis referencias

MESTRY es el nombre oficial; Jarvis es denominación histórica. No se renombra ni se recrea ninguna fuente ausente. **Solo se localizó una de las seis referencias originales.** Se buscaron nombres exactos en el workspace, proyectos/IPRE y directorios Windows seleccionados, incluido Villevault, con exclusiones documentadas. El conector Drive devolvió búsquedas vacías. Esto significa «no localizado dentro del alcance», no inexistencia global. E02, E13.

| Referencia | Disponibilidad y estado | Propósito y relación verificable | Decisiones que pueden atribuirse |
|---|---|---|---|
| `Proyecto_Jarvis_Ambiental_Etapa_1.md` | **BLOQUEADO / SIN ACCESO**, no localizado | Título referido por el ADR disponible; §26.1 de este último describe la etapa de voz fija | No se reconstruye su contenido. Wake word/STT/respuesta/reposo solo constan como referencia secundaria del ADR Drive |
| `Proyecto_Jarvis_Ambiental_Etapa_2_Personal_Secretary.md` | **BLOQUEADO / SIN ACCESO**, no localizado | Referido en §0.3 y §26.2 del ADR Drive | No se adjudican contratos o prioridades originales; el ADR describe herramientas/memoria/contexto como integración prevista |
| `Proyecto_Jarvis_Ambiental_Etapa_3_Context_Awareness.md` | **BLOQUEADO / SIN ACCESO**, no localizado | Referido en §0.3 y §26.3 del ADR Drive | Solo referencia secundaria a eventos Note20 y percepción local; no se acredita implementación ni se inventa especificación completa |
| `Jarvis_Arquitectura_Congelada_Samsung_Keyboard.md` | **BLOQUEADO / SIN ACCESO**, no localizado | §26.4 del ADR Drive exige compatibilidad con teclado/overlay/app | No se conocen los detalles originales de Keys Cafe, gestos, UI o consentimiento |
| `Jarvis_Free_Model_Broker_Arquitectura_Congelada.md` | **BLOQUEADO / SIN ACCESO**, no localizado | §26.5 y D-14 del ADR Drive conservan un rol de broker separado del acceso Drive | No se asume lista de proveedores/modelos, cuotas ni fallback aprobado en el original |
| [MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md](../../../MESTRY_Arquitectura_Congelada_Google_Drive_Sincronizacion_RAG.md) | **APROBADO / CONGELADO** en decisiones expresas; implementación no presumida | Versión 1.0, fecha 19/10/2026; extiende las cinco referencias sin reemplazarlas. §§1, 20.3, 26 y 29 contienen principios, aceptación, compatibilidad y ADR | D-01–D-15 y ADR normativos; SQLite/FTS5, WorkManager y embeddings distinguidos de decisiones congeladas |

SHA-256 del original disponible: `02dbe7979406b7e8a39b38310842166dbb2c8bc0a4b10736c832ff430d508031`. E03.

## 2. Otros documentos importantes y su función

Los estados siguientes describen la autoridad del documento. Un informe histórico de prueba no convierte su estado en una garantía de funcionamiento actual.

| Documento o conjunto | Propósito / estado | Relación y decisiones relevantes |
|---|---|---|
| [README](../../../README.md) | Índice general con avances y texto histórico; seguimiento con partes desactualizadas | Encabezado aún dice app no instalada; usar H03/H04 para estado posterior. No es autorización universal |
| [DECISIONS](../../DECISIONS.md) | Requisitos, propuestas R2 y autorizaciones por experimento | DEC11: S23 dedicado; DEC12: optimización suficiente, sin más limpieza/reset. P01–P04 conservan propuestas y no se cierran automáticamente por un piloto. Comentarios Markdown dejan de ser requisito del piloto por preferencia humana |
| [ARCHITECTURE](../../ARCHITECTURE.md) | Arquitectura de investigación R2 con avances posteriores | Distribución de responsabilidades y separación entre desarrollo/servicio documental; propuesta Linux condicionada no equivale a aprobación de producto |
| [EXECUTIVE_REPORT](../../EXECUTIVE_REPORT.md) | Síntesis de investigación y límites | Contexto de decisiones y alternativas, no inventario operativo actual |
| [OS_RESEARCH](../../OS_RESEARCH.md) | Evaluación de sistemas/rutas, **PROPUESTO** | No autoriza Windows ARM, flash ni cambio de kernel; leer con EXP04/EXP05 posteriores |
| [CODEX_REMOTE_RESEARCH](../../CODEX_REMOTE_RESEARCH.md) | Investigación de app oficial, app-server y UX | Criterios multiproyecto/continuidad; las frases «app-server no iniciado» pertenecen a su etapa, superada por pilotos posteriores |
| [FRONTEND_AUDIT](../../FRONTEND_AUDIT.md) | Auditoría estática de clientes por commits | Hallazgos de clientes base; no asumir que sus defaults describen el parche desplegado |
| [GOOGLE_DRIVE_RAG](../../GOOGLE_DRIVE_RAG.md) | Diseño documental R2, principalmente **PROPUESTO** | Corpus read-only separado de publicaciones nuevas, metadatos/IDs, feedback y conflictos. Comentarios opcionales por decisión posterior; no demuestra RAG implementado |
| [ANDROID_AGENT](../../ANDROID_AGENT.md) | Investigación y diseño de Device Agent, **PROPUESTO** | Catálogo determinista, separación planner/validador/ejecutor; modelos y permisos no instalados por esta auditoría |
| [ROADMAP](../../ROADMAP.md) | Plan por puertas de validación | No es lista de tareas ya completadas; contrastar con handoffs por fecha |
| [VALIDATION_PLAN](../../VALIDATION_PLAN.md) | Protocolos V00–V13 y avances parciales | No equiparar pruebas EXP/pilotos a cierre de cada V completo. V03 exige más que un proyecto sintético; comentarios V13 no bloquean el piloto actual |
| [EVIDENCE](../../EVIDENCE.md) | Fuentes primarias y evidencia de investigación | «COMPROBADO EN DOCUMENTACIÓN» no significa probado en teléfono; no se revalidaron enlaces web como parte de esta auditoría local |
| [S23_SERVER_AUDIT](../../S23_SERVER_AUDIT.md) | Auditoría histórica read-only del 20/10 | Recursos, inventario y propuestas de limpieza anteriores; las propuestas no autorizan más deshabilitaciones |
| [INSTALLATION_LOG](../../INSTALLATION_LOG.md) | Cronología experimental y recuperación | Diferencia preparación, acciones reales y límites; scripts históricos no deben ejecutarse en bloque |
| [DEBIAN13_MINIMAL_REPORT](../../DEBIAN13_MINIMAL_REPORT.md) | Aceptación mínima histórica Debian, **IMPLEMENTADO Y VERIFICADO** entonces | EXP02; prueba tras reinicio pendiente; no es runtime principal Codex validado por usuario |
| [TERMUX_X11_REPORT](../../TERMUX_X11_REPORT.md) | Ventana/teclado mínimos verificados históricamente | EXP03; no demuestra aplicación oficial Linux ni necesidad de X11 para Horus |
| [CHATGPT_LINUX_ARM64_PLAN](../../CHATGPT_LINUX_ARM64_PLAN.md) | Plan conservado con condición de parada posterior | No ejecutar continuación del plan antiguo tras el bloqueo del sandbox |
| [CHATGPT_LINUX_ARM64_REPORT](../../CHATGPT_LINUX_ARM64_REPORT.md) | Auditoría de paquete; **BLOQUEADO** antes de instalar la app | EXP04: paquete verificado no significa aplicación instalada o renderer probado |
| [CODEX_SANDBOX_REPORT](../../CODEX_SANDBOX_REPORT.md) | Fallo controlado del sandbox en kernel actual documentado | EXP05: no trasladar ese fallo al Codex Horus que funcionó con acceso completo aceptado; tampoco llamarlo aislamiento resuelto |
| [HORUS_REPORT](../../HORUS_REPORT.md) | EXP06, Codex local y fixtures verificados | Horus/Alpine y herramientas ejecutadas en S23; estado remoto inicial apagado fue actualizado después |
| [S25_REMOTE_ACCESS](../../S25_REMOTE_ACCESS.md) | SSH/ProxyJump, migración y tarea remota históricas | Termux 8023 y Horus loopback 8022; no repetir migración ni usar instrucciones antiguas de 8022 como política actual |
| [HORUS_DRIVE_PUBLISH](../../HORUS_DRIVE_PUBLISH.md) | Publicación limitada por revisiones, con cambios posteriores de destino | Dos publicaciones históricas; destino actual no se redirige por asignar otra carpeta en el navegador |
| [DRIVE_S25_HANDOFF](../../DRIVE_S25_HANDOFF.md) | Índice de transferencia con encabezado 22/10 y cronología conservada | Su estado Drive/piloto7 se complementa con piloto8; párrafos OAuth iniciales no prevalecen sobre resultados posteriores |
| [Handoff app r4](../../validation/mestry-s25-resumed-20261021T154810Z/HANDOFF.md) | Resultado de recuperación/interrupción/publicación, histórico | H02; cuenta pruebas reales distintas de tests simulados; no repetir force-stop o cambios de caché durante esta auditoría |
| [Handoff Drive/piloto7](../../validation/mestry-s25-drive-ui-20261021T200418Z/HANDOFF.md) | Último cierre específico de navegador/actividad Drive | H03; raíz asignada, cero documentos autorizados visibles, escritor anterior en papelera, nueva política never/dangerFullAccess |
| [Handoff acceso/piloto8](../../validation/mestry-s23-remote-access-20261022T034500Z/HANDOFF.md) | Último cierre de VPN, celular, watchdog y límites | H04; prevalece para versión APK/acceso. Conserva pendientes 24 h, PC apagado, tarea activa y recuperación tras reinicio |
| [Guía cliente](../../../tools/s25-codex-client/README.md), [broker](../../../tools/horus_publish/README.md), [acceso privado](../../../tools/s23-remote-access/README.md) | Uso y fronteras de pilotos concretos | Código/allowlists no representan todos los contratos de MESTRY Core; guardar alcance de cada herramienta |

## 3. Matriz D-01–D-15: decisión, implementación y evidencia

En todas las filas la decisión normativa es **APROBADO / CONGELADO** por el ADR disponible; la columna Estado se refiere a su realización técnica en el alcance auditado.

| Requisito | Decisión arquitectónica | Implementación real / prueba | Estado técnico | Brecha |
|---|---|---|---|---|
| D-01 | Nombre oficial MESTRY, sin renombrado automático de históricos | Documentos/herramientas nuevos usan MESTRY; originales no renombrados. E01–E03 | **IMPLEMENTADO Y VERIFICADO** documentalmente | Cinco históricos no localizados; no inferir cambio de wake word/paquetes |
| D-02 | Drive autoritativo para originales seleccionados | Tres raíces externas configuradas; piloto Drive con raíz elegida históricamente. E09–E13, H03 | **CONFIGURADO / NO VERIFICADO** integralmente | Falta mapa por ID/cuenta/autoridad y acceso actual |
| D-03 | Core decide; Tool Manager/DriveConnector accede; RAG recupera; persistencia local separada | Broker Termux separado de Horus, catálogo limitado y journal de publicaciones. E05, H03/H06 | **IMPLEMENTADO Y VERIFICADO** como piloto, no arquitectura completa | Core/Tool Manager/RAG integrados no localizados; SQLite del publicador no es catálogo de corpus |
| D-04 | Sincronización selectiva, incremental, sin descargar todo Drive por consulta | Navegador usa metadata/lectura dirigida; rclone/FolderSync operan sobre árboles amplios. E05, E09–E12 | **PENDIENTE** en conector general | No feed `changes` durable ni indexación selectiva encontrada; alinear sincronizadores externos |
| D-05 | Lectura directa cuando conviene; RAG multifuente cuando sea necesario | `drive_browser.py` lista y lee texto/Markdown o exporta texto de Google Docs. Pruebas fake + raíz real histórica. E05–E06, H03 | **IMPLEMENTADO Y VERIFICADO** para navegador acotado | Preview real sobre documentos de nueva raíz pendiente; RAG ausente |
| D-06 | Escritura nativa por APIs estructuradas; no nativos con flujo controlado | Publicador crea revisiones Markdown separadas de un fixture. H06 | **PENDIENTE** para edición por formato | No hay editor general Docs/Sheets/Slides ni actualización controlada de binarios integrada |
| D-07 | LLM propone; controlador independiente valida identidad, autorización y resultado | Receptor fija cuenta/destino/fixture y verifica hashes; broker usa catálogo. E05–E06, H06 | **IMPLEMENTADO Y VERIFICADO** dentro del piloto | Sin Action Controller general ni confirmaciones por acción del producto. El modo YOLO de desarrollo no es esa autorización |
| D-08 | No sobrescribir silenciosamente; detener/reconciliar incertidumbre | Publicador reserva ID/journal y verifica resultado; pruebas de reintento/alteración. E05–E06, H06 | **IMPLEMENTADO Y VERIFICADO** para publicaciones nuevas | No probado para edición concurrente del mismo original ni entre clientes externos; resync rclone merece revisión |
| D-09 | Privilegios mínimos y datos no confiables, sin secretos al LLM | Separación UID Termux/Horus histórica; piloto `drive.file`; config rclone scope `drive`; scanner local acotado sin hallazgos. E05, E09, E14, H03 | **PENDIENTE** aceptación global | Conexiones externas/retención y permiso por archivo sin conciliar; cifrado integral no verificado |
| D-10 | Operación Android S23 sin PC permanente | Herramientas/model harness ejecutadas en S23, prueba de celular e historial frescos. H01/H04 | **PENDIENTE** aceptación | PC físicamente apagado y alimentación/reposo prolongados nunca aceptados |
| D-11 | Recursos limitados; caché/cómputo selectivos | Lecturas de recursos históricas y límites del piloto; sincronizadores copiaron dependencias/build. H01/H05, E10/E12 | **PENDIENTE** | Sin medición actual del servicio documental ni límites globales/corpus |
| D-12 | Fallback explícito, sin falso éxito ni frescura | Broker devuelve unavailable/unsupported y las guías distinguen ausencias. E05–E06 | **PENDIENTE** integralmente | Offline y caché con vigencia del Core no implementados ni aceptados |
| D-13 | MVP pequeño antes de ampliar; sin infraestructura adicional injustificada | Pilotos de fixtures y un proyecto; sin servidor nuevo introducido en auditoría. E04/H01–H04 | **IMPLEMENTADO Y VERIFICADO** como estrategia experimental | MVP asistente ambiental/documental integral aún no aceptado |
| D-14 | Free Model Broker solo si requiere razonamiento; sin acceso privilegiado Drive al proveedor | Codex es herramienta de desarrollo; no se encontró el broker MESTRY | **PENDIENTE** | Recuperar arquitectura original; no presentar login ChatGPT de Codex como Free Model Broker |
| D-15 | Interfaces reutilizan herramientas del mismo Core | Cliente S25 usa broker común acotado; D-03 solo parcial. E05/H03 | **PENDIENTE** para producto | Voz, Samsung Keyboard/overlay y app de producto sin integración compartida demostrada |

ADR-MESTRY-DRIVE-001–007 y 011 recogen los principios congelados anteriores. En §29 **008 (SQLite+FTS5) y 009 (WorkManager) son PROPUESTOS; 010 (embeddings/RAG híbrido) es PENDIENTE**. La elección de SQLite para el journal del publicador no aprueba ni verifica el índice FTS del producto. No se seleccionan librerías o intervalos nuevos en esta auditoría.

## 4. Matriz de componentes funcionales

«No localizado» se refiere al código inspeccionado, no a una búsqueda dentro del almacenamiento privado inaccesible del S23. Las pruebas históricas se distinguen de las actuales.

| Componente | Decisión arquitectónica | Implementación encontrada | Prueba | Estado | Brecha |
|---|---|---|---|---|---|
| Voz / wake word / STT / TTS | Referencia secundaria §26.1; fuente Etapa 1 ausente | No localizada | Ninguna de producto actual | **PENDIENTE**; especificación original **BLOQUEADA / SIN ACCESO** | Recuperar original y luego definir aceptación de voz sin inventar palabra/modelo |
| Samsung Keyboard | §26.4 y D-15; documento específico ausente | No integración encontrada | No se auditó el teclado del teléfono | **BLOQUEADO / SIN ACCESO** para original/dispositivo | Mantener teclado; detalles funcionales sin verificar |
| Keys Cafe | Solicitado por esta auditoría; referencia específica no disponible | No encontrada | Ninguna | **PENDIENTE** | No confundir posible instalación con integración |
| Overlay | §26.4 como interfaz de intención/preview/consentimiento | No localizado | Ninguna | **PENDIENTE** | No equiparar menús de la app piloto a overlay del asistente |
| Aplicación Android | D-15; piloto de desarrollo autorizado históricamente | S25 piloto8, Kotlin/Compose, Java/OkHttp, política/Keystore; fuente local fijada | E04/E06 actuales; instalación/UI H02–H04 históricas | **IMPLEMENTADO Y VERIFICADO**, piloto | No es app final de voz/secretaría ni navegación libre de todos los repositorios |
| MESTRY Core | D-03, D-15 | No localizado | Ninguna | **PENDIENTE** | Contratos, composición y ciclo de vida del producto |
| Intent Router | Referido por arquitectura funcional solicitada; fuente de etapas ausente | No localizado | Ninguna | **PENDIENTE** | No inferirlo del dispatcher RPC del bridge |
| Difficulty Router | Arquitectura funcional solicitada; reglas originales no disponibles | No localizado | Ninguna | **PENDIENTE** | Dataset/política/medición por definir tras recuperar fuentes |
| Orquestador | Responsabilidad Core, D-03 | Solo backend Codex de desarrollo | Pruebas bridge históricas y política local | **PENDIENTE** para MESTRY | Orquestar turnos Codex no prueba herramientas del asistente |
| Contexto / memoria | §5.1 y §26.2 separan memoria operativa de Drive | Historial Codex y estado privado de pilotos | Recuperación histórica H02/H04 | **PENDIENTE** para memoria MESTRY | Conversación persistente no equivale a preferencias/memoria del producto |
| RAG / KnowledgeRetriever | D-04/05, §11 | No índice/chunker/retriever integrado encontrado | Sin evaluación RAG | **PENDIENTE** | Corpus, extracción, citas, invalidación y métricas |
| Reasoning Engine | Papel previsto del razonamiento, D-14 | Codex funciona como herramienta de desarrollo | Tareas sintéticas H01/H02 | **PENDIENTE** como módulo MESTRY | No convertir Codex en motor del producto sin contrato/decisión |
| Free Model Broker | D-14, §26.5; fuente original ausente | No localizado | Ninguna | **PENDIENTE**; original **BLOQUEADO / SIN ACCESO** | No proveedores/quotas/fallback asumidos |
| Tool Manager | D-03/15 | Catálogos limitados del piloto, no manager general | E05/E06 | **PENDIENTE** integración | Contratos comunes y política de herramientas |
| Action Controller / permisos | D-07/08/09 | Publicador fijo y ACL de bridge; validación efectiva de política Codex | E05/E06, H03/H06 | **IMPLEMENTADO Y VERIFICADO** acotado; general **PENDIENTE** | ACL no es sandbox; confirmación y auditoría de acciones del producto pendientes |
| DriveConnector general | §§8, 14, 18 | `drive_browser.py`, publicador y OAuth de piloto | 54 tests actuales fake; raíz/refresh históricos | **PENDIENTE** integralmente | No feed incremental, índice, edición nativa general o corpus admitido |
| Google Calendar | Autoridad propia §5.1 | No integración localizada | Ninguna | **PENDIENTE** | No inferirla de una cuenta Google conectada |
| Canvas | Autoridad propia §5.1 | No integración localizada | Ninguna | **PENDIENTE** | Sin conector/credenciales/contrato comprobados |
| Gmail | Integración solicitada; sin especificación original leída | No integración localizada | Ninguna | **PENDIENTE** | OAuth Drive no acredita autorización Gmail |
| Notas y tareas | §26.2, memoria separada | Solo archivos de prueba/documentación | Ninguna de integración | **PENDIENTE** | Modelo de autoridad y APIs por verificar |
| Device Agent | Diseño en ANDROID_AGENT, no implementación aprobada general | Helpers ADB/UI de diagnóstico en WSL | Pruebas de parser/observación y ensayos históricos | **PROPUESTO** para producto | Un helper host no es agente autónomo Android, ni controla permisos del modelo |
| Servicios del S23 | D-10 y §16 | Termux SSH, Horus, Tailscale, bridge/watchdog históricos | H01–H04; sin acceso hoy | **IMPLEMENTADO Y VERIFICADO**, histórico; hoy **BLOQUEADO / SIN ACCESO** | Boot/UID/PC apagado/24 h |
| Percepción Note20 | §26.3, etapa futura no requerida para Drive | Ningún recurso Note20 inspeccionado | Ninguna | **PENDIENTE** | Fuera del incremento actual; no introducirlo como dependencia |

## 5. Criterios de aceptación del ADR, §20.3

No se cierra un criterio por hallar una biblioteca, aprobar una decisión o superar una API simulada. La siguiente valoración es para el **MVP documental integrado**, no para el mérito de cada piloto.

| Criterio | Evidencia parcial existente | Estado de aceptación actual | Evidencia que falta |
|---|---|---|---|
| AC-01: autorizar al menos un archivo | Fixtures previos y Picker/raíz MESTRY históricos | **CONFIGURADO / NO VERIFICADO** | Archivo vigente identificado, grant real y lectura por la conexión del S23 |
| AC-02: encontrar archivo y metadata | Navegador y metadata/raíz histórica | **CONFIGURADO / NO VERIFICADO** | Documento actual del corpus, ID/cuenta/metadata y UI concordantes |
| AC-03: leer documento y citar origen | Previews con fixtures; dos publicaciones descargadas históricamente | **PENDIENTE** | Documento autorizado→lectura integrada→origen/cita verificables en respuesta |
| AC-04: evitar segunda descarga sin cambio | No se encontró caché documental con prueba correspondiente | **PENDIENTE** | Conteo de solicitudes y revisión/hash sin cambios |
| AC-05: detectar cambio remoto e invalidar índice | Edición de fixture recibida en piloto anterior; no índice incremental | **PENDIENTE** | Cambio en Drive, invalidación de texto y actualización de generación/cursor |
| AC-06: edición reversible autorizada | Creación de nuevas revisiones de un fixture | **PENDIENTE** | Edición controlada del archivo de prueba y reversión; publicación nueva no cierra edición del original |
| AC-07: lectura posterior verifica edición | Readback independiente de publicaciones históricas | **CONFIGURADO / NO VERIFICADO** | Readback de la edición aceptada en AC-06 sobre identidad/revisión actuales |
| AC-08: conflicto rechaza/reconcilia | Pruebas de alteración/idempotencia del publicador | **PENDIENTE** | Carrera real de edición del original sin sobrescritura; no equivale al nombre de una opción sync |
| AC-09: offline comunica caché/ausencia | Errores explícitos del broker; sin flujo offline documental general | **PENDIENTE** | Ensayo sin red con contenido autorizado y estado de antigüedad correcto |
| AC-10: reinicio conserva cursor y no duplica | No cursor de changes integrado ni ensayo de reinicio | **PENDIENTE** | Checkpoint durable, recuperación controlada y no repetición; requiere alcance autorizado |
| AC-11: sin secretos/contenido innecesario en logs | Scanner actual acotado sin hallazgos y minimización histórica | **CONFIGURADO / NO VERIFICADO** | Revisión del flujo MVP completo y logs actuales del dispositivo; scanner no cubre imágenes/todas las formas de secreto |
| AC-12: flujo Android o límites PC explícitos | Procesos S23 y UI S25 históricos; límites PC expresos | **BLOQUEADO / SIN ACCESO** para aceptación actual | Lectura actual en Android; ensayo PC apagado si se reclama independencia operativa |

Balance: **0 criterios cerrados integralmente; 7 PENDIENTES, 4 CONFIGURADOS / NO VERIFICADOS y 1 BLOQUEADO / SIN ACCESO**. Las capacidades históricas no se descartan, pero no se extrapolan a un Core/conector integral ni a disponibilidad actual.

## 6. Discrepancias y precedencia para continuar

| Discrepancia | Evidencia que la resuelve o limita | Acción documental propuesta |
|---|---|---|
| «App pendiente de instalación» en README vs piloto instalado | H02/H03/H04 documentan actualizaciones r4→r7→r8 | Mantener histórico; usar esta auditoría y último handoff al retomar. Actualizar README solo con autorización fuera de los cinco documentos solicitados |
| «Ninguna arquitectura aprobada» R2 vs documento Drive congelado | ADR disponible se declara congelado solo en decisiones expresas; R2 contiene propuestas distintas | No reinterpretar R2 como derogación de D-01–D-15. Registrar alcance/autoridad en próxima revisión, sin editar congelados |
| Corpus read-only/publicaciones versionadas vs bisync bidireccional de árboles | Diseño R2 y D-02/04/08/09 frente a script/BD reales | Evaluar alineación por carpeta; no desactivar ni cambiar sincronización de forma automática |
| Éxito de publicación anterior vs destino actualmente utilizable | H06 prueba éxito; H03 registra papelera por decisión del usuario y escritor sin redirección | No restaurar ni publicar al destino antiguo; aprobar destino vigente de una ampliación |
| Permiso de raíz Drive vs acceso a descendientes | H03 y código validan grants/raíces por archivo; raíz histórica sin documentos visibles | No declarar corpus vacío global ni ampliar scopes por comodidad |
| ACL proyecto vs `dangerFullAccess` de herramientas Codex | Comentario explícito en `pilot-policy.mjs`, código y H03 | Mantener frontera epistemológica: filtrado de RPC/paths no confina shell del agente |
| Supervisor vivo vs autorrecuperación completa | H04 separa salud observada de muerte de UID/reinicio no ensayados | No declarar Boot/24 h por tener un PID o archivo enabled |
| SuperDisplay Stopped histórico vs Running actual | E11 y H03; inicio Auto conservado | Registrar deriva sin atribuir causa ni parar servicios |

Orden de lectura para otra sesión: [01](01_ESTADO_ACTUAL_MESTRY.md) → [02](02_INFRAESTRUCTURA_Y_SINCRONIZACION.md) → este documento → último handoff específico → [04](04_PLAN_DE_CONTINUIDAD.md) y [05](05_EVIDENCIAS_Y_PRUEBAS.md). Las autorizaciones históricas no amplían la fase de auditoría actual ni autorizan reejecutar instaladores, OAuth o migraciones.
