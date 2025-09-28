from typing import Optional, Any, Dict

import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

from fivcadvisor.utils import OutputDir


class EmbeddingDB(object):
    def __init__(
        self,
        function: Optional[EmbeddingFunction] = None,
        output_dir: Optional[OutputDir] = None,
        **kwargs,
    ):
        assert function is not None
        self.function = function
        self.output_dir = output_dir or OutputDir()
        self.db = chromadb.PersistentClient(path=str(self.output_dir))

    def get_collection(self, name: str) -> "EmbeddingCollection":
        return EmbeddingCollection(
            self.db.get_or_create_collection(
                name,
                embedding_function=self.function,
            )
        )


class EmbeddingCollection(object):
    def __init__(self, collection: chromadb.Collection):
        self.collection = collection
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add text to the collection."""
        chunks = self.text_splitter.split_text(text)
        self.collection.add(
            documents=chunks,
            metadatas=([metadata] * len(chunks)) if metadata else None,
            ids=[str(hash(chunk)) for chunk in chunks],
        )

    def search(self, query: str, num_documents: int = 10) -> list:
        """Search the collection."""
        return self.collection.query(query_texts=[query], n_results=num_documents)[
            "documents"
        ][0]

    def delete(self):
        """Delete the collection."""
        self.collection.delete()
