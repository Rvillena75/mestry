import socket
import threading
import unittest

from observe_s23 import ExistingAdb, ProbeError, metadata, summary


class ObservationTests(unittest.TestCase):
    def fixture(self, responses):
        server = socket.socket()
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        self.addCleanup(server.close)
        requests = []
        def worker():
            with server.accept()[0] as connection:
                connection.settimeout(2)
                def exact(length):
                    value = b''
                    while len(value) < length:
                        part = connection.recv(length-len(value))
                        if not part:
                            return value
                        value += part
                    return value
                for response in responses:
                    length = int(exact(4), 16)
                    requests.append(exact(length).decode())
                    for byte in response:
                        connection.sendall(bytes([byte]))
        thread = threading.Thread(target=worker)
        thread.start()
        self.addCleanup(thread.join, 3)
        return server.getsockname()[1], requests

    def test_existing_server_protocol_handles_fragmented_replies(self):
        port, requests = self.fixture([b'OKAY', b'OKAYSM-S918B\r\n'])
        adb = ExistingAdb('fixture-serial', port=port)
        self.assertEqual(adb.shell('getprop ro.product.model'), 'SM-S918B\n')
        self.assertEqual(requests, ['host:transport:fixture-serial', 'shell:getprop ro.product.model'])

    def test_rejection_does_not_export_server_diagnostic(self):
        port, _ = self.fixture([b'FAIL'])
        with self.assertRaisesRegex(ProbeError, '^EXISTING_ADB_QUERY_REJECTED$'):
            ExistingAdb('fixture', port=port).shell('getprop ro.product.model')

    def test_raw_vendor_history_and_unknown_values_are_excluded(self):
        value = metadata('  USB powered: true\n  level: 79\n  temperature: 210\n'
                         'MemAvailable: 4000000 kB\nmWakefulness=Dozing\n'
                         'Thermal Status: 0\nprivate battery QR=opaque_fixture\n'
                         '  level: unavailable\n')
        self.assertEqual(value['level'], 79)
        self.assertEqual(value['thermal_status'], 0)
        self.assertTrue(value['USB powered'])
        self.assertNotIn('opaque_fixture', str(value))

    def test_partial_or_failed_sampling_cannot_claim_full_health(self):
        value = summary([{'bridge_health': True, 'wakefulness': 'Dozing'}, {'error': 'QUERY_FAILED'}], False)
        self.assertFalse(value['complete'])
        self.assertFalse(value['all_samples_healthy'])
        self.assertEqual(value['successful_samples'], 1)
        self.assertEqual(value['idle_samples'], 1)
        self.assertFalse(value['availability_24h_verified'])


if __name__ == '__main__':
    unittest.main()
