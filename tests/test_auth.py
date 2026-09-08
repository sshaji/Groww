import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from sip_lab.auth import authenticated_client, credentials, save_credentials


class AuthTests(unittest.TestCase):
    def test_round_trip_private_and_preserves_unrelated_settings(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
            path = Path(d) / '.env'
            path.write_text('OTHER=keep\nGROWW_ACCESS_TOKEN=old\n')
            secret = 'quotes" dollar$ backtick` slash\\ hash#'
            save_credentials('test-key', secret, path)
            self.assertEqual(credentials(path)['GROWW_API_SECRET'], secret)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertIn('OTHER=keep', path.read_text())
            self.assertNotIn('GROWW_ACCESS_TOKEN', credentials(path))

    def test_environment_override(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / '.env'
            save_credentials('file-key', 'file-secret', path)
            with patch.dict(os.environ, {'GROWW_API_KEY': 'env-key'}):
                self.assertEqual(credentials(path)['GROWW_API_KEY'], 'env-key')

    def test_no_shell_evaluation(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {}, clear=True):
            path = Path(d) / '.env'
            path.write_text('GROWW_API_KEY=$(echo never-execute)\n')
            self.assertEqual(credentials(path)['GROWW_API_KEY'], '$(echo never-execute)')

    def test_auth_error_is_safe_and_actionable(self):
        class Client:
            @staticmethod
            def get_access_token(**kwargs):
                class GrowwAPIAuthorisationException(Exception):
                    pass
                raise GrowwAPIAuthorisationException('secret must not appear')
        with patch.dict('sys.modules', {'growwapi': type('Module', (), {'GrowwAPI': Client})}):
            with self.assertRaisesRegex(ValueError, 'approval is required'):
                authenticated_client({'GROWW_API_KEY': 'key', 'GROWW_API_SECRET': 'secret'})
