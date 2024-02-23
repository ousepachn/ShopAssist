import os
from trulens_eval import TruCustomApp
import numpy as np
from trulens_eval.feedback.provider.openai import OpenAI as fOpenAI
from trulens_eval.feedback import Groundedness
from trulens_eval import Feedback, Select
from trulens_eval import Tru
from trulens_eval.tru_custom_app import instrument
from RAGQuery import Evalution
tru = Tru()


class Evaluate:
    def get_metrics(self):
        fopenai = fOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        grounded = Groundedness(groundedness_provider=fopenai)

        # Define a groundedness feedback function
        groundedness = (
            Feedback(grounded.groundedness_measure_with_cot_reasons,
                     name="Groundedness")
            .on(Select.RecordCalls.retrieve.rets.collect())
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
        )

        # Question/answer relevance between overall question and answer.
        relevance = (
            Feedback(fopenai.relevance_with_cot_reasons,
                     name="Answer Relevance")
            .on(Select.RecordCalls.retrieve.args.query)
            .on_output()
        )

        # Question/statement relevance between question and each context chunk.
        context_relevance = (
            Feedback(fopenai.qs_relevance_with_cot_reasons,
                     name="Context Relevance")
            .on(Select.RecordCalls.retrieve.args.query)
            .on(Select.RecordCalls.retrieve.rets.collect())
            .aggregate(np.mean)
        )

        return groundedness, relevance, context_relevance

    def eval(self, query, filters):
        result = ""
        rag = Evalution()
        g, r, cr = self.get_metrics()
        tru_rag = TruCustomApp(rag, app_id='RAG v1', feedbacks=[g, r, cr])

        with tru_rag as recording:
            result = rag.query(query, filters)

        print(tru.get_leaderboard(app_ids=["RAG v1"]))
        return result
