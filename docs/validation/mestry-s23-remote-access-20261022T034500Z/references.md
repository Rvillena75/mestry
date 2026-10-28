# Fuentes primarias

- Tailscale Android: https://tailscale.com/docs/install/android
- SSH convencional: https://tailscale.com/docs/reference/ssh-over-tailscale
- Reglas grants: https://tailscale.com/docs/reference/syntax/grants
- Caducidad de equipo: https://tailscale.com/docs/features/access-control/key-expiry
- VPN Android y aplicaciones permitidas: https://developer.android.com/develop/connectivity/vpn
- Rangos UID VPN y contrapartes SDK sandbox, fuente AOSP: https://android.googlesource.com/platform/frameworks/base/+/afe0d0e3c7b4/services/core/java/com/android/server/connectivity/Vpn.java

Fuente Tailscale Android inspeccionada: commit 9832bc5847db423f72e9b225f22a09d8d1e0e91c,
IPNReceiver, IPNService y selector SplitTunnelAppPicker. La UI instalada y sus
capacidades Android prevalecen sobre una descripción documental anterior que
limitaba el modo incluir a MDM. No se instaló MDM ni se cambió el cliente oficial.
Las acciones explícitas CONNECT_VPN/DISCONNECT_VPN solicitan el cliente ya
autorizado; no sustituyen el consentimiento Android ni el login del usuario.
