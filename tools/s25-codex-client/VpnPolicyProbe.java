package com.haochen.codexremote;

import java.util.Set;

/** Run against the exact Java policy/tracker compiled into the APK. */
public final class VpnPolicyProbe {
    private static int checks;
    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        VpnLeasePolicy policy = new VpnLeasePolicy();
        check(policy.enterForeground(1000), "first open requests VPN");
        check(!policy.enterForeground(2000), "resume does not enqueue duplicate VPN connects");
        check(policy.stopReason(60_999).isEmpty(), "initial connection has bounded setup time");
        check(policy.stopReason(61_000).equals("unreachable"), "cache or missing server hello is not connectivity");
        policy = new VpnLeasePolicy();
        policy.enterForeground(0);
        policy.confirmConnection();
        policy.leaveForeground(10_000);
        check(policy.stopReason(39_999).isEmpty(), "30 second background grace");
        policy.leaveForeground(20_000);
        check(policy.stopReason(40_000).equals("background"), "duplicate background callback does not extend deadline");
        policy.enterForeground(39_000);
        check(policy.stopReason(40_000).isEmpty(), "returning cancels pending shutdown");
        policy.leaveForeground(45_000);
        policy.taskCount(2);
        check(policy.stopReason(76_000).isEmpty(), "running tasks retain VPN after grace");
        policy.taskCount(1);
        check(policy.stopReason(80_000).isEmpty(), "one completion does not terminate another task");
        policy.taskCount(0);
        check(policy.stopReason(80_001).equals("background"), "last completion releases expired grace");
        policy.taskCount(1);
        policy.manualDisconnect();
        check(policy.stopReason(80_002).equals("manual"), "explicit disconnect releases even during task");
        policy = new VpnLeasePolicy();
        policy.enterForeground(0);
        policy.confirmConnection();
        policy.taskCount(1);
        policy.loseConnection(10_000);
        policy.loseConnection(20_000);
        check(policy.stopReason(99_999).isEmpty(), "temporary loss retains connection retry window");
        check(policy.stopReason(100_000).equals("connection_lost"), "failure retries do not retain VPN forever");
        policy.confirmConnection();
        check(policy.stopReason(110_000).isEmpty(), "actual recovered connection clears failure deadline");
        VpnTurnTracker tracker = new VpnTurnTracker();
        tracker.started("session-a", "turn-1");
        tracker.started("session-a", "turn-1");
        tracker.started("session-b", "turn-1");
        check(tracker.count() == 2, "idempotent per-session task identities");
        tracker.completed("session-a", "wrong-id");
        check(tracker.count() == 2, "unrelated completion cannot release VPN");
        tracker.completed("session-a", "turn-1");
        check(tracker.count() == 1, "different session task survives");
        tracker.replace("session-b", Set.of());
        check(tracker.count() == 0, "explicit authoritative empty task snapshot releases lease");
        tracker.started("bad/path", "turn-1");
        tracker.started("session-a", "");
        check(tracker.count() == 0, "invalid metadata cannot retain VPN");
        System.out.println("{\"status\":\"PASS\",\"checks\":" + checks + ",\"source\":\"APK Java policy and tracker\",\"model_turns_started\":0}");
    }
}
