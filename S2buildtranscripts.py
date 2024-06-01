import os
import pandas as pd
import moviepy.editor as mp
from openai import OpenAI
from langdetect import detect
import utils.openAiRateLimit as oirt
import re
# Define the paths
audio_outfolder = "audio_output/"
transcript_outfolder = "transcript_output/"

# Set present working directory
os.chdir('c:\\Users\\ousep\\OneDrive\\Documents\\phase2\\LabLab Hackathon\\ShopAssist\\ShopAssist\\')


#TODO, ADD A COUNTER TO INDICATE HOW MANY POSTS REMAIN

# Function to convert video to audio
def convert_video_to_audio(video_path, audio_outfolder,creatorid):
    video_name = os.path.basename(video_path)
    audio_name = os.path.splitext(video_name)[0] + ".mp3"
    audio_path = os.path.join(audio_outfolder,creatorid, audio_name)
    #Create folder for creator, videos if none exists
    if not os.path.exists(os.path.join(audio_outfolder,creatorid)):
        os.makedirs(os.path.join(audio_outfolder,creatorid))
    clip=mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path

# Function to convert audio to transcript
def convert_audio_to_transcript(audio_path):
    audio_file= open(audio_path, "rb")
    transcript = oirt.audiocompletions_with_backoff(
    model="whisper-1",
    file=audio_file,
    prompt=Prompt
    )
    return transcript

# Append together pickle files and create a dataframe
data = pd.read_pickle('picklefiles\\all-posts.pkl')

# Convert video to audio.  Iterate through the dataframe and process each URL, 
for url in data["url"]:
    # 
    if url.endswith(".mp4"):
        creatorid = data.loc[data["url"] == url,'creatorid'].values[0]
        audio_path = convert_video_to_audio(url, audio_outfolder,creatorid)
        data.loc[data["url"] == url, "audio_url"] = audio_path
    
 
#TODO, ADD AN INDICATOR TO SHOW THAT TRANSCRIPTI0N STARTED

client = OpenAI()
Model="whisper-1"
Prompt='Please add punctuation. Do not miss any words.  Even if the word is soft, please transcribe it.'
for url in data["audio_url"]:
    if str(url)!='nan':
    # Convert audio to transcripts.  Iterate through the dataframe and process each audio URL
        transcript=convert_audio_to_transcript(url)
        print(url)
       # Save the transcript in the dataframe
        data.loc[data["audio_url"] == url, "audio_transcript"] = transcript.text# Save the dataframe as a pickle file

# build only english version of the transcripts from audio
#TODO - NEED TO SEE HOW TO REMOVE AUDIO LYRICS FRMO AUDIO
for t in data["audio_transcript"]:
    if str(t)!='nan' and len(t)>1 and bool(re.match('^(?=.*[a-zA-Z])', t)):
        if detect(t) == 'en':
            data.loc[data["audio_transcript"] == t, "en_audio_transcript"]=t

data.drop_duplicates(subset=['post_id'],inplace=True)
data.to_pickle('picklefiles\\all-postss2.pkl')

data.to_csv("csvfiles\\allpostss2.csv")


