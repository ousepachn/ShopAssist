###This document outlines the testig scripts that were used check if the rAG output is coherent.  We used TruLens and the suggested RAG triad framework to finalize the final prompt
## things to note: 1. The hydrationceo bot has decent performance, with minimal customizations and parameter edits
##                 2. The whatsmitafound bot does not perform as well. Low groundedness and context scores.  This is due to the fact that most of her videos have 'songs with lyrics' 
##                      in the background. Also she does not do voiceovers in her videos is transcribing on '''
## Todo: To improve the RAG performance for the whatsmitafoudn bot.  Upgrade the gpt4 vision based workflow where we are going from video -> frmes -> images -> text.  
##      This will heolp us trascribe videos which do not have voice overs, and also videos where there is music with lyrics playing the background.  
## Guess TruLens helped us get to this conclusion.
## The gitrepo also contains a pdf outlining the findings of the TruLens evaluation.  The pdf is named TruLensEval.pdf


import numpy as np
from langchain_openai import OpenAIEmbeddings
import os
import time
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from trulens_eval import Tru
from trulens_eval.tru_custom_app import instrument
from trulens_eval import Feedback, Select, TruCustomApp
from trulens_eval.feedback import Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as fOpenAI



# setting up OpenAI and Pinecone
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


### BEGIN TRULENS TESTING SETUP ####

profile_name='hydrationceo'
primer_beauty = f"""You are beauty reviewer bot.  A highly intelligent system that helps answer questions from users. 
All available information is provided above the users question. Answer the users question using this information.
If the answer can not be found in the information provided, truthfully say "I don't know".  Be objective and succint in your response. answer in first person.  
Do not use the phrase "blogger", "bot", "based on the information" in your response.  Response should not be more than 2 sentences
"""
primer_fashion = f"""You are fashion reviewer bot. A highly intelligent system that helps answer questions from users to about fashion. 
All available information is provided above the users question. Answer the users question using this information.
If the answer can not be found in the information provided, truthfully say "I don't know".  Be objective and succint in your response. answer in first person.  
Do not use the phrase "blogger", "bot", "based on the information" in your response.  Response should not be more than 2 sentences
"""
client=OpenAI()
tru = Tru()
class RAG_from_scratch:
    @instrument
    def retrieve(self, query: str, profile_name: str) -> list:
        """
        Retrieve relevant text from vector store.
        """
        results=index.query(
        vector=embed.embed_query(query),
        filter={
            "creatorid": {"$eq": profile_name}
        },
        top_k=3,
        include_metadata=True
    )
        return [result["metadata"]["text"] for result in results['matches']]

    @instrument
    def generate_completion(self, query: str, context_str: str, primer: str) -> str:
        """
        Generate answer from context.
        """
        augmented_query = "\n\n---\n\n".join(context_str)+"\n\n---\n\n"+ query
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": augmented_query}
            ]
        ).choices[0].message.content
        return completion

    @instrument
    def query(self, query: str, profile_name: str, primer: str) -> str:
        context_str = self.retrieve(query,profile_name)
        completion = self.generate_completion(query, context_str, primer)
        return completion

rag = RAG_from_scratch()



    



# Initialize provider class
fopenai = fOpenAI()

grounded = Groundedness(groundedness_provider=fopenai)

# Define a groundedness feedback function
f_groundedness = (
    Feedback(grounded.groundedness_measure_with_cot_reasons, name = "Groundedness")
    .on(Select.RecordCalls.retrieve.rets.collect())
    .on_output()
    .aggregate(grounded.grounded_statements_aggregator)
)

# Question/answer relevance between overall question and answer.
f_qa_relevance = (
    Feedback(fopenai.relevance_with_cot_reasons, name = "Answer Relevance")
    .on(Select.RecordCalls.retrieve.args.query[0])
    .on_output()
)

# Question/statement relevance between question and each context chunk.
f_context_relevance = (
    Feedback(fopenai.qs_relevance_with_cot_reasons, name = "Context Relevance")
    .on(Select.RecordCalls.retrieve.args.query)
    .on(Select.RecordCalls.retrieve.rets.collect())
    .aggregate(np.mean)
)    


tru_beauty_rag = TruCustomApp(rag,
    app_id = 'ShopAssist hydrationceo',
    feedbacks = [f_groundedness, f_qa_relevance, f_context_relevance])

with tru_beauty_rag as recording:
    for q in ['what is the best sunscreen?','what is the best moisturizer?',
              'what is the best shampoo for dry scalp?', 'fixes for breakouts?',
              'best lip gloss?','best drugstore foundation?',
              'best drugstore mascara?','best drugstore eyeshadow?',
              'best drugstore eyeliner?','best drugstore blush?',
              'best drugstore acne treatment?','best drugstore anti-aging treatment?',
              'best nail polish removers?']:
        rag.query(q,profile_name='hydrationceo', primer=primer_beauty)

    
tru_fashion_rag = TruCustomApp(rag,
    app_id = 'ShopAssist whatsmitafound',
    feedbacks = [f_groundedness, f_qa_relevance, f_context_relevance])

with tru_fashion_rag as recording:
    for q in ['are denims still in?', 'best outfit recommendations from amazon',
              'what pairs well with a black skirt?','best drugstore lipsticks?',
              'how to style a white shirt?','how to style a black dress?',
              'most comfortable heels?','best summer sandals?']:
        rag.query(q,profile_name='whatsmitafound', primer=primer_fashion)
    
tru.get_leaderboard(app_ids=['ShopAssist hydrationceo','ShopAssist whatsmitafound'])

tru.run_dashboard(port=8502)