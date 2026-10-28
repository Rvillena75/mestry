# Publicación privada Horus → Drive — piloto

Estado: preparación; **OAuth del S23 y publicación real todavía pendientes**. No reutiliza el token del conector de ChatGPT. El cliente Android de proyectos/conversaciones del S25 sigue siendo otro incremento.

El piloto acepta únicamente `S23_PUBLISH_TEST.md` del proyecto sintético `/workspace/projects/mestry-horus-smoke`, máximo 64 KiB. Horus solicita publicar por el SSH Termux existente en 8023. Una clave nueva, exclusiva y con comando forzado permite publicar o descargar el cliente público; no abre una shell, túneles ni acceso a OAuth. Las claves WSL/S25 existentes se conservan.

## 1. Crear el cliente Google (usuario)

En [Google Cloud Console](https://console.cloud.google.com/), con `owner@example.invalid`:

1. Crear un proyecto **MESTRY S23 Publisher** (o seleccionar uno reservado a este piloto).
2. En **APIs y servicios → Biblioteca**, habilitar **Google Drive API**.
3. En **Google Auth Platform → Branding**, iniciar la configuración, nombre **MESTRY S23 Publisher**, correo de soporte y contacto propios.
4. En **Audience / Público**, elegir **External / Externa**, porque se usa una cuenta Gmail personal. Para el primer ensayo mantener **Testing / Pruebas** y agregar `owner@example.invalid` como usuario de prueba.
5. En **Data Access / Acceso a datos**, añadir solo `https://www.googleapis.com/auth/drive.file`. No añadir acceso completo a Drive ni al corpus personal.
6. En **Clients / Clientes → Create client**, tipo **Desktop app / Aplicación de escritorio**, nombre **MESTRY Termux Publisher**. Este es un programa Python de consola; no elegir Android ni aplicación web. Si aparece la opción de cliente para agente de IA, marcarla para este cliente dedicado a solicitudes de Horus.
7. Descargar el JSON a una carpeta local privada. **No pegarlo en el chat, subirlo al repositorio, Drive o al workspace de Horus.** Comunicar solo que está creado y la ruta local del archivo, si se solicita.

Google documenta que los refresh tokens de una app externa en **Testing** caducan a los **7 días** cuando se pide Drive. Eso sirve para el primer ensayo; antes de declarar autonomía continua habrá que pasar la configuración OAuth a **In production / En producción** y autorizar de nuevo. Publicar el estado OAuth no comparte los documentos ni publica este programa en una tienda. No prometer tokens permanentes: también pueden revocarse.

Fuentes oficiales comprobadas el 2026-10-21: [configuración y cliente de escritorio](https://developers.google.com/workspace/drive/api/quickstart/python), [scopes de Drive](https://developers.google.com/workspace/drive/api/guides/api-specific-auth), [OAuth de aplicaciones de escritorio y PKCE](https://developers.google.com/identity/protocols/oauth2/native-app), [caducidad de refresh tokens](https://developers.google.com/identity/protocols/oauth2#expiration).

## 2. Instalación y autorización privadas

`python3 tools/horus_publish/install.py --stage` instala código en Termux mediante el alias SSH ya verificado `mestry-s23`. No instala paquetes, registra claves, abre sockets nuevos ni inicia OAuth. El publicador queda inactivo sin credenciales, carpeta y clave dedicada. El runtime S23 usa Python estándar. La biblioteca oficial de Google se instala **solo en WSL**, en un venv privado de preparación, con `install.py --dependencies`.

Después de crear el cliente, el usuario ejecuta en WSL:

```sh
python3 tools/horus_publish/install.py --import-client '/ruta/local/al/cliente.json'
```

El helper valida el tipo y endpoints del JSON sin mostrar sus valores, y lo transmite por stdin del SSH existente a almacenamiento privado Termux. No conserva una copia en el proyecto. No reemplaza un cliente o token existente.

**Requisito de autorización pendiente por la regla de puertos del usuario:** el login inicial necesita un callback temporal **127.0.0.1:53682 en WSL**, durante un máximo de 180 segundos. El código está preparado, pero no se debe ejecutar hasta obtener aprobación expresa. No cambia 8022/8023. Después, el usuario ejecuta en WSL:

```sh
~/.local/share/mestry-publish-setup/venv/bin/python tools/horus_publish/authorize_wsl.py '/ruta/local/al/cliente.json' --allow-loopback-53682
```

El helper muestra un enlace **solo en la terminal local del usuario** para abrir en el navegador del **PC**. Elegir la cuenta indicada y comprobar el permiso. No copiar el enlace OAuth, códigos ni tokens al chat ni ejecutar este helper bajo `mestry_session.py` u otro logger. La biblioteca oficial valida estado/PKCE; el callback se cierra al finalizar o vencer el plazo. La cuenta y los scopes se comprueban en WSL y en Termux antes de guardar el token en el S23. Se transfiere por stdin de SSH y no se guarda el token en WSL ni se entrega a Horus. Esta preparación usa el PC una vez; publicar y renovar el token no dependen de él. Se verificará el callback real con el navegador del PC antes de darlo por válido.

La primera instalación de la biblioteca en Termux encontró una dependencia CFFI sin compilador. Se conserva la evidencia del fallo y se revierte ese paquete/venv incompletos. El diseño final evita instalar compiladores o fijar una biblioteca antigua: autorización interactiva oficial en WSL y refresh grant estándar de Google en el runtime nativo S23. La renovación real sigue pendiente de OAuth.

## 3. Destino y clave exclusiva

Con el token ya autorizado, en Termux `python3 ~/.local/lib/mestry-publish/oauth_setup.py prepare-folder` crea una carpeta privada **Horus** usando un ID reservado en SQLite. Con `drive.file`, este cliente nuevo no obtiene automáticamente acceso a la carpeta Review creada por otro cliente OAuth. Por eso el bootstrap consiste en mover **esa carpeta nueva**, mediante el conector ya autorizado o manualmente en Drive, dentro de [MESTRY/Review](https://drive.google.com/drive/folders/DRIVE_FOLDER_03_EXAMPLE). El publicador comprobará su ID, padre y permisos antes de subir documentos. No ampliar el scope para localizar carpetas antiguas.

En la terminal **Horus del S25**, generar una clave exclusiva sin reemplazar ninguna existente:

```sh
umask 077
mkdir -p ~/.ssh
test ! -e ~/.ssh/id_ed25519_mestry_publish && ssh-keygen -q -t ed25519 -N '' -C mestry-horus-publish -f ~/.ssh/id_ed25519_mestry_publish
cat ~/.ssh/id_ed25519_mestry_publish.pub
```

Comunicar **solo la línea pública** `ssh-ed25519 … mestry-horus-publish`. No la clave privada. El operador registra esa clave con `install.py --register-key public-key.txt`: requiere exactamente las dos claves previas WSL/S25, hace copia privada y conserva ambas líneas intactas. Restringe la nueva clave a loopback y los comandos `mestry-publish-v1` / `mestry-publish-bootstrap-v1`.

Tras registrar la clave, el operador proporciona el bootstrap con la clave de host Termux fijada. El cliente queda en `~/.local/bin/mestry-publish`, sin OAuth. El comando de uso será:

```sh
cd /workspace/projects/mestry-horus-smoke
~/.local/bin/mestry-publish S23_PUBLISH_TEST.md
```

## Contrato y límites

- Termux real UID Android **10348** guarda OAuth; Horus real UID **10350** ejecuta Codex. El aislamiento proviene de Android, no de PRoot ni de una carpeta Linux. Esto adapta la recomendación histórica de no guardar OAuth junto a Codex: Codex ahora se ejecuta en **otra app/UID**, no en Termux. No usar este piloto para ejecutar Codex también en Termux.
- El receptor fija cuenta, documento y destino; no recibe rutas de escritura remotas, comandos o IDs de destino del agente. La allowlist del cliente es comodidad, no prueba criptográfica de procedencia de los bytes de un agente que controla su workspace.
- Una revisión nueva crea otro `.md`; nunca actualiza, borra o comparte los anteriores. El mismo contenido se deduplica por ID determinista. Las ediciones humanas anteriores se conservan.
- ID Drive reservado y persistido **antes** del upload. Un timeout se reconcilia por ese mismo ID; no se crea otra copia. El éxito requiere leer los bytes completos y comprobar SHA-256, metadata, padre y privacidad. Una revisión alterada no se declara verificada.
- Máximo 20 reservas nuevas por día UTC y 32 en total en este piloto. No sincroniza corpus, feedback ni comentarios, no vigila carpetas y no crea un daemon nuevo. La ejecución se solicita desde Horus y funciona en el teléfono; PC apagado y renovación real se probarán por separado.
- Estado privado Termux: `~/.local/state/mestry-publish` (700; archivos 600). Código privado: `~/.local/lib/mestry-publish`. La clave dedicada se puede revocar retirando solo su línea de `authorized_keys`; no ejecutar la antigua reversión de puertos.

## Verificación

```sh
python3 -m unittest discover -s tools/horus_publish -p 'test_*.py' -v
```

Las pruebas usan Drive falso en memoria y archivos temporales. No autorizan Google, abren listeners ni prueban una publicación real. Las bibliotecas OAuth, UID, SSH forzado, token renovado, publicación/readback desde S23, lectura S25 y funcionamiento con PC apagado requieren evidencia propia.
