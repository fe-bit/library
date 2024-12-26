from haystack import Pipeline
from ..models import Paper
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore


template = """
Summarize the following information in less than 1000 length.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}
"""


class AiPaperSummaryPipeline:
    def __init__(self, document_store: InMemoryDocumentStore):
        self.summarizer_pipe = Pipeline()
        self.summarizer_pipe.add_component("prompt_builder", PromptBuilder(template=template))
        self.summarizer_pipe.add_component("gemini", GoogleAIGeminiGenerator(model="gemini-1.5-flash"))
        self.summarizer_pipe.connect("prompt_builder", "gemini")
        self.document_store = document_store

    def run(self, paper:Paper):
        documents = self.document_store.filter_documents({"field": "meta.db_id", "operator": "==", "value": paper.pk})
        res = self.summarizer_pipe.run({
                "prompt_builder": {
                    "documents": documents,
                }
            })
        return "\n".join(res["gemini"]["replies"])
    