import streamlit as st
from openai import OpenAI
from millify import millify
import time
import os
import utils.QueryVectorDB as qvdb

############hardcoded datainputs

profile_name='hydrationceo'
bio='📍NYC\n 💖 your unfiltered skincare & beauty bestie \n Business only: rachel@hydrationceo.com\n Product Faves 👇'
a_link='https://www.instagram.com/hydrationceo/'
social_text='Social: [{profile}]({link})'.format(profile=profile_name,link=a_link)
followers=1234567
followees=1234
posts=12345
placeholder="What were the under $15 lipsticks reviewed in the last 2 weeks?" 
##########################

# system message to 'prime' the model
primer = f"""You are beauty reviewer bot.  A highly intelligent system that helps answer questions from users to a famous beauty blogger. 
The three most relevant posts from the blogger is provided above the users question. Answer the users question using this information.
If the answer can not be found in the information provided, truthfully say "I don't know".  Be objective and succint in your response. answer in first person.  
Do not use the phrase "blogger", "bot", "based on the information" in your response.  Response should not be more than 2 sentences
"""
##########################


def rag_query(query):
    Vector=qvdb.embed.embed_query(query)

    results=qvdb.index.query(
        vector=Vector,
        filter={
            "creatorid": {"$eq": profile_name}
        },
        top_k=3,
        include_metadata=True
    )

    contexts = [result["metadata"]["text"] for result in results['matches']]
    augmented_query = "\n\n---\n\n".join(contexts)+"\n\n---\n\n"+ query    
    posts=results['matches']
    return augmented_query,posts


#configurations
st.set_page_config(
    page_title="ShopAssist - "+profile_name,
    page_icon="💆‍♂️",
)






### begin header
st.markdown("""
  <style> .st-emotion-cache-1v0mbdj > img {border-radius: 50%;}
  </style>
    """,unsafe_allow_html=True
)
hd_row=st.container()
r1=hd_row.columns([0.33,0.67])
r1[0].image('hydrationceo/profile_pic.jpg')
with r1[1]:
    st.subheader(profile_name)
    st.markdown(social_text,unsafe_allow_html=True)
    st.markdown('Bio: {Bio}'.format(Bio=bio))
    r1a=st.columns(3)
    r1a[0].metric(label='Posts',value=millify(posts))
    r1a[1].metric(label='Followers',value=millify(followers))
    
    r1a[2].metric(label='Following',value=millify(followees))
    st.divider()

#### end header

client=OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask about the products I featured to get link details and discount codes"}]


# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# User-provided prompt
if prompt := st.chat_input(placeholder=placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        augmented_query,posts=rag_query(prompt)
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": augmented_query}
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        hd_row=st.container()
        for post in posts:
            r1=hd_row.columns([0.15,0.85])
            r1[0].image(post['metadata']['thumbnail_url'])
            with r1[1]:
                st.markdown("**post link:** www.instagram.com/p/"+post['id'],unsafe_allow_html=True)
                st.markdown('**Date:** '+ post['metadata']['date_utc'])
                st.markdown('**Tags:** '+str(post['metadata']['caption_hashtags']))
                st.markdown('**Relevance Score:** '+ str(post['score'])[:4])
    st.session_state.messages.append({"role": "assistant", "content": response})