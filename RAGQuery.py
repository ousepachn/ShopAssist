
from openai import OpenAI
import time
from SaveData import SaveData
from trulens_eval.tru_custom_app import instrument

limit = 3750
embed_model = "text-embedding-ada-002"

client = OpenAI()


class Evalution:
    @instrument
    def retrieve(self, query, filters):
        contexts = SaveData().retrieve_k_context(4, query, filters)
        # build our prompt with the retrieved contexts included
        prompt_start = (
            "Answer the question based on the context below.\n\n" +
            "Context:\n")
        prompt_end = (
            f"\n\nQuestion: {query} Make sure to append url links as well\n Answer:")

        # append contexts until hitting limit
        for i in range(1, len(contexts)):
            if len("\n\n---\n\n".join(contexts[:i])) >= limit:
                prompt = (
                    prompt_start +
                    "\n\n---\n\n".join(contexts[:i-1]) +
                    prompt_end)
                break
            elif i == len(contexts)-1:
                prompt = (
                    prompt_start +
                    "\n\n---\n\n".join(contexts) +
                    prompt_end)
        return prompt

    @instrument
    def query(self, query, filters):
        prompt = self.retrieve(query, filters)
        # instructions
        sys_prompt = "You are a helpful assistant that always answers questions."

        PROMPT_MESSAGES = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ]

        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=PROMPT_MESSAGES,
        )

        print(res.choices[0].message.content.strip())
        return res.choices[0].message.content.strip()
