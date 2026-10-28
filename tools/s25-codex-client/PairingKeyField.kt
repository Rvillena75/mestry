package com.haochen.codexremote

import android.content.ClipData
import android.content.ClipDescription
import android.content.ClipboardManager
import android.content.Context
import android.os.Build
import android.os.PersistableBundle
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation

@Composable
internal fun MainActivity.PairingKeyField() {
    Column {
        OutlinedTextField(
            value = bridgeToken,
            onValueChange = { if (!connected) bridgeToken = it.trim() },
            enabled = !connected,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            label = { Text("Clave de conexión privada") },
            visualTransformation = PasswordVisualTransformation(),
        )
        Text("Se guarda cifrada en Android Keystore. Pégala solo en el ingreso oculto de Horus.")
        TextButton(enabled = !connected, onClick = {
            val generated = BridgeTokenVault.generate()
            val saved = runCatching { BridgeTokenVault(this@PairingKeyField).write(generated) }.isSuccess
            if (!saved) {
                showNotice("No se pudo guardar la clave de conexión")
                return@TextButton
            }
            bridgeToken = generated
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = ClipData.newPlainText("MESTRY conexión privada", generated)
            if (Build.VERSION.SDK_INT >= 33) {
                clip.description.extras = PersistableBundle().apply {
                    putBoolean(ClipDescription.EXTRA_IS_SENSITIVE, true)
                }
            }
            clipboard.setPrimaryClip(clip)
            mainHandler.postDelayed({
                val current = clipboard.primaryClip?.getItemAt(0)?.text?.toString()
                if (current == generated) {
                    if (Build.VERSION.SDK_INT >= 28) clipboard.clearPrimaryClip()
                    else clipboard.setPrimaryClip(ClipData.newPlainText("", ""))
                }
            }, 120_000)
            showNotice("Clave nueva copiada durante dos minutos. Empareja Horus antes de conectar.")
        }) { Text("Generar y copiar una clave nueva") }
    }
}
