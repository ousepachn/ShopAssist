import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
import time
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm

#todo, check using the full transcript instead of the current transcript

# get API key from top-right dropdown on OpenAI website
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

data=pd.read_pickle('picklefiles//all-postss6.pkl')

data=pd.concat([data,df])

data.to_pickle(f'picklefiles/all-posts')
profiles=pd.read_pickle('picklefiles//all-profiles.pkl')
df_profiles=pd.concat([profiles,df_profiles])
df_profiles.to_pickle(f'picklefiles//all-profiles.pkl')
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
index_name = "shopassist-ada-002-v3" #"shopassist-ada-002-v1"
existing_indexes = [
    index_info["name"] for index_info in pc.list_indexes()
]

# check if index already exists (it shouldn't if this is first time)
if index_name not in existing_indexes:
    # if does not exist, create index
    pc.create_index(
        index_name,
        dimension=1536,  # dimensionality of ada 002
        metric='cosine',
        spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

# connect to index
index = pc.Index(index_name)
time.sleep(1)
# view index stats
index.describe_index_stats()
### END INITIALIZE AN EMBEDDING INDEX IN PINECONE ##


### LOAD DATA INTO THE PINECONE INDEX ##
data.drop_duplicates(subset=['post_id'],inplace=True)
data=data[data["transcript"].notna()]

batch_size = 100

texts = []
metadatas = []

for i in tqdm(range(0, len(data), batch_size)):
    # get end of batch
    i_end = min(len(data), i+batch_size)
    batch = data.iloc[i:i_end]
    # first get metadata fields for this record
    metadatas = [{
        'creatorid': record['creatorid'],
        'post_id': record['post_id'],
        'thumbnail_url': record['thumbnail_url'],
        'date_utc': record['date_utc'].date(),
        'caption_hashtags': record['caption_hashtags'],
        'text': record['transcript']
    } for j, record in batch.iterrows()]
    # get the list of contexts / documents
    documents = batch['transcript']
    # create document embeddings
    embeds = embed.embed_documents(documents)
    # get IDs
    ids = batch['post_id']
    # add everything to pinecone
    index.upsert(vectors=zip(ids, embeds, metadatas))
index.describe_index_stats()

### END LOAD DATA INTO THE PINECONE INDEX ##


