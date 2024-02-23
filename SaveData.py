import os
import time
from pinecone import Pinecone
from pinecone import ServerlessSpec, PodSpec
from EmbedChunks import EmbedChunks


class SaveData:
    def __init__(self):
        self.index_name = "instagram-project"
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_KEY"))

        self.__initiailize_database()

    def __initiailize_database(self):
        self.cloud = os.environ.get('PINECONE_CLOUD') or 'PINECONE_CLOUD'
        self.spec = ServerlessSpec(cloud='aws', region='us-west-2')

        # If index doesn't exist create one.
        if self.index_name not in self.pinecone.list_indexes().names():
            self.pinecone.create_index(
                self.index_name,
                dimension=1536,  # dimensionality of text-embedding-ada-002
                metric='cosine',
                spec=self.spec
            )

        # connecting to created index
        self.index = self.pinecone.Index(self.index_name)

    def insert_data(self, batch):
        self.index.upsert(batch)

    def retrieve_k_context(self, k, query, filters):
        contexts = []
        embedded_query = self.embed_query(query)[0]

        res = self.index.query(
            vector=embedded_query,
            top_k=k,
            include_metadata=True,
            filter=filters,
        )

        for i in res['matches']:
            context = i['metadata']['text'] + \
                f"\nURL for the product: {i['metadata']['thumbnail_url']}"
            contexts.append(context)

        return contexts

    def embed_query(self, query):
        return EmbedChunks("text-embedding-ada-002").embedding_model.embed_documents([query])
