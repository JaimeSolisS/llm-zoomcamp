
from rag_helper import RAGBase
from starter import index, client

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
import sqlite3
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

provider = TracerProvider()

#Console
#provider.add_span_processor(
#    SimpleSpanProcessor(ConsoleSpanExporter())
#)




trace.set_tracer_provider(provider)

tracer = trace.get_tracer("llm-zoomcamp")

class SQLiteSpanExporter(SpanExporter):

    def __init__(self, db_path="traces.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS spans (
                name TEXT,
                start_time INTEGER,
                end_time INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost REAL
            )
        """)
        self.conn.commit()

    def export(self, spans):
        for span in spans:
            attrs = dict(span.attributes or {})
            self.conn.execute(
                "INSERT INTO spans VALUES (?, ?, ?, ?, ?, ?)",
                (
                    span.name,
                    span.start_time,
                    span.end_time,
                    attrs.get("input_tokens"),
                    attrs.get("output_tokens"),
                    attrs.get("cost"),
                ),
            )
        self.conn.commit()
        return SpanExportResult.SUCCESS

    def shutdown(self):
        self.conn.close()

    def force_flush(self):
        return True

#Store to SQLite
provider.add_span_processor(
    SimpleSpanProcessor(SQLiteSpanExporter("traces.db"))
)

class RAGTraced(RAGBase):

    def search(self, query, num_results=5):
        with tracer.start_as_current_span("search") as span:
            response = super().search(query, num_results=num_results)
            return response

    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            response = super().llm(prompt)
            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
            return response

    def rag(self, query):
        with tracer.start_as_current_span("rag") as span:
            response = super().rag(query)
            return response


if __name__ == "__main__":
    rag = RAGTraced(index=index, llm_client=client)
    query = "How does the agentic loop keep calling the model until it stops?"
    answer = rag.rag(query)
    print(answer)
