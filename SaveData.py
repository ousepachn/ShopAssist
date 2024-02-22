import pinecone_datasets
import os
from pinecone import Pinecone
from pinecone import ServerlessSpec, PodSpec


api_key = "aaa996e2-d5f1-4566-90b4-11dc43bed41e"

class SaveData:
    def __init__(self):
        self.index_name = "instagram-project"
        self.pinecone = Pinecone(api_key=api_key)

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
