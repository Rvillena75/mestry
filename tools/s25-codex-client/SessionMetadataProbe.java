import java.lang.reflect.Method;
import org.json.JSONArray;
import org.json.JSONObject;

/** Runs the installed APK's pure metadata parser against synthetic JSON only. */
public final class SessionMetadataProbe {
    private static Object companion;
    private static Class<?> session;

    private static Object parse(String method, JSONObject input) throws Exception {
        return companion.getClass().getMethod(method, JSONObject.class).invoke(companion, input);
    }

    private static String field(Object parsed, String method) throws Exception {
        return (String) session.getMethod(method).invoke(parsed);
    }

    private static JSONObject base() throws Exception {
        return new JSONObject().put("id", "synthetic-session")
                .put("cwd", "/workspace/projects/mestry-horus-smoke");
    }

    private static void check(JSONArray tests, String name, boolean passed) throws Exception {
        tests.put(new JSONObject().put("name", name).put("pass", passed));
    }

    public static void main(String[] arguments) {
        JSONObject report = new JSONObject();
        try {
            session = Class.forName("com.haochen.codexremote.SessionInfo");
            companion = session.getField("Companion").get(null);
            JSONArray tests = new JSONArray();
            JSONObject nullable = base().put("title", JSONObject.NULL)
                    .put("name", JSONObject.NULL).put("preview", "Prueba desde el S25")
                    .put("reasoningEffort", JSONObject.NULL).put("model", JSONObject.NULL);
            Object envelope = parse("fromSession", nullable);
            Object thread = parse("fromThread", nullable);
            check(tests, "session_null_title_uses_preview",
                    "Prueba desde el S25".equals(field(envelope, "getTitle")));
            check(tests, "thread_null_title_uses_preview",
                    "Prueba desde el S25".equals(field(thread, "getTitle")));
            check(tests, "nullable_model_and_reasoning_are_empty",
                    "".equals(field(envelope, "getModel"))
                            && "".equals(field(envelope, "getReasoningEffort")));
            Object empty = parse("fromSession", base().put("title", JSONObject.NULL)
                    .put("name", JSONObject.NULL).put("preview", JSONObject.NULL));
            check(tests, "missing_title_uses_session_id",
                    "syntheti".equals(field(empty, "titleLine")));
            Object literal = parse("fromSession", base().put("title", "null"));
            check(tests, "literal_user_title_null_is_preserved",
                    "null".equals(field(literal, "getTitle")));
            Object previous = parse("fromSession", base().put("title", "Titulo previo"));
            Method merge = session.getMethod("mergedWith", session);
            Object merged = merge.invoke(empty, previous);
            check(tests, "null_update_preserves_previous_title",
                    "Titulo previo".equals(field(merged, "getTitle")));
            boolean passed = true;
            for (int index = 0; index < tests.length(); index++) {
                passed &= tests.getJSONObject(index).getBoolean("pass");
            }
            report.put("marker", "MESTRY_INSTALLED_APK_METADATA_PROBE");
            report.put("status", passed ? "PASS" : "FAIL");
            report.put("tests", tests);
            report.put("real_account_or_credentials_read", false);
            report.put("model_turns_started", 0);
            report.put("ports_opened", false);
        } catch (Throwable failure) {
            try {
                report.put("status", "ERROR");
                report.put("error_class", failure.getClass().getSimpleName());
            } catch (Exception ignored) { }
        }
        System.out.println(report.toString());
    }
}
