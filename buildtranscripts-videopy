import os
import time
import cv2
from openai import OpenAI 
import base64
import requests
import pandas as pd
import utils.openAiRateLimit as oirt


# from VectorizeDataset import Preprocessing
# from EmbedChunks import EmbedChunks
# from SaveData import SaveData
# use_serverless = True

SKIP_RATE = 30
GPT_ACCEPT_RATE = 12
api_key=os.getenv("OPENAI_API_KEY")
Client=OpenAI()


#read the latest dataframe
df = pd.read_pickle('dataframe.pickle')
video_outfolder = "video-out"


# Function to convert video to frames
def convert_video_to_frames(video_path, creatorid,video_outfolder,overwrite=False):
  video_name = os.path.basename(video_path)
  folder_name=os.path.join(video_outfolder, creatorid,os.path.splitext(video_name)[0] )
  
  #Create folder for creator, videos if none exists
  if not os.path.exists(folder_name):
        os.makedirs(folder_name)
  # Check if '.jpg' files exist in 'folder_name' and overwrite=False
  if not overwrite and any(file.endswith('.jpg') for file in os.listdir(folder_name)):
    print("JPG files already exist in the folder. Skipping conversion.")
  else:
    print("running video to frames conversion")
    #read video and save frames (max frames per video is limited to 500/30=16.6 seconds at 30fps)
    video = cv2.VideoCapture(video_path)
    i=0
    while video.isOpened() and i<500:
        success, frame = video.read()
        if not success:
            break
        if i%SKIP_RATE==0:
          frames_path = os.path.join(folder_name,'frame'+str(i).zfill(3)+".jpg")
          cv2.imwrite(frames_path, frame) 
          print(frames_path)
        i+=1
    video.release()  
  return folder_name





# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def convert_frames_to_transcript(frames,max_frames=15):
  headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "The below pictures are frames from a video sequence. Extract all text and product labels mentioned in the image. Describe all products along with color, material in 1-2 sentences. If something is not clear, do not make stuff up. products are mostly clothes and fashion accessroies."
          }
        ]
      }
    ],
    "max_tokens": 500
  }

  image_urls = []
  for frame in os.listdir(frames):
    enc_image=encode_image(os.path.join(frames,frame))
    image_url = {
              "type": "image_url",
              "image_url": {
                  "url": f"data:image/jpeg;base64,{enc_image}",  #"url": f"data:image/jpeg;base64,{encode_image(os.path.join('video-out',image))}"
                  "detail": "low"
              }
          }
    image_urls.append(image_url)
  print(f'frames loaded (max):',len(image_urls),'(',max_frames,')')
  payload["messages"][0]["content"].extend(image_urls[:max_frames])
  try:
    response = oirt.completions_http_with_backoff("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    transcript = response.json()['choices'][0]['message']['content']
    res_header = response.headers
  except Exception as e:
    print(f"Exception occurred: {e}")
    transcript = 'skipped transcript'
    res_header = None

  return transcript, res_header






for url in df['url']:
   if df.loc[df["url"] == url,'typename'].values[0]=='GraphVideo':
      creatorid = df.loc[df["url"] == url,'creatorid'].values[0]
      frames_path=convert_video_to_frames(url,creatorid, video_outfolder,overwrite=False)
      df.loc[df["url"] == url, "frames_url"] = frames_path


df.to_pickle("dataframe.pickle")


for frames in df["frames_url"]:
   if str(frames)!='nan' and str(df.loc[df["frames_url"] == frames,'video_transcript'].values[0])=='nan':
      print(f"frame: {frames}")
      transcript,res_header=convert_frames_to_transcript(frames,max_frames=12)
      df.loc[df["frames_url"] == frames, "video_transcript"] = transcript
      print(f"remaining requests: {res_header['x-ratelimit-remaining-requests']}")
      print(f"remaining tokens  tokens: {res_header['x-ratelimit-remaining-tokens']}")

df.to_pickle("dataframe.pickle")


#loop for missed videos
missed_videos = []
for video_transcript in df["video_transcript"]:
   if str(video_transcript)!='nan' and len(str(video_transcript))<=50:
     missed_videos.append(df.loc[df["video_transcript"] == video_transcript,'frames_url'].values[0])


for frames in missed_videos: 
   if str(frames)!='nan':
      print(f"frame: {frames}")
      transcript,res_header=convert_frames_to_transcript(frames,max_frames=12)
      df.loc[df["frames_url"] == frames, "video_transcript"] = transcript
      print(f"remaining requests: {res_header['x-ratelimit-remaining-requests']}")
      print(f"remaining tokens  tokens: {res_header['x-ratelimit-remaining-tokens']}")

df.to_pickle("dataframe.pickle")


#create combined transcript
for index, row in df.iterrows():
  audio_transcript = str(row['en_audio_transcript'])
  video_transcript = str(row['video_transcript'])
  print("processing transcript: ", index)
  if audio_transcript != 'nan' and video_transcript != 'nan':
    input_msg = f"AUDIO TRANSCRIPT: {audio_transcript}\n\n\nVIDEO TRANSCRIPT: {video_transcript}"
    try:
      response = oirt.completions_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
          {"role": "system", "content": "combine the below audio transcript and video transcript into a single summary. Provide a list of any products and brands mentioned in the transcript. List the products and brands with special emphasis to the AUDIO TRANSCRIPT. Be truthful, if no products or brands are available, say N/A"},
          {"role": "user", "content": input_msg}
        ]
      )
      transcript = response.choices[0].message.content
    except Exception as e:
      print(f"OpenAI API request error: {e}")
      transcript = 'nan'
      pass
    title = str(row['caption'])
    tags = str(row['caption_hashtags'])
    transcript_full = f"TRANSCRIPT: {transcript}\n\n\nTITLE: {title}\n\n\nTAGS: {tags}"
    df.loc[index, "transcript"] = transcript_full
    
 df.to_pickle("dataframe.pickle")
