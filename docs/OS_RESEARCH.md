# Sistemas operativos y selección del entorno

**Revisión R2 — 2026-10-19, America/Santiago. Propuesta sin aprobar.** La ejecución de Codex en el S23 es ahora una condición de selección. Cloud y hosts externos no pueden ganar por promedio una comparación que exige ejecución local. [Fuentes](EVIDENCE.md), [Codex y experiencia visual](CODEX_REMOTE_RESEARCH.md), [protocolos](VALIDATION_PLAN.md).

## Corrección de la evaluación anterior

La matriz R1 recomendaba Android + Cloud al valorar independencia del PC y menor administración. Ese criterio era insuficiente para la prioridad aclarada: **harness, repositorios y comandos de Codex deben estar en el S23**, además de existir una interfaz visual multiproyecto desde el S25. La recomendación R1 y sus totales quedan sustituidos; no eran decisiones aprobadas.

La app oficial Linux ARM64 merece una evaluación como candidata principal, no una nota secundaria. Está publicada para Debian 13 de escritorio. Eso permite formular un experimento razonable en PRoot, pero no permite declararlo compatible. Ninguna ruta local ha sido ejecutada ni demostrada en este dispositivo.

## Inventario pendiente

Solo se conoce lo declarado: S23 Ultra, 256 GB, Snapdragon 8 Gen 2 for Galaxy, pantalla dañada y uso principalmente Wi-Fi. RAM, almacenamiento libre, Android/API, One UI, modelo SM-S918 completo, CSC, firmware, estado de batería, kernel y bootloader siguen pendientes de V00. No se asume que sea desbloqueable ni que permita namespaces, KVM o un servidor gráfico persistente.

## Candidata principal: Android OEM + Debian 13 ARM64 en PRoot

Cadena propuesta: **Android → Termux → PRoot-Distro/Debian 13 ARM64 → app oficial Linux**, con Termux:X11 como display local. No reemplaza Android, no virtualiza otro kernel y no requiere desbloquear el bootloader. El userland glibc de Debian resuelve una clase de problemas ABI que Termux/Bionic puede presentar, pero las llamadas al sistema siguen alcanzando el kernel Android bajo las restricciones de su UID y SELinux. [T01–T02, N01–N03](EVIDENCE.md).

| Capa | Evidencia favorable | Incertidumbre o bloqueo que debe medirse |
|---|---|---|
| Aplicación | OpenAI ofrece paquete `.deb` ARM64 y soporta Debian 13 **desktop** | No publica soporte Android/PRoot; falta inspeccionar control, dependencias y ejecutables del paquete fijado |
| ABI y herramientas | Debian ARM64 puede proporcionar glibc y herramientas Linux | Binarios auxiliares, resolución de rutas, locks, sockets, PTY y subprocesses no quedan probados por abrir una ventana |
| Sesión gráfica | Termux:X11 documenta uso con PRoot y `--shared-tmp` | APK y componente Termux coherentes, DISPLAY, Xauthority y D-Bus; estabilidad de foco, portapapeles y teclado remoto |
| GPU | Android conserva sus drivers OEM | Eso no proporciona automáticamente OpenGL/Vulkan de escritorio dentro de Debian; empezar con renderizado compatible y medir, sin prometer aceleración Adreno |
| Servicios | Un escritorio ligero puede usar D-Bus de sesión | PRoot no garantiza systemd, keyring, portal de escritorio o apertura del navegador por `xdg-open` |
| Sandbox de interfaz | Debe conservarse la protección del motor gráfico/renderer | Un usuario aparente no root evita una clase de rechazo de arranque, pero no crea namespaces reales; no aceptar `--no-sandbox` como solución rutinaria |
| Sandbox de comandos | Codex documenta bubblewrap en Linux | Existe reporte específico Debian 13/PRoot con fallo de aislamiento; debe pasar prueba negativa real |
| Autenticación | Login oficial ChatGPT documentado | Callback/browser/keyring en esta topología; persistencia y renovación sin trasplantar tokens del PC |
| Remoto | Puede compartirse un display X ya existente | Termux:X11 **no es** un servidor remoto; hace falta validar la cadena VNC privada descrita abajo |

La app se documenta actualmente como **ChatGPT desktop app con Codex integrado** y el ejecutable como `chatgpt`. No se busca ni se instala un supuesto paquete Android oficial de Codex. La preview no ofrece todavía Computer Use para Linux; esto no impide usar Codex con archivos/comandos ni reemplaza el futuro Device Agent Android. [O12/N01](EVIDENCE.md).

### Bloqueo de seguridad con evidencia específica

El [reporte #47402](https://github.com/openai/codex/issues/47402) describe Codex 0.156.0 ARM64 dentro de Termux/PRoot/Debian 13: login y herramientas sin sandbox funcionan, pero el aislamiento normal falla. Es un reporte de usuario reproducible, **no una prueba en nuestro S23 ni demostración de que toda versión posterior falle**. También explica por qué `doctor` favorable o `unshare` con salida cero no son pruebas suficientes: PRoot puede presentar una vista sintética. [N04](EVIDENCE.md#revision-r2-fuentes-nuevas).

Hay tres fronteras distintas: sandbox del renderer, sandbox de ejecución de Codex y sandbox Android del UID Termux. **PRoot no añade una cuarta frontera fiable entre procesos del mismo UID.** Ni aprobación humana ni `workspace-write` escrito en una UI demuestran enforcement. Si el paquete solo arranca sin protección del renderer, o Codex solo ejecuta comandos con acceso completo, esta candidata falla la puerta del piloto seguro; no se remedia con root ni cambios de kernel en esta fase.

### Display y acceso gráfico desde S25

Propuesta a validar: app y escritorio ligero en un único display Termux:X11; **TigerVNC `x0vncserver`** comparte ese display hacia loopback; S25 utiliza un visor con túnel SSH autenticado sobre la red privada S25–S23. El paquete scraping de TigerVNC existe para Debian 13 ARM64. No modifica el servidor X ni convierte el S25 en ejecutor. `x0vncserver` puede escuchar en todas las interfaces por defecto: exigir localhost y comprobarlo. [N08](EVIDENCE.md#revision-r2-fuentes-nuevas).

El README actual de Termux:X11 también describe menor CPU para Termux cuando X11 ocupa el primer plano y una variante `sharedUid` que requiere la firma de Termux GitHub, incompatible con las otras fuentes indicadas. Es una opción de empaquetado a auditar, no un ajuste rutinario: comparte autoridad dentro del UID y no justifica desinstalar apps con datos ni garantiza sobrevivir al reposo. Medir primero la configuración ordinaria y registrar fuente/firma exactas. [N02](EVIDENCE.md#revision-r2-fuentes-nuevas).

La combinación exacta X11/PRoot/extensiones X/visor SSH no está probada. `x11vnc` comparte displays pero su repositorio se declara sin mantenedor; no se prefiere al TigerVNC mantenido. Una sesión **Xvnc** virtual puede ser un experimento secundario si el display Termux:X11 no sigue disponible con pantalla apagada: conserva la app Linux, pero es otra configuración gráfica que debe documentarse, no un resultado favorable atribuido a Termux:X11.

En S25, que el escritorio remoto sea visible no garantiza comodidad táctil. Medir cambio entre proyectos, lectura de diff y aprobaciones. No se diseñan teclados propios. No se recomienda trasladar a Android instrucciones de Tailscale Serve/Tailscale SSH de un host Linux: Android necesita un servidor OpenSSH separado. [T03–T05](EVIDENCE.md).

## Respaldo local: app-server sin escritorio completo

**Android OEM + Termux; Codex y un bridge app-server en el S23; cliente visual en S25.** Probar primero la compatibilidad nativa, sin suponer que Linux musl = Android soportado; si un fallo ABI/rutas lo justifica, repetir en Debian ARM64. Evita la carga del escritorio, pero no elimina dependencias del harness, autenticación, locks, sockets, sandbox o lifecycle Android.

Se prefiere para el primer piloto de respaldo el transporte stdio de chenhaoc, **después de corregir sus permisos y endpoints**. Scouthe requiere además el servicio/socket Unix compartido. Sus APK son clientes, no hosts. Los tres proyectos tienen bloqueos de adopción de seguridad/procedencia: [auditoría fijada por commit](FRONTEND_AUDIT.md). Un wrapper no soluciona un binario Codex incompatible.

El [reporte #49402](https://github.com/openai/codex/issues/49402) distingue una regresión Unix de Termux nativo en 0.159.1 frente a 0.154.0; el reporte está cerrado, sin que ese estado por sí solo pruebe un arreglo. El [#26277](https://github.com/openai/codex/issues/26277) describe otro fallo de startup lock. No trasladar diagnósticos de esos teléfonos al S23 sin V02. No se propone instalar versiones antiguas vulnerables ni eliminar checks de aislamiento para pasar. [N04](EVIDENCE.md#revision-r2-fuentes-nuevas).

<a id="windows-arm-nativo-investigacion-abierta-instalacion-bloqueada"></a>
## Windows ARM nativo: investigación abierta, instalación bloqueada

Windows 11 ARM64 y la app oficial ARM64 existen. **No se encontró un puerto funcional documentado para el S23 Ultra exacto**, y tampoco se conoce la variante del usuario. Se reconsultaron Renegade/edk2-msm y WOA-Drivers y se buscaron `S23 Ultra`, `SM-S918`, `dm3q`, `SM8550`, Windows y UEFI. En edk2 hay trabajo SM8550 y una placa **dm1q/S23 base**; no se identificó dm3q/S23 Ultra. Los árboles de referencia siguen en [W01–W03](EVIDENCE.md#windows-firmware-y-hardware). Una búsqueda pública negativa tiene confianza media sobre ausencia global, no prueba imposibilidad.

Los resultados TWRP, kernels Android o `flash_windows.bat` —un script que se ejecuta **desde** Windows— no prueban que Windows arranque **en** el teléfono. Firmware de Android o una imagen genérica Qualcomm no sustituyen drivers Windows de la placa.

| Puerta documental | Evidencia requerida para la variante exacta | Situación |
|---|---|---|
| Identificación y firmware | SM-S918 completo, CSC, build, cadena de arranque y versiones permitidas | Pendiente V00; no se leyó el teléfono |
| Bootloader | Documentación de desbloqueabilidad de ese modelo/firmware y estados OEM Lock/KnoxGuard | No comprobada; liberación de operador no equivale a bootloader libre |
| UEFI y ACPI | Puerto dm3q mantenido, inicialización/particiones y tablas coherentes | No identificado en fuentes revisadas |
| Almacenamiento UFS | Driver Windows, integridad y recuperación de datos demostrados | No identificado |
| Pantalla, táctil y GPU | Panel exacto, entrada y driver WDDM estable | No identificados |
| Wi-Fi/USB/red | Conectividad estable y recuperación USB | No identificados; esenciales para servidor remoto |
| PMIC/carga/temperatura | Gestión real de alimentación, USB-C/PD y térmica | No identificada; arranque no valida uso continuo |
| Seguridad y updates | Requisitos Windows, firma de drivers, TPM/arranque, actualizaciones y rollback | No demostrados |
| Recuperación | Paquete íntegro de firmware y procedimiento mantenido de vuelta al estado previo | No demostrado; no autoriza flasheo |

Las familias B/B-DS, U/U1, W, N o 0 son ejemplos de sufijos a identificar, **no una tabla universal de desbloqueabilidad**. Magisk documenta restricciones regionales y requisitos de Samsung; Knox documenta cambios irreversibles del Warranty Bit por componentes no aprobados. No se asume que toda operación de desbloqueo produzca el mismo efecto, ni se solicita hacerlo. [W05–W06](EVIDENCE.md).

**Clasificación:** un sistema Windows utilizable en este S23 es **no viable con la evidencia actual**; desarrollar un puerto sería **experimental y de alto riesgo**. La línea de investigación permanece abierta: reconsiderar solo tras evidencia de placa/variante, drivers y recuperación. No se recomienda como siguiente experimento reversible. Windows 10 ARM no elimina ninguno de estos bloqueos ni aporta ventaja demostrada.

La compatibilidad de aplicación es un segundo nivel: OpenAI publica MSIX ARM64, pero faltan inspección del manifiesto/dependencias de la versión fijada, login, repositorios/hilos, shell y sandbox sobre ese hipotético port. No se afirma que Microsoft Store sea imprescindible: hay descarga oficial MSIX. MXC y sandbox legacy tienen requisitos distintos; tener GUI Windows o soporte ARM no prueba ninguno. [O06–O08](EVIDENCE.md).

## Windows virtualizado, emulado y compatibilidad

| Técnica | Distinción | Evaluación actual |
|---|---|---|
| QEMU x86/x64 con TCG | Windows completo con traducción de ISA | Reversible, pero suma Windows, app y Android con RAM desconocida; sin benchmark útil, no candidata prioritaria |
| QEMU ARM64 con TCG | Windows ARM completo, emulación software | Misma ISA no equivale a aceleración; firmware/drivers virtuales y consumo pendientes |
| QEMU/KVM ARM64 | Virtualización real si el kernel permite acceso | No acreditada para una app sin privilegios en este S23 stock |
| AVF/pKVM | Marco Android con permisos/payloads acotados | No demuestra VM Windows general disponible para Termux |
| Winlator/Wine/Box64 | Compatibilidad de aplicaciones Windows | No es Windows; app Codex/MSIX, sus servicios y sandbox NT no acreditados |
| RDP a otro Windows | Control de otro host | Puede mostrar la app, pero no ejecuta Codex en el S23 |

[W07–W09](EVIDENCE.md). No se inventan tiempos, RAM, FPS ni rendimiento de compilación. QEMU/TCG es **experimental con riesgo operativo**, sin implicar el riesgo de brick de un flasheo. No se recomienda invertir primero en una VM Windows cuando existe una app ARM64 Linux sin guest Windows. Una VM que solo arranca no supera V03/V04; exigir aplicación, herramientas y continuidad útiles.

## Matriz ponderada y puertas obligatorias

Antes de puntuar: **G1** ejecución en S23 sin PC; **G2** interfaz visual que permita varios proyectos/hilos; **G3** aislamiento efectivo y acceso privado; **G4** instalación reversible preservando Android, salvo una futura decisión expresa basada en soporte real. Fallar una puerta elimina la alternativa del piloto. Una puerta pendiente impide declarar ganadora verificada.

Escala de adecuación: 0 incumple/bloqueado; 1 pobre; 2 parcial; 3 buena con condiciones; 4 cobertura directa. **ND** = faltan datos; intervalos = hipótesis acotada, no medición. No sumar ND como cero ni como valor medio. Se mantienen los trece criterios pedidos, pero se corrige la selección anterior.

| Criterio | Peso | Justificación |
|---|---:|---|
| Compatibilidad de Codex | 18 | App/harness, tools, historial y recuperación son el requisito central |
| Funcionamiento sin PC | 8 | Es condición obligatoria además del peso; no compensable |
| Facilidad visual multiproyecto | 14 | Una shell única no cumple la experiencia solicitada |
| Hardware S23 | 8 | Drivers y Wi-Fi deben conservarse |
| Estabilidad | 8 | Recuperación y pantalla apagada forman parte de la utilidad |
| Rendimiento | 6 | Interacción y tools deben ser cómodos, sin extrapolar benchmarks |
| Energía/temperatura | 5 | Operación prolongada en teléfono |
| Seguridad | 12 | Condición obligatoria; ni sandbox omitido ni tokens expuestos |
| Mantenimiento | 7 | El sistema debe ahorrar tiempo al usuario |
| Riesgo de instalación | 6 | Se prefieren experimentos reversibles y Android intacto |
| Integración Android | 4 | Debe seguir disponible para Device Agent |
| Extensibilidad Drive/RAG | 2 | Contratos simples, sin complejidad por sí misma |
| Costos | 2 | Se usa hardware existente; gastos adicionales no autorizados |
| **Total** | **100** | |

| Criterio | App Linux/PRoot/X11 | app-server Termux | app-server Debian/PRoot | Windows nativo S23 | Windows QEMU |
|---|---:|---:|---:|---:|---:|
| Codex | 1–4 | 1–3 | 1–3 | ND | ND |
| Sin PC | 4 | 4 | 4 | ND | 4 |
| Facilidad visual | 3–4 | 2–3 | 2–3 | ND | ND |
| Hardware | 4 | 4 | 4 | 0 | 2–3 |
| Estabilidad | ND | ND | ND | ND | ND |
| Rendimiento | ND | ND | ND | ND | ND |
| Energía | ND | ND | ND | ND | ND |
| Seguridad | ND | ND | ND | ND | ND |
| Mantenimiento | 1–2 | 2–3 | 1–2 | 0–1 | 1 |
| Riesgo instalación | 3 | 3 | 3 | 0 | 3 |
| Android | 4 | 4 | 4 | 0 | 3 |
| Extensibilidad | 3 | 3 | 3 | ND | 2 |
| Costos | 3–4 | 3–4 | 3–4 | ND | 1–2 |
| **Puertas actuales** | G1/G2 plausibles; G3/G4 pendientes | G2/G3/G4 pendientes | G2/G3/G4 pendientes | G3/G4 sin soporte | G2/G3 sin evidencia útil |
| **Total** | No calculable todavía | No calculable todavía | No calculable todavía | No habilitado | No habilitado |

Razones de las diferencias: la app oficial tiene mayor paridad de UX potencial, pero más capas gráficas; app-server evita esas capas y añade mantenimiento de un cliente de terceros. Android conserva drivers, no garantiza supervivencia. Todos los candidatos Android reciben 3 en instalación porque paquetes, almacenamiento y credenciales tienen cambios reversibles, no riesgo cero. Windows nativo falla hardware/recuperación; QEMU conserva Android pero añade drivers virtuales y un guest. Costos incluyen cuotas Codex existentes/no comprobadas; no se presupone gratuidad.

Fórmula para la futura selección de alternativas que pasen puertas: `S = sum(peso * puntuacion) / 4`. Antes del ensayo se fijan los cortes de cada conversión de métricas a escala, usando los umbrales propuestos de V03/V04/V10; después de V00–V04 se completan las celdas y se conserva esa rúbrica, sin ajustarla retrospectivamente para favorecer una rama. **Publicar hoy un total preciso sería arbitrario.** La matriz pondera qué medir; la recomendación actual se basa en paridad potencial, reversibilidad y número de capas, con incertidumbre explícita.

## Clasificación y recomendación

| Alternativa | Clasificación en R2 | Papel |
|---|---|---|
| Debian 13 ARM64 desktop en hardware soportado + app | Viable con evidencia de producto | Referencia; no prueba el teléfono |
| S23/PRoot/Debian/X11 + app oficial | Potencialmente viable, pendiente de prueba | **Candidata principal condicionada**; primer experimento |
| S23/Termux o PRoot + app-server + cliente corregido | Potencialmente viable, pendiente de prueba | **Respaldo local**; no aprobar valores actuales de los bridges |
| Windows nativo S23 Ultra | No viable con la evidencia actual | Investigación abierta, sin procedimiento de instalación |
| Crear puerto Windows, Linux nativo o modificar kernel | Experimental y de alto riesgo | Proyecto distinto; fuera del piloto |
| Windows TCG | Experimental y de alto riesgo operativo | Baja prioridad; utilidad no demostrada |
| KVM stock/Winlator para app oficial | No viable con la evidencia actual | Capacidades esenciales no acreditadas |
| Cloud o Linux/Windows externo | Viable con evidencia como producto, **incumple G1** | Solo reconsiderar si el usuario cambia el requisito |
| PC actual con Remote | Viable con evidencia para acceso, **incumple G1/sin PC** | Referencia ocasional, no respaldo automático |

**Recomendación:** aprobar una arquitectura local en Android con dos interfaces sustituibles: app oficial Linux como candidata principal; app-server/stdio y cliente móvil corregido como respaldo. Se autorizarían pruebas por separado. Si ambas fallan aislamiento, disponibilidad o UX, registrar que la meta local no está demostrada y volver al usuario con ese resultado; no sustituirla silenciosamente por Cloud ni reducir seguridad para cerrar el diseño.
