import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
import time
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI


# get API key from top-right dropdown on OpenAI website
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


model_name = 'text-embedding-ada-002'

embed = OpenAIEmbeddings(
    model=model_name,
    openai_api_key=OPENAI_API_KEY
)


# initialize connection to pinecone (get API key at app.pinecone.io)
api_key = os.getenv("PINECONE_API_KEY")

# configure client
pc = Pinecone(api_key=api_key)

spec = ServerlessSpec(
    cloud="aws", region="us-west-2"
)


### INITIALIZE AN EMBEDDING INDEX IN PINECONE ##
index_name = "shopassist-ada-002-v1"


# connect to index
index = pc.Index(index_name)
time.sleep(1)
# view index stats
index.describe_index_stats()


