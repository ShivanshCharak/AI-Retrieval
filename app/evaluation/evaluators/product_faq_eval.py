import asyncio
from pathlib import Path

import numpy as np
import pandas as pd
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output = f"results/product_faq_eval_{timestamp}.csv"

from app.db.qdrant_client_embedder import embedder
from app.services.query_translation.product_faq import product_faq

CSV_PATH = Path(__file__).parent / "datasets/product_faq_eval_expected_answers.csv"
OUTPUT_PATH = Path(__file__).parent / "results/product_faq_eval_{timestamp}.csv"

SEM_LIMIT = 20
SIMILARITY_THRESHOLD = 0.60

semaphore = asyncio.Semaphore(SEM_LIMIT)


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def evaluate_row(row):
    async with semaphore:
        query = row["query"]
        expected = row["expected_answer"]

        try:
            # Generate answer
            result = await asyncio.to_thread(product_faq, query)

            # Embed expected + generated answer
            embeddings = await asyncio.to_thread(
                embedder.embed_documents,
                [result.response, expected],
            )

            similarity = cosine_similarity(
                embeddings[0],
                embeddings[1],
            )

            passed = similarity >= SIMILARITY_THRESHOLD

            print(f"{'PASSED' if passed else 'FAILED'} " f"{similarity:.3f} | {query}")

            return {
                "query": query,
                "expected_answer": expected,
                "generated_answer": result.response,
                "llm_confidence": result.confidence,
                "semantic_similarity": round(float(similarity), 4),
                "passed": passed,
            }

        except Exception as e:
            print(f"Failed | {query}")

            return {
                "query": query,
                "expected_answer": expected,
                "generated_answer": "",
                "llm_confidence": 0.0,
                "semantic_similarity": 0.0,
                "passed": False,
                "error": str(e),
            }


async def main():
    df = pd.read_csv(CSV_PATH)

    print(f"Evaluating {len(df)} queries...")

    tasks = [evaluate_row(row) for _, row in df.iterrows()]

    results = await asyncio.gather(*tasks)

    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)

    passed = results_df["passed"].sum()
    total = len(results_df)

    print("\n==============================")
    print(f"Passed : {passed}/{total}")
    print(f"Accuracy: {passed / total:.2%}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("==============================")


if __name__ == "__main__":
    asyncio.run(main())
