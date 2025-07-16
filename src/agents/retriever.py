import os
import glob
from typing import List, Dict, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_community.embeddings import HuggingFaceEmbeddings
#from langchain_openai import OpenAIEmbeddings
#from langchain_community.vectorstores import Chroma
#from langchain_community.embeddings import OpenAIEmbeddings

class PDFRetriever:
    """
    Loads, chunks, embeds, and retrieves relevant text passages from a collection of files.
    """

    def __init__(self, papers_dir: str = "papers", persist_dir: str = "chroma_db"):
        """
        Initialize the retriever.
        """
        self.papers_dir = papers_dir
        self.persist_dir = persist_dir
        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        #self.embedding = OpenAIEmbeddings()
        self.vector_db = None

    def load_and_index_papers(self) -> None:
        """
        Loads all PDFs from the papers_dir, chunks the text, embeds, and persists in a vector DB.
        """
        pdf_files = glob.glob(os.path.join(self.papers_dir, "*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in directory: {self.papers_dir}")

        all_documents = []
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(pdf_file)
                docs = loader.load_and_split()
                for doc in docs:
                    doc.metadata["filename"] = os.path.basename(pdf_file)
                    # Ensure 'page' metadata is present (may be named 'page', 'page_number', etc)
                    # LangChain's PyPDFLoader usually adds 'page', but just in case we double-check:
                    page = doc.metadata.get("page", None)
                    if page is None:
                        # If the loader splits by page, you might know the current page by order
                        # For robustness, it might be needed to set it to '?' if not available
                        doc.metadata["page"] = "?"
                all_documents.extend(docs)
            except Exception as e:
                print(f"Error loading {pdf_file}: {e}")
        print(f"Loaded {len(all_documents)} document chunks from {len(pdf_files)} PDFs.")

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        split_documents = splitter.split_documents(all_documents)
        print(f"Split into {len(split_documents)} smaller chunks.")

        try:
            self.vector_db = Chroma.from_documents(
                split_documents,
                self.embedding,
                persist_directory=self.persist_dir
            )
            #self.vector_db.persist()
            print("Embedding and storage complete.")
        except Exception as e:
            print("Failed to embed and store documents:", e)
            raise

    def load_existing_index(self) -> None:
        """
        Loads an existing persisted vector database.
        """
        if not os.path.exists(self.persist_dir):
            raise FileNotFoundError("Persisted vector DB not found. Run load_and_index_papers() first.")
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding
        )
        # Dummy test
        try:
            _ = self.vector_db._collection.count()
        except Exception as e:
            raise RuntimeError(f"Failed to load Chroma index: {e}")

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Dict[str, str]]]:
        """
        Runs similarity search and returns relevant chunks with citation metadata.
        """
        if not self.vector_db:
            raise RuntimeError("Vector DB not loaded. Call load_and_index_papers() or load_existing_index() first.")

        results = self.vector_db.similarity_search(query, k=top_k)
        answers = []
        for r in results:
            citation = {
                "filename": r.metadata.get("filename", "Unknown"),
                "page": str(r.metadata.get("page", "?"))
            }
            answers.append({"text": r.page_content, "citation": citation})
        return answers

