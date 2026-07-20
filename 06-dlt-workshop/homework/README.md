# Homework: dlt

In this homework we will take the FAQ agent from Module 1,
instrument it with [Pydantic Logfire](https://logfire.dev) for
observability,
then pull the trace data back out with dlt and analyze it.

In Module 1 we wrote the agent loop by hand and then we saw toyaikit -
an agentic framework.

For this homework we rewrote into [Pydantic AI](https://ai.pydantic.dev/),
so it's easier to integrate it with Logfire. Pydantic AI and Logfire
work really well together, that's why we use them here.

In Module 5 we learn about monitoring and observability, and implement
our own monitoring solution. Logfire is an alternative for that.

## Getting the code

The rewritten agent is in the [homework/](homework/) directory. Download
it with `wget`:

```bash
PREFIX=https://raw.githubusercontent.com/DataTalksClub/llm-zoomcamp/main/cohorts/2026/workshops/dlt/homework

wget $PREFIX/agent.py
wget $PREFIX/ingest.py
wget $PREFIX/main.py
wget $PREFIX/.env.example -O .env
```

The agent code is in [homework/agent.py](homework/agent.py). Here we use
Pydantic AI which we didn't cover previously.
Conceptually there's nothing new: we covered everything already in module 1.
The comments in the file will explain what's happening and how things map to
what we learned previously.

Make sure to read through it before proceeding.

## Setup

We start by configuring our project:

```bash
uv init
uv add openai minsearch requests python-dotenv pydantic-ai logfire
uv add "dlt[duckdb]"
```

Open `.env` and add your `OPENAI_API_KEY`:

```bash
OPENAI_API_KEY=sk-YOUR_KEY_HERE
```

Make sure it's in `.gitignore`:

```
.env
```

You can use any other provider instead of OpenAI. Check Pydantic AI documentation
to see how you can use your provider.

Verify that the agent runs:

```bash
uv run python main.py
```

## Question 1. Instrument the agent with Logfire

Sign up for a free [Logfire](https://logfire.dev) account, create a
project, and generate a write token. Put it in `.env` as
`LOGFIRE_TOKEN`.

Instrument the agent:

```python
logfire.configure()
logfire.instrument_pydantic_ai()
```

Run the agent a few times with different questions and open your
project on Logfire to see the traces.

For the following query

> How do I run Ollama locally?

how many spans does a single agent run produce?

Each span is either the agent run itself, an LLM call, or a tool call.
The number can vary between runs because the model decides how many
times to search.

- 1
- 5
- 15
- 30

````json
[
    {
        "id": "1d0b969028",
        "course": "llm-zoomcamp",
        "section": "Module 1: RAG",
        "question": "Ollama: How to install Ollama?",
        "answer": "First, install Ollama by visiting [https://ollama.com/download](https://ollama.com/download) and choosing your operating system:\n\n- **macOS**: Download the `.pkg` and install it.\n- **Windows**: Download the `.msi` and install it.\n- **Linux**: Run the following command in the terminal:\n\n  ```bash\n  curl -fsSL https://ollama.com/install.sh | sh\n  ```\n\nOnce installed, open a terminal and type:\n\n```bash\nollama run llama3\n```\n\nThis command will:\n\n- Download the LLaMA 3 model (~4GB).\n- Start the model locally.\n- Open a chat-like interface where you can type questions.\n\nTo test the Ollama local server, run the following command:\n\n```bash\ncurl http://localhost:11434\n```\n\nYou should receive a response similar to:\n\n```json\n{\"models\": [...]}  \n```\n\nThen, install the Python client with:\n\n```bash\npip install ollama\n```\n\nHere is a minimal Python example:\n\n```python\nimport ollama\n\nresponse = ollama.chat(\n    model='llama3',\n    messages=[{\"role\": \"user\", \"content\": your_prompt}]\n)\n\nprint(response['message']['content'])\n```"
    },
    {
        "id": "aa310de435",
        "course": "llm-zoomcamp",
        "section": "Module 1: RAG",
        "question": "Can I run the course locally instead of Codespaces?",
        "answer": "Yes. Codespaces is just the easiest way for everyone to start with the same environment.\n\nYou can run the course locally if you are comfortable setting up Python, `uv`, Jupyter, Docker, and any other tools needed for the module.\n\nIf you run locally, make sure you document your setup and keep your environment reproducible."
    },
    {
        "id": "c6fc2d4d11",
        "course": "llm-zoomcamp",
        "section": "Module 1: RAG",
        "question": "Connection refused error when prompting Ollama RAG",
        "answer": "If you encounter this error while doing the homework, you can resolve it by restarting the Ollama server using the following command:\n\n```bash\n!nohup ollama serve > nohup.out 2>&1 &\n```\n\nMake sure to rerun the cell containing `ollama serve` if you stop and restart the notebook cell."
    },
    {
        "id": "f442efe5b4",
        "course": "llm-zoomcamp",
        "section": "Module 3: Orchestration",
        "question": "Which AI providers does Kestra support besides Gemini? Can I use Groq, Ollama, or a local model?",
        "answer": "Kestra's AI plugin is provider-agnostic: it supports OpenAI, Gemini, Anthropic, xAI, Grok, and any OpenAI-compatible provider, including local models served through Ollama or LM Studio. You swap the provider block in a flow without changing anything else. See the [full list of supported providers](https://kestra.io/plugins/plugin-ai/provider).\n\nThe course uses Gemini because it has a generous free tier, but you are free to use any provider. The [awesome-llms list](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/awesome-llms.md) in the course repo tracks free and free-tier options; Groq is a popular choice because it is OpenAI-compatible and works with both the chat completions and responses APIs.\n\nThere are two ways to use AI in Kestra:\n\n- The **AI plugin** (`io.kestra.plugin.ai`) is the generic one. It is the most flexible for switching providers, though new vendor-specific API features take a bit longer to land here.\n- The **provider-specific plugins** (e.g. `plugin-gemini`, `plugin-openai`) expose features unique to that vendor, such as Gemini video generation, before they reach the generic AI plugin.\n\nFor OpenAI-compatible providers that don't have their own plugin (DeepSeek, Groq, xAI), point the OpenAI plugin at the provider's base URL instead of the default endpoint."
    },
    {
        "id": "830f3d2018",
        "course": "llm-zoomcamp",
        "section": "Module 1: RAG",
        "question": "My Codespace won't reconnect (stuck on \"Finishing up\") or my setup has disappeared — what should I do?",
        "answer": "These are usually GitHub Codespaces reliability issues rather than a problem with the course, so there's no single guaranteed fix — but the following workarounds resolve most cases.\n\n**Codespace won't connect / stuck on \"Finishing up\":**\n\n- Go to [github.com/codespaces](https://github.com/codespaces), stop the codespace, and start it again.\n- If it still won't connect, open it in the **browser** instead of desktop VS Code, or try a different browser (Edge/Chrome/Brave).\n- As a last resort, delete the codespace and create a new one.\n\n**\"My setup is all gone\":**\n\n- The repo in `/workspaces` persists across stop/start, but a **rebuild or a brand-new codespace** starts from a clean image, and system/global installs outside your project don't always survive. Reinstalling is quick with `uv` (`uv sync` / `uv add ...`).\n- **Commit and push your work often** — uncommitted changes survive a stop/start but are lost if you delete or recreate the codespace.\n\nIf Codespaces keeps being flaky for you, consider running the course locally instead — see \"[Can I run the course locally instead of Codespaces?](026_aa310de435_can-i-run-the-course-locally-instead-of-codespaces.md)\"."
    }
]
````

**Answer: 4**

## Question 2. Load traces into DuckDB with dlt

Generate a read token for your Logfire project and set it as
`LOGFIRE_READ_TOKEN` in `.env`.

Initialize a dlt-hub project like in the workshop. Then ask your coding
agent to pull the data from Pydantic Logfire and save it into DuckDB.

The dltHub AI workbench has a ready-made context for Logfire. Point your
agent to it: https://dlthub.com/context/source/logfire

If you don't currently use a coding agent, you can use something like OpenCode:
you should be able to complete one session with the free account.

Alternatively, you can do it in the old way (using ChatGPT or your favorite search engine).

If you don't currently use a coding agent, you can use something like OpenCode:
you should be able to complete one session with the free account.

Alternatively, you can do it in the old way (using ChatGPT or your favorite search engine).

The logfire traces contain deeply nested JSON (span attributes with
LLM messages, tool calls, token usage, etc.). dlt automatically
normalizes this into a set of tables - one for the main records, plus
child tables for each nested level.

How many tables did dlt create? Check with:

```sql
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'agent_traces';
```

- 1
- 3
- 24
- 100

Promt:

> Using the dltHub Logfire source context at https://dlthub.com/context/source/logfire, create a dlt pipeline that reads traces from my Logfire project (using LOGFIRE_READ_TOKEN from .env) and loads them into a DuckDB database, into a schema/dataset called agent_traces.

```sql
SELECT COUNT(*) FROM information_schema.tables
  WHERE table_schema = 'agent_traces';
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│      22      │
└──────────────┘
```

**Answer: 24**

## Question 3. Query traces with an agent

Using a coding agent (you can also write the code by hand) find the
input token usage for the agent run from Q1.

The token counts are stored in the span attributes as
`gen_ai.usage.input_tokens`. Sum them across all LLM calls within the
trace. The number depends on how many searches the agent made, so
report the range it falls into:

- 100 - 500
- 1500 - 5000
- 10000 - 20000
- 50000 - 100000

```bash
SELECT
      trace_id,
      SUM(attributes__gen_ai_usage_input_tokens) AS total_input_tokens
  FROM agent_traces.traces
  WHERE attributes__gen_ai_usage_input_tokens IS NOT NULL
  GROUP BY trace_id;

the trace 019f7302... (from your main.py FAQ agent run) has 2 LLM calls (one tool search in between):

  ┌───────────────────────────────────┬──────────────┬───────────────┐
  │               span                │ input_tokens │ output_tokens │
  ├───────────────────────────────────┼──────────────┼───────────────┤
  │ chat gpt-5.4-mini (before search) │ 204          │ 24            │
  ├───────────────────────────────────┼──────────────┼───────────────┤
  │ chat gpt-5.4-mini (after search)  │ 1532         │ 268           │
  └───────────────────────────────────┴──────────────┴───────────────┘

  Total input tokens = 204 + 1532 = 1736
```

\*\*Answer: 1500-5000

## Submit the results

- Submit your results here: https://courses.datatalks.club/llm-zoomcamp-2026/homework/dlt
