"""dlt REST API pipeline: load Claude Code agent logs from test API into DuckDB."""

import dlt
from dlt.sources.rest_api import rest_api_source, RESTAPIConfig
from dlt.hub import run

BASE_URL = "https://test-agent-traces-api-xt2e7ottma-ew.a.run.app"


@run.pipeline("agent_logs")
def load_agent_logs(max_records: int = 20_000) -> None:
    """Load Claude Code agent logs from the test API into DuckDB.

    Args:
        max_records: Total records to load. Defaults to 20,000.
                     API supports up to 1,000,000. Max 1,000 per page.
    """
    pipeline = dlt.pipeline(
        pipeline_name="agent_logs",
        destination="playground",
        dataset_name="agent_data",
    )

    config: RESTAPIConfig = {
        "client": {
            "base_url": BASE_URL,
        },
        "resources": [
            {
                "name": "logs",
                "endpoint": {
                    "path": "/logs",
                    "method": "GET",
                    "params": {
                        "limit": 1000,
                    },
                    "data_selector": "logs",
                    "paginator": {
                        "type": "offset",
                        "limit": 1000,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "total",
                        "maximum_offset": max_records,
                    },
                },
                "primary_key": "index",
                "write_disposition": "replace",
            }
        ],
    }

    source = rest_api_source(config)
    load_info = pipeline.run(source)
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_agent_logs(max_records=20_000)
