import logging
import re
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
        """Handles a user question and returns a structured response with sources and conversational memory."""
        meta_q = question.lower().strip()
        history = self.memory.get_history()
        ORDINAL_WORDS = {
            "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
            "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
        }

        # --- Meta-question handlers ---
        for word, n in ORDINAL_WORDS.items():
            if f"{word} question" in meta_q:
                if n <= len(history):
                    answer = history[n-1]["question"]
                else:
                    answer = f"There is no question number {n}."
                return {"answer": answer, "sources": [], "memory": history}
        nth_q_match = re.search(r"(?:what\s+was\s+)?(?:the\s+)?(\d+)(?:st|nd|rd|th)?\s+question", meta_q)
        if nth_q_match:
            n = int(nth_q_match.group(1))
            if 1 <= n <= len(history):
                answer = history[n - 1]["question"]
            else:
                answer = f"There is no question number {n}."
            return {"answer": answer, "sources": [], "memory": history}
        if "last question" in meta_q:
            answer = history[-2]["question"] if len(history) > 1 else "Not enough history."
            return {"answer": answer, "sources": [], "memory": history}
        if "last answer" in meta_q:
            answer = history[-2]["answer"] if len(history) > 1 else "Not enough history."
            return {"answer": answer, "sources": [], "memory": history}
        if "previous questions" in meta_q or "list questions" in meta_q:
            questions = [entry["question"] for entry in history[:-1]] if len(history) > 1 else []
            answer = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions)) if questions else "No previous questions."
            return {"answer": answer, "sources": [], "memory": history}

        # --- Normal question (RAG) flow ---
        try:
            pdf_chunks = self.retriever.retrieve(question)
        except Exception as e:
            self.logger.error(f"Failed to retrieve from PDFs: {e}")
            pdf_chunks = []
        try:
            web_chunks = self.websearcher.search(question, num_results=3)
        except Exception as e:
            self.logger.error(f"Failed to retrieve from web: {e}")
            web_chunks = []

        history3 = self.memory.get_history(n=3)
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

        if not all_chunks or not all(isinstance(chunk, dict) and "text" in chunk for chunk in all_chunks):
            self.logger.debug(f"No valid text chunks found in retrieval. Chunks: {all_chunks}")
            result = {
                "answer": "Sorry, I couldn't find any relevant information in the documents or online.",
                "sources": [],
                "reasoning": "No retrievable context."
            }
        else:
            try:
                result = self.synthesizer.synthesize(question, all_chunks, history=history3)
            except Exception as e:
                self.logger.error(f"Synthesizer failed: {e}")
                result = {
                    "answer": "Sorry, an error occurred while generating the answer.",
                    "sources": [],
                    "reasoning": f"Error: {e}"
                }

        self.memory.add(question, result["answer"], result["sources"])
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "memory": history3,
        }



