"""Regression checks for route attribution and fresh-response metadata."""
import unittest
from unittest.mock import patch

from mobile_validate import history_metadata
from network_test import cellular_ready
from vpn_observe import vpn_agents


class ObservationTests(unittest.TestCase):
    def test_not_vpn_capability_is_not_a_vpn_transport(self):
        physical = 'NetworkAgentInfo{ Transports: WIFI Capabilities: VALIDATED NOT_VPN}'
        vpn = 'NetworkAgentInfo{ Transports: CELLULAR|VPN Capabilities: INTERNET}'
        self.assertEqual(vpn_agents(physical), [])
        self.assertEqual(vpn_agents(physical + '\n' + vpn), [vpn])

    def test_cellular_default_and_no_wifi_agent_are_required(self):
        network = {'wifi_enabled': False, 'active_default_transport': {
            'transports': 'CELLULAR', 'validated': True}, 'transport_capabilities': [
                {'transports': 'CELLULAR'}, {'transports': 'CELLULAR|VPN'}]}
        self.assertTrue(cellular_ready(network))
        network['transport_capabilities'].append({'transports': 'WIFI|VPN'})
        self.assertFalse(cellular_ready(network))

    def test_cellular_available_does_not_prove_cellular_default(self):
        network = {'wifi_enabled': False, 'active_default_transport': {
            'transports': 'WIFI', 'validated': True}, 'transport_capabilities': [{'transports': 'CELLULAR'}]}
        self.assertFalse(cellular_ready(network))

    def test_fresh_incremental_response_is_distinct_from_full_snapshot(self):
        lines = '\n'.join([
            '100.100 123 123 D CodexRemoteSync: session.sync applied sessionId=fixture conversationItems=27 cacheEntries=35',
            '102.100 123 123 D CodexRemoteSync: session.content response sessionId=fixture last=99 entries=35 items=27 conversationBefore=27',
            '104.100 123 123 D CodexRemoteSync: session.sync applied sessionId=fixture conversationItems=27 cacheEntries=35',
        ])
        with patch('mobile_validate.shell', return_value=lines):
            rows = history_metadata(100, 103)
        self.assertEqual([row['method'] for row in rows], ['session.sync', 'session.content'])
        self.assertTrue(rows[0]['entries_are_merged_history_count'])
        self.assertEqual(rows[1]['last_seq'], 99)
        self.assertEqual(len(rows), 2)


if __name__ == '__main__':
    unittest.main()
