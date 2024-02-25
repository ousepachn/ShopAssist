import os
import time
import cv2
import openai
import base64

from VectorizeDataset import Preprocessing
from EmbedChunks import EmbedChunks
from SaveData import SaveData
use_serverless = True

SKIP_RATE = 30
GPT_ACCEPT_RATE = 12
PATH = "./2024-02-17_15-58-58_UTC.mp4"
GPT_KEY = "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"

openai.api_key = GPT_KEY
result = """
The text in the frames reads as follows:

1. "Is this $12 Quo balm a dupe for the Dior lip glow? 🤔"
2. "So I picked this up in Canada and you cannot tell"
3. "me that these do not look identical even the colors"
4. "look identical."
5. "So we're going to start with the Dior lip glow"
6. "in the shade raspberry."
7. "It's definitely giving like chapstick vibes"

The context is a comparison between a $12 Quo balm and a Dior lip glow product, with the person in the video suggesting that the Quo balm might be a more affordable alternative ("dupe") to the Dior product. She mentions picking up the Quo balm in Canada and comments on the similarity in appearance between the two products. She then proceeds to demonstrate the Dior lip glow in the shade raspberry, noting that it feels like a chapstick.The text in the frames reads as follows:

1. It's definitely giving like chapstick vibes
2. It's definitely giving like chapstick vibes
3. but very minty and I'm #literal*mint that so
4. but very minty and I'm #literal*mint that so
5. but very minty and I'm #literal*mint that so
6. I really like that this one is not super glowy.
7. I really like that this one is not super glowy.
8. but it is very hydrating. Now...
9. but it is very hydrating. Now...
10. We have quo in punch.
11. We have quo in punch.
12. (No text visible)

Please note that the text in frames 3, 4, and 5 seems to be cut off and may not represent the full sentence or intended hashtag. The text in frames 10 and 11 appears to be a product name or color, but it is not entirely clear due to the text being cut off.The text in the frames reads as follows:

1. Literally looks the same.
2. (No text in this frame)
3. So not quite as pigmented and there's no Peppermint at all.
4. So not quite as pigmented and there's no Peppermint at all.
5. So not quite as pigmented and there's no Peppermint at all.
6. But in terms of feeling they feel identical on the lips.
7. But in terms of feeling they feel identical on the lips.
8. But in terms of feeling they feel identical on the lips.
9. So you tell me are we going for the dupe or are
10. So you tell me are we going for the dupe or are
11. we sticking with the OG?
"""


class CaptureVideoFrames:
    def captureVideo(self, path):
        video = cv2.VideoCapture(path)
        base64Frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()
        return base64Frames

    def completeChat(self, frames):
        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [
                    "These are frames from a video that I want you to analyze. If there is any text in these frames make sure to return that as well, while maintaining the context. Don't explain it, just return what's in the frames",
                    *map(lambda x: {"image": x, "resize": 768}, frames),
                ],
            },
        ]

        res = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=PROMPT_MESSAGES,
            temperature=0.1,
            max_tokens=300
        )
        return res['choices'][0]['message']['content'].strip()

    def summarizeText(self, generatedText):
        prompt = f"""The following is a section of the transcript of a video you 
        generated. There seems to be some redundant information. Can you remove redudancy from the input text, but make sure to include all important points. 
        Also santize the output.
        
        {generatedText}
        """

        completion = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            max_tokens=500,
            temperature=0.1,
            prompt=prompt,
            frequency_penalty=0
        )
        return completion['choices'][0]['text'].strip()

    def callGPT(self):
        frames = self.captureVideo(PATH)
        result = ""
        for i in range(0, len(frames), GPT_ACCEPT_RATE * SKIP_RATE):
            result += self.completeChat(frames[i:i +
                                        (GPT_ACCEPT_RATE*SKIP_RATE):SKIP_RATE])
            time.sleep(25)
        print("\n\n"+result+"\n\n")
        print(len(frames))
        print(self.summarizeText(result))
        return "\nThe context is a comparison between the Quo balm and Dior lip glow products in terms of pigmentation and feeling on the lips. The person in the video notes that the two products look identical and have a similar feeling on the lips, but the Quo balm is not as pigmented and does not have peppermint in it. She then asks for the viewer's opinion on whether they should go for the more affordable \"dupe\" or stick with the original Dior product."


if __name__ == "__main__":
    summarizedData = CaptureVideoFrames().callGPT()
    preProcData = Preprocessing().preprocess(summarizedData)
    data = EmbedChunks("text-embedding-ada-002")(preProcData)
    SaveData().insert_data(data)
    # model(preProcData)
