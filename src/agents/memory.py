import logging
from typing import List, Dict, Any, Optional

class MemoryKeeper:
    """
    Stores the conversational memory (Q&A pairs with sources).
    Suitable for single-session/single-user applications.
    """

    def __init__(self, max_length: Optional[int] = None):
        """
        :param max_length: If set, only keep the latest max_length entries (FIFO).
        """
        self.history: List[Dict[str, Any]] = []
        self.max_length = max_length
        self.logger = logging.getLogger("MemoryKeeper")

    def add(self, question: str, answer: str, sources: Optional[Any] = None) -> None:
        """
        Store an entry containing question, answer and sources.
        """
        entry = {
            "question": question,
            "answer": answer,
            "sources": sources
        }
        self.history.append(entry)
        if self.max_length is not None and len(self.history) > self.max_length:
            # Remove oldest entry (FIFO)
            removed = self.history.pop(0)
            self.logger.debug(f"Max history exceeded; removing oldest entry: {removed}")

        self.logger.info(f"Added memory entry. Total entries: {len(self.history)}")

    def get_history(self, n: int = None) -> List[Dict[str, Any]]:
        """
        Return the last n entries (or all if n is None).
        Returns a copy to prevent outside mutation.
        """
        if n is None:
            return list(self.history)
        else:
            return list(self.history[-n:])

    def get_last_question(self) -> Optional[str]:
        """
        Returns the most recent question, or None if memory is empty.
        """
        if self.history:
            return self.history[-1]["question"]
        return None

    def get_last_answer(self) -> Optional[str]:
        """
        Returns the most recent answer, or None if memory is empty.
        """
        if self.history:
            return self.history[-1]["answer"]
        return None

    def clear(self) -> None:
        """
        Clears all memory entries.
        """
        self.logger.info(f"Memory cleared. {len(self.history)} entries removed.")
        self.history = []

    def export_memory(self) -> List[Dict[str, Any]]:
        """
        Returns the entire conversation history as a list of dicts (deep copy).
        """
        import copy
        return copy.deepcopy(self.history)

    def import_memory(self, history: List[Dict[str, Any]]) -> None:
        """
        Loads memory from a provided history list (overwrites existing memory).
        """
        import copy
        self.history = copy.deepcopy(history)
        self.logger.info(f"Memory imported with {len(self.history)} entries.")
