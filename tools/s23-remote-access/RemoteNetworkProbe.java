import android.os.Process;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.InetSocketAddress;
import java.net.Socket;
import org.json.JSONArray;
import org.json.JSONObject;

/** One-shot client connections from the approved app UID. No secrets or listeners. */
public final class RemoteNetworkProbe {
    private static final String PEER = "192.0.2.11";
    public static void main(String[] args) {
        JSONObject result = new JSONObject();
        try {
            boolean allowed = false;
            try (Socket socket = new Socket()) {
                socket.connect(new InetSocketAddress(PEER, 8023), 6000);
                socket.setSoTimeout(4000);
                String banner = new BufferedReader(new InputStreamReader(socket.getInputStream(), "US-ASCII")).readLine();
                allowed = banner != null && banner.startsWith("SSH-2.0-OpenSSH_");
            } catch (Exception ignored) { }
            JSONArray blocked = new JSONArray();
            boolean denied = true;
            for (int port : new int[]{22, 8022, 8787, 18787}) {
                boolean reachable = false;
                try (Socket socket = new Socket()) {
                    socket.connect(new InetSocketAddress(PEER, port), 1500);
                    reachable = true;
                } catch (Exception ignored) { }
                blocked.put(new JSONObject().put("port", port).put("reachable", reachable));
                denied &= !reachable;
            }
            result.put("marker", "MESTRY_S25_PRIVATE_NETWORK_PROBE").put("uid", Process.myUid())
                .put("peer", PEER).put("ssh_8023_banner_matches", allowed).put("other_ports", blocked)
                .put("credentials_read", false).put("listeners_created", false).put("model_turns_started", 0)
                .put("status", allowed && denied ? "PASS" : "FAIL");
        } catch (Exception failure) {
            try { result.put("status", "ERROR").put("error_class", failure.getClass().getSimpleName()); } catch (Exception ignored) { }
        }
        System.out.println(result.toString());
    }
}
