from haystack import Pipeline, Document
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.writers import DocumentWriter
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack.utils import ComponentDevice
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.routers import FileTypeRouter
import os
from ..models import Paper
from haystack.components.converters import MarkdownToDocument, PyPDFToDocument, TextFileToDocument

from dataclasses import dataclass

@dataclass
class PaperSearch:
    title: str
    authors: str
    year: int
    url: str
    further_information: str
    content: str
    pk: int

HAYSTACK_TELEMETRY_ENABLED = "False"

# MODEL_PATH = "sentence-transformers/all-mpnet-base-v2"
MODEL_SIM_RANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"



class HaystackSearch:
    def __init__(self) -> None:
        self.document_store = self.load_from_disk()
        document_splitter = DocumentSplitter(split_by="word", split_length=512, split_overlap=32)
        document_embedder = SentenceTransformersDocumentEmbedder(meta_fields_to_embed=["title", "further_information"])
        document_embedder.warm_up()
        document_writer = DocumentWriter(self.document_store)

        # self.indexing_pipeline = Pipeline()
        # self.indexing_pipeline.add_component("document_splitter", document_splitter)
        # self.indexing_pipeline.add_component("document_embedder", document_embedder)
        # self.indexing_pipeline.add_component("document_writer", document_writer)

        # self.indexing_pipeline.connect("document_splitter", "document_embedder")
        # self.indexing_pipeline.connect("document_embedder", "document_writer")        

        # self.indexing_pipeline = Pipeline()
        # self.indexing_pipeline.add_component("converter", PyPDFToDocument())
        # self.indexing_pipeline.add_component("cleaner", DocumentCleaner())
        # self.indexing_pipeline.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=5))
        # self.indexing_pipeline.add_component("document_embedder", document_embedder)
        # self.indexing_pipeline.add_component("writer", DocumentWriter(document_store=self.document_store))
        # self.indexing_pipeline.connect("converter", "cleaner")
        # self.indexing_pipeline.connect("cleaner", "splitter")
        # self.indexing_pipeline.connect("splitter", "document_embedder")
        # self.indexing_pipeline.connect("document_embedder", "writer")
        file_type_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"])
        text_file_converter = TextFileToDocument()
        markdown_converter = MarkdownToDocument()
        pdf_converter = PyPDFToDocument()
        document_joiner = DocumentJoiner()
        document_cleaner = DocumentCleaner()
        document_splitter = DocumentSplitter(split_by="word", split_length=150, split_overlap=50)


        self.indexing_pipeline = Pipeline()
        self.indexing_pipeline.add_component(instance=file_type_router, name="file_type_router")
        self.indexing_pipeline.add_component(instance=text_file_converter, name="text_file_converter")
        self.indexing_pipeline.add_component(instance=markdown_converter, name="markdown_converter")
        self.indexing_pipeline.add_component(instance=pdf_converter, name="pypdf_converter")
        self.indexing_pipeline.add_component(instance=document_joiner, name="document_joiner")
        self.indexing_pipeline.add_component(instance=document_cleaner, name="document_cleaner")
        self.indexing_pipeline.add_component(instance=document_splitter, name="document_splitter")
        self.indexing_pipeline.add_component(instance=document_embedder, name="document_embedder")
        self.indexing_pipeline.add_component(instance=document_writer, name="document_writer")

        self.indexing_pipeline.connect("file_type_router.text/plain", "text_file_converter.sources")
        self.indexing_pipeline.connect("file_type_router.application/pdf", "pypdf_converter.sources")
        self.indexing_pipeline.connect("file_type_router.text/markdown", "markdown_converter.sources")
        self.indexing_pipeline.connect("text_file_converter", "document_joiner")
        self.indexing_pipeline.connect("pypdf_converter", "document_joiner")
        self.indexing_pipeline.connect("markdown_converter", "document_joiner")
        self.indexing_pipeline.connect("document_joiner", "document_cleaner")
        self.indexing_pipeline.connect("document_cleaner", "document_splitter")
        self.indexing_pipeline.connect("document_splitter", "document_embedder")
        self.indexing_pipeline.connect("document_embedder", "document_writer")

        

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

        print(self.document_store.count_documents())

    def add_documents(self, documents):
        self.indexing_pipeline.run({"document_splitter": {"documents": documents}})

    
    def add_or_update_papers(self, papers:list[Paper]):
        def get_meta(paper:Paper):
            return {
                    "authors": paper.authors, 
                    "title": paper.title,
                    "further_information": paper.further_information,
                    "db_id": paper.pk,
            }
        
        if isinstance(papers, Paper):
            papers = [papers]    
        # TODO
        if isinstance(papers, list):
            self.delete_papers(papers)
            for p in papers:
                self.indexing_pipeline.run({"file_type_router": {"sources": [p.file.path], "meta": get_meta(p)}})
        else:
            raise TypeError("Argument should be a paper or a list of papers")
        
        self.save_to_disk()
        # self.indexing_pipeline.run({"converter": {"sources": file_names}})

        # self.indexing_pipeline.run({"document_splitter": {"documents": docs}})

    def delete_papers(self, paper):
        if isinstance(paper, Paper):
            self.document_store.delete_documents([paper.id])       
        elif isinstance(paper, list) and isinstance(paper[0], Paper):
            self.document_store.delete_documents([r.id for r in paper])
        elif isinstance(paper, list) and isinstance(paper[0], int):
            self.document_store.delete_documents(paper)

        self.save_to_disk()

    def save_to_disk(self) -> None:
        print("saving to disk")
        self.document_store.save_to_disk("paper-db.json")

    def load_from_disk(self) -> InMemoryDocumentStore:
        if not os.path.exists("paper-db.json"):
            print("empty db")
            return InMemoryDocumentStore()
        return InMemoryDocumentStore.load_from_disk("paper-db.json")
        
    def search(self, query:str):
        result = self.document_ranker_pipeline.run(
                                        {"text_embedder": {"text": query}, 
                                         "bm25_retriever": {"query": query, "top_k": 20,}, 
                                         "ranker": {"query": query, "top_k": 20}}
        )
        print(self.document_store.count_documents())
        final_result = []
        
        paper_id2obj = {p.pk: p for p in Paper.objects.all()}
        for rank, doc in enumerate(result['ranker']["documents"], 1):
            doc_id = doc.meta["db_id"]
            if doc_id not in paper_id2obj:
                continue
            paper = paper_id2obj[doc_id]
            # paper_search = PaperSearch(
            #     title=paper.title,
            #     authors=paper.authors,
            #     year=paper.year,
            #     url=paper.url,
            #     further_information=paper.further_information,
            #     content=doc.content,
            #     pk=paper.pk
            # )
            if hasattr(paper, "content"):
                paper.content.append(doc.content)
            else:
                paper.content = [doc.content]
            if paper not in final_result:
                final_result.append(paper)
        print(final_result)
        return final_result