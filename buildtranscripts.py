import os
import pandas as pd
import moviepy.editor as mp
from openai import OpenAI
from langdetect import detect
# Define the paths
audio_outfolder = "audio_output/"
transcript_outfolder = "transcript_output/"

# Function to convert video to audio
def convert_video_to_audio(video_path, audio_outfolder):
    video_name = os.path.basename(video_path)
    audio_name = os.path.splitext(video_name)[0] + ".mp3"
    audio_path = os.path.join(audio_outfolder, audio_name)
    clip=mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path

# Function to convert audio to transcript
def convert_audio_to_transcript(audio_path):
    audio_file= open(audio_path, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    prompt=Prompt
    )
    return transcript

# Append together pickle files and create a dataframe
data = pd.DataFrame()
for file in os.listdir():
    if file.endswith(".pkl"):
        df = pd.read_pickle(file)
        data=pd.concat([data,df], ignore_index=True)

# Convert video to audio.  Iterate through the dataframe and process each URL, 
for url in data["url"]:
    # 
    if url.endswith(".mp4"):
        audio_path = convert_video_to_audio(url, audio_outfolder)
        data.loc[data["url"] == url, "audio_url"] = audio_path
    
 

client = OpenAI()
Model="whisper-1"
Prompt='Please add punctuation. Do not miss any words.  Even if the word is soft, please transcribe it.'
for url in data["audio_url"][data["audio_transcript"].isna()]:
    if str(url)!='nan':
    # Convert audio to transcripts.  Iterate through the dataframe and process each audio URL
        transcript=convert_audio_to_transcript(url)
        print(transcript)
       # Save the transcript in the dataframe
        data.loc[data["audio_url"] == url, "audio_transcript"] = transcript.text# Save the dataframe as a pickle file

# build only english version of the transcripts from audio
#TODO - NEED TO SEE HOW TO REMOVE AUDIO LYRICS FRMO AUDIO
for t in data["audio_transcript"]:
    if str(t)!='nan' and len(t)>1:
        if detect(t) == 'en':
            data.loc[data["audio_transcript"] == t, "en_audio_transcript"]=t

data.drop_duplicates(subset=['post_id'],inplace=True)
data.to_pickle("dataframe.pickle")

data.to_csv("dataframe.csv")
