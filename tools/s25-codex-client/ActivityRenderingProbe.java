import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONObject;

/** Exercises the installed APK renderer with synthetic items; never reads history. */
public final class ActivityRenderingProbe {
    private static final String PREFIX = "com.haochen.codexremote.";
    private static Constructor<?> bubble;
    private static Constructor<?> note;

    private static Object message(String id, boolean user, String text, String turn, String phase) throws Exception {
        return bubble.newInstance(id, user, text, 0, 0, new ArrayList<>(), turn, id, null, null, phase);
    }
    private static Object tool(String id, String text, String turn) throws Exception {
        return note.newInstance(id, text, id, turn);
    }
    private static String field(Object object, String getter) throws Exception {
        return String.valueOf(object.getClass().getMethod(getter).invoke(object));
    }
    private static void check(JSONArray results, String name, boolean value) throws Exception {
        results.put(new JSONObject().put("name", name).put("pass", value));
    }

    public static void main(String[] arguments) {
        JSONObject report = new JSONObject();
        try {
            bubble = Class.forName(PREFIX + "ConversationItem$Bubble").getConstructor(String.class, boolean.class,
                    String.class, int.class, int.class, List.class, String.class, String.class, String.class, Long.class, String.class);
            note = Class.forName(PREFIX + "ConversationItem$SystemNote").getConstructor(String.class, String.class, String.class, String.class);
            Class<?> contextType = Class.forName(PREFIX + "ConversationImageRenderContext");
            Object context = contextType.getConstructor(String.class, String.class).newInstance(null, null);
            Method build = Class.forName(PREFIX + "ConversationActivityHtmlKt").getMethod("buildConversationActivityItems",
                    List.class, String.class, contextType, boolean.class, Map.class);
            Object user1 = message("user1", true, "Solicitud 1", "turn1", null);
            Object user2 = message("user2", true, "Solicitud 2", "turn2", null);
            List<Object> items = new ArrayList<>(Arrays.asList(tool("before", "Conexión", null), user1,
                    message("comment1", false, "Progreso visible", "turn1", "commentary"),
                    tool("tool1", "Comando y salida <script>alert('fixture')</script>", "turn1"),
                    message("final1", false, "Respuesta final uno", "turn1", "final_answer"), user2,
                    tool("tool2", "Otra salida", "turn2"),
                    message("final2", false, "Respuesta final dos", "turn2", "final_answer"),
                    tool("foreign", "Aviso de otro turno", "foreign-turn")));
            Map<String, Object> cache = new HashMap<>();
            List<?> rendered = (List<?>) build.invoke(null, items, "/fixture", context, false, cache);
            List<String> ids = new ArrayList<>();
            for (Object item : rendered) ids.add(field(item, "getId"));
            JSONArray tests = new JSONArray();
            check(tests, "activity_follows_its_own_user_message", ids.equals(Arrays.asList("before", "user1", "activity_user1", "final1", "user2", "activity_user2", "final2", "foreign")));
            String html = field(rendered.get(2), "getHtml");
            check(tests, "disclosure_is_collapsed_initially", html.contains("<details class=\"cr-activity\"") && !html.matches("(?s).*<details[^>]*\\sopen(?:=|\\s|>).*"));
            check(tests, "commentary_and_complete_command_output_retained", html.contains("Progreso visible") && html.contains("Comando y salida") && html.contains("alert"));
            check(tests, "tool_output_html_escaped", !html.contains("<script>") && html.contains("&lt;script&gt;"));
            check(tests, "final_answer_stays_outside_disclosure", !html.contains("Respuesta final uno") && field(rendered.get(3), "getHtml").contains("Respuesta final uno"));
            check(tests, "foreign_turn_not_misattributed", !field(rendered.get(5), "getHtml").contains("Aviso de otro turno"));
            items.set(3, tool("tool1", "Salida actualizada", "turn1"));
            List<?> updated = (List<?>) build.invoke(null, items, "/fixture", context, false, cache);
            check(tests, "update_preserves_group_id_and_replaces_old_output", field(updated.get(2), "getId").equals("activity_user1") && field(updated.get(2), "getHtml").contains("Salida actualizada") && !field(updated.get(2), "getHtml").contains("alert"));
            List<?> reconciled = (List<?>) build.invoke(null, Arrays.asList(user2, message("only-final", false, "Nuevo snapshot", "turn2", "final_answer")), "/fixture", context, false, cache);
            check(tests, "new_snapshot_can_remove_activity_without_stale_dom_store", reconciled.size() == 2 && !cache.containsKey("tool1") && !cache.containsKey("comment1"));
            boolean passed = true;
            for (int i = 0; i < tests.length(); i++) passed &= tests.getJSONObject(i).getBoolean("pass");
            report.put("marker", "MESTRY_INSTALLED_APK_ACTIVITY_PROBE").put("status", passed ? "PASS" : "FAIL")
                    .put("tests", tests).put("real_history_or_credentials_read", false).put("model_turns_started", 0).put("ports_opened", false);
        } catch (Throwable failure) {
            try { report.put("status", "ERROR").put("error_class", failure.getClass().getSimpleName()); } catch (Exception ignored) { }
        }
        System.out.println(report.toString());
    }
}
