import os
import time
import base64
import requests
import cv2
from openai import OpenAI 
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
df = pd.read_pickle('picklefiles\\all-postss2.pkl')
video_outfolder = "video-out"

df = df[df['creatorid'].isin(["kirtitewani","fatimaa.younus","hemali.mistry","whatsmitafound","hydrationceo"])]
#PROMPT TEMPLATES:
# Define creatorid to text mappings
creatorid_to_text = {
  "hydrationceo": "The below pictures are frames from a video sequence. Try to extract all text and product labels mentioned in the image. Try to describe all products along with brandnames, manufacturer name and usage type in 1-2 sentences. If something is not clear, do not make stuff up.  Do not comment on the person but only about the products. Products are mostly beauty products.",
  "whatsmitafound": "The below pictures are frames from a video sequence. Try to Extract all text and product labels mentioned in the image. Try to describe all products along with brandnames, manufacturer name and and usage type in 1-2 sentences. If something is not clear, do not make stuff up. You dont have to comment about the person. The products are mostly clothes and fashion accessories.",
  "kirtitewani": "The below pictures are frames from a video sequence from a beauty blogger. Try to extract all text and product labels mentioned in the image. Try to describe all beauty conditions along with products, brandnames and usage details in 1-2 sentences. If something is not clear, do not make stuff up. You dont have to comment about the person. The products are mostly used for beauty treatments.",
  "hemali.mistry": "The below pictures are frames from a video sequence from a lifestyle influencer. Try to extract all text and product labels mentioned in the images. Try to describe all locations, brands, fashion products, restaurant locations, travel details etc in 1-2 sentences. If something is not clear, do not make stuff up. You dont have to comment about the people. The product, restaurant promotiions are most important.",
  "thescenenewyork": "The below pictures are frames from a video sequence from a restaurant reviewer. Try to extract all text, restaurant name, location and cuisine related details mentioned. If there are special themes associated with the restaurant, try to extract that as well. Descriptions should be maximum 1-2 sentences.  If something is not clear, do not make stuff up. You dont have to comment about the people. The cuisine, atmosphere and location details are important.",
  "payalforstyle": "The below pictures are frames from a video sequence from a lifestyle influencer. Try to extract all text and product labels mentioned in the images. Try to describe all locations, brands, fashion products, restaurant locations, travel details etc in 1-2 sentences. If something is not clear, do not make stuff up. You dont have to comment about the person. The product, restaurant promotiions are most important.",
  "fatimaa.younus": "The below pictures are frames from a video sequence from a lifestyle influencer. Try to extract all text and product labels mentioned in the images. Try to describe all locations, brands, fashion products, restaurant locations, travel details etc in 1-2 sentences. If something is not clear, do not make stuff up. You dont have to comment about the person. The product, restaurant promotiions are most important."
  # Add more mappings as needed
}


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

def convert_frames_to_transcript(frames,creatorid,max_frames=15):
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
            "text": creatorid_to_text.get(creatorid, "The below pictures are frames from a video sequence. Extract all text and product labels mentioned in the image. Describe all products along with color, material in 1-2 sentences. If something is not clear, do not make stuff up. products are mostly clothes and fashion accessroies.")
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
  print(payload["messages"][0]["content"][0]["text"])
  payload["messages"][0]["content"].extend(image_urls[:max_frames])
  try:
    response = oirt.completions_http_with_backoff("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    transcript = response.json()['choices'][0]['message']['content']
    res_header = response.headers
  except Exception as e:
    print(f"Exception occurred: {e} response: {response}")
    transcript = 'skipped transcript'
    res_header = None

  return transcript, res_header






for url in df['url']:
   if df.loc[df["url"] == url,'typename'].values[0]=='GraphVideo':
      creatorid = df.loc[df["url"] == url,'creatorid'].values[0]
      frames_path=convert_video_to_frames(url,creatorid, video_outfolder,overwrite=False)
      df.loc[df["url"] == url, "frames_url"] = frames_path


df.to_pickle("picklefiles\\all-postss3v2.pkl")

#####TEMPORRARY CODE TO BE DELETED
df=pd.read_pickle("picklefiles\\all-postss3.pkl")
df=pd.read_pickle("picklefiles\\all-postss3v2.pkl")
df=pd.concat([dfa,dfb])

################################
df['video_transcript']='nan'  
  

for frames in df["frames_url"]:
  if str(frames)!='nan' and str(df.loc[df["frames_url"] == frames,'video_transcript'].values[0]) in ['nan', 'skipped transcript']:
    print(f"frame: {frames}")
    creatorid = df.loc[df["frames_url"] == frames,'creatorid'].values[0]
    transcript,res_header=convert_frames_to_transcript(frames,creatorid,max_frames=12)
    df.loc[df["frames_url"] == frames, "video_transcript"] = transcript
    if res_header:
      print(f"remaining requests: {res_header['x-ratelimit-remaining-requests']}")
      print(f"remaining tokens: {res_header['x-ratelimit-remaining-tokens']}")

df.to_pickle("picklefiles\\all-postss4v3.pkl")


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

df.to_pickle("picklefiles\\all-postss5.pkl")


df.reset_index(drop=True, inplace=True)
#create combined transcript
i=0
tot_rw=df.shape[0]
for index, row in df.iterrows():
  print(i, 'of', tot_rw, '. index:', index)
  transcript='to be created'
  audio_transcript = str(row['en_audio_transcript']) if pd.notna(row['en_audio_transcript']) else ''
  video_transcript = str(row['video_transcript']) if pd.notna(row['video_transcript']) else ''
  # print("processing transcript: ", index, video_transcript[:30], 'loc based:',df.loc[index,"video_transcript"][:30])
  if audio_transcript != ''or video_transcript != '':
    i=i+1
    input_msg = f"AUDIO TRANSCRIPT: {audio_transcript}\n\n\nVIDEO TRANSCRIPT: {video_transcript}"
    try:
      response = oirt.completions_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
          {"role": "system", "content": "The below audio and video transcripts are from influencers. Combine them into a single summary capturing relevant themes, products, places, brand names, etc. If available, provide a list of any products, locations, restaurants, foods and brands mentioned in the transcript. You can ignore short transcripts with less than 50 words. Be truthful, DO NOT HALLUCINATE."},
          {"role": "user", "content": input_msg}
        ]
      )
      transcript = response.choices[0].message.content
    except Exception as e:
      print(f"OpenAI API request error: {e} response: {response} ")
      transcript = 'nan'
    title = str(row['caption'])
    tags = str(row['caption_hashtags'])
    transcript_op = f"TRANSCRIPT: {transcript}\n\n\nTITLE: {title}\n\n\nTAGS: {tags}"
    transcript_op_full = f"TRANSCRIPT: {transcript}\n\n\nAUDIO: {audio_transcript}\n\n\nVIDEO: {video_transcript}\n\n\nTITLE: {title}\n\n\nTAGS: {tags}"
    print("transcript_full = ",transcript,"\n\n\nTITLE: ",df.loc[index, ["creatorid","caption"]],"\n\n\naudio: ",audio_transcript[:30],"\n\n\nvideo: ",video_transcript[:30])
  else :
    transcript_op= f"TRANSCRIPT: N/A\n\n\nTITLE: {title}\n\n\nTAGS: {tags}"
    transcript_op_full = f"TRANSCRIPT: N/A\n\n\nAUDIO: N/A\n\n\nVIDEO: N/A\n\n\nTITLE: {title}\n\n\nTAGS: {tags}"
  df.loc[index, "transcript"] = transcript_op
  df.loc[index, "transcript-long"] = transcript_op_full
    
df.to_pickle("picklefiles\\all-postss6.pkl")


