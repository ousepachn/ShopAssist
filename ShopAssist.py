import streamlit as st
import numpy as np
from millify import millify
import time

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

#configurations
st.set_page_config(
    page_title="ShopAssisst",
    page_icon="👋",
)

st.sidebar.success("Select a profile to talk to the AI ShopAssistant.")


st.markdown(
    """

    ShopAssisst: 
    An AI assisted search tool for identifying products reviewed by your favorite influencers on 
    Instagram.
    
    **👈 Select a demo from the sidebar** to see some examples

    Users of instagram have great difficulty searching for products featured in posts or stories shared by 
    their favorite influencers. Instagram and other social media applications have limited search 
    functionality. Ex: if you were trying to search for the name of the moisturizer your favorite influencer 
    shared a story about last week, you will not be able to find.  Google does not Index social media sites like instagram
    (walled gardens) and Instagram Search is really bad (https://www.reddit.com/r/Instagram/comments/vjq7bc/instagram_search_sucks_any_ways_to_get_around_its/). 
    Moreover social media companies  restrict indexing and do not permit external product links in their apps to ensure 
    that users stay on the platform, but this also restricts the user experience. 
    
    ShopAssist uses OpenAIs Video, Whisper and GPT4 models to transcribe multimodel posts data into text. We then vectorize and embed 
    the data in pinecone for easy search retrieval.  Resulsts are then passed through Truelens for search result evaluation.   
    
    This demo only limits to posts data, and has many bugs since it was put together in less thana week by non developers. Teh tech offers promise
    and provides influencers an easy way to increase their affiliate sales revenue and reduce the amount of time spent on Content operations. 

"""
)