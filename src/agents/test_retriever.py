from agents.retriever import PDFRetriever

# Example usage:
if __name__ == "__main__":
    retriever = PDFRetriever(papers_dir="papers")
    retriever.load_and_index_papers()
    results = retriever.retrieve("How does dopamine affect motivation?")
    for r in results:
        print(r["text"])
        print(r["citation"])