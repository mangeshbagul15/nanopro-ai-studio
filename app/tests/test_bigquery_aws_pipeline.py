import sys
import unittest
from pathlib import Path
from unittest.mock import patch

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from app.core import bigquery_aws_pipeline as pipeline


class _FakeDataset:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id


class _FakeTable:
    def __init__(self, table_id):
        self.table_id = table_id


class _FakeBqClient:
    project = "demo-project"

    def __init__(self, datasets, tables=None, fail_list=False):
        self._datasets = datasets
        self._tables = tables or {}
        self._fail_list = fail_list

    def list_datasets(self):
        if self._fail_list:
            raise RuntimeError("bigquery auth missing")
        return [_FakeDataset(name) for name in self._datasets]

    def list_tables(self, ref):
        dataset = ref.rsplit(".", 1)[-1]
        return [_FakeTable(name) for name in self._tables.get(dataset, [])]


class _FakeService:
    def __init__(self, fail=False):
        self.fail = fail

    def _guard(self):
        if self.fail:
            raise RuntimeError("AccessDenied: simulated")

    def get_queue_url(self, **kwargs):
        if self.fail:
            raise RuntimeError("sqs denied")
        return {"QueueUrl": "https://sqs.local/nanopro-pipeline-events"}

    def create_queue(self, **kwargs):
        return {"QueueUrl": "https://sqs.local/nanopro-pipeline-events"}

    def send_message(self, **kwargs):
        return {"MessageId": "msg-1"}

    def describe_table(self, **kwargs):
        return {"Table": {"TableName": kwargs.get("TableName")}}

    def create_table(self, **kwargs):
        return {}

    def put_item(self, **kwargs):
        return {}

    def put_metric_data(self, **kwargs):
        return {}

    def list_tables(self, **kwargs):
        self._guard()
        return {"TableNames": []}

    def list_queues(self, **kwargs):
        self._guard()
        return {"QueueUrls": []}

    def list_metrics(self, **kwargs):
        self._guard()
        return {"Metrics": []}

    def get_databases(self, **kwargs):
        self._guard()
        return {"DatabaseList": []}

    def create_database(self, **kwargs):
        return {}

    def update_table(self, **kwargs):
        return {}

    def list_work_groups(self, **kwargs):
        self._guard()
        return {"WorkGroups": []}

    def list_functions(self, **kwargs):
        self._guard()
        return {"Functions": []}

    def list_topics(self, **kwargs):
        self._guard()
        return {"Topics": []}


def _manifest(dataset, tables):
    files = [
        {"table": name, "key": f"bronze/bigquery/{dataset}/{name}/{name}.parquet",
         "rows": 10, "bytes": 1000, "sha256": "a" * 64, "status": "uploaded",
         "columns": [{"name": "id", "type": "BIGINT"}, {"name": "label", "type": "VARCHAR"}]}
        for name in tables
    ]
    return {
        "bucket": "nanopro-data-lake",
        "prefix": f"bronze/bigquery/{dataset}",
        "source": f"bigquery:{dataset}",
        "exported_at": "2026-11-18T00:00:00Z",
        "files": files,
        "failures": [],
        "manifest_key": f"bronze/bigquery/{dataset}/_MANIFEST.json",
        "success_marker": f"bronze/bigquery/{dataset}/_SUCCESS",
    }


class BigQueryAwsPipelineTests(unittest.TestCase):
    def setUp(self):
        pipeline._CAPS_CACHE.update({"at": 0.0, "value": None})

    def test_capabilities_not_configured(self):
        with patch.object(pipeline, "_aws_config", return_value={
            "access_key": "", "secret_key": "", "region": "ap-southeast-2", "bucket": "",
        }):
            result = pipeline.capabilities(force=True)
        self.assertEqual(result["status"], "not_configured")
        self.assertEqual(result["services"]["s3"]["status"], "not_configured")

    def test_capabilities_reports_denied_services(self):
        cfg = {"access_key": "a", "secret_key": "b", "region": "ap-southeast-2", "bucket": "nanopro-data-lake"}

        class _S3:
            def head_bucket(self, **kwargs):
                return {}

        def fake_aws_client(config, service):
            return _FakeService(fail=(service == "lambda"))

        with patch.object(pipeline, "_aws_config", return_value=cfg), \
             patch.object(pipeline, "_s3_client", return_value=_S3()), \
             patch.object(pipeline, "_aws_client", side_effect=fake_aws_client):
            result = pipeline.capabilities(force=True)
        self.assertEqual(result["status"], "success")
        self.assertIn("sqs", result["available_services"])
        self.assertEqual(result["services"]["lambda"]["status"], "unavailable")

    def test_run_pipeline_success_exports_all_datasets(self):
        cfg = {"access_key": "a", "secret_key": "b", "region": "ap-southeast-2", "bucket": "nanopro-data-lake"}
        bq = _FakeBqClient(
            ["nanopro_cbs_bronze", "nanopro_studio"],
            {"nanopro_cbs_bronze": ["customers", "accounts"], "nanopro_studio": ["runs"]},
        )

        exported = []

        def fake_export(client, s3, bucket, schema, tables, prefix=""):
            exported.append((schema, list(tables), prefix))
            return _manifest(schema, tables)

        with patch.object(pipeline, "_aws_config", return_value=cfg), \
             patch.object(pipeline, "_bq_client", return_value=bq), \
             patch.object(pipeline, "_s3_client", return_value=object()), \
             patch.object(pipeline, "_aws_client", side_effect=lambda c, s: _FakeService()), \
             patch.object(pipeline, "export_tables", side_effect=fake_export):
            result = pipeline.run_pipeline()

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["tables"]), 2)
        self.assertEqual(result["rows"], 20)
        self.assertEqual(result["s3"]["prefix"], "s3://nanopro-data-lake/bronze/bigquery/")
        self.assertEqual(result["aws_services"]["sqs"]["status"], "sent")
        self.assertEqual(result["aws_services"]["dynamodb"]["status"], "recorded")
        self.assertEqual(result["aws_services"]["cloudwatch"]["status"], "published")
        self.assertEqual(result["aws_services"]["glue"]["status"], "registered")
        self.assertEqual(result["aws_services"]["glue"]["tables"], 2)
        prefixes = {item[2] for item in exported}
        self.assertEqual(prefixes, {"bronze/bigquery/nanopro_cbs_bronze"})
        self.assertNotIn("nanopro_studio", {item[0] for item in exported})

    def test_register_catalog_maps_types_and_locations(self):
        cfg = {"access_key": "a", "secret_key": "b", "region": "ap-southeast-2", "bucket": "nanopro-data-lake"}
        captured = []

        class _Glue(_FakeService):
            def create_table(self, **kwargs):
                captured.append(kwargs["TableInput"])
                return {}

        files = [{
            "table": "Customers",
            "key": "bronze/bigquery/nanopro_cbs_bronze/customers/customers.parquet",
            "columns": [
                {"name": "CUSTOMER_ID", "type": "VARCHAR"},
                {"name": "BALANCE", "type": "DECIMAL(10,2)"},
                {"name": "OPENED_ON", "type": "DATE"},
            ],
        }]
        with patch.object(pipeline, "_aws_client", return_value=_Glue()):
            res = pipeline._register_catalog(cfg, files)

        self.assertEqual(res["status"], "registered")
        self.assertEqual(res["database"], "nanopro_bronze")
        table = captured[0]
        self.assertEqual(table["Name"], "customers")
        self.assertEqual(table["StorageDescriptor"]["Location"],
                         "s3://nanopro-data-lake/bronze/bigquery/nanopro_cbs_bronze/customers/")
        types = {col["Name"]: col["Type"] for col in table["StorageDescriptor"]["Columns"]}
        self.assertEqual(types, {"customer_id": "string", "balance": "decimal(10,2)", "opened_on": "date"})

    def test_run_pipeline_bigquery_listing_failure_is_honest(self):
        cfg = {"access_key": "a", "secret_key": "b", "region": "ap-southeast-2", "bucket": "nanopro-data-lake"}
        bq = _FakeBqClient([], fail_list=True)
        with patch.object(pipeline, "_aws_config", return_value=cfg), \
             patch.object(pipeline, "_bq_client", return_value=bq), \
             patch.object(pipeline, "_s3_client", return_value=object()), \
             patch.object(pipeline, "_aws_client", side_effect=lambda c, s: _FakeService()):
            result = pipeline.run_pipeline()
        self.assertEqual(result["status"], "error")
        self.assertIn("BigQuery dataset listing failed", result["message"])
        self.assertEqual(result["_http"], 502)

    def test_run_pipeline_partial_when_one_dataset_fails(self):
        cfg = {"access_key": "a", "secret_key": "b", "region": "ap-southeast-2", "bucket": "nanopro-data-lake"}
        bq = _FakeBqClient(
            ["good", "bad"],
            {"good": ["t1"], "bad": ["t2"]},
        )

        def fake_export(client, s3, bucket, schema, tables, prefix=""):
            if schema == "bad":
                raise RuntimeError("S3 upload denied")
            return _manifest(schema, tables)

        with patch.object(pipeline, "_aws_config", return_value=cfg), \
             patch.object(pipeline, "_bq_client", return_value=bq), \
             patch.object(pipeline, "_s3_client", return_value=object()), \
             patch.object(pipeline, "_aws_client", side_effect=lambda c, s: _FakeService()), \
             patch.object(pipeline, "export_tables", side_effect=fake_export):
            result = pipeline.run_pipeline()

        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["tables"]), 1)
        self.assertTrue(any("bad" in f for f in result["failures"]))

    def test_run_pipeline_requires_bucket(self):
        with patch.object(pipeline, "_aws_config", return_value={
            "access_key": "", "secret_key": "", "region": "ap-southeast-2", "bucket": "",
        }):
            result = pipeline.run_pipeline()
        self.assertEqual(result["status"], "error")
        self.assertIn("AWS_S3_BUCKET", result["message"])


if __name__ == "__main__":
    unittest.main()
