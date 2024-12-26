from haystack.document_stores.in_memory import InMemoryDocumentStore
import os
from ..models import Paper
from .indexing_pipeline import IndexingPipeline
from .hybrid_search_pipeline import HybridSearchPipeline
from .ai_summary_pipeline import AiSearchPaperSummaryPipeline
from .ai_paper_summary_pipeline import AiPaperSummaryPipeline
from .paper_qa_pipeline import PaperQAPipeline


HAYSTACK_TELEMETRY_ENABLED = "False"

class HaystackSearch:
    def __init__(self) -> None:
        self.document_store = self.load_from_disk()
        self.indexing_pipeline = IndexingPipeline(self.document_store)
        self.hybrid_search_pipeline = HybridSearchPipeline(self.document_store)
        self.ai_summary_pipeline = AiSearchPaperSummaryPipeline(self.document_store)
        self.ai_paper_summary_pipeline = AiPaperSummaryPipeline(self.document_store)
        self.paper_qa_pipeline = PaperQAPipeline(self.document_store)

        print(self.document_store.count_documents())

    def add_or_update_papers(self, papers:list[Paper]):
        def get_meta(paper:Paper):
            return {
                    "authors": paper.authors, 
                    "title": paper.title,
                    "further_information": paper.further_information,
                    "db_id": paper.pk,  
                    "ai_summary": paper.ai_summary                  
            }
        
        if isinstance(papers, Paper):
            papers = [papers]    
        if isinstance(papers, list):
            self.delete_papers(papers)
            for paper in papers:
                self.indexing_pipeline.run(paper, get_meta(paper))
                if paper.ai_summary is None:
                    paper.ai_summary = self.ai_paper_summary_pipeline.run(paper)
                    paper.save()
                    self.add_or_update_papers(paper) # Rerun the pipeline to update the ai_summary field
                                
        else:
            raise TypeError("Argument should be a paper or a list of papers")
        
        self.save_to_disk()

    def delete_papers(self, paper):
        if isinstance(paper, Paper):
            self.document_store.delete_documents([paper.pk])       
        elif isinstance(paper, list) and isinstance(paper[0], Paper):
            self.document_store.delete_documents([r.pk for r in paper])
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
        final_result = self.hybrid_search_pipeline.run(query)
        # for p in final_result:
        #     p.ai_search_summary = self.ai_summary_pipeline.run(query, p.documents)
        return final_result

    def ask_question_about_paper(self, question:str, paper:Paper|None = None):
        return self.paper_qa_pipeline.run(question, paper)
    