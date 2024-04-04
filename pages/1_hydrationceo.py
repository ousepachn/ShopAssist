import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from openai import OpenAI
from millify import millify
import pandas as pd
import time
import os
import utils.QueryVectorDB as qvdb


df=pd.read_pickle('all-profiles03052024.pkl')
############hardcoded datainputs

profile_name='hydrationceo'
name=df[df['creatorid'] == profile_name]['name'].values[0]
bio = df[df['creatorid'] == profile_name]['bio'].values[0]
a_link=f'https://www.instagram.com/{profile_name}/'
social_text='Social: [{profile}]({link})'.format(profile=profile_name,link=a_link)
followers=df[df['creatorid'] == profile_name]['followers'].values[0]
followees=df[df['creatorid'] == profile_name]['followees'].values[0]
posts = df[df['creatorid'] == profile_name]['posts'].values[0]
profile_pic = df[df['creatorid'] == profile_name]['profile_pic'].values[0]
refreshed_Date = df[df['creatorid'] == profile_name]['date_refreshed'].values[0]
refreshed_Date = str(refreshed_Date)[:10]
placeholder="What were the under $15 lipsticks reviewed in the last 2 weeks?" 
##########################

# system message to 'prime' the model
primer = f"""You are beauty reviewer bot.  A highly intelligent system that helps answer questions from users. 
All available information is provided above the users question. Answer the users question using this information.
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


#css styles
style_image1 = """
max-width: 100%;
border-radius: 50%;
"""

tags="""
    .htag {
    color: #3E6D8E;
    background-color: #E0EAF1;
    padding: 3px 4px 3px 4px;
    margin: 2px 2px 2px 0;
    text-decoration: none;
    font-size: 60%;
    line-height: 2.4;
    white-space: nowrap;
    border-radius: 5%;
}

.htag:hover {
    background-color: #3E6D8E !important;
    color: #E0EAF1;
    text-decoration: none;
    border-radius: 5%;
}
"""

profilepicurl=str(f'.\\app\static\{profile_name}_profile_pic.jpg').replace('\\','/')
hd_row=st.container()

r1=hd_row.columns([0.33,0.67])

r1[0].markdown(f'<img src="{profilepicurl}" style="{style_image1}">',
    unsafe_allow_html=True,
)
with r1[1]:
    if st.button("🏠Return Home"):
        st.switch_page(f"ShopAssist.py")
    st.subheader(profile_name)
    st.markdown(social_text,unsafe_allow_html=True)
    st.markdown(name)
    st.markdown('Bio: {Bio}'.format(Bio=bio))
    st.markdown('Last Refreshed: {date}'.format(date=refreshed_Date))
    
r2=st.container()
with r2:
    with stylable_container(
        key='metrics',
        css_styles="""
        [data-testid="column"] {
        width: calc(33% - 1rem) !important;
        flex: 1 1 calc(33% - 1rem) !important;
        min-width: calc(33% - 1rem) !important;
        }
        """,
    ):
        r2a=st.columns(3)
        r2a[0].metric(label='Posts',value=millify(posts))
        r2a[1].metric(label='Followers',value=millify(followers))
        r2a[2].metric(label='Following',value=millify(followees))
st.divider()

#### end header

st.info("""The demo is limited to the last 50 posts (no stories, highlights).\nHere are a few sample queries 
        [Best Drugstore lipsticks?,   What is the best moisturizer?,  shampoo recommendations for dry scalp?]""")  

client=OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask about the products I featured to get link details and discount codes"}]
avatar = {
    "assistant": "💄",
    "user": "🐱"
}

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"],avatar=avatar[message["role"]]):
        st.write(message["content"])


# User-provided prompt
if prompt := st.chat_input(placeholder=placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user",avatar=avatar["user"]):
        st.write(prompt)
    

    # Display assistant response in chat message container
    with st.chat_message("assistant",avatar=avatar["assistant"]):
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
        if response!="I don't know.":
            hd_row=st.container()
            for post in posts:
                r1=hd_row.columns([0.15,0.85])
                r1[0].image(str(post['metadata']['thumbnail_url']).replace('\\','/'))
                hashtags_string = ' '.join([f"<a class='htag' href='https://www.instagram.com/p/{post['id']}'>{tag}</a>" for tag in post['metadata']['caption_hashtags']])
                with r1[1]:
                    with stylable_container(
                    key='metrics',
                    css_styles=tags,
                    ):
                        st.markdown("**post link:** www.instagram.com/p/"+post['id'],unsafe_allow_html=True)
                        st.markdown('**Post Date:** '+ post['metadata']['date_utc'])
                        st.markdown('**Tags:** '+hashtags_string, unsafe_allow_html=True)
                        st.markdown('**Relevance Score:** '+ str(post['score'])[:4])
    st.session_state.messages.append({"role": "assistant", "content": response})



# ls=df['caption_hashtags'][0]


# str()
