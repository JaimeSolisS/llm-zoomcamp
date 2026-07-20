import os
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()

import dlt
from dlt.common.pendulum import pendulum
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="logfire")
def logfire_source(
    read_token: str = os.getenv("LOGFIRE_READ_TOKEN"),
    base_url: str = dlt.config.value,
    sql: str = "SELECT * FROM records ORDER BY start_timestamp DESC",
    min_timestamp: Optional[str] = None,
) -> Any:
    """Load traces (spans) from a Logfire project via the Query API.

    Args:
        read_token: Logfire read token. Auto-loaded from .env (LOGFIRE_READ_TOKEN).
        base_url: Logfire API base URL, e.g. https://logfire-us.pydantic.dev/. Auto-loaded from config.toml.
        sql: SQL query run against Logfire's `records` table (spans/traces).
        min_timestamp: ISO8601 lower bound for `start_timestamp`. Defaults to 30 days ago.

    Example calls:
        pipeline.run(logfire_source())
        pipeline.run(logfire_source(sql="SELECT * FROM records WHERE parent_span_id IS NULL"))
    """
    if min_timestamp is None:
        min_timestamp = pendulum.now("UTC").subtract(days=30).to_iso8601_string()

    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "auth": {
                "type": "bearer",
                "token": read_token,
            },
        },
        "resources": [
            {
                "name": "traces",
                "endpoint": {
                    "path": "v2/query",
                    "method": "POST",
                    "headers": {"Accept": "application/json"},
                    "json": {
                        "sql": sql,
                        "min_timestamp": min_timestamp,
                        "limit": 10000,
                    },
                    "data_selector": "data",
                },
                "write_disposition": "replace",
            },
        ],
    }

    yield from rest_api_resources(config)


def load_logfire_traces() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire_traces",
        destination="duckdb",
        dataset_name="agent_traces",
    )

    load_info = pipeline.run(logfire_source())
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    load_logfire_traces()
