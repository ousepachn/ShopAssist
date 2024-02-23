import streamlit as st
from openai import OpenAI
from millify import millify
import time
import os
import utils.QueryVectorDB as qvdb

############hardcoded datainputs

profile_name='whatsmitafound'
bio=' Welcome Friend. I’m Smita from Dallas TX \n Stand out style on a budget. Click link below to shop my looks. \n 📧 Whatsmitafound@gmail.com'
a_link='https://www.instagram.com/whatsmitafound/'
social_text='Social: [{profile}]({link})'.format(profile=profile_name,link=a_link)
followers=459261
followees=1234
posts=1090
placeholder="What were latest denim finds at target?" 

# system message to 'prime' the model
primer = f"""You are fashion blogger bot. A highly intelligent system that helps answer questions from users to a famous fashion blogger. 
The three most relevant posts from the blogger is provided above the users question. Answer the users queestion using this information.
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
    print(augmented_query)
    return augmented_query



#configurations
st.set_page_config(
    page_title="ShopAssist - "+profile_name,
    page_icon="👗",
)



### begin header
st.markdown("""
  <style> .st-emotion-cache-1v0mbdj > img {border-radius: 50%;}
  </style>
    """,unsafe_allow_html=True
)
hd_row=st.container()
r1=hd_row.columns([0.33,0.67])
r1[0].image(profile_name+'/profile_pic.jpg')
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

##begin chatbot, reference: https://github.com/dataprofessor/llama2/blob/master/streamlit_app.py, https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

client=OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Store LLM generated responses
if "messages2" not in st.session_state.keys():
    st.session_state["messages2"] = [{"role": "assistant", "content": "Ask about the products I featured to get link details and discount codes"}]


# Display or clear chat messages
for message in st.session_state.messages2:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# User-provided prompt
if prompt := st.chat_input(placeholder=placeholder):
    st.session_state.messages2.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": rag_query(prompt)}
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages2.append({"role": "assistant", "content": response})



  
    