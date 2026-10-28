package com.haochen.codexremote;

import android.content.Context;
import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.SecureRandom;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Pairing credential only. Never stores Google OAuth or Codex credentials. */
public final class BridgeTokenVault {
    private static final String ALIAS = "mestry_s25_bridge_v1";
    private static final int FLAGS = Base64.NO_WRAP | Base64.URL_SAFE | Base64.NO_PADDING;
    private final SharedPreferences storage;

    public BridgeTokenVault(Context context) {
        storage = context.getSharedPreferences("mestry_pairing_private", Context.MODE_PRIVATE);
    }

    private SecretKey key(boolean create) throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (!store.containsAlias(ALIAS)) {
            if (!create) throw new IllegalStateException("Pairing key unavailable; pair again privately");
            KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
            generator.init(new KeyGenParameterSpec.Builder(ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).build());
            return generator.generateKey();
        }
        return (SecretKey) store.getKey(ALIAS, null);
    }

    public String read() throws Exception {
        String envelope = storage.getString("sealed_token", null);
        if (envelope == null) return "";
        String[] parts = envelope.split("\\.", -1);
        if (parts.length != 2) throw new IllegalStateException("Pairing data invalid");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key(false), new GCMParameterSpec(128, Base64.decode(parts[0], FLAGS)));
        cipher.updateAAD(ALIAS.getBytes(StandardCharsets.UTF_8));
        return new String(cipher.doFinal(Base64.decode(parts[1], FLAGS)), StandardCharsets.UTF_8);
    }

    public void write(String token) throws Exception {
        if (token == null || !token.matches("[A-Za-z0-9_-]{43,128}")) throw new IllegalArgumentException("Use a generated pairing key");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key(true));
        cipher.updateAAD(ALIAS.getBytes(StandardCharsets.UTF_8));
        String value = Base64.encodeToString(cipher.getIV(), FLAGS) + "." +
            Base64.encodeToString(cipher.doFinal(token.getBytes(StandardCharsets.UTF_8)), FLAGS);
        if (!storage.edit().putString("sealed_token", value).commit()) throw new IllegalStateException("Pairing could not be saved");
    }

    public static String generate() {
        byte[] bytes = new byte[32];
        new SecureRandom().nextBytes(bytes);
        return Base64.encodeToString(bytes, FLAGS);
    }
}
