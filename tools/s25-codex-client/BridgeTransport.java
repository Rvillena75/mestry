package com.haochen.codexremote;

import java.net.URI;
import okhttp3.Request;

/** Only the local end of the approved SSH tunnel receives a pairing header. */
public final class BridgeTransport {
    private static volatile String token = "";
    private BridgeTransport() {}

    public static void setToken(String value) {
        if (value == null || !value.matches("[A-Za-z0-9_-]{43,128}"))
            throw new IllegalArgumentException("Falta una clave de conexión válida");
        token = value;
    }

    public static String canonicalUrl(String raw) {
        final URI uri;
        try { uri = URI.create(raw); }
        catch (Exception error) { throw new IllegalArgumentException("Dirección de conexión inválida"); }
        if (!"127.0.0.1".equals(uri.getHost()) || uri.getPort() != 18787 ||
            uri.getUserInfo() != null || uri.getRawQuery() != null || uri.getFragment() != null ||
            !("ws".equals(uri.getScheme()) || "http".equals(uri.getScheme())))
            throw new IllegalArgumentException("Usa el túnel SSH local 127.0.0.1:18787, sin token en la URL");
        return uri.toString();
    }

    public static Request.Builder request(String raw) {
        // HTTP endpoints may use session_id/path query parameters, never credentials.
        final URI uri;
        try { uri = URI.create(raw); }
        catch (Exception error) { throw new IllegalArgumentException("Dirección de recurso inválida"); }
        if (!"127.0.0.1".equals(uri.getHost()) || uri.getPort() != 18787 ||
            uri.getUserInfo() != null || uri.getFragment() != null ||
            !("ws".equals(uri.getScheme()) || "http".equals(uri.getScheme())) ||
            (uri.getRawQuery() != null && uri.getRawQuery().toLowerCase(java.util.Locale.ROOT).contains("token")) ||
            token.isEmpty()) throw new IllegalArgumentException("Recurso fuera de la conexión privada");
        return new Request.Builder().url(raw).header("X-Bridge-Token", token);
    }
}
