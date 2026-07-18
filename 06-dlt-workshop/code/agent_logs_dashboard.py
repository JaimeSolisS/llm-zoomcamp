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
    #pipeline = dlt.attach("agent_logs")
    pipeline = dlt.attach("agent_logs", destination="playground", dataset_name="agent_data")
    dataset = pipeline.dataset()
    return (dataset,)


@app.cell
def _(mo):
    mo.md("""
    # Claude Code Agent Logs Dashboard
    **20,000 records** · 2,476 sessions · 5 projects · 4 models · 2 days (2026-01-01 to 2026-01-02)
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Messages by Claude Model
    """)
    return


@app.cell
def _(dataset):
    df_chart1 = dataset("""
        SELECT
            message__model AS model,
            COUNT(*) AS messages
        FROM logs
        WHERE message__model IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()
    return (df_chart1,)


@app.cell
def _(alt, df_chart1):
    _chart = alt.Chart(df_chart1).mark_bar().encode(
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
    ## Sessions per Project
    """)
    return


@app.cell
def _(dataset):
    df_chart2 = dataset(r"""
        SELECT
            REGEXP_REPLACE(cwd, '.*/([^/]+)$', '\1') AS project,
            COUNT(DISTINCT session_id) AS sessions,
            COUNT(*) AS events
        FROM logs
        WHERE cwd IS NOT NULL
        GROUP BY 1
        ORDER BY sessions DESC
    """).df()
    return (df_chart2,)


@app.cell
def _(alt, df_chart2):
    _chart = alt.Chart(df_chart2).mark_bar().encode(
        x=alt.X("sessions:Q", title="Sessions"),
        y=alt.Y("project:N", sort="-x", title="Project"),
        color=alt.Color("events:Q", title="Total Events", scale=alt.Scale(scheme="blues")),
        tooltip=["project:N", "sessions:Q", "events:Q"]
    ).properties(title="Sessions per Project", width=500, height=250)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Events by Git Branch
    """)
    return


@app.cell
def _(dataset):
    df_chart3 = dataset("""
        SELECT
            git_branch,
            COUNT(*) AS events,
            COUNT(DISTINCT session_id) AS sessions
        FROM logs
        WHERE git_branch IS NOT NULL
        GROUP BY 1
        ORDER BY events DESC
    """).df()
    return (df_chart3,)


@app.cell
def _(alt, df_chart3):
    _chart = alt.Chart(df_chart3).mark_bar(color='steelblue').encode(
        x=alt.X("git_branch:N", sort="-y", title="Git Branch"),
        y=alt.Y("events:Q", title="Event Count"),
        tooltip=["git_branch:N", "events:Q", "sessions:Q"]
    ).properties(title="Events by Git Branch", width=450, height=280)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Input vs Output Tokens per Project
    """)
    return


@app.cell
def _(dataset):
    df_chart4 = dataset(r"""
        SELECT
            REGEXP_REPLACE(cwd, '.*/([^/]+)$', '\1') AS project,
            SUM(usage__input_tokens) / 1e6 AS input_tokens_m,
            SUM(usage__output_tokens) / 1e6 AS output_tokens_m
        FROM logs
        WHERE cwd IS NOT NULL
        GROUP BY 1
        ORDER BY input_tokens_m DESC
    """).df()
    return (df_chart4,)


@app.cell
def _(alt, df_chart4):
    import pandas as pd
    _melted = df_chart4.melt(
        id_vars=["project"],
        value_vars=["input_tokens_m", "output_tokens_m"],
        var_name="token_type", value_name="tokens_millions"
    )
    _chart = alt.Chart(_melted).mark_bar().encode(
        x=alt.X("project:N", title="Project"),
        y=alt.Y("tokens_millions:Q", title="Tokens (millions)"),
        color=alt.Color("token_type:N", title="Token Type"),
        xOffset="token_type:N",
        tooltip=["project:N", "token_type:N", alt.Tooltip("tokens_millions:Q", format=".2f")]
    ).properties(title="Input vs Output Tokens per Project (millions)", width=500, height=300)
    _chart
    return


@app.cell
def _(mo):
    mo.md("""
    ## Assistant Stop Reasons
    """)
    return


@app.cell
def _(dataset):
    df_chart5 = dataset("""
        SELECT
            message__stop_reason AS stop_reason,
            COUNT(*) AS count
        FROM logs
        WHERE message__stop_reason IS NOT NULL
        GROUP BY 1
        ORDER BY count DESC
    """).df()
    return (df_chart5,)


@app.cell
def _(alt, df_chart5):
    _chart = alt.Chart(df_chart5).mark_arc(innerRadius=60).encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color("stop_reason:N", title="Stop Reason"),
        tooltip=["stop_reason:N", "count:Q"]
    ).properties(title="Assistant Stop Reasons", width=300, height=300)
    _chart
    return


if __name__ == "__main__":
    app.run()
