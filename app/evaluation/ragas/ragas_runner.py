# app/evaluation/runners/ragas_runner.py

from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    ContextPrecision,
    ContextRecall,
    AnswerRelevancy,
)


def run_ragas(records):

    dataset = Dataset.from_list(records)

    result = evaluate(
        dataset=dataset,
        metrics=[
            Faithfulness(),
            ContextPrecision(),
            ContextRecall(),
            AnswerRelevancy(),
        ],
    )

    return result
