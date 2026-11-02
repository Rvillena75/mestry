# MESTRY — Revisión del plan y brechas de implementación

Fecha: **01/11/2026**, America/Santiago. Revisión del código, planes y evidencia
existentes; comprobaciones actuales de lectura en WSL, GitHub y el S23 por el
servidor ADB existente y el SSH autorizado. Sin implementar automatizaciones,
iniciar servicios, ejecutar turnos Codex ni modificar sincronizadores.

## Resultado

La siguiente etapa de desarrollo es **H1: demostrar continuidad de trabajo por
GitHub entre WSL y S23**. La publicación pública de MESTRY completó la base Git
de H2, pero no demuestra recepción, ejecución o publicación desde el teléfono.
H2 sigue parcial; H3 no está implementada. H4 tiene componentes parciales y H5
conserva sus pruebas físicas pendientes.

Hay además un prerrequisito operativo actual: **Termux acepta SSH, pero Horus
no tiene procesos observables y los puertos 8022/8787 rechazan conexiones**.
Para ejecutar el laboratorio habrá que abrir el entorno existente y revalidar
su perfil. Esto no exige reiniciar H0 ni reinstalar nada.

## Qué plan prevalece

1. [Informe 09, §H](09_REORIENTACION_CONTINUIDAD_TRABAJO.md#h-plan-mínimo-de-implementación-y-pruebas):
   fases H0–H5 de continuidad de **proyectos**, no de conversaciones.
2. [Informe 10, §H](10_CIERRE_H0_VERIFICACION_REAL.md#h-preparación-concreta-de-h1):
   laboratorio, límites y criterios concretos para aceptar H1.
3. [Informe 11](11_CORRECCIONES_POST_H0.md): correcciones del 27/10; sus éxitos
   no sustituyen una comprobación actual de disponibilidad.
4. [Publicación GitHub](../../GITHUB_PUBLICATION.md): base pública autorizada
   el 27/10. Sustituye la propuesta de H2 de hacer este repositorio privado;
   no convierte en públicos otros proyectos ni el laboratorio de prueba.

El [plan 06](06_PLAN_IMPLEMENTACION_Y_PRUEBAS.md) conserva componentes de la
propuesta D anterior. No desarrollar su gateway Windows para compartir hilo,
coordinador de propietario/épocas ni transferencia de conversaciones. El resto
del roadmap de producto se conserva como antecedente, sin desplazar H1 por RAG
o por otra instalación Linux.

## Estado por incremento

| Etapa | Estado | Ya disponible | Desarrollo o validación que falta |
|---|---|---|---|
| **H0 — inventario y accesos** | **Cerrada históricamente; preflight actual parcial** | Inventario de Alpine/perfiles, herramientas y GitHub acreditado en 10/11; ADB y SSH Termux funcionan hoy | Reabrir el guest existente y comprobar perfil, herramientas y GitHub antes del lab. No repetir la auditoría completa ni dar por caducadas credenciales sin probarlas |
| **H1 — laboratorio de continuidad** | **Sin cierre ni implementación localizada** | Protocolo detallado y herramientas históricamente admitidas | Fixture, dos clones, ida/vuelta de commits, pruebas en ARM64/WSL, segunda cuenta por turnos y casos negativos de dirty/untracked/divergencia/uso activo/red |
| **H2 — base Git y flujo Windows** | **Parcial** | Repo público, clon fuera de rclone, ignores/attributes, AGENTS, fuentes reproducibles y documentación; publicación manual verificada | Acciones `start/finish/receive/check`, contrato de entorno, estado de trabajo mantenido y exclusión local del checkout durante toda la tarea. Validar ambas cuentas sin compartir homes |
| **H3 — recepción/publicación S23 y proyecto en S25** | **No implementada ni aceptada como flujo Git** | Bridge/cliente/supervisor desarrollados y probados históricamente; S25 funcionó según usuario | Clon operativo independiente, autenticación vigente del perfil, fetch/aviso, recepción solo en puntos seguros, publicación revisada, validación por plataforma y admisión del proyecto en el cliente |
| **H4 — documentos y recuperación autónoma** | **Parcial** | Broker/navegador/publicador acotados; FolderSync corregido y transferencias verificadas el 27/10 | Conciliar autoridades e IDs de las raíces, lectura de un documento autorizado vigente en los destinos requeridos, datos por hash, copias de recuperación y restore alternativo sin PC. No equiparar TwoWay con backup |
| **H5 — disponibilidad prolongada** | **Pendiente de aceptación** | SSH/Boot y supervisión existentes; controles históricos de salud y recuperación | PC realmente apagado, cargador de pared, reposo/tarea activa, 24 h y procedimiento de arranque/desbloqueo. Fallos de bridge/UID/reinicio requieren protocolo y autorización específica |

Los estados «no implementada/localizada» se refieren al código y evidencia
disponibles. No se inspeccionó el filesystem privado del guest detenido ni se
concluye que esté vacío, que haya perdido proyectos o que sus logins hayan fallado.

## Comprobaciones actuales y límites

| Evidencia | Resultado observado el 01/11 |
|---|---|
| Git local y remoto | `main` local y `refs/heads/main` remoto: `0499557b70eef14a3fce993ee6a8935fe2a0f053`; working tree limpio al iniciar la revisión |
| Scripts de sesión previstos | No existen `tools/work-session.sh`, `tools/check-env.sh` ni `tools/WorkSession.ps1` |
| Estado del proyecto | No se localizó `STATUS.md`; AGENTS/README/documentación sí existen. Un archivo llamado STATUS no es obligatorio si se reutiliza otro registro mantenido |
| Laboratorio WSL | Ausentes las rutas previstas `~/mestry-lab/continuidad-trabajo-v1` y su auxiliar |
| Remoto sintético previsto | Consulta exacta a `Rvillena75/mestry-continuidad-lab`: HTTP 404 con la conexión actual. No prueba inexistencia de laboratorios con otro nombre/propietario |
| S23 USB | Servidor ADB Windows reutilizado, equipo esperado revalidado por serial y **SM-S918B**, estado **device**, Android **16**. Solo aparece S23 en esa enumeración |
| Versiones instaladas | Horus **1.1.0 / 6**, FolderSync **4.14.0**. Esto acredita instalación, no ejecución ni autenticación vigente |
| Procesos Horus | `pidof` del proceso principal y de `:terminal` sin resultados; enumeración adicional por UID real del paquete: **0 procesos**, sin consultar argumentos ni contenido de tareas |
| Paquete Horus | Instalado, no oculto/suspendido; `stopped=false`, `enabled=0` — valor predeterminado de Android, no «deshabilitado» |
| SSH Termux | Sesión nueva autenticada con el alias existente, UID Termux esperado |
| Puertos dentro del S23 | 8022 y 8787: `connect_ex=111`; `/healthz` no accesible por conexión rechazada |
| Causa del estado Horus | No determinada. Los registros de salida consultados incluyen eventos antiguos de actualización; no justifican atribuirles la indisponibilidad actual |
| Alimentación/temperatura | USB=true, AC=false, batería 79%, temperatura 26,1 °C en la muestra. No acredita independencia física del PC |
| No revalidado hoy | Guest Alpine, Git/gh/Codex del guest, logins, workspace privado, pares/último resultado FolderSync y circuito S25 extremo a extremo |

`tools/mestry_session.py` es un registrador de experimentos SSH/ADB: su nombre
no implica que ya implemente el inicio/cierre de trabajo Git. Los locks del
publicador o del supervisor tampoco sustituyen un control de uso del checkout.

## Orden concreto para continuar

### 1. Recuperar disponibilidad del entorno existente

Abrir Horus normalmente en el S23; iniciar sesión local si la pide y retomar
Bare terminal del perfil `/home/horus`. Comprobar el guest y sus herramientas;
si procede, usar los controladores **ya instalados** del bridge y supervisor
después de confirmar su estado. No ejecutar instaladores, migraciones ni la
configuración de ejemplo del repositorio público.

**Aceptar:** perfil y workspace correctos, Git/GitHub de ese perfil verificados;
bridge saludable si se va a usar S25. La terminal por sí sola basta para el
laboratorio Git, sin convertir la recuperación del cliente S25 en otra auditoría.

### 2. Ejecutar H1 sobre un alcance sintético

Mantener los destinos previstos del informe 10: dos clones aislados y un remoto
de prueba, sin usar datos reales. Crear `calc.py`, prueba stdlib, README, AGENTS,
estado e ignores/attributes. La publicación pública de MESTRY no sustituye esta
prueba ni autoriza subir archivos de prueba a `main` por defecto.

**Aceptar:** WSL publica, S23 recibe y ejecuta la misma versión; S23 modifica y
publica, la segunda cuenta WSL recibe y ejecuta; hashes/commits/pruebas por target.
Demostrar bloqueos sin pérdida con archivos nuevos, cambios locales, divergencia,
proyecto ocupado y remoto no disponible. Un `.env` sintético no debe publicarse.

### 3. Completar H2 y después incorporar H3

Implementar el script Bash de sesión y el comprobador de entorno; PowerShell
es solo una entrada opcional a WSL. Reutilizar documentación existente para el
estado y registrar qué se probó, qué quedó sin publicar y qué debe continuar.
Validar primero en H1, luego admitir MESTRY con una configuración local privada.

**Aceptar:** `start` reconoce el estado y prepara solo un checkout libre/limpio;
`finish` selecciona cambios revisados, prueba y confirma la ref publicada;
`receive` preserva trabajo local y el último entorno funcional; `check` muestra
publicación, recepción, entorno y errores por separado. Empezar en S23 con
**fetch + aviso** hasta cubrir todos los puntos de entrada que escriban o ejecuten
pruebas. Un `git status` limpio no demuestra que no haya una tarea activa.

Estas acciones se describen para el siguiente incremento; no se ejecutaron
durante esta revisión. La autorización anterior de publicación de MESTRY no se
extiende por defecto a nuevos repositorios, instalaciones, escrituras en S23 o
ensayos de fallo. La política de publicación automática sigue por definir.

## Pendientes de producto más allá de la continuidad

Según la [trazabilidad arquitectónica](../../auditorias/2026-10-26/03_TRAZABILIDAD_ARQUITECTONICA.md)
y la inspección del código actual, quedan fuera de lo implementado:

- Catálogo/caché documental con cursor de cambios incremental, invalidación y
  frescura; el paginado de `files.list` del navegador no equivale a ese pipeline.
- Extracción/indexación, búsqueda documental con citas y evaluación RAG.
- Edición nativa general de Docs/Sheets/Slides y control general de acciones;
  el publicador fijo por revisiones solo resuelve un caso acotado.
- MESTRY Core y contratos compartidos de herramientas, intención, memoria y
  permisos; el bridge de desarrollo no acredita el Core del asistente.
- Voz/STT/TTS, teclado/overlay, secretaría, conectores personales y Device Agent.
  Las cinco fuentes normativas previas siguen sin constar en este repositorio;
  recuperar sus originales antes de inventar requisitos de esas etapas.

No se reintroduce sincronización de conversaciones, un backend adicional en S25,
un coordinador distribuido ni otra distribución Linux para cubrir estas brechas.

## Registro y archivos afectados

Lecturas: `git status/log/ls-remote`; existencia de scripts/rutas; API de
metadatos del remoto sintético; servicios del servidor ADB existente
`host:devices-l`, selección del transporte conocido y comandos shell acotados
`getprop`, `dumpsys package`, `pidof`, `ps` por UID, `dumpsys battery` y metadata de salida;
SSH Termux con UID, sockets loopback y health. Sin lectura de conversaciones,
claves o archivos de autenticación; sin volcar entornos ni logs de otras apps.

Se añade este seguimiento y un encabezado vigente en ROADMAP. Se corrigen dos
referencias al nombre del informe 10 que el saneamiento público convirtió por
error en `DRIVE_ID_01_EXAMPLE.md`. No se cambian los originales históricos o
congelados, código, dispositivos, permisos, configuración de red o sincronizadores.
No se repiten los 82 tests por cambios exclusivamente documentales. Sin commit
ni push durante esta revisión; el informe queda local en el clon de desarrollo.
