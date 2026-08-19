from pathlib import Path


from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()


from fastapi import APIRouter
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
import pandas as pd

router = APIRouter()

RESULTS_DIR = Path("app/evaluation/evaluators/results")


def metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
    }


@router.get("/evaluation/classification")
async def classification_eval():

    router_df = pd.read_csv(
        "app/evaluation/evaluators/results/" "router_eval_2026-08-11_03-04-28.csv"
    )

    router_df = router_df.dropna(subset=["expected_route", "predicted_route"])

    router_metrics = metrics(
        router_df["expected_route"].astype(str),
        router_df["predicted_route"].astype(str),
    )

    # -------------------------
    # Retrieval Planner
    # -------------------------

    planner_df = pd.read_csv(
        "app/evaluation/evaluators/results/"
        "retrieval_planner_eval_2026-08-11_07-22-12.csv"
    )

    planner_metrics = {}

    for target in ["memory", "vector", "repo"]:

        y_true = planner_df[f"expected_use_{target}"].astype(bool)

        y_pred = planner_df[f"predicted_use_{target}"].astype(bool)

        planner_metrics[target] = metrics(
            y_true,
            y_pred,
        )

    return {
        "router": {
            "node": "Router",
            **router_metrics,
        },
        "retrieval_planner": {
            "node": "Retrieval Planner",
            "memory": planner_metrics["memory"],
            "vector": planner_metrics["vector"],
            "repo": planner_metrics["repo"],
        },
    }


RESULTS_DIR = Path("app/evaluation/evaluators/results")


@router.get("/evaluation/retrieval")
async def retrieval_eval():

    try:

        files = {
            "dense": RESULTS_DIR / "retrieval_eval_2026-08-13_08-00-13.csv",
            "hybrid": RESULTS_DIR / "retrieval_eval_2026-08-13_10-06-08.csv",
            "reranked": RESULTS_DIR / "retrieval_eval_2026-08-13_12-14-45.csv",
        }

        columns = [
            "id",
            "query",
            "expected_id",
            "rank",
            "recall@1",
            "recall@3",
            "recall@5",
            "recall@10",
            "hit_rate@1",
            "hit_rate@3",
            "hit_rate@5",
            "hit_rate@10",
            "ndcg@1",
            "ndcg@3",
            "ndcg@5",
            "ndcg@10",
            "mrr",
            "passed",
        ]

        response = {}

        for name, file_path in files.items():

            if not file_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=(f"{name} evaluation file not found: " f"{file_path}"),
                )

            df = pd.read_csv(file_path)

            available_columns = [column for column in columns if column in df.columns]

            # Convert NaN → None so FastAPI can serialize JSON
            df = df[available_columns].astype(object)
            df = df.where(
                pd.notna(df),
                None,
            )

            rows = df.to_dict(orient="records")

            response[name] = {
                "file": file_path.name,
                "count": len(rows),
                "rows": rows,
            }

        return response

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
