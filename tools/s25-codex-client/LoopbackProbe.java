import android.system.ErrnoException;
import android.system.Os;
import android.system.OsConstants;
import java.io.ByteArrayOutputStream;
import java.io.FileDescriptor;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import org.json.JSONArray;
import org.json.JSONObject;

/** One-shot ADB diagnostic: never listens, changes settings, or reads credentials. */
public final class LoopbackProbe {
    private static final int PORT = 18787;

    // Binding without listen reserves an address momentarily; it accepts no traffic.
    private static int bindOnly(InetAddress address, int family) throws Exception {
        FileDescriptor descriptor = Os.socket(family, OsConstants.SOCK_STREAM, 0);
        try {
            if (family == OsConstants.AF_INET6) {
                Os.setsockoptInt(descriptor, OsConstants.IPPROTO_IPV6,
                        OsConstants.IPV6_V6ONLY, 1);
            }
            try {
                Os.bind(descriptor, address, PORT);
                return 0;
            } catch (ErrnoException error) {
                return error.errno;
            }
        } finally {
            Os.close(descriptor);
        }
    }

    private static String request(String path, boolean badWebSocketToken) throws Exception {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress("127.0.0.1", PORT), 3000);
            socket.setSoTimeout(3000);
            String headers = "GET " + path + " HTTP/1.1\r\nHost: 127.0.0.1:" + PORT + "\r\n";
            headers += badWebSocketToken
                    ? "Connection: Upgrade\r\nUpgrade: websocket\r\n"
                    + "Sec-WebSocket-Version: 13\r\n"
                    + "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                    + "X-Bridge-Token: deliberately-invalid\r\n"
                    : "Connection: close\r\n";
            socket.getOutputStream().write((headers + "\r\n")
                    .getBytes(StandardCharsets.US_ASCII));
            ByteArrayOutputStream buffer = new ByteArrayOutputStream();
            byte[] block = new byte[1024];
            while (buffer.size() < 8192) {
                int count = socket.getInputStream().read(block, 0,
                        Math.min(block.length, 8192 - buffer.size()));
                if (count < 0) break;
                buffer.write(block, 0, count);
            }
            return buffer.toString("UTF-8");
        }
    }

    public static void main(String[] args) {
        JSONObject result = new JSONObject();
        try {
            int loopback = bindOnly(InetAddress.getByName("127.0.0.1"), OsConstants.AF_INET);
            int ipv6Any = bindOnly(InetAddress.getByName("::"), OsConstants.AF_INET6);
            int nonLoopback = 0;
            int successes = 0;
            JSONArray failures = new JSONArray();
            for (NetworkInterface network : Collections.list(NetworkInterface.getNetworkInterfaces())) {
                for (InetAddress address : Collections.list(network.getInetAddresses())) {
                    if (address.isLoopbackAddress() || address.isAnyLocalAddress()) continue;
                    nonLoopback++;
                    int family = address.getAddress().length == 4
                            ? OsConstants.AF_INET : OsConstants.AF_INET6;
                    int errno = bindOnly(address, family);
                    if (errno == 0) successes++;
                    else failures.put(new JSONObject().put("family", family).put("errno", errno));
                }
            }
            String health = request("/healthz", false);
            boolean healthOk = health.startsWith("HTTP/1.1 200 ")
                    && health.contains("\"name\":\"mestry-s25-pilot\"")
                    && health.contains("\"version\":\"0.1.0\"");
            boolean unauthDenied = request("/v1/sessions", false).startsWith("HTTP/1.1 401 ");
            boolean badTokenDenied = request("/", true).startsWith("HTTP/1.1 401 ");
            boolean privateBind = loopback == OsConstants.EADDRINUSE
                    && ipv6Any == 0 && nonLoopback > 0 && nonLoopback == successes;
            result.put("marker", "MESTRY_S25_LOOPBACK_PROBE");
            result.put("port", PORT);
            result.put("bind_only_no_listen", true);
            result.put("loopback_ipv4_in_use", loopback == OsConstants.EADDRINUSE);
            result.put("ipv6_wildcard_unbound", ipv6Any == 0);
            result.put("non_loopback_addresses_tested", nonLoopback);
            result.put("non_loopback_bind_successes", successes);
            result.put("non_loopback_failures", failures);
            result.put("loopback_bind_verified", privateBind);
            result.put("health_identity_matches", healthOk);
            result.put("unauthenticated_sessions_denied", unauthDenied);
            result.put("invalid_websocket_token_denied", badTokenDenied);
            result.put("status", privateBind && healthOk && unauthDenied && badTokenDenied
                    ? "PASS" : "FAIL");
        } catch (Exception error) {
            try {
                result.put("status", "FAIL");
                result.put("error_class", error.getClass().getSimpleName());
            } catch (Exception ignored) { }
        }
        System.out.println(result.toString());
    }
}
