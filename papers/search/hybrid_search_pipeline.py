from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.utils import ComponentDevice
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from ..models import Paper

MODEL_SIM_RANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class HybridSearchPipeline:
    def __init__(self, document_store:InMemoryDocumentStore):
        self.document_store = document_store
        text_embedder = SentenceTransformersTextEmbedder(
            device=ComponentDevice.from_str("cpu")
        )
        text_embedder.warm_up()
        self.embedding_retriever = InMemoryEmbeddingRetriever(document_store=self.document_store)
        bm25_retriever = InMemoryBM25Retriever(document_store=self.document_store)
        document_joiner = DocumentJoiner()

        self.ranker = TransformersSimilarityRanker(model=MODEL_SIM_RANKER)
        self.ranker.warm_up()

        self.document_ranker_pipeline = Pipeline()

        self.document_ranker_pipeline.add_component("text_embedder", text_embedder)
        self.document_ranker_pipeline.add_component("embedding_retriever", self.embedding_retriever)
        self.document_ranker_pipeline.add_component("bm25_retriever", bm25_retriever)
        self.document_ranker_pipeline.add_component("document_joiner", document_joiner)
        self.document_ranker_pipeline.add_component("ranker", self.ranker)

        self.document_ranker_pipeline.connect("text_embedder", "embedding_retriever")
        self.document_ranker_pipeline.connect("bm25_retriever", "document_joiner")
        self.document_ranker_pipeline.connect("embedding_retriever", "document_joiner")
        self.document_ranker_pipeline.connect("document_joiner", "ranker")
        

    def run(self, query:str):
        result = self.document_ranker_pipeline.run(
                                        {"text_embedder": {"text": query}, 
                                         "bm25_retriever": {"query": query, "top_k": 20,}, 
                                         "ranker": {"query": query, "top_k": 20}}
        )
        final_result = []
        
        paper_id2obj = {p.pk: p for p in Paper.objects.all()}
        for rank, doc in enumerate(result['ranker']["documents"], 1):
            doc_id = doc.meta["db_id"]
            if doc_id not in paper_id2obj:
                continue
            paper = paper_id2obj[doc_id]
            if hasattr(paper, "content"):
                paper.content.append(doc.content)
                paper.documents.append(doc)
            else:
                paper.content = [doc.content]
                paper.documents = [doc]

            if paper not in final_result:
                final_result.append(paper)
        return final_result