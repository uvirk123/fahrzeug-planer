

import json
import logging

from app.logging_config import JsonFormatter


def test_formatter_outputs_json_with_extra_fields():
    record = logging.makeLogRecord(
        {"name": "test", "levelname": "INFO", "msg": "hello", "method": "GET"}
    )

    output = json.loads(JsonFormatter().format(record))

    assert output["message"] == "hello"
    assert output["level"] == "INFO"
    assert output["method"] == "GET"
    assert "timestamp" in output


def test_requests_are_logged(client, caplog):
    with caplog.at_level(logging.INFO, logger="app"):
        client.get("/health")

    record = next(r for r in caplog.records if r.getMessage() == "request")
    assert record.path == "/health"
    assert record.status_code == 200


def test_rejected_api_key_is_logged_as_warning(client, caplog):
    del client.headers["X-API-Key"]

    with caplog.at_level(logging.WARNING, logger="app"):
        client.get("/projects")

    assert any(r.levelname == "WARNING" for r in caplog.records)