import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mcp_config_shape_diff as m

class ShapeDiffTests(unittest.TestCase):
    def run_cli(self, payload, arg='-'):
        if arg == '-':
            return subprocess.run([sys.executable, str(Path(m.__file__)), '-'], input=payload, capture_output=True)
        return subprocess.run([sys.executable, str(Path(m.__file__)), arg], capture_output=True)
    def test_diff_sorted_and_sanitized(self):
        payload = b'{"before":{"mcpServers":{"z":{"command":"SECRET-CMD","args":["SECRET-ARG"],"env":{"TOKEN":"SECRET-VALUE"}},"a":{"url":"SECRET-URL"}}},"after":{"mcpServers":{"z":{"command":"OTHER","args":["OTHER"],"env":{"TOKEN":"OTHER"}},"b":{}}}}'
        p = self.run_cli(payload)
        self.assertEqual(p.returncode, 1)
        out = p.stdout.decode()
        self.assertLess(out.index('"server":"a"'), out.index('"server":"b"'))
        for secret in ("SECRET", "OTHER"):
            self.assertNotIn(secret, out)
    def test_same_shape_values_not_detected(self):
        b = {'mcpServers': {'x': {'command':'one','args':['a'],'env':{'K':'v'}}}}
        a = {'mcpServers': {'x': {'command':'two','args':['b'],'env':{'K':'z'}}}}
        out, code = m.compare(b, a)
        self.assertEqual(code, 0)
        self.assertIn('unchanged', out)
    def test_fixture_cli_exact_output_and_exit(self):
        expected = ('{"servers":[{"server":"added","status":"added"},{"server":"local","status":"changed","command_present_changed":false,"url_present_changed":false,"transport_changed":false,"cwd_present_changed":false,"args_count_before":1,"args_count_after":2,"env_key_count_before":1,"env_key_count_after":2,"env_key_set_changed":true},{"server":"remote","status":"unchanged","command_present_changed":false,"url_present_changed":false,"transport_changed":false,"cwd_present_changed":false,"args_count_before":0,"args_count_after":0,"env_key_count_before":0,"env_key_count_after":0,"env_key_set_changed":false}]}')
        p = self.run_cli(b'', str(Path(m.__file__).resolve().parent / 'fixtures' / 'example.json'))
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout, (expected + os.linesep).encode())
        self.assertEqual(p.stderr, b'')
    def test_duplicate_nonfinite_and_shape_invalid(self):
        for raw in (b'{"before":{},"before":{},"after":{}}', b'{"before":NaN,"after":{}}', b'{"before":{"mcpServers":{"x":{"ignored":1e400}}},"after":{"mcpServers":{}}}', b'[]'):
            self.assertEqual(self.run_cli(raw).returncode, 2)
    def test_deep_json_is_fixed_error_without_traceback(self):
        raw = b'{"before":{"mcpServers":{"x":{"ignored":' + b'[' * 1500 + b'0' + b']' * 1500 + b'}}},"after":{"mcpServers":{}}}'
        p = self.run_cli(raw)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, ('{"error":"E_INPUT"}' + os.linesep).encode())
        self.assertEqual(p.stderr, b'')
    def test_limits(self):
        with self.assertRaises(m.InvalidInput): m.load_snapshot(b'{"before":{"mcpServers":'+b'{'+b','.join((b'"s%d":{}'%i) for i in range(129))+b'},"after":{"mcpServers":{}}}')
        with self.assertRaises(m.InvalidInput): m.load_snapshot(b'{"before":{"mcpServers":{"x":{'+b','.join((b'"k%d":0'%i) for i in range(65))+b'}}},"after":{"mcpServers":{}}}')
        with self.assertRaises(m.InvalidInput): m.load_snapshot(b' ' * (m.MAX_INPUT + 1))
    def test_input_paths(self):
        for path in ('https://host/file','\\\\server\\share\\x','\\\\.\\device','C:relative','file:stream'):
            with self.assertRaises(m.InvalidInput): m.read_input(path)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'input.json'
            path.write_bytes(b'{}')
            self.assertEqual(m.read_input(str(path)), b'{}')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(m.InvalidInput): m.read_input(d)
            if os.name != 'nt':
                path = Path(d) / 'absolute.json'
                path.write_bytes(b'{}')
                self.assertEqual(m.read_input(str(path)), b'{}')
        # Network/UNC spellings are rejected even when tested on POSIX.
        for path in ('//server/share/file', r'\\server\share\file', r'\\?\C:\file', r'\\.\device'):
            with self.assertRaises(m.InvalidInput): m.read_input(path)
    def test_explicit_enum_then_inference(self):
        self.assertEqual(m.transport({'type':'sse','command':'x'}), 'remote')
        self.assertEqual(m.transport({'command':'x'}), 'stdio')
        self.assertEqual(m.transport({'url':'x'}), 'remote')
        self.assertEqual(m.transport({'command':'x','url':'y'}), 'unknown')
    def test_output_budget_counts_line_ending_cross_platform(self):
        before = {f'{i:03}': {} for i in range(128)}
        after = {name: {} for name in before}
        with patch.object(m, 'MAX_OUTPUT', 100_000):
            result, _ = m.compare(before, after)
        actual_line = result + os.linesep
        exact_size = len(actual_line.encode('utf-8'))
        with patch.object(m, 'MAX_OUTPUT', exact_size):
            self.assertEqual(m.compare(before, after)[0], result)
        # One byte below the complete platform line ending must fail.
        with patch.object(m, 'MAX_OUTPUT', exact_size - 1):
            with self.assertRaises(m.InvalidInput): m.compare(before, after)

if __name__ == '__main__': unittest.main()
