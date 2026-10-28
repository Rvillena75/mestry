# MESTRY: prueba gráfica mínima del S23

**20 de octubre de 2026 — aceptación mínima cumplida.** Debian 13 ARM64 ejecuta `xterm` mediante Termux:X11 en el S23, sin root Android. El usuario confirmó que ve letras y `MESTRY_GUI_INPUT=PASS`; WSL verificó el marcador invitado de **06:58:56 UTC**. No se instaló ChatGPT/Codex ni XFCE.

| Elemento | Resultado |
|---|---|
| APK oficial normal | **1.03.01-fa3a8b4-06.10.26**, `com.termux.x11`, ARM64, sin `sharedUserId` |
| Integridad | SHA-256 **64995746d1887a0e70bc8977d4a9c5ea56e3e00eadd4a6eeab32ae6048ba733a**, coincidente con GitHub; firma APK v2 verificada |
| Paquete Termux | **termux-x11-nightly 1.03.01-6**, xkeyboard-config 2.48-1, repositorio X11 firmado |
| Cliente Debian | **xterm 398-1**; xauth, fuentes DejaVu y xdotool para foco; 33 paquetes nuevos con dependencias, sin Mesa/LLVM o escritorio |
| Display | **`:1`**, socket Unix compartido; TCP deshabilitado. Loopback IPv4/IPv6 y LAN WSL rechazaron puerto 6001 |
| Autenticación | Cookie privada MIT-MAGIC-COOKIE-1; cliente sin cookie rechazado, cliente autorizado conectado |
| Ventana e interacción | **PASS**, captura inspeccionada, confirmación humana y marcador dentro de Debian |
| Protecciones | SELinux Enforcing, bootloader bloqueado/Verified Boot green, UID real Termux 10348 y capacidades efectivas 0 |

La instalación siguió las [instrucciones oficiales de Termux:X11](https://github.com/termux/termux-x11), con el APK normal compatible con el Termux existente de F-Droid. La versión del loader del repositorio no es idéntica a la de la nightly; se conserva esa diferencia y se acredita compatibilidad funcional del par probado.

El primer intento mostró la ventana pero no recibía letras: el foco X11 estaba en PointerRoot. Se enfocó explícitamente el único `xterm` MESTRY y se añadió el enfoque al helper. El usuario volvió a escribir **MESTRY_OK**, pulsó Enter y confirmó el PASS. No se sustituyó esa prueba por entrada sintética.

[Captura visual inspeccionada, antes de escribir](validation/mestry-x11-20261020T052004Z/xterm_focus_corrected.png). La captura final adicional se omitió al estar otra aplicación al frente; no se capturó esa otra app.

Para iniciar una demo nueva desde WSL:

```bash
ssh mestry-s23 '$HOME/bin/mestry-x11 demo'
```

Abrir Termux:X11 en el S23. Si ya está la demo abierta, recuperar su foco con:

```bash
ssh mestry-s23 '$HOME/bin/mestry-x11 focus'
```

Para cerrarla y detener solo este servidor:

```bash
ssh mestry-s23 '$HOME/bin/mestry-x11 stop'
```

El wrapper Debian conserva su comportamiento anterior; únicamente `MESTRY_SHARED_TMP=1` activa `--shared-tmp`. Boot sigue iniciando solo SSH. La demo quedó abierta; no se añadió arranque automático de gráficos.

| Recurso | Antes | Después |
|---|---:|---:|
| RAM disponible, mediana | **3,23 GiB** | **2,88 GiB** |
| Instancia Debian | **196,21 MiB** | **221,87 MiB** |
| PREFIX + home Termux | — | **+31,18 MiB** |
| Código APK instalado, aparte | Ausente | **14,04 MiB** |
| Datos libres finales | — | **212,09 GiB** |

PSS del servidor + PRoot + xterm activos: **92,75 MiB**; visor Android **51,78 MiB** en otra lectura y fuera del primer plano. Son instantáneas con condiciones distintas; la diferencia de RAM global no se atribuye íntegramente a X11. Los datos privados del APK no se midieron. El rootfs ya está incluido en PREFIX. [Métricas originales y cálculos](validation/mestry-x11-20261020T052004Z/resources_summary.json).

El problema de socket descrito en el [issue #1115](https://github.com/termux/termux-x11/issues/1115) **no apareció en esta sesión**. La prueba tras reinicio sigue pendiente. Tampoco se acreditan estabilidad de 30 minutos, segundo plano prolongado o seguridad de la futura aplicación: V01 global continúa parcial. Las notificaciones del nuevo APK siguen sin conceder, pendientes de revisión manual para pruebas de continuidad; no se forzaron permisos.

[Registro completo, errores y reversión](INSTALLATION_LOG.md) · [Aceptación estructurada](validation/mestry-x11-20261020T052004Z/acceptance_review.json) · [Plan siguiente para revisión](CHATGPT_LINUX_ARM64_PLAN.md).
