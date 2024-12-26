from haystack import Pipeline
from ..models import Paper
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
import os


template = """
Given the query, summarize the following information and add additional information only if necessary.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Query: {{ query }}
"""


class AiSearchPaperSummaryPipeline:
    def __init__(self, document_store: InMemoryDocumentStore):
        self.summarizer_pipe = Pipeline()
        self.summarizer_pipe.add_component("prompt_builder", PromptBuilder(template=template))
        self.summarizer_pipe.add_component("gemini", GoogleAIGeminiGenerator(model=os.environ.get("GOOGLE_GEMINI_MODEL")))
        self.summarizer_pipe.connect("prompt_builder", "gemini")

        self.document_store = document_store

    def run(self, query, documents):
        res = self.summarizer_pipe.run({
                "prompt_builder": {
                    "documents": documents,
                    "query": query
                }
            })
        return "\n".join(res["gemini"]["replies"])
    
    def summarize_paper(self, paper:Paper):
        self.document_store.filter_documents({"db_id": paper.pk})

        raise NotImplementedError("This method is not implemented yet")