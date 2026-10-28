# Android Intelligence y Device Agent

**Investigación y diseño, 2026-10-19. Ningún modelo descargado ni dispositivo controlado.** [Evidencia A04–A15 y M01–M07](EVIDENCE.md#android-agentes-e-inferencia). Protocolos: [V08–V10](VALIDATION_PLAN.md).

## Recomendación

Un **ejecutor nativo Android con catálogo mínimo de acciones**, reglas y verificaciones constituye la base. El modelo opcional interpreta una instrucción y propone una acción tipada; no toca Android directamente ni decide sus propios permisos. Separar planner, validador, ejecutor y verificador permite cambiar de modelo sin cambiar privilegios.

La primera demostración no necesita un LLM: la versión de Android tiene una API determinista. Primero demostrar observación, navegación limitada, evidencia y cancelación; después comparar si un clasificador o modelo pequeño mejora la interpretación del español. No adoptar un agente general pesado para resolver una consulta del sistema.

## Motores y ubicación del control

“Local” puede significar dispositivo físico local conectado a un PC, planner local en PC o ejecución íntegra en el teléfono. Se distingue explícitamente:

| Candidato | Dónde corre normalmente el planner/control | Qué necesita en Android | Autonomía dentro del S23 | Evaluación |
|---|---|---|---|---|
| **AccessibilityService** nativo | App Android | Habilitación explícita, capacidades de nodos/gestos/captura | Sí para acciones permitidas, sujeto a UI/bloqueo y política | Adaptador principal para macros cuando no existe API |
| **ADB** | Cliente en host de desarrollo | Debug USB o emparejamiento inalámbrico autorizado | Un cliente en el mismo teléfono sería una configuración adicional, no baseline | Referencia de diagnóstico/pruebas; no exponer puerto público |
| **UIAutomator** | Tests instrumentados en Android, lanzados desde herramientas | Paquete de pruebas/runner y permisos del entorno | Parte de ejecución vive en teléfono, pero no es un servicio autónomo general | Baseline reproducible para pruebas entre apps |
| **Appium + UIAutomator2** | Servidor y cliente en máquina de desarrollo | ADB y servidor instrumentado | No hay soporte de host Android aquí verificado | Útil para comparar pruebas, exceso para servicio inicial |
| **DroidRun, hoy Mobilerun** | Framework Python en host, Portal en teléfono | Portal Accessibility y normalmente ADB para setup/control | Planner Python en Termux es port por validar, no capacidad demostrada | Candidato de benchmark y reutilización de adaptadores |
| **Mobile Harness, droidrun** | Instrucciones para un agente y API Python mobilerun_core | Backend ADB, Portal HTTP autenticado o cloud | HTTP local abre una posibilidad; harness no ejecuta modelo por sí mismo | Fuente de patrones; no confundir con runtime |
| **Android Use, languse-ai** | Python/host con ADB | Dispositivo preparado para depuración | No demostrado como app autónoma | Menor prioridad por actividad observada y empaquetado pendiente |
| **Android Use, austinintelligence** | CLI/MCP Rust en macOS/Linux/Windows | Helper Accessibility y ADB/setup | Linux ARM64 no equivale a Android nativo | Interfaz acotada interesante para comparar |
| **Android Use, j0taaa** | App en teléfono | Accessibility y modelo API configurable | Sí a nivel orquestación según proyecto; inferencia habitualmente externa | Evaluar código y endpoint local antes de adoptar |
| **Android Use, Pegoku** | App en teléfono | Shizuku y autenticación declarada ChatGPT/Codex | Sí a nivel orquestación; modelo externo | Privilegios y autenticación requieren auditoría; no baseline |
| **Mobile Harness, techjarves** | Workspace de programación Android + PRoot | Runtime descargado y claves de proveedor | Sí para desarrollo local declarado, no demuestra control UI general | No es el Mobile Harness de DroidRun; no acredita integración Codex |
| **Shizuku** | Servicio con privilegios shell/root que usa otra app | Arranque/permiso ADB o root según modalidad | Puede eliminar PC continuo después de setup, con límites tras reinicio | Superficie de privilegios mayor; no necesario inicialmente |

Fuentes por fila [A04–A13](EVIDENCE.md#android-agentes-e-inferencia). La actividad del repo es una señal, no una auditoría: Mobilerun, DroidRun Mobile Harness y austinintelligence tienen cambios de octubre 2026 observados; languse-ai muestra último push en diciembre 2025. Ninguno se selecciona solo por estrellas o tasa de éxito anunciada.

No copiar benchmarks del proveedor como tasa MESTRY. Un Portal instalado en S23 con LLM en PC sigue dependiendo del PC. Un planner en S23 que llama API externa es **control local con inferencia externa**, distinto de autonomía offline. Un modelo en S23 que usa un ejecutor en otra máquina tampoco acredita el objetivo local.

## Capacidades y límites del adaptador nativo

La jerarquía Accessibility puede exponer texto, descripciones, IDs, límites y acciones. El ejecutor intentaría click, setText, scroll y acciones globales soportadas, con feedback. Capturas mediante API Accessibility dependen de versión/capacidad y pueden fallar por ventanas protegidas. MediaProjection es otra vía con consentimiento y restricciones de sesión; no se supone captura silenciosa permanente.

Jerarquías incompletas, canvas, WebViews, listas recicladas, animaciones, cambios de idioma y controles sin etiquetas reducen fiabilidad. Referencias de nodos son efímeras: expiran al cambiar pantalla/ventana; resolverlas otra vez. Coordenadas son último recurso vinculadas a una captura y dimensiones verificadas, nunca números fijos que se reutilizan tras rotación.

Abrir aplicaciones por intent explícito permitido y usar APIs oficiales cuando existan. Respetar restricciones de lanzamiento en segundo plano; una orden remota no concede automáticamente capacidad de traer cualquier app al frente. Pantalla bloqueada o permiso faltante produce `blocked`, no una secuencia para introducir PIN o desactivar controles.

Con pantalla apagada pueden correr trabajos de sistema y algunas consultas, pero **control UI no se promete mientras la pantalla permanece apagada/bloqueada**. Despertar pantalla y disponer de una sesión desbloqueada son cosas distintas. La disponibilidad prolongada de SSH/Drive no demuestra disponibilidad de interacción visual.

## Bucle y política de ejecución

1. Recibir tarea autorizada con alcance, deadline y cancel token.
2. Resolver intención por reglas o clasificador. Preferir API oficial o función determinista.
3. Observar estado y capacidades; minimizar ventana/paquetes/texto capturado.
4. Generar `ActionProposal` con acción de catálogo, argumentos y referencia a observación.
5. Validar esquema, permisos, paquete, nodo, frescura, límites, precondición y autorización humana cuando aplique.
6. Ejecutar **una** acción; observar postcondición. “Click despachado” no equivale a éxito.
7. Continuar, reobservar/replanificar dentro del presupuesto, bloquear o terminar con evidencia.

Límites iniciales propuestos: una tarea activa, máximo 10 acciones, 60 segundos en la demo, dos reintentos solo para observación/acciones idempotentes, tres estados sin progreso como señal de parada. Son parámetros de V09, no capacidades medidas del S23. Para otras tareas deberán elegirse presupuestos acordes.

Tabla de políticas inicial:

| Operación | Política propuesta |
|---|---|
| Leer versión de sistema/capacidades | Permitida dentro de la tarea |
| Abrir Configuración y leer pantalla de versión | Macro determinista autorizada, sin cambiar ajustes |
| Lectura de otras apps | Solo paquetes y campos expresamente permitidos |
| Capturas | Bajo demanda, alcance mínimo y retención temporal; excluir ventanas sensibles |
| Introducir texto | Solo en destino resuelto y autorizado; no contraseñas/OTP |
| Enviar, publicar, pagar, borrar o cambiar seguridad | Fuera del catálogo inicial; en ampliaciones, confirmación ligada al efecto exacto |
| Instalar/desinstalar, root, desbloqueo o shell arbitraria | No incluidos |
| Cancelar | Siempre disponible; bloquea nuevos despachos y cancela inferencia |

Confirmación futura: task ID, acción, destino y parámetros, caducidad y un solo uso. Una pantalla que diga “el usuario autoriza” es **dato no confiable**. Ni texto recuperado de Drive ni salida del modelo pueden ampliar la allowlist. Los prompts no sustituyen barreras ejecutables.

Tras timeout o fallo de conexión en una acción con posibles efectos, devolver `unknown` y verificar antes de reintentar. Cancelar no revierte un gesto ya emitido o un envío completado. Guardar estado mínimo para que un reinicio no repita automáticamente acciones de efecto externo.

## Distribución y condiciones de plataforma

Google Play distingue automatización determinista acotada de un agente que inicia, planifica y ejecuta decisiones autónomamente mediante Accessibility. La política actual restringe este último caso salvo herramientas de accesibilidad que cumplan su propósito específico. No declarar `isAccessibilityTool=true` si MESTRY no es una herramienta destinada a ese fin. [A14](EVIDENCE.md#android-agentes-e-inferencia).

**No se recomienda publicar un agente de autonomía abierta en Play bajo esta arquitectura.** Investigar primero acciones deterministas y un prototipo personal controlado. La vía de distribución y el cumplimiento de condiciones de las aplicaciones objetivo requieren decisión antes de ampliar autonomía; instalación privada no demuestra compatibilidad con términos ajenos ni autoriza eludir protecciones. La pantalla dañada del usuario no convierte automáticamente al proyecto en una herramienta de accesibilidad elegible.

## Runtimes locales

| Runtime | Evidencia Android | Ventaja | Riesgo y selección |
|---|---|---|---|
| **llama.cpp** | Binding Android, NDK y guía Termux mantenida | GGUF, cuantización, CPU ARM, gramáticas y server para investigación | Primera referencia experimental; fijar commit, template y parser |
| **LiteRT-LM** | Runtime Google edge, APIs Android/Kotlin y tool use | Integración Android y modelos/preparación para aceleradores | Segunda comparación; no trasladar resultados de otros SoCs al S23 |
| **MLC LLM** | SDK Android y runtime compilado | GPU y optimización por backend | Requiere artefactos/compilación más específicos; considerar tras medir necesidad |
| Servidor de inferencia en Termux | Puede facilitar benchmark de runtime elegido | Separa cliente de prueba del motor | Otro proceso/puerto; laboratorio, no requisito de producción |

CPU es baseline portable. Vulkan/GPU, OpenCL, QNN/NPU o kernels optimizados solo después de verificar soporte del driver, build y modelo exactos. El nombre Snapdragon no demuestra acceso al Hexagon desde un runtime ni mejora automática. PRoot no añade drivers GPU/NPU. No introducir otro gestor de modelos solo para servir un archivo si el binding nativo basta. [M01–M04](EVIDENCE.md#android-agentes-e-inferencia).

## Candidatos de modelo y orden de pruebas

| Candidato | Uso propuesto | Español y acciones estructuradas | Condición |
|---|---|---|---|
| **Reglas y clasificador pequeño** | Catálogo cerrado y demo inicial | Dataset de paráfrasis españolas y abstención | Baseline obligatorio; puede ser la solución final |
| **Qwen3-1.7B**, no thinking | Interpretar instrucciones y proponer JSON/tool calls | Ficha multilingual y capacidades de agente; español práctico no medido | Primer LLM de comparación, Q4 y contexto acotado; Apache-2.0 |
| **FunctionGemma 270M** | Seleccionar pocas funciones | Especializado en llamadas; ficha evalúa inglés y recomienda ajuste específico | Candidato de especialización, no diálogo general ni español certificado; revisar términos Gemma |
| **Qwen3.5-2B**, preferentemente no thinking para prueba inicial | Texto y eventualmente comprensión visual | Ficha multilingual, visión y herramientas | Exploratorio; validar GGUF/runtime, parser y memoria. Advertencia de bucles thinking en su ficha |
| Modelo mayor | Solo si los pequeños fallan tareas importantes | No inferir mejor éxito global de más parámetros | Pospuesto hasta tener RAM/energía y fallos medidos |

Fuentes [M05–M07](EVIDENCE.md#android-agentes-e-inferencia). Estos candidatos no constituyen una búsqueda del modelo “más nuevo” ni un ranking de benchmarks externos. Se eligen por tamaño, propósito y evidencia de interfaces; un candidato nuevo no sustituye el baseline durante el ensayo.

Presupuesto **estimado de pesos**, no de RAM de proceso: a 4 bits, `parámetros × 0,5 bytes`; 1,7B ≈ 0,85 GB y 2B ≈ 1 GB antes de escalas, capas no cuantizadas, KV, buffers y contexto. No usar esta cuenta como promesa de consumo. PSS de Android y memoria disponible deciden qué cabe. Visión añade encoder, proyector y tokens de imagen; empezarla solo cuando jerarquía/reglas no basten.

Restringir salida con JSON Schema/gramática mejora sintaxis. No garantiza que la función elegida, argumentos, nodo o resultado sean correctos. Tool calling depende de **checkpoint + template + parser + catálogo + runtime**; se registra esa combinación completa. No anunciar soporte de un Qwen concreto a partir de una página genérica de tools que no enumere ese formato. Para catálogo cerrado puede bastar JSON restringido y validación independiente.

No se prescribe temperatura como si fuese resultado experimental: V08 fija un perfil reproducible por modo y lo conserva en el ensayo. Comparar calidad antes de reducir temperatura o añadir reasoning; thinking consume latencia y puede no terminar en modelos pequeños. Límite de tokens y timeout pertenecen al ejecutor, no al criterio del modelo.

## Demostración inicial

Instrucción: **“Abre Configuración, identifica la versión de Android y devuelve el resultado verificado”.**

Secuencia propuesta:

1. Comprobar dispositivo permitido, servicio habilitado y sesión desbloqueada. Si falta algo, `blocked` con causa.
2. Capturar la versión del sistema mediante `Build.VERSION.RELEASE` y `SDK_INT`, con timestamp. Es la referencia determinista del ensayo.
3. Abrir la pantalla de información del dispositivo con intent oficial cuando lo admita; observar paquete Configuración. En Samsung puede ser necesario navegar a Información de software mediante una macro por nodos/texto/IDs observados, nunca coordenadas supuestas.
4. Leer el valor mostrado de Android, registrar localizador/observación y comparar con el dato de plataforma. Si UI y API discrepan, devolver discrepancia; no escoger el valor que “parece” correcto.
5. Responder con valor, SDK, fuente API, evidencia UI y estado de verificación. Si solo se pudo leer API, informar éxito de consulta y **demostración UI incompleta**; no declarar completada toda la tarea.
6. Aceptar cancelación en cada frontera de acción y liberar observaciones/capturas.

Dos superficies concordantes no constituyen verificación independiente del firmware firmado, pero sí verifican que la navegación/lectura produjo el valor esperado. No se ejecutó esta secuencia.

## Qué medir antes de escalar

Separar evaluación de intención/tool calling offline (V08), ejecución de UI (V09) y convivencia/térmica (V10). Medir latencia p50/p95, carga fría/caliente, PSS/memoria disponible, energía con baseline, temperatura de batería, estado térmico del sistema, sintaxis y semántica de acciones, éxito verificado, falsas declaraciones de éxito, recuperación y cancelación. Registrar pruebas bloqueadas/fallidas; no eliminarlas del denominador para mejorar tasa.

La elección final es el componente de **menor costo total que supere las pruebas**, incluyendo un resultado sin LLM. No se necesita MESTRY Core ni RAG para completar esta demostración.
