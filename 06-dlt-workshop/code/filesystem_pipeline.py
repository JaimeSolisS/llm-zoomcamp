"""dlt filesystem pipeline: load Claude conversation logs from local JSONL files into DuckDB."""

import dlt
from dlt.sources.filesystem import filesystem, read_jsonl


def load_raw_logs() -> None:
    """Load all Claude session JSONL logs into DuckDB.

    bucket_url is read from .dlt/config.toml under [sources.filesystem].
    file_glob matches all .jsonl files recursively across project folders.
    """
    pipeline = dlt.pipeline(
        pipeline_name="claude_logs",
        destination="duckdb",
        dataset_name="claude_data",
        dev_mode=True,
    )

    reader = (filesystem(file_glob="**/*.jsonl") | read_jsonl()).with_name("raw_logs")

    load_info = pipeline.run(reader, write_disposition="replace")
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_raw_logs()
