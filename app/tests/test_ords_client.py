import json
import sys
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

_ORDS_CLIENT_PATH = Path(__file__).resolve().parents[1] / "core" / "ords_client.py"
_ORDS_CLIENT_SPEC = importlib.util.spec_from_file_location("ords_client_under_test", _ORDS_CLIENT_PATH)
if _ORDS_CLIENT_SPEC is None or _ORDS_CLIENT_SPEC.loader is None:
    raise RuntimeError("Unable to load the ORDS client test target.")
_ORDS_CLIENT_MODULE = importlib.util.module_from_spec(_ORDS_CLIENT_SPEC)
_ORDS_CLIENT_SPEC.loader.exec_module(_ORDS_CLIENT_MODULE)
ORDSClient = _ORDS_CLIENT_MODULE.ORDSClient


class _JsonResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


class TestORDSClient(unittest.TestCase):
    def _connection_configs(self, environment_url="https://oracleapex.com/ords/"):
        return {
            "ORACLE_APEX_23AI_CLOUD": {
                "metadata": {
                    "environment_url": environment_url,
                    "workspace": "nanoprostudio",
                    "schema_alias": "nanoprostudio",
                }
            },
            "NANOPRO_ORDS_REPORTING_CLIENT": {
                "username": "test-oauth-client",
                "secret_value": "test-oauth-secret",
                "metadata": {"oauth_client_id": "test-oauth-client"},
            },
        }

    def _fake_app_modules(self, configs):
        fake_app = ModuleType("app")
        fake_app.__path__ = []
        fake_core = ModuleType("app.core")
        fake_core.__path__ = []
        fake_connection_manager = ModuleType("app.core.connection_manager")
        fake_connection_manager.connection_manager = SimpleNamespace(
            get_connection_config=lambda name, mask=False: configs.get(name)
        )
        return {
            "app": fake_app,
            "app.core": fake_core,
            "app.core.connection_manager": fake_connection_manager,
        }

    def test_verification_uses_configured_apex_host_and_bearer_token(self):
        configs = self._connection_configs()

        with (
            patch.dict(sys.modules, self._fake_app_modules(configs)),
            patch("urllib.request.urlopen") as urlopen,
        ):
            urlopen.side_effect = [
                _JsonResponse({"access_token": "test-access-token"}),
                _JsonResponse({"items": [], "links": []}),
            ]
            result = ORDSClient().verify()

        self.assertTrue(result["success"])
        self.assertEqual(result["rows"], 0)
        self.assertEqual(
            result["endpoint"],
            "https://oracleapex.com/ords/nanoprostudio/nanopro/v1/l2/",
        )
        requests = [call.args[0] for call in urlopen.call_args_list]
        self.assertEqual(
            requests[0].full_url,
            "https://oracleapex.com/ords/nanoprostudio/oauth/token",
        )
        self.assertEqual(
            requests[1].get_header("Authorization"),
            "Bearer test-access-token",
        )

    def test_rejects_non_https_ords_endpoint(self):
        configs = self._connection_configs("http://oracleapex.com/ords/")

        with patch.dict(sys.modules, self._fake_app_modules(configs)):
            with self.assertRaisesRegex(RuntimeError, "must be an HTTPS URL"):
                ORDSClient()

    def test_migrates_legacy_apex_hostname_to_current_service(self):
        configs = self._connection_configs("https://apex.oracle.com/ords/")

        with patch.dict(sys.modules, self._fake_app_modules(configs)):
            client = ORDSClient()

        self.assertEqual(client.base_url, "https://oracleapex.com/ords")

    def test_reports_timeout_without_exposing_credentials(self):
        configs = self._connection_configs()

        with (
            patch.dict(sys.modules, self._fake_app_modules(configs)),
            patch("urllib.request.urlopen", side_effect=TimeoutError),
        ):
            with self.assertRaisesRegex(RuntimeError, "OAuth token request failed"):
                ORDSClient().verify()

    def test_requires_dedicated_oauth_client_credentials(self):
        configs = self._connection_configs()
        configs.pop("NANOPRO_ORDS_REPORTING_CLIENT")

        with (
            patch.dict(sys.modules, self._fake_app_modules(configs)),
            patch("urllib.request.urlopen") as urlopen,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "NANOPRO_ORDS_REPORTING_CLIENT needs the ORDS OAuth client ID and secret",
            ):
                ORDSClient()

        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
