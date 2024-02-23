import streamlit as st
import numpy as np
from millify import millify
import time

############hardcoded datainputs

profile_name='whatsmitafound'
bio=' Welcome Friend. I’m Smita from Dallas TX \n Stand out style on a budget. Click link below to shop my looks. \n 📧 Whatsmitafound@gmail.com'
a_link='https://www.instagram.com/whatsmitafound/'
social_text='Social: [{profile}]({link})'.format(profile=profile_name,link=a_link)
followers=459261
followees=1234
posts=1090
placeholder="What were the under $15 lipsticks reviewed in the last 2 weeks?" 
##########################

#configurations
st.set_page_config(
    page_title="ShopAssist - whatsmitafound",
    page_icon="👋",
)



### begin header
st.markdown("""
  <style> .st-emotion-cache-1v0mbdj > img {border-radius: 50%;}
  </style>
    """,unsafe_allow_html=True
)
hd_row=st.container()
r1=hd_row.columns([0.33,0.67])
r1[0].image('{profile_name}/profile_pic.jpg')
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

##begin chatbot, reference: https://github.com/dataprofessor/llama2/blob/master/streamlit_app.py
cont=st.container(border=True)
r1=cont.columns(5)
i=0
for val in r1:
  cont2=val.container(height=120)
  cont2.button("click me",i,use_container_width=True)
  i=i+1

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Ask about the products I featured to get link details and discount codes"}]


# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])



# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot   <-- THIS SECTION WILL NEED TO BE CHANGED FOR OPENAI
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
#    UNCOMMENT BELOW 4 LINES
    # output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
    #                        input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
    #                               "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    # return output
            

# User-provided prompt
if prompt := st.chat_input(placeholder=placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)