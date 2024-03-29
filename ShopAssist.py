import streamlit as st
import numpy as np
from millify import millify


#configurations
st.set_page_config(
    page_title="ShopAssisst",
    page_icon="🛒",
)

st.sidebar.success("ShopAssist: Select an influencer to talk to their AI Assistant.")


st.markdown(
    """

    ## ShopAssist: 
    ### Your favourite influencer's AI assitant. Use ShopAssist to talk to influencers and search through content, product reviews, recommendations and more.
    
    **👈 Select an influencer profile from the sidebar to see some examples**

    Social media users have great difficulty searching for products featured in posts or stories shared by 
    by influencers. Instagram and other social applications have limited search 
    functionality. 
    
    We've all been there, We liked the lipgloss (or smartwatch) an influencer reviewed last week, 
    we're at the store now, and we're scanning through countless posts before finally giving up in frustration!!

    Why is it so hard to search through influencer posts? Well, Google does not Index social media sites ( Instagram
    is a walled gardens) and Social platform content search is really bad [(link)](https://www.reddit.com/r/Instagram/comments/vjq7bc/instagram_search_sucks_any_ways_to_get_around_its/). 
    
    Social media companies have no incentive to improve search on their platforms, more time users spend on the platform = more ad revenues.
    
    We thought we could do better.  ShopAssist lets you talk to your influencer and search through their posts. Try it out now!
    
"""
)

st.text_area("","ShopAssist uses OpenAIs Video, Whisper and GPT4 models to transcribe multimodel posts data into text. We then vectorize and embed\
 the data in pinecone for easy search retrieval.  \nResults are then passed through Truelens for search result evaluation.\n")  


st.markdown(
    """

    


    This is limited demo, restricted to only posts data from the last 50 posts.  It was put together by non developers in less than a week as a POC for something bigger.
    Email me at [(jcvdevacc@gmail.com)] for more details on the project or if you want to collaborate.  We're working to improve the social 
    commerce experience for consumers, while providing influencers incremental sales revenue.
     

    

    


"""
)
