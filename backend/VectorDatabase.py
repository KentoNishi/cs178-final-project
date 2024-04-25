import os
import chromadb
from chromadb.utils import embedding_functions

class VectorDatabase:
    """
    VectorDatabase is a wrapper around a ChromaDB client,
    providing a simple interface for interacting with the database.
    """

    def __init__(self, db_path=None):
        """
        Initialize a VectorDatabase instance.

        Args:
            db_path (str, optional): the path to the database. Defaults to None.
        """

        # OpenAI Embedding Function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small",
        )

        # Store ChromaDB persistent path
        self.db_path = db_path

        # Setup ChromaDB vector database
        self.client = chromadb.PersistentClient(path=db_path)


    def get(self, source: str, ids: list[str]):
        # Get ChromaDB collection
        collection = self.client.get_collection(
            source, embedding_function=self.embedding_function
        )
        return collection.get(ids=ids, include=["documents", "metadatas"])


    def query(self, source: str, query: str, n_results=2, filters={}) -> list[dict]:
        """
        Query a collection/namespace in the vector database.

        Args:
            source (str): the name of the collection/namespace to query.
            query (str): the query to use.
            n_results (int, optional): the number of results to return. Defaults to 2.
            filters (dict, optional): a dictionary of filters to apply. Defaults to an empty dictionary.

        Returns:
            dict: a dictionary containing the results of the query.
        """

        # Get ChromaDB collection
        collection = self.client.get_collection(
            source, embedding_function=self.embedding_function
        )

        # Perform query
        results = collection.query(
            query_texts=query,
            where=filters,
            n_results=n_results,
        )

        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append(
                {
                    "id": results["ids"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": results["distances"][0][i],
                }
            )

            # Should add metadata here

        return formatted_results