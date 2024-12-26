from haystack import Pipeline
from ..models import Paper
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever


template = """
Given the following content, answer the question.

Context: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}
"""


class PaperQAPipeline:
    def __init__(self, document_store: InMemoryDocumentStore):
        self.pipe = Pipeline()
        self.pipe.add_component("embedder", SentenceTransformersTextEmbedder())
        self.pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
        self.pipe.add_component("prompt_builder", PromptBuilder(template=template))
        self.pipe.add_component("gemini", GoogleAIGeminiGenerator(model="gemini-1.5-flash"))
        
        self.pipe.connect("embedder.embedding", "retriever.query_embedding")
        self.pipe.connect("retriever", "prompt_builder.documents")
        self.pipe.connect("prompt_builder", "gemini")
        self.document_store = document_store

    def run(self, query:str, paper:Paper|None = None):
        if paper:
            res = self.pipe.run({"embedder": {"text": query, }, 
                                "retriever": {"filters": {"field": "meta.db_id", "operator": "==", "value": paper.pk}},
                                "prompt_builder": {"query": query}
            })
        else:
            res = self.pipe.run({"embedder": {"text": query, }, 
                                "prompt_builder": {"query": query}
            })

        return "\n".join(res["gemini"]["replies"])
    