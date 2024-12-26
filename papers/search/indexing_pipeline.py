from haystack import Pipeline, Document
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack.components.joiners import DocumentJoiner
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.routers import FileTypeRouter
import os
from ..models import Paper
from haystack.components.converters import MarkdownToDocument, PyPDFToDocument, TextFileToDocument
from haystack.document_stores.types import DuplicatePolicy


class IndexingPipeline:
    def __init__(self, document_store: InMemoryDocumentStore) -> None:
        self.document_store = document_store

        file_type_router = FileTypeRouter(mime_types=["text/plain", "application/pdf", "text/markdown"])
        text_file_converter = TextFileToDocument()
        markdown_converter = MarkdownToDocument()
        pdf_converter = PyPDFToDocument()
        document_joiner = DocumentJoiner()
        document_cleaner = DocumentCleaner()
        document_splitter = DocumentSplitter(split_by="word", split_length=150, split_overlap=50)
        document_splitter = DocumentSplitter(split_by="word", split_length=512, split_overlap=32)
        document_embedder = SentenceTransformersDocumentEmbedder(meta_fields_to_embed=["title", "further_information", "ai_summary"])
        document_embedder.warm_up()
        document_writer = DocumentWriter(self.document_store, policy=DuplicatePolicy.OVERWRITE)


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

    def run(self, paper:Paper, meta_data:dict):
        self.indexing_pipeline.run({"file_type_router": {"sources": [paper.file.path], "meta": meta_data}})