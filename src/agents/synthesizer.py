import re
from typing import List, Dict, Any
import openai

class Synthesizer:
    def __init__(self, model="gpt-3.5-turbo", temperature=0.1):
        self.model = model
        self.temperature = temperature

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Formats context for the LLM. Includes text and its citation.
        """
        context_strs = []
        for i, chunk in enumerate(chunks):
            text = chunk["text"].replace("\n", " ")
            citation = chunk["citation"]
            citation_str = f"[{i+1}] {citation['filename']}, page {citation.get('page', '?')}"
            context_strs.append(f"{citation_str}: {text}")
        return "\n\n".join(context_strs)
    
    def build_prompt(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Builds a prompt for the LLM including context and explicit instructions
        """
        context = self.format_context(chunks)
        prompt = (
            "You are an expert neuroscience research assistant. "
            "Given the following extracts from research papers and web sources, answer the user's question. "
            "Cite your sources by their number in square brackets (e.g., [1]). "
            "If you don't know, say so honestly. Do not cite outside or non-existent sources."
            f"Context: \n{context}\n\n"
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
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens
        )
        answer = response.choices[0].message.content.strip()

        # Simple way to parse which sources (numbers) were cited in the answer
        cited = re.findall(r"\[(\d+)\]", answer)
        cited_indices = set(int(i) - 1 for i in cited if i.isdigit())
        cited_sources = [
            chunks[i]["citation"]
            for i in cited_indices
            if 0 <= i < len(chunks)
        ]

        # You can also include the actual context chunks used for transparency
        return {
            "answer": answer,
            "sources": cited_sources,
            "reasoning": "Synthesized by LLM based on retrieved document chunks."
        }