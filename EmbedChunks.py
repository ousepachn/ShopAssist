import uuid
from langchain_openai import OpenAIEmbeddings
OPENAI_API_KEY = "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"

keys = ['creatorid', 'post_id', 'title', 'caption', 'likes', 'thumbnail_url',
        'url', 'date_utc', 'typename', 'caption_hashtags', 'is_video']


class EmbedChunks:
    def __init__(self, model_name):
        self.embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    def __call__(self, batch, metadata):
        res = self.embedding_model.embed_documents(batch)
        meta_data_formatted = self.create_metadata(metadata
                                                   )
        output = []
        for embedding, text in zip(res, batch):
            output.append({"id": str(uuid.uuid4()), 'values': embedding,
                          'metadata': {'text': text, **meta_data_formatted}})

        return output

    def create_metadata(self, metadata):
        dict = {}
        for i, j in zip(keys, metadata):
            dict[i] = j

        return dict
