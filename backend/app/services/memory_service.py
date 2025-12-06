import os
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any
import uuid

# Mock Milvus Client for environments where milvus-lite fails
class MockMilvusClient:
    def __init__(self, uri):
        print(f"MockMilvusClient initialized with {uri}")
        self.data = []

    def has_collection(self, collection_name):
        return True

    def create_collection(self, collection_name, dimension, auto_id, id_type, consistency_level):
        pass

    def insert(self, collection_name, data):
        self.data.append(data)
        print(f"MockMilvusClient: Inserted data {data}")

    def search(self, collection_name, data, filter, limit, output_fields):
        # Very basic mock search - return everything matching session_id in filter
        # filter string example: 'session_id == "123"'
        session_id = filter.split('==')[1].strip().strip('"')
        results = []
        for item in self.data:
            if item.get("session_id") == session_id:
                # Wrap in search result structure
                results.append({"entity": item, "distance": 0.0})
        # Return list of list of hits
        return [results]

class MemoryService:
    def __init__(self):
        # Use milvus-lite for local file-based storage or connect to a server
        self.uri = "./milvus_demo.db"

        try:
            from pymilvus import MilvusClient
            self.client = MilvusClient(self.uri)
        except Exception as e:
            print(f"Warning: MilvusClient initialization failed ({e}). Using MockMilvusClient.")
            self.client = MockMilvusClient(self.uri)

        self.collection_name = "chat_history"

        try:
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        except Exception:
            self.embeddings = None
            print("Warning: OpenAIEmbeddings not initialized (missing API Key)")

        self._init_collection()

    def _init_collection(self):
        if self.client.has_collection(self.collection_name):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=1536, # Dimension for text-embedding-3-small
            auto_id=True,
            id_type="int",
            consistency_level="Strong"
        )

    def add_memory(self, session_id: str, role: str, content: str):
        if not self.embeddings or os.getenv("OPENAI_API_KEY") == "sk-dummy-key":
            # For mock mode, insert dummy vector
            vector = [0.1] * 1536
        else:
            vector = self.embeddings.embed_query(content)

        data = {
            "vector": vector,
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp":  None # Add timestamp if needed
        }
        self.client.insert(collection_name=self.collection_name, data=data)

    def search_memory(self, session_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.embeddings or os.getenv("OPENAI_API_KEY") == "sk-dummy-key":
             # Use dummy vector for search
             vector = [0.1] * 1536
        else:
            vector = self.embeddings.embed_query(query)

        # Search with filter for session_id
        res = self.client.search(
            collection_name=self.collection_name,
            data=[vector],
            filter=f'session_id == "{session_id}"',
            limit=limit,
            output_fields=["content", "role"]
        )

        memories = []
        for hits in res:
            for hit in hits:
                memories.append(hit["entity"])
        return memories

memory_service = MemoryService()
