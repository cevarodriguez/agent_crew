import os
import glob
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

class PDFRetriever:
    def __init__(self, papers_dir="papers", persist_dir="chroma_db"):
        self.papers_dir = papers_dir
        self.persist_dir = persist_dir
        self.embedding = OpenAIEmbeddings()
        self.vector_db = None

    def load_and_index_papers(self):
        # Function to load all PDFs
        pdf_files = glob.glob(os.path.join(self.papers_dir, "*.pdf"))
        all_documents = []
        # Iterate through the list
        for pdf_file in pdf_files:
            loader = PyPDFLoader(pdf_file)
            docs = loader.load_and_split()
            for doc in docs:
                # Add PDF file name to metadata for citation purposes
                doc.metadata["filename"] = os.path.basename(pdf_file)
            all_documents.extend(docs)
        print(f"Loaded {len(all_documents)} document chunks from {len(pdf_files)} PDFs.")

        # Chunk the splits
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        split_documents = splitter.split_documents(all_documents)
        print(f"Split into {len(split_documents)} smaller chunks.")

        # Embed and store in vector DB
        self.vector_db = Chroma.from_documents(
            split_documents,
            self.embedding,
            persist_directory=self.persist_dir
        )
        self.vector_db.persist()
        print("Embedding and storage complete")

    def load_existing_index(self):
        # This will help avoiding re-indexing
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding
        )

    def retrieve(self, query, top_k=4):
        # We run similarity search and return the relevant chunks
        results = self.vector_db.similarity_search(query, k=top_k)
        answers = []
        for r in results:
            citation = {
                "filename": r.metadata.get("filename", "Unknown"),
                "page": r.metadata.get("page", "Unknown")
            }
            answers.append({"text": r.page_content, "citation": citation})
        return answers