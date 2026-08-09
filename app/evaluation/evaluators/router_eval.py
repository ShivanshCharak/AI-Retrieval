import asyncio
from pathlib import Path
from datetime import datetime

import pandas as pd

from app.graph.nodes.graph_router import graph_router_node

CSV_PATH = Path(__file__).parent.parent / "datasets/router_dataset.csv"

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

OUTPUT_PATH = Path(__file__).parent / "results" / f"router_eval_{timestamp}.csv"

SEM_LIMIT = 20

semaphore = asyncio.Semaphore(SEM_LIMIT)


async def evaluate_row(row):
    async with semaphore:
        query = row["query"]
        expected = row["expected_route"]

        try:
            # Run synchronous router without blocking event loop
            result = await asyncio.to_thread(
                graph_router_node,
                query,
            )

            predicted = result["route"]

            confidence = result.get(
                "confidence",
                0.0,
            )

            passed = predicted == expected

            print(
                f"{'PASSED' if passed else 'FAILED'} "
                f"| expected={expected} "
                f"| predicted={predicted} "
                f"| confidence={confidence:.3f} "
                f"| {query}"
            )

            return {
                "query": query,
                "expected_route": expected,
                "predicted_route": predicted,
                "confidence": confidence,
                "passed": passed,
                "error": "",
            }

        except Exception as e:

            print(f"FAILED | {query} | ERROR: {e}")

            return {
                "query": query,
                "expected_route": expected,
                "predicted_route": "",
                "confidence": 0.0,
                "passed": False,
                "error": str(e),
            }


async def main():

    df = pd.read_csv(CSV_PATH)

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

    passed = results_df["passed"].sum()
    total = len(results_df)

    accuracy = passed / total if total > 0 else 0.0

    print("\n==============================")
    print(f"Passed  : {passed}/{total}")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("==============================")


if __name__ == "__main__":
    asyncio.run(main())
