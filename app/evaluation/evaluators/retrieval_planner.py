import asyncio
from pathlib import Path
from datetime import datetime

import pandas as pd

from app.graph.nodes.retrieval_node import retrieval_node

CSV_PATH = Path(__file__).parent.parent / "datasets/retrieval_planner_eval.csv"

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

OUTPUT_PATH = (
    Path(__file__).parent / "results" / f"retrieval_planner_eval_{timestamp}.csv"
)

SEM_LIMIT = 20

semaphore = asyncio.Semaphore(SEM_LIMIT)


def to_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() == "true"

    return bool(value)


async def evaluate_row(row):
    async with semaphore:

        query = row["query"]

        expected_memory = to_bool(row["expected_use_memory"])
        expected_vector = to_bool(row["expected_use_vector"])
        expected_repo = to_bool(row["expected_use_repo"])

        try:
            result = await asyncio.to_thread(
                retrieval_node,
                query,
            )

            predicted_memory = result["use_memory"]
            predicted_vector = result["use_vector"]
            predicted_repo = result["use_repo"]

            confidence = result.get(
                "confidence",
                0.0,
            )

            passed = (
                predicted_memory == expected_memory
                and predicted_vector == expected_vector
                and predicted_repo == expected_repo
            )

            print(
                f"{'PASSED' if passed else 'FAILED'} "
                f"| expected_memory={expected_memory} "
                f"| predicted_memory={predicted_memory} "
                f"| expected_vector={expected_vector} "
                f"| predicted_vector={predicted_vector} "
                f"| expected_repo={expected_repo} "
                f"| predicted_repo={predicted_repo} "
                f"| confidence={confidence:.3f} "
                f"| {query}"
            )

            return {
                "query": query,
                "expected_use_memory": expected_memory,
                "predicted_use_memory": predicted_memory,
                "expected_use_vector": expected_vector,
                "predicted_use_vector": predicted_vector,
                "expected_use_repo": expected_repo,
                "predicted_use_repo": predicted_repo,
                "confidence": confidence,
                "passed": passed,
                "error": "",
            }

        except Exception as e:

            print(f"FAILED | {query} | ERROR: {e}")

            return {
                "query": query,
                "expected_use_memory": expected_memory,
                "predicted_use_memory": "",
                "expected_use_vector": expected_vector,
                "predicted_use_vector": "",
                "expected_use_repo": expected_repo,
                "predicted_use_repo": "",
                "confidence": 0.0,
                "passed": False,
                "error": str(e),
            }


async def main():

    df = pd.read_csv(CSV_PATH, usecols=range(6))

    print(f"Evaluating {len(df)} queries...")

    tasks = [evaluate_row(row) for _, row in df.iterrows()]

    results = await asyncio.gather(*tasks)

    results_df = pd.DataFrame(results)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # Overall exact-match accuracy
    passed = results_df["passed"].sum()
    total = len(results_df)

    accuracy = passed / total if total > 0 else 0.0

    # Individual dimension accuracy
    memory_accuracy = (
        (results_df["predicted_use_memory"] == results_df["expected_use_memory"]).mean()
        if total > 0
        else 0.0
    )

    vector_accuracy = (
        (results_df["predicted_use_vector"] == results_df["expected_use_vector"]).mean()
        if total > 0
        else 0.0
    )

    repo_accuracy = (
        (results_df["predicted_use_repo"] == results_df["expected_use_repo"]).mean()
        if total > 0
        else 0.0
    )

    print("\n==============================")
    print(f"Passed           : {passed}/{total}")
    print(f"Overall Accuracy : {accuracy:.2%}")
    print(f"Memory Accuracy  : {memory_accuracy:.2%}")
    print(f"Vector Accuracy  : {vector_accuracy:.2%}")
    print(f"Repo Accuracy    : {repo_accuracy:.2%}")
    print(f"Saved to         : {OUTPUT_PATH}")
    print("==============================")


if __name__ == "__main__":
    asyncio.run(main())
