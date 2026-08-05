import asyncio
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from app.db.qdrant_client_embedder import embedder
from app.services.query_translation.multi_query import generate_multi_queries
from app.db.metadata_store import get_collection_metadata

SEM_LIMIT = 20
SIMILARITY_THRESHOLD = 0.60

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

CSV_PATH = Path(__file__).parent / "multi_query_eval_expected_answers.csv"
OUTPUT_PATH = Path(__file__).parent / f"results/multi_query_eval_{timestamp}.csv"

semaphore = asyncio.Semaphore(SEM_LIMIT)


def cosine_similarity(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def evaluate_row(row):
    metadata = get_collection_metadata()
    async with semaphore:
        query = row["query"]

        expected_queries = [
            row["expected_query_1"],
            row["expected_query_2"],
            row["expected_query_3"],
            row["expected_query_4"],
            row["expected_query_5"],
        ]

        try:
            # If using GraphState:
            # generated_queries = await asyncio.to_thread(
            #     generate_multi_queries,
            #     {"query": query},
            #     metadata,
            # )
            generated_queries = await asyncio.to_thread(
                generate_multi_queries,
                {"query": query},
                metadata,
            )

            if len(generated_queries) != 5:
                raise ValueError(
                    f"Expected 5 generated queries, got {len(generated_queries)}"
                )

            embeddings = await asyncio.to_thread(
                embedder.embed_documents,
                generated_queries + expected_queries,
            )

            similarities = []

            for i in range(5):
                similarities.append(
                    cosine_similarity(
                        embeddings[i],
                        embeddings[i + 5],
                    )
                )

            avg_similarity = float(np.mean(similarities))
            passed = avg_similarity >= SIMILARITY_THRESHOLD

            print(
                f"{'PASSED' if passed else 'FAILED'} | "
                f"{avg_similarity:.3f} | {query}"
            )

            return {
                "query": query,
                "generated_queries": generated_queries,
                "expected_queries": expected_queries,
                "average_similarity": round(avg_similarity, 4),
                "passed": passed,
            }

        except Exception as e:
            import traceback

            traceback.print_exc()

            return {
                "query": query,
                "generated_queries": [],
                "expected_queries": expected_queries,
                "average_similarity": 0.0,
                "passed": False,
                "error": str(e),
            }


async def main():
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    print(f"Evaluating {len(df)} queries...")

    results = await asyncio.gather(*(evaluate_row(row) for _, row in df.iterrows()))

    results_df = pd.DataFrame(results)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(OUTPUT_PATH, index=False)

    passed = int(results_df["passed"].sum())
    total = len(results_df)

    print("\n==============================")
    print(f"Passed : {passed}/{total}")
    print(f"Accuracy: {passed / total:.2%}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("==============================")


if __name__ == "__main__":
    asyncio.run(main())
