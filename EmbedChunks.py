import uuid
from langchain_openai import OpenAIEmbeddings
GPT_KEY = "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"


class EmbedChunks:
    def __init__(self, model_name):
        self.embedding_model = OpenAIEmbeddings(openai_api_key=GPT_KEY)

    def __call__(self, batch):
        res = self.embedding_model.embed_documents(batch[0])

        output = []
        for metadata, embedding in zip(batch[1], res):
            output.append({"id": str(uuid.uuid4()), 'values': embedding,
                          'metadata': metadata})

        return output
