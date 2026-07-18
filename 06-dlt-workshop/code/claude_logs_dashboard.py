import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import dlt

    return alt, dlt, mo


@app.cell
def _(dlt):
    pipeline = dlt.attach("claude_logs")
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(mo):
    mo.md("""
    # Claude Code Usage Dashboard
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Daily Output Tokens
    """)
    return


@app.cell
def _(dataset):
    df_chart1 = dataset("""
        SELECT
            DATE_TRUNC('day', timestamp)::DATE AS day,
            SUM(message__usage__output_tokens) AS output_tokens,
            COUNT(DISTINCT session_id) AS sessions
        FROM raw_logs
        WHERE timestamp IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """).df()
    return (df_chart1,)


@app.cell
def _(alt, df_chart1):
    _chart = alt.Chart(df_chart1).mark_line(point=True, color='steelblue').encode(
        x=alt.X("day:T", title="Date"),
        y=alt.Y("output_tokens:Q", title="Output Tokens"),
        tooltip=["day:T", "output_tokens:Q", "sessions:Q"]
    ).properties(title="Daily Output Tokens", width=600, height=300)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Model Usage
    """)
    return


@app.cell
def _(dataset):
    df_chart2 = dataset("""
        SELECT
            message__model AS model,
            COUNT(*) AS messages
        FROM raw_logs
        WHERE message__model IS NOT NULL
          AND message__model != '<synthetic>'
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()
    return (df_chart2,)


@app.cell
def _(alt, df_chart2):
    _chart = alt.Chart(df_chart2).mark_bar().encode(
        x=alt.X("messages:Q", title="Message Count"),
        y=alt.Y("model:N", sort="-x", title="Model"),
        color=alt.Color("model:N", legend=None),
        tooltip=["model:N", "messages:Q"]
    ).properties(title="Messages by Claude Model", width=500, height=200)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Cache Efficiency by Session
    """)
    return


@app.cell
def _(dataset):
    df_chart3 = dataset("""
        SELECT
            SUBSTRING(session_id, 1, 8) AS session_short,
            MIN(timestamp)::DATE AS session_date,
            SUM(message__usage__cache_read_input_tokens) AS cache_read_tokens,
            SUM(message__usage__cache_creation_input_tokens) AS cache_write_tokens,
            SUM(message__usage__output_tokens) AS output_tokens
        FROM raw_logs
        WHERE session_id IS NOT NULL
        GROUP BY session_id
        ORDER BY MIN(timestamp)
    """).df()
    return (df_chart3,)


@app.cell
def _(alt, df_chart3):
    _melted = df_chart3.melt(
        id_vars=["session_short", "session_date"],
        value_vars=["cache_read_tokens", "cache_write_tokens", "output_tokens"],
        var_name="token_type", value_name="tokens"
    )
    _chart = alt.Chart(_melted).mark_bar().encode(
        x=alt.X("session_short:N", title="Session (first 8 chars)", sort="ascending"),
        y=alt.Y("tokens:Q", title="Tokens"),
        color=alt.Color("token_type:N", title="Token Type"),
        tooltip=["session_short:N", "session_date:T", "token_type:N", "tokens:Q"]
    ).properties(title="Token Breakdown by Session", width=600, height=300)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Session Duration vs Events
    """)
    return


@app.cell
def _(dataset):
    df_chart4 = dataset("""
        SELECT
            SUBSTRING(session_id, 1, 8) AS session_short,
            MIN(timestamp)::DATE AS session_date,
            EPOCH(MAX(timestamp) - MIN(timestamp)) / 60.0 AS duration_minutes,
            COUNT(*) AS events
        FROM raw_logs
        WHERE timestamp IS NOT NULL AND session_id IS NOT NULL
        GROUP BY session_id
        HAVING EPOCH(MAX(timestamp) - MIN(timestamp)) / 60.0 < 500
    """).df()
    return (df_chart4,)


@app.cell
def _(alt, df_chart4):
    _chart = alt.Chart(df_chart4).mark_circle(size=120).encode(
        x=alt.X("duration_minutes:Q", title="Duration (minutes)"),
        y=alt.Y("events:Q", title="Event Count"),
        color=alt.Color("session_date:T", title="Date"),
        tooltip=["session_short:N", "session_date:T", "duration_minutes:Q", "events:Q"]
    ).properties(title="Session Duration vs Event Count", width=500, height=300)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Activity by Project
    """)
    return


@app.cell
def _(dataset):
    df_chart5 = dataset("""
        SELECT
            REGEXP_REPLACE(cwd, '.*/([^/]+/[^/]+)$', '\\1') AS project,
            COUNT(DISTINCT session_id) AS sessions,
            COUNT(*) AS events
        FROM raw_logs
        WHERE cwd IS NOT NULL
        GROUP BY 1
        ORDER BY sessions DESC
    """).df()
    return (df_chart5,)


@app.cell
def _(alt, df_chart5):
    _chart = alt.Chart(df_chart5).mark_bar().encode(
        x=alt.X("sessions:Q", title="Sessions"),
        y=alt.Y("project:N", sort="-x", title="Project"),
        color=alt.Color("events:Q", title="Events", scale=alt.Scale(scheme="blues")),
        tooltip=["project:N", "sessions:Q", "events:Q"]
    ).properties(title="Sessions per Project", width=500, height=280)
    _chart
    return


if __name__ == "__main__":
    app.run()
