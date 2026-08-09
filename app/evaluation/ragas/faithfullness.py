from datasets import Dataset
from ragas import evaluate
from ragas.metrics import Faithfulness

from app.evaluation.ragas.llm import ragas_llm


def evaluate_faithfulness(
    query: str,
    contexts: list[str],
    answer: str,
):
    dataset = Dataset.from_dict(
        {
            "user_input": [query],
            "retrieved_contexts": [contexts],
            "response": [answer],
        }
    )

    result = evaluate(
        dataset,
        metrics=[
            Faithfulness(llm=ragas_llm),
        ],
    )

    return result
