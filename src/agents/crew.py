import logging
from agents.retriever import PDFRetriever
from agents.synthesizer import Synthesizer
from agents.memory import MemoryKeeper
from agents.websearcher import WebSearcher
from typing import Dict, Any

class Crew:
    """
    Orchestrates Retriever, WebSearcher, Synthesizer, and Memory agents to answer questions with full citations.
    """

    def __init__(
            self,
            papers_dir: str = "papers",
            persist_dir: str = "chroma_db",
            model: str = "gpt-3.5-turbo"
    ):
        """
        Initializes all crew agents and prepares retriever vector store.
        """
        self.logger = logging.getLogger("Crew")
        self.retriever = PDFRetriever(papers_dir, persist_dir)
        self.synthesizer = Synthesizer(model=model)
        self.memory = MemoryKeeper()
        self.websearcher = WebSearcher()

        try:
            self.retriever.load_existing_index()
            self.logger.info("Vector DB loaded from disk.")
        except Exception as e:
            self.logger.warning(f"No existing index found, building index: {e}")
            try:
                self.retriever.load_and_index_papers()
                self.logger.info("Vector DB created and persisted.")
            except Exception as err:
                self.logger.error(f"Failed to build vector DB: {err}")
                raise

    def handle_question(self, question: str) -> Dict[str, Any]:
        """
        Handles a user question by retrieving PDF and web evidence, synthesizing an answer,
        saving it in memory, and returning a structured response.
        """
        # 1. Retrieve from PDFs
        try:
            pdf_chunks = self.retriever.retrieve(question)
        except Exception as e:
            self.logger.error(f"Failed to retrieve from PDFs: {e}")
            pdf_chunks = []

        # 2. Retrieve from web
        try:
            web_chunks = self.websearcher.search(question, num_results=3)
        except Exception as e:
            self.logger.error(f"Failed to retrieve from web: {e}")
            web_chunks = []

        # 3. Get conversational memory (last 3 QAs)
        history = self.memory.get_history(n=3)

        # 4. Combine chunks, numbering PDFs as [1], [2] and web as [W1], [W2]
        all_chunks = []
        for i, chunk in enumerate(pdf_chunks):
            chunk = dict(chunk)
            chunk["citation_type"] = "pdf"
            chunk["citation_num"] = i + 1
            all_chunks.append(chunk)
        for i, chunk in enumerate(web_chunks):
            chunk = dict(chunk)
            chunk["citation_type"] = "web"
            chunk["citation_num"] = i + 1
            all_chunks.append(chunk)

        # 5. Synthesize answer
        try:
            result = self.synthesizer.synthesize(question, all_chunks)
        except Exception as e:
            self.logger.error(f"Synthesizer failed: {e}")
            result = {
                "answer": "Sorry, an error occurred while generating the answer.",
                "sources": [],
                "reasoning": f"Error: {e}"
            }

        # 6. Store in memory
        self.memory.add(question, result["answer"], result["sources"])

        # 7. Return structured response
        response = {
            "answer": result["answer"],
            "sources": result["sources"],
            "memory": history,
        }
        return response
