import streamlit as st
import numpy as np




#configurations
st.set_page_config(
    page_title="ShopAssisst",
    page_icon="🛒",
)


st.sidebar.success("ShopAssist: Select an influencer to talk to their AI Assistant.")


st.markdown(
    """

    ## 🛒 ShopAssist: Your influencer's AI assitant. 
    **Use ShopAssist to search through influencer content, product reviews, recommendations and more.**
    
    Its not easy search and find products featured in posts or stories shared 
    by influencers. Instagram (and social media) has limited search functions. 
    capabilities. 
    We thought we could build a better experience.  ShopAssist lets you talk to your influencer and search through their posts. Try it out now!
    
     **Select an influencer profile below to begin** 
     :point_down:
    
    """
)
style_image1 = """
max-width: 100%;
border-radius: 50%;
"""

influencers=["hydrationceo","whatsmitafound","charminglystyled",
             "kirtitewani","hemali.mistry","thescenenewyork",
             "payalforstyle","mkbhd","reeti_shop"]

N=6
row=st.container()
with row:
    r1=st.columns(3)
    for count,col in enumerate(r1):
        with col:
            with st.container():
                img,btn=st.columns([0.2,0.8])
                with img:
                    st.markdown(str(f"<img src='.\\app\static\{influencers[count]}_profile_pic_sml.jpg' style='{style_image1}'>").replace('\\','/'),
                    unsafe_allow_html=True,)
                with btn:
                    if st.button(influencers[count], key=count):
                        st.switch_page(f"pages/{influencers[count]}.py")
row=st.container()
with row:
    r2=st.columns(3)
    for count,col in enumerate(r2):
        with col:
            with st.container():
                img,btn=st.columns([0.2,0.8])
                with img:
                    st.markdown(str(f"<img src='.\\app\static\{influencers[count+3]}_profile_pic_sml.jpg' style='{style_image1}'>").replace('\\','/'),
                    unsafe_allow_html=True,)
                with btn:
                    if st.button(influencers[count+3], key=count+3):
                        st.switch_page(f"pages/{influencers[count+3]}.py")
#css styles

st.markdown(
    """<style> [data-testid="stExpander"] details {
    border-style: none;
    } </style>""",
    unsafe_allow_html=True
)


st.markdown("""
            **:red[Want to] :orange[see] :green[influencers] :orange[you follow] :red[on] :violet[shopassist?] [(click here)](https://forms.gle/S88EPYd5p2keKj9w9)**
            """)


st.divider()
with st.expander("**Why ShopAssist?**"):
    st.markdown(
       """

    We've all been there, We liked the lipgloss (or smartwatch) an influencer reviewed last week, 
    we're at the store now, and we're scanning through countless posts before finally giving up in frustration!!

    Why is it so hard to search through influencer posts? Well, Google does not Index social media sites ( Instagram
    is a walled gardens) and Social platform content search is really bad [(link)](https://www.reddit.com/r/Instagram/comments/vjq7bc/instagram_search_sucks_any_ways_to_get_around_its/). 
    
    Social media companies have no incentive to improve search on their platforms, more time users spend on the platform = more ad revenues.
        
    """
    )
with st.expander("**What is the tech behind ShopAssist?**"):
     st.markdown(
       """ShopAssist uses OpenAI's Video, Whisper and GPT4 models to transcribe multimodel posts (audio,video,images and text data) into searchable indexes. We then vectorize and embed\
 the data in pinecone for RAG based querying and retrieval.
    """)  


st.markdown(
    """
    <span style='font-size: 0.875em;'>This is a limited demo, restricted to only posts data from the last 50 posts. It was hacked together as a POC for something bigger.
    Email me at [jcvdevacc@gmail.com](mailto:jcvdevacc@gmail.com) for more details on the project or if you want to collaborate. We're working to improve the social 
    commerce experience for creators, brands, and consumers! PS: Thanks for reading. You're awesome! Feel free to reach out.
    </span>
    
    """,  unsafe_allow_html=True  

)