import re
from typing import List, Dict, Any
import openai

class Synthesizer:
    """
    Synthesizes answers from PDF and web context chunks using an LLM,
    and returns both the answer and the cited sources.
    """

    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.1):
        self.model = model
        self.temperature = temperature

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Formats context for the LLM. Includes text and its citation as [N] or [WN].
        """
        context_strs = []
        for chunk in chunks:
            text = chunk["text"].replace("\n", " ")
            citation = chunk["citation"]
            ctype = chunk.get("citation_type", "pdf")
            cnum = chunk.get("citation_num", 1)
            if ctype == "pdf":
                citation_str = f"[{cnum}] {citation.get('filename', 'PDF')}, page {citation.get('page', '?')}"
            elif ctype == "web":
                citation_str = f"[W{cnum}] {citation.get('title', citation.get('url', 'web'))}"
            else:
                citation_str = f"[{cnum}]"
            context_strs.append(f"{citation_str}: {text}")
        return "\n\n".join(context_strs)
    
    def build_prompt(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Builds a prompt for the LLM including context and explicit instructions.
        """
        context = self.format_context(chunks)
        prompt = (
            "You are an expert neuroscience research assistant. "
            "Given the following extracts from research papers and web sources, answer the user's question. "
            "Cite PDF sources as [1], [2], etc., and web sources as [W1], [W2], etc., using the numbers provided in the context. "
            "If you don't know, say so honestly. Do not cite outside or non-existent sources.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer (with citations):"
        )
        return prompt

    def synthesize(self, question: str, chunks: List[Dict[str, Any]], max_tokens: int = 400) -> Dict[str, Any]:
        """
        Uses the LLM to synthesize an answer.
        Returns a dict with the answer, sources, and reasoning.
        """
        prompt = self.build_prompt(question, chunks)
        messages = [
            {"role": "system", "content": "You are a neuroscience research assistant."},
            {"role": "user", "content": prompt}
        ]
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Error: Failed to get an answer from the LLM: {e}"

        # Parse citations for both PDF ([1], [2]) and web ([W1], [W2])
        pdf_cited = re.findall(r"\[(\d+)\]", answer)
        web_cited = re.findall(r"\[W(\d+)\]", answer)

        cited_indices = set()
        for i, chunk in enumerate(chunks):
            ctype = chunk.get("citation_type", "pdf")
            cnum = str(chunk.get("citation_num", 1))
            if (ctype == "pdf" and cnum in pdf_cited) or (ctype == "web" and cnum in web_cited):
                cited_indices.add(i)

        cited_sources = [
            chunks[i]["citation"]
            for i in cited_indices
            if 0 <= i < len(chunks)
        ]

        return {
            "answer": answer,
            "sources": cited_sources,
            "reasoning": "Synthesized by LLM based on provided document and web chunks."
        }
