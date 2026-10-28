> Copia pública saneada: datos locales sustituidos por ejemplos. Las decisiones se conservan; el original congelado permanece intacto fuera de Git.

# MESTRY — Arquitectura congelada: Google Drive como nube documental, sincronización incremental, RAG y edición segura

> **Documento de decisión arquitectónica (ADR + especificación funcional/técnica).**  
> **Proyecto vigente:** MESTRY.  
> **Fecha de congelación:** 2026-10-19.  
> **Versión del documento:** 1.0.  
> **Estado:** **CONGELADO en las decisiones de arquitectura indicadas expresamente como tales.**  
> **Estado de implementación:** **NO VERIFICADO / NO SE PRESUME IMPLEMENTADO.**  
> **Alcance:** Integración de Google Drive como fuente documental, índice local, recuperación de conocimiento (RAG), actualización incremental y modificación controlada de archivos.  
> **Prioridad:** Extensión transversal de las capacidades documentales y académicas; no bloquea el MVP de voz de la Etapa 1.  
> **Compatibilidad:** Debe respetar las arquitecturas congeladas anteriores, aunque estas aún utilicen el nombre histórico «Jarvis».

---

## 0. Convenciones, alcance de la congelación y control del cambio

### 0.1. Cambio de nombre

**Decisión aprobada y congelada:** el nombre del **proyecto completo** es ahora **MESTRY**. Desde esta fecha, los nuevos documentos, módulos y planificación del proyecto utilizarán **MESTRY** como denominación principal. No se reescriben ni renombran automáticamente los documentos anteriores: los títulos con «Jarvis» se conservan como referencias históricas inmutables hasta que se autorice una migración documental explícita.

El nombre «Jarvis» puede seguir apareciendo en términos históricos tales como «Jarvis Core», «Jarvis Companion» y la frase vocal «Hey Jarvis» que ya figuran en documentos previos. **No queda aprobada en este documento una sustitución automática de la palabra de activación**, del nombre de una aplicación ya creada ni de identificadores de paquetes existentes. En diagramas nuevos, **MESTRY Core** representa el mismo rol arquitectónico del **Jarvis Core** anterior; es una normalización de nomenclatura, no un segundo núcleo.

### 0.2. Qué significa «congelado»

Quedan congelados **los principios, responsabilidades, límites y comportamientos obligatorios** especificados en las secciones marcadas como decisiones. El detalle de librerías, parámetros numéricos, nombres de clases, rutinas de extracción y calendarios de desarrollo son **propuestas operativas** que se deben validar antes de adoptarse como definitivas, salvo declaración expresa en contrario. Una prueba propuesta no constituye una prueba realizada.

| Etiqueta | Significado |
|---|---|
| **APROBADO / CONGELADO** | Decisión arquitectónica vigente; solo modificable con autorización explícita. |
| **PROPUESTO** | Forma recomendada de implementar una decisión; su adopción definitiva requiere validación técnica. |
| **PENDIENTE** | Falta información o decisión deliberadamente reservada. |
| **NO PROBADO** | No existe evidencia de funcionamiento real y no debe informarse como éxito. |
| **COMPROBADO EN DOCUMENTACIÓN** | Capacidades publicadas por el proveedor; no equivalen a pruebas en el Galaxy S23 Ultra. |

### 0.3. Documento nuevo, sin alteraciones a archivos previos

Este documento **extiende** y **no reemplaza** estas cinco fuentes de verdad anteriores:

1. `Proyecto_Jarvis_Ambiental_Etapa_1.md`.
2. `Proyecto_Jarvis_Ambiental_Etapa_2_Personal_Secretary.md`.
3. `Proyecto_Jarvis_Ambiental_Etapa_3_Context_Awareness.md`.
4. `Jarvis_Arquitectura_Congelada_Samsung_Keyboard.md`.
5. `Jarvis_Free_Model_Broker_Arquitectura_Congelada.md`.

Si surge una contradicción con una decisión anterior congelada, **detener el cambio, registrar la discrepancia y solicitar decisión**. No corregir silenciosamente ninguno de esos cinco documentos.

### 0.4. Estado real a la fecha de congelación

| Elemento | Estado conocido |
|---|---|
| Nombre oficial del proyecto «MESTRY» | **Aprobado por el usuario el 2026-10-19.** |
| Integración Google Drive como fuente documental principal | **Aprobada conceptualmente y congelada por este documento.** |
| Arquitectura híbrida nube + índice local + RAG | **Congelada como diseño.** |
| OAuth de la aplicación MESTRY en Google Cloud | **No verificado.** |
| Código Android del conector, sincronizador o indexador | **No verificado.** |
| Permisos reales de Drive y archivos autorizados | **No verificados.** |
| Pruebas de lectura, edición, concurrencia y latencia | **No realizadas en el contexto de este documento.** |
| Aplicación Android/servicios en producción | **No se afirma que existan.** |

---

## 1. Decisiones arquitectónicas congeladas (resumen normativo)

**D-01. Nombre:** el proyecto se denomina **MESTRY**.

**D-02. Autoridad documental:** **Google Drive** será la fuente de verdad para los **archivos originales seleccionados** que MESTRY administre (apuntes, documentos, recursos académicos y archivos de proyectos). No se declara que Drive sea la fuente de verdad de todas las formas de memoria, tareas, calendario o estado operacional.

**D-03. Separación de responsabilidades:** Drive **almacena documentos**; **MESTRY Core** decide; el **Tool Manager / Drive Connector** accede a la nube; el **motor RAG** recupera evidencia; la **base local** mantiene índice, caché y estado de sincronización. Ninguna interfaz duplica estas responsabilidades.

**D-04. Sincronización selectiva:** **nunca descargar o reindexar todo Drive antes de cada consulta**. Utilizar metadatos locales, cambios incrementales, comprobaciones específicas de vigencia y descargas dirigidas.

**D-05. Directo cuando conviene:** una lectura o búsqueda simple puede resolverse **directamente contra la API de Google Drive/Workspace**; una pregunta semántica multifuente puede usar **índice/RAG local** actualizado.

**D-06. Edición diferenciada por formato:** documentos nativos de **Google Docs, Sheets y Slides** se editan mediante APIs estructuradas cuando la operación sea soportada. Archivos no nativos (por ejemplo `.md`, `.txt`, `.docx`, `.pptx`, `.xlsx`) se editan con flujo controlado de descarga/procesamiento/subida, cuando corresponda.

**D-07. Seguridad del controlador:** un LLM **no escribe directamente** en Drive. Propone una operación estructurada; un controlador independiente valida identidad del archivo, permisos, argumentos, riesgo, alcance, confirmación y resultado.

**D-08. Protección contra sobrescrituras:** verificar versión/estado antes de escribir; preferir controles de revisión nativos cuando existan. Ante conflicto o incertidumbre, **no sobrescribir silenciosamente**; detener, reconciliar o solicitar aprobación.

**D-09. Privacidad:** OAuth con permisos mínimos y selección explícita de documentos/carpetas cuando sea viable; cifrado y retención mínima; contenido obtenido desde Drive tratado como **datos no confiables**, nunca instrucciones superiores al controlador.

**D-10. Independencia del computador:** el diseño de producción debe operar desde Android en el **Galaxy S23 Ultra** sin requerir Windows/WSL2 encendido de manera permanente, sujeto a pruebas reales de Android, conectividad y consumo.

**D-11. Uso eficiente:** indexar solo archivos útiles, actualizar solo los cambiados, limitar caché y cómputo, evitar procesos intensivos persistentes y no reactivar modelos grandes solo para comprobar metadatos.

**D-12. Fallback explícito:** sin conexión, permisos o API disponible, ofrecer información local con señalización de antigüedad; no declarar que una respuesta está actualizada o que una edición se completó si no pudo verificarse.

**D-13. Evolución gradual:** primero un **MVP extremo a extremo**, después sincronización incremental, RAG ampliado y edición multiformato. No introducir servidor permanente, NAS, bases de datos distribuidas, colas remotas o infraestructura adicional sin una necesidad probada.

**D-14. Compatibilidad con el Free Model Broker:** el broker se utiliza solo si la tarea necesita razonamiento; el conocimiento se recupera **antes o durante la preparación del contexto**, y no se entrega acceso privilegiado de Drive al proveedor de LLM.

**D-15. Componentización reutilizable:** voz, Samsung Keyboard + overlay, app Android y futuras interfaces llaman a **las mismas herramientas documentales** del Core; no habrá un conector Drive por interfaz.

---

## 2. Propósito y casos de uso

### 2.1. Objetivo

Dar a MESTRY acceso confiable y eficiente al conocimiento del usuario almacenado en Google Drive para localizar documentos, extraer información, responder preguntas citando fuentes, detectar actualizaciones y ejecutar modificaciones seguras, sin imponer al usuario una sincronización manual constante ni obligarlo a encender su computador.

### 2.2. Ejemplos objetivo

**Consulta focalizada:** «MESTRY, busca el PDF de la guía 4 de Investigación Operativa y resume el ejercicio 2». Comportamiento: localizar el archivo, verificar acceso y versión, recuperar contenido necesario, responder con referencia a archivo y página cuando sea posible.

**Consulta académica multifuente:** «Según mis apuntes de Evaluación de Proyectos, explícame el déficit acumulado máximo». Comportamiento: identificar el curso, recuperar fragmentos de apuntes relevantes con evidencia y generar una explicación contextualizada, sin inventar citas.

**Consulta de estado:** «¿Qué documentos de Gestión de Operaciones cambiaron desde ayer?». Comportamiento: usar bitácora de cambios y metadatos, distinguiendo modificaciones conocidas de periodos no sincronizados.

**Edición nativa:** «Agrega una sección de conclusiones a mi informe de Gestión de Operaciones». Comportamiento: identificar el documento, mostrar la propuesta cuando sea necesario, validar autorización y revisión, ejecutar mediante API estructurada, comprobar el resultado y comunicarlo.

**Edición de código/apuntes Markdown:** «Actualiza el README del proyecto con los pasos de instalación». Comportamiento: descargar solo el archivo elegido, editar una copia de trabajo, contrastar cambios, verificar que no se modificó remotamente, subir una nueva versión y confirmar mediante lectura posterior.

**Modo offline:** «Muéstrame lo que teníamos de descomposición de Benders». Comportamiento: usar fragmentos cacheados si existen y señalar que no se comprobó Drive.

### 2.3. No objetivos

No se busca: sustituir Drive por un sistema de archivos propio; crear un NAS; sincronizar indiscriminadamente todo el almacenamiento personal; convertir el S23 en servidor de archivos general; almacenar contraseñas de Google; exponer el Drive completo a un LLM; hacer scraping de drive.google.com como camino normal; prometer análisis de archivos no soportados; versionar todo un repositorio Git mediante Drive; reemplazar Google Calendar, Canvas, notas estructuradas o SQLite; instalar Windows en el teléfono para conseguir la integración.

---

## 3. Requisitos funcionales y no funcionales

### 3.1. Requisitos funcionales obligatorios

| ID | Capacidad requerida | Criterio observable |
|---|---|---|
| RF-01 | Autorización selectiva | El usuario puede conectar/desconectar una cuenta y conocer permisos concedidos. |
| RF-02 | Descubrimiento | Encontrar documentos por nombre, carpeta, MIME, fecha y contexto autorizado. |
| RF-03 | Metadatos | Conservar ID estable, MIME, URL, revisión/versionado, fechas, permisos y sincronización. |
| RF-04 | Lectura | Obtener contenido de archivos autorizados en los formatos soportados. |
| RF-05 | Indexación | Crear y mantener un índice local de texto por documento y versión. |
| RF-06 | Consulta directa | Responder búsquedas y lecturas concretas sin construir RAG innecesariamente. |
| RF-07 | RAG | Recuperar fragmentos, formar contexto acotado, citar fuentes y abstenerse sin evidencia. |
| RF-08 | Cambios incrementales | Aplicar altas, modificaciones, movimientos, pérdidas de acceso y eliminaciones. |
| RF-09 | Frescura | Indicar al controlador si un documento está vigente, posiblemente desactualizado o desconocido. |
| RF-10 | Edición | Ejecutar escritura autorizada con precondiciones de versión y verificación posterior. |
| RF-11 | Conflictos | Bloquear o resolver explícitamente colisiones, sin sobrescritura silenciosa. |
| RF-12 | Fallos | Recuperarse de red inestable, caducidad de autenticación, límites de API y reinicios. |
| RF-13 | Offline | Responder desde caché identificada como offline, si está disponible. |
| RF-14 | Observabilidad | Mantener registro mínimo del estado y errores sin almacenar contenidos sensibles de más. |
| RF-15 | Borrado local | El usuario puede vaciar caché e índice sin borrar originales de Drive. |
| RF-16 | Independencia | Los resultados son reutilizables desde todas las interfaces de MESTRY. |

### 3.2. Requisitos no funcionales

- **RNF-01 / Integridad:** nunca reportar una escritura como exitosa sin respuesta de API y verificación razonable posterior.
- **RNF-02 / Batería:** no procesar grandes volúmenes en segundo plano mientras el dispositivo está con poca batería; no mantener cargas intensivas innecesarias.
- **RNF-03 / Latencia:** el camino de consulta seleccionará el menor trabajo compatible con el requisito de vigencia.
- **RNF-04 / Privacidad:** los fragmentos académicos solo pueden enviarse a proveedores externos si una política de datos de MESTRY lo permite; preferir minimización y contexto relevante, no archivos completos por defecto.
- **RNF-05 / Tolerancia a fallos:** operaciones cancelables, reintentables de modo seguro y reanudables donde la API lo permita.
- **RNF-06 / Portabilidad:** desacoplar API, almacenamiento, extractor y RAG; desarrollo desde Windows/WSL2 y despliegue Android sin dependencia de un proceso remoto propio.
- **RNF-07 / Transparencia:** explicar qué archivo se usó, cuál era su fecha/versión conocida y si hubo escritura efectiva.
- **RNF-08 / Coste:** privilegiar servicios oficiales, nivel gratuito cuando proceda, indexación local y sin infraestructura recurrente nueva.
- **RNF-09 / Mantenibilidad:** un solo mecanismo de conexión, sincronización e indexación; nada de conectores duplicados por cliente.

---

## 4. Arquitectura lógica definitiva

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                            INTERFACES MESTRY                              │
│ Voz (wake word histórico) | Samsung Keyboard + overlay | App | futuras    │
└───────────────────────────────────┬────────────────────────────────────────┘
                                    │ solicitud y contexto autorizado
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                               MESTRY CORE                                 │
│ Intent Router → Orquestador → controlador independiente de acciones        │
│       │                   │                         │                      │
│       │                   ├── Knowledge/RAG ────────┤                      │
│       │                   │    │                    │                      │
│       │                   ├── Reasoning Engine      │                      │
│       │                   │    └─ Free Model Broker │                      │
│       │                   └── Tool Manager ─────────┤                      │
│       │                                             ▼                      │
│       │                          Drive Connector (una sola instancia       │
│       │                          lógica, independiente de interfaz)       │
│       │                            │        │        │                     │
│       │                       Metadata  Reader  Writer                    │
│       │                            │        │        │                     │
│       │                         Sync Engine / Change Tracker              │
│       │                            │        │                              │
│       │                         Local Index / Cache                       │
│       │                            │        │                              │
│       │                         SQLite + FTS + chunks                     │
└───────┴────────────────────────────┼────────┼──────────────────────────────┘
                                    │ HTTPS oficial + OAuth
                                    ▼
              ┌──────────────────────────────────────────────┐
              │ Google Drive API + Docs/Sheets/Slides APIs   │
              │ Archivos originales y revisiones remotas     │
              └──────────────────────────────────────────────┘
```

**Regla de propiedad:** el Tool Manager es el punto de acceso autorizado a Drive. MESTRY Core controla y valida toda acción. Un resultado RAG es **evidencia**, no una orden. El broker puede elaborar respuestas, pero no es un proceso con credenciales de Google.

### 4.1. Módulos y responsabilidades

| Módulo lógico | Responsabilidad | No debe hacer |
|---|---|---|
| `DriveConnector` | Autenticar y llamar a APIs oficiales bajo contratos tipados | Razonamiento LLM. |
| `DriveCatalog` | Descubrimiento y metadatos de archivos permitidos | Descargar todos los contenidos automáticamente. |
| `DriveChangeTracker` | Gestionar tokens y eventos de cambios incrementales | Decidir por sí mismo qué compartir con un LLM. |
| `DocumentReader` | Obtener o exportar la representación correcta según MIME | Alterar documentos. |
| `DocumentExtractor` | Convertir representaciones en texto + estructura + localizadores | Inventar páginas, celdas o títulos. |
| `DocumentIndexer` | Crear/reemplazar fragmentos y actualizar FTS | Conservar índice caducado tras revocación. |
| `KnowledgeRetriever` | Buscar y ordenar fragmentos con filtros contextuales | Ejecutar instrucciones escritas dentro de documentos. |
| `DriveWriteAdapter` | Aplicar cambios estructurados o cargas versionadas | Sobrescribir archivos en conflicto. |
| `ActionController` | Validar riesgos, permiso, consentimiento, precondiciones y verificación | Delegar permisos al LLM. |
| `SyncScheduler` | Coordinar ejecuciones periódicas oportunistas | Mantener sincronización pesada permanente. |
| `SyncStatus` | Exponer frescura, errores y operaciones pendientes | Afirmar certeza cuando no hay datos. |

### 4.2. Prioridad de ejecución

1. **API oficial de Google** para operación estructurada específica.
2. **Operación local determinista** (buscar metadatos/caché/índice; transformar un archivo local autorizado).
3. **Automatización nativa/específica** cuando una API no alcance y sea legal/técnicamente aceptable.
4. **Automatización visual/de accesibilidad**, solo como respaldo excepcional, frágil y con autorización clara; no debe ser el mecanismo principal de Drive.

La disponibilidad de la **conexión Google Drive de ChatGPT** no significa que el APK de MESTRY herede esas credenciales, permisos o herramientas. El conector propio de MESTRY requiere su propia integración y autorización OAuth apropiada.

---

## 5. Modelo de datos: qué vive en la nube y qué vive en Android

### 5.1. Clasificación por autoridad

| Clase de datos | Fuente de verdad | Réplica/estado local | Observación |
|---|---|---|---|
| Original de un PDF/Word/PPT/Markdown seleccionado | Google Drive | Caché opcional, no autoritativa | No descargar por defecto todo el corpus. |
| Google Doc/Sheet/Slide seleccionado | Google Workspace | Extractos, índice, revisión conocida | La estructura original permanece en Google. |
| Metadatos de archivos autorizados | Google Drive | SQLite, fecha de observación | Pueden quedar obsoletos. |
| Texto procesado, fragmentos RAG | Derivado del original | SQLite/FTS | Regenerable, invalidable. |
| Embeddings (si se adoptan) | Derivado del original | Índice local opcional | No obligatorio en MVP. |
| Estado de sincronización | Cliente MESTRY | SQLite transaccional | Incluye tokens/cursor, sin secretos en logs. |
| Preferencias y memoria operativa de MESTRY | Modelo de persistencia del Core | SQLite u otro backend decidido por Core | **Drive no sustituye esta memoria.** |
| Calendario/tareas/Canvas | APIs propias de cada servicio | Caché según su conector | No duplicar orígenes de verdad. |
| Copias de seguridad de MESTRY | Pendiente de política separada | Exportación opcional | **No usar Drive como backup automático de credenciales.** |

### 5.2. Regla de caché

La caché sirve a tres propósitos: velocidad, operación offline y evitar costos de red. **Nunca constituye autoridad sobre la última versión remota**. Debe poder borrarse y reconstruirse sin afectar los originales. Cada entrada indica `source_revision`, `indexed_at`, `last_checked_at`, `freshness_state`, `access_state` y estado de extracción.

### 5.3. Alcance inicial de Drive

**Decisión congelada:** solo se accede a archivos autorizados y relevantes. **PROPUESTO:** permitir al usuario incorporar documentos/carpetas por selección y etiquetarlos según ramo/proyecto (`evaluacion_proyectos`, `gestion_operaciones`, `investigacion_operativa`, `software`, `otros`). **PENDIENTE:** seleccionar mecanismo definitivo para autorizar una carpeta completa con permisos mínimos y comportamiento correcto en Android; no asumir que `drive.file` habilita lectura automática de todos los descendientes de cualquier carpeta elegida.

---

## 6. Autenticación, cuentas y permisos de Google

### 6.1. Principios congelados

- OAuth 2.0 oficial; **nunca solicitar ni conservar la contraseña de Google**.
- Solicitar únicamente permisos requeridos para la operación vigente.
- Las operaciones de lectura y escritura están separadas por nivel de autorización y por política interna del Action Controller.
- Permitir revocación y desconexión; borrar credenciales locales y material sensible derivado cuando proceda.
- No convertir un token de acceso en instrucción para el LLM, ni transmitirlo a modelos terceros.
- Si una cuenta no tiene permisos sobre un archivo, respetarlo; ni reintentar con cuentas alternativas sin autorización explícita.

### 6.2. Estrategia de scopes

**Preferencia inicial:** `https://www.googleapis.com/auth/drive.file`, que permite trabajar con archivos creados/abiertos/compartidos expresamente con la aplicación, según el flujo de autorización y selección compatible. No permite presumir acceso general a todo el Drive; si el usuario quiere indexar todo su espacio personal, esa decisión exigirá evaluar permisos más amplios, revisión de verificación de Google y política de privacidad.

**Alternativas sujetas a aprobación:** `drive.metadata.readonly` para descubrimiento de metadatos, u otros permisos de lectura/escritura más amplios si una capacidad autorizada los exige. La documentación oficial categoriza ciertos permisos generales como **restringidos**, que pueden conllevar verificación y requisitos de evaluación de seguridad, particularmente en apps públicas. Antes de implementar deben verificarse los scopes concretos y si `drive.file` basta para Docs/Sheets/Slides y para cada operación elegida.

**Regla crítica:** los **scopes OAuth** no equivalen a la **autorización de cada archivo** ni al **permiso del controlador de acciones**. Las tres verificaciones son independientes.

### 6.3. Flujo conceptual de conexión

1. El usuario elige conectar su cuenta de Google desde una interfaz autorizada de MESTRY.
2. MESTRY inicia el consentimiento OAuth oficial mediante el mecanismo de identidad vigente y compatible con Android.
3. Se obtiene un acceso limitado a archivos seleccionados según el alcance aceptado.
4. MESTRY consulta la identidad de cuenta y registra un identificador local no secreto de conexión.
5. Al solicitar un archivo, se validan acceso real, `capabilities.canDownload`, `capabilities.canEdit` y permisos requeridos según operación.
6. Los tokens se gestionan de forma segura siguiendo recomendaciones vigentes; se evita su volcado a archivos de diagnóstico.
7. Ante revocación, se bloquean nuevas acciones y se invalidan datos derivados conforme a la política de retención.

**PENDIENTE:** seleccionar la biblioteca de autorización Android más adecuada, identificar el flujo de Google Picker o selector alternativo, revisar sus limitaciones de UI y confirmar comportamiento con Android/One UI del S23. No se declara resuelto por el hecho de existir un conector Drive conectado en ChatGPT.

### 6.4. Protección de credenciales

Aplicar almacenamiento seguro con controles del sistema Android y, cuando corresponda, Android Keystore. Nunca incluir credenciales en SQLite, archivos Markdown, registros, prompts, repositorios ni copias sincronizadas por Drive. Cifrar contenidos sensibles en reposo según evaluación de amenaza, usar HTTPS/TLS para tránsito y restringir permisos del proceso Android.

---

## 7. Descubrimiento de archivos: sin descargas innecesarias

### 7.1. Identidad primaria

Usar como clave de documento el **ID estable de Google Drive** más identidad de cuenta/corpus, no el nombre ni la ruta. Los nombres son ambiguos y una operación de mover/renombrar no debe duplicar el documento. Las rutas se reconstruyen a partir de metadatos y parent IDs cuando estén disponibles y autorizados.

### 7.2. Campos mínimos de metadatos

`id`, `name`, `mimeType`, `parents`, `modifiedTime`, `version`, `size` cuando aplique, `md5Checksum` para archivos binarios cuando esté disponible, `webViewLink`, `description`, `trashed`, `capabilities.canDownload`, `capabilities.canEdit`, fecha de observación y estado de acceso. Agregar metadatos de revisiones específicas por API nativa si se requieren para escritura.

**Advertencia:** `md5Checksum` de Drive **solo se aplica a archivos binarios**. **No usar MD5 de Drive como detector de cambios en Google Docs/Sheets/Slides**. Las revisiones de Docs y otros servicios tienen semánticas diferentes. `modifiedTime` y `version` son señales útiles, pero la corrección de una escritura exige precondiciones específicas del formato y nueva lectura cuando corresponda.

### 7.3. Selección y búsqueda

- Buscar primero por ID almacenado o por catálogo local cuando la intención sea precisa.
- Si no existe índice suficiente, usar `files.list` de Drive con filtros `q`, `fields` y `pageToken`; no recuperar grandes respuestas con campos innecesarios.
- Para búsquedas complejas, reconocer que `fullText contains` de Drive **no es RAG** y tiene semánticas de tokenización/consulta distintas de una búsqueda vectorial; no sustituye a la extracción profunda y búsqueda por pasajes.
- Limitar resultados a archivos dentro del corpus autorizado; pedir desambiguación si hay dos archivos plausibles y escribir implicaría riesgo.
- Identificar y manejar accesos directos de Drive sin crear ciclos ni editar el objetivo equivocado.
- No afirmar que todo Drive fue indexado cuando únicamente se autorizaron algunos archivos.

---

## 8. Sincronización incremental: núcleo del diseño

### 8.1. Distinción fundamental

**Comprobar cambios no equivale a descargar contenidos.** El sincronizador procesa eventos y metadatos; solo actualiza el contenido local de documentos seleccionados y relevantes para la búsqueda, consultas o caché.

### 8.2. Mecanismo oficial

Google Drive API v3 proporciona `changes.getStartPageToken` y `changes.list`. Este registro devuelve el **estado actual** de archivos modificados desde el cursor, **no un parche textual entre revisiones**. Cuando `changes.list` devuelve `nextPageToken`, faltan páginas; el cursor de sincronización estable debe consolidarse solo después de procesarlas. `newStartPageToken` aparece al completar el lote y se utiliza como base de sincronizaciones posteriores.

### 8.3. Arranque inicial sin ventanas de pérdida

El arranque debe tolerar cambios que ocurren **durante** el escaneo. **Secuencia propuesta:**

1. Validar OAuth, cuenta y corpus autorizado.
2. Solicitar `changes.getStartPageToken` y guardar un token **provisional anterior al escaneo**.
3. Enumerar metadatos de documentos autorizados; construir catálogo inicial bajo una transacción/etapa controlada.
4. Procesar los cambios desde el token provisional, paginando con `changes.list` hasta recibir el token de inicio nuevo.
5. Aplicar eventos y repetir una verificación/conciliación si el corpus cambió durante el bootstrap.
6. Confirmar un **checkpoint durable** del cursor solo tras aplicar los cambios y estados locales previstos.
7. Marcar estado `READY`, `PARTIAL` o `DEGRADED` conforme a lo realmente cubierto.

No debe asumirse que el registro contiene todos los documentos históricos: por eso existe el catálogo inicial. Tampoco debe inventarse soporte de carpetas recursivas bajo `drive.file`; verificar el conjunto efectivamente visible. Si la API limita resultados por scopes, reflejar esa limitación.

### 8.4. Ciclo incremental normal

```text
[Inicio programado o demanda de frescura]
       │
       ▼
[¿Hay red + cuenta válida + permiso suficiente?]
       ├── NO → marcar DEGRADED, conservar último cursor confirmado
       └── SÍ
             │
             ▼
     changes.list(pageToken = cursor_confirmado)
             │
             ▼
     Aplicar todos los eventos de la página
             │
             ├── Archivo nuevo: registrar, extraer según política
             ├── Modificado: marcar contenido/índice como STALE
             ├── Renombrado/movido: actualizar catálogo
             ├── Eliminado/trashed: invalidar índice, aplicar retención
             └── Permiso revocado/removido: no seguir exponiendo contenido
             │
             ▼
   ¿nextPageToken?
             ├── SÍ → procesar página siguiente
             └── NO → persistir newStartPageToken y checkpoint
             │
             ▼
     Programar extracción solo para elegibles
```

### 8.5. Persistencia y atomicidad

- No adelantar el cursor durable más allá de cambios cuya aplicación local esté comprometida.
- Separar «evento procesado e índice invalidado» de «contenido nuevamente descargado»: es correcto adelantar el cursor si la invalidación quedó **durablemente** registrada y la reindexación pendiente está en una cola durable.
- Ante caída a mitad de página, reintentar sin duplicar ni revertir eventos ya aplicados; operaciones sobre catálogo y cola deben ser **idempotentes**.
- Distinguir estado de sincronización por cuenta/corpus, y por unidad compartida si en el futuro se soportan Shared Drives.
- Si el conjunto de scopes o archivos seleccionados cambia, ejecutar reconciliación y bootstrap del nuevo alcance; no suponer que el cursor anterior cubre nuevos archivos autorizados.
- Tratar pérdida de acceso como revocación de visibilidad: invalidar búsquedas y copias derivadas conforme a política de seguridad.
- Si ocurre un error irrecuperable de token/cursor, reconstruir catálogo y recuperar un nuevo punto de partida con una estrategia que no pierda cambios.

### 8.6. Notificaciones push: fuera del MVP

`changes.watch` puede avisar de cambios, pero requiere receptor **HTTPS públicamente accesible** y gestión de canales con expiración. La notificación no entrega el contenido cambiado: exige de todos modos usar el feed. Para un S23 que opera sin servidor propio y busca bajo mantenimiento, **no integrar webhooks/push inicialmente**. **PENDIENTE DE MEDICIÓN:** incorporarlos solo si polling oportunista + verificaciones bajo demanda no satisfacen el objetivo de frescura.

### 8.7. Carpetas, permisos y unidades compartidas

Los cambios pueden reflejar renombramientos, movimientos, eliminaciones y modificaciones de acceso. No todos los cambios observables corresponden necesariamente a contenidos que la aplicación tiene derecho a leer. Para Shared Drives hay registros y parámetros específicos; **no se incluye soporte completo de Shared Drives en el MVP**. Si se añade, deberán administrarse sus propios tokens y reglas de permisos, sin mezclar indiscriminadamente las secuencias.

---

## 9. Frescura bajo demanda: política antes de cada respuesta

### 9.1. Clasificación

| Clase | Ejemplo | Comportamiento |
|---|---|---|
| `FRESH_REQUIRED` | «¿Qué dice la última versión?», «edita este informe ahora» | Revalidar archivo concreto o conjunto limitado **antes** de usarlo; para escribir, revisión obligatoria. |
| `FRESH_PREFERRED` | «Según mis apuntes…» | Revisar cambios si el costo es razonable; si falla, usar índice con aviso de antigüedad. |
| `CACHE_ACCEPTABLE` | «Explícame Benders con mis notas guardadas» | Puede usar caché versionada y mostrar fecha de actualización. |
| `LOCAL_ONLY` | Sin conexión / modo privado | No acceder a Drive ni al cloud; responder solo con datos locales y avisar limitación. |

### 9.2. Algoritmo de consulta

1. Interpretar intención y el requisito de frescura.
2. Seleccionar posibles documentos por curso, tema, nombre, IDs y corpus permitido.
3. Si hay suficientes metadatos locales, filtrar sin red innecesaria.
4. Revalidar versiones de los documentos **candidatos** cuando la política lo exija, o consultar cambios incrementales en el corpus pertinente.
5. Si una fuente cambió, invalidar los fragmentos antiguos **antes de considerarlos vigentes**.
6. Descargar/procesar solo archivos necesarios, con límites de tamaño y timeouts.
7. Recuperar pasajes y construir respuesta.
8. Adjuntar estado de frescura, referencia y fecha/versiones conocidas.

### 9.3. Nunca prometer «tiempo real» en abstracto

La sincronización periódica de Android puede sufrir retrasos por batería, Doze, conectividad y cuotas. «Actualizado» significa **confirmado a la hora declarada**. Si la comprobación no se realizó, la respuesta debe decirlo.

### 9.4. Ejemplo de decisión

```text
Consulta: "¿Dónde está la presentación de la clase 5?"
→ DriveCatalog / files.list si es necesario, sin LLM ni descarga.

Consulta: "¿Qué argumento usa esa presentación?"
→ DocumentReader + extractor del archivo elegido.

Consulta: "Compara los criterios de dos cursos según mis guías"
→ Cambios incrementales + índice local + RAG + broker si es necesario.

Consulta: "Agrega una tabla a ese documento"
→ Resolución de identidad + control de riesgo + adapter estructurado.
```

---

## 10. Lectura y extracción por formato

### 10.1. Despacho MIME

| Tipo | Lectura preferida | Escritura preferida | Riesgos |
|---|---|---|---|
| Google Docs | API Docs para estructura; exportación si conviene | `documents.batchUpdate` | Índices, estilos, colaboración, revisiones. |
| Google Sheets | API Sheets por rangos/metadatos | `spreadsheets.values.*` / `spreadsheets.batchUpdate` según operación | Fórmulas, celdas protegidas, formatos. |
| Google Slides | API Slides para elementos | `presentations.batchUpdate` | Diseño, posición y estructura compleja. |
| PDF binario | Drive `files.get(alt=media)` y extracción local | Generalmente copia editada/archivo nuevo | Escaneos, OCR, gráficos y firma digital. |
| `.md`, `.txt`, `.json`, `.csv` | Descarga binaria y parsing | Edición local + actualización versionada | Codificación, saltos de línea, esquema, concurrencia. |
| `.docx`, `.xlsx`, `.pptx` | Descarga binaria y parser adecuado | Edición local conservando formato + actualización | Integridad de formato, macros, relaciones internas. |
| Imagen/audio/video | Solo cuando exista herramienta y autorización | Fuera del MVP documental | Consumo, privacidad, OCR/transcripción. |

Las exportaciones de archivos **nativos Google Workspace** mediante `files.export` tienen límites publicados por Google (actualmente **10 MB por exportación**). Para documentos grandes deben verificarse opciones de API por estructura/descarga apropiada; **no asumir que una exportación limitada entrega un documento completo**.

### 10.2. Normas de extracción

- Guardar contenido normalizado **junto a un localizador verificable**: documento, sección, página, diapositiva, hoja/rango o encabezado, según el formato y lo realmente extraíble.
- Conservar relaciones útiles: tabla, encabezados, listas, jerarquía de secciones y orden.
- Para PDF, distinguir **página física** de numeración impresa. Si la extracción no permite identificar página, citar el archivo sin inventarla.
- No enviar el archivo íntegro al LLM si basta recuperar fragmentos.
- Los escaneos que necesiten OCR quedan marcados `NEEDS_OCR`; OCR será una extensión evaluable por calidad/costo, no requisito del MVP.
- Respetar límites de archivo y memoria: descartar caché temporal tras procesar y evitar cargas completas en RAM cuando sea posible.
- El extractor se identifica por versión (`extractor_version`) para reindexación dirigida cuando cambie la lógica.

### 10.3. Formatos no soportados

Responder con limitación explícita y, si la lectura es relevante, ofrecer abrir el original con la aplicación correspondiente. **No fabricar un resumen del contenido no leído.**

---

## 11. RAG documental y búsqueda académica

### 11.1. Reglas congeladas

RAG se usa cuando la pregunta depende de documentos propios; no ante toda pregunta general. El **Intent Router** decide si requiere material del usuario; **KnowledgeRetriever** encuentra evidencia; el **Free Model Broker**, cuando sea necesario, razona **sobre fragmentos seleccionados**, respetando la política de salida de información.

### 11.2. Índice inicial

**PROPUESTO para el primer incremento académico:** SQLite con **FTS5** para búsqueda lexical por texto, título, encabezado, ramo, tipo y metadatos. Evitar implementar embeddings desde el primer día si las consultas reales pueden satisfacerse con FTS y ranking sencillo.

**PROPUESTO para una segunda iteración:** embeddings locales o proveedor permitido de embeddings, y recuperación híbrida lexical + semántica con reranking acotado. Debe justificarse por benchmarks en consultas reales; no se adopta un servicio vectorial remoto por defecto.

### 11.3. Chunking

- Fragmentar por estructura semántica (títulos, secciones, párrafos, diapositivas, filas/rangos), no por bytes arbitrarios.
- Dividir fragmentos grandes según límites de tokens configurables; mantener solapamiento solo si mejora recuperación medida.
- Asociar cada `chunk` a `(account_id, file_id, source_revision, extractor_version, chunk_index)` y localizador de origen.
- Conservar un hash local del texto extraído si es útil para detectar duplicados/reprocesamiento; no confundirlo con `md5Checksum` remoto.
- Reemplazar en bloque fragmentos de una versión antigua para impedir mezclar citas de revisiones distintas.

### 11.4. Recuperación y construcción de contexto

```text
Intención: requiere documentos del usuario
  → resolver curso/carpeta/archivo permitido
  → comprobar frescura según política
  → buscar candidatos en FTS + metadatos
  → (opcional) búsqueda semántica / reranking
  → seleccionar pasajes distintos, pertinentes y actuales
  → construir contexto con fuente, revisión y localizador
  → Reasoning Engine / broker cuando se requiera
  → validar fidelidad de citas
  → respuesta con enlaces/ubicaciones
```

### 11.5. Respuestas y citación

- Incluir nombre y enlace del archivo original cuando se conozca `webViewLink` y esté permitido.
- Preferir «Documento X, sección Y / página P» si el localizador es confiable.
- Diferenciar claramente cita textual breve, resumen e inferencia del modelo.
- Si las fuentes no bastan o hay contradicciones, informar la limitación y evitar crear contenido no sustentado.
- No citar un documento revocado ni un chunk invalidado como si estuviera vigente.
- La fecha de sincronización forma parte del estado de la respuesta cuando es relevante.

### 11.6. Riesgos de prompt injection

Todo contenido documental puede contener textos del tipo «ignora instrucciones anteriores» o «envía este archivo a …». Estos son **datos no confiables**. Jamás obtienen permiso de acceso, escritura, envío o modificación. Los datos de RAG viajan por un canal delimitado de contexto, sin autoridad de sistema o desarrollador.

---

## 12. Edición segura: flujo general obligatorio

### 12.1. Política de autorización

| Acción | Tratamiento general |
|---|---|
| Buscar y leer archivo autorizado | Normalmente ejecutable sin confirmación adicional, sujeto a permisos y contexto. |
| Crear un archivo nuevo en carpeta expresamente autorizada | Operación reversible; confirmar si la intención/ubicación es ambigua o según preferencias. |
| Modificar documento existente | Mostrar preview/diff cuando el cambio no sea trivial; confirmar si la política o el riesgo lo exige. |
| Compartir un documento, cambiar permisos o publicarlo | **Confirmación explícita previa obligatoria.** |
| Eliminar definitivamente, vaciar papelera, destruir revisiones | **Confirmación explícita previa obligatoria**; fuera del MVP. |
| Exfiltrar datos mediante correo/web/terceros | **Confirmación explícita previa obligatoria** y minimización de datos. |

Ningún texto presente dentro de un archivo constituye consentimiento para ejecutar acciones.

### 12.2. Pipeline de escritura

1. Resolver inequívocamente la identidad del archivo y su cuenta.
2. Comprobar que sigue dentro del corpus autorizado y que `canEdit` u otra capacidad exigida está disponible.
3. Leer versión/revisión actual y contenido/estructura necesario.
4. Proponer cambio estructurado con alcance limitado; mostrar preview/diff o resumen según riesgo.
5. Obtener confirmación explícita cuando corresponda, **antes de la ejecución**.
6. Revalidar la revisión justo antes de escribir y aplicar precondición de concurrencia cuando la API la soporte.
7. Ejecutar operación única y recuperable; idempotencia en el cliente cuando sea posible.
8. Leer o consultar el resultado y verificar que el objetivo quedó aplicado (no solo HTTP 200 genérico).
9. Invalidar o reindexar el documento afectado; actualizar catálogo y estado local.
10. Informar éxito únicamente tras verificación; de lo contrario, comunicar estado desconocido/pendiente/error.

### 12.3. Edición nativa Google Docs

**Preferir** `documents.batchUpdate` con operaciones pequeñas y bien localizadas, no exportar a `.docx` y sobrescribir todo el Google Doc. Emplear `WriteControl.requiredRevisionId` cuando sea posible: si la revisión ya no es la actual, Google rechaza el cambio; MESTRY debe releer y reconciliar. `targetRevisionId` tiene otra semántica de colaboración y no debe utilizarse indiscriminadamente como reemplazo de la comprobación estricta.

Los índices y rangos estructurales de Docs pueden cambiar entre lectura y escritura; construir solicitudes a partir de la estructura más reciente. Nunca afirmar edición correcta sin verificar el fragmento insertado/modificado.

### 12.4. Edición nativa Google Sheets

Preferir operaciones por rangos/celdas y cambios mínimos. Inspeccionar si existen fórmulas, celdas protegidas, validaciones y formatos antes de modificar. Un documento de cálculo no debe reemplazarse por CSV si se busca conservar su estructura. La política específica de concurrencia/validación dependerá de las capacidades verificadas de la API elegida; se requiere lectura/confirmación antes y después en el MVP.

### 12.5. Edición nativa Google Slides

Usar solicitudes estructuradas al API de presentaciones para textos/elementos puntuales. Cambios visuales complejos exigen lectura de estructura y verificación; la renderización/revisión visual puede requerir herramientas adicionales. **No prometer fidelidad visual perfecta sin pruebas.**

### 12.6. Edición de archivos no nativos

```text
Resolver fileId, metadatos y estado
      ↓
Descargar versión autorizada a temporal privado
      ↓
Validar extensión, contenido, parser y tamaño
      ↓
Editar una copia; generar diff/revisión previa
      ↓
Confirmación apropiada
      ↓
Reconsultar metadatos/revisión remota
      ↓
Si cambió: detener o reconciliar (no sobrescribir)
      ↓
Subir nueva versión del MISMO fileId cuando sea seguro
      ↓
Verificar contenido / hash apropiado / metadatos / versión
      ↓
Actualizar índice local y limpiar temporales
```

Para archivos grandes o red inestable, evaluar `uploadType=resumable`. En archivos binarios pueden utilizarse hash del archivo descargado, bytes resultantes y metadata remota para verificaciones; **un chequeo de metadatos antes de subir no garantiza por sí solo una escritura atómica frente a modificaciones concurrentes**. Mientras no exista una precondición remota fiable para ese tipo de operación, el comportamiento seguro es **serializar en MESTRY, minimizar ventana de carrera y ante alto riesgo crear copia/versionado en lugar de sobrescribir**. La política concreta de escritura condicional debe validarse contra el endpoint seleccionado; no suponer soporte universal de `If-Match` para Drive v3.

### 12.7. Prevención de duplicados

Cada solicitud de acción posee `operation_id` local; se registra estado `PREPARED`, `AWAITING_CONFIRMATION`, `EXECUTING`, `VERIFYING`, `COMMITTED`, `FAILED` o `UNKNOWN`. Un timeout después de un envío no autoriza a repetir ciegamente una inserción o un archivo nuevo: **primero comprobar si ya ocurrió**.

### 12.8. Manejo de conflicto

Ante una revisión inesperada, archivo movido fuera del alcance, permisos revocados, cambio de identidad o datos incompatibles: bloquear la escritura; mantener en memoria temporal un diff local si es seguro; ofrecer refrescar propuesta, crear una copia con consentimiento o cancelar. Nunca aceptar tácitamente «última escritura gana».

---

## 13. Persistencia local: propuesta de esquema mínimo

**Decisión congelada:** MESTRY mantiene **estado local compacto, transaccional y reconstruible**; no utiliza Drive como base operacional. **PROPUESTO:** SQLite como motor único de persistencia para metadatos, sincronización, índices y colas locales. En Android puede utilizarse Room, sujeto a integración con la arquitectura efectiva del repositorio.

### 13.1. Entidades

| Entidad | Campos de diseño | Finalidad |
|---|---|---|
| `accounts` | `account_id`, `provider`, `display_label`, `auth_state`, `connected_at` | Cuenta conectada sin secretos en BD. |
| `corpora` | `corpus_id`, `account_id`, `name`, `selection_mode`, `state`, `created_at` | Espacios académicos/proyectos explícitamente autorizados. |
| `corpus_files` | `corpus_id`, `file_id`, `added_at`, `access_policy` | Asociación N:M entre corpus y archivo. |
| `drive_files` | `account_id`, `file_id`, `name`, `mime_type`, `parent_id`, `modified_time`, `version`, `md5_checksum`, `web_url`, `capabilities`, `catalog_state`, `last_checked_at` | Catálogo de metadatos. |
| `content_snapshots` | `account_id`, `file_id`, `source_revision`, `extractor_version`, `indexed_at`, `freshness`, `bytes_cached`, `index_state` | Versionado de contenido procesado. |
| `document_chunks` | `chunk_id`, `file_id`, `source_revision`, `location_json`, `text`, `hash`, `token_count` | Fragmentos recuperables con trazabilidad. |
| `document_fts` | Índice FTS5 sincronizado de `document_chunks` | Recuperación textual local. |
| `sync_checkpoints` | `account_id`, `corpus_id/drive_id`, `committed_page_token`, `last_success`, `state`, `last_error` | Checkpoints durables por fuente. |
| `pending_jobs` | `job_id`, `type`, `file_id`, `priority`, `required_revision`, `attempts`, `state`, `created_at` | Trabajos idempotentes de extracción/sincronización. |
| `action_operations` | `operation_id`, `intent`, `file_id`, `risk`, `approval_state`, `expected_revision`, `result_state`, `verification_at` | Auditoría mínima y prevención de duplicados. |
| `app_settings` | `key`, `value`, `updated_at` | Límites, modos de sincronización y preferencias. |

### 13.2. Esquema ilustrativo (no migración lista para ejecutar)

El siguiente SQL es **referencial**; los campos exactos, claves compuestas y tipos deberán ajustarse tras revisar el código existente. No contiene esquema de credenciales ni contenido sensible por defecto.

```sql
CREATE TABLE drive_files (
  account_id       TEXT NOT NULL,
  file_id          TEXT NOT NULL,
  name             TEXT NOT NULL,
  mime_type        TEXT NOT NULL,
  parent_id        TEXT,
  remote_version   TEXT,
  modified_time    TEXT,
  md5_checksum     TEXT,
  web_url          TEXT,
  can_download     INTEGER NOT NULL DEFAULT 0,
  can_edit         INTEGER NOT NULL DEFAULT 0,
  catalog_state    TEXT NOT NULL DEFAULT 'DISCOVERED',
  last_checked_at  TEXT,
  PRIMARY KEY(account_id, file_id)
);

CREATE TABLE content_snapshots (
  account_id        TEXT NOT NULL,
  file_id           TEXT NOT NULL,
  source_revision   TEXT NOT NULL,
  extractor_version TEXT NOT NULL,
  indexed_at        TEXT,
  freshness_state   TEXT NOT NULL DEFAULT 'UNKNOWN',
  index_state       TEXT NOT NULL DEFAULT 'PENDING',
  PRIMARY KEY(account_id, file_id),
  FOREIGN KEY(account_id, file_id)
    REFERENCES drive_files(account_id, file_id)
);

CREATE TABLE document_chunks (
  chunk_id         TEXT PRIMARY KEY,
  account_id       TEXT NOT NULL,
  file_id          TEXT NOT NULL,
  source_revision  TEXT NOT NULL,
  ordinal          INTEGER NOT NULL,
  locator_json     TEXT,
  content_text     TEXT NOT NULL,
  local_sha256     TEXT
);

CREATE TABLE sync_checkpoints (
  account_id          TEXT NOT NULL,
  scope_id            TEXT NOT NULL,
  committed_page_token TEXT,
  last_success_at     TEXT,
  sync_state          TEXT NOT NULL DEFAULT 'UNINITIALIZED',
  last_error_code     TEXT,
  PRIMARY KEY(account_id, scope_id)
);

CREATE TABLE pending_jobs (
  job_id            TEXT PRIMARY KEY,
  account_id        TEXT NOT NULL,
  file_id           TEXT,
  job_type          TEXT NOT NULL,
  expected_revision TEXT,
  state             TEXT NOT NULL DEFAULT 'QUEUED',
  retries           INTEGER NOT NULL DEFAULT 0,
  created_at        TEXT NOT NULL
);
```

**Restricción de integridad importante:** `document_chunks` nunca debe participar en recuperación como vigente si `source_revision` difiere de la versión indexada vigente o el acceso está revocado. Las versiones anteriores podrán conservarse temporalmente para recuperación si una política explícita lo permite, pero deben quedar fuera del índice consultable normal. Para texto cifrado local se debe evaluar un mecanismo compatible con búsquedas y la política de seguridad real: **no asumir que SQLite estándar cifra datos en reposo**.

### 13.3. Política de limpieza

**PROPUESTO:** caché de trabajo con presupuesto configurable, expulsión LRU de binarios y preservación preferente de metadatos/chunks recientes, salvo revocación. El límite exacto en MB/GB es **PENDIENTE** de medir en el S23 y de la cantidad de material académico. Los documentos completos descargados para operaciones temporales deben eliminarse después de verificar, salvo selección expresa de modo offline.

---

## 14. Contratos internos del Drive Connector

Los siguientes contratos son **interfaces conceptuales** y no implican que ya existan clases con esos nombres. Su misión es permitir reemplazar SDK, API client, extractor o RAG sin alterar MESTRY Core.

```kotlin
// PSEUDOCÓDIGO DE DISEÑO: no se declara compilable.
interface DriveConnector {
    suspend fun searchFiles(query: FileSearchQuery): Result<List<RemoteFile>>
    suspend fun getMetadata(fileId: String): Result<RemoteFile>
    suspend fun getContent(fileId: String, mode: ReadMode): Result<DocumentData>
    suspend fun getChanges(cursor: String): Result<ChangesPage>
    suspend fun applyWrite(request: ValidatedWriteRequest): Result<WriteReceipt>
}

interface DocumentExtractor {
    suspend fun extract(input: DocumentData): ExtractionResult
}

interface DocumentIndexer {
    suspend fun replaceSnapshot(snapshot: ExtractedSnapshot): IndexResult
    suspend fun invalidate(accountId: String, fileId: String): Unit
}

interface KnowledgeRetriever {
    suspend fun retrieve(request: RetrievalQuery): RetrievalResult
}

interface ActionController {
    suspend fun authorize(request: ProposedAction): AuthorizationDecision
    suspend fun verify(receipt: WriteReceipt): VerificationResult
}
```

### 14.1. Tipos canónicos propuestos

```json
{
  "RemoteFile": {
    "account_id": "account_alias",
    "file_id": "drive_file_id",
    "name": "Guia_04.pdf",
    "mime_type": "application/pdf",
    "remote_revision": "opaque-version-or-revision",
    "web_view_url": "remote-url-if-authorized",
    "can_read": true,
    "can_edit": false,
    "last_observed_at": "RFC3339 timestamp"
  },
  "RetrievedPassage": {
    "file_id": "drive_file_id",
    "source_revision": "opaque-version-or-revision",
    "locator": {"type": "pdf_page", "value": 7},
    "text": "Extracto obtenido del documento",
    "freshness": "VERIFIED|CACHED|STALE|UNKNOWN"
  }
}
```

### 14.2. Contrato de escritura propuesto

```json
{
  "tool": "drive.edit_document",
  "operation_id": "stable-opaque-id",
  "account_id": "authorized-account",
  "file_id": "authorized-drive-file-id",
  "expected_revision": "revision-read-before-proposal",
  "edit_type": "insert_section",
  "payload": {
    "heading": "Conclusiones",
    "body": "Texto de propuesta validado"
  },
  "risk": "REVERSIBLE_WRITE",
  "approval": {
    "required": true,
    "granted_for_this_action": false
  }
}
```

**Validaciones obligatorias:** los IDs se resuelven contra el catálogo autenticado, la acción debe pertenecer a un conjunto permitido (allowlist), los argumentos deben respetar un esquema estricto, `operation_id` evita duplicados y la confirmación solo cubre la operación mostrada. Un JSON generado por un LLM **no implica autorización**.

### 14.3. Herramientas conceptuales del Tool Manager

- `drive.search_files(filter)`.
- `drive.get_file_metadata(file_id)`.
- `drive.read_document(file_id, range_or_section)`.
- `drive.list_recent_changes(corpus_id, since)`.
- `knowledge.retrieve(query, corpus_id, freshness_policy)`.
- `drive.propose_edit(file_id, operation)`.
- `drive.commit_edit(approved_proposal_id)`.
- `drive.create_file(parent_id, mime_type, proposed_content)`.
- `sync.refresh_file(file_id)` y `sync.refresh_corpus(corpus_id)`.
- `sync.get_status()`.

La lista es una **superficie de contrato**, no una promesa de endpoints ya implementados. No exponer al LLM comandos genéricos como «ejecuta cualquier request HTTP con mi token».

---

## 15. Operación offline y cola de tareas

### 15.1. Lectura offline

MESTRY puede recuperar texto indexado o documentos marcados para acceso sin conexión. Debe indicar si la versión fue comprobada hace tiempo o si la conexión no permite verificarla. La ausencia del archivo en caché significa «no disponible sin conexión», no «el archivo no existe».

### 15.2. Escritura offline

**Decisión congelada:** una solicitud de escritura sin conectividad **no se reporta como aplicada**. Puede prepararse un borrador local, mostrar la operación y conservar un estado pendiente **solo si la política lo permite**. Antes de ejecutar posteriormente, debe volver a comprobar revisión y, según la categoría de riesgo/tiempo transcurrido, solicitar confirmación renovada.

**PROPUESTO para MVP:** deshabilitar el despacho automático de escrituras offline; permitir guardar un borrador local explícito y hacer que el usuario lo envíe cuando la conexión vuelva. El objetivo es evitar duplicados, colisiones y cambios inesperados.

### 15.3. Estados

```text
DRAFT_LOCAL
   └─(conexión + solicitud explícita)→ REVALIDATING
         ├─ conflicto → NEEDS_REVIEW
         ├─ sin permiso → BLOCKED
         └─ revisión compatible → AWAITING_APPROVAL (si aplica)
                                  ↓
                               EXECUTING
                                  ↓
                               VERIFYING
                          ┌───────┴────────┐
                       COMMITTED         UNKNOWN / FAILED
```

Una operación en estado `UNKNOWN` se investiga antes de reintentar.

---

## 16. Android S23 Ultra: segundo plano, batería y rendimiento

### 16.1. Hardware y despliegue

- **S23 Ultra:** candidato a MESTRY Core persistente y nodo fijo de voz, conectado preferentemente por Wi‑Fi, respetando las limitaciones de pantalla y conectividad descritas en la Etapa 1.
- **S25 Ultra:** teléfono principal e interfaz/componente Android; no duplicar el índice maestro ni el razonamiento permanentemente por una necesidad puramente documental.
- **Note20 Ultra:** reservado para percepción ambiental de una etapa posterior; **no es necesario** para Google Drive, RAG ni sincronización.
- **Windows 11 + WSL2:** estación de desarrollo, pruebas ADB e integración; **no requisito operativo para producción**.

**Decisión congelada:** la integración Drive no justifica por sí sola introducir el Note20, un PC encendido 24/7 ni transformar Android en Windows.

### 16.2. Programación de sincronización

**PROPUESTO:** `WorkManager` para tareas persistentes y periódicas, condicionadas por red y batería. La documentación de Android permite configurar intervalos periódicos con **mínimo de 15 minutos**, pero no garantiza una ejecución puntual: Android puede diferir trabajos según restricciones y gestión energética. El valor de intervalo definitivo requiere medición; **no se congelan 15 minutos como frecuencia obligatoria**.

Tareas propuestas:

1. `MetadataSyncWorker`: sincronización incremental ligera; red disponible; ejecución oportunista.
2. `ContentIndexWorker`: descarga/extracción de archivos seleccionados, preferiblemente Wi‑Fi y batería adecuada; trabajos grandes cuando cargue o el usuario los solicite.
3. `ReconcileWorker`: reparación de inconsistencias y verificaciones limitadas, no escaneo completo continuo.
4. `CachePruneWorker`: expulsión de temporales y caché innecesaria.

### 16.3. Política energética

- En reposo, mantener solo los procesos imprescindibles ya requeridos por la Etapa 1; **no mantener el LLM, indexador ni lector de Drive permanentemente activos**.
- Despertar el subsistema Drive únicamente por consulta o tarea programada.
- Limitar concurrencia, RAM, tamaño de lote, CPU y tiempo por extracción; los umbrales concretos se definirán tras perfiles reales.
- Pausar indexación pesada si temperatura, almacenamiento o batería no permiten operar con seguridad.
- Priorizar lectura de metadatos sobre transferencia de documentos completos.
- Evitar conflictos con la cadena de voz `wake word → STT → respuesta → reposo` del S23.

### 16.4. Doze, reinicios y restricciones del sistema

La programación periódica debe tolerar demoras, reinicios de proceso, ausencia de Wi‑Fi y suspensión del sistema. Las tareas deben ser **idempotentes** y su cursor durable debe permitir retomarlas sin reindexar desde cero. No utilizar un servicio de primer plano continuo para polling de Drive solo porque sea más sencillo programar un bucle infinito. Si Android/One UI impone restricciones concretas, deben medirse y documentarse.

---

## 17. Experiencia de usuario y transparencia

### 17.1. Respuesta de consulta

Forma deseada:

> «En la guía de Evaluación de Proyectos, el déficit acumulado máximo se obtiene acumulando los saldos negativos por período y tomando la mayor necesidad de financiamiento. Fuente: *Guía de Evaluación de Proyectos*, página 7. Archivo comprobado en Drive a las 17:10».

El contenido académico anterior es **solo un ejemplo ilustrativo**, no una cita de una guía real.

### 17.2. Respuesta con información cacheada

> «Puedo responder con los apuntes guardados localmente, pero no he podido comprobar si existe una versión más reciente en Google Drive».

### 17.3. Solicitud de modificación

> «Encontré *Informe de Gestión de Operaciones*. Propongo insertar la sección “Conclusiones” al final. Este es el contenido y el cambio previsto. ¿Confirmas?».

### 17.4. Conflicto

> «El documento cambió desde que preparé la edición. No sobrescribí nada. Puedo revisar la versión nueva y rehacer la propuesta».

### 17.5. Estado de sincronización

MESTRY debe poder mostrar: cuenta conectada, corpus disponibles, fecha de último chequeo, número de archivos catalogados, pendientes de indexar, documentos inaccesibles, errores relevantes y si los resultados son `FRESH`, `CACHED`, `STALE`, `UNKNOWN` u `OFFLINE`. No ofrecer porcentajes ficticios de avance.

---

## 18. Manejo de errores, reintentos y recuperación

### 18.1. Matriz de errores

| Fallo | Lectura / sincronización | Escritura |
|---|---|---|
| Sin Wi‑Fi / Internet | Usar caché autorizada e indicar antigüedad. | No ejecutar ni declarar éxito; conservar borrador si se autorizó. |
| HTTP 401 | Pedir renovación de autenticación; no reintentos infinitos. | Bloquear escritura hasta reautorizar y revalidar. |
| HTTP 403 por permisos | Marcar acceso restringido; retirar del índice si ya no está autorizado. | Bloquear y mostrar motivo. |
| HTTP 403 por cuota / HTTP 429 | Backoff exponencial con variación aleatoria; respetar límites. | No duplicar la operación; revalidar estado antes de reintentar. |
| HTTP 404 | Revisar identidad, eliminación o pérdida de acceso. | Detener; no crear archivo sustituto automáticamente. |
| HTTP 5xx | Reintentar con presupuesto y backoff. | Primero determinar si el servidor aplicó la escritura; evitar duplicados. |
| Archivo demasiado grande | Posponer, segmentar o informar limitación. | No subir una conversión parcial. |
| PDF escaneado | Marcar `NEEDS_OCR`; no inventar texto. | Modificación no soportada salvo flujo específico aprobado. |
| Token/cursor inválido | Reconciliar y reconstruir con checkpoint seguro. | Revalidar archivo antes de ejecutar. |
| Cambio concurrente | Invalidar/sustituir contenido obsoleto. | Bloquear, recuperar la versión nueva y pedir reconciliación. |
| Reinicio del proceso | Reanudar trabajos idempotentes. | Recuperar `operation_id`; verificar si la escritura ya ocurrió. |
| Revocación de acceso | Eliminar/ocultar derivados según política. | Bloquear definitivamente hasta nueva autorización explícita. |

### 18.2. Política de reintentos

**PROPUESTO:** backoff exponencial acotado con jitter, límites de intentos y detección de errores permanentes. No reintentar automáticamente `permissionDenied`, `notFound` sin cambios de contexto ni operaciones potencialmente duplicadas con resultado incierto. Los parámetros finales deben adaptarse a cuotas vigentes del proveedor y experiencia real.

### 18.3. Manejo de cambios observados vs. cambios aplicados

Los errores de extracción no impiden necesariamente avanzar el feed si la información quedó invalidada y existe una tarea durable pendiente. Un cambio remoto debe reflejarse en el catálogo aunque el dispositivo no haya logrado descargar su contenido. En ese caso, **el índice antiguo no puede presentarse como actualizado**.

---

## 19. Modelo de seguridad, privacidad y amenazas

### 19.1. Fronteras de confianza

```text
Solicitud del usuario autenticado
          │
          ▼
MESTRY Core / política de autorización (confiable)
          │
          ├─ Datos desde Drive (NO CONFIABLES como instrucciones)
          ├─ Fragmentos RAG (NO CONFIABLES como instrucciones)
          ├─ Salidas de LLM (PROPUESTAS, NO ACCIONES PRIVILEGIADAS)
          └─ APIs oficiales (respuestas verificables, pero sujetas a errores)
          │
          ▼
Action Controller → permiso → ejecución → verificación → auditoría mínima
```

### 19.2. Amenazas y contramedidas

| Amenaza | Control |
|---|---|
| Prompt injection en documento | Delimitar contexto; ignorar instrucciones operativas procedentes de fuentes; validación de herramienta fuera del LLM. |
| Compartir datos con proveedor no autorizado | Política de clasificación y minimización; filtros previos al broker; consentimiento según riesgo. |
| Fuga de OAuth token | Gestión segura y no exposición en logs, mensajes, prompts ni Drive. |
| Escritura en archivo erróneo | Resolver `file_id` + cuenta + corpus + verificación de nombre y revisión; desambiguar antes de escribir. |
| Sobrescritura por carrera | Precondición de revisión y reconciliación; no «last write wins». |
| Duplicado por timeout/reintento | `operation_id`, estado `UNKNOWN`, consulta del resultado antes de reiterar. |
| Índice desactualizado | Estados de frescura y validez por revisión; invalidación ante cambios. |
| Retención tras revocación | Bloqueo inmediato de consultas y eliminación/invalidación de datos derivados conforme a política. |
| Descarga de material malicioso | Parser restringido/sandbox cuando corresponda; límites de recursos; no ejecutar macros ni código extraído. |
| Acumulación de datos personales | Caché mínima, limpieza automática, control del usuario y políticas de retención. |
| Exceso de permisos | `drive.file` como preferencia y escalamiento de scopes con justificación explícita. |

### 19.3. Protección de datos sensibles

No guardar por defecto audio, video, capturas, pulsaciones, cookies de autenticación, archivos enteros ni prompts históricos extensos. El contenido documental sensible debe estar sujeto a una política por tipo de fuente y tarea: `LOCAL_ONLY`, `CLOUD_ALLOWED_WITH_MINIMIZATION` o `REQUIRES_EXPLICIT_CONSENT` son **categorías propuestas**, no políticas ya implementadas. El procesamiento sobre documentos médicos, financieros o personales debe evaluarse particularmente por privacidad y por las condiciones de los proveedores.

### 19.4. Auditoría mínima

Registrar: timestamp, herramienta, `operation_id`, ID interno/alias del archivo, tipo de acción, resultado, estado de confirmación y causa de error. **No registrar por defecto el cuerpo completo de documentos ni credenciales.** Acceso al log limitado; retención por plazo definido más adelante.

---

## 20. Métricas, rendimiento y criterios de aceptación

### 20.1. Métricas a observar

| Métrica | Propósito | Estado |
|---|---|---|
| `drive_api_calls_per_query` | Medir sobrecoste de API | PROPUESTO. |
| `bytes_downloaded_per_query` | Confirmar descargas selectivas | PROPUESTO. |
| `metadata_sync_duration_ms` | Costo de sincronización | PROPUESTO. |
| `files_reindexed_per_change` | Detectar reindexación excesiva | PROPUESTO. |
| `cache_hit_rate` | Eficacia de la caché | PROPUESTO. |
| `retrieval_precision_at_k` | Calidad de recuperación RAG | PROPUESTO. |
| `citation_grounding_rate` | Sustento de citas en archivo real | PROPUESTO. |
| `stale_answer_rate` | Frecuencia de respuestas con índice no vigente | PROPUESTO. |
| `write_verification_success_rate` | Fiabilidad de escritura | PROPUESTO. |
| `write_conflict_prevented_count` | Eficacia de precondiciones | PROPUESTO. |
| `battery_delta_per_hour` | Efecto en S23 durante reposo/sync | PENDIENTE medir. |
| `peak_memory_mb`, `temperature_delta` | Costo de indexación | PENDIENTE medir. |

### 20.2. Objetivos iniciales de benchmark (NO congelados)

**Hipótesis a probar, no promesas de rendimiento:**

- Consulta repetida sin cambios: evitar volver a descargar el documento ya indexado.
- Dos consultas simultáneas al mismo archivo: compartir/serializar el trabajo de descarga para no duplicarlo.
- Una modificación de un archivo: invalidar y actualizar solo ese archivo y su dependencia de índice.
- Escritura a revisión obsoleta: **cero sobrescrituras silenciosas**.
- Escritura con error de red incierto: **cero reintentos ciegos**.
- Archivo revocado: **cero apariciones nuevas en recuperación después de invalidación**.
- Respuesta offline: nunca informar que está actualizada en la nube.

Los tiempos máximos de respuesta, frecuencia de sincronización, presupuesto de batería, tamaños de caché y tasas mínimas de precisión se definirán **después** de medir corpus y dispositivo reales. Congelar números sin evidencia sería una decisión artificial.

### 20.3. Criterios mínimos para llamar funcional al MVP

**AC-01.** Un usuario autoriza al menos un archivo mediante un flujo compatible y documentado.  
**AC-02.** MESTRY encuentra ese archivo por nombre o ID y muestra metadatos reales.  
**AC-03.** Puede leer un documento de prueba soportado y citar su origen.  
**AC-04.** Una segunda lectura no descarga nuevamente el mismo contenido si la revisión no cambió.  
**AC-05.** Una modificación hecha directamente en Drive se detecta y el índice local deja de usar texto obsoleto.  
**AC-06.** Puede preparar y ejecutar una edición reversible de un archivo de prueba con autorización apropiada.  
**AC-07.** La operación posterior lee/verifica la versión remota modificada.  
**AC-08.** Una edición concurrente provoca rechazo o reconciliación, nunca sobrescritura silenciosa.  
**AC-09.** Sin Internet, el sistema informa claramente que usa caché o no dispone del archivo.  
**AC-10.** Un reinicio no corrompe el cursor ni duplica cambios.  
**AC-11.** No se observan credenciales ni contenido sensible innecesario en logs de prueba.  
**AC-12.** El flujo funciona desde Android o se reporta expresamente qué parte sigue limitada a desarrollo desde PC.

**Ninguno de estos criterios se declara cumplido en esta fecha.**

---

## 21. Plan de pruebas detallado

### 21.1. Unitarias

- Reconocimiento de MIME y selección de adapter.
- Selección de política de frescura según intención.
- Idempotencia de eventos repetidos en `changes.list`.
- Correcta transición de `FRESH → STALE → INDEXING → FRESH`.
- Invalidación y reemplazo atómico de chunks por revisión.
- Desambiguación de nombres duplicados.
- Filtrado por cuenta y corpus autorizado.
- Normalización de texto y localizadores de PDF/Slides/Docs.
- Construcción de propuestas de escritura sin ejecución privilegiada.
- Bloqueo de herramientas por operación no permitida o confirmación ausente.

### 21.2. Integración con Drive / Workspace en cuenta de prueba

1. Crear carpeta o conjunto de archivos de prueba exclusivamente para MESTRY.
2. Autorizar acceso mínimo posible, registrar scopes concedidos y limitaciones reales.
3. Importar un `.md`, un PDF con texto, un Google Doc y (posteriormente) una Sheet y una Slide.
4. Recuperar metadatos; verificar correspondencia MIME/ID.
5. Descargar/extractar y contrastar salida contra contenido conocido.
6. Editar un archivo desde el navegador y comprobar evento de cambio.
7. Renombrar archivo sin alterar su ID; verificar que no se duplica.
8. Mover archivo fuera del corpus seleccionado; verificar estado de alcance según permisos reales.
9. Revocar acceso; validar exclusión de recuperación.
10. Traspasar un documento por `changes.list` paginado y simular caída a mitad de lote.
11. Ejecutar inserción nativa de Docs; confirmar revisión y contenido.
12. Simular edición concurrente y comprobar que el controlador detiene la escritura incompatible.
13. Cortar red después de enviar una operación; verificar que no se duplica al reintentar.
14. Reautorizar cuenta y repetir lectura sin fuga de tokens.

### 21.3. Ensayos en Galaxy S23 Ultra

- Pantalla apagada, teléfono bloqueado y proceso sujeto a Doze.
- Wi‑Fi desconectado y reconectado.
- Reinicio y recuperación de tareas programadas.
- S23 conectado a corriente y sin corriente (si la condición del hardware lo permite).
- Medición de consumo/temperatura durante 30–60 minutos de uso representativo **como plan de prueba, no como dato ya obtenido**.
- Indexación de un PDF mediano con memoria limitada.
- Voz y sincronización concurrentes: la respuesta del wake word no debe bloquearse por un extractor intensivo.
- Reposo prolongado: no mantener CPU activa innecesariamente.
- Verificar particularidades de One UI y restricciones de segundo plano vigentes.

### 21.4. Evaluación RAG

Preparar un conjunto de preguntas y respuestas verificadas manualmente:

- Preguntas con respuesta literal en apuntes.
- Preguntas que requieren combinar dos secciones del mismo documento.
- Preguntas que requieren combinar dos documentos diferentes.
- Preguntas sobre conceptos ausentes del corpus.
- Preguntas con documentos deliberadamente contradictorios.
- Preguntas que usan dos versiones del mismo archivo.
- Preguntas con contenidos maliciosos simulados (prompt injection).

Registrar fuentes recuperadas, precisión de citación, omisiones y latencia antes de declarar útil una mejora de recuperación híbrida.

### 21.5. Validación manual de edición

- Comparar contenido antes/después.
- Inspeccionar estilos y elementos no modificados.
- Revisar historial de versión de Google.
- Verificar que el archivo conserva ID, nombre, ubicación y permisos salvo cambio autorizado.
- En Word/PowerPoint/Excel, abrir el archivo actualizado en la aplicación correspondiente y comprobar integridad y formato.
- Confirmar que «cancelar» evita toda modificación remota.

---

## 22. Roadmap de implementación por incrementos

**Regla:** no implementar toda la arquitectura de una sola vez. Cada hito entrega una capacidad útil de extremo a extremo, con evidencia reproducible. El calendario concreto de implementación es **PENDIENTE** y se subordina a mantener estable la Etapa 1.

### Hito A — Descubrimiento de código y entorno (sin cambios funcionales)

- Revisar repositorio y estado real de MESTRY/legado Jarvis.
- Identificar módulos Core, Tool Manager, Android Companion y persistencia ya existentes.
- Registrar versiones Android, SDK, librerías, pruebas y dependencias.
- Confirmar qué APIs Google están habilitadas y si se cuenta con un proyecto Google Cloud autorizado.
- Revisar estructura de carpetas real y permisos de usuario.
- **Salida:** informe de brechas; ningún éxito técnico presumido.

### Hito B — MVP lectura directa

- Conexión OAuth de prueba.
- Selección de un documento explícito.
- `DriveConnector.search/getMetadata/getContent` mínimo.
- Extraer texto de formato sencillo (primero `.txt`/`.md` o Google Doc según permisos efectivos).
- Responder una consulta citando el documento.
- **Prueba principal:** «lee este archivo» funciona desde el Core con fuente identificable.

### Hito C — Catálogo y caché

- SQLite local y relación `account_id/file_id`.
- Caché limitada por versión y fecha.
- Evitar doble descarga cuando no hubo cambios.
- Diagnóstico `FRESH/CACHED/UNKNOWN`.
- **Prueba principal:** consulta repetida reutiliza contenido de forma verificable.

### Hito D — Sincronización incremental

- Bootstrap con token provisional, catálogo y feed.
- Persistencia transaccional de checkpoints.
- Invalidez de contenido y reindexación dirigida.
- WorkManager oportunista si despliegue Android viable.
- **Prueba principal:** una modificación remota se detecta sin volver a descargar todo el corpus.

### Hito E — RAG académico

- Extractor(es) para PDF y/o Google Docs.
- Fragmentos con referencia fiable.
- SQLite FTS5 + búsqueda por curso/tipo.
- Integración con Reasoning Engine/Free Model Broker y control de privacidad.
- **Prueba principal:** responder pregunta de material de curso con cita correcta.

### Hito F — Escritura controlada

- Propuesta estructurada y confirmación de cambio.
- Implementar primero **un solo formato** de escritura de bajo riesgo; **preferible Google Docs** si revisiones y API funcionan como se espera.
- Precondición de revisión, verificación posterior y actualización del índice.
- **Prueba principal:** inserción controlada sin pérdida de contenido y conflicto correctamente rechazado.

### Hito G — Ampliación progresiva

- Markdown/archivos binarios con edición versionada.
- Sheets/Slides si hay uso que lo justifique.
- OCR, embeddings, selección avanzada de carpetas, soporte multicuenta/Shared Drives, sincronización push o backups, **solo previa evaluación y aprobación cuando alteren alcance o coste**.

**Dependencias en secuencia:** Hito B exige OAuth; C exige lectura; D exige catálogo y tokens; E exige extracción e índice; F exige Action Controller y un adaptador de edición; G depende de evidencia de utilidad y restricciones reales.

---

## 23. Propuesta de organización de código (pendiente de revisar repositorio)

No se crean archivos de código como parte de este documento. Estructura ilustrativa para un proyecto modular Android/Kotlin:

```text
mestry/
├── core/
│   ├── orchestration/
│   ├── intents/
│   ├── actioncontrol/
│   └── knowledge/
│       ├── RetrievalPolicy.kt
│       ├── KnowledgeRetriever.kt
│       └── CitationBuilder.kt
├── tools/
│   └── drive/
│       ├── api/DriveConnector.kt
│       ├── auth/GoogleAuthorization.kt
│       ├── catalog/DriveCatalog.kt
│       ├── sync/DriveChangeTracker.kt
│       ├── read/DocumentReader.kt
│       ├── extract/DocumentExtractor.kt
│       ├── write/DriveWriteAdapter.kt
│       └── model/DriveModels.kt
├── storage/
│   ├── MestryDatabase.kt
│   ├── FileDao.kt
│   ├── SyncCheckpointDao.kt
│   └── DocumentChunkDao.kt
├── background/
│   ├── MetadataSyncWorker.kt
│   └── ContentIndexWorker.kt
├── interfaces/
│   ├── voice/
│   ├── overlay/
│   └── app/
└── tests/
    ├── unit/
    ├── integration/
    └── android/
```

**Nota:** nombres de rutas y tecnologías **no congelados**. Debe adaptarse al código existente, evitando crear un módulo redundante si el Tool Manager ya puede alojar un adapter Drive.

---

## 24. Pseudocódigo de procesos críticos

### 24.1. Consulta informada por frescura

```text
function answer_document_question(user_request):
    intent = IntentRouter.classify(user_request)
    scope = AuthorizationContext.allowed_corpora(user_request.user)
    policy = FreshnessPolicy.for_intent(intent)

    candidates = DriveCatalog.find_candidates(intent, scope)
    if candidates.empty and network_available:
        candidates = DriveConnector.searchFiles(intent.filters_within(scope))

    for file in select_relevant(candidates):
        if policy.requires_remote_verification:
            remote = DriveConnector.getMetadata(file.id)
            if remote.access_denied:
                DocumentIndexer.invalidate(file.id)
                continue
            if remote.revision != local_index.revision(file.id):
                DocumentIndexer.invalidate(file.id)
                queue_extract(file.id, remote.revision)

    ensure_needed_documents_indexed_with_budget()
    passages = KnowledgeRetriever.retrieve(intent.query, scope)
    passages = filter_valid_revision_and_access(passages)

    if passages.insufficient:
        return qualified_no_evidence_response()

    answer = ReasoningEngine.answer_with_sources(passages, intent)
    return CitationBuilder.verify_and_render(answer, passages, freshness_status)
```

### 24.2. Procesamiento idempotente de cambios

```text
function sync_changes(account, scope):
    cursor = checkpoints.committed_cursor(account, scope)
    if cursor is null:
        return bootstrap_scope(account, scope)

    repeat:
        page = drive.changes.list(pageToken=cursor, includeRemoved=true, ...)
        transaction:
            for change in page.changes:
                apply_metadata_change_idempotently(change)
                if change.changed_or_removed:
                    invalidate_old_chunks(change.fileId)
                    enqueue_refresh_only_if_eligible(change.fileId)
            persist_page_progress_safely(page)

        if page.nextPageToken exists:
            cursor = page.nextPageToken
        else:
            transaction: checkpoints.commit(page.newStartPageToken)
            return SUCCESS
```

**Aclaración:** `persist_page_progress_safely` representa un diseño transaccional que permite reanudar páginas y no equivale a comprometer prematuramente el checkpoint terminal. La paginación, parámetros y campos `changes.list` definitivos deberán confrontarse con el SDK real.

### 24.3. Escritura sin doble envío

```text
function commit_prepared_edit(proposal_id, user_approval):
    proposal = proposed_actions.get(proposal_id)
    controller.validate_and_require_approval(proposal, user_approval)
    controller.ensure_not_already_committed(proposal.operation_id)

    remote_before = drive.get_current_revision(proposal.file_id)
    if remote_before != proposal.expected_revision:
        return CONFLICT_NO_WRITE

    result = drive.write_with_supported_precondition(proposal)
    if result.is_ambiguous_timeout:
        mark(UNKNOWN)
        return REQUIRES_REMOTE_RECONCILIATION

    verified = drive.read_back_and_verify(result, proposal)
    if not verified:
        mark(UNKNOWN_OR_FAILED)
        return NEEDS_REVIEW

    transaction:
        mark(COMMITTED)
        invalidate_index(proposal.file_id)
        enqueue_refresh(proposal.file_id)
    return VERIFIED_SUCCESS
```

**No convertir este pseudocódigo en código de producción sin incorporar semánticas reales de la API, validaciones y tests.**

---

## 25. Decisiones alternativas estudiadas y descartes

| Alternativa | Evaluación | Decisión |
|---|---|---|
| Descargar todo Drive antes de cada pregunta | Fuerte latencia, batería, cuota, tráfico y datos innecesarios. | **Descartada.** |
| Usar Drive directamente para todas las búsquedas sin índice | Sencillo inicialmente, pero insuficiente para RAG propio y sin conexión. | **Descartado como única estrategia**; válido para búsquedas puntuales. |
| Mantener réplica local completa de Drive | Gasta almacenamiento y aumenta costo operativo; riesgo de archivos no necesarios. | **Descartada por defecto.** |
| Drive + índice/caché local incremental | Compromiso entre frescura, recuperación, batería y mantenimiento. | **Aprobada / congelada.** |
| NAS en red local | Más infraestructura y mantenimiento para un problema que Drive ya resuelve. | **No requerido.** |
| Google Drive como reemplazo de SQLite | Drive no ofrece transacciones locales rápidas para estado interno del agente. | **Descartada.** |
| Webhooks/servidor HTTPS propio desde el día uno | Requiere endpoint público y renovación de canales. | **Fuera del MVP; posible futuro.** |
| Edición visual en Drive web | Frágil y dependiente de UI. | **Solo respaldo excepcional.** |
| Escribir Google Docs descargando/reemplazando completo | Riesgo de pérdida de formato y colaboración. | **Descartado como ruta normal.** |
| Subir sin verificar cambios concurrentes | Sobrescritura silenciosa. | **Prohibido.** |
| Modelo LLM con token Drive y acceso HTTP arbitrario | Riesgos graves de privacidad y ejecución. | **Prohibido.** |
| Servicio vectorial remoto desde el MVP | Infraestructura, costos y transferencia adicionales aún no justificados. | **No adoptado inicialmente.** |
| SQLite/FTS5 y embeddings opcionales | Simple, portable y suficiente como hipótesis inicial. | **Propuesto, sujeto a benchmark.** |

---

## 26. Compatibilidad con etapas y decisiones anteriores

### 26.1. Etapa 1 — asistente de voz fijo

La integración Drive **no debe retrasar** la capacidad base del S23 de detectar la palabra de activación, convertir voz, clasificar, responder y volver a reposo. Drive solo se activa si la solicitud requiere archivos. No hay sincronización pesada constante ni dependencia del Note20.

### 26.2. Etapa 2 — Personal Secretary

La Etapa 2 ya considera herramientas, memoria operativa, notas y contexto. MESTRY añade **DriveConnector** como herramienta documental y **KnowledgeRetriever** para consultar material autorizado. La memoria de preferencias, eventos y tareas mantiene su propia semántica; no se reemplaza por un conjunto de archivos sincronizados.

### 26.3. Etapa 3 — Context Awareness

Los eventos estructurados del Note20 pueden enriquecer prioridades o contexto de tareas, pero **no habilitan por sí mismos acceso adicional a Drive**. La cámara no participa del flujo documental, salvo futura extensión aprobada. El Note20 sigue procesando percepción localmente y transmitiendo eventos, no video continuo.

### 26.4. Samsung Keyboard, overlay y app

Las interfaces únicamente envían la intención, contexto y consentimiento. No implementan OAuth ni RAG duplicados de manera separada. El teclado Samsung se conserva; el overlay presenta vista previa/diff y confirmaciones cuando corresponda. Se respeta la arquitectura antigua aunque se use el nombre MESTRY a nivel de proyecto.

### 26.5. Free Model Broker

Se conservan reglas/modelos locales para tareas simples, servicios gratuitos oficiales autorizados para razonamiento cuando aporten valor, fallback y verificación. MESTRY **no** automatiza ChatGPT/Gemini web para eludir APIs ni cuotas, ni envía documentos completos a modelos gratuitos sin analizar privacidad y límites. El broker no gestiona OAuth de Drive.

---

## 27. Riesgos, incertidumbres y decisiones pendientes

| ID | Riesgo / incertidumbre | Tratamiento actual | Condición para cerrar |
|---|---|---|---|
| P-01 | Experiencia Android de selección de archivos con `drive.file` | No asumir acceso recursivo a carpetas. | Probar OAuth/selector y alcance real en S23. |
| P-02 | Verificación de Google para una app pública con scopes restringidos | Evitar scopes amplios. | Revisar política vigente al distribuir. |
| P-03 | Edición atómica de binarios ante concurrencia | No sobrescribir si no hay seguridad. | Probar precondiciones soportadas y recuperación. |
| P-04 | APIs de revisión distintas para Docs, Sheets, Slides | Adapter separado por tipo. | Ensayos de edición concurrente por formato. |
| P-05 | Límite de exportación de Workspace | No asumir exportaciones grandes completas. | Seleccionar lectura adecuada y probar. |
| P-06 | Calidad de extracción PDF con tablas | Recuperación acotada y abstención. | Benchmark en guías reales. |
| P-07 | OCR de documentos escaneados | No está incluido inicialmente. | Demanda real + prueba de motor. |
| P-08 | Latencia/consumo de indexación en S23 | Trabajos oportunistas y presupuestos. | Perfil real CPU/RAM/temperatura/batería. |
| P-09 | Frecuencia de sincronización útil | No congelar intervalo aún. | Medir frescura vs batería y cambios reales. |
| P-10 | Política de caché de documentos privados | Minimización y borrado controlado. | Aprobar retención y cifrado de contenido. |
| P-11 | Almacenamiento de embeddings | FTS5 como primera hipótesis. | Medición de calidad de RAG. |
| P-12 | Multicuenta y Shared Drives | Fuera del MVP. | Necesidad comprobada y diseño de scopes/tokens. |
| P-13 | Formatos Office complejos | No garantizar fidelidad. | Pruebas de apertura y verificación después de editar. |
| P-14 | Estado actual del repositorio de MESTRY | Desconocido. | Inspección del código y entorno real. |
| P-15 | Compatibilidad de nombres históricos Jarvis | Conservar etiquetas/archivos antiguos. | Plan de migración independiente aprobado. |
| P-16 | Privacidad de documentos enviados a LLM gratuitos | Minimización y política de salida. | Evaluar proveedor, condiciones y consentimiento. |
| P-17 | Backup/restauración del índice y estado de MESTRY | Índice reconstruible, tokens protegidos. | Política de backup separada y recuperación ensayada. |
| P-18 | Calidad de citas en formatos con pocos localizadores | Indicar solo posiciones verificables. | Implementar localizadores por extractor. |

---

## 28. Reglas operativas no negociables

1. **Drive es la fuente de verdad de originales seleccionados; la base local es caché/índice.**
2. **No se descarga todo antes de cada consulta.**
3. **No se transfiere todo el contenido de Drive a proveedores de IA.**
4. **No se entregan credenciales al LLM ni se interpretan documentos como instrucciones privilegiadas.**
5. **No se escribe en archivos no autorizados o ambiguos.**
6. **No se sobrescribe silenciosamente una versión remota que cambió.**
7. **No se reintenta a ciegas una escritura que pudo haberse completado.**
8. **No se declara «sincronizado» o «actualizado» sin comprobarlo.**
9. **No se declara un hito probado sin evidencia real.**
10. **No se cambia Samsung Keyboard ni el Free Model Broker congelado por instalar Drive.**
11. **No se exige encender el PC para usar la función cotidiana cuando el despliegue Android sea viable.**
12. **No se añade infraestructura persistente nueva sin beneficio medido.**
13. **No se eliminan documentos originales cuando se limpia la caché.**
14. **No se renombran los archivos congelados anteriores por el cambio de nombre a MESTRY.**
15. **No se convierten parámetros técnicos propuestos en decisiones permanentes sin prueba y aprobación.**

---

## 29. Registro de decisiones (ADR)

| ADR | Decisión | Estado | Motivación |
|---|---|---|---|
| ADR-MESTRY-DRIVE-001 | Google Drive como repositorio documental autoritativo de archivos seleccionados | **CONGELADO** | Centralizar documentos, múltiples dispositivos, mantenimiento mínimo. |
| ADR-MESTRY-DRIVE-002 | Catálogo local, caché e indexación selectiva en el S23 | **CONGELADO** | Respuesta rápida, uso offline, reducción de tráfico. |
| ADR-MESTRY-DRIVE-003 | Sincronización incremental más revalidación bajo demanda | **CONGELADO** | Frescura sin sincronización completa por consulta. |
| ADR-MESTRY-DRIVE-004 | Edición nativa Workspace por API, binarios por descarga/edición/subida controlada | **CONGELADO** | Preservar estructura y minimizar escrituras destructivas. |
| ADR-MESTRY-DRIVE-005 | Action Controller independiente con verificación/revisiones | **CONGELADO** | Seguridad, integridad y control de acciones. |
| ADR-MESTRY-DRIVE-006 | Privilegios mínimos y autorización selectiva | **CONGELADO** | Privacidad y menor superficie de riesgo. |
| ADR-MESTRY-DRIVE-007 | No añadir servidor HTTPS/webhook al MVP | **CONGELADO para MVP** | Evitar infraestructura innecesaria. |
| ADR-MESTRY-DRIVE-008 | SQLite + FTS5 inicial | **PROPUESTO** | Simplicidad y adecuación local; requiere evaluar código/benchmarks. |
| ADR-MESTRY-DRIVE-009 | WorkManager para sincronización oportunista | **PROPUESTO** | Respetar restricciones Android; requiere prueba real. |
| ADR-MESTRY-DRIVE-010 | Embeddings/RAG híbrido avanzados | **PENDIENTE** | Demostrar mejora suficiente respecto de FTS. |
| ADR-MESTRY-DRIVE-011 | Renombrar el proyecto de Jarvis a MESTRY | **CONGELADO** | Instrucción explícita del propietario del proyecto. |

---

## 30. Checklist previa a cualquier implementación

- [ ] Confirmar acceso al repositorio, rama y versión real del proyecto.
- [ ] Leer los cinco documentos previos y este ADR antes de modificar arquitectura.
- [ ] Identificar módulos reales a reutilizar; impedir duplicación de Core/Tool Manager.
- [ ] Confirmar qué funcionalidades están efectivamente implementadas y probadas.
- [ ] Preparar cuenta/carpeta/archivos de prueba sin documentos personales críticos.
- [ ] Evaluar OAuth, selectors y scopes concretos en Android.
- [ ] Definir alcance del primer formato de lectura y edición.
- [ ] Probar lectura y versiones de un archivo de prueba.
- [ ] Probar cambio remoto y cursor incremental con reinicio.
- [ ] Implementar revalidación antes de una escritura.
- [ ] Añadir confirmación/preview acorde al riesgo.
- [ ] Verificar integridad post-escritura y no duplicación.
- [ ] Ejecutar pruebas de permisos revocados y prompt injection.
- [ ] Medir latencia, red, almacenamiento y consumo del S23.
- [ ] Actualizar el registro de tareas y resultados **en un documento de seguimiento separado**, sin editar ADRs congelados sin autorización.

---

## 31. Fuentes técnicas oficiales verificadas para esta decisión

Fuentes revisadas durante la preparación del presente documento (2026-10-19). Los enlaces son referencias de diseño; las políticas, SDKs, cuotas y APIs deben reconfirmarse antes de implementar y distribuir.

1. **Drive API — Choose scopes:**  
   <https://developers.google.com/workspace/drive/api/guides/api-specific-auth>  
   Referencia sobre `drive.file`, permisos mínimos, scopes restringidos y verificación de aplicaciones.
2. **Drive API — Retrieve changes:**  
   <https://developers.google.com/workspace/drive/api/guides/manage-changes>  
   Uso de `changes.getStartPageToken` y `changes.list`.
3. **Drive API — Changes and revisions overview:**  
   <https://developers.google.com/workspace/drive/api/guides/change-overview>  
   Semántica de cambios, revisiones y limitaciones del feed.
4. **Drive API — changes.list reference:**  
   <https://developers.google.com/workspace/drive/api/reference/rest/v3/changes/list>  
   `nextPageToken`, `newStartPageToken`, paginación y opciones.
5. **Drive API — Search for files and folders:**  
   <https://developers.google.com/workspace/drive/api/guides/search-files>  
   Filtros `files.list`, búsqueda por nombre, contenido y carpeta.
6. **Drive API — Files resource:**  
   <https://developers.google.com/workspace/drive/api/reference/rest/v3/files>  
   Metadatos, `md5Checksum`, capacidades y estado del archivo.
7. **Drive API — Download and export files:**  
   <https://developers.google.com/workspace/drive/api/guides/manage-downloads>  
   Lectura de binarios, exportación de Workspace y límites.
8. **Drive API — Upload file data:**  
   <https://developers.google.com/workspace/drive/api/guides/manage-uploads>  
   Subidas simples, multipart y reanudables.
9. **Google Docs API — documents.batchUpdate:**  
   <https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate>  
   Escritura estructurada, `requiredRevisionId` y `targetRevisionId`.
10. **Drive API — Resolve errors:**  
    <https://developers.google.com/workspace/drive/api/guides/handle-errors>  
    Errores HTTP y backoff exponencial.
11. **Drive API — Push notifications:**  
    <https://developers.google.com/workspace/drive/api/guides/push>  
    Webhooks HTTPS y expiración de canales; justifica exclusión del MVP.
12. **Android Developers — Define work requests:**  
    <https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work>  
    WorkManager, intervalos periódicos y restricciones de ejecución.
13. **Google Drive — About changes:**  
    <https://developers.google.com/workspace/drive/api/guides/about-changes>  
    Alcance del registro de cambios y su semántica de estado.

---

## 32. Protocolo de evolución del documento

- Este archivo es una **nueva referencia congelada** para la integración de Drive en MESTRY.
- Un cambio a las decisiones D-01 a D-15 o ADR congelados requiere **solicitud y aprobación explícita** del propietario.
- Nuevas alternativas pueden documentarse en un archivo complementario `MESTRY_Drive_Propuestas_y_Pruebas.md` (nombre sugerido, **no creado**).
- La implementación puede registrar resultados, benchmarks, fallos y diferencias respecto de las propuestas **sin editar silenciosamente** este documento.
- Si una API deja de estar disponible, registrar incidencia y proponer sustitución compatible con el contrato antes de modificar la arquitectura congelada.
- Las decisiones antiguas continúan siendo válidas en cuanto no contradigan la aprobación explícita del cambio de nombre y la nueva extensión documental.

---

## 33. Conclusión ejecutiva y criterio rector

**MESTRY utilizará Google Drive como fuente de verdad documental de archivos seleccionados y autorizados.** El S23 Ultra mantendrá únicamente el catálogo, la caché y el índice necesarios para consultas rápidas y RAG. La sincronización identificará cambios incrementales y revalidará bajo demanda la información importante, sin descargar todo Drive antes de responder. La edición se realizará mediante APIs nativas estructuradas cuando existan, o mediante descarga/edición/subida con protección frente a conflictos para formatos convencionales. El Core conservará la responsabilidad de interpretar solicitudes; el controlador independiente decidirá qué acciones están autorizadas, verificará revisiones y confirmará resultados. Todo ello funcionará desde múltiples interfaces de MESTRY y aspirará a autonomía Android sin PC encendido.

**Principio final congelado:** *MESTRY debe ahorrar más tiempo del que cuesta mantenerlo; Drive aporta disponibilidad del conocimiento, mientras el índice local aporta rapidez y el controlador aporta seguridad.*

**Fin del documento — arquitectura congelada, no implementación certificada.**
